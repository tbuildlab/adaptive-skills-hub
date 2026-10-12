"""Fixed bounded Owner decision membership, never a grant or effect.

Pure deterministic preparation. Public projections and candidates remain NONE;
only the enrolled native controller may supply actual SDK and browser-origin
observations and execute the independently fenced durability protocol.
"""
from ash import g3_n01_owner_state as state
from ash import g3_n01_owner_context as owner
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_public_review as review
from ash import g3_n02_presentation as page
from ash import g3_delegated_control_codec as c
from ash import g3_delegated_record_codec as r
from ash import g3_grant_codec as grants
from ash.g3_control_semantics import require


def _record(body,objects):
    raw=r.canonical_bytes(body);parsed=r.parse_metadata(raw)
    objects[c.digest(raw)]=raw
    return dict(id=parsed.record_id,body_sha256=parsed.body_sha256)


def _proof(rows,objects,*,name,kind,body,enrollment,context_id,now_ms,until_ms):
    raw=c.canonical(body);sha=c.digest(raw);objects[sha]=raw
    ref=dict(ref=name,sha256=sha)
    assertion=c.canonical(dict(schema_version='nexus.g3.n01.native-source-observation.v1',
        event=name,kind=kind,evidence_sha256=sha,source_enrollment_sha256=enrollment.enrollment_sha256,
        deployment_id=enrollment.value['deployment_id'],process_nonce=enrollment.value['process_nonce'],
        observed_at_ms=now_ms,authority='NONE',real_admission='NO'))
    digest=c.digest(assertion);objects[digest]=assertion
    rows.append(dict(schema_version=c.VERSION,family='source',revision=1,source_id=name,
        evidence_ref=ref,assertion_sha256=digest,kind=kind,principal=enrollment.value['principal'],
        binding_id=state.BINDING_ID,context_id=context_id,registration_id=state.REGISTRATION_ID,
        observed_at_ms=now_ms,expires_at_ms=until_ms,conclusion='PASS',state='CURRENT'))
    return ref


def _enrolled(rows,root,enrollment,now_ms):
    require(type(enrollment) is source.EnrolledSource and c.digest(enrollment.canonical_bytes)==enrollment.enrollment_sha256)
    value=enrollment.value
    require(root['quarantine']=='OPEN' and root['authority_config_sha256']==source.CONFIG
        and root['incarnation']=='n01-owner-'+value['process_nonce'][:32])
    require(review.FROM_MS<=value['issued_at_ms']<=now_ms<value['expires_at_ms']<=review.UNTIL_MS)
    bound=next(row for row in rows if row['family']=='binding' and row['binding_id']==state.BINDING_ID)
    reg=next(row for row in rows if row['family']=='registration' and row['registration_id']==state.REGISTRATION_ID)
    require(bound['state']==reg['state']=='CURRENT' and bound['principal']==value['principal'])
    require(reg['purpose']=='PRODUCTION' and reg['enforcement_sha256']==value['artifact_inventory_sha256']
        and reg['n02_revision']==page.TEMPLATE_REVISION and reg['issuer_ref']=='n01-owner-only')
    return dict(owner=bound['principal'],owner_generation=bound['owner_generation'],
        binding_id=bound['binding_id'],binding_generation=bound['binding_generation'],
        workspace_id=bound['workspace_id'],project_id=bound['project_id'])


