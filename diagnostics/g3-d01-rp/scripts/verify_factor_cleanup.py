"""Bounded administrative artifact. Never promoted onto the stable diagnostic domain."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re
HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('cleanup_qr', HERE/'scripts/verify_owner_qr.py')
QR = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(QR)
SCOPE_FILE = HERE/'factor-cleanup/reviewed-scope.json'

def need(ok, reason):
    if not ok: raise RuntimeError('FACTOR_CLEANUP_BLOCKED: '+reason)

def reviewed_scope():
    scope = json.loads(SCOPE_FILE.read_text(encoding='utf-8'))
    registration = QR.G3.generation3_input()['provider']
    need(scope['project_id'] == registration['project_id'] and scope['owner_user_id'] == registration['owner_user_id'], 'Owner binding')
    need(scope['application_generation'] == registration['application_generation'] == 3, 'generation')
    need(re.fullmatch(r'totp-test-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', scope['exposed_totp_id']), 'fixed factor ID')
    return scope

def compose(valid_from, enabled=False):
    need(type(enabled) is bool and type(valid_from) is int and valid_from > 0, 'closed activation')
    scope = reviewed_scope()
    config = dict(enabled=enabled, valid_from=valid_from, valid_until=valid_from+1800000, scope=scope)
    return {
      'package.json': b'{"name":"nexus-g3-fixed-factor-cleanup","private":true,"type":"module","engines":{"node":"24.x"},"dependencies":{}}\n',
      'vercel.json': b'{"functions":{"api/factor-cleanup.js":{"maxDuration":30}}}\n',
      'api/factor-cleanup.js': (HERE/'factor-cleanup/endpoint.js').read_bytes().replace(b'\r\n', b'\n'),
      'lib/cleanup.js': (HERE/'factor-cleanup/cleanup.js').read_bytes().replace(b'\r\n', b'\n'),
      'lib/configuration.js': ('export const configuration = Object.freeze('+json.dumps(config, separators=(',', ':'))+');\n').encode(),
    }

def validate(blobs, valid_from, enabled=False):
    need(blobs == compose(valid_from, enabled) and len(blobs) == 5, 'closed source')
    QR.G3.HISTORICAL.scan(blobs)
    for name, body in blobs.items():
        need(not any(part.startswith('.') for part in Path(name).parts), 'hidden files')
        text = body.decode()
        need(not re.search(r'console\s*\.|\beval\s*\(|\bimport\s*\(|\brequire\s*\(', text), 'dynamic code or logs')
        need(not re.search(r'''["'](?:d|p|q|dp|dq|qi|oth)["']\s*:''', text), 'private key field')
        if name.endswith('.js'):
            for target in re.findall(r"from ['\"]([^'\"]+)['\"]", text):
                if target.startswith('node:'): need(target in ('node:https','node:crypto'), 'native import')
                else: need((Path(name).parent/target).as_posix().replace('api/../','') in blobs, 'closed import')
    transport = blobs['lib/cleanup.js']
    need(b"'/v1/users/totps/' + scope.exposed_totp_id" in transport and b"'/v1/users/' + scope.owner_user_id" in transport, 'exact routes')
    need(b"['GET','DELETE']" in transport and b"method === 'GET'" in transport, 'method closure')
    need(b'Authorization:' in transport and b'console' not in transport, 'server custody')
    need(not any(name.startswith('public/') for name in blobs), 'no browser assets')
    return dict(profile='FIXED_EXPOSED_FACTOR_CLEANUP', files=5, authority='NONE', real_admission_enabled='NO',
      scope_sha256=hashlib.sha256(json.dumps(reviewed_scope(), separators=(',', ':')).encode()).hexdigest(),
      zip_sha256=hashlib.sha256(QR.G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
      valid_until=valid_from+1800000, enabled=enabled,
      files_sha256={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),source_uid=hashlib.sha1(b).hexdigest()) for n,b in sorted(blobs.items())})

def build(output, valid_from, enabled=False):
    output = QR.G3.HISTORICAL.safe_output(output); need(not output.exists(), 'fresh output')
    blobs = compose(valid_from, enabled); report = validate(blobs, valid_from, enabled)
    for name, body in blobs.items():
        path=output/'source'/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
    (output/'cleanup-source.zip').write_bytes(QR.G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('profile','files','authority','real_admission_enabled','enabled','zip_sha256')}))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True); parser.add_argument('--valid-from',type=int,required=True)
    parser.add_argument('--enable-fixed-cleanup',action='store_true'); args=parser.parse_args()
    build(args.output,args.valid_from,args.enable_fixed_cleanup)
