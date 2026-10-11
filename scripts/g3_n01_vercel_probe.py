"""Read-only TEST_ONLY runtime federation qualification, never Owner authority.

Only the generated deployment URL is admitted; its existing native Vercel
authentication must be verified before the one explicitly budgeted invocation.
No provider login, source enrollment, write, retry, grant or dispatch occurs.
"""
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import threading
from ash import g3_checkpoint_custody as f
from ash import g3_control_codec as c
from ash.g3_primary_ledger import DelegatedDynamoReservations

DEADLINE=datetime(2026,10,13,10,51,37,tzinfo=timezone.utc)
A='arn:aws:iam::175880707430:role/NexusG3QualificationCaller'
R='arn:aws:iam::862902859484:role/NexusG3N01AppendRead'
TABLE='arn:aws:dynamodb:ap-southeast-1:175880707430:table/NexusG3AuthorityV1'
CONFIG='3632c49345ea111aa992b27a8645e44f479fe7685c98ac04515147891fd0a2d1'
GENESIS={'id':'nexus.g3.production.recovery-checkpoint.v2:ca736f0ab3d739456f41f6107f1582941c071835b6ca05c8f98e624b64e61f50',
         'body_sha256':'7fe0fb527ce2c8bb519a0f837124bfce22ce8e964008f2aa0fc7b4f1c9b036db'}
HEAD={'id':'nexus.g3.production.recovery-checkpoint.v2:2324a4475c42debe0a21e2b94cd42f1c3d68e9dc1af0397223dfdde4a4076281',
      'body_sha256':'52dd16d2303656eec0f3c6413e5337f03cb1e64531b7acf8ace920bcaf89ad41'}
REGISTRATION_SHA='95eb86f481e86adca195ec6f0cb646bd73afd058d238bb803bec459dd626f04f'
LOCK=threading.Lock()
OUTCOME=None


class ReadOnlyService:
    def __init__(self, client, kind, limit):
        self.client=client;self.kind=kind;self.limit=limit;self.attempts=0
        self.meta=client.meta
    def __getattr__(self, operation):
        def invoke(**kwargs):
            f.require(datetime.now(timezone.utc)<DEADLINE and self.attempts<self.limit)
            if self.kind=='DDB':
                f.require(operation=='get_item' and kwargs['TableName']==TABLE
                    and kwargs['Key']['pk']=={'S':'authority#'+f.INSTANCE})
            else:
                f.require(operation in ('list_object_versions','get_object','get_object_retention'))
                f.require(kwargs['Bucket']=='nexus-d03-custody-862902859484-ap-southeast-1-v1'
                    and kwargs['ExpectedBucketOwner']=='862902859484'
                    and kwargs.get('Key',kwargs.get('Prefix','')).startswith((f.NORMAL,f.APPROVALS)))
            self.attempts+=1
            return getattr(self.client,operation)(**kwargs)
        return invoke


