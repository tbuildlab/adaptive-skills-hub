"""In-memory adversarial mutation tests; no provider or credential use."""
from pathlib import Path
import copy, hashlib, importlib.util, unittest, tempfile, json, subprocess
SPEC=importlib.util.spec_from_file_location('g2artifact',Path(__file__).resolve().parents[1]/'scripts/verify_generation2.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.reviewed_public_input()

class Generation2Artifacts(unittest.TestCase):
 def setUp(self): self.disabled=M.compose('DISABLED',DATA)
 def reject(self,blobs,profile='DISABLED'):
  with self.assertRaises(RuntimeError): M.validate(blobs,profile,DATA)
 def mutate(self,name,old,new):
  blobs=dict(self.disabled);self.assertIn(old,blobs[name]);blobs[name]=blobs[name].replace(old,new);self.reject(blobs)
 def test_exact_inventory_19(self): self.assertEqual(M.validate(self.disabled,'DISABLED',DATA)['files'],19)
 def test_deterministic(self):
  self.assertEqual(M.HISTORICAL.frozen_zip(self.disabled),M.HISTORICAL.frozen_zip(dict(reversed(list(self.disabled.items())))))
 def test_distinct_from_historical(self): self.assertNotEqual(hashlib.sha256(M.HISTORICAL.frozen_zip(self.disabled)).hexdigest(),M.HISTORICAL.SOURCE_SHA256)
 def test_only_input_changes(self): self.assertEqual({n for n,b in M.originals().items() if b!=self.disabled[n]},{M.INPUT})
 def test_live_changes_only_two_files(self):
  live=M.compose('LIVE_DIAGNOSTIC',DATA)
  self.assertEqual({n for n,b in M.originals().items() if b!=live[n]},{M.INPUT,M.POLICY})
  self.assertEqual(M.validate(live,'LIVE_DIAGNOSTIC',DATA)['authority'],'NONE')
 def test_live_cannot_validate_as_disabled(self): self.reject(M.compose('LIVE_DIAGNOSTIC',DATA))
 def test_unsupported_profile(self):
  with self.assertRaises(RuntimeError): M.compose('PRODUCTION_AUTHORITY',DATA)
 def test_missing_module(self):
  blobs=dict(self.disabled);blobs.pop('lib/server/credential-custody.js');self.reject(blobs)
 def test_extra_env(self):
  blobs=dict(self.disabled);blobs['.env']=b'OFFLINE_CONTAMINATION';self.reject(blobs)
 def test_extra_authority(self):
  blobs=dict(self.disabled);blobs['ash/authority.py']=b'OFFLINE_CONTAMINATION';self.reject(blobs)
 def test_extra_route_d(self):
  blobs=dict(self.disabled);blobs['docs/nexus-route-d-test.md']=b'OFFLINE_CONTAMINATION';self.reject(blobs)
 def test_extra_vercel_state(self):
  blobs=dict(self.disabled);blobs['.vercel/project.json']=b'{}';self.reject(blobs)
 def test_changed_generation(self): self.mutate(M.INPUT,b'"registration_generation": 2',b'"registration_generation": 1')
 def test_changed_origin(self): self.mutate(M.INPUT,b'https://nexus-g3-qual.vercel.app',b'https://other.invalid')
 def test_changed_keyset(self): self.mutate(M.INPUT,b'"alg": "RS256"',b'"alg": "HS256"')
 def test_changed_expiry(self): self.mutate(M.INPUT,str(DATA['keyset']['valid_until']).encode(),b'9999999999999')
 def test_disabled_gate_mutation(self): self.mutate(M.POLICY,b'CODE_REVIEWED_LIVE_ENABLED = false',b'CODE_REVIEWED_LIVE_ENABLED = true')
 def test_public_owner_disclosure(self): self.mutate('public/app.js',b'let csrf=null;',b'let csrf=null;/*'+DATA['provider']['owner_user_id'].encode()+b'*/')
 def test_changed_transport(self): self.mutate('lib/server/stytch-transport.js',b'rejectUnauthorized: true',b'rejectUnauthorized: false')
 def test_changed_provider_route(self): self.mutate(M.POLICY,b'https://test.stytch.com',b'https://api.stytch.com')
 def test_changed_scope(self): self.mutate(M.INPUT,b'"session_max_minutes": 15',b'"session_max_minutes": 60')
 def test_arbitrary_project_input_rejected(self):
  data=copy.deepcopy(DATA);data['provider']['project_id']='project-test-other'
  with self.assertRaises(RuntimeError): M.compose('DISABLED',data)
 def test_arbitrary_owner_input_rejected(self):
  data=copy.deepcopy(DATA);data['provider']['owner_user_id']='user-test-other'
  with self.assertRaises(RuntimeError): M.compose('LIVE_DIAGNOSTIC',data)
 def test_arbitrary_review_window_rejected(self):
  data=copy.deepcopy(DATA);data['keyset']['valid_until']+=86400000
  with self.assertRaises(RuntimeError): M.compose('LIVE_DIAGNOSTIC',data)
 def test_readiness_profile_closed_inventory(self):
  blobs=M.compose('LIVE_DIAGNOSTIC_READINESS',DATA)
  self.assertEqual(M.validate(blobs,'LIVE_DIAGNOSTIC_READINESS',DATA)['files'],19)
  self.assertEqual({n for n,b in M.originals().items() if b!=blobs[n]},{M.INPUT,M.POLICY,M.CUSTODY})
 def test_readiness_profile_has_no_extra_secret_read(self):
  blob=M.compose('LIVE_DIAGNOSTIC_READINESS',DATA)[M.CUSTODY]
  self.assertEqual(blob.count(b'process.env.STYTCH_PROJECT_ID'),1)
  self.assertEqual(blob.count(b'process.env.STYTCH_SECRET'),1)
  self.assertNotIn(b'console.',blob)
  self.assertNotIn(b'Object.keys(process.env)',blob)
 def test_readiness_cannot_be_disabled(self): self.reject(M.compose('LIVE_DIAGNOSTIC_READINESS',DATA))
 def readiness_runtime(self,variant,expected,expected_reads):
  blobs=M.compose('LIVE_DIAGNOSTIC_READINESS',DATA)
  with tempfile.TemporaryDirectory(prefix='nexus-g3-readiness-offline-') as directory:
   root=Path(directory)
   for name,blob in blobs.items():
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
   script="""
import {syncBuiltinESMExports} from 'node:module';
import https from 'node:https';import http from 'node:http';import net from 'node:net';import tls from 'node:tls';
let network=0,reads=0;const deny=()=>{network++;throw Error('OFFLINE_NETWORK');};
https.request=deny;https.get=deny;http.request=deny;http.get=deny;net.connect=deny;net.createConnection=deny;tls.connect=deny;
globalThis.fetch=deny;syncBuiltinESMExports();
const {DEPLOYMENT:d}=await import('./lib/server/deployment-input.js');
Date.now=()=>d.keyset.valid_from+1;
const variant=process.argv[1],expected=process.argv[2],expectedReads=Number(process.argv[3]);
process.env=new Proxy(Object.create(null),{get(_t,n){
 if(n==='STYTCH_PROJECT_ID'){reads++;return variant==='PROJECT_MISSING'?undefined:variant==='PROJECT_MISMATCH'?'OFFLINE_WRONG_PROJECT':d.provider.project_id;}
 if(n==='STYTCH_SECRET'){reads++;return variant==='SECRET_MISSING'?undefined:'OFFLINE_INVALID_CREDENTIAL';}
 return undefined;},ownKeys(){throw Error('OFFLINE_ENV_ENUMERATION');}});
const {default:handler}=await import('./api/diagnostic.js');
const base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
const request=async(method,body,headers)=>{const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(b){this.body=JSON.parse(b);}};await handler({method,url:'/api/diagnostic',body,headers},res);return res;};
const page=await request('GET',undefined,base);
if(reads!==0||network!==0)throw Error('GET_CREDENTIAL_READ');
const res=await request('POST',{action:'EMAIL_OTP_SEND'},{...base,'content-type':'application/json','x-g3-csrf':page.body.csrf,cookie:page.headers['Set-Cookie'].split(';')[0]});
if(res.statusCode!==403||res.body.error_class!==expected||res.body.result!=='DENY'
 ||res.body.authority!=='NONE'||res.body.real_admission!=='DISABLED'||network!==0||reads!==expectedReads)throw Error('READINESS_BOUNDARY');
const safe=JSON.stringify(res.body);
if(safe.includes('OFFLINE_INVALID_CREDENTIAL')||safe.includes(d.provider.project_id)||safe.includes(d.provider.owner_user_id))throw Error('EVIDENCE_LEAK');
"""
   # Windows OpenSSL initialization needs the OS root. Supply only this known
   # non-secret path, never copy/enumerate the real environment or credentials.
   environment={'SystemRoot':r'C:\Windows'} if Path(r'C:\Windows\System32').is_dir() else {}
   result=subprocess.run(['node','--input-type=module','-e',script,variant,expected,str(expected_reads)],cwd=root,env=environment,capture_output=True)
   self.assertEqual(result.returncode,0,result.stderr.decode())
 def test_project_missing_denies_before_secret_read(self):self.readiness_runtime('PROJECT_MISSING','PROJECT_CONFIG_MISSING',1)
 def test_project_mismatch_denies_before_secret_read(self):self.readiness_runtime('PROJECT_MISMATCH','PROJECT_CONFIG_MISMATCH',1)
 def test_secret_missing_denies_without_network(self):self.readiness_runtime('SECRET_MISSING','SECRET_CONFIG_MISSING',2)
 def test_secret_format_denies_without_network(self):self.readiness_runtime('SECRET_FORMAT','SECRET_CONFIG_FORMAT',2)

if __name__=='__main__':unittest.main()
