"""One human-origin current Owner login over the already qualified Test issuer.

Only the protected fixed HTTP controller may invoke this relying-party seam.
OTP/TOTP and original session material stay in private runtime memory, are never
logged or returned in evidence, and are not restored or refreshed. This is a new
current context, not a repetition or renewal of the closed D01 qualification.
"""
import hashlib
import hmac
from datetime import datetime,timezone
import re
import secrets
import time

from stytch import Client
from ash import g3_delegated_control_codec as control
from ash import g3_n01_owner_context as owner
from ash import g3_n01_public_review as review
from ash.g3_n01_owner_persistence import OwnerMembershipFence
from ash.g3_n01_runtime_context import CurrentSession
from ash.g3_n01_stytch_transport import BoundedStytchSession
from ash.g3_primary_ledger import DelegatedDynamoReservations
from ash.g3_control_semantics import require
from ash import g3_n02_presentation as presentation


class OwnerIngress:
    """NONE: current identity only, no registration, decision or durable authority."""
    def __init__(self,client,transport,fence,ledger,*,delivery_email_sha256):
        require(type(client) is Client and type(transport) is BoundedStytchSession)
        require(client.sync_client._session is transport and client.sync_client.project_id==owner.PROJECT)
        require(type(fence) is OwnerMembershipFence and type(ledger) is DelegatedDynamoReservations)
        control.old.check_type(delivery_email_sha256,'h')
        self.__client=client;self.__transport=transport;self.__fence=fence;self.__ledger=ledger
        self.__email_sha=delivery_email_sha256
        self.__csrf=secrets.token_hex(32);self.__cookie=secrets.token_hex(32)
        self.__method=None;self.__bearer=None;self.__context=None
        self.__started=int(time.time()*1000);self.__monotonic=time.monotonic()
        self.__last_wall=self.__started;self.__last_monotonic=self.__monotonic
        self.__until=min(self.__started+120000,self.__fence.public_review.valid_until_ms)
        self.__state='PREAUTH'
    @property
    def authority(self):return 'NONE'
    @property
    def state(self):return self.__state
    def __repr__(self):return 'OwnerIngress(authority=NONE)'
    def __reduce_ex__(self,_):raise TypeError('N01_OWNER_INGRESS_NOT_RESTORABLE')
    def __getstate__(self):raise TypeError('N01_OWNER_INGRESS_NOT_RESTORABLE')
    def attach_cookie(self,handler):
        require(self.__state in ('PREAUTH','CURRENT'))
        # Legitimate protected browser delivery only; never an evidence getter.
        handler.send_header('Set-Cookie','__Host-NexusN01='+self.__cookie+'; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=300')
    def authenticated_form(self,headers,*,csrf):
        try:
            require(type(csrf) is str and len(csrf)==64 and hmac.compare_digest(csrf,self.__csrf))
            values=headers.get_all('Cookie');require(type(values) is list and len(values)==1)
            own=[]
            for part in values[0].split(';'):
                name,sep,value=part.strip().partition('=')
                if name=='__Host-NexusN01':require(sep=='=');own.append(value)
            require(len(own)==1 and hmac.compare_digest(own[0],self.__cookie))
            return 'FORM_MATCH_ONLY_NONE'
        except Exception:
            self.retire()
            raise ValueError('N01_OWNER_FORM_DENIED') from None
    def write_form(self,handler):
        """Fixed browser form; input codes are never echoed or read by the operator."""
        require(self.__state in ('PREAUTH','OTP_SENT','OTP_VERIFIED'))
        field,title,kind,auto=(('email','Current enrolled Owner email','email','email') if self.__state=='PREAUTH'
            else ('code','Fresh email code','password','one-time-code') if self.__state=='OTP_SENT'
            else ('totp_code','Current authenticator code','password','one-time-code'))
        label='<label>'+title+' <input name="'+field+'" type="'+kind+'" autocomplete="'+auto+'" required maxlength="'+('320' if field=='email' else '6')+'"></label>'
        page=('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>N01 current Owner authentication</title><h1>Current Owner authentication</h1>'
            '<p>Dedicated Stytch Consumer Test profile. This establishes current identity only; REAL_ADMISSION remains NO.</p>'
            '<form method="post" action="/api/n01/login"><input type="hidden" name="csrf" value="'+self.__csrf+'">'
            +label+'<button type="submit">Continue</button></form></html>').encode()
        handler.wfile.write(page)
    def current_projection(self):
        require(self.__state=='CURRENT')
        self.__gate()
        return self.__context.recheck()
    def render_current(self,challenge,view,*,now_ms):
        require(self.__state=='CURRENT')
        return presentation.render(challenge,view,csrf=self.__csrf,now_ms=now_ms)
    def compare_current_decision(self,raw,shown,headers,*,expected_host,now_ms):
        require(self.__state=='CURRENT')
        # The cookie/CSRF comparison remains inside this private relying party.
        # Native handler validates cardinality before this closed input lens.
        result=presentation.compare_post(raw,shown,csrf=self.__csrf,
            origin=headers.get('Origin'),host=headers.get('Host'),expected_host=expected_host,
            method='POST',content_type=headers.get('Content-Type'),now_ms=now_ms)
        # compare_post already proved equality to the private CSRF. Cookie
        # authentication never exports that value to a controller or audit log.
        self.authenticated_form(headers,csrf=self.__csrf)
        self.__gate()
        return result
    def __gate(self):
        now=int(time.time()*1000)
        require(self.__fence.public_review.valid_from_ms<=self.__started<=self.__last_wall<=now<self.__until
                and time.monotonic()>=self.__last_monotonic)
        if self.__state=='CURRENT':
            require(type(self.__context) is CurrentSession)
            self.__context.recheck()
        else:require(0<=time.monotonic()-self.__monotonic<120)
        require(self.__client.sync_client._session is self.__transport
                and self.__client.sync_client.project_id==owner.PROJECT)
        fence=self.__fence.gate_reader()
        enrollment=fence.current_source()
        history=fence.read(valid_until=datetime.fromtimestamp(self.__fence.public_review.valid_until_ms/1000,timezone.utc))
        self.__ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
        rows=[control.decode(row.value) for row in history.states[-1].checked.rows]
        root=next(value for value in rows if value['family']=='root')
        require(root['quarantine']=='OPEN' and root['incarnation']=='n01-owner-'+enrollment.value['process_nonce'][:32])
        bound=[value for value in rows if value['family']=='binding' and value['state']=='CURRENT']
        require(len(bound)==1 and bound[0]['principal']==enrollment.value['principal'])
        registered=[value for value in rows if value['family']=='registration' and value['state']=='CURRENT']
        require(len(registered)==1 and registered[0]['purpose']=='PRODUCTION'
                and registered[0]['enforcement_sha256']==enrollment.value['artifact_inventory_sha256'])
        require(registered[0]['subject_kind']=='owner-context'
                and registered[0]['adapter_revision']=='n01-owner-controller-v1'
                and registered[0]['issuer_ref']=='n01-owner-only'
                and registered[0]['config_sha256']==enrollment.value['authority_config_sha256'])
        finished=int(time.time()*1000);monotonic=time.monotonic()
        require(now<=finished<self.__until and monotonic>=self.__last_monotonic)
        if self.__state!='CURRENT':require(monotonic-self.__monotonic<120)
        self.__last_wall=finished;self.__last_monotonic=monotonic
        return enrollment
    def send_email(self,email):
        try:
            require(self.__state=='PREAUTH' and type(email) is str and 0<len(email)<=320)
            normalized=email.strip().lower()
            require(hmac.compare_digest(hashlib.sha256(normalized.encode()).hexdigest(),self.__email_sha))
            self.__gate();self.__state='UNKNOWN'
            self.__client.otps.email.send(email=normalized,expiration_minutes=2)
            body=self.__transport._native_body
            require(type(body) is dict and body.get('status_code')==200
                    and type(body.get('email_id')) is str
                    and re.fullmatch(r'email-test-[a-f0-9-]{36}',body['email_id']))
            self.__method=body['email_id'];self.__state='OTP_SENT'
            return 'CURRENT_OWNER_EMAIL_REQUESTED_NONE'
        except Exception:
            self.retire();raise ValueError('N01_OWNER_LOGIN_RETIRED') from None
        finally:self.__transport._native_body=None
    def authenticate_email(self,code):
        try:
            require(self.__state=='OTP_SENT' and type(code) is str and re.fullmatch('[0-9]{6}',code))
            self.__gate();self.__state='UNKNOWN'
            self.__client.otps.authenticate(method_id=self.__method,code=code,session_duration_minutes=15)
            body=self.__transport._native_body
            require(type(body) is dict and body.get('status_code')==200
                    and body.get('user',{}).get('user_id')==owner.OWNER
                    and body.get('session',{}).get('user_id')==owner.OWNER
                    and type(body.get('session_token')) is str and 0<len(body['session_token'])<=8192)
            self.__bearer=body['session_token'];self.__method=None;self.__state='OTP_VERIFIED'
            return 'CURRENT_OWNER_EMAIL_VERIFIED_NONE'
        except Exception:
            self.retire();raise ValueError('N01_OWNER_LOGIN_RETIRED') from None
        finally:self.__transport._native_body=None
    def authenticate_totp(self,code):
        try:
            require(self.__state=='OTP_VERIFIED' and type(code) is str and re.fullmatch('[0-9]{6}',code))
            enrolled=self.__gate();self.__state='UNKNOWN'
            self.__client.totps.authenticate(user_id=owner.OWNER,totp_code=code,session_token=self.__bearer)
            body=self.__transport._native_body
            require(type(body) is dict and body.get('status_code')==200
                    and type(body.get('session_token')) is str and 0<len(body['session_token'])<=8192)
            bearer=body['session_token'];self.__transport._native_body=None;self.__bearer=None
            self.__context=CurrentSession(self.__client,self.__transport,bearer,self.__fence.public_review.keys,
                review_from_ms=self.__fence.public_review.valid_from_ms,review_until_ms=self.__fence.public_review.valid_until_ms,
                operation_until_ms=enrolled.value['expires_at_ms'])
            self.__until=self.__context.deadline_ms;self.__state='CURRENT'
            # Rotate the process-only browser session after fresh MFA.
            self.__cookie=secrets.token_hex(32);self.__csrf=secrets.token_hex(32)
            return self.__context
        except Exception:
            self.retire();raise ValueError('N01_OWNER_LOGIN_RETIRED') from None
        finally:self.__transport._native_body=None
    def retire(self):
        self.__state='RETIRED';self.__cookie=None;self.__csrf=None;self.__method=None;self.__bearer=None
        if self.__context is not None:self.__context.retire()
        self.__context=None;self.__transport.close();self.__client=None
