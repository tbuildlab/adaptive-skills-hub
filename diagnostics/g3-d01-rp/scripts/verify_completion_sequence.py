"""Run the already-authorized diagnostic completion sequence after fresh MFA."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('sequence_parent', HERE/'scripts/verify_retired_context.py')
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
G3 = BASE.G3
PROFILES = ('DISABLED_COMPLETION_SEQUENCE', 'LIVE_DIAGNOSTIC_COMPLETION_SEQUENCE')
REVISION = 'g3-d01-completion-sequence-v12'

SEQUENCE = r'''
// Only a directly completed fresh TOTP action starts this fixed sequence.
// These are diagnostic observations, not grants, receipts or provider dispatch.
let sequenceBusy=false, sequenceStarted=false;
const sequenceTrace=[];
const completionActions=['PAGE','DECISION_POST_SIMULATION','RECEIPT_SIMULATION','INTENT_SIMULATION','CLAIM_SIMULATION'];
const completionFields=['diagnostic','authority','real_admission','qualified_live','result','error_class','ceremony_stage','context_expires_at','completed_action','completed_points','operation_result','revoke_observation'];
function retainCompletion(value){
  if(sequenceTrace.length>=7)throw Error('closed completion bound');
  sequenceTrace.push(Object.fromEntries(completionFields.map(k=>[k,value?.[k]??null])));
  const current=JSON.parse(evidence.textContent);
  evidence.textContent=JSON.stringify({...current,completion_trace:sequenceTrace},null,2);
}
function stopCompletion(){
  csrf=null;controls.disabled=true;clearCodes();stageButtons('RETIRED');
  status.textContent='Diagnostic sequence stopped — authority NONE';
  evidence.textContent=JSON.stringify({diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',real_admission:'DISABLED',qualified_live:false,result:'DENY',error_class:'REQUEST',ceremony_stage:'RETIRED',context_expires_at:null,completed_action:null,completed_points:0,operation_result:'DENY',revoke_observation:'NOT_CONFIRMED',completion_trace:sequenceTrace},null,2);
}
async function ownerAction(action){
  if(sequenceBusy)return;
  const receipt=await call(action);
  if(action!=='TOTP_AUTHENTICATE'||sequenceStarted||!receipt||receipt.result!=='PASS'
    ||receipt.operation_result!=='PASS'||receipt.completed_action!==action
    ||receipt.ceremony_stage!=='MFA_VERIFIED'||receipt.completed_points!==0||!fresh())return;
  sequenceStarted=true;sequenceBusy=true;
  const originalDeadline=deadline;
  try{
    retainCompletion(receipt);
    for(const [i,step] of completionActions.entries()){
      if(!fresh()||deadline!==originalDeadline){stopCompletion();return;}
      const observed=await call(step);
      retainCompletion(observed);
      if(!observed||observed.result!=='PASS'||observed.operation_result!=='PASS'
        ||observed.completed_action!==step||observed.completed_points!==i+1
        ||observed.ceremony_stage!=='MFA_VERIFIED'||observed.context_expires_at!==originalDeadline){stopCompletion();return;}
    }
    if(!fresh()||deadline!==originalDeadline){stopCompletion();return;}
    const terminal=await call('SESSION_REVOKE_EXACT');
    retainCompletion(terminal);
    if(!terminal||terminal.result!=='DENY'||terminal.operation_result!=='PASS'
      ||terminal.completed_action!=='SESSION_REVOKE_EXACT'||terminal.completed_points!==5
      ||terminal.ceremony_stage!=='RETIRED'||terminal.context_expires_at!==null
      ||terminal.revoke_observation!=='REMOTE_REJECTION_CONFIRMED'){stopCompletion();return;}
  }catch{stopCompletion();}
  finally{sequenceBusy=false;controls.disabled=true;clearCodes();}
}
'''

def compose(data, profile=PROFILES[0]):
    G3.HISTORICAL.need(profile in PROFILES, 'completion sequence profile')
    blobs = BASE.compose(data, BASE.PROFILES[0 if profile == PROFILES[0] else 1])
    blobs[G3.INPUT] = blobs[G3.INPUT].replace(BASE.REVISION.encode(), REVISION.encode())
    put = lambda old, new: BASE.BASE.BASE.put(blobs, 'public/app.js', old, new)
    put("  finally{if(body?.code)body.code=null;busy=false;}\n}",
        "  finally{if(body?.code)body.code=null;busy=false;}\n  return JSON.parse(evidence.textContent);\n}")
    put("for(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>call(button.dataset.action));",
        SEQUENCE+"\nfor(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>ownerAction(button.dataset.action));")
    return blobs

def validate(blobs, data, profile=PROFILES[0]):
    parent = BASE.PROFILES[0 if profile == PROFILES[0] else 1]
    previous = BASE.compose(data, parent); report = BASE.validate(previous, data, parent)
    G3.HISTORICAL.need(blobs == compose(data, profile), 'exact completion sequence source')
    changed = {G3.INPUT, 'public/app.js'}
    G3.HISTORICAL.need({n for n in blobs if blobs[n] != previous[n]} == changed, 'two-file client sequence delta')
    G3.HISTORICAL.scan(blobs); G3.HISTORICAL.config_review(blobs)
    report.update(profile=profile, deployment_revision=REVISION,
        changed_runtime_files=sorted(changed), completion_sequence='FRESH_MFA_FIXED_ONCE_NO_RETRY',
        completion_trace='BOUNDED_SANITIZED_NON_AUTHORITATIVE',
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output, profile=PROFILES[0]):
    output = G3.HISTORICAL.safe_output(output); G3.HISTORICAL.need(not output.exists(), 'fresh output')
    data = G3.generation3_input(); blobs = compose(data, profile); report = validate(blobs, data, profile)
    for n,b in blobs.items():
        p=output/'source'/n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')})); return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--profile',choices=PROFILES,default=PROFILES[0]);a=p.parse_args();build(a.output,a.profile)
