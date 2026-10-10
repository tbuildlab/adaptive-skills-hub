"""Synthetic current-factor UI and accepted transport regressions; no live IO."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('existing_totp',HERE/'scripts/verify_existing_totp.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.G3.reviewed_public_input()
CLIENT=r'''
import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const variant=process.argv[1],T=1791564000000;
let now=T,calls=[],events={},buttons={},pending=false;
const email={value:''},totp={value:''},evidence={textContent:''},controls={disabled:true};
for(const action of ['EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE','LOCAL_LOGOUT'])buttons[action]={dataset:{action},addEventListener(k,f){this[k]=f;}};
const document={visibilityState:'visible',getElementById(id){return {status:{},evidence,operations:controls,'email-code':email,'totp-code':totp}[id];},
 querySelectorAll(){return Object.values(buttons);}};
function reply(){return {diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',qualified_live:false,
 adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true,result:'PASS',error_class:'NONE',context_expires_at:T+300000,csrf:'a'.repeat(64),unexpected:'UNSAFE_SYNTHETIC'};}
let response=reply();
const c=vm.createContext({document,window:{addEventListener(k,f){events[k]=f;}},Date:{now(){return now;}},setTimeout(){},
 location:{origin:variant==='ORIGIN'?'https://other.invalid':'https://nexus-g3-qual.vercel.app'},
 fetch:async(url,options)=>{assert.equal(url,'/api/diagnostic');assert.equal(email.value,'');assert.equal(totp.value,'');
  calls.push(options.method==='POST'?JSON.parse(options.body):null);
  if(calls.length>1&&variant==='NETWORK')throw Error('UNSAFE_SYNTHETIC');
  if(calls.length>1&&variant==='BUSY')await new Promise(resolve=>setImmediate(resolve));
  return {ok:variant!=='HTTP_FAIL'||calls.length===1,async json(){if(calls.length>1&&variant==='JSON_FAIL')throw Error('UNSAFE_SYNTHETIC');return response;}};
 },console:new Proxy({}, {get(){throw Error('LOGGING_FORBIDDEN');}})});
vm.runInContext(fs.readFileSync('public/app.js','utf8'),c);await new Promise(resolve=>setImmediate(resolve));
if(variant==='ORIGIN'){assert.equal(calls.length,0);assert.equal(controls.disabled,true);}
else{
 assert.equal(calls.length,1);assert.equal(controls.disabled,false);
 email.value='000000';totp.value='000000';response=reply();
 if(variant==='INVALID')totp.value='bad';
 if(variant==='EXPIRED')now=T+300000;
 if(variant==='ROLLBACK')now=T-1;
 if(variant==='EXTENDED')response.context_expires_at=T+300001;
 if(variant==='DENY'){response.result='DENY';response.error_class='AUTH_REJECTED';response.context_expires_at=null;}
 if(variant==='AUTHORITY')response.authority='REAL';
 if(variant==='ADMISSION')response.real_admission='ENABLED';
 if(variant==='QUALIFIED')response.qualified_live=true;
 if(variant==='MODE')response.adapter_mode='FAKE_DISABLED';
 if(variant==='FREE_TEXT')response.error_class='UNSAFE_SYNTHETIC';
 if(variant==='CSRF')response.csrf='invalid';
 if(variant==='MISSING_EXPIRY')response.context_expires_at=null;
 if(variant==='HIDDEN'){document.visibilityState='hidden';events.visibilitychange();assert.equal(totp.value,'');assert.equal(email.value,'');}
 else if(variant==='UNLOAD'){events.pagehide();assert.equal(totp.value,'');assert.equal(email.value,'');}
 else{
  buttons[variant==='EMAIL'?'EMAIL_OTP_AUTHENTICATE':'TOTP_AUTHENTICATE'].click();
  if(variant==='BUSY')buttons.TOTP_AUTHENTICATE.click();
  await new Promise(resolve=>setImmediate(resolve));await new Promise(resolve=>setImmediate(resolve));
  if(['INVALID','EXPIRED','ROLLBACK'].includes(variant))assert.equal(calls.length,1);
  else{assert.equal(calls.length,2);assert.deepEqual(Object.keys(calls[1]).sort(),['action','code']);
   assert.equal(calls[1].action,variant==='EMAIL'?'EMAIL_OTP_AUTHENTICATE':'TOTP_AUTHENTICATE');
   const out=JSON.parse(evidence.textContent);assert.equal(out.result,['PASS','EMAIL','BUSY'].includes(variant)?'PASS':'DENY');
   assert.equal(out.authority,'NONE');assert.equal(out.real_admission,'DISABLED');assert.equal(out.qualified_live,false);
   assert.equal(evidence.textContent.includes('UNSAFE'),false);assert.equal(evidence.textContent.includes('csrf'),false);}
  assert.equal(email.value,'');assert.equal(totp.value,'');
 }
}
'''

class ExistingTotpArtifact(unittest.TestCase):
    def run_client(self,variant):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-current-totp-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',CLIENT,variant],cwd=root,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic UI assertion failed; no raw response retained')
    def test_inventory_profiles(self):
        for profile in M.PROFILES:self.assertEqual(M.validate(M.compose(DATA,profile),DATA,profile)['files'],20)
    def test_only_input_and_public_delta(self):
        old=M.BASE.compose(DATA);new=M.compose(DATA)
        self.assertEqual({n for n in new if new[n]!=old[n]},{M.G3.INPUT,'public/index.html','public/app.js'})
        self.assertEqual(new[M.G3.SERVICE],old[M.G3.SERVICE])
    def test_no_enrollment_button(self):
        html=M.compose(DATA)['public/index.html']
        self.assertNotIn(b'data-action="TOTP_CREATE"',html)
        self.assertNotIn(b'id="show-owner"',html)
        self.assertIn(b'data-action="TOTP_AUTHENTICATE"',html)
    def test_review_and_generations_unchanged(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
        for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
    def test_mutation_denied(self):
        blobs=M.compose(DATA);blobs[M.G3.SERVICE]+=b'\n// mutation\n'
        with self.assertRaises(RuntimeError):M.validate(blobs,DATA)
    def run_transport(self,tail):
        prefix=(HERE/'tests/integration.test.js').read_text().split("test('01 current service")[0]
        r=subprocess.run(['node','--input-type=module','-e',prefix+tail],cwd=HERE/'tests',capture_output=True,timeout=20)
        self.assertEqual(r.returncode,0,'Synthetic transport assertion failed; no raw response retained')
    def test_authenticate_without_enrollment(self):
        self.run_transport("const f=await ready();assert.equal(f.backend.contextInfo().two,true);assert.equal(f.io.requestShapes().some(s=>s.op==='TOTP_CREATE'),false);f.backend.retire();")
    def test_no_primary_denies_before_io(self):
        self.run_transport("const f=fixture([]);deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.io.requestShapes().length,0);")
    def test_duplicate_authenticate_denies(self):
        self.run_transport("const f=await ready();const count=f.io.requestShapes().length;deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.io.requestShapes().length,count);")
    def test_expired_context_denies(self):
        self.run_transport("const f=await primary(fixture([sent(),reply(raw())]));f.time(T+300000);deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.io.requestShapes().length,2);")

for variant in ('PASS','EMAIL','BUSY','ORIGIN','INVALID','EXPIRED','ROLLBACK','EXTENDED','DENY',
 'AUTHORITY','ADMISSION','QUALIFIED','MODE','FREE_TEXT','CSRF','MISSING_EXPIRY','NETWORK','JSON_FAIL','HTTP_FAIL','HIDDEN','UNLOAD'):
    setattr(ExistingTotpArtifact,'test_client_'+variant.lower(),lambda self,v=variant:self.run_client(v))
