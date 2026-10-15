"""Finite PUBLIC no-model snapshot proof; never the source-bound real attempt."""
from pathlib import Path
import sys
import json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ash import g6_native_binding as guard, g6_retention_substitution as binding
from scripts.qualify_g6_native_binding import controller_failure

def main():
    results={}
    for case in sorted(binding.PUBLIC_CASES-{'deterministic_controller_failure'}):
        try:
            value=guard.public_attempt(case)
            passed=(value['status']=='PUBLIC_FIXTURE_VERIFIED' if case in ('deterministic_report','deterministic_io') else
                    value['status']=='QUARANTINE' and value.get('reason') not in ('BINDING_OR_HOST_FAILURE','RESERVED_NOT_COMPLETED'))
            if case=='deterministic_cancel':passed=passed and value.get('reason')=='CANCELLED' and value.get('public_tree_ready') is True
            if case=='deterministic_timeout':passed=passed and value.get('reason')=='TIMEOUT' and value.get('public_tree_ready') is True
            if case=='deterministic_invalid':passed=passed and value.get('returncode')==2
        except Exception as error:
            value={'status':'HOLD_PUBLIC_BINDING','exception_class':type(error).__name__};passed=False
        results[case]={'passed':bool(passed),'disposition':value}
        print(json.dumps({'case':case,'passed':bool(passed),'reason':value.get('reason')}),flush=True)
    value=controller_failure('deterministic_controller_failure')
    results['deterministic_controller_failure']={'passed':value['status']=='PASS_PUBLIC_CONTROLLER_FAILURE','result':value}
    record={'schema':'nexus.g6.deterministic-retention-public-qualification.v1',
            'status':'PASS_PUBLIC_DETERMINISTIC_COMPOSITION_ONLY' if all(v['passed'] for v in results.values()) else 'HOLD',
            'results':results,'binding_sha256':guard.normalized_sha(ROOT/'ash/g6_native_binding.py'),
            'substitution_sha256':guard.normalized_sha(Path(binding.__file__)),
            'runtime_pins_sha256':guard.normalized_sha(ROOT/binding.PINS),
            'actual_retention_workflow_executed':False,'model_loaded':False,'private_input_processed':False,
            'real_admission':'NO'}
    with (ROOT/binding.PUBLIC_WORK/'qualification.json').open('x',encoding='utf8') as out:
        json.dump(record,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps({'status':record['status'],'cases':len(results),'pass':sum(v['passed'] for v in results.values())}))
    return 0 if record['status']=='PASS_PUBLIC_DETERMINISTIC_COMPOSITION_ONLY' else 1

if __name__=='__main__':raise SystemExit(main())
