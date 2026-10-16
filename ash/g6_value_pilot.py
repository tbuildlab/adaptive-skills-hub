"""Six fixed retention pilot slots, not an executor, scheduler or value verdict.

The shared guard is experimental safety in BOTH arms; never score it as unique
Nexus value. Every slot needs its own fresh exact-subject Owner signature.
"""
from pathlib import Path
import hashlib
import json
import time

from . import g6_native_binding as guard, g6_retention_substitution as binding
from . import g6_private_completion as task, g3_grant_codec as codec
from .ecosystem_storage import stable_read_bytes

ROOT=Path(__file__).resolve().parents[1]
_LOADED_SHA=guard.normalized_sha(Path(__file__))
ROLES=('pilot_native_1','pilot_nexus_1','pilot_nexus_2','pilot_native_2',
       'pilot_native_interrupted','pilot_nexus_interrupted')
REVIEW='research/nexus-g6-retention-value-pilot-independent-review-v1.json'
DESIGN='research/nexus-g6-retention-value-pilot-design-v1.json'
BATCH='output/g6-retention-value-pilot-v1'
PACKETS='output/g6-retention-value-pilot-owner-signing-v1'
_ACTIVE_BATCH=False  # Process-local only; restart cannot restore a reserved batch.


def source_gate():
    guard.require(guard.normalized_sha(Path(__file__))==_LOADED_SHA,'LOADED_VALUE_PILOT_REVISION_CHANGED')
    guard.require(frozenset(ROLES)==guard.VALUE_PILOT_ROLES,'VALUE_PILOT_CLOSED_SLOTS')


def work(role):
    source_gate();guard.require(role in ROLES,'VALUE_PILOT_CLOSED_SLOT')
    return BATCH+'/'+role


def packet(role):
    source_gate();guard.require(role in ROLES,'VALUE_PILOT_CLOSED_SLOT')
    return PACKETS+'/'+role+'/decision.json'


def dispatch_gate(role):
    """Fixed order and batch retirement; never an authentication substitute."""
    guard.require(role in ROLES,'VALUE_PILOT_CLOSED_SLOT')
    batch=ROOT/BATCH
    guard.require(_ACTIVE_BATCH is True and batch.is_dir()
                  and not (batch/'pilot-result.json').exists(),'PILOT_BATCH_NOT_ACTIVE')
    reserved=json.loads(stable_read_bytes(batch/'batch-reservation.json',maximum_bytes=8192))
    guard.require(reserved=={'design_sha256':guard.normalized_sha(ROOT/DESIGN),
        'payloads':{r:hashlib.sha256(stable_read_bytes(ROOT/packet(r),maximum_bytes=65536)).hexdigest() for r in ROLES}},
        'PILOT_BATCH_BINDING')
    prior=ROLES[:ROLES.index(role)]
    guard.require({p.name for p in batch.iterdir() if p.is_dir()}==set(prior),'PILOT_ORDER_OR_REPLAY')
    for previous in prior:
        receipt=json.loads(stable_read_bytes(ROOT/work(previous)/'result/pilot-receipt.json',maximum_bytes=32768))
        expected='INJECTED_FINALIZATION_INTERRUPTION' if previous.endswith('_interrupted') else 'PILOT_RETENTION_ARTIFACT_VERIFIED'
        guard.require(receipt.get('slot')==previous and receipt.get('retired') is True
                      and receipt.get('status')==expected and receipt.get('automatic_retry') is False
                      and receipt.get('authenticated_payload_sha256')==reserved['payloads'][previous]
                      and receipt.get('job_active_after_termination')==0,'PILOT_PREDECESSOR_NOT_ACCEPTED')


def native_plan(role):
    directory=ROOT/work(role)
    plan=binding._plan(directory/'bin',directory/'input',directory/'result')
    plan.update(schema='nexus.g6.fixed-retention-value-pilot-plan.v1',
        pilot='FEASIBILITY_ONLY_NOT_PREREGISTERED_COMPARISON',
        pilot_slot=role,nexus_enabled=role.startswith('pilot_nexus'),
        controlled_finalization_interruption=role.endswith('_interrupted'),
        pilot_design_sha256=guard.normalized_sha(ROOT/DESIGN),
        packet=packet(role),batch=BATCH,release_authority='NONE')
    return plan


