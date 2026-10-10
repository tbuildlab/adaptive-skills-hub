"""Native form and replay/boundary tests; synthetic browser/server IO only."""
from pathlib import Path
import copy,importlib.util,subprocess,tempfile,unittest
SPEC=importlib.util.spec_from_file_location('owner_form',Path(__file__).resolve().parents[1]/'scripts/verify_owner_form.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.BASE.BASE.reviewed_public_input()
RUNTIME=r"""
import {readFileSync} from 'node:fs';import {runInNewContext} from 'node:vm';
import {syncBuiltinESMExports} from 'node:module';import https from 'node:https';
const variant=process.argv[1];let network=0;
https.request=()=>{network++;throw Error('OFFLINE_NETWORK');};globalThis.fetch=https.request;syncBuiltinESMExports();
const {DEPLOYMENT:d}=await import('./lib/server/deployment-input.js');
if(variant.startsWith('SERVER_')) {
 const {createOfflineDiagnosticHandler}=await import('./lib/server/diagnostic-service.js');
 const {createOfflineRegistration,createOfflineCurrentControl}=await import('./lib/server/provider-registration.js');
 const {createOfflineCredentials}=await import('./lib/server/credential-custody.js');
 const {createOfflineIo}=await import('./lib/server/stytch-transport.js');
 const r={...d.provider,owner_user_id:'fixture-owner',source:'OFFLINE_SYNTHETIC',delivery_email:'owner@example.invalid'};
 const registration=createOfflineRegistration(r),current=createOfflineCurrentControl(Object.fromEntries(['project_id','owner_user_id','project_generation','application_generation','owner_generation','binding_generation','deployment_revision'].map(k=>[k,r[k]])));
 const credentials=createOfflineCredentials({STYTCH_PROJECT_ID:r.project_id,STYTCH_SECRET:'OFFLINE_CREDENTIAL_PLACEHOLDER'},registration),io=createOfflineIo([],true);
 const handler=createOfflineDiagnosticHandler({registration,current,credentials,io,keyset:d.keyset,clock:()=>d.keyset.valid_from+1});
 const base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
 async function request(method,body,headers){const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(b){this.body=JSON.parse(b);}};await handler({method,url:'/api/diagnostic',body,headers},res);return res;}
 const page=await request('GET',undefined,base),headers={...base,'content-type':'application/x-www-form-urlencoded',cookie:page.headers['Set-Cookie'].split(';')[0]};
 let body={action:'OWNER_TOTP_DISPLAY',csrf:page.body.csrf};
 if(variant==='SERVER_STRING')body=new URLSearchParams(body).toString();
 if(variant==='SERVER_DUPLICATE')body=new URLSearchParams(body).toString()+'&csrf='+page.body.csrf;
 if(variant==='SERVER_WRONG_CSRF')body.csrf='0'.repeat(64);
 if(variant==='SERVER_EXTRA')body.extra='OFFLINE_INVALID';
 if(variant==='SERVER_WRONG_ORIGIN')headers.origin='https://other.invalid';
 const result=await request('POST',body,headers);
 if(result.body.result!=='DENY'||result.body.authority!=='NONE'||result.body.real_admission!=='DISABLED'||result.body.context_expires_at!==null||result.body.csrf!==null||io.requestShapes().length!==0||network!==0)throw Error('PRE_FACTOR_FORM_DENY');
 // Unauthenticated view cannot create a private envelope or promote authority.
 if(JSON.stringify(result.body).includes('OFFLINE_CREDENTIAL_PLACEHOLDER'))throw Error('FORM_SECRET_LEAK');
 process.exit(0);
}
let requests=0,resolveFetch;const handlers={};
const nodes={status:{},evidence:{},operations:{disabled:true},'email-code':{value:''},
 'owner-channel-form':{addEventListener:(event,fn)=>{handlers[event]=fn;}},'owner-channel-csrf':{value:''}};
const browser={location:{origin:'https://nexus-g3-qual.vercel.app'},document:{getElementById:n=>nodes[n],querySelectorAll:()=>[],createElement:()=>{throw Error('SCRIPTED_FORM_FORBIDDEN');},body:{append:()=>{throw Error('SCRIPTED_FORM_FORBIDDEN');}}},
 fetch:()=>{requests++;return new Promise(resolve=>{resolveFetch=resolve;});}};
runInNewContext(readFileSync('./public/app.js','utf8')+'\nthis.call=call;',browser);
let prevented=0;const event=()=>({preventDefault(){prevented++;}});
if(variant==='EARLY') {
 handlers.submit(event());if(prevented!==1||requests!==1)throw Error('EARLY_FORM');process.exit(0);
}
const responseCsrf=variant==='NO_CSRF'?null:variant==='BAD_CSRF'?'OFFLINE_INVALID':'a'.repeat(64);
resolveFetch({json:async()=>({csrf:responseCsrf,adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true})});
await new Promise(resolve=>setImmediate(resolve));
if(nodes['owner-channel-csrf'].value!==(responseCsrf??''))throw Error('FORM_BINDING');
if(variant==='ORIGIN')browser.location.origin='https://other.invalid';
if(variant==='DISABLED')nodes.operations.disabled=true;
if(variant==='BUSY'){const pending=browser.call('PAGE');if(requests!==2)throw Error('PENDING');}
if(variant==='LOCAL_LOGOUT') {
 const pending=browser.call('LOCAL_LOGOUT');resolveFetch({json:async()=>({csrf:null,adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true})});await pending;
}
if(variant==='ERROR') {
 const pending=browser.call('PAGE');resolveFetch({json:async()=>{throw Error('OFFLINE_RESPONSE_ERROR');}});await pending;
}
const before=requests;handlers.submit(event());
const deny=['ORIGIN','DISABLED','BUSY','LOCAL_LOGOUT','ERROR','NO_CSRF','BAD_CSRF'].includes(variant);
if(prevented!==(deny?1:0)||requests!==before||network!==0)throw Error('FORM_GUARD');
if(!deny){
 if(nodes.operations.disabled!==true||nodes['owner-channel-csrf'].value!=='a'.repeat(64))throw Error('NATIVE_FORM_ACCEPT');
 handlers.submit(event());if(prevented!==1||requests!==before)throw Error('DUPLICATE_FORM');
}
"""

class OwnerFormArtifact(unittest.TestCase):
    def runtime(self,variant):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-owner-form-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            env={'SystemRoot':r'C:\Windows'} if Path(r'C:\Windows\System32').is_dir() else {}
            result=subprocess.run(['node','--input-type=module','-e',RUNTIME,variant],cwd=root,env=env,capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr.decode())
    def reject(self,b):
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_exact_inventory(self):self.assertEqual(M.validate(M.compose(DATA),DATA)['files'],19)
    def test_exact_three_file_change_from_previous(self):
        old=M.BASE.compose(DATA);new=M.compose(DATA)
        self.assertEqual({n for n,b in old.items() if b!=new[n]},{M.BASE.BASE.INPUT,'public/index.html','public/app.js'})
    def test_old_request_stage_hash_preserved(self):self.assertEqual(M.BASE.validate(M.BASE.compose(DATA),DATA)['zip_sha256'],'9c1ff95de2f2c096baac7abfa3e19d4fdeeab39b62c6cdd3b51defc54513540d')
    def test_server_channel_unchanged(self):self.assertEqual(M.compose(DATA)[M.BASE.BASE.SERVICE],M.BASE.compose(DATA)[M.BASE.BASE.SERVICE])
    def test_review_interval_unchanged(self):
        r=M.validate(M.compose(DATA),DATA)
        for name in ('valid_from','valid_until'):self.assertEqual(r['public_review_'+name],DATA['keyset'][name])
    def test_wrong_registered_input_rejected(self):
        d=copy.deepcopy(DATA);d['provider']['owner_user_id']='fixture-impostor'
        with self.assertRaises(RuntimeError):M.compose(d)
    def test_old_profile_cannot_promote(self):self.reject(M.BASE.compose(DATA))
    def test_scripted_submit_rejected(self):
        b=M.compose(DATA);b['public/app.js']+=b'\nownerForm.submit();';self.reject(b)
    def test_arbitrary_form_route_rejected(self):
        b=M.compose(DATA);b['public/index.html']=b['public/index.html'].replace(b'action="/api/diagnostic"',b'action="https://other.invalid"');self.reject(b)
    def test_get_secret_url_rejected(self):
        b=M.compose(DATA);b['public/index.html']=b['public/index.html'].replace(b'method="POST"',b'method="GET"');self.reject(b)
    def test_one_use_removal_rejected(self):
        b=M.compose(DATA);b['lib/server/owner-channel.js']=b['lib/server/owner-channel.js'].replace(b'retireOwnerEnvelope(handle);',b'/* unsafe */');self.reject(b)
    def test_client_owner_identifier_rejected(self):
        b=M.compose(DATA);b['public/app.js']+=DATA['provider']['owner_user_id'].encode();self.reject(b)
    def test_extra_env_path_rejected(self):
        b=M.compose(DATA);b['.env']=b'OFFLINE_INVALID';self.reject(b)
    def test_deterministic_package(self):self.assertEqual(M.BASE.BASE.HISTORICAL.frozen_zip(M.compose(DATA)),M.BASE.BASE.HISTORICAL.frozen_zip(dict(reversed(list(M.compose(DATA).items())))))
    def test_native_form_accepts_only_current_local_context(self):self.runtime('ACCEPT')
    def test_early_form_denied(self):self.runtime('EARLY')
    def test_cross_origin_form_denied(self):self.runtime('ORIGIN')
    def test_disabled_form_denied(self):self.runtime('DISABLED')
    def test_inflight_form_denied(self):self.runtime('BUSY')
    def test_logout_clears_form_context(self):self.runtime('LOCAL_LOGOUT')
    def test_error_clears_form_context(self):self.runtime('ERROR')
    def test_missing_csrf_form_denied(self):self.runtime('NO_CSRF')
    def test_malformed_csrf_form_denied(self):self.runtime('BAD_CSRF')
    def test_pre_factor_form_denies_without_provider(self):self.runtime('SERVER_OBJECT')
    def test_pre_factor_urlencoded_form_denies_without_provider(self):self.runtime('SERVER_STRING')
    def test_duplicate_form_members_never_authorize(self):self.runtime('SERVER_DUPLICATE')
    def test_wrong_form_csrf_never_authorizes(self):self.runtime('SERVER_WRONG_CSRF')
    def test_extra_form_members_never_authorize(self):self.runtime('SERVER_EXTRA')
    def test_cross_origin_form_never_authorizes(self):self.runtime('SERVER_WRONG_ORIGIN')

if __name__=='__main__':unittest.main()
