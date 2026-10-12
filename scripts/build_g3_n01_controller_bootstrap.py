"""Closed additive bootstrap artifact, excludes all prior D01 diagnostic files.

No credential, public contact data, fixture or environment file is packaged.
This artifact cannot authenticate an Owner or enroll a source; it measures the
actual deployed source and reads the approved public review through native STS.
"""
import hashlib
import json
from pathlib import Path
import argparse
import subprocess

from ash import g3_delegated_control_codec as codec
from scripts.build_g3_n01_vercel_probe import MODULES

ROOT=Path(__file__).resolve().parents[1]
EXTRA=('ash/g3_n01_public_review.py','ash/g3_n01_public_pin.py','ash/g3_n01_owner_context.py',
    'ash/g3_n01_source_enrollment.py','ash/g3_n01_controller_bootstrap.py',
    'scripts/g3_n01_controller_bootstrap.py')


def build(destination):
    files={name:(ROOT/name).read_bytes().replace(b'\r\n',b'\n') for name in (*MODULES,*EXTRA)}
    # Transport's historic facade imports only these pure shared operations.
    files['scripts/g3_production_metadata.py']=b'from ash.g3_record_codec import canonical_bytes, parse_json, parse_metadata, domain_digest, MetadataError\n'
    locks={}
    for name in ('nexus-production-d03-sdk-requirements-v1.txt','nexus-production-n01-identity-sdk-requirements-v1.txt'):
        for line in (ROOT/'research'/name).read_text().splitlines():
            if line and not line.startswith('#'):
                key=line.split('==')[0];assert key not in locks or locks[key]==line;locks[key]=line
    files['requirements.txt']=('\n'.join(locks[key] for key in sorted(locks))+'\n').encode()
    files['.python-version']=b'3.12\n'
    files['index.html']=b'<!doctype html><html lang="en"><meta charset="utf-8"><title>N01 bootstrap</title><p>Protected bootstrap only. No Owner context or execution authority.</p></html>\n'
    files['vercel.json']=codec.canonical({'name':'nexus-g3-qual','functions':{'api/n01-controller.py':{'maxDuration':60}}})
    inventory={name:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for name,raw in sorted(files.items())}
    manifest=codec.canonical(inventory)
    files['source-inventory.json']=manifest
    files['api/n01-controller.py']=(
        'from pathlib import Path\nfrom http.server import BaseHTTPRequestHandler\n'
        'from scripts import g3_n01_controller_bootstrap as service\n'
        "service.ARTIFACT_ROOT=Path(__file__).resolve().parents[1]\n"
        'service.EXPECTED_MANIFEST_SHA='+repr(codec.digest(manifest))+'\n'
        'class handler(service.handler,BaseHTTPRequestHandler):\n    pass\n').encode()
    complete={name:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for name,raw in sorted(files.items())}
    digest=codec.digest(codec.canonical(complete))
    destination.mkdir(parents=True,exist_ok=True)
    source_head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    metadata=dict(schema_version='nexus.g3.n01.controller-bootstrap-artifact.v1',source_head=source_head,
        artifact_inventory_sha256=digest,files=complete,authority='NONE',real_admission='NO',
        maximum_explicit_invocations=8,maximum_s3_attempts_per_invocation=12,ddb_attempts=0)
    (destination/'artifact.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    request=dict(name='nexus-g3-qual',project='prj_xH23xMATVChdhX34OS2vjI8dfWN2',target='production',
        files=[dict(file=name,data=raw.decode(),encoding='utf-8') for name,raw in sorted(files.items())],
        meta={'n01Profile':'PUBLIC_REVIEW_BOOTSTRAP_ONLY','n01SourceHead':source_head,'n01ArtifactSha256':digest},
        projectSettings=dict(framework=None,buildCommand=None,outputDirectory=None,nodeVersion='24.x'))
    (destination/'exact-body.json').write_text(json.dumps(request),encoding='utf-8')
    snapshot=destination/'source'
    for name,raw in files.items():
        path=snapshot/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destination',type=Path,required=True)
    result=build(parser.parse_args().destination)
    print(json.dumps({key:result[key] for key in ('artifact_inventory_sha256','source_head','authority','real_admission')}))
