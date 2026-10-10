"""Synthetic fixed Owner metadata observation; no provider credentials or network."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('factor_read',HERE/'scripts/verify_owner_factor_observation.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
SCRIPT=r'''
import assert from 'node:assert/strict';import {configuration as c} from './lib/configuration.js';
import {requestGate,scopeDigest,projectOwnerFactors,parseUniqueJson,runProtectedObservation} from './lib/observation.js';
const v=process.argv[1],T=c.valid_from,env={VERCEL_ENV:'production',VERCEL_PROJECT_ID:c.scope.vercel_project_id,VERCEL_URL:'nexus-g3-qual-offline-tdy0225.vercel.app'};
const request={method:'POST',host:env.VERCEL_URL,content_type:'application/json',marker:'fixed-owner-factor-read-v1',body:{action:'OBSERVE_FACTORS',scope_sha256:scopeDigest(c.scope)}};
let cfg=structuredClone(c),now=T;
if(v==='DISABLED')cfg.enabled=false;if(v==='EXPIRED')now=c.valid_until;if(v==='FUTURE')now=T-1;
if(v==='WINDOW')cfg.valid_until=T+1800001;if(v==='GENERATION')cfg.scope.application_generation=2;
if(v==='PROJECT')env.VERCEL_PROJECT_ID='other';if(v==='PREVIEW')env.VERCEL_ENV='preview';
if(v==='HOST')request.host='nexus-g3-qual.vercel.app';if(v==='ORIGIN')request.origin='https://nexus-g3-qual.vercel.app';
if(v==='SITE')request.fetch_site='same-origin';if(v==='METHOD')request.method='PUT';
if(v==='CONTENT')request.content_type='text/plain';if(v==='MARKER')request.marker='wrong';
if(v==='SCOPE')request.body.scope_sha256='0'.repeat(64);if(v==='BODY')request.body.extra='invalid';
if(v==='ACTION')request.body.action='DELETE_EXPOSED_FACTOR';if(v==='STRING')request.body=JSON.stringify(request.body);
if(v==='STATUS')request.method='GET';
if(['VALID','STATUS'].includes(v))assert.equal(requestGate(request,cfg,env,now),v==='VALID'?'OBSERVE_FACTORS':'STATUS');
else if(!v.startsWith('PROJECTION')&&!['JSON','DUPLICATE_JSON','DISABLED_CUSTODY'].includes(v))assert.notEqual(requestGate(request,cfg,env,now),'OBSERVE_FACTORS');
const factor={totp_id:'totp-test-00000000-0000-0000-0000-000000000001',verified:true};
const body={status_code:200,user_id:c.scope.owner_user_id,status:'active',is_locked:false,totps:[factor],arbitrary:'OFFLINE_CANARY_DO_NOT_RENDER'};
if(v==='PROJECTION_OTHER')body.user_id='user-test-00000000-0000-0000-0000-000000000002';
if(v==='PROJECTION_DUPLICATE')body.totps.push(factor);if(v==='PROJECTION_MALFORMED')factor.verified='true';
if(v==='PROJECTION_LOCKED')body.is_locked=true;if(v==='PROJECTION_PENDING')body.status='pending';
if(v==='PROJECTION_OVERSIZE')body.totps=Array(33).fill(factor);
if(v.startsWith('PROJECTION_')&&v!=='PROJECTION_SAFE')assert.throws(()=>projectOwnerFactors(body,c.scope));
if(v==='PROJECTION_SAFE'){const p=projectOwnerFactors(body,c.scope);assert.equal(p.total_totp_count,1);assert.equal(p.verified_totp_count,1);assert.equal(p.unverified_totp_count,0);assert.equal(p.mutation_calls,0);assert.equal(p.authority,'NONE');assert.equal(p.real_admission,'DISABLED');assert.match(p.factors[0].factor_sha256,/^[a-f0-9]{64}$/);assert.equal(JSON.stringify(p).includes(factor.totp_id),false);assert.equal(JSON.stringify(p).includes('OFFLINE_CANARY'),false);}
if(v==='JSON')assert.equal(parseUniqueJson(Buffer.from('{"status_code":200}')).status_code,200);
if(v==='DUPLICATE_JSON')assert.throws(()=>parseUniqueJson(Buffer.from('{"status_code":200,"status_code":400}')));
if(v==='DISABLED_CUSTODY'){const e=new Proxy(env,{get(target,key){if(String(key).startsWith('STYTCH'))throw Error('SECRET_ACCESS');return target[key];}});const p=await runProtectedObservation({...c,enabled:false},e);assert.equal(p.result,'DENY');assert.equal(p.provider_calls,0);}
'''

class OwnerFactorObservationArtifact(unittest.TestCase):
    def run_variant(self,variant):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-factor-read-offline-') as d:
            root=Path(d)
            for n,b in M.compose(1791626000000,True).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',SCRIPT,variant],cwd=root,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic-only observation assertion failed')
    def test_inventory(self):self.assertEqual(M.validate(M.compose(1791626000000),1791626000000)['files'],5)
    def test_mutation(self):
        b=M.compose(1791626000000);b['lib/observation.js']+=b'// mutation\n'
        with self.assertRaises(RuntimeError):M.validate(b,1791626000000)
    def test_default_disabled(self):self.assertIn(b'"enabled":false',M.compose(1791626000000)['lib/configuration.js'])

for variant in ('VALID','STATUS','DISABLED','EXPIRED','FUTURE','WINDOW','GENERATION','PROJECT','PREVIEW','HOST','ORIGIN','SITE',
 'METHOD','CONTENT','MARKER','SCOPE','BODY','ACTION','STRING','PROJECTION_SAFE','PROJECTION_OTHER','PROJECTION_DUPLICATE',
 'PROJECTION_MALFORMED','PROJECTION_LOCKED','PROJECTION_PENDING','PROJECTION_OVERSIZE','JSON','DUPLICATE_JSON','DISABLED_CUSTODY'):
    setattr(OwnerFactorObservationArtifact,'test_'+variant.lower(),lambda self,v=variant:self.run_variant(v))
