"""Synthetic native-SDK compatibility; never live enrollment or authority."""
import copy
import json
import pickle
import unittest
from unittest.mock import patch

import requests
from stytch import Client

from ash.g3_n01_runtime_context import CurrentSession
from ash.g3_n01_stytch_transport import BoundedStytchSession
from ash.g3_n01_owner_context import PROJECT
from tests import test_g3_n01_owner_context as vectors
from tests.test_g3_n01_stytch_transport import reply
NOW=vectors.NOW


class CurrentSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):vectors.OwnerContextTests.setUpClass()
    def setUp(self):
        self.vector=vectors.OwnerContextTests();self.transport=BoundedStytchSession()
        self.client=Client(PROJECT,'SYNTHETIC_NON_AUTHORITY',environment='test',sync_session=self.transport)
        self.clock=patch('time.time',return_value=NOW/1000);self.clock.start()
        self.monotonic=patch('time.monotonic',return_value=10000);self.monotonic.start()
    def tearDown(self):
        self.clock.stop();self.monotonic.stop();self.transport.close()
    def response(self):
        value=self.vector.response()
        value.update(request_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',session_token='SYNTHETIC_NON_AUTHORITY')
        value['session']['roles']=[]
        value['session']['authentication_factors'][0]['email_factor']['email_address']='fixture@example.invalid'
        value['user'].update(emails=[],status='active',phone_numbers=[],webauthn_registrations=[],
            providers=[],crypto_wallets=[],biometric_registrations=[],is_locked=False,roles=[])
        return value
    def native(self,value):return reply(json.dumps(value).encode())
    def begin(self):
        return CurrentSession(self.client,self.transport,'SYNTHETIC_NON_AUTHORITY',self.vector.keys,
            review_from_ms=NOW-10000,review_until_ms=NOW+600000,operation_until_ms=NOW+600000)
    def test_current_native_sdk_context_and_recheck_remain_none(self):
        with patch.object(requests.Session,'request',side_effect=[self.native(self.response()),self.native(self.response())]) as native:
            context=self.begin();self.assertEqual(context.authority,'NONE')
            self.assertEqual(context.recheck().authority,'NONE');self.assertEqual(native.call_count,2)
            self.assertEqual(context.deadline_ms,NOW+298000)
            self.assertIsNone(self.transport._native_body)
            self.assertNotIn('SYNTHETIC_NON_AUTHORITY',repr(context));context.retire()
    def test_original_bearer_rotation_denies_despite_same_signed_user(self):
        changed=self.response();changed['session_token']='SYNTHETIC_CHANGED'
        with patch.object(requests.Session,'request',side_effect=[self.native(self.response()),self.native(changed)]):
            context=self.begin()
            with self.assertRaisesRegex(ValueError,'^N01_CURRENT_SESSION_RETIRED$'):context.recheck()
            self.assertTrue(context.retired);self.assertTrue(self.transport.retired)
    def test_session_or_factor_lineage_change_is_terminal(self):
        for change in ('session','factor'):
            with self.subTest(change=change):
                self.transport=BoundedStytchSession()
                self.client=Client(PROJECT,'SYNTHETIC_NON_AUTHORITY',environment='test',sync_session=self.transport)
                changed=self.response()
                if change=='session':changed['session']['session_id']='session-test-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
                else:
                    factor=changed['session']['authentication_factors'][1]
                    factor['last_authenticated_at']=factor['last_authenticated_at'][:-1]+'.000000001Z'
                with patch.object(requests.Session,'request',side_effect=[self.native(self.response()),self.native(changed)]):
                    context=self.begin()
                    with self.assertRaises(ValueError):context.recheck()
                    self.assertTrue(context.retired)
    def test_context_cannot_be_serialized_or_restore_a_bearer(self):
        with patch.object(requests.Session,'request',return_value=self.native(self.response())):
            context=self.begin()
            with self.assertRaisesRegex(TypeError,'N01_SESSION_NOT_RESTORABLE'):pickle.dumps(context)
            with self.assertRaises(TypeError):copy.deepcopy(context)
            context.retire()
    def test_retirement_or_original_deadline_denies_before_http(self):
        with patch.object(requests.Session,'request',return_value=self.native(self.response())) as native:
            context=self.begin()
            with patch('time.time',return_value=(NOW+298000)/1000):
                with self.assertRaises(ValueError):context.recheck()
            self.assertEqual(native.call_count,1);self.assertTrue(context.retired)
            with self.assertRaises(ValueError):context.recheck()
            self.assertEqual(native.call_count,1)
    def test_unknown_native_result_closes_without_retry_or_buffer(self):
        with patch.object(requests.Session,'request',side_effect=[self.native(self.response()),RuntimeError('SYNTHETIC_PRIVATE_ERROR')]) as native:
            context=self.begin()
            with self.assertRaisesRegex(ValueError,'^N01_CURRENT_SESSION_RETIRED$'):context.recheck()
            with self.assertRaises(ValueError):context.recheck()
            self.assertEqual(native.call_count,2);self.assertIsNone(self.transport._native_body)
    def test_exact_native_revoke_and_exact_remote_rejection(self):
        responses=[self.native(self.response()),self.native(self.response()),reply(),
            reply(b'{"status_code":404,"error_type":"session_not_found","request_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}',404)]
        with patch.object(requests.Session,'request',side_effect=responses) as native:
            context=self.begin();self.assertEqual(context.revoke(),'EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY')
            self.assertEqual(native.call_count,4)
            self.assertEqual(set(native.call_args_list[2].kwargs['json']),{'session_id'})
            self.assertTrue(context.retired);self.assertIsNone(self.transport._native_body)
    def test_generic_rejection_does_not_qualify_revoke(self):
        responses=[self.native(self.response()),self.native(self.response()),reply(),reply(status=500)]
        with patch.object(requests.Session,'request',side_effect=responses) as native:
            context=self.begin()
            with self.assertRaises(ValueError):context.revoke()
            self.assertTrue(context.retired);self.assertEqual(native.call_count,4)
    def test_sdk_transport_rebinding_is_rejected_before_unbounded_io(self):
        with patch.object(requests.Session,'request',return_value=self.native(self.response())) as native:
            context=self.begin()
            self.client.sync_client._SyncClient__session=requests.Session()
            with self.assertRaises(ValueError):context.recheck()
            self.assertEqual(native.call_count,1);self.assertTrue(context.retired)


if __name__=='__main__':unittest.main()
