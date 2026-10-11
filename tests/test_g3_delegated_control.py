"""Delegated storage/semantic/transport fixtures are never live evidence."""
import copy
from dataclasses import replace
import unittest
from ash import g3_control_codec as old, g3_delegated_control_codec as c
from ash import g3_delegated_record_codec as r, g3_control_semantics as s
from ash import g3_transition_protocol as p, g3_primary_ledger as m
from tests.g3_delegated_state_fixtures import state,checked,vector,CONFIG
from tests.test_g3_primary_ledger import MemoryClient,ARN


class DelegatedControlTests(unittest.TestCase):
    def test_complete_terminal_and_unknown_lineages_remain_none(self):
        for claimed in (False,True):
            values,bodies,evidence,assertions=state(claimed)
            with self.subTest(claimed=claimed):self.assertEqual(checked(values,bodies,evidence,assertions).authority,'NONE')
            self.assertFalse(any(v['family']=='source' and v['kind']=='D04' for v in values))
    def test_snapshot_preserves_exact_v2_rows_in_v1_page_format(self):
        values,bodies,evidence,assertions=state()
        result=checked(values,bodies,evidence,assertions)
        self.assertEqual(c.decode(result.snapshot.root)['codec_version'],'nexus.g3.control-snapshot.v1')
        self.assertEqual(c.encode_snapshot(c.verify_snapshot(result.snapshot)),result.snapshot)
        with self.assertRaises(old.OfflineError):old.verify_snapshot(result.snapshot)
    def test_v1_rows_and_mixed_record_references_are_rejected(self):
        values,*_=state();root=values[0];root['schema_version']=old.VERSION
        with self.assertRaises(old.OfflineError):c.ControlRow.from_value(root)
        values,*_=state();row=next(v for v in values if v['family']=='challenge')
        row['record_ref']['id']=row['record_ref']['id'].replace('.v2:', '.v1:')
        with self.assertRaises(old.OfflineError):c.ControlRow.from_value(row)
    def test_wrong_configuration_and_test_membership_cannot_promote(self):
        values,bodies,evidence,assertions=state();snapshot=checked(values,bodies,evidence,assertions).snapshot
        with self.assertRaises(s.ControlError):s.check_delegated_control(snapshot,bodies,evidence,profile='TEST_ONLY',protected_config='d'*64,assertions=assertions)
        with self.assertRaises(s.ControlError):s.check_delegated_control(snapshot,bodies,evidence,profile='PRODUCTION',protected_config=CONFIG,assertions=assertions)
    def test_source_registration_configuration_mismatch_quarantines(self):
        values,bodies,evidence,assertions=state()
        next(v for v in values if v['family']=='registration')['config_sha256']='d'*64
        with self.assertRaises(s.ControlError):checked(values,bodies,evidence,assertions)
    def test_fabricated_d04_source_pass_is_not_qualified(self):
        values,bodies,evidence,assertions=state()
        next(v for v in values if v['family']=='source')['kind']='D04'
        with self.assertRaises(s.ControlError):checked(values,bodies,evidence,assertions)
    def test_wrong_principal_and_corrupt_evidence_quarantine(self):
        for mutation in ('principal','evidence'):
            values,bodies,evidence,assertions=state()
            if mutation=='principal':next(v for v in values if v['family']=='binding')['principal']['subject']='wrong-owner'
            else:evidence[next(iter(evidence))]=b'{}'
            with self.subTest(mutation=mutation),self.assertRaises(s.ControlError):checked(values,bodies,evidence,assertions)
    def test_terminal_nonce_and_unknown_result_cannot_be_revived(self):
        values,bodies,evidence,assertions=state(True)
        next(v for v in values if v['family']=='nonce')['state']='PENDING'
        with self.assertRaises(s.ControlError):checked(values,bodies,evidence,assertions)
    def test_exact_versioned_transition_remains_preparation(self):
        before,after,head,*_=vector()
        candidate=p.prepare_delegated_transition(before,after,head,group='T5',transition='INVALIDATE',record_refs=[])
        self.assertEqual(candidate.authority,'NONE')
        self.assertEqual(r.parse_metadata(candidate.checkpoint).to_dict()['authority_config_sha256'],CONFIG)
        with self.assertRaises(s.ControlError):p.prepare_transition(before,after,head,group='T5',transition='INVALIDATE',record_refs=[])
    def test_recovery_requires_new_epoch_and_incarnation(self):
        before,after,head,*_=vector('RECOVER')
        self.assertEqual(p.prepare_delegated_transition(before,after,head,group='T9',transition='RECOVER',record_refs=[]).authority,'NONE')
        with self.assertRaises(s.ControlError):p.prepare_delegated_transition(before,after,head,group='T5',transition='INVALIDATE',record_refs=[])
    def test_transport_enrollment_and_finalize_do_not_create_authority(self):
        before,after,head,*_=vector();client=MemoryClient()
        ledger=m.DelegatedDynamoReservations(client,table_arn=ARN,instance=r.parse_json(head)['authority_instance'],max_attempts=100)
        self.assertEqual(ledger.enroll_genesis(head,before.snapshot).authority,'NONE');self.assertTrue(ledger.quarantined)
        ledger.observe_current(independent_checkpoint=head)
        candidate=p.prepare_delegated_transition(before,after,head,group='T5',transition='INVALIDATE',record_refs=[])
        ledger.prepare(candidate);ledger.finalize(candidate,independent_checkpoint=candidate.checkpoint)
        self.assertTrue(ledger.quarantined)
        fresh=m.DelegatedDynamoReservations(client,table_arn=ARN,instance=ledger.instance,max_attempts=100)
        self.assertTrue(fresh.quarantined)
    def test_mismatched_snapshot_header_cannot_reserve_even_with_forged_dataclass(self):
        before,after,head,*_=vector();client=MemoryClient()
        ledger=m.DelegatedDynamoReservations(client,table_arn=ARN,instance=r.parse_json(head)['authority_instance'],max_attempts=100)
        ledger.enroll_genesis(head,before.snapshot);ledger.observe_current(independent_checkpoint=head)
        candidate=p.prepare_delegated_transition(before,after,head,group='T5',transition='INVALIDATE',record_refs=[])
        before_calls=len(client.calls)
        with self.assertRaises(m.LedgerError):ledger.prepare(replace(candidate,snapshot=before.snapshot))
        self.assertEqual(before_calls,len(client.calls));self.assertTrue(ledger.quarantined)


if __name__=='__main__':unittest.main()
