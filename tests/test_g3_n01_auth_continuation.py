"""Paired observations and exact head-8 continuation models, TEST_ONLY/NONE."""
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

ROOT=Path(__file__).resolve().parents[1]
BUDGET_OBSERVATIONS={}
PairClient=atomic_fixture.PairClient

def materials():
    return tuple(c.canonical(c.decode((ROOT/"research"/name).read_bytes().strip())) for name in ("nexus-production-n01-pending-public-pin-review-auth-continuation-v5.json","nexus-production-n01-public-pin-owner-acceptance-auth-continuation-v5.json"))

class AuthContinuationTests(unittest.TestCase):
    def setUp(self):
        self.old=atomic_fixture.AtomicContinuationTests();self.old.setUp();self.addCleanup(self.old.doCleanups)
        oldpins=review.current_atomic_pins();oldnow=oldpins.valid_from_ms+1000
        recovery=atomic.prepare_forward_recovery(self.old.history,process_nonce='9'*64,now_ms=oldnow)
        head9=fixture.appended(self.old.history,recovery,{})
        value=dict(self.old.current.value,process_nonce='9'*64,artifact_inventory_sha256='a'*64,
            review_generation=4,review_package_sha256=oldpins.package_sha256,review_acceptance_sha256=oldpins.acceptance_sha256,
            issued_at_ms=oldnow,expires_at_ms=oldpins.valid_until_ms)
        raw=c.canonical(value);enrolled=source.EnrolledSource(raw,c.digest(raw))
        candidate,objects=state.prepare_owner_enrollment(head9,enrolled,now_ms=oldnow+1,restart_profile=atomic.PROFILE)
        self.history=fixture.appended(head9,candidate,objects)
        vector=self.old.old.vector.fixture.vector
        self.custody_client=vector.client;self.env=self.old.old.vector.fixture.source_vector.env
        vector.install(recovery.checkpoint,recovery.snapshot,recovery.descriptor,9)
        vector.install(candidate.checkpoint,candidate.snapshot,candidate.descriptor,10)
        for digest,body in objects.items():vector.client.add(custody.NORMAL+'objects/'+digest,body)
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode='DELEGATED_EXECUTOR',
            authority_config_sha256=source.CONFIG,source_enrollment_sha256=enrolled.enrollment_sha256,checkpoint=head9.head,previous_checkpoint=self.old.history.head,
            authority_epoch=6,incarnation='n01-owner-'+'9'*32,application_generation=1,review_generation=4,expires_at_ms=oldpins.valid_until_ms,no_automatic_redispatch='REQUIRED',real_admission='NO')
        auth_raw=c.canonical(authorization)
        vector.client.add(atomic.SOURCE_PREFIX+'registration.json',raw)
        vector.client.add(atomic.RECOVERY_PREFIX+'00000000000000000009/authorization.json',auth_raw)
        for name,val in dict(HEAD4=self.history.head,HEAD3=head9.head,OLD_NONCE='9'*64,OLD_SOURCE_SHA=enrolled.enrollment_sha256,
                OLD_AUTH_SHA=c.digest(auth_raw),OLD_ARTIFACT='a'*64,OLD_ENV=dict(VERCEL_DEPLOYMENT_ID=value['deployment_id'],VERCEL_URL=value['deployment_host'])).items():
            p=patch.object(auth,name,val);p.start();self.addCleanup(p.stop)
        self.pins=review.auth_attempt_pins();self.now=self.pins.valid_from_ms+1000
        self.public=review.verify_review(*materials(),now_ms=self.now,review_generation=5,restart_profile=auth.PROFILE)
        import sys
        class HistoricalDate(datetime):
            @classmethod
            def now(cls,tz=None):return cls.fromtimestamp(self.now/1000,tz)
        for name,module in list(sys.modules.items()):
            value=getattr(module,'datetime',None)
            if 'g3_' in name and isinstance(value,type) and issubclass(value,datetime):
                p=patch.object(module,'datetime',HistoricalDate);p.start();self.addCleanup(p.stop)
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
            patch.object(service,'CUSTODY_REVISION',3),patch.object(service,'REVIEW_GENERATION',5),patch.object(boot,'PROCESS_NONCE','8'*64),\
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
    def test_confirm_deny_scalar_equivalence_full_semantic_budget(self):
        for choice in ('CONFIRM','DENY'):
            scalar=self.run_model(False,choice);paired=self.run_model(True,choice)
            self.assertEqual(scalar['items'],paired['items'])
            self.assertEqual(paired['items']['HEAD']['sequence'],{'N':'15'})
            self.assertLessEqual(paired['attempts'],189)
            self.assertLessEqual(348+paired['attempts'],537)
            self.assertLessEqual(paired['s3_attempts']+32,16000)
            self.assertEqual([(r['pages'],r['objects']) for r in paired['material']],[(3,0),(3,2),(7,8),(9,4),(9,2)])
            self.assertTrue(all(r['maximum_page_bytes']<32768 for r in paired['material']))
            self.assertFalse(any('grant' in key or 'claim' in key or 'intent' in key for key in paired['items']))
            BUDGET_OBSERVATIONS[choice]={key:value for key,value in paired.items() if key!='items'}

    def test_forward_recovery_preserves_history_and_cannot_replay_or_reuse_incarnation(self):
        candidate=auth.prepare_forward_recovery(self.history,process_nonce='8'*64,now_ms=self.now)
        after=fixture.appended(self.history,candidate,{})
        self.assertEqual(after.checkpoints[:-1],self.history.checkpoints)
        self.assertTrue(set(self.history.objects)<=set(after.objects))
        rows=[c.decode(row.value) for row in after.states[-1].checked.rows]
        self.assertTrue(all(row['state']=='RETIRED' for row in rows if row['family']=='source'))
        for history,nonce in ((self.old.history,'8'*64),(after,'8'*64),(self.history,'9'*64),(self.history,'9'*32+'8'*32)):
            with self.assertRaises(ValueError):auth.prepare_forward_recovery(history,process_nonce=nonce,now_ms=self.now)
        self.assertFalse(any(row['family'] in ('context','grant','challenge') for row in rows))

    def test_missing_or_mutated_independent_recover_nine_quarantines(self):
        key=atomic.RECOVERY_PREFIX+'00000000000000000009/authorization.json'
        with patch('time.time',return_value=self.now/1000):
            history=auth.HistoricalOwnerFence(self.custody_client).read(valid_until=datetime.fromtimestamp(self.pins.valid_until_ms/1000,timezone.utc))
            self.assertEqual(history.head,self.history.head)
            self.custody_client.rows.pop(key)
            with self.assertRaises(ValueError):auth.HistoricalOwnerFence(self.custody_client).read(valid_until=datetime.fromtimestamp(self.pins.valid_until_ms/1000,timezone.utc))

    def test_v5_exact_window_acceptance_profile_and_no_authority(self):
        self.assertEqual(self.public.authority,'NONE')
        self.assertEqual(c.decode(materials()[0])['approval'],'NOT_OBTAINED')
        for generation,profile in ((4,auth.PROFILE),(5,atomic.PROFILE),(True,auth.PROFILE),(1,auth.PROFILE)):
            with self.assertRaises(ValueError):review.current_pins(generation,restart_profile=profile)
        for now in (self.pins.valid_from_ms-1,self.pins.valid_until_ms):
            with self.assertRaises(ValueError):review.verify_review(*materials(),now_ms=now,review_generation=5,restart_profile=auth.PROFILE)
        with self.assertRaises(ValueError):review.verify_review(materials()[0],v4_fixture.materials()[1],now_ms=self.now,review_generation=5,restart_profile=auth.PROFILE)

    def test_builder_keeps_cumulative_cost_and_separate_one_attempt(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)
            value=builder.build(target/'artifact',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=auth.PROFILE,review_generation=5)
            loader=(target/'artifact/source/api/n01-controller.py').read_text()
            self.assertIn('service.native.MAX_DDB=189',loader)
            self.assertIn('service.REVIEW_GENERATION=5',loader)
            self.assertEqual(value['prior_ddb_charged_conservative']+value['maximum_ddb_attempts'],value['approved_aggregate_ddb_attempts'])
            self.assertEqual(value['approved_aggregate_ddb_attempts'],537)
            self.assertEqual(value['expected_predecessor'],auth.HEAD4)
            self.assertEqual(value['authentication_attempt_limit'],1)
            self.assertEqual(value['maximum_s3_attempts']+value['independent_r_admin_s3_attempts_reserved'],16000)
            self.assertEqual(value['maximum_s3_writes']+value['independent_r_admin_s3_writes_reserved'],240)
            self.assertEqual(value['maximum_new_bytes_per_backend']+value['independent_r_admin_bytes_reserved'],8388608)
            self.assertEqual(value['real_admission'],'NO')
            review_writer.build(target/'r.py',review_generation=5,restart_profile=auth.PROFILE)
            code=(target/'r.py').read_text();self.assertIn(self.pins.prefix,code)
            self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',code)
            self.assertIn('n01-public-review-auth-continuation-v5-r-receipt.json',code)
            for generation in (1,2,4):
                with self.assertRaises(ValueError):builder.build(target/'bad',delivery_email_sha256='a'*64,transport_revision=3,restart_profile=auth.PROFILE,review_generation=generation)

    def test_native_shared_one_attempt_cap_is_not_reset_on_lease_or_unknown(self):
        vector=native_fixture.NativeTransportTests();vector.setUp();self.addCleanup(vector.doCleanups)
        native=service.native;native._BUDGET['ddb']=188
        with patch('time.time',return_value=self.now/1000),patch.object(native,'MAX_DDB',189):
            driver=native.NativeTransport('SYNTHETIC_ONLY',review_generation=5,review_profile=auth.PROFILE)
            driver.primary.transact_get_items(TransactItems=[{'Get':{'TableName':native.TABLE,'Key':{'pk':{'S':'authority#'+custody.INSTANCE},'sk':{'S':'HEAD'}}}}])
            self.assertEqual(driver.ddb_attempts,189);driver.close()
            next_driver=native.NativeTransport('SYNTHETIC_ONLY',review_generation=5,review_profile=auth.PROFILE)
            before=len(vector.trace)
            with self.assertRaises(ValueError):next_driver.primary.get_item(TableName=native.TABLE,Key={'pk':{'S':'authority#'+custody.INSTANCE},'sk':{'S':'HEAD'}},ConsistentRead=True)
            self.assertEqual(len(vector.trace),before);self.assertEqual(native._BUDGET['ddb'],189)
            self.assertTrue(next_driver.retired)

    def test_source_custody_requires_new_profile_exact_head_ten_and_generation_five(self):
        vector=source_fixture.OwnerSourceBuilderTests();vector.setUp();self.addCleanup(vector.doCleanups)
        value=vector.observation['source_proposal']
        value.update(review_generation=5,review_package_sha256=self.pins.package_sha256,review_acceptance_sha256=self.pins.acceptance_sha256,
            issued_at_ms=self.now,expires_at_ms=self.pins.valid_until_ms)
        digest=c.digest(c.canonical(value));vector.observation['source_sha256']=digest
        authorization=vector.observation['recovery_authorization']
        authorization.update(source_enrollment_sha256=digest,previous_checkpoint=auth.HEAD4,authority_epoch=7,review_generation=5,expires_at_ms=self.pins.valid_until_ms)
        vector.observation['recovery_authorization_sha256']=c.digest(c.canonical(authorization))
        with tempfile.TemporaryDirectory() as folder,patch('time.time',return_value=self.now/1000):
            target=Path(folder)/'r.py'
            result=source_writer.build(vector.observation,vector.deployment,target,now_ms=self.now,custody_revision=3,restart_profile=auth.PROFILE,review_generation=5)
            code=target.read_text()
            self.assertEqual(result['maximum_s3_attempts'],16)
            self.assertIn(auth.SOURCE_PREFIX,code);self.assertIn(auth.RECOVERY_PREFIX+'00000000000000000011/',code)
            self.assertIn('n01-owner-source-auth-attempt-v1-r-receipt.json',code)
            authorization['previous_checkpoint']=atomic.HEAD4
            vector.observation['recovery_authorization_sha256']=c.digest(c.canonical(authorization))
            with self.assertRaises(ValueError):source_writer.build(vector.observation,vector.deployment,target,now_ms=self.now,custody_revision=3,restart_profile=auth.PROFILE,review_generation=5)

if __name__=='__main__':unittest.main()
