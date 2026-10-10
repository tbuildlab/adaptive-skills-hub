"""Closed diagnostics, retirement and client races; synthetic IO only."""
from pathlib import Path
import copy, importlib.util, subprocess, tempfile, unittest

SPEC=importlib.util.spec_from_file_location('request_stage',Path(__file__).resolve().parents[1]/'scripts/verify_request_stage.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.BASE.reviewed_public_input()

RUNTIME=r"""
import {syncBuiltinESMExports} from 'node:module';
import https from 'node:https';import http from 'node:http';import net from 'node:net';import tls from 'node:tls';
import {readFileSync} from 'node:fs';import {runInNewContext} from 'node:vm';
let network=0;const trap=()=>{network++;throw Error('OFFLINE_NETWORK');};
https.request=trap;https.get=trap;http.request=trap;http.get=trap;net.connect=trap;net.createConnection=trap;tls.connect=trap;
globalThis.fetch=trap;syncBuiltinESMExports();
const {DEPLOYMENT:d}=await import('./lib/server/deployment-input.js');
const {createOfflineDiagnosticHandler,createDiagnosticHandler}=await import('./lib/server/diagnostic-service.js');
const {createOfflineRegistration,createOfflineCurrentControl}=await import('./lib/server/provider-registration.js');
const {createOfflineCredentials}=await import('./lib/server/credential-custody.js');
const {createOfflineIo,createOfflineStytchTransport}=await import('./lib/server/stytch-transport.js');
const {pinnedKeys}=await import('./lib/server/pinned-identity.js');
const {safeResult}=await import('./lib/server/pre-secret-policy.js');
const variant=process.argv[1],expected=process.argv[2];
if(variant.startsWith('LIVE_MISSING_')) {
 Date.now=()=>d.keyset.valid_from+1;let projectReads=0,secretReads=0;
 process.env=new Proxy(Object.create(null),{get(_t,n){
  if(n==='STYTCH_PROJECT_ID'){projectReads++;return variant==='LIVE_MISSING_PROJECT'?undefined:d.provider.project_id;}
  if(n==='STYTCH_SECRET'){secretReads++;return undefined;}return undefined;
 },ownKeys(){throw Error('ENV_ENUMERATION');}});
 const live=createDiagnosticHandler(),base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
 const request=async(method,body,headers)=>{const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(b){this.body=JSON.parse(b);}};await live({method,url:'/api/diagnostic',body,headers},res);return res;};
 const page=await request('GET',undefined,base);
 if(projectReads!==0||secretReads!==0)throw Error('GET_CREDENTIAL_READ');
 const result=await request('POST',{action:'EMAIL_OTP_SEND'},{...base,'content-type':'application/json','x-g3-csrf':page.body.csrf,cookie:page.headers['Set-Cookie'].split(';')[0]});
 if(result.body.error_class!==expected||result.body.result!=='DENY'||result.body.authority!=='NONE'||result.body.real_admission!=='DISABLED'||projectReads!==1||secretReads!==(variant==='LIVE_MISSING_PROJECT'?0:1)||network!==0)throw Error('LIVE_FAIL_CLOSED');
 process.exit(0);
}
const r={...d.provider,owner_user_id:'fixture-owner',source:'OFFLINE_SYNTHETIC',delivery_email:'owner@example.invalid'};
const registration=createOfflineRegistration(r);
const current=createOfflineCurrentControl(Object.fromEntries(['project_id','owner_user_id','project_generation','application_generation','owner_generation','binding_generation','deployment_revision'].map(k=>[k,r[k]])));
const credentials=createOfflineCredentials({STYTCH_PROJECT_ID:r.project_id,STYTCH_SECRET:'OFFLINE_CREDENTIAL_PLACEHOLDER'},registration);
const io=createOfflineIo([{status:200,headers:{'content-type':'application/json'},chunks:[JSON.stringify({status_code:200,user_id:'fixture-owner',email_id:'fixture-email'})]}],true);
let now=d.keyset.valid_from+1;
const input={registration,current,credentials,io,keyset:d.keyset,publicKeys:d.keyset.keys,clock:()=>now};
const handler=createOfflineDiagnosticHandler(input);
const base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
async function request(h,method,body,headers,url='/api/diagnostic'){
 const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(b){this.body=JSON.parse(b);}};
 await h({method,url,body,headers},res);return res;
}
const page=await request(handler,'GET',undefined,base);
const headers={...base,'content-type':'application/json','x-g3-csrf':page.body.csrf,cookie:page.headers['Set-Cookie'].split(';')[0]};
let h={...headers},body={action:'EMAIL_OTP_AUTHENTICATE',code:'000000'},url='/api/diagnostic',selected=handler;
let expectedCalls=0;
if(variant.startsWith('CLIENT_')) {
 let requests=0,resolveFetch;const listeners={};
 const nodes={status:{},evidence:{},operations:{disabled:false},'email-code':{value:variant==='CLIENT_EMPTY'?'':variant==='CLIENT_SHAPE'?'abc':'000000'},'show-owner':{addEventListener(){}}};
 const browser={location:{origin:base.origin},document:{getElementById:n=>nodes[n],querySelectorAll:()=>[],createElement:()=>{throw Error('UNEXPECTED_FORM');}},
 fetch:()=>{requests++;return new Promise(resolve=>{resolveFetch=resolve;});}};
 // Startup GET is synthetic and resolved before the private input test.
 runInNewContext(readFileSync('./public/app.js','utf8')+'\nthis.call=call;',browser);
 resolveFetch({json:async()=>({csrf:'a'.repeat(64),adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true})});
 await new Promise(resolve=>setImmediate(resolve));requests=0;
 nodes['email-code'].value=variant==='CLIENT_EMPTY'?'':variant==='CLIENT_SHAPE'?'abc':'000000';
 if(variant==='CLIENT_DOUBLE') {
  const first=browser.call('EMAIL_OTP_AUTHENTICATE');const second=browser.call('EMAIL_OTP_AUTHENTICATE');
  if(requests!==1||nodes.operations.disabled!==true||nodes['email-code'].value!=='')throw Error('CLIENT_RACE');
  resolveFetch({json:async()=>({csrf:'b'.repeat(64),adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true,result:'DENY',authority:'NONE',real_admission:'DISABLED'})});
  await Promise.all([first,second]);if(nodes.operations.disabled)throw Error('CLIENT_RECOVERY');
 } else {
  await browser.call('EMAIL_OTP_AUTHENTICATE');
  const e=JSON.parse(nodes.evidence.textContent);
  if(requests!==0||e.error_class!=='REQUEST_CODE_SHAPE'||e.authority!=='NONE'||e.result!=='DENY'||e.evidence_source!=='LOCAL_INPUT_VALIDATION_ONLY')throw Error('CLIENT_LOCAL_DENY');
 }
 if(network!==0)throw Error('CLIENT_NETWORK');process.exit(0);
}
if(variant==='COOKIE_MISSING')delete h.cookie;
if(variant==='COOKIE_BAD')h.cookie='__Host-g3d01=OFFLINE_INVALID';
if(variant==='COOKIE_DUPLICATE')h.cookie=headers.cookie+'; '+headers.cookie;
if(variant==='CSRF_MISSING')delete h['x-g3-csrf'];
if(variant==='CSRF_WRONG')h['x-g3-csrf']='0'.repeat(64);
if(variant==='ORIGIN')h.origin='https://other.invalid';
if(variant==='HOST')h.host='other.invalid';
if(variant==='CROSS_SITE')h['sec-fetch-site']='cross-site';
if(variant==='ROUTE')url='/api/other';
if(variant==='CONTENT_TYPE')h['content-type']='text/plain';
if(variant==='BODY_NULL')body=null;
if(variant==='BODY_STRING')body='OFFLINE_INVALID';
if(variant==='BODY_EXTRA')body.extra='OFFLINE_INVALID';
if(variant==='SIZE')body.extra='X'.repeat(4096);
if(variant==='CODE_MEMBER')delete body.code;
if(variant==='CODE_TYPE')body.code=0;
if(variant==='CODE_SHAPE')body.code='abc';
if(variant==='ORDER')body={action:'PAGE'};
if(variant==='RESTART')selected=createOfflineDiagnosticHandler(input);
if(variant==='EXPIRED')now+=300000;
if(variant==='ACTION'){
 const send=await request(handler,'POST',{action:'EMAIL_OTP_SEND'},headers);
 if(send.body.result!=='PASS')throw Error('SYNTHETIC_SEND');body={action:'UNKNOWN_ACTION'};expectedCalls=1;
}
if(variant==='METHOD_STATE'){
 const backend=createOfflineStytchTransport({...input,publicKeys:pinnedKeys(d.keyset,r,now)});
 const result=await backend.EMAIL_OTP_AUTHENTICATE({code:'000000'});
 if(result.error_class!=='REQUEST_METHOD_STATE'||result.result!=='DENY'||io.requestShapes().length!==0||network!==0)throw Error('METHOD_GUARD');
 process.exit(0);
}
if(variant==='CONTINUITY'){
 body={action:'LOCAL_LOGOUT'};
 const result=await request(handler,'POST',body,h);
 if(result.body.error_class!=='RETIRED'||result.body.result!=='DENY'||result.body.context_expires_at!==null||result.body.csrf!==null||io.requestShapes().length!==0)throw Error('CONTINUITY');
 if(result.headers['Set-Cookie']?.includes('Max-Age=0')!==true)throw Error('COOKIE_RETIREMENT');
 process.exit(0);
}
const failure=await request(selected,'POST',body,h,url);
if(failure.statusCode!==403||failure.body.result!=='DENY'||failure.body.error_class!==expected||failure.body.authority!=='NONE'||failure.body.real_admission!=='DISABLED'||failure.body.context_expires_at!==null||failure.body.csrf!==null)throw Error('REQUEST_STAGE_PROJECTION_'+variant);
const safe=JSON.stringify(failure.body);
if(['OFFLINE_CREDENTIAL_PLACEHOLDER',r.project_id,r.owner_user_id,'fixture-email','owner@example.invalid','OFFLINE_INVALID','000000',headers['x-g3-csrf']].some(v=>safe.includes(v)))throw Error('PROJECTION_LEAK');
// Unauthenticated failures precede key identification. They cannot retire an
// unrelated page; repeating the same malformed request still denies before IO.
const unidentified=['COOKIE_BAD','COOKIE_DUPLICATE','COOKIE_MISSING','ORIGIN','HOST','CROSS_SITE','ROUTE'].includes(variant);
const after=await request(selected,'POST',{action:'EMAIL_OTP_SEND'},unidentified?h:headers,unidentified?url:'/api/diagnostic');
if(after.body.error_class!==(unidentified?expected:'RETIRED')||io.requestShapes().length!==expectedCalls||network!==0)throw Error('RETIREMENT_OR_RETRY');
if(safeResult('untrusted free text').error_class!=='UNKNOWN')throw Error('UNKNOWN_ENUM');
"""

class RequestStageArtifact(unittest.TestCase):
    def runtime(self,variant,expected='UNUSED'):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-request-stage-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            env={'SystemRoot':r'C:\Windows'} if Path(r'C:\Windows\System32').is_dir() else {}
            result=subprocess.run(['node','--input-type=module','-e',RUNTIME,variant,expected],cwd=root,env=env,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode())
    def test_exact_19_files(self):self.assertEqual(M.validate(M.compose(DATA),DATA)['files'],19)
    def test_deterministic_zip(self):self.assertEqual(M.BASE.HISTORICAL.frozen_zip(M.compose(DATA)),M.BASE.HISTORICAL.frozen_zip(M.compose(DATA)))
    def test_historical_hash_unchanged(self):
        b=M.BASE.compose('LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT',DATA)
        self.assertEqual(M.BASE.validate(b,'LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT',DATA)['zip_sha256'],'ca868970d5a55a870c4e3be9d618bc6bfe3eae6a00a51cd988a331568b451c88')
    def test_no_cross_profile_acceptance(self):
        with self.assertRaises(RuntimeError):M.validate(M.BASE.compose('LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT',DATA),DATA)
    def test_no_arbitrary_registration(self):
        d=copy.deepcopy(DATA);d['provider']['owner_user_id']='fixture-impostor'
        with self.assertRaises(RuntimeError):M.compose(d)
    def test_no_expiry_extension(self):
        b=M.compose(DATA);b[M.BASE.SERVICE]=b[M.BASE.SERVICE].replace(b'now+300000',b'now+600000')
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_no_retirement_removal(self):
        b=M.compose(DATA);b[M.BASE.SERVICE]=b[M.BASE.SERVICE].replace(b'if(key) retire(key);',b'/* forbidden */')
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_no_extra_env_file(self):
        b=M.compose(DATA);b['.env']=b'OFFLINE_INVALID'
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_missing_cookie(self):self.runtime('COOKIE_MISSING','REQUEST_CONTEXT_MISSING')
    def test_bad_cookie(self):self.runtime('COOKIE_BAD','REQUEST_COOKIE')
    def test_duplicate_cookie(self):self.runtime('COOKIE_DUPLICATE','REQUEST_COOKIE')
    def test_missing_csrf(self):self.runtime('CSRF_MISSING','REQUEST_CSRF')
    def test_wrong_csrf(self):self.runtime('CSRF_WRONG','REQUEST_CSRF')
    def test_wrong_origin(self):self.runtime('ORIGIN','REQUEST_ORIGIN')
    def test_wrong_host(self):self.runtime('HOST','REQUEST_ORIGIN')
    def test_cross_site(self):self.runtime('CROSS_SITE','REQUEST_ORIGIN')
    def test_wrong_route(self):self.runtime('ROUTE','REQUEST_ROUTE')
    def test_wrong_content_type(self):self.runtime('CONTENT_TYPE','REQUEST_CONTENT_TYPE')
    def test_null_body(self):self.runtime('BODY_NULL','REQUEST_BODY')
    def test_string_body(self):self.runtime('BODY_STRING','REQUEST_BODY')
    def test_extra_body_field(self):self.runtime('BODY_EXTRA','REQUEST_BODY')
    def test_oversize_body(self):self.runtime('SIZE','REQUEST_SIZE')
    def test_missing_code_member(self):self.runtime('CODE_MEMBER','REQUEST_CODE_MEMBER')
    def test_code_type(self):self.runtime('CODE_TYPE','REQUEST_CODE_SHAPE')
    def test_code_shape(self):self.runtime('CODE_SHAPE','REQUEST_CODE_SHAPE')
    def test_wrong_order(self):self.runtime('ORDER','REQUEST_ORDER')
    def test_unknown_action(self):self.runtime('ACTION','REQUEST_ACTION')
    def test_restart_never_restores_context(self):self.runtime('RESTART','RETIRED')
    def test_expiry_still_retires(self):self.runtime('EXPIRED','RETIRED')
    def test_no_method_state(self):self.runtime('METHOD_STATE')
    def test_local_retirement_proves_continuity_without_provider(self):self.runtime('CONTINUITY')
    def test_client_empty_code_no_submit(self):self.runtime('CLIENT_EMPTY')
    def test_client_bad_shape_no_submit(self):self.runtime('CLIENT_SHAPE')
    def test_client_double_click_one_submission(self):self.runtime('CLIENT_DOUBLE')
    def test_live_missing_project_denies_without_secret_or_network(self):self.runtime('LIVE_MISSING_PROJECT','PROJECT_CONFIG_MISSING')
    def test_live_missing_secret_denies_without_network(self):self.runtime('LIVE_MISSING_SECRET','SECRET_CONFIG_MISSING')

if __name__=='__main__':unittest.main()
