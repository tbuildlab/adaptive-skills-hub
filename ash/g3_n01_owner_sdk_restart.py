"""Exact SDK-repair forward retirement from head 6; no restored authority."""
from dataclasses import replace
from ash import g3_n01_owner_restart as prior
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as c
from ash import g3_delegated_record_codec as r
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_membership_custody as membership
from ash.g3_control_semantics import require

PROFILE='OWNER_SDK_REPAIR_FORWARD_V1'
SOURCE_PREFIX=custody.APPROVALS+'current-source-controller-sdk-repair-v1/'
RECOVERY_PREFIX=custody.APPROVALS+'owner-controller-recovery-sdk-repair-v1/'
HEAD4=dict(id=r.PREFIX+'recovery-checkpoint.v2:7d0f02227d3aece0d007685e805f0fd2c936ee777bc88e86aae50e8fbc994cc9',body_sha256='0492f25ce2c1b930ed5c4f5e9b2b0956716abb09b4cd90d7f84bb606097baabd')
HEAD3=dict(id=r.PREFIX+'recovery-checkpoint.v2:e41705595718ee3bdc71137b6736f6a49f0abdc303e8bf7cbf7a230eb821a650',body_sha256='138c264277fda62f78d15e308878ec566096dc36497819f5686f0706a9454ca3')
OLD_NONCE='62f7f9dde781cac085f0a369e9aeed2cade58205abce8005fcd060525e682b97'
OLD_SOURCE_SHA='e70f8e299e58f1c818f486f79505f7916bf21521bdaafba700ac8f21fdcc2641'
OLD_AUTH_SHA='20439af4506af3bd3ba593a7522c8c54afb44d6e864f2712299d04d0a195beb6'
OLD_ARTIFACT='e10084dedca1ad18b5fcea4d6a0414a4b8ebc3670e0013df251efd71c4eb0eb5'
OLD_ENV=dict(VERCEL_DEPLOYMENT_ID='dpl_95CToN5wALoGF64y1kh1xg9Jwf5j',VERCEL_URL='nexus-g3-qual-i7qbhdrqb-tdy0225.vercel.app')
BINDING_ID='n01-owner-binding-sdk-repair-v1'
REGISTRATION_ID='n01-owner-only-source-sdk-repair-v1'
SOURCE_ID='n01-owner-enrollment-sdk-repair-v1'
EPOCH=5
SEQUENCE=7
GENERATION=3


def historical_authorization(fence,body,ref,valid_until):
    if body['recovery_sequence']==3:return prior.historical_authorization(fence,body,ref,valid_until)
    require(ref==HEAD3 and body['recovery_sequence']==5 and body['authority_epoch']==4
        and body['previous_checkpoint']==prior.HEAD4 and body['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(fence.max_attempts-fence.attempts>=8)
    observed=[]
    try:
        for prefix,digest,name in ((prior.SOURCE_PREFIX,OLD_SOURCE_SHA,'registration.json'),
            (prior.RECOVERY_PREFIX+'00000000000000000005/',OLD_AUTH_SHA,'authorization.json')):
            reader=custody.N01S3Fence(fence.client,replace(fence.registration,prefix=prefix),max_attempts=4)
            try:
                inventory=reader.inventory('');require(len(inventory)==1 and inventory[0][0]==prefix+name)
                raw=reader.retained(*inventory[0],valid_until)
                require(c.digest(raw)==digest and reader.inventory('')==inventory);observed.append(raw)
            finally:fence.attempts+=reader.attempts
        value=c.decode(observed[0]);require(set(value)==source.FIELDS)
        require(value['process_nonce']==OLD_NONCE and value['artifact_inventory_sha256']==OLD_ARTIFACT
            and value['deployment_id']==OLD_ENV['VERCEL_DEPLOYMENT_ID'] and value['deployment_host']==OLD_ENV['VERCEL_URL'])
        require(c.decode(observed[1])==dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode=r.MODE,authority_config_sha256=source.CONFIG,
            source_enrollment_sha256=OLD_SOURCE_SHA,checkpoint=HEAD3,previous_checkpoint=prior.HEAD4,
            authority_epoch=4,incarnation=body['incarnation'],application_generation=1,review_generation=1,
            expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO'))
    except Exception:
        fence.quarantined=True;raise ValueError('N01_HISTORICAL_SDK_REPAIR_QUARANTINE') from None


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
    require(type(history) is membership.CompleteMembership and history.head==HEAD4)
    c.old.check_type(process_nonce,'h');require(process_nonce[:32] not in (OLD_NONCE[:32],prior.OLD_NONCE[:32]))
    rows,root=state._advance(history,now_ms=now_ms)
    require(root['quarantine']=='OPEN' and root['authority_epoch']==4 and root['recovery_sequence']==SEQUENCE
        and root['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(all(row['family'] in ('root','revocation','recovery','binding','registration','source') for row in rows))
    require(state.current_binding_ids(rows)==(prior.BINDING_ID,prior.REGISTRATION_ID))
    sources=[row for row in rows if row['family']=='source'];require(len(sources)==2)
    current=[row for row in sources if row['state']=='CURRENT'];require(len(current)==1)
    require(current[0]['source_id']==prior.SOURCE_ID and current[0]['evidence_ref']['sha256']==OLD_SOURCE_SHA)
    registration=next(row for row in rows if row['family']=='registration' and row['state']=='CURRENT')
    require(registration['enforcement_sha256']==OLD_ARTIFACT)
    current[0].update(revision=current[0]['revision']+1,state='RETIRED')
    root.update(authority_epoch=EPOCH,incarnation='n01-owner-'+process_nonce[:32])
    return state._prepare(history,rows,objects={},group='T9',transition='RECOVER')
