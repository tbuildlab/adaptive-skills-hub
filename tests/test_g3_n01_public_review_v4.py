"""Exact approved v4 public pins; offline evidence never grants authority."""
from pathlib import Path
from datetime import datetime,timezone
import tempfile,unittest
from unittest.mock import patch
from ash import g3_n01_public_review as review
from ash import g3_delegated_control_codec as codec
from ash import g3_n01_owner_atomic_restart as atomic
from scripts import g3_n01_owner_controller as service
from scripts import build_g3_n01_owner_controller as artifact
from scripts import build_g3_n01_public_review_custody as writer
from scripts import build_g3_n01_owner_source_custody as source_writer
from tests import test_build_g3_n01_owner_source_custody as source_fixture
from tests import test_g3_n01_public_review as old
from tests import test_g3_n01_atomic_reads as model
from tests import test_g3_n01_native_transport as fixture

ROOT=Path(__file__).resolve().parents[1]
BUDGET_OBSERVATIONS={}
def materials():
    return tuple(codec.canonical(codec.decode((ROOT/'research'/name).read_bytes().strip())) for name in
        ('nexus-production-n01-pending-public-pin-review-atomic-v4.json','nexus-production-n01-public-pin-owner-acceptance-atomic-v4.json'))

class PublicReviewV4Tests(unittest.TestCase):
    def setUp(self):self.pins=review.current_atomic_pins();self.now=self.pins.valid_from_ms+1000
    def verify(self,**kw):return review.verify_review(*materials(),now_ms=kw.get('now',self.now),review_generation=4,restart_profile=kw.get('profile',atomic.PROFILE))
    def test_exact_separate_approval_retains_old_windows_and_pending_bytes(self):
        value=self.verify();self.assertEqual(value.pins,self.pins);self.assertEqual(value.authority,'NONE')
        self.assertEqual(codec.decode(materials()[0])['approval'],'NOT_OBTAINED')
        self.assertLess(review.atomic_pins().valid_until_ms,self.pins.valid_from_ms)
        with self.assertRaises(ValueError):review.select_pins(4,restart_profile=atomic.PROFILE)
        for profile in (None,'OWNER_SDK_REPAIR_FORWARD_V1'):
            with self.assertRaises(ValueError):self.verify(profile=profile)
        with self.assertRaises(ValueError):review.current_pins(5,restart_profile=atomic.PROFILE)
    def test_expiry_wrong_digest_old_acceptance_and_mutation_deny(self):
        for now in (self.pins.valid_from_ms-1,self.pins.valid_until_ms,True):
            with self.assertRaises(ValueError):self.verify(now=now)
        proposal,acceptance=materials();altered=codec.decode(acceptance);altered['approval']='NOT_OBTAINED'
        for raw in (codec.canonical(altered),(ROOT/'research/nexus-production-n01-public-pin-owner-acceptance-atomic-v3.json').read_bytes().strip()):
            with self.assertRaises(ValueError):review.verify_review(proposal,raw,now_ms=self.now,review_generation=4,restart_profile=atomic.PROFILE)
    def test_independent_exact_versions_and_retention_are_required(self):
        vector=old.PublicReviewTests();vector.setUp();self.addCleanup(vector.doCleanups)
        client,scope=vector.memory();client.rows.clear()
        for name,raw in zip(('proposal.json','acceptance.json'),materials()):client.add(self.pins.prefix+name,raw)
        with patch('time.time',return_value=self.now/1000):
            self.assertEqual(review.read_protected_review(client,scope,now_ms=self.now,review_generation=4,restart_profile=atomic.PROFILE),self.verify())
            self.assertEqual(len(client.calls),6)
            client.add(self.pins.prefix+'acceptance.json',materials()[1],duplicate=True)
            with self.assertRaises(ValueError):review.read_protected_review(client,scope,now_ms=self.now,review_generation=4,restart_profile=atomic.PROFILE)
        self.assertFalse(any(row[0]=='put' for row in client.calls))
    def test_native_selector_passes_exact_four_without_reset_or_expired_sdk_dispatch(self):
        vector=fixture.NativeTransportTests();vector.setUp();self.addCleanup(vector.doCleanups)
        native=service.native;native._BUDGET['ddb']=19
        with patch('time.time',return_value=self.now/1000):
            driver=native.NativeTransport('SYNTHETIC_ONLY',review_generation=4,review_profile=atomic.PROFILE)
            self.assertEqual(driver.ddb_attempts,19);driver.close()
        before=len(vector.trace)
        with patch('time.time',return_value=self.pins.valid_until_ms/1000),self.assertRaises(ValueError):
            native.NativeTransport('SYNTHETIC_ONLY',review_generation=4,review_profile=atomic.PROFILE)
        self.assertEqual(before,len(vector.trace));self.assertEqual(native._BUDGET['ddb'],19)
        with patch.object(service,'REVIEW_GENERATION',4),patch.object(service,'RESTART_PROFILE',atomic.PROFILE),patch.object(native,'NativeTransport') as factory:
            service.native_transport('SYNTHETIC_ONLY');factory.assert_called_once_with('SYNTHETIC_ONLY',review_generation=4,review_profile=atomic.PROFILE)
            self.assertEqual(service.current_review(),self.pins)
    def test_exact_builders_no_redispatch_prefix_and_two_item_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            result=artifact.build(path/'artifact',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=atomic.PROFILE,review_generation=4)
            loader=(path/'artifact/source/api/n01-controller.py').read_text()
            self.assertIn('service.REVIEW_GENERATION=4',loader);self.assertIn('service.native.MAX_DDB=210',loader)
            self.assertEqual(result['approved_aggregate_ddb_attempts'],512);self.assertEqual(result['expected_predecessor'],atomic.HEAD4)
            op=path/'r.py';receipt=writer.build(op,review_generation=4,restart_profile=atomic.PROFILE);code=op.read_text()
            self.assertIn(self.pins.prefix,code);self.assertIn('n01-public-review-atomic-v4-r-receipt.json',code)
            self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',code);self.assertEqual(receipt['maximum_s3_attempts'],16)
            self.assertNotIn(str(review.atomic_pins().valid_until_ms),code)

