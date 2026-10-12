"""Pure synthetic state preparation only; never R custody or Owner authority."""
from dataclasses import replace
import json
import unittest

from ash import g3_n01_owner_state as state
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_public_review as review
from ash import g3_n01_membership_custody as membership
from ash import g3_n01_retained_state as retained
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as codec
from scripts import g3_n01_storage_contract as storage
from tests import test_g3_n01_checkpoint_custody as fixture
from tests import test_g3_n01_source_enrollment as enrollment_fixture


def appended(history,candidate,objects):
    prior=history.history
    complete=custody.ProtectedHistory(prior.checkpoints+(candidate.checkpoint,),
        prior.versions+((custody.NORMAL+f'journal/{len(prior.checkpoints):020d}','SYNTHETIC'),),
        prior.descriptors+(candidate.descriptor,),prior.controls+(candidate.snapshot.root,),prior.pages+(candidate.snapshot.pages,))
    blobs=dict(history.objects);blobs.update(objects)
    for raw in (candidate.checkpoint,candidate.snapshot.root,*candidate.snapshot.pages):blobs[codec.digest(raw)]=raw
    checked=retained.resolve_retained_state(candidate.snapshot,complete.checkpoints,blobs,profile='PRODUCTION',config_sha256=source.CONFIG)
    return membership.CompleteMembership(complete,history.states+(checked,),tuple(sorted(blobs.items())))


class OwnerStateTests(unittest.TestCase):
    def setUp(self):
        self.vector=fixture.N01CustodyTests();self.vector.setUp();self.vector.client.rows.clear()
        self.vector.before,self.vector.head,self.vector.descriptor,self.vector.next,self.vector.registration=storage.inputs(source.CONFIG,1)
        self.vector.scope=storage.scope(self.vector.registration)
        self.vector.install(self.vector.head,self.vector.before.snapshot,self.vector.descriptor,0)
        _,registration=self.vector.recovery()
        self.history=membership.MembershipFence(self.vector.client,storage.scope(registration),profile='PRODUCTION').read(valid_until=self.vector.until)
        self.source_vector=enrollment_fixture.SourceEnrollmentTests();self.source_vector.setUp();self.addCleanup(self.source_vector.doCleanups)
        self.enrolled=self.source_vector.bind()
        self.nonce=self.enrolled.value['process_nonce'];self.now=self.source_vector.now
    def recovery(self):return state.prepare_empty_recovery(self.history,process_nonce=self.nonce,now_ms=self.now)
    def ready(self):return appended(self.history,self.recovery(),{})
    def test_exact_empty_recovery_is_next_epoch_and_new_incarnation_none(self):
        candidate=self.recovery();body=codec.decode(candidate.checkpoint)
        self.assertEqual(candidate.authority,'NONE')
        self.assertEqual((body['recovery_sequence'],body['authority_epoch']),(3,3))
        self.assertEqual(body['incarnation'],'n01-owner-'+self.nonce[:32])
        self.assertEqual(body['previous_checkpoint'],self.history.head)
        roots=[codec.decode(row.value) for row in codec.verify_snapshot(candidate.snapshot)]
        self.assertEqual(next(row['quarantine'] for row in roots if row['family']=='root'),'OPEN')
        self.assertFalse(any(row['family'] in ('context','grant','intent','claim') for row in roots))
    def test_no_automatic_recovery_from_newer_or_open_lineage_or_clock_regression(self):
        with self.assertRaises(ValueError):state.prepare_empty_recovery(self.ready(),process_nonce=self.nonce,now_ms=self.now+1)
        with self.assertRaises(ValueError):state.prepare_empty_recovery(self.history,process_nonce=self.nonce,now_ms=0)
        with self.assertRaises(ValueError):state.prepare_empty_recovery(self.history,process_nonce='bad',now_ms=self.now)
    def test_owner_enrollment_records_r_source_only_without_current_context_or_grant(self):
        candidate,objects=state.prepare_owner_enrollment(self.ready(),self.enrolled,now_ms=self.now+1)
        result=appended(self.ready(),candidate,objects)
        self.assertEqual(result.authority,'NONE');self.assertEqual(candidate.authority,'NONE')
        values=[codec.decode(row.value) for row in result.states[-1].checked.rows]
        registered=next(row for row in values if row['family']=='registration')
        self.assertEqual((registered['subject_kind'],registered['issuer_ref']),('owner-context','n01-owner-only'))
        self.assertFalse(any(row['family'] in ('context','grant','intent','claim') for row in values))
        assertion=next(json.loads(raw) for raw in objects.values() if json.loads(raw).get('kind')=='OWNER_ENROLLMENT')
        self.assertEqual(assertion['current_owner_authentication'],'NOT_YET_OBSERVED')
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(result,self.enrolled,now_ms=self.now+2)
    def test_wrong_source_purpose_principal_generation_config_or_window_denies(self):
        ready=self.ready()
        for key,value in (('purpose','PRODUCTION'),('real_admission','YES'),('application_generation',2),
            ('authority_config_sha256','d'*64),('principal',dict(self.enrolled.value['principal'],subject='different')),
            ('expires_at_ms',review.UNTIL_MS+1),('source_kinds',['D01','TASK'])):
            body=dict(self.enrolled.value,**{key:value});raw=codec.canonical(body)
            fake=source.EnrolledSource(raw,codec.digest(raw))
            with self.assertRaises(ValueError):state.prepare_owner_enrollment(ready,fake,now_ms=self.now+1)
    def test_forged_digest_closed_root_and_process_mismatch_cannot_enroll(self):
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(self.history,self.enrolled,now_ms=self.now)
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(self.ready(),replace(self.enrolled,enrollment_sha256='e'*64),now_ms=self.now)
        body=dict(self.enrolled.value,process_nonce='e'*64);raw=codec.canonical(body)
        with self.assertRaises(ValueError):state.prepare_owner_enrollment(self.ready(),source.EnrolledSource(raw,codec.digest(raw)),now_ms=self.now)


if __name__=='__main__':unittest.main()
