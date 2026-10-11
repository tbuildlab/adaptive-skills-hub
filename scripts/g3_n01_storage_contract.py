"""Storage-only qualification inputs. TEST_ONLY / NONE, never source authority.

No Owner, context, source, receipt, grant, intent or claim is fabricated here.
Production code must not import this qualification-only input builder.
"""
from ash import g3_delegated_control_codec as c, g3_delegated_record_codec as r
from ash import g3_checkpoint_custody as f
from ash.g3_control_semantics import check_delegated_control
from ash.g3_transition_protocol import prepare_delegated_transition


def inputs(config_sha256, base_time_ms):
    c.old.check_type(config_sha256,'h');c.old.check_type(base_time_ms,'u')
    root=dict(schema_version=c.VERSION,family='root',revision=1,
        authority_instance=f.INSTANCE,authority_epoch=1,incarnation='n01-storage-incarnation-1',
        recovery_sequence=0,previous_checkpoint=None,time_high_water_ms=base_time_ms,
        quarantine='CLOSED',revocation_generation=1,authority_mode=r.MODE,
        authority_config_sha256=config_sha256,d04_historical_status=r.D04_STATUS)
    index=dict(schema_version=c.VERSION,family='revocation',revision=1,index_id='authority',
        grant_id=None,revocation_refs=[],generation=1,completeness='COMPLETE',state='INDEX')
    snapshot=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in (root,index)))
    before=check_delegated_control(snapshot,{}, {},profile='TEST_ONLY',protected_config=config_sha256)
    descriptor={key:root[key] for key in ('authority_instance','authority_epoch','incarnation',
        'recovery_sequence','previous_checkpoint','time_high_water_ms',*r.CONFIG_FIELDS.split())}
    descriptor.update(transition_kind='GENESIS',record_refs=[],control_after_sha256=snapshot.control_after_sha256)
    ledger=r.domain_digest(r.PREFIX+'ledger-commit.v2',descriptor)
    body={key:value for key,value in descriptor.items() if key!='control_after_sha256'}
    body.update(schema_version=r.PREFIX+'recovery-checkpoint.v2',ledger_commit_sha256=ledger)
    genesis=c.canonical(body);previous=f.reference(genesis)
    history=dict(schema_version=c.VERSION,family='recovery',revision=1,sequence=0,
        checkpoint_ref=previous,control_sha256=snapshot.control_after_sha256,
        descriptor_sha256=ledger,state='WITNESSED')
    current=dict(root,revision=2,recovery_sequence=1,previous_checkpoint=previous,
                 time_high_water_ms=base_time_ms+1)
    next_snapshot=c.encode_snapshot(tuple(c.ControlRow.from_value(v) for v in (current,index,history)))
    after=check_delegated_control(next_snapshot,{previous['id']:genesis},{},
                                  profile='TEST_ONLY',protected_config=config_sha256)
    candidate=prepare_delegated_transition(before,after,genesis,
                                         group='T5',transition='INVALIDATE',record_refs=[])
    registration=dict(schema_version='nexus.g3.n01.storage-registration.v1',purpose='TEST_ONLY',
        authority_instance=f.INSTANCE,generation=1,config_sha256=config_sha256,
        genesis=previous,admin_checkpoint_ids=[previous['id']],normal_prefix=f.NORMAL,
        real_admission='NO',no_automatic_redispatch='REQUIRED',base_time_ms=base_time_ms)
    return before,genesis,c.canonical(descriptor),candidate,registration


def blobs(snapshot, descriptor):
    raw=c.decode(descriptor)
    result={c.digest(v):v for v in (snapshot.root,*snapshot.pages)}
    result[r.domain_digest(r.PREFIX+'ledger-commit.v2',raw)]=descriptor
    return result


def scope(value):
    return f.Registration('nexus-d03-custody-862902859484-ap-southeast-1-v1','862902859484',
        f.NORMAL,f.INSTANCE,1,value['genesis']['id'],value['genesis']['body_sha256'],
        tuple(value['admin_checkpoint_ids']),value['config_sha256'])