def owner_intent(role):
    source_gate()
    material=dict(binding.owner_intent()['material'])
    for name in ('ash/g6_value_pilot.py','tests/test_g6_value_pilot.py',
                 'scripts/qualify_g6_value_pilot.py',DESIGN,
                 'docs/nexus-g6-retention-value-pilot-design-v1.md'):
        material[name]=guard.normalized_sha(ROOT/name)
    config=native_plan(role)
    subject={'schema_version':codec.SUBJECT_SCHEMA,'kind':'local_adapter','provider':'repository',
        'source_ref':'repository-owned-g6-retention-value-pilot-v1','revision':'g6-retention-value-pilot-v1',
        'capability_id':'nexus/g6-value-'+role.replace('_','-'),'action':'execute',
        'content_sha256':hashlib.sha256(codec._canonical(material)).hexdigest(),
        'config_sha256':hashlib.sha256(codec._canonical(config)).hexdigest()}
    return {'schema':'nexus.g6.native-owner-qualification-decision.v1','subject':subject,
        'subject_id':codec.subject(subject).subject_id,'material':material,'config':config,
        'issuer':{'provider':'github','login':'TDY0225','user_id':223441940,'principal':'github-user-223441940'},
        'namespace':'nexus-g3-approval-v1','purpose':'APPROVE_ONE_G6_RETENTION_VALUE_PILOT_SLOT_V1',
        'max_attempts':1,'terminal':'RETIRE_ON_COMPLETION_FAILURE_CANCEL_OR_UNKNOWN',
        'automatic_retry':False,'capability_registration':False,'real_admission':'NO'}


def native_verified_report(raw_input,raw_output):
    """Native stdlib recipe; no Nexus verifier or golden answer lookup.

    Equivalent strict task instructions, source derivation and final readback
    must remain available in this arm. Do not manufacture an inferior baseline.
    """
    if len(raw_input)>16384 or len(raw_output)>65536:return None
    try:
        if raw_input.count(b'Source records: ')!=1 or raw_input.count(b'\n/no_think')!=1:return None
        encoded=raw_input.split(b'Source records: ',1)[1].split(b'\n/no_think',1)[0]
        rows=json.loads(encoded)
        if type(rows) is not list or len(rows)!=3:return None
        lines=['attempt,outcome,action,bytes'];seen=set()
        for row in rows:
            if type(row) is not dict or set(row)!={'attempt','status','retired','retained_bytes'}:return None
            name=row['attempt'];status=row['status'];size=row['retained_bytes']
            if (type(name) is not str or not name.isascii() or not name.isalnum() or not 1<=len(name)<=16
                or name in seen or row['retired'] is not True or type(size) is not int or not 0<=size<=65536
                or status not in ('QUARANTINE','NATIVE_BOUNDED_RESULT_OBSERVED')):return None
            seen.add(name)
            outcome='QUARANTINE' if status=='QUARANTINE' else 'PUBLIC_ONLY_PASS'
            lines.append(f'{name},{outcome},KEEP,{size}')
        expected=('\n'.join(lines)+'\n').encode('ascii')
        return expected if raw_output.replace(b'\r\n',b'\n').strip()==expected+b'END_G6_AUDIT' else None
    except (KeyError,TypeError,ValueError,UnicodeError):return None


def _finish(role,directory,state):
    """Same native Host file/hash/readback services in both arms.

    Only source-derived validation recipe differs. Shared safety and observer
    evidence is excluded from an eventual incremental-value score.
    """
    guard.require(role in ROLES,'VALUE_PILOT_CLOSED_SLOT')
    result=directory/'result'
    receipt={'schema':'nexus.g6.retention-value-pilot-slot.v1','slot':role,
        'nexus_enabled':role.startswith('pilot_nexus'),'status':'QUARANTINE',
        'retired':True,'automatic_retry':False,'model_invocations':0,'real_admission':'NO',
        'final_comparison_trial':False,'monetary_cost_microunits':None,
        'cost_scope':'No new paid/cloud/provider resource; local energy/hardware monetary cost UNMEASURED'}
    started=time.monotonic()
    try:
        guard.require(state.get('status')=='DETERMINISTIC_RETENTION_RESULT_OBSERVED'
                      and state.get('retired') is True and state.get('job_active_after_termination')==0,
                      'PILOT_RESULT_NOT_ACCEPTED')
        raw=stable_read_bytes(result/'stdout.bin',maximum_bytes=65536)
        guard.require(hashlib.sha256(raw).hexdigest()==state['stdout_sha256'],'PILOT_OUTPUT_CHANGED')
        raw_input=stable_read_bytes(directory/'input/task.txt',maximum_bytes=16384)
        guard.require(hashlib.sha256(raw_input).hexdigest()==native_plan(role)['input_sha256'],'PILOT_INPUT_CHANGED')
        report=task.verified_report(raw) if role.startswith('pilot_nexus') else native_verified_report(raw_input,raw)
        guard.require(report is not None,'PILOT_REPORT_PROTOCOL')
        if role.endswith('_interrupted'):
            # Equal deterministic fault in both arms, not a claim of OS crash.
            # Original output remains local. No report is committed or retried.
            receipt.update(status='INJECTED_FINALIZATION_INTERRUPTION',artifact_committed=False,
                interruption_stage='AFTER_VALIDATED_WORKER_OUTPUT_BEFORE_ARTIFACT',
                recovery_disposition='INSPECT_ORIGINAL_ONLY_NO_REDISPATCH')
        else:
            artifact=result/'retention-index.csv'
            with artifact.open('xb') as out:out.write(report)
            reopened=stable_read_bytes(artifact,maximum_bytes=4096)
            guard.require(reopened==report,'PILOT_REPORT_READBACK')
            receipt.update(status='PILOT_RETENTION_ARTIFACT_VERIFIED',artifact_committed=True,
                artifact_sha256=hashlib.sha256(reopened).hexdigest(),artifact_bytes=len(reopened),rows=3)
        receipt.update(input_sha256=hashlib.sha256(raw_input).hexdigest(),
            stdout_sha256=state['stdout_sha256'],source_files=task.native_plan()['source_files'],
            authenticated_payload_sha256=state['authenticated_payload_sha256'],
            guard_elapsed_seconds=state.get('elapsed_seconds'),
            user_cpu_100ns=state.get('user_cpu_100ns'),job_active_after_termination=0)
    except (OSError,ValueError):
        receipt.update(status='QUARANTINE',reason='PILOT_FINALIZATION_UNVERIFIED')
    receipt['finalization_elapsed_ns']=int((time.monotonic()-started)*1000000000)
    with (result/'pilot-receipt.json').open('x',encoding='utf8') as out:
        json.dump(receipt,out,sort_keys=True);out.write('\n')
    return receipt


