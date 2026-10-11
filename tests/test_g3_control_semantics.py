"""Synthetic complete control joins; never enrolled production membership."""
import copy
import unittest
from ash import g3_control_codec as c
from ash import g3_record_codec as r
from ash import g3_control_semantics as s
from tests.test_g3_offline_control import sample
from tests.test_g3_production_metadata import samples, binding, context


def fixture():
    bodies={}; evidence={}; assertions={}
    def record(value):
        raw=r.canonical_bytes(value); ident=r.record_id(value)
        bodies[ident]=raw
        return dict(id=ident,body_sha256=c.digest(raw))
    def proof_bytes(value):
        if type(value) is dict:
            if set(value)=={'ref','sha256'}:
                raw=r.canonical_bytes({'synthetic':value['ref']})
                evidence[value['ref']]=raw;value['sha256']=c.digest(raw)
            else:
                for child in value.values():proof_bytes(child)
        elif type(value) is list:
            for child in value:proof_bytes(child)
    challenge,view,*_=samples(); proof_bytes(challenge);proof_bytes(view)
    challenge['material']['dispatch_material_sha256']=r.domain_digest(r.PREFIX+'dispatch-material.v1',challenge['material']['dispatch_payload'])
    challenge['proposal_id']=r.PREFIX+'proposal-material.v1:'+r.domain_digest(r.PREFIX+'proposal-material.v1',challenge['material'])
    challenge['binding'].update(workspace_id=challenge['material']['scope']['workspace_id'],project_id=challenge['material']['scope']['project_id'])
    genesis=samples()[-1];genesis_ref=record(genesis)
    challenge['stamp']['base_checkpoint']=genesis_ref
    challenge_ref=record(challenge)
    view['stamp']['base_checkpoint']=genesis_ref;view['challenge']=challenge_ref
    projection=dict(challenge_body=challenge,owner_context=view['owner_context'],
        template_revision=view['template_revision'],expires_at_ms=view['expires_at_ms'])
    view['presentation_sha256']=r.domain_digest(r.PREFIX+'presentation-material.v1',projection)
    view_ref=record(view)
    bound=sample('binding');b=challenge['binding'];bound.update(binding_id=b['binding_id'],principal=b['owner'],
        workspace_id=b['workspace_id'],project_id=b['project_id'])
    ctx=sample('context');ctx.update(context_id=context()['context_id'],binding_id=b['binding_id'],
        authority_epoch=1,incarnation='synthetic-run',identity_evidence=view['owner_context']['identity_evidence'],
        session_evidence=view['owner_context']['session_evidence'])
    registered=sample('registration');registered.update(registration_id='registered-test-only',purpose='TEST_ONLY')
    root=sample('root');root.update(authority_instance='synthetic-authority',authority_epoch=1,
        incarnation='synthetic-run',recovery_sequence=1,previous_checkpoint=genesis_ref,time_high_water_ms=1000)
    history=sample('recovery');history.update(sequence=0,checkpoint_ref=genesis_ref,
        descriptor_sha256=genesis['ledger_commit_sha256'])
    challenge_row=sample('challenge');challenge_row.update(challenge_id='synthetic-challenge',
        record_ref=challenge_ref,context_id=ctx['context_id'],view_id='synthetic-view',nonce=challenge['nonce'],
        expires_at_ms=challenge['expires_at_ms'])
    view_row=sample('view');view_row.update(view_id='synthetic-view',record_ref=view_ref,
        challenge_id=challenge_row['challenge_id'],context_id=ctx['context_id'],
        template_revision=view['template_revision'],presentation_sha256=view['presentation_sha256'])
    nonce=sample('nonce');nonce.update(nonce=challenge['nonce'],challenge_id=challenge_row['challenge_id'])
    values=[root,history,bound,ctx,registered,sample('revocation'),challenge_row,view_row,nonce]
    for index,(ref,raw) in enumerate(evidence.items()):
        source=sample('source');assertion=r.canonical_bytes({'fixture':ref})
        assertions[c.digest(assertion)]=assertion
        source.update(source_id='source-'+str(index),evidence_ref={'ref':ref,'sha256':c.digest(raw)},
            assertion_sha256=c.digest(assertion),kind='D01',principal=bound['principal'],
            binding_id=bound['binding_id'],context_id=ctx['context_id'],registration_id=registered['registration_id'])
        values.append(source)
    return values,bodies,evidence,assertions


