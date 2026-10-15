"""One fixed no-model substitution task; existing Host/boundary, not a runtime."""
from pathlib import Path
import hashlib
import json

from . import g6_native_binding as guard, g6_private_completion as task, g3_grant_codec as codec
from .ecosystem_storage import stable_read_bytes
from .core_capabilities import safe_path

ROOT = Path(__file__).resolve().parents[1]
_LOADED_SHA = guard.normalized_sha(Path(__file__))
WORK = 'output/g6-retention-deterministic-once-v1'
PUBLIC_WORK = 'output/g6-retention-deterministic-public-v5'
PACKET = 'output/g6-retention-deterministic-owner-signing-v1/decision.json'
REVIEW = 'research/nexus-g6-retention-deterministic-independent-review-v1.json'
PINS = 'research/nexus-g6-deterministic-host-runtime-pins-v1.json'
WORKER = 'research/nexus-g6-retention-deterministic-worker-v1.py'
PROBE = 'research/nexus-g6-retention-deterministic-public-probe-v1.py'
RUNTIME = ROOT / 'output/g6-deterministic-host-runtime-v1'
PUBLIC_CASES = frozenset({'deterministic_report', 'deterministic_invalid', 'deterministic_io',
                          'deterministic_cancel', 'deterministic_timeout', 'deterministic_controller_failure'})
PUBLIC_ROWS = [dict(attempt='sampleA', status='QUARANTINE', retired=True, retained_bytes=17),
               dict(attempt='sampleB', status='NATIVE_BOUNDED_RESULT_OBSERVED', retired=True, retained_bytes=29),
               dict(attempt='sampleC', status='QUARANTINE', retired=True, retained_bytes=0)]
PUBLIC_EXPECTED = b'attempt,outcome,action,bytes\nsampleA,QUARANTINE,KEEP,17\nsampleB,PUBLIC_ONLY_PASS,KEEP,29\nsampleC,QUARANTINE,KEEP,0\nEND_G6_AUDIT\n'
_PINS_SHA = guard.normalized_sha(ROOT / PINS)
_WORKER_SHA = guard.normalized_sha(ROOT / WORKER)
_PROBE_SHA = guard.normalized_sha(ROOT / PROBE)


def source_gate():
    guard.require(guard.normalized_sha(Path(__file__)) == _LOADED_SHA, 'LOADED_DETERMINISTIC_REVISION_CHANGED')


def runtime_pins():
    source_gate()
    raw = stable_read_bytes(ROOT / PINS, maximum_bytes=65536)
    guard.require(hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == _PINS_SHA, 'DETERMINISTIC_PINS_CHANGED')
    value = codec.parse_input(raw)
    guard.require(value['snapshot'] == RUNTIME.relative_to(ROOT).as_posix()
                  and len(value['files']) == 54, 'DETERMINISTIC_RUNTIME_INVENTORY')
    seen = set()
    for pin in value['files']:
        relative = pin['relative_path']
        guard.require(type(relative) is str and relative not in seen and '\\' not in relative,
                      'DETERMINISTIC_RUNTIME_PIN')
        safe_path(RUNTIME, relative)
        guard.require(type(pin['bytes']) is int and 0 < pin['bytes'] <= 33554432
                      and type(pin['sha256']) is str and len(pin['sha256']) == 64
                      and set(pin['sha256']) <= set('0123456789abcdef'), 'DETERMINISTIC_RUNTIME_PIN')
        seen.add(relative)
    return value['files']


def verify_runtime_inventory():
    pins = runtime_pins()
    paths = list(RUNTIME.rglob('*'))
    for path in paths:
        guard.storage._verify_path_chain_no_links(path)
    actual = {f.relative_to(RUNTIME).as_posix() for f in paths if f.is_file()}
    guard.require(actual == {p['relative_path'] for p in pins}, 'DETERMINISTIC_RUNTIME_INVENTORY')
    expected_directories = {parent.as_posix() for p in pins for parent in Path(p['relative_path']).parents if parent != Path('.')}
    guard.require({f.relative_to(RUNTIME).as_posix() for f in paths if f.is_dir()} == expected_directories,
                  'DETERMINISTIC_RUNTIME_INVENTORY')
    return pins


