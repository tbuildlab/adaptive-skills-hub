"""Exact newly approved public review; synthetic storage never grants authority."""
from datetime import datetime,timezone
from pathlib import Path
from dataclasses import replace
import tempfile,unittest
from unittest.mock import patch
from ash import g3_n01_public_review as review
from ash import g3_delegated_control_codec as c
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_owner_sdk_restart as repair
from scripts import build_g3_n01_public_review_custody as writer
from scripts import build_g3_n01_owner_controller as builder
from scripts import g3_n01_owner_controller as service
from tests import test_g3_n01_public_review as old
from tests import test_g3_n01_owner_sdk_bootstrap as sdk

ROOT=Path(__file__).resolve().parents[1]

def materials():
    return tuple(c.canonical(c.decode((ROOT/'research'/name).read_bytes().rstrip())) for name in
        ('nexus-production-n01-pending-public-pin-review-sdk-repair-v2.json','nexus-production-n01-public-pin-owner-acceptance-sdk-repair-v2.json'))

class PublicReviewV2Tests(unittest.TestCase):
    def setUp(self):
        self.pins=review.pins(2);self.now=self.pins.valid_from_ms+1;self.proposal,self.acceptance=materials()
    def verify(self,**kwargs):
        return review.verify_review(self.proposal,self.acceptance,now_ms=kwargs.get('now',self.now),review_generation=2)
    def test_new_approval_exact_generation_without_old_window_extension(self):
        v=self.verify();self.assertEqual(v.pins,self.pins);self.assertEqual(v.authority,'NONE')
        self.assertEqual(c.decode(self.proposal)['approval'],'NOT_OBTAINED')
        self.assertLess(review.UNTIL_MS,self.pins.valid_from_ms)
        with self.assertRaises(ValueError):review.verify_review(self.proposal,self.acceptance,now_ms=self.now)
        with self.assertRaises(ValueError):old.PublicReviewTests().verify(self.proposal,self.acceptance,now=self.now)
    def test_fixed_expiry_unknown_generation_and_acceptance_tamper_deny(self):
        for now in (self.pins.valid_from_ms-1,self.pins.valid_until_ms,True):
            with self.assertRaises(ValueError):self.verify(now=now)
        for generation in (0,3,True):
            with self.assertRaises(ValueError):review.pins(generation)
        changed=c.decode(self.acceptance);changed['approval']='NOT_OBTAINED'
        with self.assertRaises(ValueError):review.verify_review(self.proposal,c.canonical(changed),now_ms=self.now,review_generation=2)
    def test_exact_retained_origin_and_duplicate_denial_without_write(self):
        vector=old.PublicReviewTests();vector.setUp();self.addCleanup(vector.doCleanups)
        client,scope=vector.memory();client.rows.clear()
        client.add(self.pins.prefix+'proposal.json',self.proposal);client.add(self.pins.prefix+'acceptance.json',self.acceptance)
        with patch('time.time',return_value=self.now/1000):
            self.assertEqual(review.read_protected_review(client,scope,now_ms=self.now,review_generation=2),self.verify())
            client.add(self.pins.prefix+'acceptance.json',self.acceptance,duplicate=True)
            with self.assertRaises(ValueError):review.read_protected_review(client,scope,now_ms=self.now,review_generation=2)
        self.assertFalse(any(x[0]=='put' for x in client.calls))
    def test_custody_program_fixed_new_prefix_window_and_no_redispatch(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'op.py';writer.build(path,review_generation=2);code=path.read_text()
        self.assertIn(self.pins.prefix,code);self.assertIn(str(self.pins.valid_until_ms),code)
        self.assertNotIn(str(review.UNTIL_MS),code);self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',code)
        self.assertIn('timedelta(days=7)',code)
    def test_artifact_review_two_is_only_sdk_forward_and_reproducible(self):
        with tempfile.TemporaryDirectory() as folder:
            a=builder.build(Path(folder)/'one',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=repair.PROFILE,review_generation=2)
            b=builder.build(Path(folder)/'two',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=repair.PROFILE,review_generation=2)
            self.assertEqual(a,b);loader=(Path(folder)/'one/source/api/n01-controller.py').read_text()
            self.assertIn('service.REVIEW_GENERATION=2',loader);self.assertIn(str(self.pins.valid_until_ms),loader)
            with self.assertRaises(ValueError):builder.build(Path(folder)/'other',delivery_email_sha256='a'*64,review_generation=2)
        self.assertEqual(a['maximum_ddb_attempts'],280);self.assertEqual(a['real_admission'],'NO')
    def test_old_or_wrong_pin_binding_cannot_be_promoted(self):
        v={'review_generation':2,'application_generation':1,'review_package_sha256':review.PACKAGE_SHA,'review_acceptance_sha256':review.ACCEPTANCE_SHA}
        with self.assertRaises(ValueError):review.enrollment_pins(v)

class CurrentReviewV2LifecycleTests(unittest.TestCase):
    def test_full_forward_lifecycle_keeps_historical_authorizations_and_cost_bound(self):
        vector=sdk.SDKRepairRetirementTests();vector.setUp();self.addCleanup(vector.doCleanups)
        pins=review.pins(2);vector.now=pins.valid_from_ms+1000;vector.vector.now=vector.now
        vector.vector.fixture.source_vector.review=review.verify_review(*materials(),now_ms=vector.now,review_generation=2)
        import sys
        class CurrentDate(datetime):
            @classmethod
            def now(cls,tz=None):return cls.fromtimestamp(vector.now/1000,tz)
        for name,module in list(sys.modules.items()):
            value=getattr(module,'datetime',None)
            if 'g3_' in name and isinstance(value,type) and issubclass(value,datetime):
                p=patch.object(module,'datetime',CurrentDate);p.start();self.addCleanup(p.stop)
        with patch.object(service,'REVIEW_GENERATION',2),patch.object(service,'UNTIL',CurrentDate.fromtimestamp(pins.valid_until_ms/1000,timezone.utc)):
            vector.test_full_long_history_identity_gates_and_three_commits_fit_existing_aggregate()
        self.assertLessEqual(vector.budget_observation['ddb'],280)
