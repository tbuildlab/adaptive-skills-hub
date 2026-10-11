"""Synthetic v2 state examples only, with actual fixture-reference hashes."""
import copy
from ash import g3_control_codec as old_control, g3_record_codec as old_records
from ash import g3_delegated_control_codec as c, g3_delegated_record_codec as r
from ash import g3_control_semantics as s, g3_transition_protocol as p
from tests.test_g3_control_semantics import terminal_fixture
from tests.test_g3_offline_control import sample

CONFIG = 'c'*64
CONFIG_FIELDS = dict(authority_mode=r.MODE,authority_config_sha256=CONFIG,d04_historical_status=r.D04_STATUS)


def state(claimed=False):
    values,bodies,evidence,assertions=terminal_fixture(claimed)
    modern={};references={}
    def ref(value):
        if value['id'] in references:return references[value['id']]
        raw=bodies[value['id']]
        assert old_control.digest(raw)==value['body_sha256']
        body=convert(old_records.parse_json(raw))
        if body['schema_version'].startswith(old_records.PREFIX):
            body['schema_version']=body['schema_version'][:-1]+'2';body.update(CONFIG_FIELDS)
            if 'gate_facts' in body:
                body['gate_facts']=[f for f in body['gate_facts'] if f['kind']!='D04_EXECUTOR_EXCLUSION']
            if body['schema_version']==r.PREFIX+'presentation-view.v2':
                challenge=old_records.parse_json(modern[body['challenge']['id']])
                projection=dict(challenge_body=challenge,owner_context=body['owner_context'],
                                template_revision=body['template_revision'],expires_at_ms=body['expires_at_ms'])
                body['presentation_sha256']=r.domain_digest(r.PREFIX+'presentation-material.v1',projection)
            elif body['schema_version'] in (r.PREFIX+'owner-decision.v2',r.PREFIX+'trusted-decision-receipt.v2'):
                view=old_records.parse_json(modern[body['view']['id']])
                body['presentation_sha256']=view['presentation_sha256']
            raw=r.canonical_bytes(body);parsed=r.parse_metadata(raw)
            actual=dict(id=parsed.record_id,body_sha256=parsed.body_sha256)
        else:actual=dict(value)
        references[value['id']]=actual;modern[actual['id']]=raw
        return actual
    def convert(value):
        if type(value) is dict:
            if set(value)=={'id','body_sha256'}:return ref(value)
            return {k:convert(v) for k,v in value.items()}
        if type(value) is list:return [convert(v) for v in value]
        return value
    result=[]
    for value in values:
        if value['family']=='source' and value['kind']=='D04':continue
        value=convert(copy.deepcopy(value));value['schema_version']=c.VERSION
        if value['family']=='root':value.update(CONFIG_FIELDS)
        if value['family']=='registration':value['config_sha256']=CONFIG
        if value['family']=='view':
            value['presentation_sha256']=old_records.parse_json(modern[value['record_ref']['id']])['presentation_sha256']
        result.append(value)
    return result,modern,evidence,assertions


def checked(values,bodies,evidence,assertions,config=CONFIG):
    snapshot=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in values))
    return s.check_delegated_control(snapshot,bodies,evidence,profile='TEST_ONLY',
                                    protected_config=config,assertions=assertions)


def vector(transition='INVALIDATE',quarantine='OPEN'):
    root=sample('root');root.update(schema_version=c.VERSION,quarantine=quarantine,**CONFIG_FIELDS)
    index=sample('revocation');index['schema_version']=c.VERSION
    before=checked([root,index],{}, {},{})
    descriptor={key:root[key] for key in ('authority_instance','authority_epoch','incarnation',
        'recovery_sequence','previous_checkpoint','time_high_water_ms',*r.CONFIG_FIELDS.split())}
    descriptor.update(transition_kind='GENESIS',record_refs=[],control_after_sha256=before.snapshot.control_after_sha256)
    ledger=r.domain_digest(r.PREFIX+'ledger-commit.v2',descriptor)
    value={k:v for k,v in descriptor.items() if k!='control_after_sha256'}
    value.update(schema_version=r.PREFIX+'recovery-checkpoint.v2',ledger_commit_sha256=ledger)
    raw=r.canonical_bytes(value);parsed=r.parse_metadata(raw)
    reference=dict(id=parsed.record_id,body_sha256=parsed.body_sha256)
    current=dict(root,revision=2,recovery_sequence=1,previous_checkpoint=reference,time_high_water_ms=1)
    if transition=='RECOVER':current.update(authority_epoch=2,incarnation='new-incarnation')
    history=sample('recovery');history.update(schema_version=c.VERSION,sequence=0,checkpoint_ref=reference,
        control_sha256=before.snapshot.control_after_sha256,descriptor_sha256=ledger)
    values=[current,index,history]
    return before,checked(values,{reference['id']:raw},{},{}),raw,values
