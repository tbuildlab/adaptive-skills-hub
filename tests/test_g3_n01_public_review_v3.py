"""Expired exact v3 history and bounded atomic lifecycle; TEST_ONLY/NONE."""
from datetime import datetime, timezone
from pathlib import Path
import tempfile, unittest
from unittest.mock import patch
from ash import g3_n01_public_review as review
from ash import g3_delegated_control_codec as codec
from ash import g3_n01_owner_atomic_restart as atomic
from scripts import build_g3_n01_owner_controller as builder
from scripts import build_g3_n01_public_review_custody as writer
from scripts import g3_n01_owner_controller as service
from tests import test_g3_n01_public_review as old
from tests import test_g3_n01_atomic_reads as model
from tests import test_g3_n01_native_transport as native_fixture

ROOT=Path(__file__).resolve().parents[1]
BUDGET_OBSERVATIONS={}


def materials():
    return tuple(codec.canonical(codec.decode((ROOT/'research'/name).read_bytes().rstrip())) for name in
        ('nexus-production-n01-pending-public-pin-review-atomic-v3.json',
         'nexus-production-n01-public-pin-owner-acceptance-atomic-v3.json'))


class PublicReviewV3Tests(unittest.TestCase):
    def setUp(self):
        self.pins=review.atomic_pins();self.now=self.pins.valid_from_ms+1000
        self.proposal,self.acceptance=materials()
    def verify(self,**kw):
        return review.verify_review(self.proposal,self.acceptance,now_ms=kw.get('now',self.now),
            review_generation=3,restart_profile=kw.get('profile',atomic.PROFILE))
    def test_exact_historical_approval_cannot_extend_window_or_acceptance(self):
        result=self.verify();self.assertEqual(result.pins,self.pins);self.assertEqual(result.authority,'NONE')
        self.assertEqual(codec.decode(self.proposal)['approval'],'NOT_OBTAINED')
        for now in (self.pins.valid_from_ms-1,self.pins.valid_until_ms,self.pins.valid_until_ms+1,True):
            with self.assertRaises(ValueError):self.verify(now=now)
        for raw_index,field,value in ((0,'valid_until_ms',self.pins.valid_until_ms+1),
                (1,'canonical_review_package_sha256',review.pins(2).package_sha256),
                (1,'approval','NOT_OBTAINED')):
            raws=list(materials());changed=codec.decode(raws[raw_index]);changed[field]=value;raws[raw_index]=codec.canonical(changed)
            with self.assertRaises(ValueError):review.verify_review(*raws,now_ms=self.now,review_generation=3,restart_profile=atomic.PROFILE)
    def test_unknown_generation_and_wrong_lifecycle_deny(self):
        for generation in (3,4,True):
            with self.assertRaises(ValueError):review.pins(generation)
        for profile in (None,'OWNER_SDK_REPAIR_FORWARD_V1','unknown'):
            with self.assertRaises(ValueError):self.verify(profile=profile)
            with self.assertRaises(ValueError):review.require_enrollment_profile(self.pins,profile)
        with self.assertRaises(ValueError):review.select_pins(4,restart_profile=atomic.PROFILE)
        with patch.object(service,'REVIEW_GENERATION',3),patch.object(service,'RESTART_PROFILE',atomic.PROFILE):
            self.assertEqual(service.current_review(),self.pins)
    def test_exact_r_versions_retention_and_duplicate_denial_without_write(self):
        vector=old.PublicReviewTests();vector.setUp();self.addCleanup(vector.doCleanups)
        client,scope=vector.memory();client.rows.clear()
        client.add(self.pins.prefix+'proposal.json',self.proposal);client.add(self.pins.prefix+'acceptance.json',self.acceptance)
        with patch('time.time',return_value=self.now/1000):
            result=review.read_protected_review(client,scope,now_ms=self.now,review_generation=3,restart_profile=atomic.PROFILE)
            self.assertEqual(result,self.verify());self.assertEqual(len(client.calls),6)
            client.add(self.pins.prefix+'acceptance.json',self.acceptance,duplicate=True)
            with self.assertRaises(ValueError):review.read_protected_review(client,scope,now_ms=self.now,review_generation=3,restart_profile=atomic.PROFILE)
        self.assertFalse(any(row[0]=='put' for row in client.calls))
    def test_builders_remain_exact_reproducible_and_budget_capped(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            a=builder.build(path/'one',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=atomic.PROFILE,review_generation=3)
            b=builder.build(path/'two',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=atomic.PROFILE,review_generation=3)
            self.assertEqual(a,b)
            loader=(path/'one/source/api/n01-controller.py').read_text()
            self.assertIn('service.REVIEW_GENERATION=3',loader);self.assertIn('service.native.MAX_DDB=210',loader)
            self.assertEqual(a['approved_aggregate_ddb_attempts'],512);self.assertEqual(a['expected_predecessor'],atomic.HEAD4)
            op=path/'r.py';receipt=writer.build(op,review_generation=3,restart_profile=atomic.PROFILE)
            code=op.read_text();self.assertIn(self.pins.prefix,code);self.assertIn('n01-public-review-atomic-v3-r-receipt.json',code)
            self.assertIn(str(self.pins.valid_until_ms),code);self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',code)
            self.assertEqual(receipt['maximum_s3_attempts'],16)
            with self.assertRaises(ValueError):builder.build(path/'bad',delivery_email_sha256='a'*64,transport_revision=3,restart_profile='OWNER_SDK_REPAIR_FORWARD_V1',review_generation=3)
    def test_native_generation_three_keeps_shared_budget_and_denies_expiry_before_sdk(self):
        vector=native_fixture.NativeTransportTests();vector.setUp();self.addCleanup(vector.doCleanups)
        with patch('time.time',return_value=self.now/1000):
            native=service.native;native._BUDGET['ddb']=17
            driver=native.NativeTransport('SYNTHETIC_ONLY',review_generation=3,review_profile=atomic.PROFILE)
            self.assertEqual(driver.ddb_attempts,17);self.assertEqual(driver.authority,'NONE')
            with patch.object(native.source,'read_protected_source') as reader,self.assertRaises(ValueError):
                driver.enable_owner_storage(None,native_environment={},artifact_inventory_sha256='a'*64,process_nonce='b'*64,restart_profile=atomic.PROFILE)
            reader.assert_not_called();self.assertTrue(driver.retired)
        before=len(vector.trace)
        with patch('time.time',return_value=self.pins.valid_until_ms/1000),self.assertRaises(ValueError):
            native.NativeTransport('SYNTHETIC_ONLY',review_generation=3,review_profile=atomic.PROFILE)
        self.assertEqual(len(vector.trace),before);self.assertEqual(native._BUDGET['ddb'],17)
    def test_new_enrollment_cannot_reuse_old_public_review_digests(self):
        value=dict(application_generation=1,review_generation=3,review_package_sha256=self.pins.package_sha256,
            review_acceptance_sha256=self.pins.acceptance_sha256)
        self.assertEqual(review.enrollment_pins(value),self.pins)
        value['review_acceptance_sha256']=review.pins(2).acceptance_sha256
        with self.assertRaises(ValueError):review.enrollment_pins(value)


class HistoricalV3AtomicLifecycleTests(unittest.TestCase):
    def test_historical_v3_head_eight_confirm_and_deny_models_preserve_budget(self):
        vector=model.AtomicContinuationTests();vector.setUp();self.addCleanup(vector.doCleanups)
        pins=review.atomic_pins();vector.pins=pins;vector.now=pins.valid_from_ms+1000
        vector.public=review.verify_review(*materials(),now_ms=vector.now,review_generation=3,restart_profile=atomic.PROFILE)
        class HistoricalDate(datetime):
            @classmethod
            def now(cls,tz=None):return cls.fromtimestamp(vector.now/1000,tz)
        import sys
        for name,module in list(sys.modules.items()):
            value=getattr(module,'datetime',None)
            if 'g3_' in name and isinstance(value,type) and issubclass(value,datetime):
                p=patch.object(module,'datetime',HistoricalDate);p.start();self.addCleanup(p.stop)
        # The existing model harness retains its historical v2 fixture selector.
        # Supply only the new exact public pins; production source/retirement,
        # primary transactions and R observation contracts execute unchanged.
        with patch.object(service,'current_review',return_value=pins):
            for choice in ('DENY','CONFIRM'):
                result=vector.run_model(True,choice)
                self.assertEqual(result['attempts'],174);self.assertLessEqual(result['s3_attempts'],16000)
                self.assertEqual(result['items']['HEAD']['sequence'],{'N':'13'})
                self.assertFalse(any('grant' in key or 'intent' in key or 'claim' in key for key in result['items']))
                BUDGET_OBSERVATIONS[choice]={key:value for key,value in result.items() if key!='items'}


if __name__=='__main__':unittest.main()
