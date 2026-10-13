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

BUDGET_OBSERVATIONS={}


class PairClient(original.MemoryClient):
    def transact_get_items(self,**kwargs):
        self.calls.append(('atomic_get',kwargs))
        if getattr(self,'unknown_read',False):raise TimeoutError('SYNTHETIC_SECRET')
        rows=[{'Item':copy.deepcopy(self.items[row['Get']['Key']['sk']['S']])}
            if row['Get']['Key']['sk']['S'] in self.items else {} for row in kwargs['TransactItems']]
        return {'Responses':rows}


class AtomicReadTests(unittest.TestCase):
    def setUp(self):
        self.client=PairClient()
        self.ledger=primary.DelegatedDynamoReservations(self.client,table_arn=original.ARN,instance=custody.INSTANCE,max_attempts=210,atomic_reads=True)
    def test_exact_pair_replaces_rpc_fanout_but_retains_pre_put_post_checks(self):
        raws=(b'{"a":1}',b'{"b":2}')
        self.ledger.retain_blobs(raws)
        self.assertEqual([name for name,_ in self.client.calls],['atomic_get','put','put','atomic_get'])
        self.ledger._retained_many(raws)
        self.assertEqual(len(self.client.calls),5)
        for name,kw in self.client.calls:
            if name=='atomic_get':self.assertLessEqual(len(kw['TransactItems']),2)
        before=len(self.client.calls);self.ledger.retain_blobs(raws)
        self.assertEqual(len(self.client.calls)-before,1)
    def test_partial_reordered_corrupt_and_unknown_atomic_reads_fail_closed_without_retry(self):
        raws=(b'{"a":1}',b'{"b":2}');self.ledger.retain_blobs(raws)
        valid=self.client.transact_get_items(TransactItems=[{'Get':{'Key':self.ledger._key('blob#'+c.digest(raw))}} for raw in raws])
        for result in ({'Responses':[]},{'Responses':valid['Responses'][::-1]},
                {'Responses':[{},{}]},{'Responses':[dict(Item=dict(valid['Responses'][0]['Item'],body={'B':b'{}'})),valid['Responses'][1]]}):
            with patch.object(self.client,'transact_get_items',return_value=result),self.assertRaises(primary.LedgerError):self.ledger._retained_many(raws)
            self.assertTrue(self.ledger.quarantined)
        self.client.unknown_read=True;before=len(self.client.calls)
        with self.assertRaises(primary.LedgerError):self.ledger._retained_many(raws)
        self.assertEqual(len(self.client.calls)-before,1)
    def test_unknown_put_is_not_retried_or_promoted_by_a_prior_read(self):
        self.client.drop_blob_ack=True
        with self.assertRaises(primary.LedgerError):self.ledger.retain_blobs((b'{"a":1}',b'{"b":2}'))
        self.assertEqual([name for name,_ in self.client.calls],['atomic_get','put'])
        self.assertTrue(self.ledger.quarantined)


class AtomicNativeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.vector=native_fixture.NativeTransportTests();self.vector.setUp();self.addCleanup(self.vector.doCleanups)
    def request(self,keys=('HEAD','blob#'+'a'*64)):
        native=service.native
        return dict(TransactItems=[{'Get':{'TableName':native.TABLE,'Key':{'pk':{'S':'authority#'+custody.INSTANCE},'sk':{'S':key}}}} for key in keys])
    def test_two_item_read_is_accounted_once_and_does_not_require_write_enrollment(self):
        driver=self.vector.begin();driver.primary.transact_get_items(**self.request())
        self.assertEqual(driver.ddb_attempts,1)
        self.assertEqual(service.native._BUDGET['ddb_bytes'],0)
        self.assertEqual(self.vector.trace[-1][1],'transact_get_items')
        self.assertEqual(len(self.vector.trace[-1][2]['TransactItems']),2)
    def test_foreign_scope_duplicate_extra_projection_and_third_item_deny_before_sdk(self):
        requests=[self.request(('HEAD','HEAD')),self.request(('HEAD','x','y'))]
        foreign=self.request();foreign['TransactItems'][0]['Get']['Key']['pk']={'S':'other'};requests.append(foreign)
        extra=self.request();extra['TransactItems'][0]['Get']['ProjectionExpression']='pk';requests.append(extra)
        for request in requests:
            driver=self.vector.begin();before=len(self.vector.trace)
            with self.assertRaises(ValueError):driver.primary.transact_get_items(**request)
            self.assertEqual(len(self.vector.trace),before);self.assertTrue(driver.retired)
    def test_atomic_unknown_and_exhausted_shared_budget_never_retry(self):
        driver=self.vector.begin();driver._NativeTransport__ddb.unknown=True
        with self.assertRaises(ValueError):driver.primary.transact_get_items(**self.request())
        count=len(self.vector.trace)
        with self.assertRaises(ValueError):driver.primary.transact_get_items(**self.request())
        self.assertEqual(len(self.vector.trace),count);self.assertEqual(driver.ddb_attempts,1)
        driver=self.vector.begin();service.native._BUDGET['ddb']=service.native.MAX_DDB;count=len(self.vector.trace)
        with self.assertRaises(ValueError):driver.primary.transact_get_items(**self.request())
        self.assertEqual(len(self.vector.trace),count)