def _plan(binary, data, result):
    inherited = guard.native_plan()
    pins = runtime_pins()
    return {'schema': 'nexus.g6.fixed-deterministic-retention-plan.v1',
            'mode': 'FRESH_OWNER_SIGNATURE_REQUIRED_DETERMINISTIC_ONLY',
            'executable': str(RUNTIME / 'python.exe'), 'cwd': str(binary),
            'candidate_arguments': ['-I', '-S', '-B', str(binary / 'retention.py'), '../input/task.txt'],
            'input': str(data / 'task.txt'), 'input_sha256': hashlib.sha256(task.prompt()).hexdigest(),
            'input_classification': 'PUBLIC_PROJECT_EVIDENCE_WITH_LOCAL_ONLY_ROUTING',
            'source_files': task.native_plan()['source_files'], 'model_ref': None,
            'worker_sha256': guard.normalized_sha(ROOT / WORKER),
            'runtime_pins_sha256': guard.normalized_sha(ROOT / PINS), 'runtime_files': pins,
            'filesystem': {':root': 'deny', 'C:/Windows/System32': 'read', RUNTIME.as_posix(): 'read',
                           binary.as_posix(): 'read', (data / 'task.txt').as_posix(): 'read'},
            'environment_names': list(guard.ENV_NAMES), 'telemetry_overrides': list(guard.TELEMETRY),
            'host_material': inherited['host_material'], 'limits': inherited['limits'],
            'network': False, 'max_attempts': 1, 'automatic_retry': False,
            'output': 'local-bounded-stdout-stderr-pipes-only', 'result_directory': str(result),
            'declared_restrictions': ['no-frontier-model', 'local-only-inference-if-any', 'no-agents', 'no-remote-mcp'],
            'local_model_only_interpretation': 'No inference may leave local boundary. This separate explicitly signed configuration uses zero inference; it does not change the consumed model-specific decision.',
            'on_terminal': 'RETIRE', 'unknown_partial_late': 'QUARANTINE', 'real_admission': 'NO'}


def native_plan():
    directory = ROOT / WORK
    return _plan(directory / 'bin', directory / 'input', directory / 'result')


def public_plan(binary, data, result, case):
    guard.require(case in PUBLIC_CASES, 'DETERMINISTIC_PUBLIC_CASE')
    plan = _plan(binary, data, result)
    script = 'retention.py' if case in ('deterministic_report', 'deterministic_invalid') else 'probe.py'
    plan['candidate_arguments'] = ['-I', '-S', '-B', str(binary / script),
                                   '../input/task.txt' if script == 'retention.py' else case]
    return plan


def prepare(binary, data, *, public_case=None):
    source_gate()
    content = stable_read_bytes(ROOT / WORKER, maximum_bytes=16384).replace(b'\r\n', b'\n')
    guard.require(hashlib.sha256(content).hexdigest() == _WORKER_SHA, 'DETERMINISTIC_WORKER_CHANGED')
    with (binary / 'retention.py').open('xb') as out:
        out.write(content)
    prompt = task.prompt()
    if public_case is not None:
        guard.require(public_case in PUBLIC_CASES, 'DETERMINISTIC_PUBLIC_CASE')
        content = stable_read_bytes(ROOT / PROBE, maximum_bytes=16384).replace(b'\r\n', b'\n')
        guard.require(hashlib.sha256(content).hexdigest() == _PROBE_SHA, 'DETERMINISTIC_WORKER_CHANGED')
        with (binary / 'probe.py').open('xb') as out:
            out.write(content)
        prefix, remainder = prompt.split(b'Source records: ', 1)
        _, suffix = remainder.split(b'\n/no_think', 1)
        rows = PUBLIC_ROWS if public_case != 'deterministic_invalid' else [dict(PUBLIC_ROWS[0], retired=False), *PUBLIC_ROWS[1:]]
        prompt = prefix + b'Source records: ' + json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('ascii') + b'\n/no_think' + suffix
        (data / 'unlisted.txt').write_bytes(b'PUBLIC_UNLISTED')
    with (data / 'task.txt').open('xb') as out:
        out.write(prompt)


