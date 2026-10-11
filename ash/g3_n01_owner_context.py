"""N01's bounded current-session consistency seam, never source authority.

Reuses the closed D01 Stytch Consumer Test mapping and mature signature library.
The caller must authenticate native response origin and enrollment separately.
No credential loader, login, OTP, provider call, receipt or grant exists here.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import json
import re

from ash.g3_control_semantics import require

PROJECT='project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d'
OWNER='user-test-9da3c5e0-6828-4dfe-8d6d-6ee5dde17a8e'
MAX_CONTEXT_MS=300000


def integer(value):
    require(type(value) is int and 0 <= value <= 2**63-1)
    return value


def unique_json(raw):
    require(type(raw) is bytes and len(raw)<=16384)
    def pairs(items):
        value={}
        for key,child in items:
            require(key not in value);value[key]=child
        return value
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs)


def part(value,limit):
    require(type(value) is str and 0<len(value)<=limit and re.fullmatch(r'[A-Za-z0-9_-]+',value))
    raw=base64.urlsafe_b64decode(value+'='*((-len(value))%4))
    require(base64.urlsafe_b64encode(raw).rstrip(b'=').decode()==value)
    return raw


def timestamp(value):
    require(type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,9})?Z',value))
    stem,dot,fraction=value[:-1].partition('.')
    second=datetime.strptime(stem,'%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    milliseconds=int(second.timestamp())*1000+int((fraction+'000')[:3])
    exact=stem+'.'+fraction.ljust(9,'0')+'Z'
    return integer(milliseconds),exact


def public_keys(keys):
    """Closed reviewed public pin input, never key-source authentication."""
    import jwt
    require(type(keys) is tuple and 1<=len(keys)<=8
            and all(type(key) is dict for key in keys) and len(json.dumps(keys))<=16384)
    seen=set();result=[]
    for key in keys:
        require(set(key)=={'kty','kid','alg','use','n','e'} and key['kty']=='RSA'
                and key['alg']=='RS256' and key['use']=='sig')
        require(type(key['kid']) is str and re.fullmatch(r'jwk-test-[a-f0-9-]{36}',key['kid'])
                and key['kid'] not in seen)
        require(part(key['n'],1024)[0]!=0 and part(key['e'],16)[0]!=0)
        require(jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key)).key_size>=2048)
        seen.add(key['kid']);result.append(dict(key))
    return tuple(result)


@dataclass(frozen=True)
class OwnerProjection:
    provider_project: str
    provider_user: str
    provider_session: str
    authenticated_at_ms: int
    remote_expires_at_ms: int
    factor_lineage_sha256: str

    @property
    def authority(self):return 'NONE'


def project_current_owner(response,keys,*,review_from_ms,review_until_ms,now_ms):
    """Cryptographic/response consistency only; bytes do not prove native origin."""
    try:
        import jwt
        require(integer(review_from_ms)<=integer(now_ms)<integer(review_until_ms)
                and review_until_ms-review_from_ms<=86400000)
        require(type(response) is dict and type(response.get('status_code')) is int
                and response['status_code']==200)
        session=response['session'];user=response['user'];encoded=response['session_jwt']
        require(type(encoded) is str and len(encoded)<=16384)
        segments=encoded.split('.');require(len(segments)==3)
        header=unique_json(part(segments[0],2048));claims=unique_json(part(segments[1],12288))
        part(segments[2],2048)
        require(type(header) is dict and set(header)<={'alg','typ','kid'}
                and header['alg']=='RS256' and header.get('typ','JWT')=='JWT')
        keys=public_keys(keys)
        selected=[key for key in keys if key['kid']==header['kid']];require(len(selected)==1)
        key=selected[0]
        require(set(key)=={'kty','kid','alg','use','n','e'} and key['kty']=='RSA'
                and key['alg']=='RS256' and key['use']=='sig')
        require(type(key['kid']) is str and re.fullmatch(r'jwk-test-[a-f0-9-]{36}',key['kid']))
        require(part(key['n'],1024)[0]!=0 and part(key['e'],16)[0]!=0)
        public=jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        require(public.key_size>=2048)
        # Signature verification stays in the mature library; exact trusted-time
        # comparisons below avoid accepting caller time or a refreshed context.
        verified=jwt.decode(encoded,public,algorithms=['RS256'],options={
            'verify_aud':False,'verify_iss':False,'verify_exp':False,
            'verify_iat':False,'verify_nbf':False})
        require(verified==claims and claims['iss']=='stytch.com/'+PROJECT)
        require(claims['aud']==PROJECT or claims['aud']==[PROJECT])
        require(claims['sub']==user['user_id']==session['user_id']==OWNER)
        for field in ('iat','nbf','exp'):integer(claims[field])
        require(claims['iat']*1000<=now_ms and claims['nbf']*1000<=now_ms<claims['exp']*1000)
        require(claims['exp']>max(claims['iat'],claims['nbf']) and now_ms-claims['iat']*1000<MAX_CONTEXT_MS)
        require(type(session['session_id']) is str and re.fullmatch(r'session-test-[a-f0-9-]{36}',session['session_id']))
        factors=session['authentication_factors'];require(type(factors) is list and len(factors)<=64)
        emails=[f for f in factors if f.get('type') in ('otp','email_otp') and f.get('delivery_method')=='email']
        totps=[f for f in factors if f.get('type')=='totp' and f.get('delivery_method')=='authenticator_app']
        require(len(emails)==len(totps)==1)
        email_at,email_exact=timestamp(emails[0]['last_authenticated_at'])
        totp_at,totp_exact=timestamp(totps[0]['last_authenticated_at'])
        require(0<=now_ms-email_at<MAX_CONTEXT_MS and 0<=now_ms-totp_at<MAX_CONTEXT_MS)
        email_id=emails[0]['email_factor']['email_id'];totp_id=totps[0]['authenticator_app_factor']['totp_id']
        require(type(email_id) is str and re.fullmatch(r'email-test-[a-f0-9-]{36}',email_id))
        require(type(totp_id) is str and re.fullmatch(r'totp-test-[a-f0-9-]{36}',totp_id))
        enrolled=user['totps'];require(type(enrolled) is list and len(enrolled)==1
            and enrolled[0]['verified'] is True and enrolled[0]['totp_id']==totp_id)
        expiry,_=timestamp(session['expires_at']);require(now_ms<expiry)
        lineage=json.dumps(dict(email_id=email_id,email_at=email_exact,totp_id=totp_id,totp_at=totp_exact),
            sort_keys=True,separators=(',',':')).encode()
        return OwnerProjection(PROJECT,OWNER,session['session_id'],max(email_at,totp_at),expiry,
            hashlib.sha256(lineage).hexdigest())
    except Exception:
        raise ValueError('N01_CURRENT_OWNER_DENY') from None


def same_current_session(prior,current):
    require(type(prior) is OwnerProjection and type(current) is OwnerProjection)
    require(prior==current)
    return 'SAME_PROJECTED_SESSION_NOT_SOURCE_AUTHORITY'


class ContextDeadline:
    """One non-refreshable context deadline; no bearer or restore constructor."""
    def __init__(self,*,authenticated_at_ms,review_until_ms,operation_until_ms,monotonic_start_ms):
        self.start=integer(authenticated_at_ms);self.monotonic_start=integer(monotonic_start_ms)
        self.until=min(self.start+MAX_CONTEXT_MS,integer(review_until_ms),integer(operation_until_ms))
        require(self.start<self.until);self.retired=False;self.last_wall=self.start
        self.last_monotonic=self.monotonic_start
    def check(self,*,now_ms,monotonic_ms):
        try:
            require(not self.retired and self.last_wall<=integer(now_ms)<self.until)
            require(integer(monotonic_ms)>=self.last_monotonic)
            elapsed=monotonic_ms-self.monotonic_start
            require(0<=elapsed<self.until-self.start)
            self.last_wall=now_ms;self.last_monotonic=monotonic_ms
            return 'CURRENT_TIME_ONLY_NOT_AUTHORITY'
        except Exception:
            self.retired=True
            raise ValueError('N01_CONTEXT_RETIRED') from None
    def retire(self):self.retired=True
