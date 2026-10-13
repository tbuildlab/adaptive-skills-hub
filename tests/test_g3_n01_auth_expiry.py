"""Fixed v5 authentication window, inactive HTTP only; no provider dispatch."""
from contextlib import redirect_stdout
from io import BytesIO,StringIO
import unittest
from unittest.mock import patch
from ash import g3_n01_owner_ingress as ingress
from ash import g3_n01_public_review as review
from tests import test_g3_n01_owner_ingress as old
from tests import test_g3_n01_auth_continuation as profile
from tests import test_g3_n01_owner_closed_stages as closed


class AuthExpiryTests(unittest.TestCase):
    def setUp(self):
        self.vector=old.OwnerIngressTests();self.vector.setUp();self.addCleanup(self.vector.doCleanups)
        self.pins=review.auth_attempt_pins();self.now=self.pins.valid_from_ms+1000
        self.vector.protocol.fence.public_review=review.verify_review(*profile.materials(),now_ms=self.now,review_generation=5,restart_profile=profile.auth.PROFILE)
        self.clock=patch('time.time',return_value=self.now/1000);self.clock.start();self.addCleanup(self.clock.stop)
        self.monotonic=patch('time.monotonic',return_value=100);self.monotonic.start();self.addCleanup(self.monotonic.stop)
        self.rp=self.create()
    def create(self):
        return ingress.OwnerIngress(self.vector.client,self.vector.native,self.vector.protocol.fence,self.vector.protocol.ledger,delivery_email_sha256='a'*64)
    def handler(self):
        class Handler:
            def __init__(self):self.wfile=BytesIO();self.headers=[]
            def send_header(self,key,value):self.headers.append((key,value))
        return Handler()
    def test_cookie_and_form_share_original_deadline_without_new_window(self):
        handler=self.handler();output=StringIO()
        with redirect_stdout(output):self.rp.attach_cookie(handler);self.rp.write_form(handler)
        self.assertTrue(handler.headers[0][1].endswith('Max-Age=120'))
        self.assertIn(b'Authentication deadline (UTC)',handler.wfile.getvalue())
        with patch('time.time',return_value=(self.now+100000)/1000),patch('time.monotonic',return_value=200),redirect_stdout(output):
            next_handler=self.handler();self.rp.attach_cookie(next_handler);self.rp.write_form(next_handler)
        self.assertTrue(next_handler.headers[0][1].endswith('Max-Age=20'))
        self.assertEqual(self.rp._OwnerIngress__until,self.now+120000)
        self.assertTrue(any(row['stage']=='TIME_WINDOW' and row['result']=='PASS' for row in closed.stages(output.getvalue())))
        self.assertNotIn('Set-Cookie',output.getvalue());self.assertNotIn('csrf',output.getvalue())
    def test_expired_get_does_not_deliver_form_or_call_provider_and_is_terminal(self):
        handler=self.handler();output=StringIO()
        with patch('time.time',return_value=(self.now+120000)/1000),redirect_stdout(output),patch.object(self.vector.client.otps.email,'send') as send:
            with self.assertRaises(ValueError):self.rp.write_form(handler)
        self.assertEqual(handler.wfile.getvalue(),b'');self.assertEqual(self.rp.state,'RETIRED');send.assert_not_called()
        self.assertEqual(closed.stages(output.getvalue())[-1]['stage'],'TIME_WINDOW')
        with self.assertRaises(ValueError):self.rp.write_form(handler)
    def test_full_120_seconds_must_fit_fixed_review(self):
        for now in (self.pins.valid_from_ms-1,self.pins.valid_until_ms-119999,self.pins.valid_until_ms):
            with patch('time.time',return_value=now/1000),self.assertRaises(ValueError):self.create()
    def test_wall_or_monotonic_rollback_denies_and_no_window_reset(self):
        for wall,mono in ((self.now-1,100),(self.now,99),(self.now+119000,220)):
            with patch('time.time',return_value=self.now/1000),patch('time.monotonic',return_value=100):rp=self.create()
            with patch('time.time',return_value=wall/1000),patch('time.monotonic',return_value=mono),redirect_stdout(StringIO()),self.assertRaises(ValueError):rp.write_form(self.handler())
            self.assertEqual(rp.state,'RETIRED')

if __name__=='__main__':unittest.main()
