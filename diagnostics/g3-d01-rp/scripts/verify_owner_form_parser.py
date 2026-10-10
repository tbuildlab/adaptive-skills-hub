"""Versioned exact Owner-form decoder; no credentials, network or authority."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('owner_parser_base', HERE/'scripts/verify_owner_origin.py')
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
G3 = BASE.BASE.BASE.BASE
PROFILE = 'LIVE_DIAGNOSTIC_OWNER_FORM_PARSER'
REVISION = 'g3-d01-owner-live-form-parser-v3'
DECODER = """// Fixed transport decoder, never a Principal/schema/authority relaxation.
export function decodeOwnerDisplayForm(input) {
  let form=input;
  if(typeof form==='string') {
    if(Buffer.byteLength(form)>1024) throw new ClosedFailure('REQUEST_FORM_SIZE');
    const entries=[...new URLSearchParams(form)];
    if(entries.length!==2||new Set(entries.map(([k])=>k)).size!==2) throw new ClosedFailure('REQUEST_FORM_SCHEMA');
    form=Object.fromEntries(entries);
  }
  if(form===null||typeof form!=='object'||Array.isArray(form)) throw new ClosedFailure('REQUEST_FORM_SCHEMA');
  const prototype=Object.getPrototypeOf(form);
  if(prototype!==null&&prototype!==Object.prototype) throw new ClosedFailure('REQUEST_FORM_SCHEMA');
  const keys=Reflect.ownKeys(form);
  if(keys.length!==2||!keys.includes('action')||!keys.includes('csrf')) throw new ClosedFailure('REQUEST_FORM_SCHEMA');
  const action=Object.getOwnPropertyDescriptor(form,'action'), csrf=Object.getOwnPropertyDescriptor(form,'csrf');
  if(!action||!csrf||!action.enumerable||!csrf.enumerable||!Object.hasOwn(action,'value')||!Object.hasOwn(csrf,'value')
      ||typeof action.value!=='string'||typeof csrf.value!=='string') throw new ClosedFailure('REQUEST_FORM_SCHEMA');
  const normalized={action:action.value,csrf:csrf.value};
  if(Buffer.byteLength(new URLSearchParams(normalized).toString())>1024) throw new ClosedFailure('REQUEST_FORM_SIZE');
  if(normalized.action!=='OWNER_TOTP_DISPLAY') throw new ClosedFailure('REQUEST_FORM_SCHEMA');
  return normalized;
}
"""

def need(ok, why):
    if not ok: raise RuntimeError('OWNER_FORM_PARSER_BLOCKED: '+why)

def compose(data):
    blobs=BASE.compose(data)
    need(blobs[G3.INPUT].count(BASE.REVISION.encode())==2,'revision membership')
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    replace=BASE.BASE.BASE.replace
    replace(blobs,G3.SERVICE,'function buildHandler(factory, clock, fixture) {',DECODER+'function buildHandler(factory, clock, fixture) {')
    old="""        let form=req.body;
        if(typeof form==='string') {
          if(Buffer.byteLength(form)>1024) throw new ClosedFailure('REQUEST');
          const entries=[...new URLSearchParams(form)];
          if(entries.length!==2 || new Set(entries.map(([k])=>k)).size!==2) throw new ClosedFailure('REQUEST');
          form=Object.fromEntries(entries);
        }
        if(!closed(form,['action','csrf'])||form.action!=='OWNER_TOTP_DISPLAY'||!equal(form.csrf,page.csrf)) throw new ClosedFailure('REQUEST');"""
    replace(blobs,G3.SERVICE,old,"        const form=decodeOwnerDisplayForm(req.body);\n        if(!equal(form.csrf,page.csrf)) throw new ClosedFailure('REQUEST_FORM_CSRF');")
    replace(blobs,G3.POLICY,"'REQUEST_BUSY'","'REQUEST_BUSY', 'REQUEST_FORM_SCHEMA', 'REQUEST_FORM_SIZE', 'REQUEST_FORM_CSRF'")
    return blobs

def validate(blobs,data):
    need(blobs==compose(data) and len(blobs)==19,'exact closed source')
    report=BASE.validate(BASE.compose(data),data)
    G3.HISTORICAL.scan(blobs); G3.HISTORICAL.config_review(blobs)
    need({n for n,b in blobs.items() if b!=BASE.compose(data)[n]}=={G3.INPUT,G3.SERVICE,G3.POLICY},'three-file delta')
    for n in ('vercel.json','public/index.html','public/app.js','public/owner-transient.js'):
        need(blobs[n]==BASE.compose(data)[n],'privacy/client bytes')
    report.update(profile=PROFILE,deployment_revision=REVISION,
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output):
    output=G3.HISTORICAL.safe_output(output); need(not output.exists(),'fresh output')
    data=G3.generation3_input(); blobs=compose(data); report=validate(blobs,data)
    for n,b in blobs.items():
        p=output/'source'/n; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')})); return report

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True); build(p.parse_args().output)
