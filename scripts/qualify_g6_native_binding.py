"""One finite public suite for the fixed G6 binding; no native/model dispatch."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ash import g6_native_binding as binding


def controller_failure():
    # This is the only controller process this driver is allowed to terminate.
    command=[sys.executable,'-X','utf8','-c',
             "from ash.g6_native_binding import public_attempt; public_attempt('controller_failure')"]
    process=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    directory=ROOT/binding.WORK/'controller_failure'; handles=[]; record={}; stage='PUBLIC_READINESS'
    k=c.WinDLL(r'C:\Windows\System32\kernel32.dll',use_last_error=True)
    k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD]; k.OpenProcess.restype=w.HANDLE
    k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD]; k.WaitForSingleObject.restype=w.DWORD
    k.CloseHandle.argtypes=[w.HANDLE]; k.CloseHandle.restype=w.BOOL
    try:
        deadline=time.monotonic()+6
        while time.monotonic()<deadline:
            output=directory/'result/stdout.bin'
            if output.exists():
                with output.open('rb') as source: raw=source.read(257)
                try:
                    body=json.loads(raw)
                    pids=body['public_pids']
                    if len(pids)==2 and all(type(pid) is int and pid>0 for pid in pids): break
                except (ValueError,KeyError,TypeError): pass
            if process.poll() is not None: raise RuntimeError('CONTROLLER_DID_NOT_REACH_PUBLIC_CHILDREN')
            time.sleep(.05)
        else: raise RuntimeError('PUBLIC_CHILDREN_NOT_OBSERVED')
        for pid in pids:
            handle=k.OpenProcess(0x100000|0x1000,False,pid)
            if not handle: raise RuntimeError('PUBLIC_CHILD_HANDLE')
            handles.append(handle)
        before=[k.WaitForSingleObject(handle,0)==258 for handle in handles]
        stage='KILL_OWNED_CONTROLLER'
        process.terminate(); process.wait(timeout=3)
        after=[k.WaitForSingleObject(handle,3000)==0 for handle in handles]
        stage='RECONCILE_INTERRUPTED_ATTEMPT'
        disposition=binding.reconcile_public('controller_failure')
        record={'status':'PASS_PUBLIC_CONTROLLER_FAILURE' if all(before) and all(after) and disposition['status']=='QUARANTINE' else 'HOLD_CONTROLLER_FAILURE',
                'both_alive_before_controller_death':before,'both_signalled_after_controller_death':after,
                'disposition':disposition['status'],'automatic_retry':False}
    except Exception as error:
        record={'status':'HOLD_CONTROLLER_FAILURE','automatic_retry':False,'stage':stage,'error_class':type(error).__name__}
    finally:
        if process.poll() is None: process.terminate(); process.wait(timeout=3)
        for handle in handles: k.CloseHandle(handle)
    return record


def main():
    results={}
    expected_verified={'success','io','memory','processes','path_diagnostic'}
    cases=['success','io','overflow','stderr_overflow','nonzero','partial','timeout','cancel','cpu','memory','processes','late_output','path_diagnostic']
    for case in cases:
        try:
            result=binding.public_attempt(case)
            # A launch/setup failure is not evidence of a restriction working.
            passed=(result['status']=='PUBLIC_FIXTURE_VERIFIED' if case in expected_verified else
                    result['status']=='QUARANTINE' and result['reason'] not in ('BINDING_OR_HOST_FAILURE','RESERVED_NOT_COMPLETED'))
            if case=='timeout': passed=passed and result['reason']=='TIMEOUT' and result.get('public_tree_ready') is True
            if case=='cancel': passed=passed and result['reason']=='CANCELLED' and result.get('public_tree_ready') is True
            if case=='cpu': passed=passed and result['user_cpu_100ns']>=10000000 and result['returncode']!=0
            if case=='path_diagnostic':
                passed=passed and all(result.get('public_path_checks',{}).get(n) is True for n in binding.PUBLIC_PATH_CHECKS)
            if case=='late_output':
                raw=(ROOT/binding.WORK/case/'result/stdout.bin').read_bytes()
                observed=raw.startswith(b'{"status":"PUBLIC_FIXTURE_COMPLETE"}\n') and b'PUBLIC_LATE\n' in raw
                result['trailing_public_bytes_observed']=observed
                passed=passed and observed and result['reason'] in ('PARTIAL_RESULT','LATE_DESCENDANT')
            if case in ('overflow','stderr_overflow'): passed=passed and result['reason']=='OUTPUT_LIMIT' and result['retained_bytes']==binding.OUTPUT_LIMIT
            result['qualification_check_passed']=bool(passed)
        except Exception:
            result={'status':'HOLD_PUBLIC_SUITE','qualification_check_passed':False}
        results[case]=result
        print(json.dumps({'case':case,'passed':result['qualification_check_passed'],'reason':result.get('reason','HOLD')}),flush=True)
    results['controller_failure']=controller_failure()
    results['controller_failure']['qualification_check_passed']=results['controller_failure']['status']=='PASS_PUBLIC_CONTROLLER_FAILURE'
    replay_denied=False
    try: binding.public_attempt('success')
    except binding.BindingHold as error: replay_denied=str(error)=='ATTEMPT_RESERVED_NO_REPLAY'
    record={'schema':'nexus.g6.fixed-public-composition-qualification.v1',
            'status':'PASS_PUBLIC_COMPOSITION_ONLY' if all(r['qualification_check_passed'] for r in results.values()) and replay_denied else 'HOLD_PUBLIC_COMPOSITION',
            'results':results,'reserved_attempt_replay_denied':replay_denied,
            'binding_sha256':binding.normalized_sha(ROOT/'ash/g6_native_binding.py'),
            'fixture_sha256':binding.normalized_sha(binding.FIXTURE),
            'harness_sha256':binding.normalized_sha(Path(__file__)),
            'path_probe_source_sha256':binding.normalized_sha(binding.PUBLIC_PATH_SOURCE),
            'path_probe_binary_sha256':binding.PUBLIC_PATH_PROBE_SHA,
            'candidate_executed':False,'model_loaded':False,'private_input_processed':False,
            'signing_package_created':False,'real_admission':'NO'}
    target=ROOT/binding.WORK/'qualification.json'
    with target.open('x',encoding='utf-8') as out: json.dump(record,out,sort_keys=True,indent=2); out.write('\n')
    print(json.dumps({'status':record['status'],'cases':len(results),'passed':sum(r['qualification_check_passed'] for r in results.values()),'replay_denied':replay_denied}))
    return 0 if record['status']=='PASS_PUBLIC_COMPOSITION_ONLY' else 1


if __name__=='__main__': raise SystemExit(main())