def terminal_fixture(claimed=False):
    from ash import g3_authorization as legacy
    values,bodies,evidence,assertions=fixture()
    def row(family):return next(value for value in values if value['family']==family)
    def record(value):
        raw=r.canonical_bytes(value)
        if value['schema_version']==legacy.GRANT_SCHEMA:ident=legacy.approval_grant(value).grant_id
        else:ident=r.record_id(value)
        bodies[ident]=raw;return dict(id=ident,body_sha256=c.digest(raw))
    def actual_proof(value):
        if type(value) is dict:
            if set(value)=={'ref','sha256'}:value['sha256']=c.digest(evidence[value['ref']])
            else:
                for child in value.values():actual_proof(child)
        elif type(value) is list:
            for child in value:actual_proof(child)
    challenge=r.parse_json(bodies[row('challenge')['record_ref']['id']])
    view=r.parse_json(bodies[row('view')['record_ref']['id']])
    templates=samples();decision=templates[2]
    decision.update(stamp=challenge['stamp'],challenge=row('challenge')['record_ref'],view=row('view')['record_ref'],
        binding=challenge['binding'],owner_context=view['owner_context'],proposal_id=challenge['proposal_id'],
        nonce=challenge['nonce'],presentation_sha256=view['presentation_sha256'])
    actual_proof(decision);decision_ref=record(decision)
    receipt=templates[3]
    receipt.update(stamp=challenge['stamp'],owner_decision=decision_ref,
        **{key:decision[key] for key in ('challenge','view','binding','owner_context','proposal_id','nonce','presentation_sha256','decision')})
    actual_proof(receipt);receipt_ref=record(receipt)
    row('challenge')['state']='CONFIRM';row('context')['state']='CONSUMED'
    row('nonce').update(state='CONSUMED',decision_ref=decision_ref)
    value=sample('decision');value.update(challenge_id=row('challenge')['challenge_id'],record_ref=decision_ref,
        choice='CONFIRM',context_id=row('context')['context_id'],view_id=row('view')['view_id'],nonce=challenge['nonce']);values.append(value)
    value=sample('receipt');value.update(challenge_id=row('challenge')['challenge_id'],record_ref=receipt_ref,
        decision_ref=decision_ref,expires_at_ms=receipt['confirmation_expires_at_ms']);values.append(value)
    material=challenge['material'];registered=row('registration')
    grant=dict(schema_version=legacy.GRANT_SCHEMA,capability_id=material['subject']['capability_id'],
        subject_id=material['subject_id'],subject_sha256=material['subject_id'].rsplit(':',1)[1],
        scope=material['scope'],effective_at=1001,expires_at=15000,issuer_ref=registered['issuer_ref'],
        decision_evidence=copy.deepcopy(decision['origin_evidence']))
    grant_ref=record(grant)
    value=sample('grant');value.update(grant_id=grant_ref['id'],record_ref=grant_ref,receipt_ref=receipt_ref,
        issuer_registration=registered['registration_id'],use_until_ms=15000);values.append(value)
    value=sample('revocation');value.update(index_id=grant_ref['id'],grant_id=grant_ref['id'],state='CLEAR');values.append(value)
    intent=templates[4]
    intent.update(stamp=challenge['stamp'],receipt=receipt_ref,challenge=decision['challenge'],binding=challenge['binding'],
        owner_context=view['owner_context'],proposal_id=challenge['proposal_id'],subject_id=material['subject_id'],
        scope_sha256=material['scope_sha256'],dispatch_material_sha256=material['dispatch_material_sha256'],
        grant=grant_ref,use_until_ms=15000)
    intent['revocation_read'].update(grant=grant_ref)
    mapping={'D01_IDENTITY_CONTEXT':'D01','D03_RECOVERY_FRESHNESS':'D03','D04_EXECUTOR_EXCLUSION':'D04',
        'TECHNICAL':'TECHNICAL','TASK':'TASK','HOST':'HOST','G1':'G1','G2':'G2'}
    for fact in intent['gate_facts']:
        ref='gate-'+mapping[fact['kind']].lower();raw=r.canonical_bytes({'synthetic':ref})
        evidence[ref]=raw;fact['source_evidence']=dict(ref=ref,sha256=c.digest(raw))
        assertion=r.canonical_bytes({'fixture':ref});assertions[c.digest(assertion)]=assertion
        value=copy.deepcopy(row('source'));value.update(source_id=ref,evidence_ref=fact['source_evidence'],
            assertion_sha256=c.digest(assertion),kind=mapping[fact['kind']]);values.append(value)
    intent_ref=record(intent)
    value=sample('intent');value.update(intent_id=intent['intent_key'],record_ref=intent_ref,task_id=material['scope']['task_id'],
        grant_id=grant_ref['id'],target_sha256=material['targets']['content_sha256'],payload_sha256=material['dispatch_payload']['content_sha256'],
        registration_id=registered['registration_id'],context_id=row('context')['context_id'],use_until_ms=15000);values.append(value)
    if claimed:
        row('intent')['state']='CONSUMED';row('grant')['state']='CONSUMED'
        claim=templates[5];claim.update(stamp=challenge['stamp'],intent=intent_ref,grant=grant_ref,
            dispatch_material_sha256=material['dispatch_material_sha256'],gate_facts=copy.deepcopy(intent['gate_facts']))
        claim['revocation_read'].update(grant=grant_ref);claim_ref=record(claim)
        result=templates[6];result.update(stamp=challenge['stamp'],intent=intent_ref,grant=grant_ref,
            dispatch_material_sha256=material['dispatch_material_sha256'],claim=claim_ref);result_ref=record(result)
        value=sample('claim');value.update(attempt_key=claim['attempt_key'],intent_id=intent['intent_key'],
            record_ref=claim_ref,result_ref=result_ref,handoff_deadline_ms=claim['handoff_until_ms'],outcome='UNKNOWN');values.append(value)
    return values,bodies,evidence,assertions


