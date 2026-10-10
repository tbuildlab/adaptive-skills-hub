"""Owner-accepted pre-context MFA transition; diagnostic only, never authority."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('mfa_parent', HERE/'scripts/verify_session_stage.py')
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
G3 = BASE.G3
PROFILES = ('DISABLED_MFA_TRANSITION', 'LIVE_DIAGNOSTIC_MFA_TRANSITION')
REVISION = 'g3-d01-precontext-mfa-transition-v8'
TRANSPORT = BASE.TRANSPORT

HELPERS = r'''
// Private lineage evidence. No bearer, alias, discovery or browser-selected binding.
function factorLineage(body, two) {
  const factors = body.session.authentication_factors;
  const email = factors.find(f => ['otp', 'email_otp'].includes(f.type) && f.delivery_method === 'email');
  const totp = factors.find(f => f.type === 'totp' && f.delivery_method === 'authenticator_app');
  const exactTime = value => {
    if (timestamp(value) === null) throw new ClosedFailure('FACTORS');
    const m = /^(.*?)(?:\.(\d{1,9}))?Z$/.exec(value);
    return m[1] + '.' + (m[2] ?? '').padEnd(9, '0') + 'Z';
  };
  if (!identifier(email?.email_factor?.email_id)) throw new ClosedFailure('FACTORS');
  const lineage = { email_id: email.email_factor.email_id, email_at: exactTime(email.last_authenticated_at) };
  if (two) {
    if (!identifier(totp?.authenticator_app_factor?.totp_id)) throw new ClosedFailure('FACTORS');
    lineage.totp_id = totp.authenticator_app_factor.totp_id;
    lineage.totp_at = exactTime(totp.last_authenticated_at);
    const list = body.user.totps;
    if (!Array.isArray(list) || list.length !== 1 || list[0].verified !== true
        || list[0].totp_id !== lineage.totp_id) throw new ClosedFailure('FACTORS');
  }
  return Object.freeze(lineage);
}
function sameLineage(actual, expected) {
  if (!expected || Object.keys(expected).some(k => actual[k] !== expected[k])) throw new ClosedFailure('FACTORS');
}
'''

TOTP = r'''    const initial = await this.#recheck('TOTP_PRECHECK');
    const enrolled = initial.user.totps;
    if (!Array.isArray(enrolled) || enrolled.length !== 1 || enrolled[0].verified !== true
        || !identifier(enrolled[0].totp_id)) throw new ClosedFailure('FACTORS');
    const expectedTotp = enrolled[0].totp_id;
    if (this.#totp && this.#totp.totp_id !== expectedTotp) throw new ClosedFailure('FACTORS');
    const b = await this.#exchange('TOTP_AUTHENTICATE', { user_id: this.#session.user_id, totp_code: input.code,
      session_token: this.#token, session_duration_minutes: 15 });
    if (b.user_id !== this.#session.user_id || b.totp_id !== expectedTotp) throw new ClosedFailure('IDENTITY_TOTP_RESPONSE');
    // Only this initial ceremony may produce a candidate different session/token.
    // Existing exact registered User/project/signature/freshness checks still run.
    const candidate = this.#proof(b, ['EMAIL_OTP', 'TOTP'], false);
    const lineage = factorLineage(b, true); sameLineage(lineage, this.#bootstrap);
    if (lineage.totp_id !== expectedTotp) throw new ClosedFailure('FACTORS');
    this.#check();
    const checked = await this.#exchange('SESSION_AUTHENTICATE', { session_token: b.session_token });
    const final = this.#proof(checked, ['EMAIL_OTP', 'TOTP'], false);
    if (final.session_id !== candidate.session_id || final.user_id !== candidate.user_id)
      throw new ClosedFailure('IDENTITY_SESSION_TOTP_POSTCHECK');
    if (checked.session_token !== b.session_token) throw new ClosedFailure('IDENTITY_TOKEN_CONTINUITY');
    if (JSON.stringify(final) !== JSON.stringify(candidate)) throw new ClosedFailure('FACTORS');
    sameLineage(factorLineage(checked, true), lineage); this.#check();
    // Atomic local finalization under #run busy exclusion, after remote evidence.
    // Original deadline is contracted; never refresh a generation or review.
    this.#deadline = Math.min(this.#deadline, final.expires_at, final.factors[1].at + 300000);
    this.#session = final; this.#token = checked.session_token; this.#bootstrap = lineage;
    this.#two = true; this.#totp = null;
    retireOwnerEnvelope(this.#envelope); this.#envelope = null;'''

def compose(data, profile=PROFILES[0]):
    BASE.BASE.need(profile in PROFILES, 'MFA profile')
    blobs = BASE.compose(data, BASE.PROFILES[0 if profile == PROFILES[0] else 1])
    blobs[G3.INPUT] = blobs[G3.INPUT].replace(BASE.REVISION.encode(), REVISION.encode())
    put = lambda old, new: BASE.BASE.replace(blobs, TRANSPORT, old, new)
    put("import { projectSession }", "import { projectSession, timestamp }")
    put('const fixtures = new WeakMap();', 'const fixtures = new WeakMap();\n'+HELPERS)
    put('#native; #keyset; #ownerChannel; #envelope = null;', '#native; #keyset; #ownerChannel; #envelope = null; #bootstrap = null;')
    put('this.#retired = true; this.#token = null;', 'this.#retired = true; this.#bootstrap = null; this.#token = null;')
    put("this.#proof(body, this.#two ? ['EMAIL_OTP', 'TOTP'] : ['EMAIL_OTP'], true, false, phase);",
        "this.#proof(body, this.#two ? ['EMAIL_OTP', 'TOTP'] : ['EMAIL_OTP'], true, false, phase);\n    sameLineage(factorLineage(body, this.#two), this.#bootstrap); return body;")
    put("const s = this.#proof(b, ['EMAIL_OTP'], false);",
        "const s = this.#proof(b, ['EMAIL_OTP'], false);\n    const lineage = factorLineage(b, false);\n    if (lineage.email_id !== this.#method) throw new ClosedFailure('FACTORS');\n    this.#bootstrap = lineage;")
    text = blobs[TRANSPORT].decode()
    start = text.index("    await this.#recheck('TOTP_PRECHECK');", text.index('  TOTP_AUTHENTICATE(input)'))
    end = text.index('\n  }); }', start)
    blobs[TRANSPORT] = (text[:start]+TOTP+text[end:]).encode()
    return blobs

def validate(blobs, data, profile=PROFILES[0]):
    parent = BASE.PROFILES[0 if profile == PROFILES[0] else 1]
    previous = BASE.compose(data, parent); report = BASE.validate(previous, data, parent)
    BASE.BASE.need(blobs == compose(data, profile), 'exact MFA transition source')
    BASE.BASE.need({n for n in blobs if blobs[n] != previous[n]} == {G3.INPUT, TRANSPORT}, 'bounded two-file delta')
    for name in (G3.SERVICE, G3.CUSTODY, G3.POLICY, 'lib/stytch-identity.js', 'lib/stytch-projection.js', 'public/app.js', 'public/index.html'):
        BASE.BASE.need(blobs[name] == previous[name], 'frozen boundary '+name)
    G3.HISTORICAL.scan(blobs); G3.HISTORICAL.config_review(blobs)
    report.update(profile=profile, deployment_revision=REVISION,
        identity_acceptance_predicates='OWNER_ACCEPTED_PRECONTEXT_ONLY_TRANSITION',
        post_context_replacement='DENY_RETIRE', changed_runtime_files=[G3.INPUT, TRANSPORT],
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n: {'bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest(), 'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output, profile=PROFILES[0]):
    output=G3.HISTORICAL.safe_output(output); BASE.BASE.need(not output.exists(),'fresh output')
    data=G3.generation3_input(); blobs=compose(data,profile); report=validate(blobs,data,profile)
    for n,b in blobs.items():
        p=output/'source'/n; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}))
    return report

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True); p.add_argument('--profile',choices=PROFILES,default=PROFILES[0])
    a=p.parse_args(); build(a.output,a.profile)
