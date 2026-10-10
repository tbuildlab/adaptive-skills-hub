"""Fixed identity-denial labels only; no acceptance predicate or custody change."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('identity_stage_base',HERE/'scripts/verify_existing_totp.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3
PROFILES=('DISABLED_IDENTITY_STAGE','LIVE_DIAGNOSTIC_IDENTITY_STAGE')
REVISION='g3-d01-identity-denial-stage-v6'
TRANSPORT='lib/server/stytch-transport.js'
ERRORS=('IDENTITY_JWT_SHAPE','IDENTITY_JWT_JSON','IDENTITY_SIGNED_PROOF','IDENTITY_TOKEN_SHAPE',
        'IDENTITY_SESSION_CONTINUITY','IDENTITY_TOKEN_CONTINUITY','IDENTITY_PRIMARY_TIME',
        'IDENTITY_OTP_RESPONSE','IDENTITY_TOTP_RESPONSE')
OLD=r'''    if(typeof body.session_jwt!=='string'||body.session_jwt.length>16384)throw new ClosedFailure('IDENTITY');
    try {
      for(const part of body.session_jwt.split('.').slice(0,2))uniqueJson(new TextDecoder('utf-8',{fatal:true}).decode(Buffer.from(part,'base64url')));
    } catch { throw new ClosedFailure('IDENTITY'); }
    if (!verifyStytchIdentity(body.session_jwt, p, session.user_id, this.#keys, now)
        || typeof body.session_token !== 'string'
        || !(this.#native ? /^[\x21-\x7e]{1,2048}$/.test(body.session_token) : /^OFFLINE_[A-Z0-9_]{1,128}$/.test(body.session_token))) throw new ClosedFailure('IDENTITY');
    if (same && (session.session_id !== this.#session.session_id || session.user_id !== this.#session.user_id
        || body.session_token !== this.#token || session.factors[0].at !== this.#session.factors[0].at)) throw new ClosedFailure('IDENTITY');'''
NEW=r'''    if(typeof body.session_jwt!=='string'||body.session_jwt.length>16384)throw new ClosedFailure('IDENTITY_JWT_SHAPE');
    try {
      for(const part of body.session_jwt.split('.').slice(0,2))uniqueJson(new TextDecoder('utf-8',{fatal:true}).decode(Buffer.from(part,'base64url')));
    } catch { throw new ClosedFailure('IDENTITY_JWT_JSON'); }
    if (!verifyStytchIdentity(body.session_jwt, p, session.user_id, this.#keys, now)) throw new ClosedFailure('IDENTITY_SIGNED_PROOF');
    if (typeof body.session_token !== 'string'
        || !(this.#native ? /^[\x21-\x7e]{1,2048}$/.test(body.session_token) : /^OFFLINE_[A-Z0-9_]{1,128}$/.test(body.session_token))) throw new ClosedFailure('IDENTITY_TOKEN_SHAPE');
    if (same && (session.session_id !== this.#session.session_id || session.user_id !== this.#session.user_id)) throw new ClosedFailure('IDENTITY_SESSION_CONTINUITY');
    if (same && body.session_token !== this.#token) throw new ClosedFailure('IDENTITY_TOKEN_CONTINUITY');
    if (same && session.factors[0].at !== this.#session.factors[0].at) throw new ClosedFailure('IDENTITY_PRIMARY_TIME');'''

def need(ok,why):
    if not ok:raise RuntimeError('IDENTITY_STAGE_BLOCKED: '+why)

def replace(blobs,name,old,new):
    old,new=old.encode(),new.encode();need(blobs[name].count(old)==1,'exact membership '+name)
    blobs[name]=blobs[name].replace(old,new)

def compose(data,profile=PROFILES[0]):
    need(profile in PROFILES,'profile')
    blobs=BASE.compose(data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    replace(blobs,TRANSPORT,OLD,NEW)
    replace(blobs,TRANSPORT,
        "if (b.method_id !== this.#method || b.user_id !== registrationRecord(this.#registration).owner_user_id) throw new ClosedFailure('IDENTITY');",
        "if (b.method_id !== this.#method || b.user_id !== registrationRecord(this.#registration).owner_user_id) throw new ClosedFailure('IDENTITY_OTP_RESPONSE');")
    replace(blobs,TRANSPORT,
        "|| (this.#totp && this.#totp.totp_id !== b.totp_id)) throw new ClosedFailure('IDENTITY');",
        "|| (this.#totp && this.#totp.totp_id !== b.totp_id)) throw new ClosedFailure('IDENTITY_TOTP_RESPONSE');")
    for name in (G3.POLICY,'public/app.js'):
        old="'IDENTITY', 'FACTORS'" if name==G3.POLICY else "'IDENTITY','FACTORS'"
        replace(blobs,name,old,"'IDENTITY', "+', '.join(repr(e) for e in ERRORS)+", 'FACTORS'")
    return blobs

def validate(blobs,data,profile=PROFILES[0]):
    parent_profile=BASE.PROFILES[0 if profile==PROFILES[0] else 1]
    previous=BASE.compose(data,parent_profile);report=BASE.validate(previous,data,parent_profile)
    need(blobs==compose(data,profile),'exact deterministic source')
    need({n for n in blobs if blobs[n]!=previous[n]}=={G3.INPUT,G3.POLICY,TRANSPORT,'public/app.js'},'four-file delta')
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    need(blobs[G3.SERVICE]==previous[G3.SERVICE],'unchanged HTTP gates')
    need(blobs['lib/stytch-identity.js']==previous['lib/stytch-identity.js'],'unchanged signature predicates')
    need(blobs['lib/stytch-projection.js']==previous['lib/stytch-projection.js'],'unchanged factor/session predicates')
    need(blobs[G3.CUSTODY]==previous[G3.CUSTODY],'unchanged credential custody')
    report.update(profile=profile,deployment_revision=REVISION,identity_error_classes=list(ERRORS),
        changed_runtime_files=[G3.INPUT,G3.POLICY,TRANSPORT,'public/app.js'],
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output,profile=PROFILES[0]):
    output=G3.HISTORICAL.safe_output(output);need(not output.exists(),'fresh output')
    data=G3.generation3_input();blobs=compose(data,profile);report=validate(blobs,data,profile)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--profile',choices=PROFILES,default=PROFILES[0]);a=p.parse_args();build(a.output,a.profile)
