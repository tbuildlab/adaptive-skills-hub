"""Retirement recovery is a denial, never context restoration or refresh."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('retired_builder',HERE/'scripts/verify_retired_context.py')
B=module('retired_fixtures',HERE/'tests/test_lifecycle_evidence_artifact.py')
DATA=M.G3.reviewed_public_input()
PREFIX=B.PREFIX+r'''
function cleared(r){assert.equal(r.headers['Set-Cookie'],'__Host-g3d01=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0');assert.equal(r.json.authority,'NONE');assert.equal(r.json.real_admission,'DISABLED');assert.equal(r.json.context_expires_at,null);}
async function page(){const f=fixture([]);const first=await request(f.handler);return {f,first,headers:{cookie:first.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':first.json.csrf}};}
'''
class RetiredContextArtifact(unittest.TestCase):
 def invoke(self,script):
  with tempfile.TemporaryDirectory(prefix='nexus-g3-retired-offline-') as d:
   root=Path(d)
   for n,b in M.compose(DATA).items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   (root/'tests').mkdir()
   r=subprocess.run(['node','--input-type=module','-e',PREFIX+script],cwd=root/'tests',capture_output=True,timeout=20)
   self.assertEqual(r.returncode,0,'Synthetic retired-context assertion failed')
 def test_worker_restart_denies_and_clears(self):
  self.invoke("const {headers}=await page();const f=fixture([]);const r=await request(f.handler,'GET',undefined,headers);deny(r.json);cleared(r);assert.equal(r.json.error_class,'RETIRED');assert.equal(r.json.completed_action,null);assert.equal(f.io.requestShapes().length,0);")
 def test_expired_then_separate_new_request(self):
  self.invoke("const {f,first,headers}=await page();f.time(T+300000);const r=await request(f.handler,'GET',undefined,headers);deny(r.json);cleared(r);const next=await request(f.handler);assert.equal(next.json.ceremony_stage,'CONTEXT_READY');assert.equal(next.json.result,'DENY');assert.notEqual(next.json.csrf,first.json.csrf);assert.equal(next.json.context_expires_at,T+600000);assert.equal(f.io.requestShapes().length,0);")
 def test_old_cookie_replay_never_restores(self):
  self.invoke("const {f,headers}=await page();f.time(T+300000);cleared(await request(f.handler,'GET',undefined,headers));const next=await request(f.handler);assert.equal(next.json.ceremony_stage,'CONTEXT_READY');const r=await request(f.handler,'POST',{action:'EMAIL_OTP_SEND'},headers);deny(r.json);cleared(r);assert.equal(f.io.requestShapes().length,0);")
 def test_valid_reload_preserves_deadline(self):
  self.invoke("const {f,first,headers}=await page();f.time(T+1000);const r=await request(f.handler,'GET',undefined,headers);assert.equal(r.json.context_expires_at,first.json.context_expires_at);assert.equal(r.json.csrf,first.json.csrf);assert.equal(r.headers['Set-Cookie'],undefined);")
 def test_local_logout_clears_and_denies(self):
  self.invoke("const {f,headers}=await page();const r=await request(f.handler,'POST',{action:'LOCAL_LOGOUT'},headers);deny(r.json);cleared(r);assert.equal(r.json.ceremony_stage,'RETIRED');")
 def test_bad_csrf_retires_clears_without_io(self):
  self.invoke("const {f,headers}=await page();const r=await request(f.handler,'POST',{action:'EMAIL_OTP_SEND'},{...headers,'x-g3-csrf':'b'.repeat(64)});deny(r.json);cleared(r);assert.equal(f.io.requestShapes().length,0);")
 def test_complete_revoke_clears_cookie(self):
  self.invoke("const f=fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(transitioned()),reply(transitioned()),reply({status_code:200}),rejected()]);const get=await request(f.handler);const headers={cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':get.json.csrf};for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE'])pass((await request(f.handler,'POST',{action,...(action.endsWith('AUTHENTICATE')?{code:'000000'}:{})},headers)).json);const r=await request(f.handler,'POST',{action:'SESSION_REVOKE_EXACT'},headers);pass(r.json);cleared(r);assert.equal(r.json.revoke_observation,'REMOTE_REJECTION_CONFIRMED');assert.equal(r.json.ceremony_stage,'RETIRED');")
 def test_all_other_runtime_bytes_frozen(self):
  old=M.BASE.compose(DATA);new=M.compose(DATA)
  self.assertEqual({n for n in new if old[n]!=new[n]},{M.G3.INPUT,M.G3.SERVICE})
 def test_generations_review_and_defaults_unchanged(self):
  for p in M.PROFILES:
   r=M.validate(M.compose(DATA,p),DATA,p);self.assertEqual(r['files'],20);self.assertEqual(r['authority'],'NONE')
  old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
  for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
 def test_mutation_denied(self):
  b=M.compose(DATA);b[M.G3.SERVICE]+=b'\n// mutation\n'
  with self.assertRaises(RuntimeError):M.validate(b,DATA)
