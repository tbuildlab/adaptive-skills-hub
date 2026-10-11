"""Synthetic transport-order tests; no new or repeated AWS qualification."""
from dataclasses import replace
import pickle
import unittest

from ash import g3_n01_commit as commit
from ash import g3_delegated_control_codec as control
from ash import g3_primary_ledger as primary
from tests import test_g3_n01_checkpoint_custody as custody_fixture
from tests import test_g3_primary_ledger as ledger_fixture


class CommitTests(unittest.TestCase):
    def setUp(self):
        self.vector=custody_fixture.N01CustodyTests();self.vector.setUp()
        self.client=ledger_fixture.MemoryClient()
        self.ledger=primary.DelegatedDynamoReservations(self.client,table_arn=ledger_fixture.ARN,
            instance=self.vector.scope.authority_instance,max_attempts=150)
        self.ledger.enroll_genesis(self.vector.head,self.vector.before.snapshot)
        self.driver=commit.SingleCommit(self.ledger,self.vector.fence,
            expected_head=self.vector.head,valid_until=self.vector.until)
    def test_full_order_returns_none_and_permanently_retires_coordinator(self):
        result=self.driver.commit(self.vector.next)
        self.assertEqual(result.authority,'NONE');self.assertTrue(self.driver.retired)
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'READY'})
        self.assertEqual(self.client.items['reservation#00000000000000000001']['phase'],{'S':'FINALIZED'})
        before=(len(self.client.calls),len(self.vector.client.calls))
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next)
        self.assertEqual(before,(len(self.client.calls),len(self.vector.client.calls)))
    def test_stale_expected_head_denies_without_primary_mutation(self):
        self.vector.install(self.vector.next.checkpoint,self.vector.next.snapshot,self.vector.next.descriptor,1)
        before=len(self.client.calls)
        with self.assertRaisesRegex(ValueError,'N01_COMMIT_QUARANTINE'):self.driver.commit(self.vector.next)
        self.assertEqual(before,len(self.client.calls))
    def test_unknown_prepared_is_not_retried_or_finalized(self):
        self.client.drop_ack=True
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next)
        self.assertTrue(self.driver.retired);self.assertTrue(self.ledger.quarantined)
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'PREPARED'})
        self.assertEqual(len([op for op,_ in self.client.calls if op=='transact']),1)
        self.assertFalse(any(key.startswith('qualification/n01/v1/normal/journal/00000000000000000001')
                             for key in self.vector.client.rows))
    def test_unknown_custody_append_leaves_prepared_consumed_without_finalize(self):
        self.vector.client.mode='unknown-after'
        with self.assertRaises(ValueError):self.driver.commit(self.vector.next)
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'PREPARED'})
        self.assertTrue(self.driver.retired)
    def test_corrupted_forged_preparation_denies_before_primary_io(self):
        before=len(self.client.calls)
        for candidate in (replace(self.vector.next,snapshot=self.vector.before.snapshot),
                          replace(self.vector.next,group='T7'),replace(self.vector.next,descriptor=b'{}')):
            driver=commit.SingleCommit(self.ledger,self.vector.fence,
                expected_head=self.vector.head,valid_until=self.vector.until)
            with self.assertRaises(ValueError):driver.commit(candidate)
        self.assertEqual(before,len(self.client.calls))
    def test_clock_regression_denies_before_primary_io(self):
        rows=[control.decode(row.value) for row in control.verify_snapshot(self.vector.next.snapshot)]
        next(value for value in rows if value['family']=='root')['time_high_water_ms']=0
        forged=replace(self.vector.next,snapshot=control.encode_snapshot(tuple(
            control.ControlRow.from_value(value) for value in rows)))
        before=len(self.client.calls)
        with self.assertRaises(ValueError):self.driver.commit(forged)
        self.assertEqual(before,len(self.client.calls))
    def test_context_source_or_grant_cannot_enter_test_only_transport(self):
        rows=[control.decode(row.value) for row in control.verify_snapshot(self.vector.next.snapshot)]
        from tests.test_g3_offline_control import sample
        source=sample('source');source['schema_version']=control.VERSION
        rows.append(source)
        forged=replace(self.vector.next,snapshot=control.encode_snapshot(tuple(
            control.ControlRow.from_value(value) for value in rows)))
        before=(len(self.client.calls),len(self.vector.client.calls))
        with self.assertRaises(ValueError):self.driver.commit(forged)
        self.assertEqual(before,(len(self.client.calls),len(self.vector.client.calls)))
    def test_pickle_restart_cannot_restore_coordinator(self):
        with self.assertRaisesRegex(TypeError,'N01_COMMIT_NOT_RESTORABLE'):pickle.dumps(self.driver)
        self.assertEqual(self.driver.authority,'NONE')


if __name__=='__main__':unittest.main()
