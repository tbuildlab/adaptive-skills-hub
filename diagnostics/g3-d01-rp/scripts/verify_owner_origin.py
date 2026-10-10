"""Versioned public-page Origin correction; no provider IO or authority."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('owner_origin_base',HERE/'scripts/verify_owner_form.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
PROFILE='LIVE_DIAGNOSTIC_NATIVE_OWNER_ORIGIN'
REVISION='g3-d01-owner-live-native-origin-v3'

def need(ok,why):
    if not ok:raise RuntimeError('OWNER_ORIGIN_BLOCKED: '+why)

def compose(data):
    blobs=BASE.compose(data)
    path=BASE.BASE.BASE.INPUT
    need(blobs[path].count(BASE.REVISION.encode())==2,'exact revision membership')
    blobs[path]=blobs[path].replace(BASE.REVISION.encode(),REVISION.encode())
    BASE.BASE.replace(blobs,'public/index.html','<meta name="referrer" content="no-referrer">',
        '<meta name="referrer" content="strict-origin">')
    return blobs

def validate(blobs,data):
    need(blobs==compose(data) and len(blobs)==19,'exact source')
    # All unchanged runtime/config/client bytes retain the parent's closed review.
    report=BASE.validate(BASE.compose(data),data)
    BASE.BASE.BASE.HISTORICAL.scan(blobs)
    need(blobs['vercel.json']==BASE.compose(data)['vercel.json'],'global privacy headers')
    need(blobs[BASE.BASE.BASE.SERVICE]==BASE.compose(data)[BASE.BASE.BASE.SERVICE],'exact server gates')
    need(blobs['public/owner-transient.js']==BASE.compose(data)['public/owner-transient.js'],'private channel')
    report.update(profile=PROFILE,deployment_revision=REVISION,
        zip_sha256=hashlib.sha256(BASE.BASE.BASE.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output):
    output=BASE.BASE.BASE.HISTORICAL.safe_output(output);need(not output.exists(),'fresh output')
    data=BASE.BASE.BASE.generation3_input();blobs=compose(data);report=validate(blobs,data)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(BASE.BASE.BASE.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);build(p.parse_args().output)
