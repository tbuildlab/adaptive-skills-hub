"""Finite PUBLIC postprocessor fixtures; no real pilot, authority or model run."""
from pathlib import Path
import copy,hashlib,json,sys,tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ash import g6_value_pilot as pilot,g6_retention_substitution as binding,g6_private_completion as task


def main():
    raw=b'PUBLIC FINITE FIXTURE\nSource records: '+json.dumps(binding.PUBLIC_ROWS).encode()+b'\n/no_think'
    results={}
    with patch.object(task,'rows',return_value=copy.deepcopy(binding.PUBLIC_ROWS)):
        for name,output in [('valid',binding.PUBLIC_EXPECTED),('wrong',binding.PUBLIC_EXPECTED.replace(b'KEEP',b'DROP')),
                            ('missing',binding.PUBLIC_EXPECTED[:-4]),('noise',b'PUBLIC NOISE'+binding.PUBLIC_EXPECTED)]:
            native=pilot.native_verified_report(raw,output);nexus=task.verified_report(output)
            results['equivalent_'+name]=native==nexus and ((native is not None)==(name=='valid'))
        for role in pilot.ROLES:
            with tempfile.TemporaryDirectory(prefix='g6-public-value-') as temporary:
                path=Path(temporary);(path/'input').mkdir();(path/'result').mkdir()
                (path/'input/task.txt').write_bytes(raw);(path/'result/stdout.bin').write_bytes(binding.PUBLIC_EXPECTED)
                state={'status':'DETERMINISTIC_RETENTION_RESULT_OBSERVED','retired':True,'job_active_after_termination':0,
                    'stdout_sha256':hashlib.sha256(binding.PUBLIC_EXPECTED).hexdigest(),'authenticated_payload_sha256':'a'*64}
                with patch.object(pilot,'native_plan',return_value={'input_sha256':hashlib.sha256(raw).hexdigest()}):
                    value=pilot._finish(role,path,state)
                interrupted=role.endswith('_interrupted')
                results[role]=value['status']==('INJECTED_FINALIZATION_INTERRUPTION' if interrupted else 'PILOT_RETENTION_ARTIFACT_VERIFIED') and value['retired'] is True and not value['automatic_retry'] and (path/'result/retention-index.csv').exists()!=interrupted
    record={'schema':'nexus.g6.retention-value-public-postprocessor.v1',
        'status':'PASS_PUBLIC_POSTPROCESSOR_ONLY' if all(results.values()) else 'HOLD',
        'results':results,'cases':len(results),'real_pilot_executions':0,'model_invocations':0,
        'qualification_scope':'Finite public fixtures with patched fixture input/profile/source rows; not signed-role execution or value evidence',
        'source_sha256':hashlib.sha256((ROOT/'ash/g6_value_pilot.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
        'real_admission':'NO'}
    directory=ROOT/'output/g6-retention-value-pilot-preparation-v1';directory.mkdir(exist_ok=True)
    with (directory/'public-postprocessor-v3.json').open('x',encoding='utf8') as out:json.dump(record,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps({k:record[k] for k in ('status','cases','real_pilot_executions','model_invocations','real_admission')},sort_keys=True))
    return 0 if all(results.values()) else 1


if __name__=='__main__':raise SystemExit(main())