def owner_intent():
    material = dict(task.owner_intent()['material'])
    for name in ('ash/g6_retention_substitution.py', WORKER, PROBE, PINS,
                 'tests/test_g6_retention_substitution.py', 'scripts/qualify_g6_retention_substitution.py'):
        material[name] = guard.normalized_sha(ROOT / name)
    config = native_plan()
    subject = {'schema_version': codec.SUBJECT_SCHEMA, 'kind': 'local_adapter', 'provider': 'repository',
               'source_ref': 'repository-owned-g6-deterministic-retention-v1', 'revision': 'g6-deterministic-retention-binding-v1',
               'capability_id': 'nexus/g6-deterministic-retention-qualification', 'action': 'execute',
               'content_sha256': hashlib.sha256(codec._canonical(material)).hexdigest(),
               'config_sha256': hashlib.sha256(codec._canonical(config)).hexdigest()}
    return {'schema': 'nexus.g6.native-owner-qualification-decision.v1', 'subject': subject,
            'subject_id': codec.subject(subject).subject_id, 'material': material, 'config': config,
            'issuer': {'provider': 'github', 'login': 'TDY0225', 'user_id': 223441940, 'principal': 'github-user-223441940'},
            'namespace': 'nexus-g3-approval-v1', 'purpose': 'APPROVE_ONE_G6_DETERMINISTIC_RETENTION_SUBSTITUTION_V1',
            'max_attempts': 1, 'terminal': 'RETIRE_ON_COMPLETION_FAILURE_CANCEL_OR_UNKNOWN',
            'automatic_retry': False, 'capability_registration': False, 'real_admission': 'NO'}


def attempt():
    result = guard._fixed_attempt('deterministic', 'qualification')
    receipt = {'schema': 'nexus.g6.deterministic-retention-receipt.v1', 'status': 'QUARANTINE',
               'retired': True, 'automatic_retry': False, 'model_invocations': 0, 'real_admission': 'NO'}
    directory = ROOT / WORK / 'result'
    try:
        guard.require(result.get('status') == 'DETERMINISTIC_RETENTION_RESULT_OBSERVED'
                      and result.get('retired') is True and result.get('job_active_after_termination') == 0,
                      'DETERMINISTIC_RESULT_NOT_ACCEPTED')
        raw = stable_read_bytes(directory / 'stdout.bin', maximum_bytes=guard.OUTPUT_LIMIT)
        guard.require(hashlib.sha256(raw).hexdigest() == result['stdout_sha256'], 'DETERMINISTIC_OUTPUT_CHANGED')
        report = task.verified_report(raw)
        guard.require(report is not None, 'DETERMINISTIC_REPORT_PROTOCOL')
        destination = directory / 'retention-index.csv'
        with destination.open('xb') as out:
            out.write(report)
        reopened = stable_read_bytes(destination, maximum_bytes=4096)
        guard.require(reopened == report, 'DETERMINISTIC_REPORT_READBACK')
        receipt.update(status='DETERMINISTIC_RETENTION_ARTIFACT_VERIFIED', artifact_bytes=len(reopened), rows=3,
                       artifact_sha256=hashlib.sha256(reopened).hexdigest(), artifact_path=destination.relative_to(ROOT).as_posix())
    except (OSError, ValueError):
        receipt['reason'] = 'DETERMINISTIC_ARTIFACT_UNVERIFIED'
    with (directory / 'report-receipt.json').open('x', encoding='utf8') as out:
        json.dump(receipt, out, sort_keys=True); out.write('\n')
    return receipt