def prepare_challenge(history,enrollment,projection,*,deadline_ms,nonce,now_ms):
    """One actual-current-context candidate and complete frozen non-effect view."""
    require(type(projection) is owner.OwnerProjection)
    require(projection.provider_project==source.PROJECT and projection.provider_user==source.OWNER)
    c.old.check_type(nonce,'h')
    require(type(deadline_ms) is int and projection.authenticated_at_ms<=now_ms<deadline_ms
        <=min(projection.authenticated_at_ms+owner.MAX_CONTEXT_MS,projection.remote_expires_at_ms,review.UNTIL_MS))
    rows,root=state._advance(history,now_ms=now_ms);binding=_enrolled(rows,root,enrollment,now_ms)
    require(not any(row['family']=='context' for row in rows))  # Fixed single qualification lineage.
    context_id='n01-owner-context-v1';view_id='n01-owner-view-v1';challenge_id='n01-owner-challenge-v1';objects={}
    until=min(deadline_ms,enrollment.value['expires_at_ms'])
    base=dict(schema_version='nexus.g3.n01.current-owner-observation.v1',provider_project=projection.provider_project,
        provider_user=projection.provider_user,provider_session=projection.provider_session,
        authenticated_at_ms=projection.authenticated_at_ms,remote_expires_at_ms=projection.remote_expires_at_ms,
        factor_lineage_sha256=projection.factor_lineage_sha256,observed_at_ms=now_ms,
        authority='NONE',real_admission='NO')
    identity=_proof(rows,objects,name='n01-current-owner-identity-v1',kind='D01',
        body=dict(base,observation='FRESH_NATIVE_EMAIL_TOTP_IDENTITY'),enrollment=enrollment,
        context_id=context_id,now_ms=now_ms,until_ms=until)
    session=_proof(rows,objects,name='n01-current-owner-session-v1',kind='D01',
        body=dict(base,observation='EXACT_ORIGINAL_SESSION_REMOTE_RECHECK'),enrollment=enrollment,
        context_id=context_id,now_ms=now_ms,until_ms=until)
    context=dict(context_id=context_id,context_generation=1,authenticated_at_ms=projection.authenticated_at_ms,
        context_expires_at_ms=until,identity_evidence=identity,session_evidence=session)
    rows.append(dict(schema_version=c.VERSION,family='context',revision=1,**context,
        binding_id=state.BINDING_ID,binding_generation=binding['binding_generation'],owner_generation=binding['owner_generation'],
        authority_epoch=root['authority_epoch'],incarnation=root['incarnation'],provider_project=projection.provider_project,
        provider_user=projection.provider_user,provider_session=projection.provider_session,
        expires_at_ms=until,state='CURRENT'))
    # Context row uses expires_at_ms, not the D05 inline projection name.
    rows[-1].pop('context_expires_at_ms')
    subject=dict(schema_version=grants.SUBJECT_SCHEMA,capability_id='nexus.owner-context',kind='local_adapter',
        provider='nexus',action='record-bounded-owner-decision',source_ref='n01-owner-controller-v1',
        revision='n01-owner-controller-v1',content_sha256=enrollment.value['artifact_inventory_sha256'],config_sha256=source.CONFIG)
    scope=dict(workspace_id=state.WORKSPACE,project_id=state.PROJECT,task_id='n01-owner-decision-qualification-v1',
        task_classes=['authority-qualification'],operations=['write'])
    def json_material(value,contract,sha):
        raw=c.canonical(value)
        return dict(contract_ref=contract,contract_sha256=sha,canonical_utf8=raw.decode(),
                    content_sha256=c.digest(raw),source_evidence=session)
    targets=json_material(dict(authority_instance=root['authority_instance'],context_id=context_id,
        purpose='BOUNDED_OWNER_DECISION_RECORD_ONLY',artifact_inventory_sha256=enrollment.value['artifact_inventory_sha256']),
        'n01-owner-projection-v1',state.TARGET_CONTRACT)
    dispatch=json_material(dict(operation='record-bounded-owner-decision',context_id=context_id,
        execution_effect='NONE',grant_issuance='DENY',real_admission='NO'),'n01-no-dispatch-v1',state.NO_DISPATCH_CONTRACT)
    material=dict(subject=subject,subject_id=grants.subject(subject).subject_id,scope=scope,scope_sha256=c.digest(c.canonical(scope)),
        requested_action=subject['action'],operations=scope['operations'],targets=targets,
        effect_summary=dict(operations=scope['operations'],targets_sha256=targets['content_sha256']),
        effect_explanation='Persist one bounded Owner decision and consume its context and nonce. No grant, product execution, production release or REAL_ADMISSION enablement is authorized.',
        dispatch_payload=dispatch,dispatch_material_sha256=r.domain_digest(r.PREFIX+'dispatch-material.v1',dispatch),
        source_evidence=[identity,session])
    stamp=dict(authority_instance=root['authority_instance'],authority_epoch=root['authority_epoch'],incarnation=root['incarnation'],
        base_recovery_sequence=root['recovery_sequence']-1,base_checkpoint=history.head)
    config=dict(authority_mode=r.MODE,authority_config_sha256=source.CONFIG,d04_historical_status=r.D04_STATUS)
    challenge=dict(schema_version=r.PREFIX+'authority-challenge.v2',stamp=stamp,binding=binding,material=material,
        proposal_id=r.PREFIX+'proposal-material.v1:'+r.domain_digest(r.PREFIX+'proposal-material.v1',material),
        nonce=nonce,issued_at_ms=now_ms,expires_at_ms=until,**config)
    challenge_ref=_record(challenge,objects)
    render_evidence=_proof(rows,objects,name='n01-fixed-owner-view-v1',kind='OWNER_ENROLLMENT',
        body=dict(schema_version='nexus.g3.n02.native-frozen-presentation.v1',challenge=challenge_ref,
            template_revision=page.TEMPLATE_REVISION,complete_material_sha256=c.digest(c.canonical(material)),
            deployment_host=enrollment.value['deployment_host'],authority='NONE',real_admission='NO'),
        enrollment=enrollment,context_id=context_id,now_ms=now_ms,until_ms=until)
    shown=dict(schema_version=r.PREFIX+'presentation-view.v2',stamp=stamp,challenge=challenge_ref,owner_context=context,
        view_key=view_id,template_revision=page.TEMPLATE_REVISION,render_evidence=render_evidence,
        presentation_sha256=r.domain_digest(r.PREFIX+'presentation-material.v1',dict(challenge_body=challenge,
            owner_context=context,template_revision=page.TEMPLATE_REVISION,expires_at_ms=until)),
        issued_at_ms=now_ms,expires_at_ms=until,**config)
    view_ref=_record(shown,objects)
    rows.extend((dict(schema_version=c.VERSION,family='challenge',revision=1,challenge_id=challenge_id,
        record_ref=challenge_ref,context_id=context_id,view_id=view_id,nonce=nonce,expires_at_ms=until,state='PENDING'),
        dict(schema_version=c.VERSION,family='view',revision=1,view_id=view_id,record_ref=view_ref,context_id=context_id,
            challenge_id=challenge_id,presentation_sha256=shown['presentation_sha256'],template_revision=page.TEMPLATE_REVISION,
            deployment_revision=enrollment.value['artifact_inventory_sha256'],state='CURRENT'),
        dict(schema_version=c.VERSION,family='nonce',revision=1,nonce=nonce,challenge_id=challenge_id,state='PENDING',decision_ref=None)))
    refs=sorted((challenge_ref,view_ref),key=lambda ref:ref['id'])
    candidate=state._prepare(history,rows,objects=objects,group='T1',transition='CHALLENGE',record_refs=refs)
    return candidate,objects,c.canonical(challenge),c.canonical(shown)


