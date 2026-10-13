"""Build one exact public-only R native SDK custody enrollment operation.

No credentials, contact data or authenticated provider responses are read.
Existing protected R login supplies native SDK authentication in CloudShell.
Only two conditional objects under the previously approved N01 prefix are written.
"""
from pathlib import Path
import argparse
import hashlib
import json

from ash import g3_delegated_control_codec as codec
from ash.g3_n01_public_review import PACKAGE_SHA, ACCEPTANCE_SHA, PREFIX, UNTIL_MS
from ash import g3_n01_public_review as review

ROOT=Path(__file__).resolve().parents[1]

R_PROGRAM=r'''
import hashlib,json
from datetime import datetime,timezone,timedelta
from pathlib import Path
import boto3
from botocore.config import Config
state={'schema_version':'nexus.g3.n01.public-review-r-observation.v1','stage':'PREFLIGHT',
 'status':'QUARANTINE','authority':'NONE','real_admission':'NO','s3_attempts':0,'versions':[]}
receipt=Path('n01-public-review-r-receipt.json')
def save():receipt.write_text(json.dumps(state,sort_keys=True)+'\n')
def need(ok):
 if not ok:raise ValueError('N01_PUBLIC_REVIEW_R_QUARANTINE')
def call(operation,**kwargs):
 need(1791762711502<=int(datetime.now(timezone.utc).timestamp()*1000)<1791791511502)
 need(state['s3_attempts']<16)
 state['s3_attempts']+=1;save()
 result=getattr(s3,operation)(Bucket=BUCKET,ExpectedBucketOwner=OWNER,**kwargs)
 need(result.get('ResponseMetadata',{}).get('HTTPStatusCode') in (200,204))
 return result
def inventory():
 result=call('list_object_versions',Prefix=PREFIX,MaxKeys=16)
 need(result.get('IsTruncated') is False and not result.get('DeleteMarkers'))
 rows=result.get('Versions',[])
 need(all(r.get('IsLatest') is True and r.get('VersionId') not in ('',None,'null') for r in rows))
 need(len({r['Key'] for r in rows})==len(rows) and all(r['Key'] in PAYLOAD for r in rows))
 return {r['Key']:r['VersionId'] for r in rows}
if receipt.exists():
 print(json.dumps({'status':'ALREADY_ATTEMPTED_NO_REDISPATCH','authority':'NONE','real_admission':'NO'}))
 raise SystemExit(2)
try:
 cfg=Config(retries={'total_max_attempts':1},connect_timeout=5,read_timeout=10)
 identity=boto3.client('sts',region_name='us-east-1',config=cfg).get_caller_identity()
 need(identity['Account']==OWNER and identity['Arn']=='arn:aws:iam::'+OWNER+':root')
 del identity
 s3=boto3.client('s3',region_name='ap-southeast-1',config=cfg)
 rows=inventory();state['stage']='CONDITIONAL_PUBLIC_REVIEW_RETAIN'
 for key,raw in sorted(PAYLOAD.items()):
  if key not in rows:
   result=call('put_object',Key=key,Body=raw.encode(),IfNoneMatch='*',
    ContentType='application/json',ChecksumAlgorithm='SHA256',ObjectLockMode='COMPLIANCE',
    ObjectLockRetainUntilDate=datetime.now(timezone.utc)+timedelta(days=7))
   need(result.get('VersionId') not in ('',None,'null'))
   rows[key]=result['VersionId']
  result=call('get_object',Key=key,VersionId=rows[key]);body=result['Body']
  try:data=body.read(8193)
  finally:body.close()
  need(result.get('VersionId')==rows[key] and data==raw.encode())
  retained=call('get_object_retention',Key=key,VersionId=rows[key])['Retention']
  need(retained['Mode']=='COMPLIANCE' and retained['RetainUntilDate'].tzinfo is not None
   and retained['RetainUntilDate']>=datetime.fromtimestamp(1791791511502/1000,timezone.utc))
  state['versions'].append({'key':key,'version_id':rows[key],'sha256':hashlib.sha256(data).hexdigest(),
   'bytes':len(data),'mode':'COMPLIANCE','retain_until_utc':retained['RetainUntilDate'].isoformat()})
 need(inventory()==rows and len(rows)==2)
 state.update(stage='COMPLETE',status='PUBLIC_REVIEW_INDEPENDENTLY_RETAINED')
except Exception:
 state.update(status='QUARANTINE')
finally:
 save();print(json.dumps(state,sort_keys=True))
'''


def build(destination,*,review_generation=1,restart_profile=None):
    selected=review.current_pins(review_generation,restart_profile=restart_profile)
    PACKAGE_SHA,ACCEPTANCE_SHA,PREFIX=selected.package_sha256,selected.acceptance_sha256,selected.prefix
    names=('nexus-production-n01-pending-public-pin-review-v1.json',
           'nexus-production-n01-public-pin-owner-acceptance-v1.json')
    if review_generation==2:names=('nexus-production-n01-pending-public-pin-review-sdk-repair-v2.json',
        'nexus-production-n01-public-pin-owner-acceptance-sdk-repair-v2.json')
    if review_generation==3:names=('nexus-production-n01-pending-public-pin-review-atomic-v3.json',
        'nexus-production-n01-public-pin-owner-acceptance-atomic-v3.json')
    if review_generation==4:names=('nexus-production-n01-pending-public-pin-review-atomic-v4.json',
        'nexus-production-n01-public-pin-owner-acceptance-atomic-v4.json')
    raws=tuple(codec.canonical(codec.decode((ROOT/'research'/name).read_bytes().rstrip(b'\n'))) for name in names)
    if tuple(map(codec.digest,raws))!=(PACKAGE_SHA,ACCEPTANCE_SHA):raise ValueError('PUBLIC_REVIEW_PACKAGE_CHANGED')
    payload={PREFIX+'proposal.json':raws[0].decode(),PREFIX+'acceptance.json':raws[1].decode()}
    setup='BUCKET='+repr('nexus-d03-custody-862902859484-ap-southeast-1-v1')+'\nOWNER='+repr('862902859484')+'\n'
    setup+='PREFIX='+repr(PREFIX)+'\nPAYLOAD='+repr(payload)+'\n'
    destination.parent.mkdir(parents=True,exist_ok=True)
    program=R_PROGRAM
    if review_generation>=2:
        program=program.replace('1791762711502',str(selected.valid_from_ms)).replace('1791791511502',str(selected.valid_until_ms))
        receipt='n01-public-review-atomic-v3-r-receipt.json' if review_generation==3 else 'n01-public-review-sdk-repair-v2-r-receipt.json'
        if review_generation==4:receipt='n01-public-review-atomic-v4-r-receipt.json'
        program=program.replace('n01-public-review-r-receipt.json',receipt)
    destination.write_text(setup+program,encoding='utf-8',newline='\n')
    return dict(script_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
        maximum_s3_attempts=16,new_objects=2,maximum_public_bytes=sum(map(len,raws)),
        qualification='PUBLIC_PIN_REVIEW_CUSTODY_ONLY',real_admission='NO')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destination',type=Path,required=True)
    print(json.dumps(build(parser.parse_args().destination),sort_keys=True))
