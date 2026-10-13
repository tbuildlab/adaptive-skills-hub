"""Fixed Owner-only state preparation, never source authenticity or authority.

Uses existing immutable controls/records/nine-group contracts. No I/O, callbacks,
generic policy engine, grant, dispatch or fixture import. The native controller
must authenticate all source observations and execute the qualified durability
protocol; these publicly constructible NONE candidates cannot replace it.
"""
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as control
from ash import g3_delegated_record_codec as records
from ash import g3_n01_membership_custody as membership
from ash import g3_n01_retained_state as retained
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_public_review as review
from ash import g3_n02_presentation as presentation
from ash.g3_transition_protocol import prepare_delegated_transition
from ash.g3_control_semantics import require

BINDING_ID='n01-owner-binding-v1'
REGISTRATION_ID='n01-owner-only-source-v1'
WORKSPACE='adaptive-skills-hub'
PROJECT='nexus-production-qualification'
TARGET_CONTRACT=control.digest(control.canonical(dict(contract='n01-owner-projection-v1',
    fields=['provider_project','provider_user','provider_session','authenticated_at_ms','remote_expires_at_ms','factor_lineage_sha256'],
    purpose='CURRENT_IDENTITY_ONLY_NONE')))
NO_DISPATCH_CONTRACT=control.digest(control.canonical(dict(contract='n01-no-dispatch-v1',effect='NONE')))


def _advance(history,*,now_ms):
    require(type(history) is membership.CompleteMembership)
    require(type(now_ms) is int and now_ms>=0)
    rows=[control.decode(row.value) for row in history.states[-1].checked.rows]
    root=next(value for value in rows if value['family']=='root')
    require(now_ms>=root['time_high_water_ms'])
    sequence=root['recovery_sequence']
    require(sequence==len(history.checkpoints)-1 and 0<sequence<63)
    root.update(revision=root['revision']+1,recovery_sequence=sequence+1,
        previous_checkpoint=history.head,time_high_water_ms=now_ms)
    rows.append(dict(schema_version=control.VERSION,family='recovery',revision=1,sequence=sequence,
        checkpoint_ref=history.head,control_sha256=history.states[-1].checked.snapshot.control_after_sha256,
        descriptor_sha256=control.decode(history.checkpoints[-1])['ledger_commit_sha256'],state='WITNESSED'))
    return rows,root


def _prepare(history,rows,*,objects,group,transition,record_refs=None):
    snapshot=control.encode_snapshot(tuple(control.ControlRow.from_value(value) for value in rows))
    blobs=dict(history.objects)
    require(all(key not in blobs or blobs[key]==value for key,value in objects.items()))
    blobs.update(objects)
    config=next(value['authority_config_sha256'] for value in rows if value['family']=='root')
    resolved=retained.resolve_retained_state(snapshot,history.checkpoints,blobs,profile='PRODUCTION',config_sha256=config)
    return prepare_delegated_transition(history.states[-1].checked,resolved.checked,history.checkpoints[-1],
        group=group,transition=transition,record_refs=[] if record_refs is None else record_refs)


def prepare_empty_recovery(history,*,process_nonce,now_ms):
    """Only the closed empty storage lineage; never restore a prior Owner bearer."""
    require(type(process_nonce) is str and len(process_nonce)==64)
    control.old.check_type(process_nonce,'h')
    rows,root=_advance(history,now_ms=now_ms)
    require(root['quarantine']=='CLOSED' and root['recovery_sequence']==3)
    require(all(row['family'] in ('root','revocation','recovery') for row in rows))
    root.update(authority_epoch=root['authority_epoch']+1,incarnation='n01-owner-'+process_nonce[:32],quarantine='OPEN')
    return _prepare(history,rows,objects={},group='T9',transition='RECOVER')


