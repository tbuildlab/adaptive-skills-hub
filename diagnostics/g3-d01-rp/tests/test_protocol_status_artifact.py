"""Closed failure projection with mandatory retirement; offline only."""
from pathlib import Path
import importlib.util, json, subprocess, tempfile, unittest
SPEC=importlib.util.spec_from_file_location('protocol_artifact',Path(__file__).resolve().parents[1]/'scripts/verify_generation2.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.reviewed_public_input()
PROFILE='LIVE_DIAGNOSTIC_PROTOCOL_STATUS'

class ProtocolStatusArtifact(unittest.TestCase):
 def test_exact_four_file_change(self):
  blobs=M.compose(PROFILE,DATA)
  self.assertEqual({n for n,b in M.originals().items() if b!=blobs[n]},{M.INPUT,M.POLICY,M.CUSTODY,M.SERVICE})
  self.assertEqual(M.validate(blobs,PROFILE,DATA)['files'],19)
 def test_historical_service_unchanged(self):
  for p in ('DISABLED','LIVE_DIAGNOSTIC','LIVE_DIAGNOSTIC_READINESS'):
   self.assertEqual(M.compose(p,DATA)[M.SERVICE],M.originals()[M.SERVICE])
 def test_no_cross_profile_promotion(self):
  with self.assertRaises(RuntimeError):M.validate(M.compose(PROFILE,DATA),'LIVE_DIAGNOSTIC_READINESS',DATA)
 def test_modified_retirement_rejected(self):
  b=M.compose(PROFILE,DATA);b[M.SERVICE]=b[M.SERVICE].replace(b'retire(key); page=null;',b'page=null;')
  with self.assertRaises(RuntimeError):M.validate(b,PROFILE,DATA)
 def runtime(self,variant,expected):
  blobs=M.compose(PROFILE,DATA)
  with tempfile.TemporaryDirectory(prefix='nexus-g3-protocol-offline-') as d:
   root=Path(d)
   for n,b in blobs.items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   script=r"""
import {syncBuiltinESMExports} from 'node:module';
import https from 'node:https';import http from 'node:http';import net from 'node:net';import tls from 'node:tls';
let network=0;const deny=()=>{network++;throw Error('OFFLINE_NETWORK');};
https.request=deny;https.get=deny;http.request=deny;http.get=deny;net.connect=deny;net.createConnection=deny;tls.connect=deny;globalThis.fetch=deny;syncBuiltinESMExports();
const {DEPLOYMENT:d}=await import('./lib/server/deployment-input.js');
const {createOfflineDiagnosticHandler}=await import('./lib/server/diagnostic-service.js');
const {createOfflineRegistration,createOfflineCurrentControl}=await import('./lib/server/provider-registration.js');
const {createOfflineCredentials}=await import('./lib/server/credential-custody.js');
const {createOfflineIo}=await import('./lib/server/stytch-transport.js');
const variant=process.argv[1],expected=process.argv[2];
const r={...d.provider,owner_user_id:'fixture-owner',source:'OFFLINE_SYNTHETIC',delivery_email:'owner@example.invalid'};
const registration=createOfflineRegistration(r);
const current=createOfflineCurrentControl(Object.fromEntries(['project_id','owner_user_id','project_generation','application_generation','owner_generation','binding_generation','deployment_revision'].map(k=>[k,r[k]])));
const credentials=createOfflineCredentials({STYTCH_PROJECT_ID:r.project_id,STYTCH_SECRET:'OFFLINE_CREDENTIAL_PLACEHOLDER'},registration);
const body={status_code:200,user_id:variant==='IDENTITY'?'fixture-nonowner':'fixture-owner',email_id:'fixture-email'};
const status={AUTH_REJECTED:401,RATE_LIMITED:429,PROVIDER_UNAVAILABLE:503}[variant]??200;
const reply=variant==='TIMEOUT'?{failure:'TIMEOUT'}:{status,headers:{'content-type':'application/json'},chunks:[variant==='MALFORMED_RESPONSE'?'not-json':JSON.stringify(body)]};
const io=createOfflineIo([reply],true);
const handler=createOfflineDiagnosticHandler({registration,current,credentials,io,keyset:d.keyset,publicKeys:d.keyset.keys,clock:()=>d.keyset.valid_from+1});
const base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
async function request(method,body,headers){const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(b){this.body=JSON.parse(b);}};await handler({method,url:'/api/diagnostic',body,headers},res);return res;}
const page=await request('GET',undefined,base);
const headers={...base,'content-type':'application/json','x-g3-csrf':page.body.csrf,cookie:page.headers['Set-Cookie'].split(';')[0]};
const failure=await request('POST',{action:'EMAIL_OTP_SEND'},headers);
if(failure.statusCode!==403||failure.body.result!=='DENY'||failure.body.error_class!==expected||failure.body.authority!=='NONE'||failure.body.real_admission!=='DISABLED'||failure.body.context_expires_at!==null||failure.body.csrf!==null)throw Error('FAILURE_PROJECTION');
const again=await request('POST',{action:'EMAIL_OTP_SEND'},headers);
if(again.body.error_class!=='RETIRED'||again.body.result!=='DENY'||io.requestShapes().length!==1||network!==0)throw Error('RETIREMENT_OR_RETRY');
const safe=JSON.stringify(failure.body);
if(['OFFLINE_CREDENTIAL_PLACEHOLDER',r.project_id,r.owner_user_id,'fixture-nonowner','fixture-email','owner@example.invalid','not-json'].some(v=>safe.includes(v)))throw Error('PROJECTION_LEAK');
"""
   environment={'SystemRoot':r'C:\Windows'} if Path(r'C:\Windows\System32').is_dir() else {}
   result=subprocess.run(['node','--input-type=module','-e',script,variant,expected],cwd=root,env=environment,capture_output=True)
   self.assertEqual(result.returncode,0,result.stderr.decode())
 def test_auth_rejected_and_retired(self):self.runtime('AUTH_REJECTED','AUTH_REJECTED')
 def test_rate_limit_and_retired(self):self.runtime('RATE_LIMITED','RATE_LIMITED')
 def test_provider_unavailable_and_retired(self):self.runtime('PROVIDER_UNAVAILABLE','PROVIDER_UNAVAILABLE')
 def test_timeout_and_retired(self):self.runtime('TIMEOUT','TIMEOUT')
 def test_wrong_owner_and_retired(self):self.runtime('IDENTITY','IDENTITY')
 def test_malformed_and_retired(self):self.runtime('MALFORMED_RESPONSE','MALFORMED_RESPONSE')

if __name__=='__main__':unittest.main()
