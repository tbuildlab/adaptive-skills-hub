"""Versioned custody simulations, never production or real AWS proof."""
from datetime import datetime,timedelta,timezone
from dataclasses import replace
import unittest
from ash import g3_checkpoint_custody as f
from ash import g3_delegated_control_codec as c
from scripts import g3_n01_storage_contract as v
from tests.test_g3_d03_s3_fence import MemoryS3


class N01CustodyTests(unittest.TestCase):
    def setUp(self):
        self.before,self.head,self.descriptor,self.next,self.registration=v.inputs('c'*64,1)
        self.client=MemoryS3();self.scope=v.scope(self.registration)
        self.fence=f.N01S3Fence(self.client,self.scope)
        self.until=datetime.now(timezone.utc)+timedelta(hours=1)
        self.install(self.head,self.before.snapshot,self.descriptor,0)
    def install(self,head,snapshot,descriptor,seq,journal=True):
        for digest,raw in v.blobs(snapshot,descriptor).items():
            key=f.NORMAL+'objects/'+digest
            if key not in self.client.rows:self.client.add(key,raw)
        if journal:self.client.add(f.NORMAL+f'journal/{seq:020d}',head)
    def read(self):return self.fence.read(valid_until=self.until)
    def test_complete_closed_genesis_is_storage_only(self):
        result=self.read();self.assertEqual(result.head,f.reference(self.head))
        self.assertEqual(result.authority,'NONE');self.assertTrue(self.fence.quarantined)
    def test_v2_append_preserves_closed_root_and_config(self):
        self.install(self.next.checkpoint,self.next.snapshot,self.next.descriptor,1,False)
        result=self.fence.append(self.next.checkpoint,self.read().head,valid_until=self.until)
        self.assertEqual(result.authority,'NONE');self.assertEqual(len(result.checkpoints),2)
        self.assertEqual(c.decode(result.controls[-1])['recovery_sequence'],1)
    def test_wrong_config_denies_complete_bytes(self):
        self.fence.registration=replace(self.scope,config_sha256='d'*64)
        with self.assertRaises(f.FenceError):self.read()
    def test_fork_duplicate_version_denies(self):
        self.client.add(f.NORMAL+'journal/'+20*'0',self.head,duplicate=True)
        with self.assertRaises(f.FenceError):self.read()
    def test_partial_or_expired_inventory_never_passes(self):
        self.client.mode='partial'
        with self.assertRaises(f.FenceError):self.read()
        self.client.mode=None
        with self.assertRaises(f.FenceError):self.fence.read(valid_until=datetime.now(timezone.utc))
    def test_unknown_append_only_read_reconciliation(self):
        self.install(self.next.checkpoint,self.next.snapshot,self.next.descriptor,1,False)
        self.client.mode='unknown-after'
        with self.assertRaises(f.FenceError):
            self.fence.append(self.next.checkpoint,f.reference(self.head),valid_until=self.until)
        with self.assertRaises(f.FenceError):
            self.fence.append(self.next.checkpoint,f.reference(self.head),valid_until=self.until)
        self.client.mode=None;self.assertEqual(self.fence.reconcile(valid_until=self.until).authority,'NONE')
        self.assertEqual(len([call for call in self.client.calls if call[0]=='put']),1)
    def test_production_or_wrong_instance_registration_denied(self):
        for fields in (dict(purpose='PRODUCTION'),dict(authority_instance='other'),dict(generation=True)):
            with self.assertRaises(ValueError):replace(self.scope,**fields)
    def test_unapproved_recovery_does_not_bypass_independent_custody(self):
        body=c.decode(self.next.checkpoint)
        with self.assertRaises(f.FenceError):
            self.fence.independent_recovery_authorization(body,f.reference(self.next.checkpoint),self.until)
    def recovery(self,generation=2):
        current,candidate,registration=v.recovery_inputs(self.registration)
        self.install(current.checkpoint,current.snapshot,current.descriptor,1)
        self.install(candidate.checkpoint,candidate.snapshot,candidate.descriptor,2)
        body=c.decode(candidate.checkpoint)
        self.client.add(f.APPROVALS+f'recover/{2:020d}/authorization.json',c.canonical(dict(
            schema_version='nexus.g3.n01.storage-admin.v1',purpose='TEST_ONLY',
            config_sha256=registration['config_sha256'],generation=generation,
            checkpoint=f.reference(candidate.checkpoint),previous_checkpoint=body['previous_checkpoint'])))
        return candidate,registration
    def test_exact_independent_recovery_remains_closed_and_none(self):
        candidate,registration=self.recovery()
        self.fence=f.N01S3Fence(self.client,v.scope(registration))
        result=self.read();self.assertEqual(result.head,f.reference(candidate.checkpoint))
        self.assertEqual(result.authority,'NONE')
        self.assertEqual(c.decode(result.checkpoints[-1])['authority_epoch'],2)
    def test_stale_registration_generation_denies_latest_history(self):
        self.recovery()
        with self.assertRaises(f.FenceError):self.read()
    def test_wrong_admin_generation_cannot_qualify_recovery(self):
        candidate,registration=self.recovery(generation=1)
        self.fence=f.N01S3Fence(self.client,v.scope(registration))
        with self.assertRaises(f.FenceError):self.read()


if __name__=='__main__':unittest.main()