def prepare_decision(history,enrollment,decision,projection,*,now_ms):
    """Exact pending membership; caller authenticates fresh human POST and SDK."""
    require(type(decision) is page.UntrustedDecision and type(projection) is owner.OwnerProjection)
    rows,root=state._advance(history,now_ms=now_ms);binding=_enrolled(rows,root,enrollment,now_ms)
    context=next(row for row in rows if row['family']=='context')
    challenge=next(row for row in rows if row['family']=='challenge')
    shown=next(row for row in rows if row['family']=='view')
    nonce=next(row for row in rows if row['family']=='nonce')
    require(context['state']=='CURRENT' and challenge['state']==nonce['state']=='PENDING' and shown['state']=='CURRENT')
    require((projection.provider_project,projection.provider_user,projection.provider_session,projection.authenticated_at_ms)==
        (context['provider_project'],context['provider_user'],context['provider_session'],context['authenticated_at_ms']))
    require(now_ms<context['expires_at_ms']<=projection.remote_expires_at_ms)
    challenge_body=c.decode(dict(history.objects)[challenge['record_ref']['body_sha256']])
    view_body=c.decode(dict(history.objects)[shown['record_ref']['body_sha256']])
    require((decision.challenge_id,decision.view_id,decision.proposal_id,decision.nonce,decision.presentation_sha256)==
        (challenge['record_ref']['id'],shown['view_id'],challenge_body['proposal_id'],nonce['nonce'],shown['presentation_sha256']))
    require(decision.choice in ('CONFIRM','DENY'));objects={}
    origin=_proof(rows,objects,name='n01-exact-human-decision-origin-v1',kind='OWNER_ENROLLMENT',
        body=dict(schema_version='nexus.g3.n02.native-decision-origin.v1',choice=decision.choice,
            challenge_id=decision.challenge_id,view_id=decision.view_id,proposal_id=decision.proposal_id,
            nonce=decision.nonce,presentation_sha256=decision.presentation_sha256,method='POST',
            origin='https://'+enrollment.value['deployment_host'],same_site_cookie_csrf='EXACT_MATCH',
            native_current_session='SAME_ORIGINAL_SESSION_RECHECKED',observed_at_ms=now_ms,authority='NONE',real_admission='NO'),
        enrollment=enrollment,context_id=context['context_id'],now_ms=now_ms,until_ms=context['expires_at_ms'])
    common=dict(stamp=view_body['stamp'],challenge=challenge['record_ref'],view=shown['record_ref'],binding=binding,
        owner_context=view_body['owner_context'],proposal_id=decision.proposal_id,nonce=decision.nonce,
        presentation_sha256=decision.presentation_sha256,decision=decision.choice,authority_mode=r.MODE,
        authority_config_sha256=source.CONFIG,d04_historical_status=r.D04_STATUS)
    terminal=dict(schema_version=r.PREFIX+'owner-decision.v2',**common,observed_at_ms=now_ms,origin_evidence=origin)
    terminal_ref=_record(terminal,objects)
    receipt=dict(schema_version=r.PREFIX+'trusted-decision-receipt.v2',**common,owner_decision=terminal_ref,
        accepted_at_ms=now_ms,confirmation_expires_at_ms=context['expires_at_ms'],legacy_time_basis='UNIX_MS',provenance_evidence=[origin])
    receipt_ref=_record(receipt,objects)
    context.update(revision=context['revision']+1,state='CONSUMED')
    challenge.update(revision=challenge['revision']+1,state=decision.choice)
    nonce.update(revision=nonce['revision']+1,state='CONSUMED',decision_ref=terminal_ref)
    rows.extend((dict(schema_version=c.VERSION,family='decision',revision=1,challenge_id=challenge['challenge_id'],
        record_ref=terminal_ref,choice=decision.choice,context_id=context['context_id'],view_id=shown['view_id'],nonce=nonce['nonce']),
        dict(schema_version=c.VERSION,family='receipt',revision=1,challenge_id=challenge['challenge_id'],record_ref=receipt_ref,
            decision_ref=terminal_ref,expires_at_ms=context['expires_at_ms'])))
    return state._prepare(history,rows,objects=objects,group='T3',transition=decision.choice,
        record_refs=sorted((terminal_ref,receipt_ref),key=lambda ref:ref['id'])),objects


