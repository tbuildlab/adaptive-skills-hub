from pathlib import Path
import datetime,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.g3_signed_local_approval import LocalQualification
from scripts import verify_g3_owner_signature as origin
from ash import core_host_loop as host
from ash.core_capabilities import write
packet=Path('D:/chatgpt/安装skills/nexus-g3-owner-signing-v1-20261014')
pub=ROOT/'research/nexus-g3-owner-signing-key-v1.pub'
base=Path('D:/chatgpt/安装skills/nexus-g3-signed-local-e2e-20261014')
base.mkdir(exist_ok=False)
body=json.loads((packet/'owner-approval.json').read_bytes())
state=host.prepare('Inspect this local Git repository changes and whitespace checks, then return a maintenance report.',ROOT,['README.md','docs/nexus-roadmap-v2.md'],base/'task')
assert state['status']=='prepared'
binding={'logical_task_id':body['scope']['task_id'],'host_task_id':state['task_id'],'host_task_directory':state['directory'],'repo':str(ROOT),'input_hashes':state['input_hashes'],'task_authority':'current-explicit-Owner-task-and-Host-readonly-tool-authorization','not_a_general_dispatch_grant':True,'real_admission':'NO'}
write(base,'task-binding.json',(json.dumps(binding,sort_keys=True)+'\n').encode())
plane=LocalQualification(packet/'owner-approval.json',packet/'owner-approval.json.sig',pub)
queries=[];outcome='unknown';terminal_hash='0'*64
try:
 for step in range(4):
  current=host._load(base/'task')
  assert current['task_id']==binding['host_task_id'] and current['input_hashes']==binding['input_hashes']
  assert current['budget']['max_commands']<=body['config']['max_host_batches'] and current['budget']['max_replans']==0
  gate=plane.eligibility(body['subject'],body['scope'],plane.registration())
  assert gate['status']=='CAPABILITY_ELIGIBLE_ONLY',gate
  queries.append(gate)
  action=host.next_action(base/'task')['action'];assert action and action['task_id']==binding['host_task_id']
  path=base/(action['stage']+'-action.json');write(base,path.name,(json.dumps(action,sort_keys=True)+'\n').encode())
  result=subprocess.run([sys.executable,str(ROOT/'output/g4-local/native_host_action.py'),str(base/'task'),str(path)],capture_output=True,timeout=60,check=False)
  assert result.returncode==0,(action['stage'],result.returncode)
  observation=json.loads((base/'task'/(action['stage']+'-observation.json')).read_bytes())
  state=host.observe(base/'task',observation)
  assert state['status'] in {'prepared','completed','completed_with_findings'},state['blocker']
 assert state['receipt']['verification']=='passed' and state['commands_used']==4
 assert json.loads((base/'task/report.json').read_bytes())['task_id']==binding['host_task_id']
 receipt=(base/'task/receipt.json').read_bytes();terminal_hash=hashlib.sha256(receipt).hexdigest()
 outcome='verified-completion'
finally:
 plane.revoke(outcome,terminal_hash)
post=plane.eligibility(body['subject'],body['scope'],plane.registration())
assert post['status']=='DENY'
try:
 LocalQualification(packet/'owner-approval.json',packet/'owner-approval.json.sig',pub)
 raise AssertionError('restart unexpectedly restored authority')
except origin.Denied as error:
 assert str(error)=='ATTEMPT_ALREADY_RESERVED_NO_RESTART'
summary={'schema':'nexus.g3.signed-local-qualification.v1','observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_SIGNED_LOCAL_QUALIFICATION_NOT_FINAL_FREEZE','payload_sha256':origin.PAYLOAD_SHA,'subject_id':origin.SUBJECT_ID,'registration':plane.registration(),'task_binding':binding,'positive_eligibility_queries':len(queries),'receipt':state['receipt'],'receipt_sha256':terminal_hash,'post_revocation':post,'restart':'DENY_ALREADY_RESERVED_NO_RESTORATION','origin':'REAL_GITHUB_ACCOUNT_SIGNING_KEY_AND_NATIVE_OPENSSH_VERIFICATION','test_fixture_origin':False,'production_adapter':'UNCHANGED_DENY','real_admission':'NO','independent_final_review':'NOT_OBTAINED','g3_freeze':'NOT_YET'}
write(base,'qualification.json',(json.dumps(summary,sort_keys=True,indent=2)+'\n').encode())
(ROOT/'research/nexus-g3-signed-local-qualification-v1.json').write_bytes((json.dumps(summary,sort_keys=True,indent=2)+'\n').encode())
for name in ['origin-readback.json','approval-projection.json','registration.json','revocation.json']:
 write(ROOT/'research','nexus-g3-signed-local-'+name.replace('.json','-v1.json'),(ROOT/'output/g3-signed-local-once-v1'/name).read_bytes())
print(json.dumps({'status':summary['status'],'host_completion':state['status'],'commands_used':state['commands_used'],'post_revocation':post['status'],'restart':summary['restart'],'artifact_root':str(base),'real_admission':'NO'}))