class AtomicContinuationTests(unittest.TestCase):
    def setUp(self):
        self.old=sdk.SDKRepairRetirementTests();self.old.setUp();self.addCleanup(self.old.doCleanups)
        self.pins=review.pins(2);self.now=self.pins.valid_from_ms+1000
        self.public=review.verify_review(*public_fixture.materials(),now_ms=self.now,review_generation=2)
        recovery=prior.prepare_forward_recovery(self.old.history,process_nonce='d'*64,now_ms=self.now)
        head7=fixture.appended(self.old.history,recovery,{})
        value=dict(self.old.vector.new.value,process_nonce='d'*64,artifact_inventory_sha256='a'*64,
            review_generation=2,review_package_sha256=self.pins.package_sha256,review_acceptance_sha256=self.pins.acceptance_sha256,
            issued_at_ms=self.now,expires_at_ms=self.pins.valid_until_ms)
        raw=c.canonical(value);self.current=source.EnrolledSource(raw,c.digest(raw))
        candidate,objects=state.prepare_owner_enrollment(head7,self.current,now_ms=self.now+1,restart_profile=prior.PROFILE)
        self.history=fixture.appended(head7,candidate,objects)
        vector=self.old.vector.fixture.vector
        vector.install(recovery.checkpoint,recovery.snapshot,recovery.descriptor,7)
        vector.install(candidate.checkpoint,candidate.snapshot,candidate.descriptor,8)
        for digest,body in objects.items():vector.client.add(custody.NORMAL+'objects/'+digest,body)
        auth=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode='DELEGATED_EXECUTOR',
            authority_config_sha256=source.CONFIG,source_enrollment_sha256=self.current.enrollment_sha256,checkpoint=head7.head,previous_checkpoint=self.old.history.head,
            authority_epoch=5,incarnation='n01-owner-'+'d'*32,application_generation=1,review_generation=2,expires_at_ms=self.pins.valid_until_ms,no_automatic_redispatch='REQUIRED',real_admission='NO')
        auth_raw=c.canonical(auth)
        vector.client.add(prior.SOURCE_PREFIX+'registration.json',raw)
        vector.client.add(prior.RECOVERY_PREFIX+'00000000000000000007/authorization.json',auth_raw)
        for name,val in dict(HEAD4=self.history.head,HEAD3=head7.head,OLD_NONCE='d'*64,OLD_SOURCE_SHA=self.current.enrollment_sha256,
                OLD_AUTH_SHA=c.digest(auth_raw),OLD_ARTIFACT='a'*64,OLD_ENV=dict(VERCEL_DEPLOYMENT_ID=value['deployment_id'],VERCEL_URL=value['deployment_host'])).items():
            p=patch.object(atomic,name,val);p.start();self.addCleanup(p.stop)
    def run_model(self,paired,choice='DENY'):
        client=PairClient();head=self.history.checkpoints[-1]
        ledger=primary.DelegatedDynamoReservations(client,table_arn=original.ARN,instance=custody.INSTANCE,max_attempts=512)
        client.items['HEAD']=dict(ledger._key('HEAD'),phase={'S':'READY'},checkpoint={'B':head},sequence={'N':'8'})
        client.items['blob#'+c.digest(head)]=dict(ledger._key('blob#'+c.digest(head)),body={'B':head})
        native=Mock(primary=client,custody=self.old.vector.fixture.vector.client,ddb_attempts=0,s3_attempts=0)
        prior_rows=copy.deepcopy(native.custody.rows);native.custody.calls.clear()
        now=self.now+100
        material=[]
        original_commit=service.OwnerController._commit
        def observed_commit(controller,candidate,objects):
            material.append(dict(transition=c.decode(candidate.checkpoint)['transition_kind'],pages=len(candidate.snapshot.pages),
                objects=len(objects),maximum_page_bytes=max(map(len,candidate.snapshot.pages))))
            return original_commit(controller,candidate,objects)
        with patch.object(service,'RESTART_PROFILE',atomic.PROFILE),patch.object(service,'PRIMARY_READ_PROFILE','PAIRED_ATOMIC_V1' if paired else 'SCALAR_V1'),\
            patch.object(service,'CUSTODY_REVISION',3),patch.object(service,'REVIEW_GENERATION',2),patch.object(boot,'PROCESS_NONCE','9'*64),\
            patch.object(service,'UNTIL',datetime.fromtimestamp(self.pins.valid_until_ms/1000,timezone.utc)),patch('time.time',return_value=now/1000),\
            patch.object(service.native,'NativeTransport',return_value=native),patch.object(review,'read_protected_review',return_value=self.public),\
            patch.dict(service.os.environ,{'STYTCH_PROJECT_ID':source.PROJECT,'STYTCH_SECRET':'SYNTHETIC_NON_AUTHORITY'}),\
            patch.object(service,'DELIVERY_EMAIL_SHA','a'*64),patch.object(service.OwnerController,'_OwnerController__maintenance_gate'),\
            patch.object(service.OwnerController,'_commit',observed_commit),redirect_stdout(StringIO()):
            controller=service.OwnerController('SYNTHETIC_ONLY',self.old.vector.fixture.source_vector.env,'a'*64)
            phases=[('INITIAL_SOURCE_PROPOSAL',len(client.calls))]
            proposal=controller.proposal();raw=c.canonical(proposal['source_proposal']);enrolled=source.EnrolledSource(raw,c.digest(raw))
            native.enable_owner_storage.return_value=enrolled
            native.custody.add(atomic.SOURCE_PREFIX+'registration.json',raw)
            native.custody.add(atomic.RECOVERY_PREFIX+'00000000000000000009/authorization.json',c.canonical(proposal['recovery_authorization']))
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
    def test_head_eight_forward_model_keeps_all_checks_and_fits_remaining_budget(self):
        scalar=self.run_model(False);paired=self.run_model(True)
        self.assertEqual(scalar['items'],paired['items'])
        self.assertEqual(paired['items']['HEAD']['sequence'],{'N':'13'})
        self.assertLessEqual(paired['attempts'],210)
        self.assertLessEqual(98+134+70+paired['attempts'],512)
        self.assertLessEqual(paired['s3_attempts'],16000)
        self.assertEqual(scalar['operation_counts']['put'],paired['operation_counts']['put'])
        self.assertEqual(scalar['operation_counts']['transact'],paired['operation_counts']['transact'])
        self.assertTrue(all(row['maximum_page_bytes']<32768 for row in paired['material']))
        self.budget_observation={name:{key:val for key,val in value.items() if key!='items'} for name,value in (('scalar',scalar),('paired',paired))}
        BUDGET_OBSERVATIONS['DENY']=self.budget_observation
    def test_confirm_and_deny_consumption_both_fit_without_grant_or_dispatch(self):
        value=self.run_model(True,'CONFIRM');self.assertLessEqual(value['attempts'],210)
        self.assertFalse(any('grant' in key or 'intent' in key or 'claim' in key for key in value['items']))
        BUDGET_OBSERVATIONS['CONFIRM']={key:val for key,val in value.items() if key!='items'}
    def test_new_artifact_is_head_eight_only_and_does_not_reset_aggregate(self):
        with tempfile.TemporaryDirectory() as folder:
            result=builder.build(Path(folder),delivery_email_sha256='a'*64,transport_revision=3,restart_profile=atomic.PROFILE,review_generation=2)
        self.assertEqual(result['expected_predecessor'],atomic.HEAD4)
        self.assertEqual(result['maximum_ddb_attempts'],210)
        self.assertEqual(result['prior_native_ddb_attempts']+98+210,512)
        self.assertEqual(result['primary_read_profile'],'PAIRED_ATOMIC_V1')
    def test_stale_head_old_incarnation_and_corrupted_recovery_seven_deny(self):
        for history,nonce in ((self.old.history,'9'*64),(self.history,'d'*64)):
            with self.assertRaises(ValueError):atomic.prepare_forward_recovery(history,process_nonce=nonce,now_ms=self.now+2)
        self.old.vector.fixture.vector.client.rows.pop(prior.RECOVERY_PREFIX+'00000000000000000007/authorization.json')
        with patch('time.time',return_value=self.now/1000),self.assertRaises(ValueError):
            atomic.HistoricalOwnerFence(self.old.vector.fixture.vector.client).read(valid_until=datetime.fromtimestamp(self.pins.valid_until_ms/1000,timezone.utc))


if __name__=='__main__':unittest.main()
