"""Deterministic diagnostic-only source artifact. Does not read deployment directories."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
REPO = SOURCE.parents[1]
SERVER = ('pre-secret-policy.js', 'provider-registration.js', 'credential-custody.js',
          'stytch-transport.js', 'pinned-identity.js', 'owner-channel.js',
          'deployment-input.js', 'diagnostic-service.js')
FILES = {f'lib/server/{n}': f'lib/server/{n}' for n in SERVER}
FILES.update({f'lib/{n}':f'lib/{n}' for n in ('policy.js','http.js','adapter.js','stytch-identity.js','stytch-projection.js')})
FILES.update({'api/diagnostic.js':'future-deployment/diagnostic-entry.js',
              'public/index.html':'future-deployment/index.html','public/app.js':'future-deployment/app.js',
              'public/owner-transient.js':'future-deployment/owner-transient.js',
              'package.json':'future-deployment/package.json','vercel.json':'future-deployment/vercel.json'})
SECRET_PATTERNS = (r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'\bsecret-(?:live|test)-[A-Za-z0-9_-]{16,}', r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    r'\b(?:vcp_|vt1_)[A-Za-z0-9_-]{24,}', r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
    r'https?://[^\s/:]+:[^\s/@]+@', r'Basic [A-Za-z0-9+/]{20,}={0,2}',
    r'''(?:STYTCH_SECRET|session_token|secret)\s*[:=]\s*['"](?!OFFLINE_)[^'"]{8,}['"]''')

def require(value, reason):
    if not value: raise RuntimeError('ARTIFACT_BLOCKED: '+reason)

def build(output):
    output=Path(output).absolute()
    require(output.is_relative_to(REPO/'state') and '..' not in output.parts, 'lexical output boundary')
    for candidate in (output,*output.parents):
        if candidate==REPO: break
        if candidate.exists() or candidate.is_symlink():
            info=candidate.lstat()
            require(not candidate.is_symlink() and not (getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400)), 'output link/reparse')
    output=output.resolve()
    require(output.is_relative_to(REPO/'state') and output != REPO/'state', 'output must be ignored repository validation state')
    blobs={}
    for destination, source_name in FILES.items():
        path=SOURCE/source_name
        for candidate in (path,*path.parents):
            if candidate==SOURCE.parent: break
            info=candidate.lstat()
            require(not candidate.is_symlink() and not (getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400)), 'source link/reparse')
        require(path.resolve().is_relative_to(SOURCE), 'source boundary')
        blob=path.read_bytes().replace(b'\r\n',b'\n'); require(len(blob)<=262144, 'source size')
        text=blob.decode('utf-8')
        require(not any(re.search(p,text) for p in SECRET_PATTERNS), 'source secret-shaped value: '+destination)
        blobs[destination]=blob
    for destination,blob in blobs.items():
        if destination.endswith('.js'):
            text=blob.decode('utf-8')
            require(not re.search(r'\bimport\s*\(|\brequire\s*\(|\beval\s*\(|\bconsole\s*\.',text), 'dynamic/logging import')
            for declaration in re.findall(r'(?m)^\s*import\b[^;]+;', text):
                literals=re.findall(r'[\'"]([^\'"]+)[\'"]', declaration)
                require(len(literals)==1, 'ambiguous static import')
                module=literals[0]
                if module.startswith('node:'):continue
                require(module.startswith('.'), 'third-party module')
                target=(Path(destination).parent/module).as_posix()
                parts=[]
                for part in target.split('/'):
                    if part=='..': require(bool(parts), 'import escape'); parts.pop()
                    elif part not in ('','.'):parts.append(part)
                require('/'.join(parts) in blobs, 'missing dependency: '+module)
            if destination.startswith('public/'):
                require(not re.search(r'lib/server|process\.env|STYTCH_SECRET|session_token|session_jwt|localStorage|sessionStorage|innerHTML',text), 'client custody boundary')
    policy=blobs['lib/server/pre-secret-policy.js'].decode()
    require('CODE_REVIEWED_LIVE_ENABLED = false' in policy and 'DEPLOYMENT_REGISTRATION_ENABLED = false' in policy, 'hard gates')
    require("mode: 'FAKE_DISABLED'" in blobs['lib/server/deployment-input.js'].decode(), 'default mode')
    require('provider: null, keyset: null' in blobs['lib/server/deployment-input.js'].decode(), 'unregistered default')
    for member in blobs:
        require(not any(p in {'.env','.vercel','state','ash','docs','tests'} for p in member.split('/')), 'forbidden artifact member')
    require('lib/server/credential-custody.js' in blobs, 'credential source required')
    output.mkdir(parents=True,exist_ok=True); artifact=output/'source'
    artifact.mkdir(exist_ok=True)
    candidates=list(artifact.rglob('*'))
    for candidate in (artifact,*candidates):
        info=candidate.lstat()
        require(not candidate.is_symlink() and not (getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400)), 'artifact link/reparse')
    existing={p.relative_to(artifact).as_posix() for p in candidates if p.is_file()}
    require(existing<=set(blobs), 'unexpected artifact content')
    for name,blob in blobs.items():
        target=artifact/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    metadata={name:{'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()} for name,blob in sorted(blobs.items())}
    zip_path=output/'diagnostic-source.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,blob in sorted(blobs.items()):
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.external_attr=0o100644<<16
            archive.writestr(item,blob)
    report={'classification':'VERIFIED_OFFLINE_SOURCE_CLOSURE_ONLY','files':metadata,
            'deployment_requires_repository_manifest':False,'credential_loader_source_included':True,
            'mode':'FAKE_DISABLED','authority':'NONE','provider_build':'NOT_RUN','deployment':'NOT_RUN',
            'network_calls':0,'credential_access':'NONE','zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()}
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Run the composed entrypoint with a native-network trap; no build/deploy/login.
    script="""import https from 'node:https';import {syncBuiltinESMExports} from 'node:module';
import {pathToFileURL} from 'node:url';let calls=0;https.request=()=>{calls++;throw Error('NETWORK_FORBIDDEN');};syncBuiltinESMExports();
const {default:handler}=await import(pathToFileURL(process.argv[1]));const res={setHeader(){},end(body){this.body=JSON.parse(body);}};
await handler({method:'GET',url:'/api/diagnostic',headers:{host:'nexus-g3-qual.vercel.app'}},res);
if(calls!==0||res.body.adapter_mode!=='FAKE_DISABLED'||res.body.real_admission!=='DISABLED')throw Error('BOUNDARY');
process.stdout.write('ARTIFACT_ENTRY_PASS: FAKE_DISABLED; NETWORK_CALL_COUNT=0\\n');"""
    subprocess.run(['node','--input-type=module','-e',script,str(artifact/'api/diagnostic.js')],check=True)
    print(f'ARTIFACT_PASS: files={len(blobs)}; credential_source=INCLUDED; repository_manifest=NOT_REQUIRED; provider_build=NOT_RUN')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    build(parser.parse_args().output)
