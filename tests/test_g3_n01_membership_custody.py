"""Full reader simulations only; no authentic writer, custody or admission."""
from dataclasses import replace
import unittest

from ash import g3_n01_membership_custody as full
from ash import g3_delegated_control_codec as codec
from ash import g3_grant_codec as grants
from ash import g3_checkpoint_custody as custody
from tests import test_g3_n01_checkpoint_custody as fixture
from tests import g3_delegated_state_fixtures as bodies_fixture


class MembershipCustodyTests(unittest.TestCase):
    def setUp(self):
        self.vector=fixture.N01CustodyTests();self.vector.setUp()
        self.reader=full.MembershipFence(self.vector.client,self.vector.scope,profile='TEST_ONLY')
    def read(self):return self.reader.read(valid_until=self.vector.until)
    def test_complete_real_shape_genesis_and_next_snapshot_resolve_as_none(self):
        self.vector.install(self.vector.next.checkpoint,self.vector.next.snapshot,self.vector.next.descriptor,1)
        result=self.read()
        self.assertEqual(result.head,custody.reference(self.vector.next.checkpoint))
        self.assertEqual(len(result.states),2);self.assertEqual(result.authority,'NONE')
        self.assertTrue(self.reader.quarantined)
        self.assertTrue(all(state.authority=='NONE' for state in result.states))
    def test_write_append_and_recovery_interfaces_deny_before_mutation(self):
        before=len(self.vector.client.calls)
        for call in (lambda:self.reader.call('put_object',Key='anything'),
                     lambda:self.reader.append(None,None),lambda:self.reader.reconcile()):
            with self.assertRaises(ValueError):call()
        self.assertEqual(before,len(self.vector.client.calls))
    def test_missing_corrupted_or_extra_opaque_object_quarantines(self):
        key=next(key for key in self.vector.client.rows if key.startswith(custody.NORMAL+'objects/'))
        original=self.vector.client.rows.pop(key)
        with self.assertRaisesRegex(ValueError,'N01_MEMBERSHIP_CUSTODY_QUARANTINE'):self.read()
        self.vector.client.rows[key]=original
        self.vector.client.add(custody.NORMAL+'objects/'+'d'*64,b'{}')
        with self.assertRaises(ValueError):self.read()
    def test_duplicate_or_gap_journal_quarantines(self):
        self.vector.client.add(custody.NORMAL+'journal/'+20*'0',self.vector.head,duplicate=True)
        with self.assertRaises(ValueError):self.read()
        self.vector.client.rows[custody.NORMAL+'journal/'+20*'0'].pop()
        self.vector.install(self.vector.next.checkpoint,self.vector.next.snapshot,self.vector.next.descriptor,2)
        with self.assertRaises(ValueError):self.read()
    def test_existing_recovery_generation_is_not_reinterpreted(self):
        candidate,registration=self.vector.recovery()
        scope=custody.Registration(**{key:getattr(self.vector.scope,key) for key in self.vector.scope.__dataclass_fields__})
        with self.assertRaises(ValueError):full.MembershipFence(self.vector.client,scope,profile='TEST_ONLY').read(valid_until=self.vector.until)
        from scripts import g3_n01_storage_contract as storage
        reader=full.MembershipFence(self.vector.client,storage.scope(registration),profile='TEST_ONLY')
        self.assertEqual(reader.read(valid_until=self.vector.until).head,custody.reference(candidate.checkpoint))
    def test_profile_unknown_or_scope_promotion_cannot_enroll_a_writer(self):
        with self.assertRaises(ValueError):full.MembershipFence(self.vector.client,self.vector.scope,profile='UNKNOWN')
        with self.assertRaises(ValueError):replace(self.vector.scope,purpose='PRODUCTION')
        result=full.MembershipFence(self.vector.client,self.vector.scope,profile='PRODUCTION').read(valid_until=self.vector.until)
        self.assertEqual(result.authority,'NONE')
        self.assertEqual(result.states[-1].evidence,())
    def test_mixed_existing_grant_and_revocation_identity_parser_is_structural(self):
        _,bodies,_,_=bodies_fixture.state()
        matched=0
        for ident,raw in bodies.items():
            value=codec.decode(raw)
            if value['schema_version'] in (grants.GRANT_SCHEMA,grants.REVOCATION_SCHEMA):
                result=full.parse_retained_record(raw)
                self.assertEqual(result.record_id,ident);self.assertEqual(result.body_sha256,codec.digest(raw))
                self.assertEqual(result.authority,'NONE');matched+=1
        self.assertGreater(matched,0)
        for raw in (b'{}',b'{"schema_version":"unsupported"}',b' { }'):
            with self.assertRaises(ValueError):full.parse_retained_record(raw)
    def test_prepared_future_descriptor_never_becomes_current_membership(self):
        self.vector.install(self.vector.next.checkpoint,self.vector.next.snapshot,self.vector.next.descriptor,1,journal=False)
        result=self.read()
        self.assertEqual(result.head,custody.reference(self.vector.head))
        self.assertEqual(len(result.states),1);self.assertEqual(result.authority,'NONE')
        value=codec.decode(self.vector.next.descriptor);value['unrecognized']='UNKNOWN'
        raw=codec.canonical(value)
        from ash import g3_delegated_record_codec as records
        key=custody.NORMAL+'objects/'+records.domain_digest(records.PREFIX+'ledger-commit.v2',value)
        self.vector.client.add(key,raw)
        with self.assertRaises(ValueError):self.read()
