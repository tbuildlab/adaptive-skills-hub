"""Closed continuity refusal phases only; no session adoption or authority."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('session_stage_base', HERE/'scripts/verify_identity_stage.py')
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
G3 = BASE.G3
PROFILES = ('DISABLED_SESSION_STAGE', 'LIVE_DIAGNOSTIC_SESSION_STAGE')
REVISION = 'g3-d01-session-continuity-stage-v7'
TRANSPORT = BASE.TRANSPORT
ERRORS = tuple('IDENTITY_SESSION_' + p for p in ('TOTP_PRECHECK', 'TOTP_REPLY', 'TOTP_POSTCHECK'))

def compose(data, profile=PROFILES[0]):
    BASE.need(profile in PROFILES, 'session stage profile')
    blobs = BASE.compose(data, BASE.PROFILES[0 if profile == PROFILES[0] else 1])
    blobs[G3.INPUT] = blobs[G3.INPUT].replace(BASE.REVISION.encode(), REVISION.encode())
    put = lambda old, new: BASE.replace(blobs, TRANSPORT, old, new)
    put('#proof(body, factors, same = true, ceremony = false)',
        "#proof(body, factors, same = true, ceremony = false, phase = 'RECHECK')")
    put("throw new ClosedFailure('IDENTITY_SESSION_CONTINUITY');",
        "throw new ClosedFailure(phase === 'TOTP_PRECHECK' ? 'IDENTITY_SESSION_TOTP_PRECHECK' : phase === 'TOTP_REPLY' ? 'IDENTITY_SESSION_TOTP_REPLY' : phase === 'TOTP_POSTCHECK' ? 'IDENTITY_SESSION_TOTP_POSTCHECK' : 'IDENTITY_SESSION_CONTINUITY');")
    put('async #recheck() {', "async #recheck(phase = 'RECHECK') {")
    put("this.#proof(body, this.#two ? ['EMAIL_OTP', 'TOTP'] : ['EMAIL_OTP']);",
        "this.#proof(body, this.#two ? ['EMAIL_OTP', 'TOTP'] : ['EMAIL_OTP'], true, false, phase);")
    put("await this.#recheck();\n    const b = await this.#exchange('TOTP_AUTHENTICATE'",
        "await this.#recheck('TOTP_PRECHECK');\n    const b = await this.#exchange('TOTP_AUTHENTICATE'")
    put("this.#proof(b, ['EMAIL_OTP', 'TOTP'], true, true);",
        "this.#proof(b, ['EMAIL_OTP', 'TOTP'], true, true, 'TOTP_REPLY');")
    put("retireOwnerEnvelope(this.#envelope); this.#envelope = null;\n    await this.#recheck();",
        "retireOwnerEnvelope(this.#envelope); this.#envelope = null;\n    await this.#recheck('TOTP_POSTCHECK');")
    for name in (G3.POLICY, 'public/app.js'):
        BASE.replace(blobs, name, "'IDENTITY_SESSION_CONTINUITY'",
                     "'IDENTITY_SESSION_CONTINUITY', " + ', '.join(repr(e) for e in ERRORS))
    return blobs

def validate(blobs, data, profile=PROFILES[0]):
    parent = BASE.PROFILES[0 if profile == PROFILES[0] else 1]
    previous = BASE.compose(data, parent)
    report = BASE.validate(previous, data, parent)
    BASE.need(blobs == compose(data, profile), 'exact session stage source')
    BASE.need({n for n in blobs if blobs[n] != previous[n]} ==
              {G3.INPUT, G3.POLICY, TRANSPORT, 'public/app.js'}, 'four-file phase-label delta')
    for name in (G3.SERVICE, G3.CUSTODY, 'lib/stytch-identity.js', 'lib/stytch-projection.js', 'public/index.html'):
        BASE.need(blobs[name] == previous[name], 'preserved trust predicates ' + name)
    G3.HISTORICAL.scan(blobs); G3.HISTORICAL.config_review(blobs)
    report.update(profile=profile, deployment_revision=REVISION,
        continuity_phase_labels=list(ERRORS), identity_acceptance_predicates='UNCHANGED',
        changed_runtime_files=[G3.INPUT, G3.POLICY, TRANSPORT, 'public/app.js'],
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                         'source_uid': hashlib.sha1(b).hexdigest()} for n, b in sorted(blobs.items())})
    return report

def build(output, profile=PROFILES[0]):
    output = G3.HISTORICAL.safe_output(output); BASE.need(not output.exists(), 'fresh output')
    data = G3.generation3_input(); blobs = compose(data, profile); report = validate(blobs, data, profile)
    for n, b in blobs.items():
        p = output/'source'/n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('profile', 'files', 'zip_sha256', 'authority', 'real_admission_enabled')}))
    return report

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', required=True)
    p.add_argument('--profile', choices=PROFILES, default=PROFILES[0]); a = p.parse_args(); build(a.output, a.profile)
