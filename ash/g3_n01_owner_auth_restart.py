"""One exact head-10 forward retirement under the Owner-approved amendment.

Old terminal controller/PREAUTH remains history. This seam cannot restore it,
authenticate the Owner, dispatch providers, or create execution authority.
"""
from dataclasses import replace
from ash import g3_n01_owner_atomic_restart as prior
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as c
from ash import g3_delegated_record_codec as r
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_membership_custody as membership
from ash.g3_control_semantics import require

PROFILE='OWNER_AUTH_ATTEMPT_FORWARD_V1'
SOURCE_PREFIX=custody.APPROVALS+'current-source-controller-auth-attempt-v1/'
RECOVERY_PREFIX=custody.APPROVALS+'owner-controller-recovery-auth-attempt-v1/'
HEAD4=dict(id=r.PREFIX+'recovery-checkpoint.v2:1f2b3a821551c19b1d8c98f37ad1ef957366349175d04d7fcb38841f8fa4f4b5',body_sha256='cee49468377d9e5068c1bb07bd1faffeaa831554d06e817987899aafd0a2e7d0')
HEAD3=dict(id=r.PREFIX+'recovery-checkpoint.v2:e9cffaeac5bb818606eec93ee8b678d67882f251a09d5fa5b52ba5cc437d4911',body_sha256='5e7c419d184d224354d6c6af18190ee37b89953495ed767dac3e8a8106fddfa8')
OLD_NONCE='2f71543e6e206736d281aefb62a328afdda9f9a5f28a877f47ad183c4ac30777'
OLD_SOURCE_SHA='96375231e41cdfdc965c3e7941985ff9553c5f16bcded6dcdd5bd8d471d3cf08'
OLD_AUTH_SHA='e062a668a7c5404d9664e9af6b7c2d8897cec1aaffc9bc3622fd16e1b9f4cd67'
OLD_ARTIFACT='91c2ecb95f3e42fdd5bc3adab89c5a4dd2ebd7a7bfb6f16fd936c7b1f11ed9cd'
OLD_ENV=dict(VERCEL_DEPLOYMENT_ID='dpl_2nJDqJiwaEgbTxt4ej8PSQMLS3nW',VERCEL_URL='nexus-g3-qual-8xogl0pxo-tdy0225.vercel.app')
BINDING_ID='n01-owner-binding-auth-attempt-v1'
REGISTRATION_ID='n01-owner-only-source-auth-attempt-v1'
SOURCE_ID='n01-owner-enrollment-auth-attempt-v1'
EPOCH=7
SEQUENCE=11
GENERATION=5


def historical_authorization(fence,body,ref,valid_until):
    if body['recovery_sequence']<9:return prior.historical_authorization(fence,body,ref,valid_until)
    require(ref==HEAD3 and body['recovery_sequence']==9 and body['authority_epoch']==6
        and body['previous_checkpoint']==prior.HEAD4 and body['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(fence.max_attempts-fence.attempts>=8)
    observed=[]
    try:
        for prefix,digest,name in ((prior.SOURCE_PREFIX,OLD_SOURCE_SHA,'registration.json'),
            (prior.RECOVERY_PREFIX+'00000000000000000009/',OLD_AUTH_SHA,'authorization.json')):
            reader=custody.N01S3Fence(fence.client,replace(fence.registration,prefix=prefix),max_attempts=4)
            try:
                inventory=reader.inventory('');require(len(inventory)==1 and inventory[0][0]==prefix+name)
                raw=reader.retained(*inventory[0],valid_until)
                require(c.digest(raw)==digest and reader.inventory('')==inventory);observed.append(raw)
            finally:fence.attempts+=reader.attempts
        value=c.decode(observed[0]);require(set(value)==source.FIELDS)
        require(value['process_nonce']==OLD_NONCE and value['artifact_inventory_sha256']==OLD_ARTIFACT
            and value['deployment_id']==OLD_ENV['VERCEL_DEPLOYMENT_ID'] and value['deployment_host']==OLD_ENV['VERCEL_URL'])
        selected=review.enrollment_pins(value);require(selected.generation==4)
        require(c.decode(observed[1])==dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode=r.MODE,authority_config_sha256=source.CONFIG,
            source_enrollment_sha256=OLD_SOURCE_SHA,checkpoint=HEAD3,previous_checkpoint=prior.HEAD4,
            authority_epoch=6,incarnation=body['incarnation'],application_generation=1,review_generation=4,
            expires_at_ms=selected.valid_until_ms,no_automatic_redispatch='REQUIRED',real_admission='NO'))
    except Exception:
        fence.quarantined=True;raise ValueError('N01_HISTORICAL_AUTH_FORWARD_QUARANTINE') from None


def scope():
    original=prior.scope()
    return replace(original,admin_checkpoint_ids=original.admin_checkpoint_ids+(HEAD3['id'],))


class HistoricalOwnerFence(membership.MembershipFence):
    def __init__(self,client):super().__init__(client,scope(),profile='PRODUCTION')
    def independent_recovery_authorization(self,body,ref,valid_until):
        if body['recovery_sequence']<=2:return custody.N01S3Fence.independent_recovery_authorization(self,body,ref,valid_until)
        return historical_authorization(self,body,ref,valid_until)


def prepare_forward_recovery(history,*,process_nonce,now_ms):
    from ash import g3_n01_owner_state as state
    from ash import g3_n01_owner_restart as first
    from ash import g3_n01_owner_sdk_restart as sdk
    require(type(history) is membership.CompleteMembership and history.head==HEAD4)
    c.old.check_type(process_nonce,'h')
    require(process_nonce[:32] not in (OLD_NONCE[:32],prior.OLD_NONCE[:32],sdk.OLD_NONCE[:32],first.OLD_NONCE[:32]))
    rows,root=state._advance(history,now_ms=now_ms)
    require(root['quarantine']=='OPEN' and root['authority_epoch']==6 and root['recovery_sequence']==11
        and root['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(all(row['family'] in ('root','revocation','recovery','binding','registration','source') for row in rows))
    require(state.current_binding_ids(rows)==(prior.BINDING_ID,prior.REGISTRATION_ID))
    sources=[row for row in rows if row['family']=='source'];require(len(sources)==4)
    current=[row for row in sources if row['state']=='CURRENT'];require(len(current)==1)
    require(current[0]['source_id']==prior.SOURCE_ID and current[0]['evidence_ref']['sha256']==OLD_SOURCE_SHA)
    registration=next(row for row in rows if row['family']=='registration' and row['state']=='CURRENT')
    require(registration['enforcement_sha256']==OLD_ARTIFACT)
    current[0].update(revision=current[0]['revision']+1,state='RETIRED')
    root.update(authority_epoch=EPOCH,incarnation='n01-owner-'+process_nonce[:32])
    return state._prepare(history,rows,objects={},group='T9',transition='RECOVER')
