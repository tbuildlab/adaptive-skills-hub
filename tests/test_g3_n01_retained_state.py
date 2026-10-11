"""Complete retained-byte resolution, never qualified provenance or live proof."""
import unittest
from ash import g3_n01_retained_state as retained
from ash import g3_delegated_control_codec as control
from scripts import g3_n01_storage_contract as fixture


class RetainedStateTests(unittest.TestCase):
    def setUp(self):
        self.before,self.head,self.descriptor,self.next,self.registration=fixture.inputs('c'*64,1)
        self.objects={control.digest(self.head):self.head}
    def check(self,**kw):
        fields=dict(snapshot=self.next.snapshot,checkpoints=(self.head,),objects=self.objects,
                    profile='TEST_ONLY',config_sha256='c'*64)
        fields.update(kw);return retained.resolve_retained_state(**fields)
    def test_complete_retained_state_is_none_and_immutable_container(self):
        result=self.check();self.assertEqual(result.authority,'NONE')
        self.assertIsInstance(result.bodies,tuple);self.assertEqual(result.evidence,())
    def test_missing_corrupted_or_wrong_hash_body_quarantines(self):
        for objects in ({},{control.digest(self.head):b'{}'},{'d'*64:self.head}):
            with self.assertRaisesRegex(ValueError,'N01_RETAINED_STATE_QUARANTINE'):self.check(objects=objects)
    def test_wrong_record_id_or_config_quarantines(self):
        with self.assertRaises(ValueError):self.check(config_sha256='d'*64)
        rows=[control.decode(row.value) for row in control.verify_snapshot(self.next.snapshot)]
        root=next(value for value in rows if value['family']=='root')
        root['previous_checkpoint']['id']='nexus.g3.production.recovery-checkpoint.v2:'+'d'*64
        snapshot=control.encode_snapshot(tuple(control.ControlRow.from_value(value) for value in rows))
        with self.assertRaises(ValueError):self.check(snapshot=snapshot)
    def test_unreferenced_blob_does_not_create_membership(self):
        objects=dict(self.objects);raw=b'{"untrusted":"PASS"}';objects[control.digest(raw)]=raw
        result=self.check(objects=objects)
        self.assertEqual(result.evidence,());self.assertEqual(result.assertions,())
        self.assertEqual(len(result.bodies),1)
    def test_missing_source_evidence_never_becomes_a_pass_label(self):
        rows=[control.decode(row.value) for row in control.verify_snapshot(self.next.snapshot)]
        from tests.test_g3_offline_control import sample
        source=sample('source');source['schema_version']=control.VERSION;rows.append(source)
        snapshot=control.encode_snapshot(tuple(control.ControlRow.from_value(value) for value in rows))
        with self.assertRaises(ValueError):self.check(snapshot=snapshot)
    def test_unknown_profile_noncanonical_or_overbounded_input_denies(self):
        for kwargs in (dict(profile='UNKNOWN'),dict(checkpoints=()),dict(objects={'d'*64:b' { }'}),
                       dict(objects={str(i):b'{}' for i in range(257)})):
            with self.assertRaises(ValueError):self.check(**kwargs)
    def full(self,claimed=False):
        from tests import g3_delegated_state_fixtures as source
        values,bodies,evidence,assertions=source.state(claimed)
        snapshot=source.checked(values,bodies,evidence,assertions).snapshot
        objects={control.digest(raw):raw for raw in (*bodies.values(),*evidence.values(),*assertions.values())}
        checkpoints=tuple(raw for ident,raw in sorted(bodies.items())
                          if ident.startswith('nexus.g3.production.recovery-checkpoint.v2:'))
        return snapshot,checkpoints,objects
    def test_full_terminal_and_consumed_unknown_history_resolves_without_authority(self):
        for claimed in (False,True):
            snapshot,checkpoints,objects=self.full(claimed)
            result=self.check(snapshot=snapshot,checkpoints=checkpoints,objects=objects)
            self.assertEqual(result.authority,'NONE');self.assertTrue(result.evidence)
            self.assertTrue(result.assertions)
    def test_retained_test_membership_cannot_be_promoted_to_production(self):
        snapshot,checkpoints,objects=self.full()
        with self.assertRaises(ValueError):self.check(snapshot=snapshot,checkpoints=checkpoints,
            objects=objects,profile='PRODUCTION')
    def test_source_assertion_and_evidence_must_both_be_retained(self):
        snapshot,checkpoints,objects=self.full()
        source=next(control.decode(row.value) for row in control.verify_snapshot(snapshot)
                    if control.decode(row.value)['family']=='source')
        for digest in (source['assertion_sha256'],source['evidence_ref']['sha256']):
            partial=dict(objects);partial.pop(digest)
            with self.assertRaises(ValueError):self.check(snapshot=snapshot,checkpoints=checkpoints,objects=partial)


if __name__=='__main__':unittest.main()