def prepare_revoke_after_consumption(history,enrollment,*,remote_result,now_ms):
    """Retain exact remote logout observation; do not manufacture a grant revoke."""
    require(remote_result=='EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY')
    rows,root=state._advance(history,now_ms=now_ms);_enrolled(rows,root,enrollment,now_ms)
    context=next(row for row in rows if row['family']=='context')
    require(context['state']=='CONSUMED' and any(row['family']=='decision' for row in rows))
    objects={}
    _proof(rows,objects,name='n01-exact-session-revocation-v1',kind='D01',
        body=dict(schema_version='nexus.g3.n01.native-session-revocation.v1',provider_session=context['provider_session'],
            exact_original_session_recheck='HTTP_404_SESSION_NOT_FOUND',observed_at_ms=now_ms,
            grant_revocation='NOT_PERFORMED_NO_GRANT',authority='NONE',real_admission='NO'),
        enrollment=enrollment,context_id=context['context_id'],now_ms=now_ms,until_ms=enrollment.value['expires_at_ms'])
    for row in rows:
        eligible=row['family'] in ('view','binding','registration')
        if row['family']=='source':eligible=row['source_id']!='n01-exact-session-revocation-v1'
        if eligible and row['state']=='CURRENT':
            row.update(revision=row['revision']+1,state='RETIRED')
    root['quarantine']='CLOSED'
    return state._prepare(history,rows,objects=objects,group='T5',transition='INVALIDATE'),objects