def prepare_owner_enrollment(history,enrollment,*,now_ms,restart_profile=None):
    """Exact R-read Owner/source membership, no current authentication assertion."""
    require(type(enrollment) is source.EnrolledSource)
    value=enrollment.value
    require(set(value)==source.FIELDS and value['authority_mode']==records.MODE
            and value['authority_instance']==custody.INSTANCE and value['authority_config_sha256']==source.CONFIG)
    require(value['purpose']=='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY' and value['real_admission']=='NO')
    require(value['principal']==dict(issuer='stytch.com/'+source.PROJECT,client_id=source.PROJECT,subject=source.OWNER))
    require(value['source_kinds']==['D01','D03','OWNER_ENROLLMENT'] and value['no_automatic_redispatch']=='REQUIRED')
    selected=review.enrollment_pins(value)
    require(selected.generation==1 or restart_profile in ('OWNER_SDK_REPAIR_FORWARD_V1','OWNER_ATOMIC_FORWARD_V1'))
    require(selected.valid_from_ms<=value['issued_at_ms']<=now_ms<value['expires_at_ms']<=selected.valid_until_ms)
    require(control.digest(enrollment.canonical_bytes)==enrollment.enrollment_sha256)
    rows,root=_advance(history,now_ms=now_ms)
    require(root['quarantine']=='OPEN' and root['incarnation']=='n01-owner-'+value['process_nonce'][:32])
    require(root['authority_config_sha256']==value['authority_config_sha256'])
    binding_id,registration_id,source_id=BINDING_ID,REGISTRATION_ID,'n01-owner-enrollment-v1'
    generation=1
    if restart_profile is None:
        require(all(row['family'] in ('root','revocation','recovery') for row in rows))
    else:
        from ash import g3_n01_owner_restart as restart
        restart.require_profile(restart_profile)
        restart=restart.configuration(restart_profile)
        require(root['authority_epoch']==restart.EPOCH and root['recovery_sequence']==restart.SEQUENCE+1
            and control.decode(history.checkpoints[-1])['transition_kind']=='RECOVER'
            and control.decode(history.checkpoints[-1])['previous_checkpoint']==restart.HEAD4)
        require(all(row['family'] in ('root','revocation','recovery','binding','registration','source') for row in rows))
        bindings=[row for row in rows if row['family']=='binding']
        registrations=[row for row in rows if row['family']=='registration']
        sources=[row for row in rows if row['family']=='source']
        if restart_profile=='OWNER_ATOMIC_FORWARD_V1':
            from ash import g3_n01_owner_sdk_restart as prior
            require(len(bindings)==len(registrations)==len(sources)==3
                and state_pairs_retired(rows,(BINDING_ID,REGISTRATION_ID))
                and state_pairs_retired(rows,('n01-owner-binding-restart-v1','n01-owner-only-source-restart-v1'))
                and any(row['binding_id']==prior.BINDING_ID and row['state']=='CURRENT' for row in bindings)
                and any(row['registration_id']==prior.REGISTRATION_ID and row['state']=='CURRENT' for row in registrations)
                and all(row['state']=='RETIRED' for row in sources))
        elif restart_profile=='OWNER_SDK_REPAIR_FORWARD_V1':
            from ash import g3_n01_owner_restart as prior
            require(len(bindings)==len(registrations)==len(sources)==2
                and any(row['binding_id']==BINDING_ID and row['state']=='RETIRED' for row in bindings)
                and any(row['registration_id']==REGISTRATION_ID and row['state']=='RETIRED' for row in registrations)
                and any(row['binding_id']==prior.BINDING_ID and row['state']=='CURRENT' for row in bindings)
                and any(row['registration_id']==prior.REGISTRATION_ID and row['state']=='CURRENT' for row in registrations)
                and all(row['state']=='RETIRED' for row in sources))
        else:
            require(len(bindings)==len(registrations)==len(sources)==1
                and bindings[0]['binding_id']==BINDING_ID and bindings[0]['state']=='CURRENT'
                and registrations[0]['registration_id']==REGISTRATION_ID and registrations[0]['state']=='CURRENT'
                and sources[0]['source_id']=='n01-owner-enrollment-v1' and sources[0]['state']=='RETIRED')
        for row in (*bindings,*registrations):
            if row['state']=='CURRENT':row.update(revision=row['revision']+1,state='RETIRED')
        binding_id,registration_id,source_id=restart.BINDING_ID,restart.REGISTRATION_ID,restart.SOURCE_ID
        generation=restart.GENERATION
    rows.append(dict(schema_version=control.VERSION,family='binding',revision=1,binding_id=binding_id,
        principal=value['principal'],owner_generation=1,workspace_id=WORKSPACE,project_id=PROJECT,
        binding_generation=generation,state='CURRENT'))
    rows.append(dict(schema_version=control.VERSION,family='registration',revision=1,
        registration_id=registration_id,subject_kind='owner-context',target_revision='n01-owner-projection-v1',
        dispatch_revision='n01-no-dispatch-v1',adapter_revision='n01-owner-controller-v1',
        environment_id='vercel-nexus-g3-qual',environment_generation=value['application_generation'],
        target_contract_sha256=TARGET_CONTRACT,dispatch_contract_sha256=NO_DISPATCH_CONTRACT,
        config_sha256=value['authority_config_sha256'],enforcement_sha256=value['artifact_inventory_sha256'],
        runtime_revision=value['artifact_inventory_sha256'],n02_revision=presentation.TEMPLATE_REVISION,
        issuer_ref='n01-owner-only',state='CURRENT',purpose='PRODUCTION'))
    assertion=control.canonical(dict(schema_version='nexus.g3.n01.owner-source-observation.v1',
        kind='OWNER_ENROLLMENT',source_enrollment_sha256=enrollment.enrollment_sha256,
        principal=value['principal'],deployment_id=value['deployment_id'],process_nonce=value['process_nonce'],
        artifact_inventory_sha256=value['artifact_inventory_sha256'],observed_at_ms=now_ms,
        current_owner_authentication='NOT_YET_OBSERVED',authority='NONE',real_admission='NO'))
    digest=control.digest(assertion)
    rows.append(dict(schema_version=control.VERSION,family='source',revision=1,source_id=source_id,
        evidence_ref=dict(ref={1:'n01-r-owner-enrollment-v1',2:'n01-r-owner-enrollment-restart-v1',3:'n01-r-owner-enrollment-sdk-repair-v1',4:'n01-r-owner-enrollment-atomic-v1'}[generation],sha256=enrollment.enrollment_sha256),
        assertion_sha256=digest,kind='OWNER_ENROLLMENT',principal=value['principal'],binding_id=binding_id,
        context_id=None,registration_id=registration_id,observed_at_ms=now_ms,expires_at_ms=value['expires_at_ms'],
        conclusion='PASS',state='CURRENT'))
    objects={enrollment.enrollment_sha256:enrollment.canonical_bytes,digest:assertion}
    return _prepare(history,rows,objects=objects,group='T5',transition='INVALIDATE'),objects


