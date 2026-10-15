"""Four PUBLIC CSV-transport cases only; no candidate execution or model load."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ash import g6_native_binding as binding, g6_private_completion as private


def main():
    results = {}
    for case in sorted(binding.PRIVATE_PUBLIC_CASES):
        try:
            value = binding.public_attempt(case)
            passed = (value.get('status') == 'PUBLIC_FIXTURE_VERIFIED'
                      if case == 'retention_report' else
                      value.get('status') == 'QUARANTINE'
                      and value.get('reason') == 'UNVERIFIED_PRIVATE_RESULT')
            results[case] = {'passed': passed, 'disposition': value}
        except Exception:
            results[case] = {'passed': False, 'status': 'HOLD_PUBLIC_TRANSPORT'}
        print(json.dumps({'case': case, 'passed': results[case]['passed']}), flush=True)
    record = {'schema': 'nexus.g6.local-retention-public-qualification.v1',
              'status': 'PASS_PUBLIC_TRANSPORT_ONLY' if all(v['passed'] for v in results.values()) else 'HOLD',
              'results': results,
              'binding_sha256': binding.normalized_sha(ROOT / 'ash/g6_native_binding.py'),
              'private_binding_sha256': binding.normalized_sha(Path(private.__file__)),
              'candidate_executed': False, 'model_loaded': False,
              'private_input_processed': False, 'real_admission': 'NO'}
    with (ROOT / private.PUBLIC_WORK / 'qualification.json').open('x', encoding='utf-8') as target:
        json.dump(record, target, indent=2, sort_keys=True)
        target.write('\n')
    print(json.dumps({'status': record['status'], 'cases': len(results),
                      'pass': sum(v['passed'] for v in results.values())}))
    return 0 if record['status'] == 'PASS_PUBLIC_TRANSPORT_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())
