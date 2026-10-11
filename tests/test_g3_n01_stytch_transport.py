"""Isolated SDK/HTTP contract tests; no credentials, provider calls or authority."""
import json
import unittest
from unittest.mock import patch
from io import BytesIO

import requests
from stytch import Client

from ash import g3_n01_stytch_transport as t
from ash.g3_n01_owner_context import PROJECT


def reply(raw=None,status=200,**headers):
    value=requests.Response();value.status_code=status
    value.headers={'Content-Type':'application/json',**headers}
    value.raw=BytesIO(raw or b'{"status_code":200,"request_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}')
    return value


class TransportTests(unittest.TestCase):
    def setUp(self):self.session=t.BoundedStytchSession()
    def tearDown(self):self.session.close()
    def call(self,**kw):
        params=dict(json={'session_token':'SYNTHETIC_NON_AUTHORITY'},
            headers={'Content-Type':'application/json'})
        params.update(kw)
        return self.session.request('POST',t.ORIGIN+'/v1/sessions/authenticate',**params)
    def test_native_sdk_revoke_uses_exact_fixed_post_without_retry(self):
        client=Client(PROJECT,'SYNTHETIC_NON_AUTHORITY',environment='test',sync_session=self.session)
        with patch.object(requests.Session,'request',return_value=reply()) as native:
            result=client.sessions.revoke(session_id='session-test-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
            self.assertEqual(result.status_code,200);self.assertEqual(native.call_count,1)
            args,kw=native.call_args
            self.assertEqual(args,('POST',t.ORIGIN+'/v1/sessions/revoke'))
            self.assertEqual(set(kw['json']),{'session_id'})
            self.assertEqual(kw['timeout'],(3,5));self.assertTrue(kw['verify'])
            self.assertFalse(kw['allow_redirects']);self.assertTrue(kw['stream'])
            self.assertEqual(self.session.attempts,1);self.assertEqual(self.session.authority,'NONE')
    def test_authenticate_requests_no_session_extension_or_local_jwt_cache(self):
        client=Client(PROJECT,'SYNTHETIC_NON_AUTHORITY',environment='test',sync_session=self.session)
        # This native response intentionally lacks identity: SDK model validation
        # must deny it. Its actual request still proves direct remote selection.
        with patch.object(requests.Session,'request',return_value=reply()) as native:
            with self.assertRaises(Exception):client.sessions.authenticate(session_token='SYNTHETIC_NON_AUTHORITY')
            self.assertEqual(native.call_count,1)
            self.assertEqual(native.call_args.args,('POST',t.ORIGIN+'/v1/sessions/authenticate'))
            self.assertEqual(set(native.call_args.kwargs['json']),{'session_token'})
    def test_wrong_origin_path_query_method_or_extra_body_never_reaches_http(self):
        with patch.object(requests.Session,'request') as native:
            for method,url,body in (
                ('GET',t.ORIGIN+'/v1/sessions/authenticate',{'session_token':'SYNTHETIC'}),
                ('POST','https://api.stytch.com/v1/sessions/authenticate',{'session_token':'SYNTHETIC'}),
                ('POST',t.ORIGIN+'/v1/sessions/authenticate?x=1',{'session_token':'SYNTHETIC'}),
                ('POST',t.ORIGIN+'/v1/users/create',{}),
                ('POST',t.ORIGIN+'/v1/sessions/authenticate',{'session_token':'SYNTHETIC','session_duration_minutes':15}),
            ):
                with self.subTest(method=method,url=url):
                    session=t.BoundedStytchSession()
                    with self.assertRaisesRegex(ValueError,'^N01_IDENTITY_TRANSPORT_DENY$'):
                        session.request(method,url,json=body,headers={'Content-Type':'application/json'})
                    self.assertEqual(session.attempts,0);session.close()
            native.assert_not_called()
    def test_unqualified_http_status_or_wrong_media_type_retires(self):
        for response in (reply(status=302),reply(status=401),reply(status=500),
                reply(**{'Content-Type':'text/html'}),reply(**{'Content-Encoding':'gzip'})):
            with self.subTest(status=response.status_code):
                session=t.BoundedStytchSession()
                with patch.object(requests.Session,'request',return_value=response) as native:
                    with self.assertRaises(ValueError):
                        session.post(t.ORIGIN+'/v1/sessions/authenticate',json={'session_token':'SYNTHETIC'},
                            headers={'Content-Type':'application/json'})
                    self.assertTrue(session.retired);self.assertIsNone(session._native_body)
                    with self.assertRaises(ValueError):session.post(t.ORIGIN+'/v1/sessions/authenticate',json={})
                    self.assertEqual(native.call_count,1)
                session.close()
    def test_unknown_io_is_sanitized_terminal_and_not_retried(self):
        with patch.object(requests.Session,'request',side_effect=RuntimeError('SYNTHETIC_PRIVATE_DIAGNOSTIC')) as native:
            with self.assertRaisesRegex(ValueError,'^N01_IDENTITY_TRANSPORT_DENY$'):self.call()
            with self.assertRaises(ValueError):self.call()
            self.assertEqual(native.call_count,1);self.assertEqual(self.session.attempts,1)
    def test_duplicate_json_nan_oversize_and_wrong_length_are_closed(self):
        for raw,headers in ((b'{"status_code":200,"status_code":200}',{}),
                (b'{"status_code":200,"n":NaN}',{}),(b' '*65537,{}),
                (b'{"status_code":200}',{'Content-Length':'1'}),
                (b'{"status_code":200.0}',{})):
            session=t.BoundedStytchSession()
            with patch.object(requests.Session,'request',return_value=reply(raw,**headers)):
                with self.assertRaises(ValueError):session.request('POST',t.ORIGIN+'/v1/sessions/authenticate',
                    json={'session_token':'SYNTHETIC'},headers={'Content-Type':'application/json'})
                self.assertTrue(session.retired);self.assertIsNone(session._native_body)
            session.close()
    def test_exact_session_not_found_is_distinct_from_generic_404(self):
        raw=b'{"status_code":404,"error_type":"session_not_found"}'
        with patch.object(requests.Session,'request',return_value=reply(raw,404)):
            response=self.call();self.assertEqual(response.status_code,404)
            self.assertEqual(self.session._native_body['error_type'],'session_not_found')
        for raw in (b'{"status_code":404,"error_type":"other"}',
                    b'{"status_code":404,"error_type":"session_not_found","unknown":true}'):
            with patch.object(requests.Session,'request',return_value=reply(raw,404)):
                with self.assertRaises(ValueError):self.call()
    def test_bounded_attempts_and_closed_session_never_call_http(self):
        self.session.attempts=t.MAX_ATTEMPTS
        with patch.object(requests.Session,'request') as native:
            with self.assertRaises(ValueError):self.call()
            native.assert_not_called()
        self.assertTrue(self.session.retired)
    def test_nanosecond_response_is_preserved_before_sdk_projection(self):
        raw=b'{"status_code":200,"time":"2026-10-11T00:00:00.000000001Z"}'
        with patch.object(requests.Session,'request',return_value=reply(raw)):
            response=self.call()
            self.assertEqual(self.session._native_body['time'],'2026-10-11T00:00:00.000000001Z')
            self.assertEqual(response.json()['time'],self.session._native_body['time'])
    def test_unqualified_proxy_override_or_data_body_denies(self):
        for kw in ({'proxies':{}},{'verify':False},{'allow_redirects':True},{'data':'SYNTHETIC'}):
            session=t.BoundedStytchSession()
            with patch.object(requests.Session,'request') as native:
                with self.assertRaises(ValueError):session.request('POST',t.ORIGIN+'/v1/sessions/authenticate',
                    json={'session_token':'SYNTHETIC'},headers={'Content-Type':'application/json'},**kw)
                native.assert_not_called()
            session.close()
        self.session.mount('https://',requests.adapters.HTTPAdapter(max_retries=1))
        with patch.object(requests.Session,'request') as native:
            with self.assertRaises(ValueError):self.call()
            native.assert_not_called()


if __name__=='__main__':unittest.main()
