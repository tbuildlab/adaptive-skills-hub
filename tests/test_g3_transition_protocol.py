"""Fixed contract/crash preparation only; no durable store or live authority."""
import copy
import unittest
from ash import g3_control_codec as c, g3_record_codec as r
from ash import g3_control_semantics as s, g3_transition_protocol as p
from tests.test_g3_offline_control import sample


def vector(transition='INVALIDATE',quarantine='OPEN'):
    root=sample('root');index=sample('revocation')
    root['quarantine']=quarantine
    snapshot=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in (root,index)))
    before=s.check_control(snapshot,{}, {},profile='TEST_ONLY')
    descriptor={key:root[key] for key in ('authority_instance','authority_epoch','incarnation',
        'recovery_sequence','previous_checkpoint','time_high_water_ms')}
    descriptor.update(transition_kind='GENESIS',record_refs=[],control_after_sha256=snapshot.control_after_sha256)
    ledger=r.domain_digest(r.PREFIX+'ledger-commit.v1',descriptor)
    value={key:v for key,v in descriptor.items() if key!='control_after_sha256'}
    value.update(schema_version=r.PREFIX+'recovery-checkpoint.v1',ledger_commit_sha256=ledger)
    raw=r.canonical_bytes(value);ref=p.checkpoint_ref(raw)
    current=dict(root,revision=2,recovery_sequence=1,previous_checkpoint=ref,time_high_water_ms=1)
    if transition=='RECOVER':current.update(authority_epoch=2,incarnation='new-incarnation')
    history=sample('recovery');history.update(sequence=0,checkpoint_ref=ref,
        control_sha256=snapshot.control_after_sha256,descriptor_sha256=ledger)
    values=[current,index,history]
    def checked(values):
        snap=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in values))
        return s.check_control(snap,{ref['id']:raw},{},profile='TEST_ONLY')
    return before,checked(values),raw,values,checked


class TransitionProtocolTests(unittest.TestCase):
    def setUp(self):self.before,self.after,self.head,self.values,self.checked=vector()
    def prepare(self,**kw):
        return p.prepare_transition(self.before,self.after,self.head,
            **dict(dict(group='T5',transition='INVALIDATE',record_refs=[]),**kw))
    def reject(self,**kw):
        with self.assertRaises(s.ControlError):self.prepare(**kw)
    def test_exact_candidate_is_not_authority_or_receipt(self):
        prepared=self.prepare();self.assertEqual(prepared.authority,'NONE')
        self.assertEqual(r.parse_metadata(prepared.checkpoint).to_dict()['recovery_sequence'],1)
    def test_deterministic_preparation(self):self.assertEqual(self.prepare(),self.prepare())
    def test_wrong_transaction_group(self):self.reject(group='T7')
    def test_unknown_transition_or_group(self):
        self.reject(group='T10');self.reject(transition='GRANT_MODEL')
    def test_current_checkpoint_must_bind_full_snapshot(self):
        value=r.parse_json(self.head);value['ledger_commit_sha256']='e'*64
        self.head=r.canonical_bytes(value);self.reject()
    def test_stale_head(self):
        value=r.parse_json(self.head);value['incarnation']='wrong'
        self.head=r.canonical_bytes(value);self.reject()
    def test_sequence_cannot_be_skipped(self):
        self.values[0]['recovery_sequence']=2
        # Even a manually constructed result cannot skip transport checks.
        snap=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in self.values))
        self.after=s.CheckedControl(snap,c.verify_snapshot(snap));self.reject()
    def test_history_cannot_be_deleted(self):
        snap=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in self.values[:2]))
        self.after=s.CheckedControl(snap,c.verify_snapshot(snap));self.reject()
    def test_epoch_change_requires_recovery(self):
        self.values[0]['authority_epoch']=2;self.after=self.checked(self.values);self.reject()
    def test_incarnation_change_requires_recovery(self):
        self.values[0]['incarnation']='wrong';self.after=self.checked(self.values);self.reject()
    def test_recovery_requires_new_incarnation_and_next_epoch(self):
        self.before,self.after,self.head,self.values,self.checked=vector('RECOVER')
        self.assertEqual(self.prepare(group='T9',transition='RECOVER').authority,'NONE')
        root=next(c.decode(row.value) for row in self.before.rows if c.decode(row.value)['family']=='root')
        self.values[0]['incarnation']=root['incarnation'];self.after=self.checked(self.values)
        self.reject(group='T9',transition='RECOVER')
    def test_untracked_record_cannot_be_added_to_checkpoint(self):
        self.reject(record_refs=[dict(id=r.PREFIX+'owner-decision.v1:'+'a'*64,body_sha256='b'*64)])
    def test_quarantine_cannot_reopen_in_normal_transition(self):
        self.before,self.after,self.head,self.values,self.checked=vector(quarantine='CLOSED')
        self.values[0]['quarantine']='OPEN';self.after=self.checked(self.values)
        self.reject()


if __name__=='__main__':unittest.main()
