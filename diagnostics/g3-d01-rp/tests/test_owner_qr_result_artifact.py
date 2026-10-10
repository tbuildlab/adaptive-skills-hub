"""Offline synthetic response projection and private QR retirement tests."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('qr_result',HERE/'scripts/verify_owner_qr_result.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.G3.reviewed_public_input()
CLIENT=r'''
import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const variant=process.argv[1],T=1791564000000;
let now=T,calls=[],events={},children=[],seedRemoved=false,cancelled=0;
const input={value:'000000'},seed={textContent:'A'.repeat(32),remove(){seedRemoved=true;}};
const canvas={width:0,height:0,getContext(){return {fillRect(){},clearRect(){}};}};
const buttons={confirm:{addEventListener(k,f){this[k]=f;}},cancel:{addEventListener(k,f){this[k]=f;}}};
const metas=[{content:'a'.repeat(64),remove(){}},{content:String(T+300000),remove(){}}];
const root={querySelectorAll(){return [input];},replaceChildren(...c){children=c;}};
const document={visibilityState:'visible',createElement(tag){return {tag};},
 getElementById(id){return {code:input,seed,'totp-qr':canvas,'owner-transient':root,...buttons}[id];},
 querySelector(s){return s.includes('csrf')?metas[0]:metas[1];},querySelectorAll(){return metas;}};
let response={diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',
 qualified_live:false,adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true,
 result:'PASS',error_class:'NONE',context_expires_at:T+300000,
 csrf:'SYNTHETIC_DO_NOT_RENDER',unexpected:'SYNTHETIC_UNSAFE_FREE_TEXT'};
if(variant==='DENY'){response.result='DENY';response.error_class='AUTH_REJECTED';response.context_expires_at=null;}
if(variant==='RETIRED'){response.result='DENY';response.error_class='RETIRED';response.context_expires_at=null;}
if(variant==='FREE_TEXT'){response.result='DENY';response.error_class='SYNTHETIC_UNSAFE_FREE_TEXT';}
if(variant==='DENY_NONE'){response.result='DENY';}
if(variant==='AUTHORITY')response.authority='REAL';
if(variant==='REAL_ADMISSION')response.real_admission='ENABLED';
if(variant==='QUALIFIED')response.qualified_live=true;
if(variant==='WRONG_MODE')response.adapter_mode='FAKE_DISABLED';
if(variant==='DISABLED')response.live_diagnostic_enabled=false;
if(variant==='MISSING')delete response.diagnostic;
if(variant==='WRONG_RESULT')response.result='UNKNOWN';
if(variant==='EXTENDED')response.context_expires_at=T+300001;
if(variant==='EXPIRED')response.context_expires_at=T;
if(variant==='MISSING_EXPIRY')response.context_expires_at=null;
if(variant==='NOT_OBJECT')response=null;
const c=vm.createContext({document,window:{addEventListener(k,f){events[k]=f;}},URLSearchParams,
 Date:{now(){return now;}},location:{origin:'https://nexus-g3-qual.vercel.app',replace(){throw Error('REDIRECT_FORBIDDEN');}},
 setTimeout(){},fetch:async(url,options)=>{
  assert.equal(url,'/api/diagnostic');assert.equal(input.value,'');assert.equal(canvas.width,0);assert.ok(seedRemoved);
  calls.push(JSON.parse(options.body));
  if(variant==='NETWORK')throw Error('SYNTHETIC_UNSAFE_FREE_TEXT');
  return {ok:variant!=='HTTP_FAIL',body:{async cancel(){cancelled++;}},async json(){
   if(variant==='JSON_FAIL')throw Error('SYNTHETIC_UNSAFE_FREE_TEXT');
   if(variant==='EXPIRES_DURING_RESPONSE')now=T+300000;
   return response;}};
 },console:new Proxy({}, {get(){throw Error('LOGGING_FORBIDDEN');}})});
vm.runInContext(fs.readFileSync('public/qrcodegen.js','utf8').replace('export { qrcodegen };',''),c);
vm.runInContext(fs.readFileSync('public/owner-transient.js','utf8').replace("import { qrcodegen } from './qrcodegen.js';",'').replace('export function paintOwnerQr','function paintOwnerQr'),c);
if(variant==='HIDDEN'){document.visibilityState='hidden';events.visibilitychange();}
else if(variant==='CANCEL')buttons.cancel.click();
else buttons.confirm.click();
await new Promise(resolve=>setImmediate(resolve));
assert.equal(calls.length,1);
assert.equal(input.value,'');assert.equal(canvas.width,0);
if(variant==='HIDDEN'){assert.equal(calls[0].action,'CANCEL');assert.equal(children.length,0);assert.equal(cancelled,1);}
else {
 assert.equal(children.length,2);assert.equal(children[0].id,'evidence');assert.equal(children[1].href,'/');
 const out=JSON.parse(children[0].textContent);assert.equal(out.authority,'NONE');assert.equal(out.real_admission,'DISABLED');assert.equal(out.qualified_live,false);
 assert.equal(out.result,variant==='PASS'?'PASS':'DENY');
 if(variant==='DENY')assert.equal(out.error_class,'AUTH_REJECTED');
 if(variant==='RETIRED')assert.equal(out.error_class,'RETIRED');
 assert.equal(Object.keys(out).length,9);
 assert.equal(children[0].textContent.includes('SYNTHETIC_'),false);
 assert.equal(children[0].textContent.includes('csrf'),false);
}
buttons.confirm.click();events.pagehide();assert.equal(calls.length,1);assert.equal(children.length,0);
'''

class OwnerQrResultArtifact(unittest.TestCase):
    def run_client(self,variant):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-qr-result-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',CLIENT,variant],cwd=root,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic result assertion failed; no raw response retained')
    def test_closed_inventory_and_profiles(self):
        for profile in M.PROFILES:self.assertEqual(M.validate(M.compose(DATA,profile),DATA,profile)['files'],20)
    def test_exact_two_file_delta(self):
        old=M.BASE.compose(DATA);new=M.compose(DATA)
        self.assertEqual({n for n in new if new[n]!=old[n]},{M.G3.INPUT,M.CLIENT})
    def test_no_window_or_generation_change(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
        for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
    def test_mutation_denied(self):
        blobs=M.compose(DATA);blobs[M.CLIENT]+=b'\n// mutation\n'
        with self.assertRaises(RuntimeError):M.validate(blobs,DATA)
    def test_historical_qr_is_frozen(self):
        self.assertEqual(M.BASE.validate(M.BASE.compose(M.G3.generation3_input(),M.PROFILES[1]),M.G3.generation3_input(),M.PROFILES[1])['zip_sha256'],'ac38bd9323c2fb5684a432c90a342a610abb1645e5c35fde5abb97796555b8ec')

for variant in ('PASS','DENY','RETIRED','FREE_TEXT','DENY_NONE','AUTHORITY','REAL_ADMISSION','QUALIFIED',
 'WRONG_MODE','DISABLED','MISSING','WRONG_RESULT','EXTENDED','EXPIRED','MISSING_EXPIRY','NOT_OBJECT',
 'NETWORK','JSON_FAIL','HTTP_FAIL','EXPIRES_DURING_RESPONSE','CANCEL','HIDDEN'):
    setattr(OwnerQrResultArtifact,'test_client_'+variant.lower(),lambda self,v=variant:self.run_client(v))
