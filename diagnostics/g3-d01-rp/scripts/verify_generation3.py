"""Exact authorized generation 3 artifact; no deploy, provider or credential use."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, subprocess
from functools import lru_cache
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('historical_generation2', HERE/'scripts/verify_generation2.py')
G2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G2)
HISTORICAL = G2.HISTORICAL
PROFILES = ('DISABLED', 'LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT')
REVISION = {'DISABLED': 'g3-d01-owner-delivery-v3',
            'LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT': 'g3-d01-owner-live-credential-format-v3'}
INPUT, POLICY, CUSTODY, SERVICE = G2.INPUT, G2.POLICY, G2.CUSTODY, G2.SERVICE

def need(ok, reason):
    if not ok: raise RuntimeError('GENERATION3_BLOCKED: ' + reason)

@lru_cache(maxsize=1)
def reviewed_public_input():
    value = subprocess.check_output(['node', '--input-type=module', '-e',
        "import {DISABLED_GENERATION_3_INPUT as d} from './lib/server/owner-keyset-generation3.js';process.stdout.write(JSON.stringify(d));"], cwd=HERE)
    need(len(value) <= 16384, 'bounded public input')
    return json.loads(value)

def generation3_input():
    d = reviewed_public_input()
    previous = G2.reviewed_public_input()
    need(d['keyset']['keys'] == previous['keyset']['keys'], 'unchanged reviewed material')
    for field in ('source', 'project_id', 'valid_from', 'valid_until'):
        need(d['keyset'][field] == previous['keyset'][field], 'no renewal or new trust source')
    need(d['registration_generation'] == d['provider']['application_generation'] == d['keyset']['application_generation'] == 3,
         'exact generation')
    subprocess.run(['node', '--input-type=module', '-e',
        "import {DISABLED_GENERATION_3_INPUT as d} from './lib/server/owner-keyset-generation3.js';"
        "import {pinnedKeys} from './lib/server/pinned-identity.js';"
        "import {validateReviewedRegistration} from './lib/server/provider-registration.js';"
        "if(d.mode!=='FAKE_DISABLED'||!validateReviewedRegistration(d.provider)||!pinnedKeys(d.keyset,d.provider,Date.now()))"
        "throw Error('REVIEW_EXPIRED_OR_INVALID');"], cwd=HERE, check=True)
    return d

def input_bytes(data, profile):
    d = json.loads(json.dumps(data))
    d['mode'] = 'FAKE_DISABLED' if profile == 'DISABLED' else 'D01_DIAGNOSTIC_LIVE_STYTCH'
    d['deployment_revision'] = d['provider']['deployment_revision'] = REVISION[profile]
    return ("if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');\n"
        "// Generation 3 authorized rebind; original public review interval unchanged.\n"
        "const reviewed = " + json.dumps(d, indent=2, ensure_ascii=True) + ";\n"
        "reviewed.provider.factors = Object.freeze(reviewed.provider.factors);\n"
        "reviewed.provider = Object.freeze(reviewed.provider);\n"
        "reviewed.keyset.keys = Object.freeze(reviewed.keyset.keys.map(k => Object.freeze(k)));\n"
        "reviewed.keyset = Object.freeze(reviewed.keyset);\n"
        "export const DEPLOYMENT = Object.freeze(reviewed);\n").encode()

def compose(profile, data):
    need(profile in PROFILES, 'profile')
    need(data == reviewed_public_input(), 'exact authorized input only')
    blobs = G2.originals()
    blobs[INPUT] = input_bytes(data, profile)
    if profile != 'DISABLED':
        for name in ('CODE_REVIEWED_LIVE_ENABLED', 'DEPLOYMENT_REGISTRATION_ENABLED'):
            old = (name + ' = false').encode()
            need(blobs[POLICY].count(old) == 1, 'exact reviewed gate')
            blobs[POLICY] = blobs[POLICY].replace(old, (name + ' = true').encode())
        G2.readiness_only(blobs)
        G2.protocol_status_only(blobs)
        G2.credential_format_only(blobs)
    return blobs

def validate(blobs, profile, data):
    expected = compose(profile, data)
    need(set(blobs) == set(expected) and len(blobs) == 19, 'exact inventory')
    need(blobs == expected, 'exact reviewed transformations only')
    HISTORICAL.scan(blobs)
    HISTORICAL.config_review(blobs)
    for name, blob in blobs.items():
        if not name.endswith('.js'): continue
        text = blob.decode()
        need(not re.search(r'\bimport\s*\(|\brequire\s*\(|\beval\s*\(|\bconsole\s*\.', text), 'dynamic import/logging')
        for declaration in re.findall(r'(?m)^\s*import\b[^;]+;', text):
            literals = re.findall(r"['\"]([^'\"]+)['\"]", declaration)
            need(len(literals) == 1, 'unambiguous import')
            target = literals[0]
            if target.startswith('node:'): continue
            need(target.startswith('.'), 'third party import')
            parts = []
            for part in (PurePosixPath(name).parent/target).parts:
                if part == '..': need(bool(parts), 'import escape'); parts.pop()
                elif part != '.': parts.append(part)
            need('/'.join(parts) in blobs, 'closed static import')
        if name.startswith('public/'):
            need(not re.search(r'lib/server|process\.env|STYTCH_SECRET|session_token|session_jwt|localStorage|sessionStorage|innerHTML', text), 'client boundary')
            for value in (data['provider']['project_id'], data['provider']['owner_user_id'],
                          data['provider']['delivery_email'], data['keyset']['source']):
                need(value.encode() not in blob, 'public registration disclosure')
    return {'profile': profile, 'files': 19, 'mode': 'FAKE_DISABLED' if profile == 'DISABLED' else 'D01_DIAGNOSTIC_LIVE_STYTCH',
        'application_generation': 3, 'registration_generation': 3, 'deployment_revision': REVISION[profile],
        'authority': 'NONE', 'real_admission_enabled': 'NO',
        'zip_sha256': hashlib.sha256(HISTORICAL.frozen_zip(blobs)).hexdigest(),
        'public_review_valid_from': data['keyset']['valid_from'], 'public_review_valid_until': data['keyset']['valid_until'],
        'changed_runtime_files': [INPUT] if profile == 'DISABLED' else [INPUT, POLICY, CUSTODY, SERVICE],
        'files_sha256': {n: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                           'source_uid': hashlib.sha1(b).hexdigest()} for n, b in sorted(blobs.items())},
        'provider_calls_performed_by_builder': 0, 'credential_access_by_builder': 'NONE', 'deployment_performed': False}

def build(output, profile):
    output = HISTORICAL.safe_output(output)
    need(not output.exists(), 'fresh output required')
    data = generation3_input()
    blobs = compose(profile, data)
    report = validate(blobs, profile, data)
    source = output/'source'
    source.mkdir(parents=True)
    for name, blob in blobs.items():
        path = source/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    (output/'diagnostic-source.zip').write_bytes(HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('profile', 'files', 'application_generation', 'zip_sha256', 'authority', 'real_admission_enabled')}))
    return report

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    p.add_argument('--profile', choices=PROFILES, default='DISABLED')
    args = p.parse_args()
    build(args.output, args.profile)
