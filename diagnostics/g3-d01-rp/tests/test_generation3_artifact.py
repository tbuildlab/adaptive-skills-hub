"""Exact generation 3 artifact and trapped runtime tests; no live operations."""
from pathlib import Path
import copy, importlib.util, subprocess, tempfile, unittest

SPEC = importlib.util.spec_from_file_location('g3artifact', Path(__file__).resolve().parents[1]/'scripts/verify_generation3.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
DATA = M.reviewed_public_input()
LIVE = 'LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT'

class Generation3Artifacts(unittest.TestCase):
    def setUp(self): self.disabled = M.compose('DISABLED', DATA)
    def reject(self, blobs, profile='DISABLED'):
        with self.assertRaises(RuntimeError): M.validate(blobs, profile, DATA)
    def mutate(self, name, old, new):
        blobs = dict(self.disabled)
        self.assertIn(old, blobs[name])
        blobs[name] = blobs[name].replace(old, new)
        self.reject(blobs)
    def test_inventory_19(self): self.assertEqual(M.validate(self.disabled, 'DISABLED', DATA)['files'], 19)
    def test_deterministic_zip(self):
        self.assertEqual(M.HISTORICAL.frozen_zip(self.disabled), M.HISTORICAL.frozen_zip(dict(reversed(list(self.disabled.items())))))
    def test_disabled_changes_input_only(self):
        self.assertEqual({n for n,b in M.G2.originals().items() if b != self.disabled[n]}, {M.INPUT})
    def test_live_changes_exact_four_files(self):
        live = M.compose(LIVE, DATA)
        self.assertEqual({n for n,b in M.G2.originals().items() if b != live[n]}, {M.INPUT,M.POLICY,M.CUSTODY,M.SERVICE})
        self.assertEqual(M.validate(live,LIVE,DATA)['authority'], 'NONE')
    def test_existing_public_review_unchanged(self):
        old = M.G2.reviewed_public_input()['keyset']
        for f in ['keys','source','project_id','valid_from','valid_until']: self.assertEqual(DATA['keyset'][f],old[f])
    def test_old_generation_input_rejected(self):
        with self.assertRaises(RuntimeError): M.compose(LIVE,M.G2.reviewed_public_input())
    def test_old_builder_cannot_accept_new_generation(self):
        with self.assertRaises(RuntimeError): M.G2.compose(LIVE,DATA)
    def test_arbitrary_delivery_input_rejected(self):
        data = copy.deepcopy(DATA); data['provider']['delivery_email'] = 'offline@example.invalid'
        with self.assertRaises(RuntimeError): M.compose(LIVE,data)
    def test_unsupported_profile_rejected(self):
        with self.assertRaises(RuntimeError): M.compose('PRODUCTION_AUTHORITY',DATA)
    def test_missing_file_rejected(self):
        blobs = dict(self.disabled); blobs.pop(M.CUSTODY); self.reject(blobs)
    def test_extra_environment_file_rejected(self):
        blobs = dict(self.disabled); blobs['.env'] = b'OFFLINE_CONTAMINATION'; self.reject(blobs)
    def test_changed_generation_rejected(self): self.mutate(M.INPUT,b'"registration_generation": 3',b'"registration_generation": 2')
    def test_changed_key_rejected(self): self.mutate(M.INPUT,b'"alg": "RS256"',b'"alg": "HS256"')
    def test_changed_review_deadline_rejected(self):
        self.mutate(M.INPUT,str(DATA['keyset']['valid_until']).encode(),b'9999999999999')
    def test_public_identity_disclosure_rejected(self):
        self.mutate('public/app.js',b'let csrf=null;',b'let csrf=null;/*'+DATA['provider']['owner_user_id'].encode()+b'*/')
    def test_changed_tls_rejected(self): self.mutate('lib/server/stytch-transport.js',b'rejectUnauthorized: true',b'rejectUnauthorized: false')
    def test_production_provider_route_rejected(self): self.mutate(M.POLICY,b'https://test.stytch.com',b'https://api.stytch.com')
    def test_live_cannot_validate_as_disabled(self): self.reject(M.compose(LIVE,DATA))
    def runtime(self, profile):
        blobs = M.compose(profile,DATA)
        with tempfile.TemporaryDirectory(prefix='nexus-g3-generation3-offline-') as directory:
            root = Path(directory)
            for name,blob in blobs.items():
                path = root/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(blob)
            script = """
import {syncBuiltinESMExports} from 'node:module';
import https from 'node:https';import http from 'node:http';import net from 'node:net';import tls from 'node:tls';
let network=0,reads=0;const deny=()=>{network++;throw Error('OFFLINE_NETWORK');};
https.request=deny;https.get=deny;http.request=deny;http.get=deny;net.connect=deny;net.createConnection=deny;tls.connect=deny;
globalThis.fetch=deny;syncBuiltinESMExports();
const {DEPLOYMENT:d}=await import('./lib/server/deployment-input.js');
Date.now=()=>d.keyset.valid_from+1;
process.env=new Proxy(Object.create(null),{get(_t,n){
 if(n==='STYTCH_PROJECT_ID'){reads++;return undefined;}
 if(n==='STYTCH_SECRET')throw Error('OFFLINE_SECRET_READ');
 return undefined;},ownKeys(){throw Error('OFFLINE_ENV_ENUMERATION');}});
const {default:handler}=await import('./api/diagnostic.js');
const base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
const request=async(method,body,headers)=>{const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(b){this.body=JSON.parse(b);}};await handler({method,url:'/api/diagnostic',body,headers},res);return res;};
const page=await request('GET',undefined,base);
if(reads!==0||network!==0)throw Error('GET_SIDE_EFFECT');
const res=await request('POST',{action:'EMAIL_OTP_SEND'},{...base,'content-type':'application/json','x-g3-csrf':page.body.csrf,cookie:page.headers['Set-Cookie'].split(';')[0]});
const live=process.argv[1]==='LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT';
// The unchanged disabled factory uses the original request-denying HTTP shell.
if(res.statusCode!==(live?403:400)||res.body.error_class!==(live?'PROJECT_CONFIG_MISSING':'REQUEST')||res.body.result!=='DENY'
 ||res.body.authority!=='NONE'||res.body.real_admission!=='DISABLED'||network!==0||reads!==(live?1:0))
 throw Error(JSON.stringify({check:'FAIL_CLOSED_BOUNDARY',status:res.statusCode,error_class:res.body.error_class,
   result:res.body.result,authority:res.body.authority,real_admission:res.body.real_admission,network,reads}));
const safe=JSON.stringify(res.body);
if(safe.includes(d.provider.delivery_email)||safe.includes(d.provider.project_id)||safe.includes(d.provider.owner_user_id))throw Error('EVIDENCE_LEAK');
"""
            env = {'SystemRoot':r'C:\Windows'} if Path(r'C:\Windows\System32').is_dir() else {}
            r = subprocess.run(['node','--input-type=module','-e',script,profile],cwd=root,env=env,capture_output=True)
            self.assertEqual(r.returncode,0,r.stderr.decode())
    def test_disabled_send_never_reads_credentials_or_network(self): self.runtime('DISABLED')
    def test_live_missing_project_denies_before_secret_or_network(self): self.runtime(LIVE)

if __name__ == '__main__': unittest.main()