class ControlHelpers:
    def value(self,family):return next(v for v in self.values if v['family']==family)
    def check(self,profile='TEST_ONLY'):
        snapshot=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in self.values))
        return s.check_control(snapshot,self.bodies,self.evidence,profile=profile,assertions=self.assertions)
    def reject(self):
        with self.assertRaises((s.ControlError,c.OfflineError)) as e:self.check()
        self.assertNotIn('synthetic',str(e.exception))


class ControlSemanticsTests(ControlHelpers,unittest.TestCase):
    def setUp(self):self.values,self.bodies,self.evidence,self.assertions=fixture()
    def test_complete_challenge_and_view_remain_no_authority(self):
        self.assertEqual(self.check().authority,'NONE')
    def test_test_only_registration_cannot_enter_production(self):
        with self.assertRaises(s.ControlError):self.check('PRODUCTION')
    def test_missing_global_complete_revocation_index(self):
        self.values.remove(self.value('revocation'));self.reject()
    def test_incomplete_or_stale_global_index(self):
        for changes in ({'completeness':'INCOMPLETE'},{'generation':2},{'state':'CLEAR'}):
            value=self.value('revocation');original=copy.deepcopy(value);value.update(changes)
            self.reject();value.clear();value.update(original)
    def test_missing_retained_record(self):
        self.bodies.pop(self.value('challenge')['record_ref']['id']);self.reject()
    def test_corrupt_retained_record(self):
        self.bodies[self.value('view')['record_ref']['id']]=b'{}';self.reject()
    def test_wrong_record_domain_identity(self):
        ref=self.value('view')['record_ref'];raw=self.bodies[ref['id']]
        self.bodies[ref['id']]=r.canonical_bytes(dict(r.parse_json(raw),view_key='wrong'))
        ref['body_sha256']=c.digest(self.bodies[ref['id']]);self.reject()
    def test_missing_or_corrupt_evidence(self):
        key=next(iter(self.evidence));self.evidence.pop(key);self.reject()
    def test_missing_assertion_is_not_qualified_by_pass_label(self):
        self.assertions.clear();self.reject()
    def test_wrong_binding_generation(self):
        self.value('context')['binding_generation']=2;self.reject()
    def test_wrong_incarnation(self):
        self.value('context')['incarnation']='stale';self.reject()
    def test_duplicate_active_workspace_binding(self):
        other=dict(self.value('binding'),binding_id='other-binding');self.values.append(other);self.reject()
    def test_nonce_must_resolve_exact_challenge(self):
        self.value('nonce')['challenge_id']='orphan';self.reject()
    def test_context_cannot_have_second_challenge(self):
        other=dict(self.value('challenge'),challenge_id='other-challenge');self.values.append(other);self.reject()
    def test_recovery_history_gap(self):
        self.values.remove(self.value('recovery'));self.reject()
    def test_retirement_cannot_coexist_with_current_membership(self):
        retired=sample('retirement');retired.update(entity_kind='context',entity_id=self.value('context')['context_id'],retired_sequence=1)
        self.values.append(retired);self.reject()
    def test_invalid_profile_fails_closed(self):
        with self.assertRaises(s.ControlError):self.check('CONDITIONAL')


class TerminalControlTests(ControlHelpers,unittest.TestCase):
    def setUp(self):self.values,self.bodies,self.evidence,self.assertions=terminal_fixture(True)
    def test_complete_terminal_unknown_is_consistent_but_not_authority(self):
        self.assertEqual(self.check().authority,'NONE')
    def test_unconsumed_intent_cannot_have_a_claim(self):
        self.value('intent')['state']='ADMIT_PENDING';self.reject()
    def test_unconsumed_grant_cannot_have_a_claim(self):
        self.value('grant')['state']='CURRENT';self.reject()
    def test_second_claim_for_same_intent_denies(self):
        self.values.append(dict(self.value('claim'),attempt_key='second-attempt'));self.reject()
    def test_unknown_result_cannot_be_relabeled_success(self):
        self.value('claim')['outcome']='SUCCEEDED';self.reject()
    def test_missing_per_grant_revocation_index_is_not_clear(self):
        self.values.remove(next(v for v in self.values if v['family']=='revocation' and v['grant_id'] is not None));self.reject()
    def test_wrong_gate_source_family_is_not_pass(self):
        next(v for v in self.values if v['family']=='source' and v['kind']=='G1')['kind']='D01';self.reject()



if __name__=='__main__':unittest.main()
