"""Explicit prepared/current-custody recovery phases, TEST_ONLY / NONE.

The independent R admin write is not callable here. There is no automatic
RECOVER, retry, restore or dispatch; each phase is a distinct bounded request.
"""
from datetime import datetime,timedelta,timezone
from dataclasses import replace
import json,os,sys
from ash import g3_checkpoint_custody as f
from ash import g3_control_codec as c
from ash.g3_primary_ledger import DelegatedDynamoReservations
from scripts import g3_n01_storage_contract as v
from scripts import g3_n01_storage_live as live


def protected_registration(service,scope,expected,path,until):
    fence=f.N01S3Fence(service,replace(scope,prefix=f.APPROVALS+path+'/'))
    inventory=fence.inventory('')
    f.require(len(inventory)==1 and inventory[0][0]==f.APPROVALS+path+'/registration.json')
    f.require(fence.retained(*inventory[0],until)==c.canonical(expected))
    f.require(fence.inventory('')==inventory)


def main():
    request=json.loads((live.ROOT/'research/nexus-production-n01-recovery-run-request-v1.json').read_text())
    f.require(set(request)=={'schema_version','request_id','stage','reserved_ddb_attempts','real_admission'})
    f.require(request['schema_version']=='nexus.g3.n01.recovery-run-request.v1' and request['real_admission']=='NO')
    f.require((request['request_id'],request['stage'],request['reserved_ddb_attempts']) in
        (('n01-storage-recovery-prepare-1','prepare',64),('n01-storage-recovery-finalize-1','finalize',32)))
    ddb,s3=live.native_clients();ddb.limit=request['reserved_ddb_attempts'];s3.limit=250
    registration=json.loads((live.ROOT/'research/nexus-production-n01-storage-registration-v1.json').read_text())
    current,candidate,new_registration=v.recovery_inputs(registration)
    until=min(datetime.now(timezone.utc)+timedelta(hours=1),live.DEADLINE)
    scope=v.scope(registration)
    ledger=DelegatedDynamoReservations(ddb,table_arn=live.TABLE,instance=f.INSTANCE,max_attempts=64)
    if request['stage']=='prepare':
        protected_registration(s3,scope,registration,'storage-registration-v1',until)
        fence=f.N01S3Fence(s3,scope,max_attempts=240)
        history=fence.read(valid_until=until)
        f.require(history.checkpoints[-1]==current.checkpoint)
        ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
        result=ledger.prepare(candidate)
        f.require(result.authority=='NONE' and ledger.quarantined)
        existing=dict(fence.inventory('objects/'))
        for digest,raw in v.blobs(candidate.snapshot,candidate.descriptor).items():
            key=f.NORMAL+'objects/'+digest
            if key in existing:f.require(fence.retained(key,existing[key],until)==raw)
            else:fence.call('put_object',Key=key,Body=raw,IfNoneMatch='*',
                             ChecksumAlgorithm='SHA256',ContentType='application/json')
        outcome='REAL_PREPARED_AWAITING_INDEPENDENT_R_AUTHORIZATION'
    else:
        scope=v.scope(new_registration)
        protected_registration(s3,scope,new_registration,'storage-registration-v2',until)
        fence=f.N01S3Fence(s3,scope,max_attempts=240)
        history=fence.read(valid_until=until)
        f.require(history.checkpoints[-1]==candidate.checkpoint)
        result=ledger.finalize(candidate,independent_checkpoint=history.checkpoints[-1])
        f.require(result.authority=='NONE' and ledger.quarantined)
        reservation=ledger._get('reservation#'+f'{2:020d}')
        f.require(reservation['phase']=={'S':'FINALIZED'} and reservation['checkpoint']=={'B':candidate.checkpoint})
        old=f.N01S3Fence(s3,v.scope(registration),max_attempts=100)
        live.quarantined(lambda:old.read(valid_until=until))
        live.quarantined(lambda:ledger.observe_current(independent_checkpoint=current.checkpoint))
        fresh=DelegatedDynamoReservations(ddb,table_arn=live.TABLE,instance=f.INSTANCE,max_attempts=8)
        f.require(fresh.quarantined)
        f.require(fresh.observe_current(independent_checkpoint=history.checkpoints[-1]).authority=='NONE')
        root=next(c.decode(row.value) for row in live.cdecode(candidate.snapshot)
                  if c.decode(row.value)['family']=='root')
        f.require(root['authority_epoch']==2 and root['incarnation']=='n01-storage-incarnation-2'
                  and root['quarantine']=='CLOSED')
        outcome='REAL_RECOVERY_FINALIZED_NEW_EPOCH_INCARNATION_CLOSED'
    live.emit(dict(n01_recovery_status=outcome,stage=request['stage'],request_id=request['request_id'],
        head=f.reference(candidate.checkpoint),ddb_attempts=ddb.attempts,s3_attempts=s3.attempts,
        reserved_ddb_attempts=request['reserved_ddb_attempts'],authority='NONE',real_admission='NO',
        source_head=os.environ['GITHUB_SHA'],github_run_id=os.environ['GITHUB_RUN_ID'],
        owner_or_grant_restored=False,automatic_redispatch='DENY'))


if __name__=='__main__':
    try:main()
    except Exception:
        live.emit(dict(n01_recovery_status='QUARANTINE',authority='NONE',real_admission='NO',
                       attempts={service.kind:service.attempts for service in live.SERVICES}))
        sys.exit(1)
