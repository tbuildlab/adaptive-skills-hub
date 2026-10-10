"""Additive, diagnostic-only completion evidence and exact revoked-session recheck."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('lifecycle_parent',HERE/'scripts/verify_ceremony_stage.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3;TRANSPORT=BASE.TRANSPORT
PROFILES=('DISABLED_LIFECYCLE_EVIDENCE','LIVE_DIAGNOSTIC_LIFECYCLE_EVIDENCE')
REVISION='g3-d01-lifecycle-evidence-v10'

def compose(data,profile=PROFILES[0]):
    BASE.BASE.BASE.BASE.need(profile in PROFILES,'lifecycle profile')
    blobs=BASE.compose(data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    def put(name,old,new):BASE.put(blobs,name,old,new)
    put(TRANSPORT,'function parseBytes(chunks, contentLength) {','function parseBytes(chunks, contentLength, expectedStatus = 200) {')
    put(TRANSPORT,'body.status_code !== 200','body.status_code !== expectedStatus')
    put(TRANSPORT,'function nativeExchange(options, bytes, primitive = httpsRequest) {',r'''function rejectedBody(chunks, length) {
  const body = parseBytes(chunks, length, 404);
  const allowed = new Set(['status_code', 'error_type', 'request_id', 'error_message', 'error_url']);
  if (Object.keys(body).some(k => !allowed.has(k)) || body.error_type !== 'session_not_found')
    throw new ClosedFailure('SESSION_INVALID');
  return Object.freeze({ rejection: 'SESSION_NOT_FOUND' });
}
function nativeExchange(options, bytes, primitive = httpsRequest, expectedRejection = false) {''')
    put(TRANSPORT,'try { headerCheck(res.statusCode, res.headers); }',r'''try {
          if (expectedRejection && res.statusCode !== 404)
            throw new ClosedFailure(res.statusCode === 200 ? 'SESSION_INVALID' : failureForStatus(res.statusCode));
          headerCheck(expectedRejection ? 200 : res.statusCode, res.headers);
        }''')
    put(TRANSPORT,"finish(null, parseBytes(chunks, res.headers['content-length']));","finish(null, expectedRejection ? rejectedBody(chunks, res.headers['content-length']) : parseBytes(chunks, res.headers['content-length']));")
    put(TRANSPORT,'async #exchange(op, body) {','async #exchange(op, body, expectedRejection = false) {')
    put(TRANSPORT,'if (this.#native) return nativeExchange(options, bytes);','if (this.#native) return nativeExchange(options, bytes, httpsRequest, expectedRejection);')
    put(TRANSPORT,'return nativeExchange(options, bytes, fixturePrimitive(reply));','return nativeExchange(options, bytes, fixturePrimitive(reply), expectedRejection);')
    put(TRANSPORT,'    headerCheck(reply.status, reply.headers);',r'''    if (expectedRejection && reply.status !== 404) throw new ClosedFailure('SESSION_INVALID');
    headerCheck(expectedRejection ? 200 : reply.status, reply.headers);''')
    put(TRANSPORT,"return parseBytes(reply.chunks, reply.headers['content-length']);","return expectedRejection ? rejectedBody(reply.chunks, reply.headers['content-length']) : parseBytes(reply.chunks, reply.headers['content-length']);")
    put(TRANSPORT,'this.#busy = true;\n    try { this.#check(); await work();', 'this.#busy = true;\n    try { this.#check(); const observation = await work();')
    put(TRANSPORT,"const result = safeResult('NONE', true, !this.#native);", "const result = Object.freeze({ ...safeResult('NONE', true, !this.#native), ...(observation === 'REMOTE_REJECTION_CONFIRMED' ? { revoke_observation: observation } : {}) });")
    put(TRANSPORT,"await this.#exchange('SESSION_REVOKE_EXACT', { session_id: this.#session.session_id }); this.retire();",r'''// Retained bearer is used privately for one negative remote check only.
    // A revoke acknowledgment, 401, timeout, 5xx or generic 404 cannot pass.
    await this.#recheck(); this.#check();
    await this.#exchange('SESSION_REVOKE_EXACT', { session_id: this.#session.session_id });
    this.#check();
    const denied = await this.#exchange('SESSION_AUTHENTICATE', { session_token: this.#token }, true);
    this.#check();
    if (denied.rejection !== 'SESSION_NOT_FOUND') throw new ClosedFailure('SESSION_INVALID');
    this.retire(); return 'REMOTE_REJECTION_CONFIRMED';''')
    put(G3.SERVICE,'let key = null; let page = null;','let key = null; let page = null; let completed_action = null; let completed_points = 0;')
    put(G3.SERVICE,'...result, ceremony_stage, csrf, adapter_mode:',"...result, ceremony_stage, completed_action: result.result === 'PASS' ? completed_action : null, completed_points, revoke_observation: result.result === 'PASS' && result.revoke_observation === 'REMOTE_REJECTION_CONFIRMED' ? 'REMOTE_REJECTION_CONFIRMED' : 'NOT_CONFIRMED', csrf, adapter_mode:")
    put(G3.SERVICE,'      const info=page.backend.contextInfo();',"      if (result.result === 'PASS') { completed_action = action; completed_points = page.point; }\n      const info=page.backend.contextInfo();")
    put('public/app.js',"&&stages.has(value.ceremony_stage);",r'''&&stages.has(value.ceremony_stage)
    &&(value.completed_action===null||['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE','PAGE','DECISION_POST_SIMULATION','RECEIPT_SIMULATION','INTENT_SIMULATION','CLAIM_SIMULATION','SESSION_REVOKE_EXACT'].includes(value.completed_action))
    &&Number.isInteger(value.completed_points)&&value.completed_points>=0&&value.completed_points<=5
    &&['NOT_CONFIRMED','REMOTE_REJECTION_CONFIRMED'].includes(value.revoke_observation);''')
    put('public/app.js',"evidence_source:'SANITIZED_DIAGNOSTIC_RESPONSE',ceremony_stage:",r'''evidence_source:'SANITIZED_DIAGNOSTIC_RESPONSE',
    completed_action:valid?value.completed_action:null,completed_points:valid?value.completed_points:0,
    operation_result:valid?value.result:'DENY',
    revoke_observation:valid&&value.result==='PASS'&&value.completed_action==='SESSION_REVOKE_EXACT'&&stage==='RETIRED'&&value.context_expires_at===null&&value.csrf===null?value.revoke_observation:'NOT_CONFIRMED',
    ceremony_stage:''')
    # Clear stale completed evidence synchronously, before any asynchronous IO.
    put('public/app.js','  busy=true;controls.disabled=true;',r'''  busy=true;controls.disabled=true;
  evidence.textContent=JSON.stringify({diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',qualified_live:false,result:'DENY',error_class:'NONE',ceremony_stage:'RETIRED',context_expires_at:null,completed_action:null,completed_points:0,operation_result:'DENY',revoke_observation:'NOT_CONFIRMED',request_pending:true});''')
    return blobs

def validate(blobs,data,profile=PROFILES[0]):
    parent=BASE.PROFILES[0 if profile==PROFILES[0] else 1]
    previous=BASE.compose(data,parent);report=BASE.validate(previous,data,parent)
    BASE.BASE.BASE.BASE.need(blobs==compose(data,profile),'exact lifecycle evidence source')
    changed={G3.INPUT,G3.SERVICE,TRANSPORT,'public/app.js'}
    BASE.BASE.BASE.BASE.need({n for n in blobs if blobs[n]!=previous[n]}==changed,'four-file lifecycle delta')
    for n in (G3.CUSTODY,G3.POLICY,'lib/stytch-identity.js','lib/stytch-projection.js','public/index.html'):
        BASE.BASE.BASE.BASE.need(blobs[n]==previous[n],'frozen boundary '+n)
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    report.update(profile=profile,deployment_revision=REVISION,changed_runtime_files=sorted(changed),
        completion_evidence='CLOSED_NON_AUTHORITATIVE',revoked_session_check='EXACT_404_SESSION_NOT_FOUND_ONLY',
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output,profile=PROFILES[0]):
    output=G3.HISTORICAL.safe_output(output);BASE.BASE.BASE.BASE.need(not output.exists(),'fresh output')
    data=G3.generation3_input();blobs=compose(data,profile);report=validate(blobs,data,profile)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--profile',choices=PROFILES,default=PROFILES[0]);a=p.parse_args();build(a.output,a.profile)
