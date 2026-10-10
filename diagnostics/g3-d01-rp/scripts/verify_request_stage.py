"""Closed request-stage diagnostics; historical generation 3 bytes stay frozen."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('request_stage_base', HERE/'scripts/verify_generation3.py')
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
PROFILE = 'LIVE_DIAGNOSTIC_REQUEST_STAGE'
REVISION = 'g3-d01-owner-live-request-stage-v3'
ERRORS = ('REQUEST_ORIGIN', 'REQUEST_ROUTE', 'REQUEST_COOKIE', 'REQUEST_CONTEXT_MISSING',
          'REQUEST_CSRF', 'REQUEST_CONTENT_TYPE', 'REQUEST_SIZE', 'REQUEST_BODY',
          'REQUEST_CODE_MEMBER', 'REQUEST_CODE_SHAPE', 'REQUEST_ORDER',
          'REQUEST_ACTION', 'REQUEST_METHOD_STATE', 'REQUEST_BUSY')

def need(ok, reason):
    if not ok: raise RuntimeError('REQUEST_STAGE_BLOCKED: '+reason)

def replace(blobs, path, old, new):
    old, new = old.encode(), new.encode()
    need(blobs[path].count(old) == 1, 'exact replacement: '+path)
    blobs[path] = blobs[path].replace(old, new)

def compose(data):
    need(data == BASE.reviewed_public_input(), 'exact reviewed input only')
    blobs = BASE.compose('LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT', data)
    for old in (BASE.REVISION['LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT'],):
        # Two fixed occurrences are the deployment and provider revision.
        need(blobs[BASE.INPUT].count(old.encode()) == 2, 'revision membership')
        blobs[BASE.INPUT] = blobs[BASE.INPUT].replace(old.encode(), REVISION.encode())
    replace(blobs, BASE.POLICY, "'CREDENTIAL', 'PROJECT_CONFIG_MISSING'",
            "'CREDENTIAL', "+', '.join(repr(e) for e in ERRORS)+", 'PROJECT_CONFIG_MISSING'")
    service = BASE.SERVICE
    replace(blobs, service, "throw new ClosedFailure('REQUEST');\n  const matches", "throw new ClosedFailure('REQUEST_COOKIE');\n  const matches")
    replace(blobs, service, "throw new ClosedFailure('REQUEST');\n  return matches", "throw new ClosedFailure('REQUEST_COOKIE');\n  return matches")
    replace(blobs, service, "['cross-site','same-site'].includes(h['sec-fetch-site'])) throw new ClosedFailure('REQUEST');",
            "['cross-site','same-site'].includes(h['sec-fetch-site'])) throw new ClosedFailure('REQUEST_ORIGIN');")
    replace(blobs, service, "!['GET','POST'].includes(req.method)) throw new ClosedFailure('REQUEST');",
            "!['GET','POST'].includes(req.method)) throw new ClosedFailure('REQUEST_ROUTE');")
    replace(blobs, service, "      if (!page || h.origin!==ORIGIN || !equal(h['x-g3-csrf'],page.csrf) || h['content-type']!=='application/json'\n          || Buffer.byteLength(JSON.stringify(req.body ?? {}))>4096) throw new ClosedFailure('REQUEST');",
            "      if (!page) throw new ClosedFailure('REQUEST_CONTEXT_MISSING');\n"
            "      if (h.origin!==ORIGIN) throw new ClosedFailure('REQUEST_ORIGIN');\n"
            "      if (!equal(h['x-g3-csrf'],page.csrf)) throw new ClosedFailure('REQUEST_CSRF');\n"
            "      if (h['content-type']!=='application/json') throw new ClosedFailure('REQUEST_CONTENT_TYPE');\n"
            "      if (Buffer.byteLength(JSON.stringify(req.body ?? {}))>4096) throw new ClosedFailure('REQUEST_SIZE');")
    replace(blobs, service, "if (!body || !closed(body, ['action', ...(Object.hasOwn(body,'code') ? ['code'] : [])])) throw new ClosedFailure('REQUEST');",
            "if (!body || !closed(body, ['action', ...(Object.hasOwn(body,'code') ? ['code'] : [])])) throw new ClosedFailure('REQUEST_BODY');")
    replace(blobs, service, "if (Object.hasOwn(body,'code') !== codes.includes(action)) throw new ClosedFailure('REQUEST');",
            "if (Object.hasOwn(body,'code') !== codes.includes(action)) throw new ClosedFailure('REQUEST_CODE_MEMBER');\n"
            "      if (codes.includes(action) && (typeof body.code!=='string' || !/^\\d{6}$/.test(body.code))) throw new ClosedFailure('REQUEST_CODE_SHAPE');")
    replace(blobs, service, "if (action!=='EMAIL_OTP_SEND') throw new ClosedFailure('REQUEST'); page.backend=factory();",
            "if (action!=='EMAIL_OTP_SEND') throw new ClosedFailure('REQUEST_ORDER'); page.backend=factory();")
    replace(blobs, service, "if (action!==POINTS[page.point]) throw new ClosedFailure('REQUEST');",
            "if (action!==POINTS[page.point]) throw new ClosedFailure('REQUEST_ORDER');")
    replace(blobs, service, "      } else throw new ClosedFailure('REQUEST');", "      } else throw new ClosedFailure('REQUEST_ACTION');")
    # No token, value, length or identifier leaves the runtime. Only fixed guards.
    transport = 'lib/server/stytch-transport.js'
    replace(blobs, transport, "if (this.#busy) return safeResult('REQUEST', false, true);",
            "if (this.#busy) return safeResult('REQUEST_BUSY', false, true);")
    replace(blobs, transport, "if (!this.#method || this.#session || !closed(input, ['code']) || typeof input.code !== 'string' || !/^\\d{6}$/.test(input.code)) throw new ClosedFailure('REQUEST');",
            "if (!this.#method || this.#session) throw new ClosedFailure('REQUEST_METHOD_STATE');\n"
            "    if (!closed(input, ['code']) || typeof input.code !== 'string' || !/^\\d{6}$/.test(input.code)) throw new ClosedFailure('REQUEST_CODE_SHAPE');")
    replace(blobs, 'public/app.js', 'let csrf=null;', 'let csrf=null, busy=false;')
    replace(blobs, 'public/app.js', 'async function call(action) {', 'async function call(action) {\n  if(busy) return;')
    replace(blobs, 'public/app.js', "  if(code) code.value='';\n  try {",
            "  if(action==='EMAIL_OTP_AUTHENTICATE' && !/^\\d{6}$/.test(body.code)) {\n"
            "    evidence.textContent=JSON.stringify({diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',\n"
            "      real_admission:'DISABLED',qualified_live:false,result:'DENY',error_class:'REQUEST_CODE_SHAPE',\n"
            "      evidence_source:'LOCAL_INPUT_VALIDATION_ONLY',context_expires_at:null},null,2); return;\n"
            "  }\n  if(code) code.value='';\n  busy=true; controls.disabled=true;\n  try {")
    replace(blobs, 'public/app.js', "evidence.textContent='DENY / UNKNOWN'; }\n}",
            "evidence.textContent='DENY / UNKNOWN'; }\n  finally { busy=false; }\n}")
    return blobs

def validate(blobs, data):
    need(blobs == compose(data) and len(blobs) == 19, 'exact closed source')
    BASE.HISTORICAL.scan(blobs)
    BASE.HISTORICAL.config_review(blobs)
    for path, blob in blobs.items():
        if not path.endswith('.js'): continue
        text = blob.decode()
        need(not re.search(r'\bimport\s*\(|\brequire\s*\(|\beval\s*\(|\bconsole\s*\.', text), 'dynamic import/logging')
        for declaration in re.findall(r'(?m)^\s*import\b[^;]+;', text):
            literals = re.findall(r"['\"]([^'\"]+)['\"]", declaration)
            need(len(literals) == 1, 'closed import')
            target = literals[0]
            if target.startswith('node:'): continue
            need(target.startswith('.'), 'external dependency')
            parts = []
            for part in (PurePosixPath(path).parent/target).parts:
                if part == '..': need(bool(parts), 'import escape'); parts.pop()
                elif part != '.': parts.append(part)
            need('/'.join(parts) in blobs, 'missing import')
        if path.startswith('public/'):
            need(not re.search(r'lib/server|process\.env|STYTCH_SECRET|session_token|session_jwt|localStorage|sessionStorage|innerHTML', text), 'client boundary')
            for value in (data['provider']['project_id'], data['provider']['owner_user_id'], data['provider']['delivery_email'], data['keyset']['source']):
                need(value.encode() not in blob, 'client identity disclosure')
    return {'profile': PROFILE, 'files': 19, 'application_generation': 3,
            'registration_generation': 3, 'deployment_revision': REVISION,
            'authority': 'NONE', 'real_admission_enabled': 'NO',
            'zip_sha256': hashlib.sha256(BASE.HISTORICAL.frozen_zip(blobs)).hexdigest(),
            'public_review_valid_from': data['keyset']['valid_from'],
            'public_review_valid_until': data['keyset']['valid_until'],
            'provider_calls_performed_by_builder': 0, 'credential_access_by_builder': 'NONE',
            'files_sha256': {n: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                               'source_uid': hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())}}

def build(output):
    output = BASE.HISTORICAL.safe_output(output)
    need(not output.exists(), 'fresh output')
    data = BASE.generation3_input()
    blobs = compose(data)
    report = validate(blobs, data)
    source = output/'source'
    source.mkdir(parents=True)
    for n,b in blobs.items():
        path=source/n; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(BASE.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}))
    return report

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    build(p.parse_args().output)
