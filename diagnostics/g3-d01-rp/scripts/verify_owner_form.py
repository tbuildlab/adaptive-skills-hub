"""Versioned native Owner form; exact source only, no provider or credentials."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('native_owner_form_base',HERE/'scripts/verify_request_stage.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
PROFILE='LIVE_DIAGNOSTIC_NATIVE_OWNER_FORM'
REVISION='g3-d01-owner-live-native-form-v3'

def need(ok,why):
    if not ok:raise RuntimeError('OWNER_FORM_BLOCKED: '+why)
def compose(data):
    need(data==BASE.BASE.reviewed_public_input(),'exact reviewed input')
    blobs=BASE.compose(data)
    input_path=BASE.BASE.INPUT
    need(blobs[input_path].count(BASE.REVISION.encode())==2,'revision membership')
    blobs[input_path]=blobs[input_path].replace(BASE.REVISION.encode(),REVISION.encode())
    BASE.replace(blobs,'public/index.html','<button id="show-owner">Display transient Owner channel</button>',
        '<button id="show-owner" type="submit" form="owner-channel-form">Display transient Owner channel</button>')
    BASE.replace(blobs,'public/index.html','<pre id="evidence"></pre>',
        '<form id="owner-channel-form" method="POST" action="/api/diagnostic">\n'
        '<input type="hidden" name="action" value="OWNER_TOTP_DISPLAY">\n'
        '<input id="owner-channel-csrf" type="hidden" name="csrf" value="">\n'
        '</form><pre id="evidence"></pre>')
    BASE.replace(blobs,'public/app.js',"const controls=document.getElementById('operations');",
        "const controls=document.getElementById('operations');\n"
        "const ownerForm=document.getElementById('owner-channel-form'), ownerCsrf=document.getElementById('owner-channel-csrf');")
    BASE.replace(blobs,'public/app.js',"const value=await res.json();csrf=typeof value.csrf==='string'?value.csrf:null;",
        "const value=await res.json();csrf=typeof value.csrf==='string'?value.csrf:null;\n    ownerCsrf.value=csrf??'';")
    BASE.replace(blobs,'public/app.js',"} catch { csrf=null; controls.disabled=true; evidence.textContent='DENY / UNKNOWN'; }",
        "} catch { csrf=null; ownerCsrf.value=''; controls.disabled=true; evidence.textContent='DENY / UNKNOWN'; }")
    old="""document.getElementById('show-owner').addEventListener('click',()=>{
  if(controls.disabled||location.origin!==origin) return;
  const form=document.createElement('form');form.method='POST';form.action='/api/diagnostic';form.hidden=true;
  for(const [name,value] of [['action','OWNER_TOTP_DISPLAY'],['csrf',csrf??'']]) {
    const input=document.createElement('input');input.type='hidden';input.name=name;input.value=value;form.append(input);
  }
  document.body.append(form);form.submit();
});"""
    # Literal fixed CSRF grammar, unrelated to OTP or bearer material.
    new="""// Native same-origin POST; no scripted navigation, HTML parsing or secret URL.
ownerForm.addEventListener('submit',event=>{
  if(busy||controls.disabled||location.origin!==origin||!/^[a-f0-9]{64}$/.test(csrf??'')) {
    event.preventDefault();return;
  }
  ownerCsrf.value=csrf;busy=true;controls.disabled=true;
});"""
    BASE.replace(blobs,'public/app.js',old,new)
    return blobs

def validate(blobs,data):
    need(blobs==compose(data) and len(blobs)==19,'exact closed source')
    BASE.BASE.HISTORICAL.scan(blobs);BASE.BASE.HISTORICAL.config_review(blobs)
    for name,blob in blobs.items():
        if not name.endswith('.js'):continue
        text=blob.decode()
        need(not re.search(r'\bimport\s*\(|\brequire\s*\(|\beval\s*\(|\bconsole\s*\.',text),'dynamic import/logging')
        for declaration in re.findall(r'(?m)^\s*import\b[^;]+;',text):
            literals=re.findall(r"['\"]([^'\"]+)['\"]",declaration);need(len(literals)==1,'unambiguous import')
            target=literals[0]
            if target.startswith('node:'):continue
            need(target.startswith('.'),'third-party module');parts=[]
            for part in (PurePosixPath(name).parent/target).parts:
                if part=='..':need(bool(parts),'import escape');parts.pop()
                elif part!='.':parts.append(part)
            need('/'.join(parts) in blobs,'closed import')
        if name.startswith('public/'):
            need(not re.search(r'lib/server|process\.env|STYTCH_SECRET|session_token|session_jwt|localStorage|sessionStorage|innerHTML|DOMParser|document\.write|\.submit\(',text),'client boundary')
            for value in (data['provider']['project_id'],data['provider']['owner_user_id'],data['provider']['delivery_email'],data['keyset']['source']):
                need(value.encode() not in blob,'public identity')
    need(blobs[BASE.BASE.SERVICE]==BASE.compose(data)[BASE.BASE.SERVICE],'server one-use channel unchanged')
    return {'profile':PROFILE,'files':19,'application_generation':3,'registration_generation':3,
        'deployment_revision':REVISION,'authority':'NONE','real_admission_enabled':'NO',
        'zip_sha256':hashlib.sha256(BASE.BASE.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        'public_review_valid_from':data['keyset']['valid_from'],'public_review_valid_until':data['keyset']['valid_until'],
        'provider_calls_performed_by_builder':0,'credential_access_by_builder':'NONE',
        'files_sha256':{n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())}}
def build(output):
    output=BASE.BASE.HISTORICAL.safe_output(output);need(not output.exists(),'fresh output')
    data=BASE.BASE.generation3_input();blobs=compose(data);report=validate(blobs,data);source=output/'source';source.mkdir(parents=True)
    for n,b in blobs.items():
        path=source/n;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(BASE.BASE.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);build(p.parse_args().output)