def read_current(native_header):
    """Vercel-injected token passed only to native STS; no decoding/logging."""
    import boto3
    from botocore.config import Config
    from botocore import UNSIGNED
    cfg=Config(retries={'total_max_attempts':1},connect_timeout=5,read_timeout=10)
    unsigned=Config(signature_version=UNSIGNED,retries={'total_max_attempts':1},
                    connect_timeout=5,read_timeout=10)
    a=boto3.client('sts',region_name='us-east-1',config=unsigned).assume_role_with_web_identity(
        RoleArn=A,RoleSessionName='NexusG3N01Vercel',WebIdentityToken=native_header,DurationSeconds=900)
    def client(service, credentials):
        return boto3.client(service,region_name='ap-southeast-1',config=cfg,
            aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    sts=client('sts',a['Credentials']);identity=sts.get_caller_identity()
    f.require(identity['Account']=='175880707430' and identity['Arn']==
              'arn:aws:sts::175880707430:assumed-role/NexusG3QualificationCaller/NexusG3N01Vercel')
    ddb=ReadOnlyService(client('dynamodb',a['Credentials']),'DDB',2)
    recovery=sts.assume_role(RoleArn=R,RoleSessionName='NexusG3N01Custody',DurationSeconds=900)
    ident=client('sts',recovery['Credentials']).get_caller_identity()
    f.require(ident['Account']=='862902859484' and ident['Arn']==
              'arn:aws:sts::862902859484:assumed-role/NexusG3N01AppendRead/NexusG3N01Custody')
    s3=ReadOnlyService(client('s3',recovery['Credentials']),'S3',100)
    del a,recovery,identity,ident
    until=min(datetime.now(timezone.utc)+timedelta(minutes=10),DEADLINE)
    scope=f.Registration('nexus-d03-custody-862902859484-ap-southeast-1-v1','862902859484',
        f.NORMAL,f.INSTANCE,2,GENESIS['id'],GENESIS['body_sha256'],(GENESIS['id'],HEAD['id']),CONFIG)
    registration=f.N01S3Fence(s3,replace(scope,prefix=f.APPROVALS+'storage-registration-v2/'),max_attempts=100)
    inventory=registration.inventory('')
    f.require(len(inventory)==1 and inventory[0][0]==f.APPROVALS+'storage-registration-v2/registration.json')
    raw=registration.retained(*inventory[0],until)
    f.require(c.digest(raw)==REGISTRATION_SHA and registration.inventory('')==inventory)
    history=f.N01S3Fence(s3,scope,max_attempts=90).read(valid_until=until)
    f.require(history.head==HEAD)
    observation=DelegatedDynamoReservations(ddb,table_arn=TABLE,instance=f.INSTANCE,max_attempts=2)
    f.require(observation.quarantined)
    f.require(observation.observe_current(independent_checkpoint=history.checkpoints[-1]).authority=='NONE')
    return dict(n01_vercel_status='NATIVE_FUNCTION_OIDC_A_R_CURRENT_STORAGE_VERIFIED',
        head=history.head,generation=2,authority_epoch=2,incarnation='n01-storage-incarnation-2',
        ddb_attempts=ddb.attempts,s3_attempts=s3.attempts,owner_context='NOT_CREATED',
        registration_purpose='TEST_ONLY',automatic_redispatch='DENY',authority='NONE',real_admission='NO')


def request_allowed(path, method, headers, environment):
    host=environment.get('VERCEL_URL','')
    return (path=='/api/n01-storage' and method=='GET' and environment.get('VERCEL_ENV')=='production'
        and re.fullmatch(r'nexus-g3-qual-[a-z0-9]+-tdy0225\.vercel\.app',host) is not None
        and headers.get_all('Host')==[host] and headers.get_all('x-vercel-oidc-token') is not None
        and len(headers.get_all('x-vercel-oidc-token'))==1 and headers.get('Origin') is None
        and datetime.now(timezone.utc)<DEADLINE)


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # No headers, credential values, bearer or request dump in logs.
    def do_GET(self):
        global OUTCOME
        status=403;result=dict(n01_vercel_status='DENY',authority='NONE',real_admission='NO')
        if request_allowed(self.path,self.command,self.headers,os.environ):
            with LOCK:
                if OUTCOME is None:
                    # Unknown response is terminal in this process; no retry.
                    OUTCOME=dict(n01_vercel_status='QUARANTINE',authority='NONE',real_admission='NO')
                    try:OUTCOME=read_current(self.headers.get('x-vercel-oidc-token'))
                    except Exception:pass
                result=OUTCOME;status=200 if result['n01_vercel_status'].endswith('_VERIFIED') else 503
        raw=json.dumps(result,sort_keys=True).encode()
        # Exact sanitized response, not headers or native credential material.
        # Native browser may execute an API request without displaying its JSON.
        print(json.dumps({'n01_runtime_readback':result},sort_keys=True),flush=True)
        self.send_response(status)
        for key,value in {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',
            'Referrer-Policy':'no-referrer','X-Frame-Options':'DENY',
            'X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"}.items():
            self.send_header(key,value)
        self.end_headers();self.wfile.write(raw)
    do_POST=do_GET
    do_PUT=do_GET
    do_DELETE=do_GET
