"""One fixed local-only G6 retention-index task; not a generic model adapter.

The source corpus is actual, already-public project evidence. PRIVATE describes
the execution/routing policy, not a claim that these sources contain secrets.
No candidate execution, private source discovery, registration or grant here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import g6_native_binding as binding, g3_grant_codec as codec
from .ecosystem_storage import stable_read_bytes

ROOT = Path(__file__).resolve().parents[1]
_LOADED_SHA = hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
WORK = 'output/g6-local-retention-once-v1'
PACKET = 'output/g6-local-retention-owner-signing-v1/decision.json'
REVIEW = 'research/nexus-g6-local-retention-independent-review-v1.json'
PUBLIC_WORK = 'output/g6-local-retention-public-v2'
END = b'END_G6_AUDIT'
SOURCES = (
    ('v1', 'output/g6-native-private-once-v1/disposition.json',
     '4faf6db8803665af8a3dcd96c26337606d94538dfc14084f89d4312e858f155b'),
    ('v2', 'output/g6-native-public-once-v2/disposition.json',
     'edec34055bb2a1333faffa6f585e054685ae05c6e9f511d4a6f770fd0cc09639'),
    ('v3', 'output/g6-native-public-once-v3/disposition.json',
     '2e557402a45a93fac5792eb77b498884f97b0dc8ca1c3426ed0bf938a76a4007'),
)


def source_gate():
    binding.require(binding.normalized_sha(Path(__file__)) == _LOADED_SHA,
                    'LOADED_PRIVATE_REVISION_CHANGED')


def rows():
    """Read only three hash-pinned PUBLIC records, extract four closed fields."""
    source_gate()
    result = []
    for identifier, relative, expected in SOURCES:
        raw = stable_read_bytes(ROOT / relative, maximum_bytes=32768)
        binding.require(hashlib.sha256(raw).hexdigest() == expected, 'RETENTION_SOURCE_IDENTITY')
        # Hash-pinned observation bytes contain elapsed-time floats. They are
        # not G3 authority documents; retain the stricter G3 parser unchanged.
        value = json.loads(raw)
        binding.require(isinstance(value, dict) and value.get('retired') is True
                        and value.get('automatic_retry') is False
                        and value.get('real_admission') == 'NO', 'RETENTION_SOURCE_STATE')
        status = value.get('status')
        binding.require(status in ('QUARANTINE', 'NATIVE_BOUNDED_RESULT_OBSERVED'),
                        'RETENTION_SOURCE_OUTCOME')
        amount = value.get('retained_bytes')
        binding.require(type(amount) is int and 0 <= amount <= binding.OUTPUT_LIMIT,
                        'RETENTION_SOURCE_SIZE')
        result.append({'attempt': identifier, 'status': status, 'retired': True,
                       'retained_bytes': amount})
    return result


def prompt():
    # These are approved PUBLIC project fields, not arbitrary private file input.
    data = json.dumps(rows(), sort_keys=True, separators=(',', ':')).encode('ascii')
    request = (b'Create a local evidence retention index from the source records.\n'
               b'Return CSV only, in source order, with header attempt,outcome,action,bytes.\n'
               b'For status QUARANTINE use outcome QUARANTINE. For status '
               b'NATIVE_BOUNDED_RESULT_OBSERVED use outcome PUBLIC_ONLY_PASS.\n'
               b'Every retired record has action KEEP. Copy retained_bytes into bytes.\n'
               b'Do not delete, reset or replay any record. No explanations or code fences.\n'
               b'After the three data rows, write END_G6_AUDIT on its own line.\n'
               b'Source records: ' + data + b'\n/no_think')
    return (b'<|im_start|>user\n' + request + b'<|im_end|>\n'
            b'<|im_start|>assistant\n<think>\n\n</think>\n\n\n')


def expected_report():
    lines = ['attempt,outcome,action,bytes']
    for row in rows():
        outcome = 'QUARANTINE' if row['status'] == 'QUARANTINE' else 'PUBLIC_ONLY_PASS'
        lines.append(f"{row['attempt']},{outcome},KEEP,{row['retained_bytes']}")
    return ('\n'.join(lines) + '\n').encode('ascii')


def verified_report(stdout):
    """One exact CSV protocol; no arbitrary markdown/noise/semantic cleanup."""
    expected = expected_report() + END
    if stdout.replace(b'\r\n', b'\n').strip() != expected:
        return None
    return expected_report()


def native_plan():
    plan = binding.native_plan()
    directory = ROOT / WORK
    binary = directory / 'bin'
    task = directory / 'input/task.txt'
    plan.update(schema='nexus.g6.local-retention-plan.v1',
                cwd=str(binary), executable=str(binary / 'llama-completion.exe'),
                backend=str(binary / 'ggml-cpu-x64.dll'), input=str(task),
                result_directory=str(directory / 'result'),
                input_sha256=hashlib.sha256(prompt()).hexdigest(),
                effective_prompt_sha256=hashlib.sha256(prompt()[:-1]).hexdigest(),
                task='real-project-retired-attempt-retention-index',
                input_classification='PUBLIC_PROJECT_EVIDENCE_WITH_LOCAL_ONLY_ROUTING',
                source_files=[{'path': p, 'sha256': h} for _, p, h in SOURCES],
                declared_restrictions=['no-frontier-model', 'local-model-only',
                                       'no-agents', 'no-remote-mcp'],
                report='verified local result/retention-index.csv; no conversation/export',
                usefulness='Inspectable retention index separates quarantines from bounded public success; KEEP every retired record.')
    plan['filesystem'] = {':root': 'deny', 'C:/Windows/System32': 'read',
                          binary.as_posix(): 'read',
                          Path(plan['model_blob']).as_posix(): 'read', task.as_posix(): 'read'}
    plan['candidate_arguments'] = list(plan['candidate_arguments'])
    plan['candidate_arguments'][-1] = END.decode('ascii')
    return plan


def owner_intent():
    material_names = (*binding.owner_intent()['material'],
                      'ash/g6_private_completion.py', 'tests/test_g6_private_completion.py',
                      'scripts/qualify_g6_private_completion.py')
    material = {name: binding.normalized_sha(ROOT / name) for name in material_names}
    config = native_plan()
    subject = {'schema_version': codec.SUBJECT_SCHEMA, 'kind': 'local_adapter',
               'provider': 'repository', 'source_ref': 'repository-owned-g6-local-retention-v1',
               'revision': 'g6-local-retention-binding-v1',
               'capability_id': 'nexus/g6-local-retention-qualification', 'action': 'execute',
               'content_sha256': hashlib.sha256(codec._canonical(material)).hexdigest(),
               'config_sha256': hashlib.sha256(codec._canonical(config)).hexdigest()}
    return {'schema': 'nexus.g6.native-owner-qualification-decision.v1',
            'subject': subject, 'subject_id': codec.subject(subject).subject_id,
            'material': material, 'config': config,
            'issuer': {'provider': 'github', 'login': 'TDY0225', 'user_id': 223441940,
                       'principal': 'github-user-223441940'}, 'namespace': 'nexus-g3-approval-v1',
            'purpose': 'APPROVE_ONE_G6_LOCAL_RETENTION_QUALIFICATION', 'max_attempts': 1,
            'terminal': 'RETIRE_ON_COMPLETION_FAILURE_CANCEL_OR_UNKNOWN',
            'automatic_retry': False, 'capability_registration': False, 'real_admission': 'NO'}


def attempt():
    """One closed task, using the existing guard; no arguments or retry loop."""
    result = binding._fixed_attempt('private', 'qualification')
    receipt = {'schema': 'nexus.g6.local-retention-receipt.v1',
               'status': 'QUARANTINE', 'retired': True, 'automatic_retry': False,
               'private_source_claim': 'NONE_PUBLIC_PROJECT_EVIDENCE',
               'real_admission': 'NO'}
    directory = ROOT / WORK / 'result'
    try:
        binding.require(result.get('status') == 'LOCAL_RETENTION_RESULT_OBSERVED'
                        and result.get('retired') is True
                        and result.get('job_active_after_termination') == 0,
                        'RETENTION_RESULT_NOT_ACCEPTED')
        raw = stable_read_bytes(directory / 'stdout.bin', maximum_bytes=binding.OUTPUT_LIMIT)
        binding.require(hashlib.sha256(raw).hexdigest() == result.get('stdout_sha256'),
                        'RETENTION_OUTPUT_CHANGED')
        report = verified_report(raw)
        binding.require(report is not None, 'RETENTION_REPORT_PROTOCOL')
        destination = directory / 'retention-index.csv'
        with destination.open('xb') as target:
            target.write(report)
        reopened = stable_read_bytes(destination, maximum_bytes=4096)
        binding.require(reopened == report, 'RETENTION_REPORT_READBACK')
        receipt.update(status='LOCAL_RETENTION_ARTIFACT_VERIFIED',
                       artifact_sha256=hashlib.sha256(reopened).hexdigest(),
                       artifact_bytes=len(reopened), rows=3,
                       artifact_path=destination.relative_to(ROOT).as_posix())
    except (OSError, ValueError):
        # Preserve the original guard record and all partial bytes, never retry.
        receipt['reason'] = 'RETENTION_ARTIFACT_UNVERIFIED'
    destination = directory / 'report-receipt.json'
    with destination.open('x', encoding='utf-8') as target:
        json.dump(receipt, target, sort_keys=True)
        target.write('\n')
    return receipt
