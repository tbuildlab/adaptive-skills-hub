"""Synthetic cryptographic/clock compatibility tests, never live D01 or N01."""
import base64
import copy
from datetime import datetime,timezone
import json
import unittest
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from ash import g3_n01_owner_context as p

NOW=1791732600000


class OwnerContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ephemeral synthetic key stays in memory; no private fixture is stored.
        cls.private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        key=json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(cls.private.public_key()))
        # The library emits key_ops; D01's accepted public pin is the closed six-
        # field representation. Normalize synthetic metadata to that contract.
        key.pop('key_ops')
        key.update(kid='jwk-test-'+ 'a'*8+'-'+ 'a'*4+'-'+ 'a'*4+'-'+ 'a'*4+'-'+ 'a'*12,
            alg='RS256',use='sig')
        cls.keys=(key,)
    def signed(self,claims=None,header=None):
        body=dict(iss='stytch.com/'+p.PROJECT,aud=p.PROJECT,sub=p.OWNER,
            iat=NOW//1000-2,nbf=NOW//1000-2,exp=NOW//1000+298)
        body.update(claims or {})
        return jwt.encode(body,self.private,algorithm='RS256',headers=header or {'kid':self.keys[0]['kid']})
    def response(self):
        when=datetime.fromtimestamp((NOW-2000)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        expires=datetime.fromtimestamp((NOW+900000)/1000,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        suffix='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        return dict(status_code=200,session_jwt=self.signed(),user=dict(user_id=p.OWNER,
            totps=[dict(totp_id='totp-test-'+suffix,verified=True)]),session=dict(user_id=p.OWNER,
            session_id='session-test-'+suffix,expires_at=expires,authentication_factors=[
            dict(type='otp',delivery_method='email',last_authenticated_at=when,email_factor=dict(email_id='email-test-'+suffix)),
            dict(type='totp',delivery_method='authenticator_app',last_authenticated_at=when,
                 authenticator_app_factor=dict(totp_id='totp-test-'+suffix))]))
    def check(self,value,**kw):
        params=dict(review_from_ms=NOW-10000,review_until_ms=NOW+10000,now_ms=NOW);params.update(kw)
        return p.project_current_owner(value,self.keys,**params)
    def test_signed_metadata_remains_none_and_contains_no_bearer(self):
        value=self.check(self.response());self.assertEqual(value.authority,'NONE')
        self.assertEqual(value.provider_user,p.OWNER);self.assertNotIn('eyJ',repr(value))
    def test_wrong_issuer_audience_or_subject_denies(self):
        for claim in ({'iss':'unqualified'},{'aud':[p.PROJECT,'other']},{'sub':'other'}):
            with self.subTest(claim=claim):
                value=self.response();value['session_jwt']=self.signed(claim)
                with self.assertRaisesRegex(ValueError,'N01_CURRENT_OWNER_DENY'):self.check(value)
    def test_review_or_signed_expiry_is_exclusive(self):
        value=self.response()
        with self.assertRaises(ValueError):self.check(value,review_until_ms=NOW)
        value['session_jwt']=self.signed({'exp':NOW//1000})
        with self.assertRaises(ValueError):self.check(value)
        value['session_jwt']=self.signed({'iat':NOW//1000-300})
        with self.assertRaises(ValueError):self.check(value)
    def test_wrong_native_user_or_session_shape_denies(self):
        for mutate in (lambda v:v['session'].update(user_id='wrong'),
                       lambda v:v['user'].update(user_id='wrong'),
                       lambda v:v['session'].update(session_id='arbitrary')):
            value=self.response();mutate(value)
            with self.assertRaises(ValueError):self.check(value)
    def test_missing_duplicate_or_unverified_factors_deny(self):
        for mutate in (lambda v:v['session']['authentication_factors'].pop(),
                       lambda v:v['session']['authentication_factors'].append(copy.deepcopy(v['session']['authentication_factors'][0])),
                       lambda v:v['user']['totps'][0].update(verified=False)):
            value=self.response();mutate(value)
            with self.assertRaises(ValueError):self.check(value)
    def test_duplicate_signed_json_and_wrong_algorithm_deny(self):
        encoded=self.signed();parts=encoded.split('.')
        raw=b'{"alg":"RS256","alg":"RS256","kid":"ignored"}'
        parts[0]=base64.urlsafe_b64encode(raw).rstrip(b'=').decode()
        value=self.response();value['session_jwt']='.'.join(parts)
        with self.assertRaises(ValueError):self.check(value)
        value['session_jwt']=jwt.encode({'sub':p.OWNER},'SYNTHETIC_NOT_AUTHORITY_32_BYTES_MINIMUM',algorithm='HS256')
        with self.assertRaises(ValueError):self.check(value)
    def test_nanosecond_lineage_change_cannot_be_hidden_by_ms_projection(self):
        first=self.response();second=copy.deepcopy(first)
        old=second['session']['authentication_factors'][1]['last_authenticated_at']
        second['session']['authentication_factors'][1]['last_authenticated_at']=old[:-1]+'.000000001Z'
        a=self.check(first);b=self.check(second)
        self.assertEqual(a.authenticated_at_ms,b.authenticated_at_ms)
        self.assertNotEqual(a.factor_lineage_sha256,b.factor_lineage_sha256)
        with self.assertRaises(ValueError):p.same_current_session(a,b)
    def test_provider_error_is_fixed_and_status_cannot_be_float(self):
        for status in (200.0,401,500):
            value=self.response();value['status_code']=status
            with self.assertRaisesRegex(ValueError,'^N01_CURRENT_OWNER_DENY$'):self.check(value)
    def test_unreviewed_or_private_key_members_cannot_enter_public_pin(self):
        for extra in ({'d':'SYNTHETIC_PRIVATE_FIELD_REJECTED'},{'key_ops':['sign']},{'unknown':True}):
            keys=(dict(self.keys[0],**extra),)
            with self.assertRaisesRegex(ValueError,'^N01_CURRENT_OWNER_DENY$'):
                p.project_current_owner(self.response(),keys,review_from_ms=NOW-1000,
                    review_until_ms=NOW+1000,now_ms=NOW)
            unused=dict(self.keys[0],kid='jwk-test-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',**extra)
            with self.assertRaises(ValueError):
                p.project_current_owner(self.response(),self.keys+(unused,),review_from_ms=NOW-1000,
                    review_until_ms=NOW+1000,now_ms=NOW)
        with self.assertRaises(ValueError):
            self.check(self.response(),review_from_ms=NOW-86400000,review_until_ms=NOW+1000)
    def test_signature_and_duplicate_selected_keys_are_rejected(self):
        value=self.response();segments=value['session_jwt'].split('.')
        signature=bytearray(p.part(segments[2],2048));signature[0]^=1
        segments[2]=base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
        value['session_jwt']='.'.join(segments)
        with self.assertRaises(ValueError):self.check(value)
        with self.assertRaises(ValueError):
            p.project_current_owner(self.response(),self.keys+self.keys,review_from_ms=NOW-1000,
                review_until_ms=NOW+1000,now_ms=NOW)
    def test_context_cannot_refresh_or_survive_retirement(self):
        value=p.ContextDeadline(authenticated_at_ms=1000,review_until_ms=999999,
            operation_until_ms=999999,monotonic_start_ms=100)
        self.assertEqual(value.until,301000)
        value.check(now_ms=2000,monotonic_ms=1100);self.assertEqual(value.until,301000)
        with self.assertRaises(ValueError):value.check(now_ms=301000,monotonic_ms=300100)
        with self.assertRaises(ValueError):value.check(now_ms=2000,monotonic_ms=1100)
    def test_clock_regression_and_elapsed_expiry_are_terminal(self):
        for now,elapsed in ((999,100),(2000,99),(2000,300100)):
            value=p.ContextDeadline(authenticated_at_ms=1000,review_until_ms=999999,
                operation_until_ms=999999,monotonic_start_ms=100)
            with self.assertRaises(ValueError):value.check(now_ms=now,monotonic_ms=elapsed)
            self.assertTrue(value.retired)
        value=p.ContextDeadline(authenticated_at_ms=1000,review_until_ms=999999,
            operation_until_ms=999999,monotonic_start_ms=100)
        value.check(now_ms=2000,monotonic_ms=1100)
        with self.assertRaises(ValueError):value.check(now_ms=2100,monotonic_ms=1099)
        self.assertTrue(value.retired)


if __name__=='__main__':unittest.main()
