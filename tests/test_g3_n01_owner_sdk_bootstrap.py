"""Real installed SDK bootstrap seam, synthetic configuration only, no network."""
from io import StringIO
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from stytch import Client
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_stytch_transport as transport
from scripts import g3_n01_owner_controller as service
from tests import test_g3_n01_owner_controller as fixture
from tests import test_g3_n01_owner_restart as restart_fixture
from tests import test_g3_n01_owner_state as state_fixture
from ash import g3_n01_owner_sdk_restart as repair
from ash import g3_n01_owner_state as state
from ash import g3_delegated_control_codec as c
from ash import g3_checkpoint_custody as custody
from ash import g3_n01_owner_restart as prior
from ash import g3_n01_controller_bootstrap as boot
from ash import g3_n01_public_review as review
from ash import g3_n01_owner_protocol as protocol
from ash import g3_n01_owner_context as owner
from ash import g3_n02_presentation as presentation
from ash.g3_primary_ledger import DelegatedDynamoReservations
from tests import test_g3_primary_ledger as ledger_fixture
from unittest.mock import Mock
from datetime import datetime,timezone
from scripts import build_g3_n01_owner_controller as builder
import tempfile
from pathlib import Path
import sys


def historical_clock(case):
    """Offline fixture date only; immutable real review is never extended."""
    from datetime import datetime as native_datetime
    stamp=(review.FROM_MS+1000)/1000
    class FixtureDateTime(native_datetime):
        @classmethod
        def now(cls,tz=None):return cls.fromtimestamp(stamp,tz)
    for name,module in list(sys.modules.items()):
        if 'g3_' in name and getattr(module,'datetime',None) is native_datetime:
            p=patch.object(module,'datetime',FixtureDateTime);p.start();case.addCleanup(p.stop)
    p=patch.object(service,'UNTIL',FixtureDateTime.fromtimestamp(review.UNTIL_MS/1000,timezone.utc));p.start();case.addCleanup(p.stop)


class OwnerSDKBootstrapTests(unittest.TestCase):
    def setUp(self):historical_clock(self)
    def test_real_sdk_read_only_property_and_supported_constructor(self):
        bounded=transport.BoundedStytchSession();self.addCleanup(bounded.close)
        client=Client(source.PROJECT,'SYNTHETIC_NON_AUTHORITY',environment='test',sync_session=bounded)
        self.assertIs(client.sync_client._session,bounded)
        self.assertIsNone(type(client.sync_client)._session.fset)
        self.assertEqual(bounded.attempts,0)

    def test_controller_login_uses_actual_sdk_constructor_then_ingress(self):
        vector=fixture.OwnerControllerTests();vector.setUp();self.addCleanup(vector.doCleanups)
        controller,_,_,headers,enrolled=vector.prepared_controller()
        with patch.object(service.OwnerController,'_OwnerController__maintenance_gate'),patch.object(service.persistence.source,'read_protected_source',return_value=enrolled),redirect_stdout(StringIO()):
            controller.maintain('recover',headers,'SYNTHETIC_ONLY')
            controller.maintain('enroll',headers,'SYNTHETIC_ONLY')
            with patch.dict(service.os.environ,{'STYTCH_PROJECT_ID':source.PROJECT,'STYTCH_SECRET':'SYNTHETIC_NON_AUTHORITY'}),patch.object(service,'DELIVERY_EMAIL_SHA','a'*64):
                self.assertEqual(controller.maintain('login',headers,'SYNTHETIC_ONLY'),'OWNER_LOGIN_READY_NONE')
        self.assertTrue(controller.initial_login)
        self.assertEqual(controller.phase,'OWNER_LOGIN_READY_NONE')
        controller._quarantine()
        self.assertEqual(controller.phase,'QUARANTINE')
        self.assertFalse(controller.initial_login)


