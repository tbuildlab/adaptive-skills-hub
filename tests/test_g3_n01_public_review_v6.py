"""Exact v6 selectors and restrictive cutoff; offline TEST_ONLY/NONE."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import copy
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime,timezone
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import Mock,patch
from ash import g3_primary_ledger as primary
from ash import g3_n01_owner_auth_restart as auth
from ash import g3_n01_owner_atomic_restart as atomic
from ash import g3_n01_owner_sdk_restart as prior
from ash import g3_n01_owner_state as state
from ash import g3_n01_owner_protocol as protocol
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_public_review as review
from ash import g3_n01_owner_context as owner
from ash import g3_n02_presentation as page
from ash import g3_n01_controller_bootstrap as boot
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as c
from scripts import g3_n01_owner_controller as service
from scripts import build_g3_n01_owner_controller as builder
from tests import test_g3_primary_ledger as original
from tests import test_g3_n01_owner_sdk_bootstrap as sdk
from tests import test_g3_n01_owner_state as fixture
from tests import test_g3_n01_public_review_v2 as public_fixture
from tests import test_g3_n01_native_transport as native_fixture

from tests import test_g3_n01_atomic_reads as atomic_fixture
from tests import test_g3_n01_public_review_v4 as v4_fixture
from scripts import build_g3_n01_public_review_custody as review_writer
from scripts import build_g3_n01_owner_source_custody as source_writer
from tests import test_build_g3_n01_owner_source_custody as source_fixture


from ash import g3_n01_public_review as review
from ash import g3_n01_owner_ingress as ingress
from ash import g3_delegated_control_codec as codec
from tests import test_g3_n01_owner_ingress as fixture
from scripts import build_g3_n01_owner_controller as builder
from scripts import build_g3_n01_public_review_custody as writer
ROOT=Path(__file__).resolve().parents[1]
PROFILE='OWNER_AUTH_ATTEMPT_FORWARD_V1'
def materials():
    return tuple(codec.canonical(codec.decode((ROOT/'research'/name).read_bytes().strip())) for name in ('nexus-production-n01-pending-public-pin-review-auth-continuation-v6.json','nexus-production-n01-public-pin-owner-acceptance-auth-continuation-v6.json'))
class V6ReviewTests(unittest.TestCase):
    def test_exact_review_rejects_expiry_wrong_profile_and_old_acceptance(self):
        pins=review.auth_attempt_v6_pins();proposal,acceptance=materials()
        result=review.verify_review(proposal,acceptance,now_ms=pins.valid_from_ms,review_generation=6,restart_profile=PROFILE)
        self.assertEqual(result.authority,'NONE');self.assertEqual(result.pins,pins)
        for now in (pins.valid_from_ms-1,pins.valid_until_ms):
            with self.assertRaises(ValueError):review.verify_review(proposal,acceptance,now_ms=now,review_generation=6,restart_profile=PROFILE)
        for generation,profile in ((5,PROFILE),(6,None),(6,'OWNER_ATOMIC_FORWARD_V1'),(7,PROFILE)):
            with self.assertRaises(ValueError):review.verify_review(proposal,acceptance,now_ms=pins.valid_from_ms,review_generation=generation,restart_profile=profile)
        old=(ROOT/'research/nexus-production-n01-public-pin-owner-acceptance-auth-continuation-v5.json').read_bytes().strip()
        with self.assertRaises(ValueError):review.verify_review(proposal,old,now_ms=pins.valid_from_ms,review_generation=6,restart_profile=PROFILE)
    def test_exact_builder_retains_all_budget_reserves_and_new_custody_namespace(self):
        with tempfile.TemporaryDirectory() as name:
            target=Path(name)
            built=builder.build(target/'artifact',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=PROFILE,review_generation=6)
            self.assertEqual(built['lifecycle_amendment_sha256'],'0673285cf0739b1a17cc0fee35f616718246c81cda673a1bb58def452b9793f5')
            self.assertEqual((built['maximum_ddb_attempts'],built['approved_aggregate_ddb_attempts'],built['maximum_s3_attempts'],built['total_new_s3_attempts_limit']),(189,537,15936,16000))
            self.assertEqual(built['operational_cutoff_ms'],1791899100000)
            written=writer.build(target/'r.py',review_generation=6,restart_profile=PROFILE)
            self.assertEqual((written['maximum_s3_attempts'],written['new_objects']),(16,2))
            self.assertIn('n01-public-review-auth-continuation-v6-r-receipt.json',(target/'r.py').read_text())
    def test_cutoff_denies_before_preauth_private_state_allocation(self):
        vector=fixture.OwnerIngressTests();vector.setUp();self.addCleanup(vector.doCleanups)
        pins=review.auth_attempt_v6_pins()
        vector.protocol.fence.public_review=review.verify_review(*materials(),now_ms=pins.valid_from_ms,review_generation=6,restart_profile=PROFILE)
        def create():return ingress.OwnerIngress(vector.client,vector.native,vector.protocol.fence,vector.protocol.ledger,delivery_email_sha256='a'*64)
        with patch('time.time',return_value=(1791899100000-1)/1000):
            self.assertEqual(create().state,'PREAUTH')
        for now in (1791899100000,pins.valid_until_ms-120000):
            with patch('time.time',return_value=now/1000),patch.object(ingress.secrets,'token_hex') as private_nonce,self.assertRaises(ValueError):create()
            private_nonce.assert_not_called()

BUDGET_OBSERVATIONS={}
PairClient=atomic_fixture.PairClient
class V6SemanticTests(unittest.TestCase):
    def setUp(self):
        from tests import test_g3_n01_auth_continuation as prior_profile
        self.fixture=prior_profile.AuthContinuationTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        for name in ('history','custody_client','env'):
            setattr(self,name,getattr(self.fixture,name))
        self.pins=review.auth_attempt_v6_pins();self.now=self.pins.valid_from_ms+1000
        self.public=review.verify_review(*materials(),now_ms=self.now,review_generation=6,restart_profile=PROFILE)
        import datetime as native_datetime,sys
        class V6FixtureDateTime(native_datetime.datetime):
            @classmethod
            def now(cls,tz=None):return cls.fromtimestamp(self.now/1000,tz)
        for name,module in list(sys.modules.items()):
            value=getattr(module,'datetime',None)
            if 'g3_' in name and isinstance(value,type) and issubclass(value,native_datetime.datetime):
                clock=patch.object(module,'datetime',V6FixtureDateTime);clock.start();self.addCleanup(clock.stop)
    def run_model(self,paired,choice='DENY'):
        client=PairClient();head=self.history.checkpoints[-1]
        ledger=primary.DelegatedDynamoReservations(client,table_arn=original.ARN,instance=custody.INSTANCE,max_attempts=537)
        client.items['HEAD']=dict(ledger._key('HEAD'),phase={'S':'READY'},checkpoint={'B':head},sequence={'N':'10'})
        client.items['blob#'+c.digest(head)]=dict(ledger._key('blob#'+c.digest(head)),body={'B':head})
        native=Mock(primary=client,custody=self.custody_client,ddb_attempts=0,s3_attempts=0)
        prior_rows=copy.deepcopy(native.custody.rows);native.custody.calls.clear()
        now=self.now+100
        material=[]
        original_commit=service.OwnerController._commit
        def observed_commit(controller,candidate,objects):
            material.append(dict(transition=c.decode(candidate.checkpoint)['transition_kind'],pages=len(candidate.snapshot.pages),
                objects=len(objects),maximum_page_bytes=max(map(len,candidate.snapshot.pages))))
            return original_commit(controller,candidate,objects)
        with patch.object(service,'RESTART_PROFILE',auth.PROFILE),patch.object(service,'PRIMARY_READ_PROFILE','PAIRED_ATOMIC_V1' if paired else 'SCALAR_V1'),\
            patch.object(service,'CUSTODY_REVISION',3),patch.object(service,'REVIEW_GENERATION',6),patch.object(boot,'PROCESS_NONCE','8'*64),\
            patch.object(service,'UNTIL',datetime.fromtimestamp(self.pins.valid_until_ms/1000,timezone.utc)),patch('time.time',return_value=now/1000),\
            patch.object(service.native,'NativeTransport',return_value=native),patch.object(review,'read_protected_review',return_value=self.public),\
            patch.dict(service.os.environ,{'STYTCH_PROJECT_ID':source.PROJECT,'STYTCH_SECRET':'SYNTHETIC_NON_AUTHORITY'}),\
            patch.object(service,'DELIVERY_EMAIL_SHA','a'*64),patch.object(service.OwnerController,'_OwnerController__maintenance_gate'),\
            patch.object(service.OwnerController,'_commit',observed_commit),redirect_stdout(StringIO()):
            controller=service.OwnerController('SYNTHETIC_ONLY',self.env,'a'*64)
            phases=[('INITIAL_SOURCE_PROPOSAL',len(client.calls))]
            proposal=controller.proposal();raw=c.canonical(proposal['source_proposal']);enrolled=source.EnrolledSource(raw,c.digest(raw))
            native.enable_owner_storage.return_value=enrolled
            native.custody.add(auth.SOURCE_PREFIX+'registration.json',raw)
            native.custody.add(auth.RECOVERY_PREFIX+'00000000000000000011/authorization.json',c.canonical(proposal['recovery_authorization']))
            for operation in ('recover','enroll','login'):
                before=len(client.calls);controller.maintain(operation,None,'SYNTHETIC_ONLY');phases.append((operation.upper(),len(client.calls)-before))
            relying=controller._OwnerController__owner
            before=len(client.calls)
            for _ in range(3):relying._OwnerIngress__gate()
            phases.append(('EMAIL_OTP_TOTP_GATES',len(client.calls)-before))
            projection=owner.OwnerProjection(owner.PROJECT,owner.OWNER,'session-test-12345678-1234-1234-1234-123456789012',now-50,now+900000,'a'*64)
            before=len(client.calls);controller._storage()
            candidate,objects,challenge,view=protocol.prepare_challenge(controller._OwnerController__history,enrolled,projection,deadline_ms=now+200000,nonce='b'*64,now_ms=now)
            controller._commit(candidate,objects);phases.append(('CONTEXT_CHALLENGE',len(client.calls)-before))
            before=len(client.calls)
            for _ in range(2):relying._OwnerIngress__gate()
            shown=page.render(challenge,view,csrf='c'*64,now_ms=now)
            decision=page.UntrustedDecision(choice,shown.challenge_id,shown.view_id,shown.proposal_id,shown.nonce,shown.presentation_sha256)
            controller._storage();candidate,objects=protocol.prepare_decision(controller._OwnerController__history,enrolled,decision,projection,now_ms=now)
            controller._commit(candidate,objects);phases.append(('DECISION_CONSUME',len(client.calls)-before))
            before=len(client.calls);controller._storage()
            candidate,objects=protocol.prepare_revoke_after_consumption(controller._OwnerController__history,enrolled,remote_result='EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY',now_ms=now)
            controller._commit(candidate,objects);controller._storage();controller._quarantine()
            phases.append(('REVOKE_FINAL_OBSERVATION',len(client.calls)-before))
        result=dict(attempts=len(client.calls),phase_calls=phases,items=copy.deepcopy(client.items),s3_attempts=len(native.custody.calls),
            operation_counts={kind:sum(call[0]==kind for call in client.calls) for kind in ('get','atomic_get','put','transact')},material=material)
        native.custody.rows=prior_rows
        return result
    def test_confirm_deny_scalar_equivalence_and_exact_approved_budgets(self):
        for choice in ('CONFIRM','DENY'):
            # Each model starts with the same TEST_ONLY head10 material; no live call.
            paired=self.run_model(True,choice)
            scalar=self.run_model(False,choice)
            self.assertEqual(paired['items'],scalar['items'])
            self.assertEqual(paired['attempts'],174)
            self.assertEqual(paired['s3_attempts'],11940)
            self.assertLessEqual(paired['attempts'],189)
            self.assertLessEqual(348+paired['attempts'],537)
            BUDGET_OBSERVATIONS[choice]=paired

if __name__=='__main__':unittest.main()
