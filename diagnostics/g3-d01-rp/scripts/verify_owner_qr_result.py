"""Additive QR result projection; historical QR source and authority gates stay frozen."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('qr_result_base',HERE/'scripts/verify_owner_qr.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3
PROFILES=BASE.PROFILES
REVISION='g3-d01-owner-local-qr-result-v4'
CLIENT=BASE.CLIENT

def need(ok,why):
    if not ok:raise RuntimeError('OWNER_QR_RESULT_BLOCKED: '+why)

def compose(data,profile=PROFILES[0]):
    blobs=BASE.compose(data,profile)
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    blobs[CLIENT]=(HERE/'future-deployment/owner-transient-qr-result.js').read_bytes().replace(b'\r\n',b'\n')
    return blobs

def validate(blobs,data,profile=PROFILES[0]):
    previous=BASE.compose(data,profile)
    report=BASE.validate(previous,data,profile)
    need(blobs==compose(data,profile),'deterministic exact source')
    need({n for n in blobs if blobs[n]!=previous[n]}=={G3.INPUT,CLIENT},'bounded delta')
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    text=blobs[CLIENT].decode()
    for banned in ('console.','innerHTML','localStorage','sessionStorage','location.replace',
                   'navigator.clipboard','toDataURL','session_token','session_jwt','process.env'):
        need(banned not in text,'client boundary')
    need(text.count("fetch('/api/diagnostic'")==1,'fixed same-origin route')
    for n,b in blobs.items():
        if n.startswith('public/'):
            for value in (data['provider']['project_id'],data['provider']['owner_user_id'],data['provider']['delivery_email'],data['keyset']['source']):
                need(value.encode() not in b,'public identity disclosure')
    report.update(deployment_revision=REVISION,changed_runtime_files=[G3.INPUT,CLIENT],
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