class SDKRepairRetirementTests(unittest.TestCase):
    def setUp(self):
        historical_clock(self)
        self.vector=restart_fixture.OwnerRestartTests();self.vector.setUp();self.addCleanup(self.vector.doCleanups)
        self.history=self.vector.enrolled()
        candidate=self.vector.recover();next_history=self.vector.forward()
        enrolled,objects=state.prepare_owner_enrollment(next_history,self.vector.new,now_ms=self.vector.now+3,restart_profile=prior.PROFILE)
        self.vector.fixture.vector.install(candidate.checkpoint,candidate.snapshot,candidate.descriptor,5)
        self.vector.fixture.vector.install(enrolled.checkpoint,enrolled.snapshot,enrolled.descriptor,6)
        for digest,raw in objects.items():self.vector.fixture.vector.client.add(custody.NORMAL+'objects/'+digest,raw)
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',
            authority_mode='DELEGATED_EXECUTOR',authority_config_sha256=source.CONFIG,source_enrollment_sha256=self.vector.new.enrollment_sha256,
            checkpoint=next_history.head,previous_checkpoint=self.vector.history.head,authority_epoch=4,incarnation='n01-owner-'+'e'*32,
            application_generation=1,review_generation=1,expires_at_ms=source.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        raw=c.canonical(authorization)
        self.vector.fixture.vector.client.add(prior.SOURCE_PREFIX+'registration.json',self.vector.new.canonical_bytes)
        self.vector.fixture.vector.client.add(prior.RECOVERY_PREFIX+'00000000000000000005/authorization.json',raw)
        for name,value in (('HEAD3',next_history.head),('HEAD4',self.history.head),('OLD_NONCE','e'*64),('OLD_SOURCE_SHA',self.vector.new.enrollment_sha256),('OLD_ARTIFACT','f'*64),
            ('OLD_AUTH_SHA',c.digest(raw)),('OLD_ENV',dict(VERCEL_DEPLOYMENT_ID=self.vector.new.value['deployment_id'],VERCEL_URL=self.vector.new.value['deployment_host']))):
            p=patch.object(repair,name,value);p.start();self.addCleanup(p.stop)
    def forward(self):
        candidate=repair.prepare_forward_recovery(self.history,process_nonce='d'*64,now_ms=self.vector.now+4)
        return state_fixture.appended(self.history,candidate,{})
    def test_repair_retains_all_old_bytes_and_retires_source(self):
        result=self.forward()
        self.assertEqual(result.checkpoints[:-1],self.history.checkpoints)
        self.assertTrue(set(self.history.objects)<=set(result.objects))
        rows=[c.decode(row.value) for row in result.states[-1].checked.rows]
        root=next(row for row in rows if row['family']=='root')
        self.assertEqual((root['authority_epoch'],root['recovery_sequence']),(5,7))
        self.assertTrue(all(row['state']=='RETIRED' for row in rows if row['family']=='source'))
        self.assertFalse(any(row['family'] in ('context','challenge','decision','grant','intent','claim') for row in rows))
    def test_old_head_replay_incarnation_collision_and_wrong_profile_deny(self):
        for history,nonce in ((self.vector.history,'d'*64),(self.forward(),'d'*64),(self.history,'e'*64),(self.history,'e'*32+'d'*32)):
            with self.assertRaises(ValueError):repair.prepare_forward_recovery(history,process_nonce=nonce,now_ms=self.vector.now+5)
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(self.forward(),self.vector.new,now_ms=self.vector.now+5,restart_profile='OWNER_FORWARD_RESTART_V1')
    def test_new_generation_three_requires_both_old_bindings_retired(self):
        raw=c.canonical(dict(self.vector.new.value,process_nonce='d'*64,artifact_inventory_sha256='a'*64))
        enrolled=source.EnrolledSource(raw,c.digest(raw))
        candidate,objects=state.prepare_owner_enrollment(self.forward(),enrolled,now_ms=self.vector.now+5,restart_profile=repair.PROFILE)
        after=state_fixture.appended(self.forward(),candidate,objects)
        rows=[c.decode(row.value) for row in after.states[-1].checked.rows]
        self.assertEqual(state.current_binding_ids(rows),(repair.BINDING_ID,repair.REGISTRATION_ID))
        current=next(row for row in rows if row['family']=='binding' and row['state']=='CURRENT')
        self.assertEqual(current['binding_generation'],3)
        next(row for row in rows if row['family']=='binding' and row['state']=='RETIRED')['state']='CURRENT'
        with self.assertRaises(ValueError):state.current_binding_ids(rows)
    def test_artifact_binds_exact_head_six_and_keeps_aggregate_cost_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact=builder.build(Path(tmp),delivery_email_sha256='a'*64,transport_revision=3,restart_profile=repair.PROFILE)
        self.assertEqual(artifact['expected_predecessor'],repair.HEAD4)
        self.assertEqual(artifact['maximum_ddb_attempts'],280)
        self.assertEqual(artifact['maximum_s3_attempts'],10000)
        self.assertLessEqual(98+134+artifact['maximum_ddb_attempts'],512)
        self.assertEqual(artifact['real_admission'],'NO')
    def test_complete_history_requires_fresh_independent_recover_three_and_five(self):
        reader=repair.HistoricalOwnerFence(self.vector.fixture.vector.client)
        history=reader.read(valid_until=datetime.fromtimestamp(source.UNTIL_MS/1000,timezone.utc))
        self.assertEqual(history.head,self.history.head)
        self.assertEqual(history.checkpoints,self.history.checkpoints)
        calls=self.vector.fixture.vector.client.calls
        self.assertTrue(any(call[1].get('Key','').startswith(prior.RECOVERY_PREFIX) for call in calls))
        self.assertFalse(any(call[0]=='put_object' for call in calls))
    def test_corrupted_or_missing_historical_recover_five_never_recovers(self):
        key=prior.RECOVERY_PREFIX+'00000000000000000005/authorization.json'
        self.vector.fixture.vector.client.rows.pop(key)
        with self.assertRaises(ValueError):repair.HistoricalOwnerFence(self.vector.fixture.vector.client).read(valid_until=datetime.fromtimestamp(source.UNTIL_MS/1000,timezone.utc))
    def test_full_long_history_identity_gates_and_three_commits_fit_existing_aggregate(self):
        public=self.vector.fixture.source_vector.review
        env=self.vector.fixture.source_vector.env
        primary=ledger_fixture.MemoryClient()
        ledger=DelegatedDynamoReservations(primary,table_arn=ledger_fixture.ARN,instance=custody.INSTANCE,max_attempts=256)
        head=self.history.checkpoints[-1]
        primary.items['HEAD']=dict(ledger._key('HEAD'),phase={'S':'READY'},checkpoint={'B':head},sequence={'N':'6'})
        primary.items['blob#'+c.digest(head)]=dict(ledger._key('blob#'+c.digest(head)),body={'B':head})
        self.vector.fixture.vector.client.calls.clear()
        native=Mock(primary=primary,custody=self.vector.fixture.vector.client,ddb_attempts=0,s3_attempts=0)
        with patch.object(service,'RESTART_PROFILE',repair.PROFILE),patch.object(service,'CUSTODY_REVISION',3),patch.object(boot,'PROCESS_NONCE','d'*64),\
            patch('time.time',return_value=(self.vector.now+100)/1000),\
            patch.object(service.native,'NativeTransport',return_value=native),patch.object(review,'read_protected_review',return_value=public),\
            patch.dict(service.os.environ,{'STYTCH_PROJECT_ID':source.PROJECT,'STYTCH_SECRET':'SYNTHETIC_NON_AUTHORITY'}),\
            patch.object(service,'DELIVERY_EMAIL_SHA','a'*64),patch.object(service.OwnerController,'_OwnerController__maintenance_gate'),redirect_stdout(StringIO()):
            controller=service.OwnerController('SYNTHETIC_ONLY',env,'a'*64)
            value=controller.proposal();raw=c.canonical(value['source_proposal']);enrolled=source.EnrolledSource(raw,c.digest(raw))
            native.enable_owner_storage.return_value=enrolled
            native.custody.add(repair.SOURCE_PREFIX+'registration.json',raw)
            native.custody.add(repair.RECOVERY_PREFIX+'00000000000000000007/authorization.json',c.canonical(value['recovery_authorization']))
            controller.maintain('recover',None,'SYNTHETIC_ONLY');controller.maintain('enroll',None,'SYNTHETIC_ONLY')
            controller.maintain('login',None,'SYNTHETIC_ONLY')
            relying=controller._OwnerController__owner
            original=relying._OwnerIngress__fence
            reader=original.gate_reader()
            self.assertIs(reader.client,original.client)
            self.assertEqual(reader.max_attempts,1000)
            self.assertIsNot(reader,original)
            reader.pending=b'SYNTHETIC_UNKNOWN_APPEND'
            with self.assertRaises(ValueError):reader.gate_reader()
            retired=original.gate_reader();retired.retired=True
            with self.assertRaises(ValueError):retired.gate_reader()
            # Fresh full reads model the three identity steps without auth calls.
            for _ in range(3):relying._OwnerIngress__gate()
            now=self.vector.now+100
            projection=owner.OwnerProjection(owner.PROJECT,owner.OWNER,'session-test-12345678-1234-1234-1234-123456789012',now-50,now+900000,'a'*64)
            controller._storage()
            candidate,objects,challenge,view=protocol.prepare_challenge(controller._OwnerController__history,enrolled,projection,deadline_ms=now+200000,nonce='b'*64,now_ms=now)
            controller._commit(candidate,objects)
            for _ in range(2):relying._OwnerIngress__gate()
            shown=presentation.render(challenge,view,csrf='c'*64,now_ms=now)
            decision=presentation.UntrustedDecision('DENY',shown.challenge_id,shown.view_id,shown.proposal_id,shown.nonce,shown.presentation_sha256)
            controller._storage()
            candidate,objects=protocol.prepare_decision(controller._OwnerController__history,enrolled,decision,projection,now_ms=now)
            controller._commit(candidate,objects)
            controller._storage()
            candidate,objects=protocol.prepare_revoke_after_consumption(controller._OwnerController__history,enrolled,remote_result='EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY',now_ms=now)
            controller._commit(candidate,objects)
            controller._storage()  # One final fresh current-head verification.
            controller._quarantine()
        self.assertEqual(primary.items['HEAD']['sequence'],{'N':'11'})
        self.assertLessEqual(len(primary.calls),280)
        self.assertLessEqual(98+134+len(primary.calls),512)
        self.budget_observation=dict(ddb=len(primary.calls),s3=len(native.custody.calls))
        self.assertLessEqual(len(native.custody.calls),10000)


if __name__=='__main__':unittest.main()
