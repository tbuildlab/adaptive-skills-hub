"""Synthetic protocol tests only. Mocked source reads do not qualify a writer."""
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pickle
import unittest
from unittest.mock import patch

from ash import g3_n01_owner_persistence as writer
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_delegated_control_codec as codec
from ash import g3_primary_ledger as primary
from ash import g3_control_semantics as semantics
from ash import g3_transition_protocol as transitions
from ash import g3_n01_membership_custody as membership
from scripts import g3_n01_storage_contract as storage
from tests import test_g3_n01_checkpoint_custody as custody_fixture
from tests import test_g3_primary_ledger as ledger_fixture

ROOT=Path(__file__).resolve().parents[1]


class OwnerPersistenceTests(unittest.TestCase):
    def setUp(self):
        proposal=codec.canonical(__import__('json').loads((ROOT/'research/nexus-production-n01-pending-public-pin-review-v1.json').read_bytes()))
        acceptance=codec.canonical(__import__('json').loads((ROOT/'research/nexus-production-n01-public-pin-owner-acceptance-v1.json').read_bytes()))
        self.review=review.verify_review(proposal,acceptance,now_ms=review.FROM_MS+1000)
        # Only the unit protocol deadline is relative to test execution. Exact
        # immutable live-review window/binding is tested in the source reader suite.
        self.deadline=patch.object(writer.review,'UNTIL_MS',int((datetime.now(timezone.utc)+timedelta(hours=2)).timestamp()*1000))
        self.deadline.start();self.addCleanup(self.deadline.stop)
        self.vector=custody_fixture.N01CustodyTests();self.vector.setUp()
        self.fence=writer.OwnerMembershipFence(self.vector.client,self.vector.scope,public_review=self.review,
            native_environment={},artifact_inventory_sha256='a'*64,process_nonce='b'*64)
        self.enrolled=source.EnrolledSource(codec.canonical(dict(principal=dict(
            issuer='stytch.com/'+source.PROJECT,client_id=source.PROJECT,subject=source.OWNER),
            source_kinds=['D01','D03','OWNER_ENROLLMENT'])),'d'*64)
        self.reader=patch.object(writer.source,'read_protected_source',return_value=self.enrolled)
        self.mock_reader=self.reader.start();self.addCleanup(self.reader.stop)
        self.client=ledger_fixture.MemoryClient()
        self.ledger=primary.DelegatedDynamoReservations(self.client,table_arn=ledger_fixture.ARN,
            instance=self.vector.scope.authority_instance,max_attempts=200)
        self.ledger.enroll_genesis(self.vector.head,self.vector.before.snapshot)
        self.driver=writer.OwnerMembershipCommit(self.ledger,self.fence,expected_head=self.vector.head,
                                               valid_until=self.vector.until)
    def test_complete_durability_is_none_with_finalized_exact_reservation(self):
        result=self.driver.commit(self.vector.next,objects={})
        self.assertEqual(result.authority,'NONE')
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'READY'})
        self.assertEqual(self.client.items['reservation#00000000000000000001']['phase'],{'S':'FINALIZED'})
        self.assertGreaterEqual(self.mock_reader.call_count,4)
        before=(len(self.client.calls),len(self.vector.client.calls))
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next,objects={})
        self.assertEqual(before,(len(self.client.calls),len(self.vector.client.calls)))
    def test_missing_current_source_denies_before_primary_mutation_and_retires(self):
        self.mock_reader.side_effect=ValueError('unavailable or stale source')
        before=len(self.client.calls)
        with self.assertRaisesRegex(ValueError,'^N01_OWNER_MEMBERSHIP_COMMIT_QUARANTINE$'):
            self.driver.commit(self.vector.next,objects={})
        self.assertEqual(before,len(self.client.calls));self.assertTrue(self.fence.retired)
    def test_unreferenced_or_corrupted_payload_never_enters_primary(self):
        before=len(self.client.calls)
        for objects in ({codec.digest(b'{}'):b'{}'},{'e'*64:b'{}'}):
            with self.assertRaises(ValueError):self.driver.commit(self.vector.next,objects=objects)
        self.assertEqual(before,len(self.client.calls))
    def test_effect_groups_and_forged_preparation_are_not_membership_operations(self):
        before=(len(self.client.calls),len(self.vector.client.calls))
        for candidate in (replace(self.vector.next,group='T7'),replace(self.vector.next,descriptor=b'{}')):
            with self.assertRaises(ValueError):self.driver.commit(candidate,objects={})
        self.assertEqual(before,(len(self.client.calls),len(self.vector.client.calls)))
    def test_stale_independent_head_denies_before_primary_write(self):
        self.vector.install(self.vector.next.checkpoint,self.vector.next.snapshot,self.vector.next.descriptor,1)
        before=len(self.client.calls)
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next,objects={})
        self.assertEqual(before,len(self.client.calls))
    def test_unknown_primary_prepare_quarantines_without_custody_or_redispatch(self):
        self.client.drop_ack=True
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next,objects={})
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'PREPARED'})
        self.assertEqual(len([op for op,_ in self.client.calls if op=='transact']),1)
        self.assertFalse(any(key.endswith('journal/00000000000000000001') for key in self.vector.client.rows))
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next,objects={})
        self.assertEqual(len([op for op,_ in self.client.calls if op=='transact']),1)
    def test_unknown_custody_never_finalizes_or_reconciles_for_authority(self):
        self.vector.client.mode='unknown-after'
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next,objects={})
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'PREPARED'})
        self.assertTrue(self.fence.retired)
        with self.assertRaises(ValueError):self.fence.reconcile(valid_until=self.vector.until)
    def test_direct_unplanned_or_scope_expanding_write_denies(self):
        before=len(self.vector.client.calls)
        arguments=dict(Key=writer.custody.NORMAL+'objects/'+'a'*64,Body=b'{}',IfNoneMatch='*',
            ContentType='application/json',ChecksumAlgorithm='SHA256')
        with self.assertRaises(ValueError):self.fence.call('put_object',**arguments)
        self.fence._begin_write({'a'*64:b'{}'},self.vector.next.checkpoint)
        for changes in ({'Key':source.PREFIX+'registration.json'},{'Body':b'{"x":1}'},
                        {'ObjectLockMode':'COMPLIANCE'},{'IfNoneMatch':'anything'}):
            with self.assertRaises(ValueError):self.fence.call('put_object',**dict(arguments,**changes))
        self.assertEqual(before,len(self.vector.client.calls))
        self.vector.client.mode='unknown-after'
        with self.assertRaises(ValueError):self.fence.call('put_object',**arguments)
        attempts=len(self.vector.client.calls)
        with self.assertRaises(ValueError):self.fence.call('put_object',**arguments)
        self.assertEqual(attempts,len(self.vector.client.calls))
    def test_restart_cannot_restore_fence_commit_or_old_process_source(self):
        for value in (self.fence,self.driver):
            with self.assertRaises(TypeError):pickle.dumps(value)
        self.mock_reader.side_effect=ValueError('new process mismatch')
        with self.assertRaises(ValueError):self.fence.read(valid_until=self.vector.until)
    def test_source_read_quota_consumed_before_failure_and_never_bypassed(self):
        self.fence.max_attempts=4;self.mock_reader.side_effect=ValueError('unknown')
        with self.assertRaises(ValueError):self.fence.current_source()
        self.assertEqual(self.fence.attempts,4)
        with self.assertRaises(ValueError):self.fence.current_source()
        self.assertEqual(self.mock_reader.call_count,1)
    def recovery_vector(self):
        current,registered=self.vector.recovery()
        history=membership.MembershipFence(self.vector.client,storage.scope(registered),profile='PRODUCTION').read(valid_until=self.vector.until)
        values=[codec.decode(row.value) for row in history.states[-1].checked.rows]
        root=next(value for value in values if value['family']=='root')
        root.update(revision=root['revision']+1,authority_epoch=root['authority_epoch']+1,
            incarnation='n01-owner-'+'b'*32,recovery_sequence=root['recovery_sequence']+1,
            previous_checkpoint=writer.custody.reference(current.checkpoint),
            time_high_water_ms=root['time_high_water_ms']+1,quarantine='OPEN')
        values.append(dict(schema_version=codec.VERSION,family='recovery',revision=1,
            sequence=2,checkpoint_ref=writer.custody.reference(current.checkpoint),
            control_sha256=history.states[-1].checked.snapshot.control_after_sha256,
            descriptor_sha256=codec.decode(current.checkpoint)['ledger_commit_sha256'],state='WITNESSED'))
        snapshot=codec.encode_snapshot(tuple(codec.ControlRow.from_value(value) for value in values))
        bodies={writer.custody.reference(raw)['id']:raw for raw in history.checkpoints}
        after=semantics.check_delegated_control(snapshot,bodies,{},profile='PRODUCTION',
            protected_config=self.vector.scope.config_sha256)
        candidate=transitions.prepare_delegated_transition(history.states[-1].checked,after,current.checkpoint,
            group='T9',transition='RECOVER',record_refs=[])
        scope=storage.scope(registered)
        scope=replace(scope,admin_checkpoint_ids=scope.admin_checkpoint_ids+(writer.custody.reference(candidate.checkpoint)['id'],))
        self.fence=writer.OwnerMembershipFence(self.vector.client,scope,public_review=self.review,
            native_environment={},artifact_inventory_sha256='a'*64,process_nonce='b'*64)
        self.enrolled=source.EnrolledSource(codec.canonical(dict(self.enrolled.value,process_nonce='b'*64)),'d'*64)
        self.mock_reader.return_value=self.enrolled
        self.ledger.retain_blob(current.checkpoint)
        self.client.items['HEAD'].update(checkpoint={'B':current.checkpoint},sequence={'N':'2'})
        self.driver=writer.OwnerMembershipCommit(self.ledger,self.fence,expected_head=current.checkpoint,valid_until=self.vector.until)
        body=codec.decode(candidate.checkpoint)
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode=writer.records.MODE,
            authority_config_sha256=scope.config_sha256,source_enrollment_sha256=self.enrolled.enrollment_sha256,
            checkpoint=writer.custody.reference(candidate.checkpoint),previous_checkpoint=body['previous_checkpoint'],
            authority_epoch=body['authority_epoch'],incarnation=body['incarnation'],application_generation=1,
            review_generation=1,expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        key=writer.RECOVERY_PREFIX+f"{body['recovery_sequence']:020d}/authorization.json"
        return candidate,authorization,key
    def test_exact_new_recovery_reuses_old_custody_without_promoting_old_authority(self):
        candidate,authorization,key=self.recovery_vector()
        self.vector.client.add(key,codec.canonical(authorization))
        result=self.driver.commit(candidate,objects={})
        self.assertEqual(result.authority,'NONE')
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'READY'})
        self.assertEqual(codec.decode(result.checkpoint)['authority_epoch'],3)
        self.assertEqual(self.fence.registration.purpose,'TEST_ONLY')
    def test_missing_independent_owner_recovery_denies_before_primary_mutation(self):
        candidate,_,_=self.recovery_vector();before=len(self.client.calls)
        with self.assertRaises(ValueError):self.driver.commit(candidate,objects={})
        self.assertEqual(before,len(self.client.calls))
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'READY'})
    def test_wrong_recovery_source_or_process_or_checkpoint_cannot_be_substituted(self):
        candidate,authorization,key=self.recovery_vector()
        self.vector.client.add(key,codec.canonical(dict(authorization,source_enrollment_sha256='e'*64)))
        before=len(self.client.calls)
        with self.assertRaises(ValueError):self.driver.commit(candidate,objects={})
        self.assertEqual(before,len(self.client.calls))


if __name__=='__main__':unittest.main()
