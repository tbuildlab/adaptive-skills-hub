"""Synthetic forward-retirement contracts only; never live custody/Owner proof."""
from dataclasses import replace
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
from ash import g3_n01_owner_restart as restart
from ash import g3_n01_owner_state as state
from ash import g3_n01_owner_protocol as protocol
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_owner_context as owner
from ash import g3_delegated_control_codec as c
from ash import g3_checkpoint_custody as custody
from tests import test_g3_n01_owner_state as fixture
from scripts import build_g3_n01_owner_controller as builder


class OwnerRestartTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixture.OwnerStateTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.now=self.fixture.now+100
        body=dict(self.fixture.enrolled.value,process_nonce=restart.OLD_NONCE,
            artifact_inventory_sha256=restart.OLD_ARTIFACT,
            deployment_id=restart.OLD_ENV['VERCEL_DEPLOYMENT_ID'],deployment_host=restart.OLD_ENV['VERCEL_URL'])
        raw=c.canonical(body);self.old=source.EnrolledSource(raw,c.digest(raw))
        recovered=state.prepare_empty_recovery(self.fixture.history,process_nonce=restart.OLD_NONCE,now_ms=self.now)
        history=fixture.appended(self.fixture.history,recovered,{})
        enrolled,objects=state.prepare_owner_enrollment(history,self.old,now_ms=self.now+1)
        self.history=fixture.appended(history,enrolled,objects)
        self.patch('HEAD3',history.head);self.patch('HEAD4',self.history.head);self.patch('OLD_SOURCE_SHA',self.old.enrollment_sha256)
        new=dict(body,process_nonce='e'*64,artifact_inventory_sha256='f'*64)
        raw=c.canonical(new);self.new=source.EnrolledSource(raw,c.digest(raw))
        self.fixture.vector.install(recovered.checkpoint,recovered.snapshot,recovered.descriptor,3)
        self.fixture.vector.install(enrolled.checkpoint,enrolled.snapshot,enrolled.descriptor,4)
        for digest,raw in objects.items():self.fixture.vector.client.add(custody.NORMAL+'objects/'+digest,raw)
        self.fixture.vector.client.add(custody.APPROVALS+'current-source-controller-v3/registration.json',self.old.canonical_bytes)
        body=c.decode(recovered.checkpoint)
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode='DELEGATED_EXECUTOR',
            authority_config_sha256=source.CONFIG,source_enrollment_sha256=self.old.enrollment_sha256,
            checkpoint=history.head,previous_checkpoint=body['previous_checkpoint'],authority_epoch=3,
            incarnation=body['incarnation'],application_generation=1,review_generation=1,
            expires_at_ms=source.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        raw=c.canonical(authorization);self.patch('OLD_AUTH_SHA',c.digest(raw))
        self.auth_key=custody.APPROVALS+'owner-controller-recovery-v3/00000000000000000003/authorization.json'
        self.fixture.vector.client.add(self.auth_key,raw)
        original=replace(self.fixture.vector.scope,generation=2,
            admin_checkpoint_ids=tuple(custody.reference(raw)['id'] for raw in self.history.checkpoints if c.decode(raw)['transition_kind'] in ('GENESIS','RECOVER')))
        p=patch.object(restart.boot,'storage_scope',return_value=original);p.start();self.addCleanup(p.stop)
    def patch(self,name,value):
        p=patch.object(restart,name,value);p.start();self.addCleanup(p.stop)
    def recover(self):return restart.prepare_forward_recovery(self.history,process_nonce='e'*64,now_ms=self.now+2)
    def forward(self):return fixture.appended(self.history,self.recover(),{})
    def enrolled(self):
        history=self.forward()
        candidate,objects=state.prepare_owner_enrollment(history,self.new,now_ms=self.now+3,restart_profile=restart.PROFILE)
        return fixture.appended(history,candidate,objects)
    def test_forward_epoch_incarnation_preserves_history_and_retires_old_source_without_owner(self):
        result=self.forward();rows=[c.decode(row.value) for row in result.states[-1].checked.rows]
        root=next(row for row in rows if row['family']=='root')
        self.assertEqual((root['authority_epoch'],root['recovery_sequence'],root['incarnation']),(4,5,'n01-owner-'+'e'*32))
        self.assertEqual(result.checkpoints[:-1],self.history.checkpoints)
        self.assertTrue(set(self.history.objects)<=set(result.objects))
        self.assertEqual(next(row['state'] for row in rows if row['family']=='source'),'RETIRED')
        self.assertFalse(any(row['family'] in ('context','grant','intent','claim') for row in rows))
        self.assertEqual(result.authority,'NONE')
    def test_replay_wrong_head_and_old_nonce_never_prepare_new_recovery(self):
        for history,nonce in ((self.forward(),'e'*64),(self.fixture.ready(),'e'*64),(self.history,restart.OLD_NONCE),
            (self.history,restart.OLD_NONCE[:32]+'e'*32),(self.history,'malformed')):
            with self.assertRaises(ValueError):restart.prepare_forward_recovery(history,process_nonce=nonce,now_ms=self.now+4)
        with self.assertRaises(ValueError):restart.prepare_forward_recovery(self.history,process_nonce='e'*64,now_ms=0)
    def test_old_empty_recovery_and_original_enrollment_stay_closed_to_forward_lineage(self):
        with self.assertRaises(ValueError):state.prepare_empty_recovery(self.history,process_nonce='e'*64,now_ms=self.now+2)
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(self.forward(),self.new,now_ms=self.now+3)
    def test_new_binding_generation_preserves_old_rows_and_does_not_revive_them(self):
        result=self.enrolled();rows=[c.decode(row.value) for row in result.states[-1].checked.rows]
        self.assertEqual(state.current_binding_ids(rows),(restart.BINDING_ID,restart.REGISTRATION_ID))
        old=next(row for row in rows if row['family']=='binding' and row['binding_id']==state.BINDING_ID)
        self.assertEqual((old['state'],old['revision']),('RETIRED',2))
        new=next(row for row in rows if row['family']=='binding' and row['binding_id']==restart.BINDING_ID)
        self.assertEqual(new['binding_generation'],2)
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(result,self.new,now_ms=self.now+4,restart_profile=restart.PROFILE)
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(self.forward(),self.old,now_ms=self.now+3,restart_profile=restart.PROFILE)
    def test_new_owner_projection_binds_fresh_generation_and_rejects_old_source(self):
        projection=owner.OwnerProjection(owner.PROJECT,owner.OWNER,'session-test-12345678-1234-1234-1234-123456789012',self.now+4,self.now+900000,'a'*64)
        args=dict(deadline_ms=self.now+200000,nonce='b'*64,now_ms=self.now+5)
        candidate,objects,_,_=protocol.prepare_challenge(self.enrolled(),self.new,projection,**args)
        result=fixture.appended(self.enrolled(),candidate,objects)
        context=next(c.decode(row.value) for row in result.states[-1].checked.rows if c.decode(row.value)['family']=='context')
        self.assertEqual((context['binding_id'],context['binding_generation'],context['authority_epoch']), (restart.BINDING_ID,2,4))
        with self.assertRaises(ValueError):protocol.prepare_challenge(self.enrolled(),self.old,projection,**args)
    def test_profile_is_closed_and_artifact_reduces_remaining_quota(self):
        for invalid in (True,1,'OWNER_FORWARD_RESTART_V2',''):
            with self.assertRaises(ValueError):restart.require_profile(invalid)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);artifact=builder.build(root,delivery_email_sha256='a'*64,transport_revision=3,restart_profile=restart.PROFILE)
            self.assertEqual(artifact['maximum_ddb_attempts']+artifact['prior_native_ddb_attempts'],256)
            loader=(root/'source/api/n01-controller.py').read_text()
            self.assertIn('service.native.MAX_DDB=190',loader)
            self.assertIn("service.RESTART_PROFILE='OWNER_FORWARD_RESTART_V1'",loader)
            self.assertEqual(artifact['expected_predecessor'],restart.HEAD4)
            with self.assertRaises(ValueError):builder.build(root,delivery_email_sha256='a'*64,transport_revision=2,restart_profile=restart.PROFILE)
    def test_full_independent_historical_reader_preserves_exact_head_and_has_no_write_path(self):
        fence=restart.HistoricalOwnerFence(self.fixture.vector.client)
        history=fence.read(valid_until=self.fixture.vector.until)
        self.assertEqual(history.head,self.history.head);self.assertEqual(history.authority,'NONE')
        calls=len(self.fixture.vector.client.calls)
        with self.assertRaises(ValueError):fence.append(self.recover().checkpoint,history.head,valid_until=self.fixture.vector.until)
        self.assertEqual(calls,len(self.fixture.vector.client.calls))
        self.assertFalse(any(op=='put' for op,_ in self.fixture.vector.client.calls))
    def test_corrupt_missing_forked_historical_authorization_never_becomes_current_source(self):
        client=self.fixture.vector.client;original=client.rows[self.auth_key]
        for rows in ([],[('1',b'{}',True)],original+[('2',original[0][1],True)]):
            client.rows[self.auth_key]=rows
            with self.assertRaises(ValueError):restart.HistoricalOwnerFence(client).read(valid_until=self.fixture.vector.until)
        client.rows[self.auth_key]=original
        args=dict(native_environment=restart.OLD_ENV,artifact_inventory_sha256=restart.OLD_ARTIFACT,
            process_nonce=restart.OLD_NONCE,now_ms=self.now+3,custody_revision=3,restart_profile=restart.PROFILE)
        with self.assertRaises(ValueError):source.read_protected_source(client,restart.scope(),self.fixture.source_vector.review,**args)
    def test_forward_custody_has_exact_new_prefix_and_no_old_head_authorization_fallback(self):
        from scripts import build_g3_n01_owner_source_custody as custody_builder
        from tests import test_build_g3_n01_owner_source_custody as vectors
        vector=vectors.OwnerSourceBuilderTests();vector.setUp()
        observation=json.loads(json.dumps(vector.observation))
        authorization=observation['recovery_authorization']
        authorization.update(previous_checkpoint=restart.HEAD4,authority_epoch=4)
        observation['recovery_authorization_sha256']=c.digest(c.canonical(authorization))
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'r.py'
            result=custody_builder.build(observation,vector.deployment,path,now_ms=vector.vector.now,custody_revision=3,restart_profile=restart.PROFILE)
            self.assertIn(restart.SOURCE_PREFIX,path.read_text())
            self.assertIn(restart.RECOVERY_PREFIX+'00000000000000000005/',path.read_text())
            self.assertIn('n01-owner-source-restart-v1-r-receipt.json',path.read_text())
            self.assertEqual(result['new_objects'],2)
            with self.assertRaises(ValueError):custody_builder.build(vector.observation,vector.deployment,path,now_ms=vector.vector.now,custody_revision=3,restart_profile=restart.PROFILE)
    def test_new_current_fence_checks_both_historical_and_fresh_recovery_bindings(self):
        from ash import g3_n01_owner_persistence as persistence
        candidate=self.recover();body=c.decode(candidate.checkpoint);client=self.fixture.vector.client
        self.fixture.vector.install(candidate.checkpoint,candidate.snapshot,candidate.descriptor,5)
        client.add(restart.SOURCE_PREFIX+'registration.json',self.new.canonical_bytes)
        key=restart.RECOVERY_PREFIX+'00000000000000000005/authorization.json'
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode='DELEGATED_EXECUTOR',
            authority_config_sha256=source.CONFIG,source_enrollment_sha256=self.new.enrollment_sha256,
            checkpoint=custody.reference(candidate.checkpoint),previous_checkpoint=restart.HEAD4,
            authority_epoch=4,incarnation=body['incarnation'],application_generation=1,review_generation=1,
            expires_at_ms=source.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        client.add(key,c.canonical(authorization))
        scope=replace(restart.scope(),admin_checkpoint_ids=restart.scope().admin_checkpoint_ids+(custody.reference(candidate.checkpoint)['id'],))
        def fence():
            return persistence.OwnerMembershipFence(client,scope,public_review=self.fixture.source_vector.review,
                native_environment=restart.OLD_ENV,artifact_inventory_sha256='f'*64,process_nonce='e'*64,
                custody_revision=3,restart_profile=restart.PROFILE)
        result=fence().read(valid_until=self.fixture.vector.until)
        self.assertEqual(result.head,custody.reference(candidate.checkpoint));self.assertEqual(result.authority,'NONE')
        original=client.rows[key]
        client.rows[key]=[('1',c.canonical(dict(authorization,incarnation='n01-owner-'+restart.OLD_NONCE[:32])),True)]
        with self.assertRaises(ValueError):fence().read(valid_until=self.fixture.vector.until)
        client.rows[key]=original
        old=client.rows[self.auth_key];client.rows[self.auth_key]=[]
        with self.assertRaises(ValueError):fence().read(valid_until=self.fixture.vector.until)
        client.rows[self.auth_key]=old
    def test_forward_owner_consumption_and_revocation_keep_old_lineage_retired(self):
        from ash import g3_n02_presentation as page
        history=self.enrolled()
        projection=owner.OwnerProjection(owner.PROJECT,owner.OWNER,'session-test-12345678-1234-1234-1234-123456789012',self.now+4,self.now+900000,'a'*64)
        candidate,objects,challenge,view=protocol.prepare_challenge(history,self.new,projection,
            deadline_ms=self.now+200000,nonce='b'*64,now_ms=self.now+5)
        history=fixture.appended(history,candidate,objects)
        shown=page.render(challenge,view,csrf='c'*64,now_ms=self.now+6)
        decision=page.UntrustedDecision('DENY',shown.challenge_id,shown.view_id,shown.proposal_id,shown.nonce,shown.presentation_sha256)
        candidate,objects=protocol.prepare_decision(history,self.new,decision,projection,now_ms=self.now+7)
        history=fixture.appended(history,candidate,objects)
        with self.assertRaises(ValueError):protocol.prepare_decision(history,self.new,decision,projection,now_ms=self.now+8)
        candidate,objects=protocol.prepare_revoke_after_consumption(history,self.new,
            remote_result='EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY',now_ms=self.now+9)
        closed=fixture.appended(history,candidate,objects)
        rows=[c.decode(row.value) for row in closed.states[-1].checked.rows]
        self.assertTrue(all(row['state']=='RETIRED' for row in rows if row['family'] in ('binding','registration')))
        self.assertEqual(next(row['state'] for row in rows if row['family']=='context'),'CONSUMED')
        self.assertFalse(any(row['family'] in ('grant','intent','claim') for row in rows))


class HistoricalPinsTests(unittest.TestCase):
    def test_production_pin_is_exact_published_checkpoint_not_a_fixture(self):
        root=Path(__file__).resolve().parents[1]
        evidence=json.loads((root/'research/nexus-production-n01-native-owner-source-observed-evidence-v1.json').read_bytes())
        self.assertIn(restart.HEAD4['id'],json.dumps(evidence))
        self.assertIn(restart.HEAD4['body_sha256'],json.dumps(evidence))
        self.assertEqual(restart.OLD_ENV['VERCEL_DEPLOYMENT_ID'],'dpl_D9FFUQGNZKSxdetaR5byf8vEVydM')


if __name__=='__main__':unittest.main()
