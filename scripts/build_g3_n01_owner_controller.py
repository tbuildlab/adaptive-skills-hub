"""Build the closed native Owner-only artifact, without operator credential reads."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from ash import g3_delegated_control_codec as codec
from scripts.build_g3_n01_vercel_probe import MODULES
from scripts.build_g3_n01_controller_bootstrap import EXTRA

ROOT=Path(__file__).resolve().parents[1]
OWNER_MODULES=('ash/g3_n01_native_transport.py','ash/g3_n01_membership_custody.py','ash/g3_n01_retained_state.py',
    'ash/g3_n01_owner_state.py','ash/g3_n01_owner_protocol.py','ash/g3_n01_owner_persistence.py',
    'ash/g3_n01_owner_ingress.py','ash/g3_n01_runtime_context.py','ash/g3_n01_stytch_transport.py',
    'ash/g3_n02_presentation.py','scripts/g3_n01_owner_controller.py','ash/g3_n01_owner_restart.py','ash/g3_n01_owner_sdk_restart.py','ash/g3_n01_owner_atomic_restart.py')


def build(destination,*,delivery_email_sha256,transport_revision=1,restart_profile=None,review_generation=1):
    from ash import g3_n01_public_review as review
    selected=review.select_pins(review_generation,restart_profile=restart_profile)
    if review_generation==2 and restart_profile not in ('OWNER_SDK_REPAIR_FORWARD_V1','OWNER_ATOMIC_FORWARD_V1'):raise ValueError('N01_REVIEW_PROFILE_DENY')
    codec.old.check_type(delivery_email_sha256,'h')
    if type(transport_revision) is not int or transport_revision not in (1,2,3):raise ValueError('N01_TRANSPORT_REVISION_DENY')
    from ash import g3_n01_owner_restart as restart
    restart.require_profile(restart_profile)
    restart=restart.configuration(restart_profile)
    atomic=restart_profile=='OWNER_ATOMIC_FORWARD_V1'
    ddb_limit=210 if atomic else 280 if restart_profile=='OWNER_SDK_REPAIR_FORWARD_V1' else 190
    s3_limit=16000 if atomic else 10000 if restart_profile=='OWNER_SDK_REPAIR_FORWARD_V1' else 6000
    if restart_profile is not None and transport_revision!=3:raise ValueError('N01_RESTART_TRANSPORT_DENY')
    names=tuple(dict.fromkeys((*MODULES,*(name for name in EXTRA if name!='scripts/g3_n01_controller_bootstrap.py'),*OWNER_MODULES)))
    files={name:(ROOT/name).read_bytes().replace(b'\r\n',b'\n') for name in names}
    files['scripts/g3_production_metadata.py']=b'from ash.g3_record_codec import canonical_bytes, parse_json, parse_metadata, domain_digest, MetadataError\n'
    locks={}
    for name in ('nexus-production-d03-sdk-requirements-v1.txt','nexus-production-n01-identity-sdk-requirements-v1.txt'):
        for line in (ROOT/'research'/name).read_text().splitlines():
            if line and not line.startswith('#'):
                key=line.split('==')[0];assert key not in locks or locks[key]==line;locks[key]=line
    files['requirements.txt']=('\n'.join(locks[key] for key in sorted(locks))+'\n').encode()
    files['.python-version']=b'3.12\n'
    files['index.html']=b'<!doctype html><html lang="en"><meta charset="utf-8"><title>N01 Owner qualification</title><p>Protected Owner-only qualification. No execution authority. REAL_ADMISSION is NO.</p></html>\n'
    files['vercel.json']=codec.canonical(dict(name='nexus-g3-qual',functions={'api/n01-controller.py':{'maxDuration':60 if transport_revision==1 else 300}},
        rewrites=([dict(source='/api/n01/:path*',destination='/api/n01-controller')] if transport_revision==1 else
                  [dict(source='/api/n01/'+route,destination='/api/n01-controller?n01_route='+route)
                   for route in ('start','login','confirm','status','recover','enroll','decision','revoke')])))
    if transport_revision==3:
        config=codec.decode(files['vercel.json']);config['regions']=['sin1'];files['vercel.json']=codec.canonical(config)
    manifest=codec.canonical({name:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for name,raw in sorted(files.items())})
    files['source-inventory.json']=manifest
    files['api/n01-controller.py']=(
        'from pathlib import Path\nfrom http.server import BaseHTTPRequestHandler\n'
        'from scripts import g3_n01_owner_controller as service\n'
        'service.ARTIFACT_ROOT=Path(__file__).resolve().parents[1]\n'
        'service.EXPECTED_MANIFEST_SHA='+repr(codec.digest(manifest))+'\n'
        'service.DELIVERY_EMAIL_SHA='+repr(delivery_email_sha256)+'\n'
        'service.CUSTODY_REVISION='+repr(transport_revision)+'\n'
        +('service.RESTART_PROFILE='+repr(restart_profile)+'\n'
           +'service.native.MAX_DDB='+str(ddb_limit)+'\nservice.native.MAX_S3='+str(s3_limit)+'\n'
           +("service.PRIMARY_READ_PROFILE='PAIRED_ATOMIC_V1'\n" if atomic else '')
           +'service.native.MAX_S3_WRITES=240\nservice.native.MAX_WRITE_BYTES=8388608\n'
           if restart_profile is not None else '')+
        ('service.REVIEW_GENERATION='+str(selected.generation)+'\nservice.UNTIL=service.datetime.fromtimestamp('+str(selected.valid_until_ms)+'/1000,service.timezone.utc)\n' if review_generation>=2 else '')+
        'class handler(service.handler,BaseHTTPRequestHandler):\n    pass\n').encode()
    complete={name:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for name,raw in sorted(files.items())}
    digest=codec.digest(codec.canonical(complete))
    destination.mkdir(parents=True,exist_ok=True)
    head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    metadata=dict(schema_version='nexus.g3.n01.owner-controller-artifact.v1',source_head=head,
        artifact_inventory_sha256=digest,files=complete,authority='NONE',real_admission='NO',
        scope='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',maximum_native_leases=8,maximum_ddb_attempts=256,
        maximum_s3_attempts=8000,maximum_s3_writes=256,maximum_new_bytes_per_backend=16777216,
        issuer_environment='STYTCH_CONSUMER_TEST',grant_issuance='NOT_IMPLEMENTED',execution='DENY')
    if review_generation>=2:
        metadata.update(review_generation=selected.generation,review_package_sha256=selected.package_sha256,review_acceptance_sha256=selected.acceptance_sha256,review_valid_until_ms=selected.valid_until_ms)
    if restart_profile is not None:
        metadata.update(restart_profile=restart_profile,expected_predecessor=restart.HEAD4,
            maximum_ddb_attempts=ddb_limit,maximum_s3_attempts=s3_limit,maximum_s3_writes=240,
            maximum_new_bytes_per_backend=8388608,prior_native_ddb_attempts=204 if atomic else 134 if restart_profile=='OWNER_SDK_REPAIR_FORWARD_V1' else 66,
            recovery='EXPLICIT_FORWARD_ONLY',old_owner_authority='NEVER_RESTORED')
    if atomic:metadata.update(primary_read_profile='PAIRED_ATOMIC_V1',maximum_read_items_per_transaction=2,approved_aggregate_ddb_attempts=512,earlier_non_owner_reserved_attempts=98)
    (destination/'artifact.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    request=dict(name='nexus-g3-qual',project='prj_xH23xMATVChdhX34OS2vjI8dfWN2',target='production',
        files=[dict(file=name,data=raw.decode(),encoding='utf-8') for name,raw in sorted(files.items())],
        meta=dict(n01Profile='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',n01SourceHead=head,n01ArtifactSha256=digest),
        projectSettings=dict(framework=None,buildCommand=None,outputDirectory=None,nodeVersion='24.x'))
    if transport_revision==3:request['projectSettings']['serverlessFunctionRegion']='sin1'
    (destination/'exact-body.json').write_text(json.dumps(request),encoding='utf-8')
    for name,raw in files.items():
        target=destination/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--delivery-email-sha256',required=True);args=parser.parse_args()
    result=build(args.destination,delivery_email_sha256=args.delivery_email_sha256)
    print(json.dumps({key:result[key] for key in ('artifact_inventory_sha256','source_head','authority','real_admission')}))
