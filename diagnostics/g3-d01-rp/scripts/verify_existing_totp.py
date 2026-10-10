"""Additive code-only current-factor UI; all accepted server bytes stay frozen."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('existing_totp_base',HERE/'scripts/verify_owner_qr_result.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3
PROFILES=('DISABLED_EXISTING_TOTP','LIVE_DIAGNOSTIC_EXISTING_TOTP')
REVISION='g3-d01-existing-totp-code-v5'

def need(ok,why):
    if not ok:raise RuntimeError('EXISTING_TOTP_BLOCKED: '+why)

def compose(data,profile=PROFILES[0]):
    need(profile in PROFILES,'profile')
    blobs=BASE.compose(data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    old=b'<button data-action="TOTP_CREATE">Prepare transient TOTP</button>\n<button id="show-owner" type="submit" form="owner-channel-form">Display transient Owner channel</button>'
    new=b'<p>Use the current verified Owner authenticator with a fresh dynamic code. No new enrollment or QR is created.</p>\n<input id="totp-code" type="text" inputmode="numeric" maxlength="6" autocomplete="off" aria-label="Current Owner TOTP code">\n<button data-action="TOTP_AUTHENTICATE">Authenticate current TOTP</button>'
    need(blobs['public/index.html'].count(old)==1,'exact UI membership')
    blobs['public/index.html']=blobs['public/index.html'].replace(old,new)
    blobs['public/app.js']=(HERE/'future-deployment/owner-existing-totp.js').read_bytes().replace(b'\r\n',b'\n')
    return blobs

def validate(blobs,data,profile=PROFILES[0]):
    previous=BASE.compose(data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    report=BASE.validate(previous,data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    need(blobs==compose(data,profile),'exact deterministic source')
    need({n for n in blobs if blobs[n]!=previous[n]}=={G3.INPUT,'public/index.html','public/app.js'},'three-file delta')
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    text=blobs['public/app.js'].decode()
    for banned in ('console.','innerHTML','localStorage','sessionStorage','process.env',
                   'session_token','session_jwt','TOTP_CREATE','navigator.clipboard'):
        need(banned not in text,'fixed client boundary')
    need(text.count('fetch(')==text.count("fetch('/api/diagnostic'")==1,'fixed same-origin route')
    for n,b in blobs.items():
        if n.startswith('public/'):
            for value in (data['provider']['project_id'],data['provider']['owner_user_id'],data['provider']['delivery_email'],data['keyset']['source']):
                need(value.encode() not in b,'public registration disclosure')
    report.update(profile=profile,deployment_revision=REVISION,changed_runtime_files=[G3.INPUT,'public/index.html','public/app.js'],
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
