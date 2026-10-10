"""Fixed diagnostic completion sequence; no live IO, secrets or authority."""
from pathlib import Path
import importlib.util, subprocess, tempfile, unittest
HERE=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('completion_builder',HERE/'scripts/verify_completion_sequence.py')
B=module('completion_fixtures',HERE/'tests/test_lifecycle_evidence_artifact.py')
DATA=M.G3.reviewed_public_input()

CLIENT=r'''
import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const variant=process.argv[1],T=1791564000000,exp=T+300000;
let now=T,requests=[],listeners={},timers=[];
const evidence={textContent:''},controls={disabled:true},status={};
const actions=['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE','PAGE','DECISION_POST_SIMULATION','RECEIPT_SIMULATION','INTENT_SIMULATION','CLAIM_SIMULATION','SESSION_REVOKE_EXACT'];
const points=actions.slice(3,8),codes={'email-code':{value:''},'totp-code':{value:'000000'}};
const buttons=actions.map(action=>({dataset:{action},disabled:true,addEventListener(_,fn){listeners[action]=fn;}}));
const doc={getElementById(id){return {evidence,operations:controls,status,...codes}[id];},querySelectorAll(){return buttons;}};
const base={diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',qualified_live:false,adapter_mode:'D01_DIAGNOSTIC_LIVE_STYTCH',live_diagnostic_enabled:true,result:'PASS',error_class:'NONE',ceremony_stage:'MFA_VERIFIED',context_expires_at:exp,csrf:'a'.repeat(64),completed_action:null,completed_points:0,revoke_observation:'NOT_CONFIRMED'};
const sandbox={document:doc,window:{addEventListener(){}},Date:{now:()=>now},setTimeout(fn){timers.push(fn);},location:{origin:'https://nexus-g3-qual.vercel.app'},console:new Proxy({}, {get(){throw Error('LOGGING_FORBIDDEN');}}),fetch:async(url,options)=>{
  assert.equal(url,'/api/diagnostic');assert.equal(options.credentials,'same-origin');assert.equal(options.redirect,'error');
  const action=options.body?JSON.parse(options.body).action:null;requests.push(action);
  if(action===null){return {ok:true,json:async()=>({...base,ceremony_stage:variant==='GET_MFA'?'MFA_VERIFIED':'OTP_VERIFIED'})};}
  let result={...base,completed_action:action};
  const index=points.indexOf(action);
  if(index>=0)result.completed_points=index+1;
  if(action==='SESSION_REVOKE_EXACT')Object.assign(result,{ceremony_stage:'RETIRED',context_expires_at:null,csrf:null,completed_points:5,revoke_observation:'REMOTE_REJECTION_CONFIRMED'});
  if(variant==='OTP_ONLY'&&action==='EMAIL_OTP_AUTHENTICATE')result.ceremony_stage='OTP_VERIFIED';
  if(variant==='EXPIRED_MFA'&&action==='TOTP_AUTHENTICATE')now=exp;
  if(variant==='DOUBLE_CLICK'&&action==='PAGE')listeners.TOTP_AUTHENTICATE();
  if(variant==='CLOCK_ROLLBACK'&&action==='PAGE')now=T-1;
  if(variant==='EXPIRY_AFTER_PAGE'&&action==='PAGE')now=exp;
  if(variant==='LONGER_DEADLINE'&&action==='PAGE')result.context_expires_at=exp+1;
  if(variant==='SHORTER_DEADLINE'&&action==='PAGE')result.context_expires_at=exp-1;
  if(variant==='WRONG_ACTION'&&action==='PAGE')result.completed_action='CLAIM_SIMULATION';
  if(variant==='WRONG_POINTS'&&action==='PAGE')result.completed_points=5;
  if(variant==='MISSING_MARKER'&&action==='PAGE')delete result.completed_action;
  if(variant==='AUTHORITY_PROMOTION'&&action==='PAGE')result.authority='OWNER';
  if(variant==='ADMISSION_PROMOTION'&&action==='PAGE')result.real_admission='ENABLED';
  if(variant==='MISSING_REVOKE'&&action==='SESSION_REVOKE_EXACT')result.revoke_observation='NOT_CONFIRMED';
  if(variant==='DENIED_REVOKE'&&action==='SESSION_REVOKE_EXACT')Object.assign(result,{result:'DENY',error_class:'RETIRED'});
  if(variant==='TIMEOUT'&&action==='RECEIPT_SIMULATION')throw Error('fixture timeout');
  if(variant==='DENY_'+index&&index>=0)Object.assign(result,{result:'DENY',error_class:'SESSION_INVALID',ceremony_stage:'RETIRED',context_expires_at:null,csrf:null,completed_action:null});
  return {ok:true,json:async()=>result};
}};
vm.runInNewContext(fs.readFileSync('public/app.js','utf8'),sandbox);
await new Promise(resolve=>setImmediate(resolve));
if(variant==='GET_MFA'){assert.deepEqual(requests,[null]);process.exit(0);}
if(variant==='OTP_ONLY'){codes['email-code'].value='000000';await listeners.EMAIL_OTP_AUTHENTICATE();assert.deepEqual(requests,[null,'EMAIL_OTP_AUTHENTICATE']);process.exit(0);}
codes['totp-code'].value='000000';
await listeners.TOTP_AUTHENTICATE();
const out=JSON.parse(evidence.textContent);
assert.equal(out.authority,'NONE');assert.equal(out.real_admission,'DISABLED');
assert.equal(out.result,'DENY');assert.equal(controls.disabled,true);
assert.equal(codes['totp-code'].value,'');
for(const forbidden of ['csrf','000000','session_token','session_jwt','recovery_codes'])assert.equal(evidence.textContent.includes(forbidden),false);
if(['VALID','DOUBLE_CLICK'].includes(variant)){
  assert.deepEqual(requests,[null,'TOTP_AUTHENTICATE',...points,'SESSION_REVOKE_EXACT']);
  assert.equal(out.operation_result,'PASS');assert.equal(out.revoke_observation,'REMOTE_REJECTION_CONFIRMED');
  assert.equal(out.completed_points,5);assert.equal(out.context_expires_at,null);
  assert.deepEqual(out.completion_trace.map(r=>r.completed_action),['TOTP_AUTHENTICATE',...points,'SESSION_REVOKE_EXACT']);
  assert.deepEqual(out.completion_trace.slice(1,6).map(r=>r.completed_points),[1,2,3,4,5]);
  assert.equal(out.completion_trace.length,7);
  assert.ok(out.completion_trace.slice(0,6).every(r=>r.context_expires_at===exp));
  await listeners.TOTP_AUTHENTICATE();assert.equal(requests.length,8);
}else{
  assert.notEqual(out.revoke_observation,'REMOTE_REJECTION_CONFIRMED');
  assert.equal(requests.filter(a=>a==='SESSION_REVOKE_EXACT').length,variant.includes('REVOKE')?1:0);
  assert.equal(new Set(requests).size,requests.length);
  if(variant.startsWith('DENY_'))assert.equal(requests.length,3+Number(variant.slice(5)));
}
'''

