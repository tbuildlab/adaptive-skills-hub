"""Synthetic human-ingress contracts; no codes, secrets or live Owner evidence."""
from email.message import Message
import hashlib
import io
import pickle
import re
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from stytch import Client
from ash import g3_n01_owner_ingress as ingress
from ash import g3_n01_public_review as review
from ash import g3_n01_stytch_transport as transport
from ash import g3_n01_source_enrollment as source
from ash import g3_delegated_control_codec as codec
from tests import test_g3_n01_owner_persistence as fixture
from tests import test_g3_offline_control as control_fixture


class OwnerIngressTests(unittest.TestCase):
    def setUp(self):
        self.protocol=fixture.OwnerPersistenceTests();self.protocol.setUp();self.addCleanup(self.protocol.doCleanups)
        self.native=transport.BoundedStytchSession();self.addCleanup(self.native.close)
        self.client=Client(ingress.owner.PROJECT,'SYNTHETIC_NON_AUTHORITY',environment='test',sync_session=self.native)
        self.email='fixture@example.invalid'
        self.now=review.FROM_MS+1000
        self.clock=patch('time.time',return_value=self.now/1000);self.clock.start();self.addCleanup(self.clock.stop)
        self.rp=ingress.OwnerIngress(self.client,self.native,self.protocol.fence,self.protocol.ledger,
            delivery_email_sha256=hashlib.sha256(self.email.encode()).hexdigest())
        self.gate=patch.object(self.rp,'_OwnerIngress__gate',return_value=SimpleNamespace(value={'expires_at_ms':review.UNTIL_MS}))
        self.mock_gate=self.gate.start();self.addCleanup(self.gate.stop)
        self.email_id='email-test-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    def body(self,value):
        def response(**kwargs):self.native._native_body=value
        return response
    def begin(self):
        with patch.object(self.client.otps.email,'send',side_effect=self.body(dict(status_code=200,email_id=self.email_id))) as call:
            self.rp.send_email(self.email);return call.call_args.kwargs
    def authenticated(self):
        self.begin()
        value=dict(status_code=200,user={'user_id':ingress.owner.OWNER},session={'user_id':ingress.owner.OWNER},
                   session_token='SYNTHETIC_NON_AUTHORITY')
        with patch.object(self.client.otps,'authenticate',side_effect=self.body(value)) as call:
            self.rp.authenticate_email('000000');return call.call_args.kwargs
    def test_email_delivery_only_exact_existing_association_and_two_minute_expiry(self):
        arguments=self.begin()
        self.assertEqual(arguments,dict(email=self.email,expiration_minutes=2))
        self.assertEqual(self.rp.state,'OTP_SENT');self.assertEqual(self.rp.authority,'NONE')
        self.assertIsNone(self.native._native_body)
    def test_unregistered_email_denies_before_source_or_provider(self):
        with patch.object(self.client.otps.email,'send') as call:
            with self.assertRaisesRegex(ValueError,'^N01_OWNER_LOGIN_RETIRED$'):self.rp.send_email('other@example.invalid')
        call.assert_not_called();self.mock_gate.assert_not_called();self.assertEqual(self.rp.state,'RETIRED')
    def test_missing_current_source_denies_before_provider(self):
        self.mock_gate.side_effect=ValueError('source missing')
        with patch.object(self.client.otps.email,'send') as call:
            with self.assertRaises(ValueError):self.rp.send_email(self.email)
        call.assert_not_called()
    def test_unknown_send_is_terminal_and_not_redispatched_or_leaked(self):
        with patch.object(self.client.otps.email,'send',side_effect=TimeoutError('sensitive fixture')) as call:
            for _ in range(2):
                with self.assertRaisesRegex(ValueError,'^N01_OWNER_LOGIN_RETIRED$'):self.rp.send_email(self.email)
        self.assertEqual(call.call_count,1);self.assertIsNone(self.native._native_body)
        self.assertNotIn('SYNTHETIC',repr(self.rp))
    def test_exact_otp_state_sequence_and_no_bearer_in_return(self):
        arguments=self.authenticated()
        self.assertEqual(arguments,dict(method_id=self.email_id,code='000000',session_duration_minutes=15))
        self.assertEqual(self.rp.state,'OTP_VERIFIED');self.assertIsNone(self.native._native_body)
        with patch.object(self.client.otps,'authenticate') as call:
            with self.assertRaises(ValueError):self.rp.authenticate_email('000000')
        call.assert_not_called()
    def test_wrong_owner_or_malformed_response_never_advances_to_mfa(self):
        self.begin()
        value=dict(status_code=200,user={'user_id':'different'},session={'user_id':'different'},session_token='SYNTHETIC_NON_AUTHORITY')
        with patch.object(self.client.otps,'authenticate',side_effect=self.body(value)):
            with self.assertRaises(ValueError):self.rp.authenticate_email('000000')
        self.assertEqual(self.rp.state,'RETIRED');self.assertTrue(self.native.retired)
    def test_mfa_consumes_exact_original_runtime_session_and_rotates_cookie(self):
        self.authenticated()
        context=SimpleNamespace(deadline_ms=self.now+60000,authority='NONE')
        value=dict(status_code=200,session_token='SYNTHETIC_MFA_NON_AUTHORITY')
        with patch.object(self.client.totps,'authenticate',side_effect=self.body(value)) as call,patch.object(ingress,'CurrentSession',return_value=context) as mapped:
            result=self.rp.authenticate_totp('000000')
        self.assertIs(result,context);self.assertEqual(self.rp.state,'CURRENT')
        self.assertEqual(call.call_args.kwargs,dict(user_id=ingress.owner.OWNER,totp_code='000000',session_token='SYNTHETIC_NON_AUTHORITY'))
        self.assertEqual(mapped.call_args.args[2],'SYNTHETIC_MFA_NON_AUTHORITY')
        self.assertIsNone(self.native._native_body)
    def test_invalid_or_early_code_cannot_call_provider(self):
        with patch.object(self.client.otps,'authenticate') as otp,patch.object(self.client.totps,'authenticate') as totp:
            with self.assertRaises(ValueError):self.rp.authenticate_totp('000000')
        otp.assert_not_called();totp.assert_not_called()
    def test_cookie_and_csrf_are_browser_only_bound_not_restorable_or_logged(self):
        class Handler:
            def __init__(self):self.headers=[];self.wfile=io.BytesIO()
            def send_header(self,key,value):self.headers.append((key,value))
        handler=Handler();self.rp.attach_cookie(handler);self.rp.write_form(handler)
        key,cookie=handler.headers[0];self.assertEqual(key,'Set-Cookie')
        self.assertIn('; Path=/; Secure; HttpOnly; SameSite=Strict;',cookie)
        self.assertNotIn('Domain=',cookie)
        csrf=re.search(r'name="csrf" value="([a-f0-9]{64})"',handler.wfile.getvalue().decode()).group(1)
        headers=Message();headers['Cookie']=cookie.split(';')[0]
        self.assertEqual(self.rp.authenticated_form(headers,csrf=csrf),'FORM_MATCH_ONLY_NONE')
        with self.assertRaises(TypeError):pickle.dumps(self.rp)
        with self.assertRaises(ValueError):self.rp.authenticated_form(headers,csrf='b'*64)
        self.assertEqual(self.rp.state,'RETIRED')
    def gate_vector(self):
        value=dict(self.protocol.enrolled.value,process_nonce='b'*64,artifact_inventory_sha256='a'*64,
                   authority_config_sha256='c'*64)
        self.protocol.mock_reader.return_value=source.EnrolledSource(codec.canonical(value),'d'*64)
        root=next(codec.decode(row.value) for row in self.protocol.vector.before.rows
                  if codec.decode(row.value)['family']=='root')
        root.update(quarantine='OPEN',incarnation='n01-owner-'+'b'*32)
        bound=control_fixture.sample('binding');bound.update(principal=value['principal'],schema_version=codec.VERSION)
        registered=control_fixture.sample('registration');registered.update(schema_version=codec.VERSION,
            purpose='PRODUCTION',enforcement_sha256='a'*64,subject_kind='owner-context',
            adapter_revision='n01-owner-controller-v1',issuer_ref='n01-owner-only',config_sha256='c'*64)
        rows=[root,bound,registered]
        def history():
            return SimpleNamespace(checkpoints=(self.protocol.vector.head,),states=(SimpleNamespace(
                checked=SimpleNamespace(rows=tuple(codec.ControlRow.from_value(row) for row in rows))),))
        return rows,history
    def test_native_gate_requires_open_current_owner_and_exact_writer_membership(self):
        self.gate.stop();rows,history=self.gate_vector()
        with patch.object(self.protocol.fence,'read',side_effect=lambda **kwargs:history()),patch.object(self.protocol.ledger,'observe_current'):
            self.assertEqual(self.rp._OwnerIngress__gate().authority,'NONE')
            for position,key,value in ((0,'quarantine','CLOSED'),(0,'incarnation','old-incarnation'),
                                       (1,'principal',dict(rows[1]['principal'],subject='different')),
                                       (2,'enforcement_sha256','d'*64),(2,'purpose','TEST_ONLY')):
                original=rows[position][key];rows[position][key]=value
                with self.assertRaises(ValueError):self.rp._OwnerIngress__gate()
                rows[position][key]=original
    def test_native_gate_rejects_expiry_and_clock_regression_across_source_io(self):
        self.gate.stop();_,history=self.gate_vector()
        with patch.object(self.protocol.fence,'read',side_effect=lambda **kwargs:history()),patch.object(self.protocol.ledger,'observe_current'):
            with patch('time.time',side_effect=[self.now/1000,self.now/1000,(self.now-1)/1000]),self.assertRaises(ValueError):
                self.rp._OwnerIngress__gate()
            with patch('time.time',return_value=(self.now+120000)/1000),self.assertRaises(ValueError):
                self.rp._OwnerIngress__gate()


if __name__=='__main__':unittest.main()
