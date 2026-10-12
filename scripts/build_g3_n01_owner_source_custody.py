"""Exact public-only source/recovery custody, restricted to existing N01 scope.

Native deployment/source readback must precede this builder. It cannot authorize
current Owner authentication, TASK/G1/G2 sources, a grant or production admission.
"""
import argparse
import hashlib
import json
from pathlib import Path
from ash import g3_delegated_control_codec as codec
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_public_review as review
from ash import g3_n01_owner_persistence as persistence
from ash import g3_n01_controller_bootstrap as boot
from ash import g3_checkpoint_custody as custody
from ash.g3_control_semantics import require
from scripts.build_g3_n01_public_review_custody import R_PROGRAM
from scripts import build_g3_n01_owner_controller as builder

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=r'''
def inventory():
 rows={}
 for prefix in PREFIXES:
  result=call('list_object_versions',Prefix=prefix,MaxKeys=16)
  need(result.get('IsTruncated') is False and not result.get('DeleteMarkers'))
  versions=result.get('Versions',[])
  need(all(r.get('IsLatest') is True and r.get('VersionId') not in ('',None,'null') for r in versions))
  need(len({r['Key'] for r in versions})==len(versions) and all(r['Key'] in PAYLOAD for r in versions))
  rows.update({r['Key']:r['VersionId'] for r in versions})
 return rows
'''


