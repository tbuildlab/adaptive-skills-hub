"""Exact review/custody consistency; fixtures never authenticate Owner intent."""
from dataclasses import replace
from datetime import datetime,timezone
from pathlib import Path
import unittest
from unittest.mock import patch

from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as codec
from ash import g3_n01_public_review as review
from scripts import build_g3_n01_public_review_custody as builder
from scripts import g3_n01_storage_contract as storage
from tests import test_g3_d03_s3_fence as fake

ROOT=Path(__file__).resolve().parents[1]


class PublicReviewTests(unittest.TestCase):
    def setUp(self):
        self.proposal=codec.canonical(codec.decode((ROOT/'research/nexus-production-n01-pending-public-pin-review-v1.json').read_bytes().rstrip()))
        self.acceptance=codec.canonical(codec.decode((ROOT/'research/nexus-production-n01-public-pin-owner-acceptance-v1.json').read_bytes().rstrip()))
        self.now=review.FROM_MS+1
        self.clock=patch('ash.g3_n01_public_review.time.time',return_value=self.now/1000)
        self.clock.start();self.addCleanup(self.clock.stop)
    def verify(self,p=None,a=None,now=None):
        return review.verify_review(self.proposal if p is None else p,self.acceptance if a is None else a,
                                   now_ms=self.now if now is None else now)
    def test_exact_approval_constrains_public_pins_only(self):
        result=self.verify();self.assertEqual(result.authority,'NONE')
        self.assertEqual(result.package_sha256,review.PACKAGE_SHA)
        self.assertEqual(result.keys,tuple(codec.decode(self.proposal)['keys']))
        self.assertEqual(codec.decode(self.proposal)['approval'],'NOT_OBTAINED')
    def test_fixed_interval_never_extends(self):
        for now in (review.FROM_MS-1,review.UNTIL_MS,True):
            with self.subTest(now=now),self.assertRaisesRegex(ValueError,'N01_PUBLIC_REVIEW_DENY'):self.verify(now=now)
        self.assertEqual(self.verify(now=review.FROM_MS).valid_until_ms,review.UNTIL_MS)
    def test_scope_generation_key_or_approval_tampering_denies(self):
        for field,value in (('project_id','other'),('application_generation',2),('real_admission','YES'),
                            ('approval','NOT_OBTAINED'),('valid_until_ms',review.UNTIL_MS+1)):
            data=codec.decode(self.acceptance);data[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.verify(a=codec.canonical(data))
        data=codec.decode(self.proposal);data['keys'][0]['n']='changed'
        with self.assertRaises(ValueError):self.verify(p=codec.canonical(data))
    def test_noncanonical_duplicate_oversized_bytes_deny(self):
        for raw in (self.proposal+b'\n',b'{"a":1,"a":2}',b'x'*8193):
            with self.assertRaises(ValueError):self.verify(p=raw)
    def test_forged_dataclass_cannot_substitute_another_key(self):
        with self.assertRaises(ValueError):review.PublicReview(b'[]',review.FROM_MS,review.UNTIL_MS,
            review.PACKAGE_SHA,review.ACCEPTANCE_SHA)
    def memory(self):
        _,_,_,_,registration=storage.inputs(review.CONFIG,1)
        scope=replace(storage.scope(registration),generation=2)
        client=fake.MemoryS3()
        client.add(review.PREFIX+'proposal.json',self.proposal)
        client.add(review.PREFIX+'acceptance.json',self.acceptance)
        return client,scope
    def test_independent_retained_read_has_no_write_or_authority(self):
        client,scope=self.memory()
        result=review.read_protected_review(client,scope,now_ms=self.now)
        self.assertEqual(result.authority,'NONE')
        self.assertFalse(any(call[0]=='put' for call in client.calls))
    def test_expiry_during_io_or_clock_regression_denies(self):
        for finish in (review.UNTIL_MS,self.now-1):
            client,scope=self.memory()
            with patch('ash.g3_n01_public_review.time.time',side_effect=[self.now/1000,finish/1000]),self.assertRaises(ValueError):
                review.read_protected_review(client,scope,now_ms=self.now)
    def test_duplicate_missing_corrupt_expired_or_legacy_custody_denies(self):
        for kind in ('duplicate','missing','corrupt','expired','legacy'):
            client,scope=self.memory()
            key=review.PREFIX+'acceptance.json'
            if kind=='duplicate':client.add(key,self.acceptance,duplicate=True)
            if kind=='missing':del client.rows[key]
            if kind=='corrupt':client.rows[key][0]=('1',b'{}',True)
            if kind=='expired':client.rows[key][0]=('1',self.acceptance,False)
            if kind=='legacy':scope=replace(scope,generation=1)
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                review.read_protected_review(client,scope,now_ms=self.now)


if __name__=='__main__':unittest.main()
