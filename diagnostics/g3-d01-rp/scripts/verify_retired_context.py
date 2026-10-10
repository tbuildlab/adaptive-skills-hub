"""Clear an already-retired diagnostic cookie; never restore its context."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('retired_parent',HERE/'scripts/verify_lifecycle_evidence.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3
PROFILES=('DISABLED_RETIRED_CONTEXT','LIVE_DIAGNOSTIC_RETIRED_CONTEXT')
REVISION='g3-d01-retired-context-v11'
def compose(data,profile=PROFILES[0]):
    G3.HISTORICAL.need(profile in PROFILES,'retired profile')
    blobs=BASE.compose(data,BASE.PROFILES[0 if profile==PROFILES[0] else 1])
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    BASE.BASE.put(blobs,G3.SERVICE,"const reply = (status, result, csrf = null) => {",r'''const reply = (status, result, csrf = null) => {
      // Key was parsed only after route/origin/time checks. Clear only a retired
      // diagnostic cookie. This response cannot create or restore any context.
      if (key && !page) res.setHeader('Set-Cookie',`${COOKIE}=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0`);''')
    return blobs
def validate(blobs,data,profile=PROFILES[0]):
    parent=BASE.PROFILES[0 if profile==PROFILES[0] else 1];previous=BASE.compose(data,parent)
    report=BASE.validate(previous,data,parent)
    G3.HISTORICAL.need(blobs==compose(data,profile),'exact retired source')
    G3.HISTORICAL.need({n for n in blobs if blobs[n]!=previous[n]}=={G3.INPUT,G3.SERVICE},'two-file retired delta')
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    report.update(profile=profile,deployment_revision=REVISION,changed_runtime_files=[G3.INPUT,G3.SERVICE],
        retired_cookie_recovery='DENY_CLEAR_THEN_SEPARATE_FRESH_REQUEST',
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report
def build(output,profile=PROFILES[0]):
    output=G3.HISTORICAL.safe_output(output);G3.HISTORICAL.need(not output.exists(),'fresh output')
    data=G3.generation3_input();blobs=compose(data,profile);report=validate(blobs,data,profile)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--profile',choices=PROFILES,default=PROFILES[0]);a=p.parse_args();build(a.output,a.profile)
