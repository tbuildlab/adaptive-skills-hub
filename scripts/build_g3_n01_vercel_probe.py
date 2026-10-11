"""Assemble one additive read-only runtime probe over the accepted D01 ZIP.

No secret discovery, environment pull, provider call or credential value access.
The prior 20 files are verified against their accepted exact artifact identities.
Only vercel.json is extended with the separately reviewed Python function.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PRIOR_SHA='cafe90c51568635e83e364750b3ed52ffaac64e32b99a9d8d6a18291de75de4d'
MODULES=('ash/__init__.py','ash/capabilities.py','ash/ecosystem_models.py',
    'ash/g1_profiles.py','ash/evaluation.py','ash/g3_proposal_codec.py',
    'ash/g3_checkpoint_custody.py','ash/g3_control_codec.py',
    'ash/g3_control_semantics.py','ash/g3_delegated_control_codec.py','ash/g3_delegated_record_codec.py',
    'ash/g3_record_codec.py','ash/g3_grant_codec.py','ash/g3_primary_ledger.py',
    'ash/g3_transition_protocol.py','scripts/g3_d03_s3_fence.py',
    'scripts/g3_production_metadata.py')


def build(prior_zip, destination):
    raw=prior_zip.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PRIOR_SHA:raise ValueError('PRIOR_ARTIFACT_MISMATCH')
    with zipfile.ZipFile(prior_zip) as archive:
        files={entry.filename:archive.read(entry) for entry in archive.infolist()}
    if len(files)!=20 or any(name.startswith('/') or '..' in Path(name).parts for name in files):
        raise ValueError('PRIOR_INVENTORY_MISMATCH')
    original={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
    config=json.loads(files['vercel.json'])
    config['functions']['api/n01-storage.py']={'maxDuration':60,'excludeFiles':'{public/**,lib/**,api/diagnostic.js}'}
    files['vercel.json']=(json.dumps(config,indent=2)+'\n').encode()
    for name in MODULES:
        files[name]=(ROOT/name).read_bytes().replace(b'\r\n',b'\n')
    files['api/n01-storage.py']=(ROOT/'scripts/g3_n01_vercel_probe.py').read_bytes().replace(b'\r\n',b'\n')
    files['requirements.txt']=(ROOT/'research/nexus-production-d03-sdk-requirements-v1.txt').read_bytes().replace(b'\r\n',b'\n')
    files['.python-version']=b'3.12\n'
    destination.mkdir(parents=True,exist_ok=True)
    archive_path=destination/'n01-vercel-probe.zip'
    with zipfile.ZipFile(archive_path,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,11,0,0,0));info.external_attr=0o100644<<16
            archive.writestr(info,data)
    inventory={name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in sorted(files.items())}
    metadata=dict(schema_version='nexus.g3.n01.vercel-probe-artifact.v1',
        source_head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
        prior_zip_sha256=PRIOR_SHA,prior_unchanged_files=sum(inventory[name]['sha256']==sha for name,sha in original.items()),
        authority='NONE',real_admission='NO',profile='TEST_ONLY_READ_ONLY_RUNTIME_FEDERATION',
        reserved_ddb_attempts=16,maximum_explicit_invocations=8,files=inventory,
        zip_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest())
    (destination/'artifact.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    request=dict(requestBody=dict(name='nexus-g3-qual',project='prj_xH23xMATVChdhX34OS2vjI8dfWN2',target='production',
        files=[dict(file=name,data=data.decode('utf-8'),encoding='utf-8') for name,data in sorted(files.items())],
        meta={'n01Profile':metadata['profile'],'n01SourceHead':metadata['source_head'],
              'n01ArtifactSha256':metadata['zip_sha256']},
        projectSettings=dict(framework=None,buildCommand=None,outputDirectory='public',nodeVersion='24.x')))
    (destination/'create-request.json').write_text(json.dumps(request),encoding='utf-8')
    return metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prior-zip',type=Path,required=True)
    parser.add_argument('--destination',type=Path,required=True);args=parser.parse_args()
    result=build(args.prior_zip,args.destination)
    print(json.dumps({key:result[key] for key in ('zip_sha256','source_head','prior_unchanged_files','reserved_ddb_attempts')}))
