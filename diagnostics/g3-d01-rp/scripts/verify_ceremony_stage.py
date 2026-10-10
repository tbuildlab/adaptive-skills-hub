"""Closed diagnostic ceremony stages; original server refusal predicates retained."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('ceremony_parent',HERE/'scripts/verify_mfa_transition.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3;TRANSPORT=BASE.TRANSPORT
PROFILES=('DISABLED_CEREMONY_STAGE','LIVE_DIAGNOSTIC_CEREMONY_STAGE')
REVISION='g3-d01-closed-ceremony-stage-v9'
ERRORS=('REQUEST_EMAIL_ALREADY_STARTED','REQUEST_TOTP_NO_PRIMARY','REQUEST_TOTP_ALREADY_FINAL','REQUEST_TOTP_CODE_SHAPE','REQUEST_MFA_NOT_FINAL')
STAGES=('CONTEXT_READY','EMAIL_SENT','OTP_VERIFIED','MFA_VERIFIED','RETIRED')
CLIENT=r'''
const stages=new Set(['CONTEXT_READY','EMAIL_SENT','OTP_VERIFIED','MFA_VERIFIED','RETIRED']);
function stageButtons(stage){
  const allowed=new Set(['LOCAL_LOGOUT','ACCOUNT_SWITCH']);
  if(stage==='CONTEXT_READY')allowed.add('EMAIL_OTP_SEND');
  if(stage==='EMAIL_SENT')allowed.add('EMAIL_OTP_AUTHENTICATE');
  if(stage==='OTP_VERIFIED')allowed.add('TOTP_AUTHENTICATE');
  if(stage==='MFA_VERIFIED')for(const action of ['PAGE','DECISION_POST_SIMULATION','RECEIPT_SIMULATION','INTENT_SIMULATION','CLAIM_SIMULATION','SESSION_REVOKE_EXACT'])allowed.add(action);
  for(const button of document.querySelectorAll('[data-action]'))button.disabled=!allowed.has(button.dataset.action);
}
'''
def put(blobs,name,old,new):BASE.BASE.BASE.replace(blobs,name,old,new)
def compose(data,profile=PROFILES[0]):
    BASE.BASE.BASE.need(profile in PROFILES,'ceremony profile')
    blobs=BASE.compose(data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    put(blobs,TRANSPORT,"if (input !== undefined || this.#method || this.#session) throw new ClosedFailure('REQUEST');",
        "if (input !== undefined) throw new ClosedFailure('REQUEST');\n    if (this.#method || this.#session) throw new ClosedFailure('REQUEST_EMAIL_ALREADY_STARTED');")
    put(blobs,TRANSPORT,"if (!this.#session || this.#two || !closed(input, ['code']) || typeof input.code !== 'string' || !/^\\d{6}$/.test(input.code)) throw new ClosedFailure('REQUEST');",
        "if (!this.#session) throw new ClosedFailure('REQUEST_TOTP_NO_PRIMARY');\n    if (this.#two) throw new ClosedFailure('REQUEST_TOTP_ALREADY_FINAL');\n    if (!closed(input, ['code']) || typeof input.code !== 'string' || !/^\\d{6}$/.test(input.code)) throw new ClosedFailure('REQUEST_TOTP_CODE_SHAPE');")
    put(blobs,TRANSPORT,"if (!this.#session || !this.#two || input !== undefined) throw new ClosedFailure('REQUEST'); await this.#recheck();",
        "if (!this.#session || !this.#two) throw new ClosedFailure('REQUEST_MFA_NOT_FINAL');\n    if (input !== undefined) throw new ClosedFailure('REQUEST'); await this.#recheck();")
    for name in (G3.POLICY,'public/app.js'):
        put(blobs,name,"'REQUEST', 'REGISTRATION'" if name==G3.POLICY else "'REQUEST','REGISTRATION'",
            "'REQUEST', "+', '.join(repr(e) for e in ERRORS)+", 'REGISTRATION'")
    put(blobs,G3.SERVICE,"res.end(JSON.stringify({ ...result, csrf, adapter_mode:",
        "const info=page?.backend?.contextInfo();\n      const ceremony_stage=!page||info?.retired?'RETIRED':info?.two?'MFA_VERIFIED':info?.primary?'OTP_VERIFIED':page.backend?'EMAIL_SENT':'CONTEXT_READY';\n      res.end(JSON.stringify({ ...result, ceremony_stage, csrf, adapter_mode:")
    put(blobs,'public/app.js',"function clearCodes()",CLIENT+'\nfunction clearCodes()')
    put(blobs,'public/app.js',"&&['PASS','DENY'].includes(value.result)&&classes.has(value.error_class);",
        "&&['PASS','DENY'].includes(value.result)&&classes.has(value.error_class)&&stages.has(value.ceremony_stage);")
    put(blobs,'public/app.js',"let result='DENY',error='MALFORMED_RESPONSE',expires=null;",
        "let result='DENY',error='MALFORMED_RESPONSE',expires=null,stage='RETIRED';")
    put(blobs,'public/app.js',"if(valid){\n    const exp=value.context_expires_at;",
        "if(valid){\n    stage=value.ceremony_stage;\n    const exp=value.context_expires_at;")
    put(blobs,'public/app.js',"else if(ok&&clockValid&&Number.isSafeInteger(exp)",
        "else if(ok&&stage!=='RETIRED'&&clockValid&&Number.isSafeInteger(exp)")
    put(blobs,'public/app.js',"status.textContent=controls.disabled?'Diagnostic retired or disabled':'Disposable diagnostic only — authority NONE';",
        "stageButtons(controls.disabled?'RETIRED':stage);\n  status.textContent=controls.disabled?'Diagnostic retired or disabled':'Disposable diagnostic only — '+stage+' — authority NONE';")
    put(blobs,'public/app.js',"evidence_source:'SANITIZED_DIAGNOSTIC_RESPONSE',context_expires_at:expires},null,2);",
        "evidence_source:'SANITIZED_DIAGNOSTIC_RESPONSE',ceremony_stage:controls.disabled?'RETIRED':stage,context_expires_at:expires},null,2);")
    return blobs
def validate(blobs,data,profile=PROFILES[0]):
    parent=BASE.PROFILES[0 if profile==PROFILES[0] else 1];previous=BASE.compose(data,parent)
    report=BASE.validate(previous,data,parent)
    BASE.BASE.BASE.need(blobs==compose(data,profile),'exact ceremony source')
    changed={G3.INPUT,G3.POLICY,G3.SERVICE,TRANSPORT,'public/app.js'}
    BASE.BASE.BASE.need({n for n in blobs if blobs[n]!=previous[n]}==changed,'five-file stage delta')
    for n in (G3.CUSTODY,'lib/stytch-identity.js','lib/stytch-projection.js','public/index.html'):
        BASE.BASE.BASE.need(blobs[n]==previous[n],'unchanged trust body '+n)
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    report.update(profile=profile,deployment_revision=REVISION,ceremony_stages=list(STAGES),ceremony_refusal_labels=list(ERRORS),
        changed_runtime_files=sorted(changed),zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report
def build(output,profile=PROFILES[0]):
    output=G3.HISTORICAL.safe_output(output);BASE.BASE.BASE.need(not output.exists(),'fresh output')
    data=G3.generation3_input();blobs=compose(data,profile);report=validate(blobs,data,profile)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--profile',choices=PROFILES,default=PROFILES[0]);a=p.parse_args();build(a.output,a.profile)
