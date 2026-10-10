"""Closed stage projection, request attribution and unchanged MFA adversaries."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('ceremony_builder',HERE/'scripts/verify_ceremony_stage.py')
B=module('ceremony_mfa_tests',HERE/'tests/test_mfa_transition_artifact.py')
DATA=M.G3.reviewed_public_input()

class CeremonyStageArtifact(B.MfaTransitionArtifact):
 def invoke(self,script):
  with tempfile.TemporaryDirectory(prefix='nexus-g3-ceremony-offline-') as d:
   root=Path(d)
   for n,b in M.compose(DATA).items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   (root/'tests').mkdir()
   r=subprocess.run(['node','--input-type=module','-e',B.PREFIX+script],cwd=root/'tests',capture_output=True,timeout=20)
   self.assertEqual(r.returncode,0,'Synthetic stage/MFA assertion failed; raw output not retained')
 def test_no_primary_attributed_without_network(self):
  self.invoke("const f=fixture([]);const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);assert.equal(o.error_class,'REQUEST_TOTP_NO_PRIMARY');assert.equal(f.io.requestShapes().length,0);assert.equal(f.backend.contextInfo().retired,true);")
 def test_email_sent_is_not_primary(self):
  self.invoke("const f=fixture([sent()]);pass(await f.backend.EMAIL_OTP_SEND());const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);assert.equal(o.error_class,'REQUEST_TOTP_NO_PRIMARY');assert.equal(f.io.requestShapes().length,1);")
 def test_duplicate_final_mfa_attributed(self):
  self.invoke("const f=await transition();const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);assert.equal(o.error_class,'REQUEST_TOTP_ALREADY_FINAL');assert.equal(f.io.requestShapes().length,5);")
 def test_missing_code_attributed_after_primary(self):
  self.invoke("const f=await primary(fixture([sent(),reply(raw())]));const o=await f.backend.TOTP_AUTHENTICATE({});deny(o);assert.equal(o.error_class,'REQUEST_TOTP_CODE_SHAPE');assert.equal(f.io.requestShapes().length,2);")
 def test_bad_code_attributed_after_primary(self):
  self.invoke("const f=await primary(fixture([sent(),reply(raw())]));const o=await f.backend.TOTP_AUTHENTICATE({code:'bad'});deny(o);assert.equal(o.error_class,'REQUEST_TOTP_CODE_SHAPE');")
 def test_duplicate_send_attributed(self):
  self.invoke("const f=fixture([sent()]);pass(await f.backend.EMAIL_OTP_SEND());const o=await f.backend.EMAIL_OTP_SEND();deny(o);assert.equal(o.error_class,'REQUEST_EMAIL_ALREADY_STARTED');assert.equal(f.io.requestShapes().length,1);")
 def test_primary_only_point_attributed(self):
  self.invoke("const f=await primary(fixture([sent(),reply(raw())]));const o=await f.backend.SESSION_AUTHENTICATE();deny(o);assert.equal(o.error_class,'REQUEST_MFA_NOT_FINAL');assert.equal(f.io.requestShapes().length,2);")
 def test_http_stage_sequence_and_actual_final_session(self):
  self.invoke("const f=fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(transitioned()),...POINTS.map(()=>reply(transitioned())),reply({status_code:200})]);"
   "const get=await request(f.handler);assert.equal(get.json.ceremony_stage,'CONTEXT_READY');const cookie=get.headers['Set-Cookie'].split(';')[0];const headers={cookie,'x-g3-csrf':get.json.csrf};"
   "for(const [action,stage] of [['EMAIL_OTP_SEND','EMAIL_SENT'],['EMAIL_OTP_AUTHENTICATE','OTP_VERIFIED'],['TOTP_AUTHENTICATE','MFA_VERIFIED']]){const r=await request(f.handler,'POST',{action,...(action.endsWith('AUTHENTICATE')?{code:'000000'}:{})},headers);pass(r.json);assert.equal(r.json.ceremony_stage,stage);assert.equal(r.json.context_expires_at,T+300000);}"
   "for(const action of POINTS){const r=await request(f.handler,'POST',{action},headers);pass(r.json);assert.equal(r.json.ceremony_stage,'MFA_VERIFIED');}"
   "const end=await request(f.handler,'POST',{action:'SESSION_REVOKE_EXACT'},headers);pass(end.json);assert.equal(end.json.ceremony_stage,'RETIRED');assert.equal(end.json.context_expires_at,null);assert.equal(f.io.requestShapes().at(-1).exact_session_id,'fixture-final-session');")
 def test_http_no_primary_is_retired_not_mfa(self):
  self.invoke("const f=fixture([sent()]);const get=await request(f.handler);const headers={cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf};pass((await request(f.handler,'POST',{action:'EMAIL_OTP_SEND'},headers)).json);const r=await request(f.handler,'POST',{action:'TOTP_AUTHENTICATE',code:'000000'},headers);deny(r.json);assert.equal(r.json.ceremony_stage,'RETIRED');assert.equal(r.json.error_class,'REQUEST_TOTP_NO_PRIMARY');assert.equal(r.json.context_expires_at,null);")
 def test_browser_phase_cannot_create_backend_state(self):
  self.invoke("const f=fixture([]);const get=await request(f.handler);const headers={cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf};const r=await request(f.handler,'POST',{action:'TOTP_AUTHENTICATE',code:'000000',ceremony_stage:'OTP_VERIFIED'},headers);deny(r.json);assert.equal(r.json.ceremony_stage,'RETIRED');assert.equal(f.io.requestShapes().length,0);")
 def test_profiles_frozen_authority_boundaries(self):
  for p in M.PROFILES:
   r=M.validate(M.compose(DATA,p),DATA,p);self.assertEqual(r['files'],20);self.assertEqual(r['authority'],'NONE')
 def test_review_generations_unchanged(self):
  old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
  for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
 def test_mutation_rejected(self):
  b=M.compose(DATA);b[M.G3.SERVICE]+=b'\n// unreviewed\n'
  with self.assertRaises(RuntimeError):M.validate(b,DATA)

CLIENT=r'''
import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const variant=process.argv[1],T=1791564000000;
const actions=['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE','PAGE','SESSION_REVOKE_EXACT','LOCAL_LOGOUT','ACCOUNT_SWITCH'];
const buttons=actions.map(action=>({dataset:{action},disabled:false,addEventListener(){}}));
const evidence={textContent:''},controls={disabled:true},status={};let calls=0;
const reply={diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',qualified_live:false,adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true,result:'PASS',error_class:'NONE',ceremony_stage:variant,context_expires_at:T+300000,csrf:'a'.repeat(64),unexpected:'UNSAFE_SYNTHETIC'};
if(variant==='MISSING')delete reply.ceremony_stage;
if(variant==='UNKNOWN')reply.ceremony_stage='UNSAFE_SYNTHETIC';
if(variant==='DENY'){reply.ceremony_stage='RETIRED';reply.result='DENY';reply.error_class='REQUEST_TOTP_NO_PRIMARY';reply.context_expires_at=null;}
if(variant==='AUTHORITY'){reply.ceremony_stage='MFA_VERIFIED';reply.authority='REAL';}
if(variant==='ADMISSION'){reply.ceremony_stage='MFA_VERIFIED';reply.real_admission='ENABLED';}
if(variant==='QUALIFIED'){reply.ceremony_stage='MFA_VERIFIED';reply.qualified_live=true;}
if(variant==='TOKEN'){reply.ceremony_stage='MFA_VERIFIED';reply.session_token='OFFLINE_SENTINEL';}
if(variant==='EXTENDED'){reply.ceremony_stage='MFA_VERIFIED';reply.context_expires_at=T+300001;}
if(variant==='EXPIRED'){reply.ceremony_stage='MFA_VERIFIED';reply.context_expires_at=T;}
if(variant==='CSRF'){reply.ceremony_stage='MFA_VERIFIED';reply.csrf='invalid';}
const document={getElementById(id){return {status,evidence,operations:controls,'email-code':{value:''},'totp-code':{value:''}}[id];},querySelectorAll(){return buttons;}};
vm.runInNewContext(fs.readFileSync('public/app.js','utf8'),{document,window:{addEventListener(){}},Date:{now:()=>T},setTimeout(){},location:{origin:'https://nexus-g3-qual.vercel.app'},fetch:async()=>{calls++;return {ok:true,json:async()=>reply};},console:new Proxy({}, {get(){throw Error('LOGGING_FORBIDDEN');}})});
await new Promise(resolve=>setImmediate(resolve));assert.equal(calls,1);
const valid=['CONTEXT_READY','EMAIL_SENT','OTP_VERIFIED','MFA_VERIFIED','TOKEN'].includes(variant);
assert.equal(controls.disabled,!valid);const out=JSON.parse(evidence.textContent);assert.equal(out.authority,'NONE');assert.equal(out.real_admission,'DISABLED');assert.equal(out.qualified_live,false);
assert.equal(evidence.textContent.includes('UNSAFE'),false);assert.equal(evidence.textContent.includes('OFFLINE_SENTINEL'),false);assert.equal(evidence.textContent.includes('csrf'),false);
if(valid){const allowed={CONTEXT_READY:['EMAIL_OTP_SEND'],EMAIL_SENT:['EMAIL_OTP_AUTHENTICATE'],OTP_VERIFIED:['TOTP_AUTHENTICATE'],MFA_VERIFIED:['PAGE','SESSION_REVOKE_EXACT'],TOKEN:['PAGE','SESSION_REVOKE_EXACT']}[variant];for(const b of buttons)assert.equal(b.disabled,!['LOCAL_LOGOUT','ACCOUNT_SWITCH',...allowed].includes(b.dataset.action));}
else {assert.equal(out.result,'DENY');assert.equal(out.ceremony_stage,'RETIRED');assert.equal(out.context_expires_at,null);for(const b of buttons.filter(b=>!['LOCAL_LOGOUT','ACCOUNT_SWITCH'].includes(b.dataset.action)))assert.equal(b.disabled,true);}
'''
class CeremonyClient(unittest.TestCase):
 def run_client(self,variant):
  with tempfile.TemporaryDirectory(prefix='nexus-g3-ceremony-client-') as d:
   root=Path(d)
   for n,b in M.compose(DATA).items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   r=subprocess.run(['node','--input-type=module','-e',CLIENT,variant],cwd=root,capture_output=True,timeout=20)
   self.assertEqual(r.returncode,0,'Synthetic closed-stage UI assertion failed')
for variant in ('CONTEXT_READY','EMAIL_SENT','OTP_VERIFIED','MFA_VERIFIED','RETIRED','MISSING','UNKNOWN','DENY','AUTHORITY','ADMISSION','QUALIFIED','TOKEN','EXTENDED','EXPIRED','CSRF'):
 setattr(CeremonyClient,'test_'+variant.lower(),lambda self,v=variant:self.run_client(v))
