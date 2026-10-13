"""Exact head-8 forward retirement; expired review never enables this process."""
from dataclasses import replace
from ash import g3_n01_owner_sdk_restart as prior
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as c
from ash import g3_delegated_record_codec as r
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_membership_custody as membership
from ash.g3_control_semantics import require

PROFILE='OWNER_ATOMIC_FORWARD_V1'
SOURCE_PREFIX=custody.APPROVALS+'current-source-controller-atomic-v1/'
RECOVERY_PREFIX=custody.APPROVALS+'owner-controller-recovery-atomic-v1/'
HEAD4=dict(id=r.PREFIX+'recovery-checkpoint.v2:01e32a4befb0cbbac1fb820b237f6a7e7d2d43f3411c9bcf0b5ce6c48e4ad077',body_sha256='e2bec061b42ee10ac844109ba1347ff94a062a0a3b41c7509628ad05a05aff81')
HEAD3=dict(id=r.PREFIX+'recovery-checkpoint.v2:6248756d006366bb80df286a8d1357cd47389ef34eb993e9e469ee2e1530ded7',body_sha256='85ef46c4a8354e1a0b8e519198e8ba593a0c6da43301e01f62008ac0fb84a606')
OLD_NONCE='965ba01bdd3a8d75d02ccdf7af75fc0fba20450c4d639c5161451704e1e8221e'
OLD_SOURCE_SHA='ea112c5b12bac062417631dbc0a0b0d5ad0e41ff1a077a72f08db687fbd8ea10'
OLD_AUTH_SHA='936c3da44798c675a06ad05f161179ca62ba0a49a97d0ff5591e55d9e999c84b'
OLD_ARTIFACT='1deb80842aedc99558db94c74b699d2d0bf165f7d4ddf4c3fbc980d3d23a1dcf'
OLD_ENV=dict(VERCEL_DEPLOYMENT_ID='dpl_EufrmzcN5baE2c8k2APkXyfbjiVD',VERCEL_URL='nexus-g3-qual-mgad2vcg2-tdy0225.vercel.app')
BINDING_ID='n01-owner-binding-atomic-v1'
REGISTRATION_ID='n01-owner-only-source-atomic-v1'
SOURCE_ID='n01-owner-enrollment-atomic-v1'
EPOCH=6
SEQUENCE=9
GENERATION=4


def historical_authorization(fence,body,ref,valid_until):
    if body['recovery_sequence']<7:return prior.historical_authorization(fence,body,ref,valid_until)
    require(ref==HEAD3 and body['recovery_sequence']==7 and body['authority_epoch']==5
        and body['previous_checkpoint']==prior.HEAD4 and body['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(fence.max_attempts-fence.attempts>=8)
    observed=[]
    try:
        for prefix,digest,name in ((prior.SOURCE_PREFIX,OLD_SOURCE_SHA,'registration.json'),
            (prior.RECOVERY_PREFIX+'00000000000000000007/',OLD_AUTH_SHA,'authorization.json')):
            reader=custody.N01S3Fence(fence.client,replace(fence.registration,prefix=prefix),max_attempts=4)
            try:
                inventory=reader.inventory('');require(len(inventory)==1 and inventory[0][0]==prefix+name)
                raw=reader.retained(*inventory[0],valid_until)
                require(c.digest(raw)==digest and reader.inventory('')==inventory);observed.append(raw)
            finally:fence.attempts+=reader.attempts
        value=c.decode(observed[0]);require(set(value)==source.FIELDS)
        require(value['process_nonce']==OLD_NONCE and value['artifact_inventory_sha256']==OLD_ARTIFACT
            and value['deployment_id']==OLD_ENV['VERCEL_DEPLOYMENT_ID'] and value['deployment_host']==OLD_ENV['VERCEL_URL'])
        selected=review.enrollment_pins(value);require(selected.generation==2)
        require(c.decode(observed[1])==dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode=r.MODE,authority_config_sha256=source.CONFIG,
            source_enrollment_sha256=OLD_SOURCE_SHA,checkpoint=HEAD3,previous_checkpoint=prior.HEAD4,
            authority_epoch=5,incarnation=body['incarnation'],application_generation=1,review_generation=2,
            expires_at_ms=selected.valid_until_ms,no_automatic_redispatch='REQUIRED',real_admission='NO'))
    except Exception:
        fence.quarantined=True;raise ValueError('N01_HISTORICAL_ATOMIC_FORWARD_QUARANTINE') from None


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
    require(type(history) is membership.CompleteMembership and history.head==HEAD4)
    c.old.check_type(process_nonce,'h')
    require(process_nonce[:32] not in (OLD_NONCE[:32],prior.OLD_NONCE[:32],first.OLD_NONCE[:32]))
    rows,root=state._advance(history,now_ms=now_ms)
    require(root['quarantine']=='OPEN' and root['authority_epoch']==5 and root['recovery_sequence']==9
        and root['incarnation']=='n01-owner-'+OLD_NONCE[:32])
    require(all(row['family'] in ('root','revocation','recovery','binding','registration','source') for row in rows))
    require(state.current_binding_ids(rows)==(prior.BINDING_ID,prior.REGISTRATION_ID))
    sources=[row for row in rows if row['family']=='source'];require(len(sources)==3)
    current=[row for row in sources if row['state']=='CURRENT'];require(len(current)==1)
    require(current[0]['source_id']==prior.SOURCE_ID and current[0]['evidence_ref']['sha256']==OLD_SOURCE_SHA)
    registration=next(row for row in rows if row['family']=='registration' and row['state']=='CURRENT')
    require(registration['enforcement_sha256']==OLD_ARTIFACT)
    current[0].update(revision=current[0]['revision']+1,state='RETIRED')
    root.update(authority_epoch=EPOCH,incarnation='n01-owner-'+process_nonce[:32])
    return state._prepare(history,rows,objects={},group='T9',transition='RECOVER')
