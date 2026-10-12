"""One explicitly authorized forward restart from the retained Owner head 4.

Historical R bytes are evidence only. They never enroll this process, restore
an Owner session, enable writes, or permit automatic recovery/redispatch.
"""
from dataclasses import replace
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as c
from ash import g3_delegated_record_codec as r
from ash import g3_n01_controller_bootstrap as boot
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_membership_custody as membership
from ash.g3_control_semantics import require

PROFILE='OWNER_FORWARD_RESTART_V1'
SOURCE_PREFIX=custody.APPROVALS+'current-source-controller-restart-v1/'
RECOVERY_PREFIX=custody.APPROVALS+'owner-controller-recovery-restart-v1/'
HEAD4=dict(id=r.PREFIX+'recovery-checkpoint.v2:75e56d2752a0775bab644785d609542fcbd27e37db120ac60b369bb6c1edbc63',
    body_sha256='0223d350fe6852b72bfa632c6c88acdb266ba6855aa5e6ec7d9e5aca7929bb71')
HEAD3=dict(id=r.PREFIX+'recovery-checkpoint.v2:fa3ddbfd0b63119dfeb753a19957a321e314b7d7749ae3cf7738ee51032ff7a1',
    body_sha256='07b698c453d259d8c7e832bb7220e84dd123ea3404872caadf1e54456e12a5a0')
OLD_NONCE='7cff975cfab6ce5e1dff8896393f900ef2070cbe6863a2b6aebd492c20497acc'
OLD_SOURCE_SHA='5df5dec882f24b6d973faf3816201b9e4dede79c4b07bb1adfd31e8f73762012'
OLD_AUTH_SHA='453d8c6748ac9dcfa059e3eaf8926ae3da826f7ecb91fd2fbb9c419ab80ebdbc'
OLD_ARTIFACT='753940e1c9a7eb30c31ad41cdd99dc27c6f0c8686703d2de7579ec7a1219ee77'
OLD_ENV=dict(VERCEL_ENV='production',VERCEL_PROJECT_ID=source.HOST_PROJECT,
    VERCEL_DEPLOYMENT_ID='dpl_D9FFUQGNZKSxdetaR5byf8vEVydM',
    VERCEL_URL='nexus-g3-qual-aavlane6w-tdy0225.vercel.app')
BINDING_ID='n01-owner-binding-restart-v1'
REGISTRATION_ID='n01-owner-only-source-restart-v1'
SOURCE_ID='n01-owner-enrollment-restart-v1'


def require_profile(value):
    require(value is None or value==PROFILE and type(value) is str)


def historical_authorization(fence,body,ref,valid_until):
    """Fresh independently retained exact old source and RECOVER 3, read only."""
    require(ref==HEAD3 and body['recovery_sequence']==body['authority_epoch']==3
        and body['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    remaining=fence.max_attempts-fence.attempts;require(remaining>=8)
    observed=[]
    try:
        for prefix,digest in ((custody.APPROVALS+'current-source-controller-v3/',OLD_SOURCE_SHA),
            (custody.APPROVALS+'owner-controller-recovery-v3/00000000000000000003/',OLD_AUTH_SHA)):
            reader=custody.N01S3Fence(fence.client,replace(fence.registration,prefix=prefix),max_attempts=4)
            try:
                inventory=reader.inventory('')
                name='registration.json' if digest==OLD_SOURCE_SHA else 'authorization.json'
                require(len(inventory)==1 and inventory[0][0]==prefix+name)
                raw=reader.retained(*inventory[0],valid_until)
                require(c.digest(raw)==digest and reader.inventory('')==inventory)
                observed.append(raw)
            finally:fence.attempts+=reader.attempts
        value=c.decode(observed[0]);require(set(value)==source.FIELDS)
        require(value['process_nonce']==OLD_NONCE and value['artifact_inventory_sha256']==OLD_ARTIFACT
            and value['deployment_id']==OLD_ENV['VERCEL_DEPLOYMENT_ID']
            and value['deployment_host']==OLD_ENV['VERCEL_URL'] and value['real_admission']=='NO')
        expected=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode=r.MODE,
            authority_config_sha256=source.CONFIG,source_enrollment_sha256=OLD_SOURCE_SHA,
            checkpoint=HEAD3,previous_checkpoint=body['previous_checkpoint'],authority_epoch=3,
            incarnation=body['incarnation'],application_generation=1,review_generation=1,
            expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        require(c.decode(observed[1])==expected)
    except Exception:
        fence.quarantined=True
        raise ValueError('N01_HISTORICAL_OWNER_RECOVERY_QUARANTINE') from None


def scope():
    original=boot.storage_scope()
    return replace(original,admin_checkpoint_ids=original.admin_checkpoint_ids+(HEAD3['id'],))


class HistoricalOwnerFence(membership.MembershipFence):
    """Fixed read-only historical witness; no current-source or write authority."""
    def __init__(self,client):
        super().__init__(client,scope(),profile='PRODUCTION')
    def independent_recovery_authorization(self,body,ref,valid_until):
        if body['recovery_sequence']<=2:
            return custody.N01S3Fence.independent_recovery_authorization(self,body,ref,valid_until)
        return historical_authorization(self,body,ref,valid_until)


def prepare_forward_recovery(history,*,process_nonce,now_ms):
    """No automatic invocation: one fresh R-authorized T9 after exact head 4."""
    from ash import g3_n01_owner_state as state
    require(type(history) is membership.CompleteMembership and history.head==HEAD4)
    c.old.check_type(process_nonce,'h');require(process_nonce!=OLD_NONCE)
    rows,root=state._advance(history,now_ms=now_ms)
    require(root['quarantine']=='OPEN' and root['authority_epoch']==3
        and root['recovery_sequence']==5 and root['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(all(row['family'] in ('root','revocation','recovery','binding','registration','source') for row in rows))
    bindings=[row for row in rows if row['family']=='binding']
    registrations=[row for row in rows if row['family']=='registration']
    sources=[row for row in rows if row['family']=='source']
    require(len(bindings)==len(registrations)==len(sources)==1)
    require(bindings[0]['binding_id']==state.BINDING_ID and bindings[0]['state']=='CURRENT'
        and registrations[0]['registration_id']==state.REGISTRATION_ID and registrations[0]['state']=='CURRENT'
        and registrations[0]['enforcement_sha256']==OLD_ARTIFACT
        and sources[0]['source_id']=='n01-owner-enrollment-v1' and sources[0]['state']=='CURRENT'
        and sources[0]['evidence_ref']['sha256']==OLD_SOURCE_SHA)
    sources[0].update(revision=sources[0]['revision']+1,state='RETIRED')
    root.update(authority_epoch=4,incarnation='n01-owner-'+process_nonce[:32])
    require(root['incarnation']!='n01-owner-'+OLD_NONCE[:32])
    return state._prepare(history,rows,objects={},group='T9',transition='RECOVER')