def build(observation,deployment,destination,*,now_ms,custody_revision=1,restart_profile=None):
    from ash import g3_n01_owner_restart as restart
    restart.require_profile(restart_profile)
    require(type(observation) is dict and set(observation)=={'status','source_proposal','source_sha256',
        'recovery_authorization','recovery_authorization_sha256','public_review','current_owner','authority','real_admission'})
    require(observation['status']=='SOURCE_PROPOSAL_READY_NONE' and observation['public_review']=='EXACT_RETAINED_REVIEW_VERIFIED'
        and observation['current_owner']=='NOT_AUTHENTICATED' and observation['authority']=='NONE' and observation['real_admission']=='NO')
    count=len(set((*builder.MODULES,*(name for name in builder.EXTRA if name!='scripts/g3_n01_controller_bootstrap.py'),*builder.OWNER_MODULES)))+6
    require(deployment['readyState']=='READY' and deployment['target']=='production' and deployment['projectId']==source.HOST_PROJECT
        and deployment['native_sso_protection']=='all_except_custom_domains' and deployment['source_identity_matches']==count)
    value=observation['source_proposal'];raw=codec.canonical(value)
    public=review.verify_review(codec.canonical(codec.decode((ROOT/'research/nexus-production-n01-pending-public-pin-review-v1.json').read_bytes().rstrip())),
        codec.canonical(codec.decode((ROOT/'research/nexus-production-n01-public-pin-owner-acceptance-v1.json').read_bytes().rstrip())),now_ms=now_ms)
    env=dict(VERCEL_ENV='production',VERCEL_PROJECT_ID=deployment['projectId'],VERCEL_DEPLOYMENT_ID=deployment['id'],VERCEL_URL=deployment['url'])
    enrolled=source.bind_source(raw,public,native_environment=env,artifact_inventory_sha256=value['artifact_inventory_sha256'],
        process_nonce=value['process_nonce'],now_ms=now_ms)
    require(enrolled.enrollment_sha256==observation['source_sha256'])
    authorization=observation['recovery_authorization'];protected=codec.canonical(authorization)
    require(codec.digest(protected)==observation['recovery_authorization_sha256'])
    require(set(authorization)=={'schema_version','purpose','authority_mode','authority_config_sha256',
        'source_enrollment_sha256','checkpoint','previous_checkpoint','authority_epoch','incarnation',
        'application_generation','review_generation','expires_at_ms','no_automatic_redispatch','real_admission'})
    require(authorization['schema_version']=='nexus.g3.n01.owner-recovery-authorization.v1'
        and authorization['purpose']=='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY' and authorization['authority_mode']=='DELEGATED_EXECUTOR'
        and authorization['authority_config_sha256']==source.CONFIG and authorization['source_enrollment_sha256']==enrolled.enrollment_sha256
        and authorization['previous_checkpoint']==(dict(id=boot.HEAD_ID,body_sha256='52dd16d2303656eec0f3c6413e5337f03cb1e64531b7acf8ace920bcaf89ad41') if restart_profile is None else restart.HEAD4)
        and authorization['authority_epoch']==(3 if restart_profile is None else 4) and authorization['incarnation']=='n01-owner-'+value['process_nonce'][:32]
        and authorization['application_generation']==authorization['review_generation']==1
        and authorization['expires_at_ms']==review.UNTIL_MS and authorization['no_automatic_redispatch']=='REQUIRED'
        and authorization['real_admission']=='NO')
    require(set(authorization['checkpoint'])=={'id','body_sha256'})
    codec.old.check_type(authorization['checkpoint']['body_sha256'],'h')
    require(authorization['checkpoint']['id'].startswith('nexus.g3.production.recovery-checkpoint.v2:'))
    codec.old.check_type(authorization['checkpoint']['id'].rsplit(':',1)[1],'h')
    require(type(custody_revision) is int and custody_revision in (1,2,3))
    prefixes=(source.PREFIX,persistence.RECOVERY_PREFIX+'00000000000000000003/') if custody_revision==1 else (
        custody.APPROVALS+f'current-source-controller-v{custody_revision}/',custody.APPROVALS+f'owner-controller-recovery-v{custody_revision}/00000000000000000003/')
    if restart_profile is not None:
        require(custody_revision==3 and value['process_nonce']!=restart.OLD_NONCE)
        prefixes=(restart.SOURCE_PREFIX,restart.RECOVERY_PREFIX+'00000000000000000005/')
    payload={prefixes[0]+'registration.json':raw.decode(),prefixes[1]+'authorization.json':protected.decode()}
    program=R_PROGRAM
    start=program.index('def inventory():');end=program.index('if receipt.exists():',start)
    program=program[:start]+INVENTORY+program[end:]
    program=program.replace('n01-public-review-r-receipt.json','n01-owner-source-r-receipt.json')
    if custody_revision!=1:program=program.replace('n01-owner-source-r-receipt.json',f'n01-owner-source-v{custody_revision}-r-receipt.json')
    if restart_profile is not None:program=program.replace(f'n01-owner-source-v{custody_revision}-r-receipt.json','n01-owner-source-restart-v1-r-receipt.json')
    program=program.replace('nexus.g3.n01.public-review-r-observation.v1','nexus.g3.n01.owner-source-r-observation.v1')
    program=program.replace('CONDITIONAL_PUBLIC_REVIEW_RETAIN','CONDITIONAL_OWNER_SOURCE_RETAIN')
    program=program.replace('PUBLIC_REVIEW_INDEPENDENTLY_RETAINED','OWNER_SOURCE_RECOVERY_INDEPENDENTLY_RETAINED')
    program=program.replace('N01_PUBLIC_REVIEW_R_QUARANTINE','N01_OWNER_SOURCE_R_QUARANTINE')
    setup='BUCKET='+repr(boot.storage_scope().bucket)+'\nOWNER='+repr('862902859484')+'\n'
    setup+='PREFIXES='+repr(prefixes)+'\nPAYLOAD='+repr(payload)+'\n'
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(setup+program,encoding='utf-8',newline='\n')
    return dict(script_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),new_objects=2,
        maximum_s3_attempts=16,maximum_public_bytes=len(raw)+len(protected),source_sha256=enrolled.enrollment_sha256,
        recovery_authorization_sha256=codec.digest(protected),retention='COMPLIANCE_7_DAYS',authority='NONE',real_admission='NO')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--observation',type=Path,required=True)
    parser.add_argument('--deployment',type=Path,required=True);parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--custody-revision',type=int,choices=(1,2,3),default=1)
    args=parser.parse_args();import time
    print(json.dumps(build(json.loads(args.observation.read_bytes()),json.loads(args.deployment.read_bytes()),
        args.destination,now_ms=int(time.time()*1000),custody_revision=args.custody_revision),sort_keys=True))