class V4ForwardLifecycleTests(unittest.TestCase):
    def test_exact_source_writer_keeps_head_eight_epoch_six_and_unique_receipt(self):
        vector=source_fixture.OwnerSourceBuilderTests();vector.setUp();self.addCleanup(vector.doCleanups)
        pins=review.current_atomic_pins();now=pins.valid_from_ms+1000
        value=vector.observation['source_proposal']
        value.update(review_generation=4,review_package_sha256=pins.package_sha256,
            review_acceptance_sha256=pins.acceptance_sha256,issued_at_ms=now,expires_at_ms=pins.valid_until_ms)
        digest=codec.digest(codec.canonical(value));vector.observation['source_sha256']=digest
        auth=vector.observation['recovery_authorization']
        auth.update(source_enrollment_sha256=digest,previous_checkpoint=atomic.HEAD4,
            authority_epoch=6,review_generation=4,expires_at_ms=pins.valid_until_ms)
        vector.observation['recovery_authorization_sha256']=codec.digest(codec.canonical(auth))
        with tempfile.TemporaryDirectory() as folder,patch('time.time',return_value=now/1000):
            path=Path(folder)/'r.py'
            def build(**kw):return source_writer.build(vector.observation,vector.deployment,path,now_ms=now,
                custody_revision=3,restart_profile=atomic.PROFILE,**kw)
            result=build(review_generation=4);code=path.read_text()
            self.assertEqual(result['maximum_s3_attempts'],16)
            self.assertIn(atomic.SOURCE_PREFIX,code);self.assertIn(atomic.RECOVERY_PREFIX+'00000000000000000009/',code)
            self.assertIn('n01-owner-source-atomic-v4-r-receipt.json',code)
            self.assertIn(str(pins.valid_until_ms),code);self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',code)
            for generation in (2,3,5):
                with self.assertRaises(ValueError):build(review_generation=generation)
            auth['previous_checkpoint']=atomic.HEAD3
            vector.observation['recovery_authorization_sha256']=codec.digest(codec.canonical(auth))
            with self.assertRaises(ValueError):build(review_generation=4)

    def test_full_confirm_and_deny_keep_current_review_four_and_all_boundaries(self):
        vector=model.AtomicContinuationTests();vector.setUp();self.addCleanup(vector.doCleanups)
        pins=review.current_atomic_pins();vector.pins=pins;vector.now=pins.valid_from_ms+1000
        vector.public=review.verify_review(*materials(),now_ms=vector.now,review_generation=4,restart_profile=atomic.PROFILE)
        class HistoricalDate(datetime):
            @classmethod
            def now(cls,tz=None):return cls.fromtimestamp(vector.now/1000,tz)
        import sys
        for name,module in list(sys.modules.items()):
            value=getattr(module,'datetime',None)
            if 'g3_' in name and isinstance(value,type) and issubclass(value,datetime):
                p=patch.object(module,'datetime',HistoricalDate);p.start();self.addCleanup(p.stop)
        with patch.object(service,'current_review',return_value=pins):
            for choice in ('CONFIRM','DENY'):
                result=vector.run_model(True,choice)
                self.assertEqual(result['attempts'],174);self.assertEqual(result['items']['HEAD']['sequence'],{'N':'13'})
                self.assertLessEqual(result['s3_attempts'],16000)
                self.assertFalse(any('grant' in key or 'claim' in key or 'intent' in key for key in result['items']))
                BUDGET_OBSERVATIONS[choice]={key:value for key,value in result.items() if key!='items'}

if __name__=='__main__':unittest.main()
