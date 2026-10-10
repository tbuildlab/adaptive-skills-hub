"""Fixed read-only Owner metadata deployment, isolated from the diagnostic domain."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('factor_observation_qr',HERE/'scripts/verify_owner_qr_result.py')
QR=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(QR)
G3=QR.G3
CHECKPOINT='cb7838fb8195732f55788a2686d4858ba33b7811'

def need(ok,why):
    if not ok:raise RuntimeError('OWNER_FACTOR_READ_BLOCKED: '+why)

def scope():
    p=G3.generation3_input()['provider']
    return dict(application_generation=p['application_generation'],classification='FIXED_OWNER_FACTOR_METADATA_READ_ONLY',
        owner_user_id=p['owner_user_id'],project_id=p['project_id'],source_checkpoint=CHECKPOINT,
        vercel_project_id='prj_xH23xMATVChdhX34OS2vjI8dfWN2')

def compose(valid_from,enabled=False):
    need(type(enabled) is bool and type(valid_from) is int and valid_from>0,'closed input')
    config=dict(enabled=enabled,valid_from=valid_from,valid_until=valid_from+1800000,scope=scope())
    return {'package.json':b'{"name":"nexus-g3-owner-factor-read","private":true,"type":"module","engines":{"node":"24.x"},"dependencies":{}}\n',
        'vercel.json':b'{"functions":{"api/owner-factor-read.js":{"maxDuration":30}}}\n',
        'api/owner-factor-read.js':(HERE/'owner-factor-observation/endpoint.js').read_bytes().replace(b'\r\n',b'\n'),
        'lib/observation.js':(HERE/'owner-factor-observation/observation.js').read_bytes().replace(b'\r\n',b'\n'),
        'lib/configuration.js':('export const configuration=Object.freeze('+json.dumps(config,separators=(',',':'))+');\n').encode()}

def validate(blobs,valid_from,enabled=False):
    need(blobs==compose(valid_from,enabled) and len(blobs)==5,'exact inventory')
    G3.HISTORICAL.scan(blobs)
    for n,b in blobs.items():
        t=b.decode();need(not re.search(r'console\s*\.|\beval\s*\(|\bimport\s*\(|\brequire\s*\(',t),'dynamic/logging')
        need(not re.search(r'''["'](?:d|p|q|dp|dq|qi|oth)["']\s*:''',t),'private key field')
        need('DELETE' not in t and 'recovery_codes' not in t and 'session_token' not in t and 'session_jwt' not in t,'no mutation or session route')
        need(not n.startswith('public/'),'no private browser page')
        for target in re.findall(r"from ['\"]([^'\"]+)['\"]",t):
            if target.startswith('node:'):need(target in ('node:https','node:crypto'),'native imports')
            else:need((Path(n).parent/target).as_posix().replace('api/../','') in blobs,'import closure')
    transport=blobs['lib/observation.js'];need(b"method:'GET',path:'/v1/users/'+scope.owner_user_id" in transport,'fixed GET only')
    return dict(profile='FIXED_OWNER_FACTOR_METADATA_READ_ONLY',files=5,authority='NONE',real_admission_enabled='NO',
        scope_sha256=hashlib.sha256(json.dumps(scope(),separators=(',',':')).encode()).hexdigest(),valid_until=valid_from+1800000,enabled=enabled,
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),source_uid=hashlib.sha1(b).hexdigest()) for n,b in sorted(blobs.items())})

def build(output,valid_from,enabled=False):
    output=G3.HISTORICAL.safe_output(output);need(not output.exists(),'fresh output')
    blobs=compose(valid_from,enabled);report=validate(blobs,valid_from,enabled)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'read-only-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--valid-from',type=int,required=True);p.add_argument('--enable-fixed-read',action='store_true');a=p.parse_args();build(a.output,a.valid_from,a.enable_fixed_read)