def state_pairs_retired(rows,pair):
    return (any(row['family']=='binding' and row['binding_id']==pair[0] and row['state']=='RETIRED' for row in rows)
        and any(row['family']=='registration' and row['registration_id']==pair[1] and row['state']=='RETIRED' for row in rows))


def current_binding_ids(rows):
    """Only the original or explicitly retired forward qualification lineage."""
    bindings=[row for row in rows if row['family']=='binding' and row['state']=='CURRENT']
    registrations=[row for row in rows if row['family']=='registration' and row['state']=='CURRENT']
    require(len(bindings)==len(registrations)==1)
    pair=(bindings[0]['binding_id'],registrations[0]['registration_id'])
    root=next(row for row in rows if row['family']=='root')
    if pair==(BINDING_ID,REGISTRATION_ID):
        require(root['authority_epoch']==3 and bindings[0]['binding_generation']==1)
    else:
        from ash import g3_n01_owner_restart as restart
        from ash import g3_n01_owner_sdk_restart as repaired
        from ash import g3_n01_owner_atomic_restart as atomic
        if pair==(atomic.BINDING_ID,atomic.REGISTRATION_ID):
            require(root['authority_epoch']==atomic.EPOCH and bindings[0]['binding_generation']==atomic.GENERATION
                and state_pairs_retired(rows,(repaired.BINDING_ID,repaired.REGISTRATION_ID))
                and state_pairs_retired(rows,(restart.BINDING_ID,restart.REGISTRATION_ID)))
        elif pair==(repaired.BINDING_ID,repaired.REGISTRATION_ID):
            require(root['authority_epoch']==5 and bindings[0]['binding_generation']==3
                and any(row['family']=='binding' and row['binding_id']==restart.BINDING_ID and row['state']=='RETIRED' for row in rows)
                and any(row['family']=='registration' and row['registration_id']==restart.REGISTRATION_ID and row['state']=='RETIRED' for row in rows))
        else:
            require(pair==(restart.BINDING_ID,restart.REGISTRATION_ID)
                and root['authority_epoch']==4 and bindings[0]['binding_generation']==2)
        require(any(row['family']=='binding' and row['binding_id']==BINDING_ID and row['state']=='RETIRED' for row in rows)
            and any(row['family']=='registration' and row['registration_id']==REGISTRATION_ID and row['state']=='RETIRED' for row in rows))
    return pair