class CompletionSequenceClient(unittest.TestCase):
    def run_client(self,variant):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-sequence-client-') as d:
            root=Path(d)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',CLIENT,variant],cwd=root,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic completion-sequence assertion failed; raw output not retained')

for variant in ['VALID','DOUBLE_CLICK','GET_MFA','OTP_ONLY','EXPIRED_MFA','CLOCK_ROLLBACK','EXPIRY_AFTER_PAGE','LONGER_DEADLINE','SHORTER_DEADLINE','WRONG_ACTION','WRONG_POINTS','MISSING_MARKER','AUTHORITY_PROMOTION','ADMISSION_PROMOTION','MISSING_REVOKE','DENIED_REVOKE','TIMEOUT',*[f'DENY_{i}' for i in range(5)]]:
    setattr(CompletionSequenceClient,'test_'+variant.lower(),lambda self,v=variant:self.run_client(v))

class CompletionSequenceArtifact(unittest.TestCase):
    def test_only_client_and_revision_change(self):
        old=M.BASE.compose(DATA);new=M.compose(DATA)
        self.assertEqual({n for n in new if old[n]!=new[n]},{M.G3.INPUT,'public/app.js'})
    def test_exact_profiles_and_unextended_review(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA)
        for profile in M.PROFILES:
            new=M.validate(M.compose(DATA,profile),DATA,profile)
            self.assertEqual(new['files'],20);self.assertEqual(new['authority'],'NONE')
            for key in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[key],new[key])
    def test_mutation_rejected(self):
        blobs=M.compose(DATA);blobs['public/app.js']+=b'\n// mutation\n'
        with self.assertRaises(RuntimeError):M.validate(blobs,DATA)
    def test_server_sequence_stays_action_attributed(self):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-sequence-http-') as d:
            root=Path(d)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            (root/'tests').mkdir()
            script=B.PREFIX+"const f=fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(transitioned()),...POINTS.map(()=>reply(transitioned())),reply(transitioned()),reply({status_code:200}),rejected()]);const get=await request(f.handler);const headers={cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf};for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE'])pass((await request(f.handler,'POST',{action,...(action.endsWith('AUTHENTICATE')?{code:'000000'}:{})},headers)).json);for(const [i,action] of POINTS.entries()){const r=await request(f.handler,'POST',{action},headers);pass(r.json);assert.equal(r.json.completed_action,action);assert.equal(r.json.completed_points,i+1);}const end=await request(f.handler,'POST',{action:'SESSION_REVOKE_EXACT'},headers);pass(end.json);assert.equal(end.json.completed_points,5);assert.equal(end.json.revoke_observation,'REMOTE_REJECTION_CONFIRMED');"
            r=subprocess.run(['node','--input-type=module','-e',script],cwd=root/'tests',capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic server sequence assertion failed')