def verification_only():
    """All six current signatures first; never reserve/dispatch from this call."""
    source_gate()
    guard.require(not (ROOT/BATCH).exists(),'PILOT_BATCH_ALREADY_RESERVED')
    return {role:guard._verify_native_owner(role)[0] for role in ROLES}


def run_once():
    """One finite prereviewed six-slot pilot, no retry/replan/fallback facility."""
    global _ACTIVE_BATCH
    source_gate();payloads=verification_only()
    batch=ROOT/BATCH;batch.mkdir(exist_ok=False)
    outcomes=[];stopped=False;failure=None;slot=None;stage='BATCH_RESERVATION'
    try:
        _ACTIVE_BATCH=True
        with (batch/'batch-reservation.json').open('x',encoding='utf8') as out:
            json.dump({'design_sha256':guard.normalized_sha(ROOT/DESIGN),'payloads':payloads},out,sort_keys=True);out.write('\n')
        for role in ROLES:
            if stopped:break
            slot=role;stage='GUARDED_DISPATCH'
            directory=ROOT/work(role)
            started=time.monotonic()
            state=guard._fixed_attempt(role,'qualification')
            stage='ARTIFACT_FINALIZATION'
            receipt=_finish(role,directory,state)
            receipt['end_to_end_elapsed_ns']=int((time.monotonic()-started)*1000000000)
            outcomes.append(receipt)
            expected='INJECTED_FINALIZATION_INTERRUPTION' if role.endswith('_interrupted') else 'PILOT_RETENTION_ARTIFACT_VERIFIED'
            stopped=receipt['status']!=expected
            if stopped:failure={'slot':role,'stage':stage,'outcome':receipt['status']}
    except Exception as error:
        stopped=True
        failure={'slot':slot,'stage':stage,'exception_class':type(error).__name__}
        raise
    finally:
        _ACTIVE_BATCH=False
        # Retire every unused slot without dispatch; a failed batch cannot later
        # be restarted with another still-valid signature from this same bundle.
        for role in ROLES:
            directory=ROOT/work(role)
            if not directory.exists():
                directory.mkdir()
                guard._write_state(directory,{'schema':'nexus.g6.fixed-native-attempt.v1',
                    'case':'qualification','status':'QUARANTINE','reason':'PILOT_NOT_DISPATCHED_BATCH_RETIRED',
                    'retired':True,'automatic_retry':False,'real_admission':'NO'})
        record={'schema':'nexus.g6.retention-value-pilot-result.v1','status':'PILOT_STOPPED' if stopped else 'PILOT_OBSERVATIONS_ONLY',
            'outcomes':outcomes,'failure':failure,'retired':True,'automatic_retry':False,'real_admission':'NO',
            'comparative_value':'NOT_ESTABLISHED_BY_THIS_RESULT','final_comparison_trial':False}
        with (batch/'pilot-result.json').open('x',encoding='utf8') as out:json.dump(record,out,sort_keys=True);out.write('\n')
    return record
