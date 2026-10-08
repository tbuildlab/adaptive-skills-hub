"""Offline-only deterministic Owner handoff. No upload/login/account/network API."""
from __future__ import annotations
import argparse,hashlib,importlib.util,io,json,re,stat,subprocess,zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent
ROOT=SOURCE.parents[1]
CHECKPOINT='3ccdb3d414ac75895361aa1274d560996c6ccd1b'
SOURCE_SHA256='84796f260303ad64e9982134075a4fadae968c70919d3ffaf17a62be51c78fc3'
REVIEW_END_MS=1791564125000
RUNBOOK='docs/nexus-g3-d01-disabled-production-deployment-owner-runbook-v1.md'
PUBLIC={'public/index.html','public/app.js','public/owner-transient.js'}
CHECKS=['Production revision/id','stable Production domain','exact reviewed source hash/trace','one function',
  'exact diagnostic route','three public assets','Node runtime','30-second duration support','security headers',
  'no Preview live mode','no Development live mode','no extra endpoint','no analytics/telemetry/debug',
  'no client native registration','no secret-bearing build output','no disabled credential access',
  'AUTHORITY NONE / REAL_ADMISSION DISABLED','no provider calls']
DISABLED_LABELS={'diagnostic':'NEXUS_G3_D01_DIAGNOSTIC_ONLY','authority':'NONE','real_admission':'DISABLED',
  'adapter_mode':'FAKE_DISABLED','result':'DENY','live_diagnostic_enabled':False}
SPEC=importlib.util.spec_from_file_location('accepted_deployment_verifier',HERE/'verify_deployment.py')
VERIFIER=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(VERIFIER)

def need(value,reason):
    if not value:raise RuntimeError('HANDOFF_BLOCKED: '+reason)

def stable_json(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()

def frozen_zip(blobs):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,blob in sorted(blobs.items()):
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.external_attr=0o100644<<16
            archive.writestr(item,blob)
    return stream.getvalue()

def scan(blobs):
    for name,blob in blobs.items():
        need(isinstance(blob,bytes) and len(blob)<=262144,'bounded bytes')
        text=blob.decode('utf-8') if not name.endswith('.zip') else ''
        need(not any(re.search(pattern,text) for pattern in VERIFIER.SECRET_PATTERNS),'secret-shaped material')
        need(not re.search(r'[\'"](?:d|p|q|dp|dq|qi|oth)[\'"]\s*:',text),'private JWK field')

def config_review(blobs):
    config=json.loads(blobs['vercel.json']);package=json.loads(blobs['package.json'])
    need(set(config)=={'framework','buildCommand','outputDirectory','functions','headers'},'closed deployment config')
    need(config['framework'] is None and config['buildCommand'] is None and config['outputDirectory']=='public','no build/framework indirection')
    need(config['functions']=={'api/diagnostic.js':{'maxDuration':30}},'exact function count/entry/duration')
    need(len(config['headers'])==1 and config['headers'][0]['source']=='/(.*)','global response headers only')
    actual={h['key']:h['value'] for h in config['headers'][0]['headers']}
    expected={'Cache-Control':'no-store','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
              'Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY'}
    need(actual==expected and len(config['headers'][0]['headers'])==len(expected),'security headers')
    need(set(package)=={'name','private','type','engines','dependencies'} and package['private'] is True
         and package['type']=='module' and package['engines']=={'node':'24.x'} and package['dependencies']=={},'exact dependency-free Node input')
    return {'classification':'PASS_SOURCE_INPUT_ONLY','node_profile':'24.x','module_type':'ESM','functions':{'api/diagnostic.js':{'maxDuration':30}},
      'public_assets':sorted(PUBLIC),'origin':'https://nexus-g3-qual.vercel.app','rewrites':0,'redirects':0,
      'actual_account_runtime_duration':'OWNER_LIVE_REVIEW_REQUIRED','actual_build_trace':'OWNER_LIVE_REVIEW_REQUIRED',
      'actual_permissions':'OWNER_LIVE_REVIEW_REQUIRED','deployment_mechanism':'OWNER_CONFIRMATION_REQUIRED',
      'secret_injection_authorized':False,'live_testing_authorized':False,'deployment_performed':False}

def validate_source(blobs):
    need(set(blobs)==set(VERIFIER.FILES) and len(blobs)==19,'exact frozen source inventory')
    scan(blobs);config=config_review(blobs)
    owner=blobs['lib/server/deployment-input.js'].decode()
    need("mode: 'FAKE_DISABLED'" in owner and 'registration_generation: 1, provider, keyset' in owner,'disabled registered input')
    need('OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET' in owner and '1791564125000' in owner,'fixed public pin/review expiry')
    policy=blobs['lib/server/pre-secret-policy.js'].decode()
    need('CODE_REVIEWED_LIVE_ENABLED = false' in policy and 'DEPLOYMENT_REGISTRATION_ENABLED = false' in policy,'compile gates')
    need("https://nexus-g3-qual.vercel.app" in blobs['lib/policy.js'].decode(),'exact stable origin')
    ids=re.findall(r'(?:project|user)-test-[a-f0-9-]{36}',owner)
    need(len(ids)==2,'server native tuple')
    for path in PUBLIC:
        text=blobs[path].decode()
        need(not any(value in text for value in ids),'native identity client leakage')
        need(not re.search(r'process\.env|STYTCH_SECRET|session_token|session_jwt|lib/server|OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET|localStorage|sessionStorage|innerHTML',text),'client custody boundary')
    bundle=frozen_zip(blobs)
    need(hashlib.sha256(bundle).hexdigest()==SOURCE_SHA256,'immutable reviewed source hash')
    return config

def safe_output(path):
    path=Path(path).absolute()
    need(path.is_relative_to(ROOT/'state') and '..' not in path.parts and path!=ROOT/'state','ignored output boundary')
    for node in (path,*path.parents):
        if node==ROOT:break
        if node.exists() or node.is_symlink():
            flags=getattr(node.lstat(),'st_file_attributes',0)
            need(not node.is_symlink() and not flags&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400),'output reparse')
    return path

