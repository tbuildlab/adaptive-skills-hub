#!/usr/bin/env python3
"""Verify one fixed Owner decision's public evidence; never register or dispatch."""
from __future__ import annotations

import argparse
import base64
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import HTTPRedirectHandler, Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ash import core_capabilities as files, g3_grant_codec as codec

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_SHA = '064f3e9609239cb5f859f13111dde5ed6cfd29c031407712d54aad5514c0f508'
PROPOSAL_SHA = '6a9fb49a874ced10ba0ea6a4aea4cd9c5d48e77c1d6f0f448551d3b7edf4504c'
SUBJECT_ID = 'nexus.g3.subject.v1:2a20b4b3b2d57f35832df83737c3a60896b9c8a2df9dd5fd116828f03ead222e'
NAMESPACE, PRINCIPAL = 'nexus-g3-approval-v1', 'github-user-223441940'


class Denied(ValueError):
    pass


def require(ok, stage):
    if not ok:
        raise Denied(stage)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bounded(path, maximum):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'INPUT_FILE')
    with path.open('rb') as stream:
        data = stream.read(maximum + 1)
    require(len(data) <= maximum, 'INPUT_SIZE')
    return data


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise Denied('SOURCE_REDIRECT')


def github(suffix):
    url = 'https://api.github.com/users/TDY0225' + suffix
    request = Request(url, headers={'Accept': 'application/vnd.github+json',
                                  'User-Agent': 'Nexus-G3-Owner-Origin-Readback',
                                  'Cache-Control': 'no-cache'})
    with build_opener(NoRedirect()).open(request, timeout=8) as response:
        require(response.status == 200, 'SOURCE_HTTP')
        require('next' not in response.headers.get('Link', ''), 'SOURCE_PAGINATION')
        require(response.headers.get('Age', '0') == '0', 'SOURCE_CACHE')
        issued = parsedate_to_datetime(response.headers.get('Date', ''))
        require(issued.tzinfo is not None and abs(time.time() - issued.timestamp()) <= 30,
                'SOURCE_DATE')
        body = response.read(262145)
        require(len(body) <= 262144, 'SOURCE_SIZE')
    return json.loads(body)


def public_key(raw):
    parts = raw.decode('ascii').strip().split()
    require(len(parts) >= 2 and parts[0] == 'ssh-ed25519', 'KEY_TYPE')
    blob = base64.b64decode(parts[1], validate=True)
    require(len(blob) == 51 and blob[:19] == b'\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20',
            'KEY_FORMAT')
    return ' '.join(parts[:2]), 'SHA256:' + base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')


def verify(payload_path, signature_path, public_path):
    # Only the public .pub file is opened; no private key/agent or signing call.
    require(Path(public_path).suffix.lower() == '.pub', 'PUBLIC_FILE_REQUIRED')
    raw = bounded(payload_path, 65536)
    require(sha(raw) == PAYLOAD_SHA, 'PAYLOAD_DIGEST')
    body = json.loads(raw)
    require(body['proposal_sha256'] == PROPOSAL_SHA and body['subject_id'] == SUBJECT_ID,
            'SUBJECT_PROPOSAL_BINDING')
    require(body['issuer'] == {'provider': 'github', 'login': 'TDY0225', 'user_id': 223441940,
                               'principal': PRINCIPAL} and body['namespace'] == NAMESPACE,
            'ISSUER_BINDING')
    require(body['effective_at'] <= time.time() < body['expires_at'], 'DECISION_VALIDITY')
    require(codec.subject(body['subject']).subject_id == SUBJECT_ID, 'SUBJECT_CODEC')
    def digest(value):
        return sha((json.dumps(value, sort_keys=True, ensure_ascii=False,
                               separators=(',', ':')) + '\n').encode('utf-8'))
    require(digest(body['component']) == body['subject']['content_sha256']
            and digest(body['config']) == body['subject']['config_sha256']
            and digest(body['review_evidence']) == body['review_evidence_sha256'], 'INTERNAL_BINDING')
    for name, expected in {**body['component']['material_files'], **body['review_evidence']}.items():
        require(sha(files.read_bytes(ROOT, name)) == expected, 'CURRENT_COMPONENT_OR_REVIEW')
    require(sha(files.read_bytes(ROOT, 'research/nexus-g3-approval-origin-bootstrap-proposal-v1.json'))
            == PROPOSAL_SHA, 'PROPOSAL_BYTES')
    key, fingerprint = public_key(bounded(public_path, 4096))
    signature = bounded(signature_path, 16384)
    require(signature.startswith(b'-----BEGIN SSH SIGNATURE-----'), 'SIGNATURE_FORMAT')
    source_started = time.monotonic()
    profile = github('')
    require(type(profile) is dict and profile.get('id') == 223441940
            and profile.get('login') == 'TDY0225', 'GITHUB_IDENTITY')
    keys = github('/ssh_signing_keys?per_page=100')
    require(type(keys) is list and 1 <= len(keys) <= 64, 'SIGNING_KEY_REGISTRY')
    matches = [entry for entry in keys if type(entry) is dict
               and type(entry.get('key')) is str and ' '.join(entry['key'].split()[:2]) == key]
    require(len(matches) == 1 and type(matches[0].get('id')) is int, 'SIGNING_KEY_MEMBERSHIP')
    # This is the exact native executable inspected for this Windows procedure;
    # a caller-controlled environment must not select a replacement verifier.
    executable = Path(r'C:\Windows\System32\OpenSSH\ssh-keygen.exe')
    require(executable.is_file(), 'OPENSSH_UNAVAILABLE')
    with tempfile.TemporaryDirectory(prefix='nexus-g3-public-verification-') as temporary:
        directory = Path(temporary)
        allowed = directory / 'allowed_signers'
        allowed.write_text(f'{PRINCIPAL} namespaces="{NAMESPACE}" {key}\n', encoding='ascii')
        sig = directory / 'decision.sig'
        sig.write_bytes(signature)
        result = subprocess.run([str(executable), '-Y', 'verify', '-f', str(allowed),
                                 '-I', PRINCIPAL, '-n', NAMESPACE, '-s', str(sig)],
                                input=raw, capture_output=True, timeout=5, check=False)
        require(result.returncode == 0, 'CRYPTOGRAPHIC_SIGNATURE')
    require(0 <= time.monotonic() - source_started <= 30, 'SOURCE_FRESHNESS')
    require(body['effective_at'] <= time.time() < body['expires_at'], 'DECISION_VALIDITY')
    return {'status': 'SIGNATURE_AND_BOUND_DECISION_VERIFIED', 'payload_sha256': PAYLOAD_SHA,
            'proposal_sha256': PROPOSAL_SHA, 'subject_id': SUBJECT_ID,
            'github_user_id': 223441940, 'github_login': 'TDY0225',
            'github_signing_key_id': matches[0]['id'], 'key_fingerprint': fingerprint,
            'namespace': NAMESPACE, 'principal': PRINCIPAL,
            'record_kind': 'READBACK_ONLY_NOT_BEARER_AUTHORITY',
            'registration_created': False, 'dispatch_authority': 'none', 'real_admission': 'NO'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', type=Path, required=True)
    parser.add_argument('--signature', type=Path, required=True)
    parser.add_argument('--public-key', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.payload, args.signature, args.public_key)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        stage = str(error) if type(error) is Denied else 'UNAVAILABLE_OR_MALFORMED_EVIDENCE'
        print(json.dumps({'status': 'DENY_OR_UNKNOWN', 'stage': stage,
                          'registration_created': False, 'dispatch_authority': 'none',
                          'real_admission': 'NO'}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
