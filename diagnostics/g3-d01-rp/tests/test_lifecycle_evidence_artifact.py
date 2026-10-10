"""No-network completion attribution and exact remote rejection adversaries."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('lifecycle_builder',HERE/'scripts/verify_lifecycle_evidence.py')
B=module('lifecycle_mfa_tests',HERE/'tests/test_mfa_transition_artifact.py')
DATA=M.G3.reviewed_public_input()
PREFIX=B.PREFIX+r'''
function rejected(extra={}) {return {status:404,headers:{'content-type':'application/json'},chunks:[JSON.stringify({status_code:404,error_type:'session_not_found',...extra})]};}
'''
class LifecycleEvidenceArtifact(B.MfaTransitionArtifact):
 def invoke(self,script):
  with tempfile.TemporaryDirectory(prefix='nexus-g3-lifecycle-offline-') as d:
   root=Path(d)
   for n,b in M.compose(DATA).items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   (root/'tests').mkdir()
   r=subprocess.run(['node','--input-type=module','-e',PREFIX+script],cwd=root/'tests',capture_output=True,timeout=20)
   self.assertEqual(r.returncode,0,'Synthetic lifecycle assertion failed; raw output not retained')
 def test_final_revoke_uses_final_session(self):
  self.invoke("const f=await transition([reply(transitioned()),reply({status_code:200}),rejected()]);const o=await f.backend.SESSION_REVOKE_EXACT();pass(o);assert.equal(o.revoke_observation,'REMOTE_REJECTION_CONFIRMED');const shapes=f.io.requestShapes();assert.equal(shapes.at(-2).exact_session_id,'fixture-final-session');assert.deepEqual(shapes.at(-1).keys,['session_token']);assert.equal(shapes.at(-1).duration,null);assert.equal(f.backend.contextInfo().retired,true);deny(await f.backend.SESSION_AUTHENTICATE());assert.equal(shapes.length,f.io.requestShapes().length);")
 def test_http_completed_points_and_terminal_receipt(self):
  self.invoke("const f=fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(transitioned()),...POINTS.map(()=>reply(transitioned())),reply(transitioned()),reply({status_code:200}),rejected()]);const get=await request(f.handler);assert.equal(get.json.completed_action,null);assert.equal(get.json.completed_points,0);const headers={cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf};for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE']){const r=await request(f.handler,'POST',{action,...(action.endsWith('AUTHENTICATE')?{code:'000000'}:{})},headers);pass(r.json);assert.equal(r.json.completed_action,action);}for(const [i,action] of POINTS.entries()){const r=await request(f.handler,'POST',{action},headers);pass(r.json);assert.equal(r.json.completed_action,action);assert.equal(r.json.completed_points,i+1);}const end=await request(f.handler,'POST',{action:'SESSION_REVOKE_EXACT'},headers);pass(end.json);assert.equal(end.json.ceremony_stage,'RETIRED');assert.equal(end.json.completed_action,'SESSION_REVOKE_EXACT');assert.equal(end.json.completed_points,5);assert.equal(end.json.revoke_observation,'REMOTE_REJECTION_CONFIRMED');assert.equal(end.json.csrf,null);assert.equal(end.json.context_expires_at,null);")
 def test_duplicate_point_no_io_and_no_completed_action(self):
  self.invoke("const f=fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(transitioned()),reply(transitioned())]);const get=await request(f.handler);const headers={cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf};for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE','PAGE'])pass((await request(f.handler,'POST',{action,...(action.endsWith('AUTHENTICATE')?{code:'000000'}:{})},headers)).json);const before=f.io.requestShapes().length;const r=await request(f.handler,'POST',{action:'PAGE'},headers);deny(r.json);assert.equal(r.json.completed_action,null);assert.equal(f.io.requestShapes().length,before);")
 def test_browser_evidence_cannot_change_state(self):
  self.invoke("const f=fixture([]);const get=await request(f.handler);const r=await request(f.handler,'POST',{action:'EMAIL_OTP_SEND',completed_points:5},{cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf});deny(r.json);assert.equal(r.json.completed_action,null);assert.equal(f.io.requestShapes().length,0);")
 def test_revoke_before_expiry_requires_remote_precheck(self):
  self.invoke("const f=await transition([{status:401,headers:{},chunks:[]}]);deny(await f.backend.SESSION_REVOKE_EXACT());assert.equal(f.io.requestShapes().length,6);assert.equal(f.io.requestShapes().at(-1).op,'SESSION_AUTHENTICATE');")
 def test_revoke_expired_no_network(self):
  self.invoke("const f=await transition();f.time(T+300000);deny(await f.backend.SESSION_REVOKE_EXACT());assert.equal(f.io.requestShapes().length,5);")
 def test_profiles_frozen_authority_boundaries(self):
  for p in M.PROFILES:self.assertEqual(M.validate(M.compose(DATA,p),DATA,p)['authority'],'NONE')
 def test_review_generations_unchanged(self):
  a=M.BASE.validate(M.BASE.compose(DATA),DATA);b=M.validate(M.compose(DATA),DATA)
  for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(a[k],b[k])
 def test_mutation_rejected(self):
  b=M.compose(DATA);b[M.TRANSPORT]+=b'\n// mutation\n'
  with self.assertRaises(RuntimeError):M.validate(b,DATA)

NEGATIVE_CASES={
 'positive_after_revoke':"reply(transitioned())",
 'generic_401':"{status:401,headers:{'content-type':'application/json'},chunks:['{}']}",
 'generic_404':"rejected({error_type:'project_not_found'})",
 'wrong_body_status':"rejected({status_code:200})",
 'unexpected_bearer':"rejected({session_token:'OFFLINE_SENTINEL'})",
 'timeout':"{failure:'TIMEOUT'}",
 'unavailable':"{status:503,headers:{},chunks:[]}",
 'rate_limited':"{status:429,headers:{},chunks:[]}",
 'redirect':"{status:302,headers:{},chunks:[]}",
 'malformed':"{status:404,headers:{'content-type':'application/json'},chunks:['{']}",
 'duplicate_key':"{status:404,headers:{'content-type':'application/json'},chunks:['{\"status_code\":404,\"error_type\":\"wrong\",\"error_type\":\"session_not_found\"}']}",
 'wrong_content_type':"{status:404,headers:{'content-type':'text/plain'},chunks:['{}']}",
 'oversize':"{status:404,headers:{'content-type':'application/json'},chunks:['x'.repeat(65537)]}",
 'body_missing':"{status:404,headers:{'content-type':'application/json'},chunks:[]}",
}
for name,case in NEGATIVE_CASES.items():
 def test(self,c=case):
  self.invoke("const f=await transition([reply(transitioned()),reply({status_code:200}),"+c+"]);const o=await f.backend.SESSION_REVOKE_EXACT();deny(o);assert.notEqual(o.revoke_observation,'REMOTE_REJECTION_CONFIRMED');assert.equal(f.backend.contextInfo().retired,true);assert.equal(f.io.requestShapes().length,8);deny(await f.backend.SESSION_AUTHENTICATE());assert.equal(f.io.requestShapes().length,8);")
 setattr(LifecycleEvidenceArtifact,'test_negative_'+name,test)

CLIENT=r'''
import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const variant=process.argv[1],T=1791564000000;
const evidence={textContent:''},controls={disabled:true},status={};let listener;
const button={dataset:{action:'PAGE'},disabled:false,addEventListener(name,fn){listener=fn;}};
const reply={diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',qualified_live:false,adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true,result:'PASS',error_class:'NONE',ceremony_stage:'MFA_VERIFIED',context_expires_at:T+300000,csrf:'a'.repeat(64),completed_action:'PAGE',completed_points:1,revoke_observation:'NOT_CONFIRMED'};
if(variant==='REVOKED')Object.assign(reply,{ceremony_stage:'RETIRED',context_expires_at:null,csrf:null,completed_action:'SESSION_REVOKE_EXACT',completed_points:5,revoke_observation:'REMOTE_REJECTION_CONFIRMED'});
if(variant==='MISSING')delete reply.completed_action;
if(variant==='UNKNOWN')reply.completed_action='UNSAFE';
if(variant==='NEGATIVE')reply.completed_points=-1;
if(variant==='OVERSIZE')reply.completed_points=6;
if(variant==='FLOAT')reply.completed_points=1.5;
if(variant==='BAD_REVOKE')reply.revoke_observation='UNSAFE';
if(variant==='DENY_REVOKE')Object.assign(reply,{result:'DENY',error_class:'RETIRED',ceremony_stage:'RETIRED',context_expires_at:null,csrf:null,completed_action:'SESSION_REVOKE_EXACT',revoke_observation:'REMOTE_REJECTION_CONFIRMED'});
const doc={getElementById(id){return {status,evidence,operations:controls,'email-code':{value:''},'totp-code':{value:''}}[id];},querySelectorAll(){return [button];}};
let calls=0;vm.runInNewContext(fs.readFileSync('public/app.js','utf8'),{document:doc,window:{addEventListener(){}},Date:{now:()=>T},setTimeout(){},location:{origin:'https://nexus-g3-qual.vercel.app'},fetch:async()=>{calls++;if(calls>1)return new Promise(()=>{});return {ok:true,json:async()=>reply};},console:new Proxy({}, {get(){throw Error('LOGGING_FORBIDDEN');}})});
await new Promise(resolve=>setImmediate(resolve));const out=JSON.parse(evidence.textContent);
assert.equal(out.authority,'NONE');assert.equal(out.real_admission,'DISABLED');assert.equal(evidence.textContent.includes('csrf'),false);
if(variant==='VALID'){assert.equal(out.completed_action,'PAGE');assert.equal(out.completed_points,1);listener();const pending=JSON.parse(evidence.textContent);assert.equal(pending.request_pending,true);assert.equal(pending.completed_action,null);assert.equal(pending.operation_result,'DENY');}
else if(variant==='REVOKED'){assert.equal(out.result,'DENY');assert.equal(controls.disabled,true);assert.equal(out.operation_result,'PASS');assert.equal(out.revoke_observation,'REMOTE_REJECTION_CONFIRMED');}
else {assert.equal(out.result,'DENY');assert.equal(out.revoke_observation,'NOT_CONFIRMED');}
'''
class LifecycleClient(unittest.TestCase):
 def run_client(self,v):
  with tempfile.TemporaryDirectory(prefix='nexus-g3-lifecycle-client-') as d:
   root=Path(d)
   for n,b in M.compose(DATA).items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   r=subprocess.run(['node','--input-type=module','-e',CLIENT,v],cwd=root,capture_output=True,timeout=20)
   self.assertEqual(r.returncode,0,'Synthetic completion UI assertion failed')
for v in ('VALID','REVOKED','MISSING','UNKNOWN','NEGATIVE','OVERSIZE','FLOAT','BAD_REVOKE','DENY_REVOKE'):
 setattr(LifecycleClient,'test_'+v.lower(),lambda self,v=v:self.run_client(v))