def validate_handoff(payload,source):
    validate_source(source)
    expected={'deployment-source.zip','source-manifest.json','SHA256SUMS.txt','source-bundle.sha256.txt',
              'deployment-config-summary.json','OWNER-CHECKLIST.md','POST-DEPLOYMENT-EVIDENCE.json','DISABLED-LABELS.json'}|{'source/'+p for p in source}
    need(set(payload)==expected and len(payload)==27,'exact handoff inventory')
    scan(payload)
    need(payload['deployment-source.zip']==frozen_zip(source),'frozen source ZIP')
    for name,blob in source.items():need(payload['source/'+name]==blob,'source byte identity')
    manifest=json.loads(payload['source-manifest.json'])
    need(manifest=={name:{'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()} for name,blob in source.items()},'source file manifest')
    need(payload['source-bundle.sha256.txt'].decode()==SOURCE_SHA256+'  deployment-source.zip\n','bundle digest list')
    need(payload['SHA256SUMS.txt'].decode()==''.join(hashlib.sha256(blob).hexdigest()+'  '+name+'\n' for name,blob in sorted(source.items())),'per-file digest list')
    need(json.loads(payload['deployment-config-summary.json'])==config_review(source),'config evidence boundary')
    evidence=json.loads(payload['POST-DEPLOYMENT-EVIDENCE.json'])
    need(evidence=={'deployment_verified':False,'network_calls_performed':0,
      'checks':[{'check':c,'status':'OWNER_LIVE_REVIEW_REQUIRED'} for c in CHECKS]},'closed unverified hosted checklist')
    need(json.loads(payload['DISABLED-LABELS.json'])==DISABLED_LABELS,'disabled labels cannot promote authority')
    return True

def prepare(output):
    output=safe_output(output);output.mkdir(parents=True,exist_ok=True)
    artifact=VERIFIER.build(output/'artifact')
    source={name:(output/'artifact/source'/name).read_bytes() for name in artifact['files']}
    config=validate_source(source)
    proof_run=subprocess.run(['node',str(HERE/'prove_disabled_startup.mjs'),str(output/'artifact/source')],check=True,capture_output=True,text=True,timeout=20)
    proof=json.loads(proof_run.stdout)
    need(proof['startup']=='PASS' and all(proof[k]==0 for k in ('network_calls','credential_read_attempts','credential_loader_calls','native_factory_calls','provider_operation_calls','jwks_runtime_calls','signature_calls','owner_material_calls','environment_enumerations')),'startup traps')
    # Read only the current explicitly reviewed, secret-free Owner checklist.
    checklist=(ROOT/RUNBOOK).read_bytes().replace(b'\r\n',b'\n')
    evidence={'deployment_verified':False,'network_calls_performed':0,'checks':[{'check':c,'status':'OWNER_LIVE_REVIEW_REQUIRED'} for c in CHECKS]}
    payload={
      'deployment-source.zip':frozen_zip(source),'source-manifest.json':stable_json(artifact['files']),
      'SHA256SUMS.txt':''.join(hashlib.sha256(blob).hexdigest()+'  '+name+'\n' for name,blob in sorted(source.items())).encode(),
      'source-bundle.sha256.txt':(SOURCE_SHA256+'  deployment-source.zip\n').encode(),
      'deployment-config-summary.json':stable_json(config),'OWNER-CHECKLIST.md':checklist,
      'POST-DEPLOYMENT-EVIDENCE.json':stable_json(evidence),
      'DISABLED-LABELS.json':stable_json(DISABLED_LABELS),
      **{'source/'+p:blob for p,blob in source.items()}}
    validate_handoff(payload,source)
    destination=output/'handoff';destination.mkdir(exist_ok=True)
    existing=list(destination.rglob('*'))
    for node in existing:
        need(not node.is_symlink() and not getattr(node.lstat(),'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400),'handoff reparse')
    need({p.relative_to(destination).as_posix() for p in existing if p.is_file()}<=set(payload),'unexpected handoff content')
    for name,blob in payload.items():
        path=destination/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
    zipped=frozen_zip(payload);(output/'owner-handoff.zip').write_bytes(zipped)
    # Check ZIP inventory before opening any unexpected content.
    with zipfile.ZipFile(io.BytesIO(zipped)) as archive:
        need(set(archive.namelist())==set(payload) and len(archive.namelist())==27,'ZIP members')
        validate_handoff({name:archive.read(name) for name in archive.namelist()},source)
    result={'handoff':'READY','source_checkpoint':CHECKPOINT,'source_file_count':19,'source_sha256':SOURCE_SHA256,
      'handoff_file_count':27,'handoff_sha256':hashlib.sha256(zipped).hexdigest(),'source_files':artifact['files'],
      'startup_proof':proof,'owner_deployment_mechanism':'OWNER_CONFIRMATION_REQUIRED','actual_build_verified':False,
      'actual_runtime_verified':False,'actual_permissions':'OWNER_REQUIRED','review_end_ms':REVIEW_END_MS}
    (output/'handoff-result.json').write_bytes(stable_json(result))
    print('HANDOFF_PASS: source=19; handoff=27; source_hash='+SOURCE_SHA256+'; mode=FAKE_DISABLED; network=0; credential_reads=0; hosted_build/runtime=UNVERIFIED')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    prepare(parser.parse_args().output)
