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


def prepare_owner_enrollment(history,enrollment,*,now_ms):
    """Exact R-read Owner/source membership, no current authentication assertion."""
    require(type(enrollment) is source.EnrolledSource)
    value=enrollment.value
    require(set(value)==source.FIELDS and value['authority_mode']==records.MODE
            and value['authority_instance']==custody.INSTANCE and value['authority_config_sha256']==source.CONFIG)
    require(value['purpose']=='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY' and value['real_admission']=='NO')
    require(value['principal']==dict(issuer='stytch.com/'+source.PROJECT,client_id=source.PROJECT,subject=source.OWNER))
    require(value['source_kinds']==['D01','D03','OWNER_ENROLLMENT'] and value['no_automatic_redispatch']=='REQUIRED')
    require(value['application_generation']==value['review_generation']==1
        and value['review_package_sha256']==review.PACKAGE_SHA and value['review_acceptance_sha256']==review.ACCEPTANCE_SHA)
    require(review.FROM_MS<=value['issued_at_ms']<=now_ms<value['expires_at_ms']<=review.UNTIL_MS)
    require(control.digest(enrollment.canonical_bytes)==enrollment.enrollment_sha256)
    rows,root=_advance(history,now_ms=now_ms)
    require(root['quarantine']=='OPEN' and root['incarnation']=='n01-owner-'+value['process_nonce'][:32])
    require(root['authority_config_sha256']==value['authority_config_sha256'])
    require(all(row['family'] in ('root','revocation','recovery') for row in rows))
    rows.append(dict(schema_version=control.VERSION,family='binding',revision=1,binding_id=BINDING_ID,
        principal=value['principal'],owner_generation=1,workspace_id=WORKSPACE,project_id=PROJECT,
        binding_generation=1,state='CURRENT'))
    rows.append(dict(schema_version=control.VERSION,family='registration',revision=1,
        registration_id=REGISTRATION_ID,subject_kind='owner-context',target_revision='n01-owner-projection-v1',
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
    rows.append(dict(schema_version=control.VERSION,family='source',revision=1,source_id='n01-owner-enrollment-v1',
        evidence_ref=dict(ref='n01-r-owner-enrollment-v1',sha256=enrollment.enrollment_sha256),
        assertion_sha256=digest,kind='OWNER_ENROLLMENT',principal=value['principal'],binding_id=BINDING_ID,
        context_id=None,registration_id=REGISTRATION_ID,observed_at_ms=now_ms,expires_at_ms=value['expires_at_ms'],
        conclusion='PASS',state='CURRENT'))
    objects={enrollment.enrollment_sha256:enrollment.canonical_bytes,digest:assertion}
    return _prepare(history,rows,objects=objects,group='T5',transition='INVALIDATE'),objects
