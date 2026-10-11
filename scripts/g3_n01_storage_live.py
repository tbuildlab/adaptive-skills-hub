"""One bounded real primary/custody storage run; TEST_ONLY and NONE.

Native GitHub federation, temporary credentials in SDK memory only. This script
does not fabricate production source/Owner evidence or dispatch an effect.
Unknown writes are reconciled read-only; the request's entire attempt reservation
is counted even if the job crashes. R enrollment is a separate protected context.
"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import json,os,re,sys,urllib.request
import subprocess
from dataclasses import replace
from ash import g3_checkpoint_custody as f
from ash import g3_control_codec as c
from ash.g3_primary_ledger import DelegatedDynamoReservations,LedgerError
from scripts import g3_n01_storage_contract as v

ROOT=Path(__file__).resolve().parents[1]
TABLE='arn:aws:dynamodb:ap-southeast-1:175880707430:table/NexusG3AuthorityV1'
A='arn:aws:iam::175880707430:role/NexusG3QualificationCaller'
R='arn:aws:iam::862902859484:role/NexusG3N01AppendRead'
DEADLINE=datetime(2026,10,13,10,51,37,tzinfo=timezone.utc)
PHASE='REQUEST_VALIDATION'
SERVICES=[]


def emit(value):print(json.dumps(value,sort_keys=True),flush=True)


def size(value):
    if isinstance(value,(str,bytes)):return len(value)+32
    if type(value) is dict:return 32+sum(size(k)+size(v) for k,v in value.items())
    if type(value) is list:return 32+sum(size(v) for v in value)
    return 32


class BoundedService:
    def __init__(self,sdk,kind,limit):
        self.sdk=sdk;self.kind=kind;self.limit=limit;self.attempts=0
        self.responses=[];self.drop_operation=None;self.payload_bytes=0
        self.meta=sdk.meta;SERVICES.append(self)
    def __getattr__(self,operation):
        def call(**kw):
            f.require(datetime.now(timezone.utc)<DEADLINE and self.attempts<self.limit)
            if self.kind=='DDB':
                f.require(operation in ('get_item','put_item','transact_write_items','update_item'))
                if operation=='transact_write_items':
                    f.require(len(kw['TransactItems'])<=2)
                    for item in kw['TransactItems']:
                        f.require(next(iter(item.values()))['TableName']==TABLE and size(item)<=400*1024)
                    self.payload_bytes+=size(kw['TransactItems'])
                else:
                    f.require(kw.get('TableName')==TABLE)
                    if operation=='put_item':
                        f.require(size(kw['Item'])<=400*1024);self.payload_bytes+=size(kw['Item'])
            else:
                f.require(kw.get('Bucket')=='nexus-d03-custody-862902859484-ap-southeast-1-v1')
                f.require(kw.get('ExpectedBucketOwner')=='862902859484')
                key=kw.get('Key',kw.get('Prefix',''))
                f.require(key.startswith((f.NORMAL,f.APPROVALS,'qualification/n01/v1/faults/')))
                if operation=='put_object':
                    f.require(type(kw['Body']) is bytes and len(kw['Body'])<=65536)
                    self.payload_bytes+=len(kw['Body'])
            f.require(self.payload_bytes<=64*1024*1024)
            self.attempts+=1
            try:result=getattr(self.sdk,operation)(**kw)
            except Exception as error:
                response=getattr(error,'response',{});code=response.get('Error',{}).get('Code','UNAVAILABLE')
                if type(code) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,64}',code):code='UNCLASSIFIED'
                status=response.get('ResponseMetadata',{}).get('HTTPStatusCode')
                self.responses.append((operation,status,code))
                emit(dict(service=self.kind,operation=operation,attempt=self.attempts,http_status=status,error_code=code))
                raise ValueError('N01_STORAGE_QUARANTINE') from None
            meta=result.get('ResponseMetadata',{});status=meta.get('HTTPStatusCode')
            self.responses.append((operation,status,None))
            emit(dict(service=self.kind,operation=operation,attempt=self.attempts,
                      http_status=status,request_id=meta.get('RequestId')))
            if operation==self.drop_operation:
                self.drop_operation=None
                raise ValueError('N01_INJECTED_ACK_LOSS_AFTER_REAL_COMMIT')
            return result
        return call


def native_clients(*,read_only=False):
    global PHASE
    import boto3
    from botocore.config import Config
    from botocore import UNSIGNED
    f.require(os.environ.get('GITHUB_REPOSITORY')=='TDY0225/adaptive-skills-hub')
    f.require(os.environ.get('GITHUB_REF')=='refs/heads/nexus-v2-production-qualification')
    f.require(os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_RUN_ATTEMPT')=='1')
    f.require(datetime.now(timezone.utc)<DEADLINE)
    url=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']
    f.require(url.startswith('https://'))
    request=urllib.request.Request(url+('&' if '?' in url else '?')+'audience=sts.amazonaws.com',
        headers={'Authorization':'Bearer '+os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})
    PHASE='NATIVE_GITHUB_OIDC'
    with urllib.request.urlopen(request,timeout=20) as response:token=json.load(response)['value']
    config=Config(retries={'total_max_attempts':1},connect_timeout=10,read_timeout=20)
    unsigned=Config(signature_version=UNSIGNED,retries={'total_max_attempts':1},connect_timeout=10,read_timeout=20)
    PHASE='A_ASSUME_WEB_IDENTITY'
    a=boto3.client('sts',region_name='us-east-1',config=unsigned).assume_role_with_web_identity(
        RoleArn=A,RoleSessionName='NexusG3N01GitHub',WebIdentityToken=token,DurationSeconds=900)
    del token,request
    def client(service,credentials):
        return boto3.client(service,region_name='ap-southeast-1',config=config,
            aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    sts=client('sts',a['Credentials']);identity=sts.get_caller_identity()
    f.require(identity['Account']=='175880707430' and identity['Arn']==
        'arn:aws:sts::175880707430:assumed-role/NexusG3QualificationCaller/NexusG3N01GitHub')
    ddb=client('dynamodb',a['Credentials']);PHASE='R_ASSUME_CUSTODY'
    r=sts.assume_role(RoleArn=R,RoleSessionName='NexusG3N01Custody',DurationSeconds=900)
    identity=client('sts',r['Credentials']).get_caller_identity()
    f.require(identity['Account']=='862902859484' and identity['Arn']==
        'arn:aws:sts::862902859484:assumed-role/NexusG3N01AppendRead/NexusG3N01Custody')
    s3=client('s3',r['Credentials']);del a,r
    emit(dict(native_github_oidc_a_to_r='VERIFIED',authority='NONE'))
    return BoundedService(ddb,'DDB',20 if read_only else 108),BoundedService(s3,'S3',250 if read_only else 650)


def restart_read_only():
    """A fresh OS process/native federation; no primary/custody write path."""
    global PHASE
    ddb,s3=native_clients(read_only=True)
    registration=json.loads((ROOT/'research/nexus-production-n01-storage-registration-v1.json').read_text())
    until=min(datetime.now(timezone.utc)+timedelta(hours=1),DEADLINE)
    fence=f.N01S3Fence(s3,v.scope(registration),max_attempts=240)
    PHASE='READ_ONLY_RESTART_CURRENT_CUSTODY'
    history=fence.read(valid_until=until)
    f.require(c.decode(history.checkpoints[-1])['recovery_sequence']==1)
    ledger=DelegatedDynamoReservations(ddb,table_arn=TABLE,instance=f.INSTANCE,max_attempts=20)
    f.require(ledger.quarantined)
    observed=ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
    from ash.g3_delegated_control_codec import EncodedSnapshot
    snapshot=EncodedSnapshot(history.controls[-1],history.pages[-1])
    f.require(c.decode(next(row.value for row in cdecode(snapshot) if c.decode(row.value)['family']=='root'))['quarantine']=='CLOSED')
    f.require(observed.authority=='NONE')
    emit(dict(restart_process='REAL_FRESH_PROCESS_READ_ONLY',pid=os.getpid(),
        ddb_attempts=ddb.attempts,s3_attempts=s3.attempts,authority='NONE',real_admission='NO'))


def cdecode(snapshot):
    from ash.g3_delegated_control_codec import verify_snapshot
    return verify_snapshot(snapshot)


def quarantined(action):
    try:action()
    except (ValueError,TypeError):return
    raise ValueError('N01_STORAGE_UNEXPECTED_ACCEPTANCE')


def main():
    global PHASE
    request=json.loads((ROOT/'research/nexus-production-n01-storage-run-request-v1.json').read_text())
    f.require(request==dict(schema_version='nexus.g3.n01.storage-run-request.v1',
        request_id='n01-storage-append-1',stage='append',reserved_ddb_attempts=128,
        aggregate_ddb_ceiling=512,real_admission='NO'))
    ddb,s3=native_clients()
    registration=json.loads((ROOT/'research/nexus-production-n01-storage-registration-v1.json').read_text())
    before,genesis,descriptor,candidate,actual=v.inputs(registration['config_sha256'],registration['base_time_ms'])
    f.require(registration==actual)
    scope=v.scope(registration);until=min(datetime.now(timezone.utc)+timedelta(hours=1),DEADLINE)
    PHASE='INDEPENDENT_STORAGE_REGISTRATION'
    protected=f.N01S3Fence(s3,replace(scope,prefix=f.APPROVALS+'storage-registration-v1/'))
    inventory=protected.inventory('');f.require(len(inventory)==1)
    f.require(inventory[0][0]==f.APPROVALS+'storage-registration-v1/registration.json')
    f.require(protected.retained(*inventory[0],until)==c.canonical(registration))
    f.require(protected.inventory('')==inventory)
    fence=f.N01S3Fence(s3,scope,max_attempts=850)
    history=fence.read(valid_until=until);f.require(history.checkpoints==(genesis,))
    outcomes={}
    def service_refusal(label,action,status,code,service):
        count=len(service.responses);quarantined(action)
        f.require(len(service.responses)==count+1 and service.responses[-1][1:]==(status,code))
        outcomes[label]=f'REAL_SERVICE_{status}_{code}'
    PHASE='EXACT_PRIMARY_SCOPE'
    service_refusal('wrong_partition',lambda:ddb.get_item(TableName=TABLE,ConsistentRead=True,
        Key={'pk':{'S':'authority#wrong-instance'},'sk':{'S':'HEAD'}}),400,'AccessDeniedException',ddb)
    service_refusal('ordinary_update',lambda:ddb.update_item(TableName=TABLE,
        Key={'pk':{'S':'authority#'+f.INSTANCE},'sk':{'S':'HEAD'}},
        UpdateExpression='SET #p = :p',ExpressionAttributeNames={'#p':'phase'},
        ExpressionAttributeValues={':p':{'S':'READY'}}),400,'AccessDeniedException',ddb)
    PHASE='PRIMARY_GENESIS_ENROLLMENT'
    ledger=DelegatedDynamoReservations(ddb,table_arn=TABLE,instance=f.INSTANCE,max_attempts=120)
    result=ledger.enroll_genesis(genesis,before.snapshot)
    f.require(result.authority=='NONE' and ledger.quarantined)
    ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
    service_refusal('duplicate_head_put',lambda:ddb.put_item(TableName=TABLE,
        Item=dict(ledger._key('HEAD'),phase={'S':'READY'},checkpoint={'B':genesis},sequence={'N':'0'}),
        ConditionExpression='attribute_not_exists(pk)'),400,'ConditionalCheckFailedException',ddb)
    PHASE='REAL_PREPARE_WITH_INJECTED_ACK_LOSS'
    ddb.drop_operation='transact_write_items';quarantined(lambda:ledger.prepare(candidate))
    f.require(ledger.quarantined and ddb.drop_operation is None)
    quarantined(lambda:ledger.observe_current(independent_checkpoint=genesis))
    outcomes['prepare_ack_loss']='REAL_COMMIT_INJECTED_ACK_LOSS_QUARANTINE_NO_RETRY'
    PHASE='EXACT_RETAINED_CANDIDATE'
    existing=dict(fence.inventory('objects/'))
    for digest,raw in v.blobs(candidate.snapshot,candidate.descriptor).items():
        key=f.NORMAL+'objects/'+digest
        if key in existing:
            f.require(fence.retained(key,existing[key],until)==raw)
        else:fence.call('put_object',Key=key,Body=raw,IfNoneMatch='*',ContentType='application/json',ChecksumAlgorithm='SHA256')
    PHASE='REAL_S3_APPEND_WITH_INJECTED_ACK_LOSS'
    s3.drop_operation='put_object'
    quarantined(lambda:fence.append(candidate.checkpoint,history.head,valid_until=until))
    f.require(fence.pending==candidate.checkpoint and s3.drop_operation is None)
    quarantined(lambda:fence.append(candidate.checkpoint,history.head,valid_until=until))
    current=fence.reconcile(valid_until=until);f.require(current.checkpoints[-1]==candidate.checkpoint)
    outcomes['append_ack_loss']='REAL_COMMIT_INJECTED_ACK_LOSS_READ_ONLY_RECONCILIATION'
    PHASE='REAL_FINALIZE_WITH_INJECTED_ACK_LOSS'
    ddb.drop_operation='transact_write_items'
    quarantined(lambda:ledger.finalize(candidate,independent_checkpoint=current.checkpoints[-1]))
    f.require(ledger.quarantined and ddb.drop_operation is None)
    outcomes['finalize_ack_loss']='REAL_COMMIT_INJECTED_ACK_LOSS_QUARANTINE_NO_RETRY'
    restarted=DelegatedDynamoReservations(ddb,table_arn=TABLE,instance=f.INSTANCE,max_attempts=20)
    f.require(restarted.quarantined)
    quarantined(lambda:restarted.observe_current(independent_checkpoint=genesis))
    fresh=f.N01S3Fence(s3,scope).read(valid_until=until)
    result=restarted.observe_current(independent_checkpoint=fresh.checkpoints[-1])
    f.require(result.authority=='NONE')
    # Pure transport equality cannot restore bearer authority. Closed semantic
    # root and TEST_ONLY registration still deny every production operation.
    f.require(all(c.decode(row.value).get('quarantine','CLOSED')=='CLOSED' for row in before.rows))
    outcomes['restart']='REAL_FRESH_INDEPENDENT_READ_TRANSPORT_ONLY_AUTHORITY_NONE'
    PHASE='STALE_TRANSACTION_SERVICE_REFUSAL'
    wrong='reservation#stale-check'
    service_refusal('stale_transaction',lambda:ddb.transact_write_items(TransactItems=[
        {'Put':{'TableName':TABLE,'Item':dict(ledger._key(wrong),body={'S':'non-authorizing-probe'}),
                'ConditionExpression':'attribute_not_exists(pk)'}},
        {'Update':{'TableName':TABLE,'Key':ledger._key('HEAD'),
            'UpdateExpression':'SET #p = :p','ConditionExpression':'checkpoint = :old',
            'ExpressionAttributeNames':{'#p':'phase'},
            'ExpressionAttributeValues':{':p':{'S':'READY'},':old':{'B':genesis}}}}
    ]),400,'TransactionCanceledException',ddb)
    f.require(ddb.get_item(TableName=TABLE,Key=ledger._key(wrong),ConsistentRead=True).get('Item') is None)
    outcomes['failed_transaction_atomicity']='REAL_CONDITION_FAILURE_NO_PARTIAL_PUT'
    service_refusal('duplicate_journal',lambda:s3.put_object(Bucket=scope.bucket,ExpectedBucketOwner=scope.owner,
        Key=f.NORMAL+f'journal/{1:020d}',Body=candidate.checkpoint,IfNoneMatch='*',
        ContentType='application/json'),412,'PreconditionFailed',s3)
    service_refusal('approval_mutation',lambda:s3.put_object(Bucket=scope.bucket,ExpectedBucketOwner=scope.owner,
        Key=f.APPROVALS+'storage-registration-v1/registration.json',Body=c.canonical(registration),
        IfNoneMatch='*',ContentType='application/json'),403,'AccessDenied',s3)
    PHASE='REAL_FRESH_PROCESS_RESTART'
    restarted_process=subprocess.run([sys.executable,'-m','scripts.g3_n01_storage_live','--read-only-restart'],
                                     cwd=ROOT,timeout=180)
    f.require(restarted_process.returncode==0)
    outcomes['fresh_process_restart']='REAL_READ_ONLY_PROCESS_NO_AUTHORITY_RESTORATION'
    emit(dict(n01_storage_status='QUALIFIED_STORAGE_ONLY_NOT_PRODUCTION_AUTHORITY',
        request_id=request['request_id'],github_run_id=os.environ['GITHUB_RUN_ID'],source_head=os.environ['GITHUB_SHA'],
        ddb_parent_attempts=ddb.attempts,ddb_reserved_attempts=128,s3_parent_attempts=s3.attempts,
        ddb_payload_upper_bound_bytes=ddb.payload_bytes,s3_written_payload_bytes=s3.payload_bytes,
        head=fresh.head,sequence=1,outcomes=outcomes,authority='NONE',real_admission='NO',
        evidence_classes=['REAL_AWS_SERVICE_RESPONSES','INJECTED_TRANSPORT_ACK_LOSS','NON_AUTHORITATIVE_STORAGE_INPUTS'],
        owner_confirmation='NOT_PERFORMED',production_g3_e2e='NOT_PERFORMED',automatic_redispatch='DENY'))


if __name__=='__main__':
    try:
        if sys.argv[1:]==['--read-only-restart']:restart_read_only()
        else:
            f.require(sys.argv[1:]==[]);main()
    except Exception:
        emit(dict(n01_storage_status='QUARANTINE',phase=PHASE,authority='NONE',real_admission='NO',
            attempts={s.kind:s.attempts for s in SERVICES},ddb_reserved_attempts=128))
        sys.exit(1)
