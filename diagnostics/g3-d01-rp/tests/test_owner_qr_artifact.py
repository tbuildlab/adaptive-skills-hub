"""Synthetic-only private QR and quarantine regression. No real enrollment material."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('owner_qr',HERE/'scripts/verify_owner_qr.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.G3.reviewed_public_input()
CLIENT=r'''
import assert from 'node:assert/strict';
import vm from 'node:vm';import fs from 'node:fs';
const variant=process.argv[1],T=1791564000000;
let now=T, calls=[],pixels=[],timers=[],events={},removed=false,clears=0;
let synthetic='A'.repeat(32);
if(variant==='BAD_SEED')synthetic='<invalid>';
if(variant==='SHORT')synthetic='A'.repeat(15);
if(variant==='OVERSIZE')synthetic='A'.repeat(129);
if(variant==='LOWERCASE')synthetic='a'.repeat(32);
if(variant==='PADDING')synthetic='A'.repeat(32)+'=';
let captured=null,qrObject=null,segmentObjects=null;
const canvas={width:0,height:0,getContext(){return variant==='NO_CANVAS'?null:{
 fillStyle:'',fillRect(x,y,w,h){pixels.push([x,y,w,h,this.fillStyle]);},clearRect(){clears++;}};}};
const seed={textContent:synthetic,remove(){removed=true;}};
const input={value:'000000'};
const buttons={confirm:{addEventListener(e,f){this[e]=f;}},cancel:{addEventListener(e,f){this[e]=f;}}};
const metas=[{content:'a'.repeat(64),remove(){}},{content:String(T+300000),remove(){}}];
const root={textContent:'',querySelectorAll(){return [input];},replaceChildren(){this.cleared=true;}};
const document={visibilityState:'visible',getElementById(id){return {seed,'totp-qr':canvas,'owner-transient':root,code:input,...buttons}[id];},
 querySelector(s){return s.includes('csrf')?metas[0]:metas[1];},querySelectorAll(){return metas;}};
if(variant==='BAD_CSRF')metas[0].content='invalid';
if(variant==='EXPIRED')now=T+300000;
if(variant==='BAD_DEADLINE')metas[1].content='invalid';
const c=vm.createContext({document,window:{addEventListener(e,f){events[e]=f;}},URLSearchParams,
 Date:{now(){return now;}},location:{origin:variant==='WRONG_ORIGIN'?'https://other.invalid':'https://nexus-g3-qual.vercel.app',replace(){}},
 setTimeout(f){timers.push(f);},fetch:async(url,options)=>{assert.equal(url,'/api/diagnostic');
  assert.equal(options.credentials,'same-origin');assert.equal(options.redirect,'error');
  calls.push({body:JSON.parse(options.body),keepalive:options.keepalive});return {body:{async cancel(){}}};},
 console:new Proxy({}, {get(){throw Error('LOGGING_FORBIDDEN');}})});
vm.runInContext(fs.readFileSync('public/qrcodegen.js','utf8').replace('export { qrcodegen };',''),c);
c.qrcodegen.QrSegment.makeSegments=((original)=>text=>{captured=text;segmentObjects=original(text);return segmentObjects;})(c.qrcodegen.QrSegment.makeSegments);
c.qrcodegen.QrCode.encodeSegments=((original)=>(...a)=>{if(variant==='LIBRARY_FAILURE')throw Error('OFFLINE');qrObject=original(...a);return qrObject;})(c.qrcodegen.QrCode.encodeSegments);
vm.runInContext(fs.readFileSync('public/owner-transient.js','utf8').replace("import { qrcodegen } from './qrcodegen.js';",'').replace('export function paintOwnerQr','function paintOwnerQr'),c);
const bad=['BAD_SEED','SHORT','OVERSIZE','LOWERCASE','PADDING','NO_CANVAS','BAD_CSRF','EXPIRED','BAD_DEADLINE','WRONG_ORIGIN','LIBRARY_FAILURE'].includes(variant);
if(bad){assert.ok(root.cleared);assert.equal(canvas.width,0);assert.equal(input.value,'');
 assert.ok(calls.every(x=>x.body.action==='CANCEL'));assert.ok(calls.length<=1);
}else{
 assert.ok(removed);assert.equal(seed.textContent,'');assert.equal(calls.length,0);
 const uri=new URL(captured);assert.equal(uri.protocol,'otpauth:');assert.equal(uri.host,'totp');
 assert.equal(decodeURIComponent(uri.pathname.slice(1)),'Nexus G3:D01 disposable Owner');
 assert.equal(uri.searchParams.get('secret'),synthetic);assert.equal(uri.searchParams.get('issuer'),'Nexus G3');
 assert.equal(uri.searchParams.get('algorithm'),'SHA1');assert.equal(uri.searchParams.get('digits'),'6');assert.equal(uri.searchParams.get('period'),'30');
 assert.equal([...uri.searchParams].length,5);assert.ok(canvas.width<=512);assert.ok(canvas.width>100);
 assert.ok(pixels.some(x=>x[4]==='#000000'));assert.equal(pixels[0][4],'#ffffff');
 assert.ok(qrObject.modules.every(row=>row.every(x=>x===false)));
 assert.ok(segmentObjects.every(s=>s.bitData.every(x=>x===0)));
 if(variant==='CANCEL')buttons.cancel.click();
 if(variant==='CONFIRM')buttons.confirm.click();
 if(variant==='BAD_CODE'){input.value='bad';buttons.confirm.click();}
 if(variant==='PAGEHIDE')events.pagehide();
 if(variant==='UNLOAD')events.beforeunload();
 if(variant==='HIDDEN'){document.visibilityState='hidden';events.visibilitychange();}
 if(variant==='VISIBLE')events.visibilitychange();
 if(variant==='TIMEOUT'){now=T+300000;timers[0]();}
 if(['CANCEL','CONFIRM','BAD_CODE','PAGEHIDE','UNLOAD','HIDDEN','TIMEOUT'].includes(variant)){
  assert.ok(root.cleared);assert.equal(canvas.width,0);assert.equal(input.value,'');assert.ok(clears>0);
  assert.equal(calls.length,variant==='TIMEOUT'?0:1);
  if(calls.length)assert.equal(calls[0].body.action,variant==='CONFIRM'?'TOTP_AUTHENTICATE':'CANCEL');
  const count=calls.length;events.pagehide();buttons.confirm.click();assert.equal(calls.length,count);
 }else{assert.equal(calls.length,0);assert.ok(!root.cleared);}
}
'''

class OwnerQrArtifact(unittest.TestCase):
    def run_node(self,script,variant='',profile=M.PROFILES[0]):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-qr-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA,profile).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',script,variant],cwd=root,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic QR assertion failed; no private output retained')
    def test_closed_twenty_file_inventory(self):self.assertEqual(M.validate(M.compose(DATA),DATA)['files'],20)
    def test_exact_upstream_whitespace_only_normalization(self):
        lines=M.VENDOR.read_bytes().replace(b'\r\n',b'\n').split(b'\n')
        for number in (52,640,644,790,816):lines[number-1]+=b' '
        self.assertEqual(hashlib.sha256(b'\n'.join(lines)).hexdigest(),'6a1116192ed1dd67fa1bf31e77f5817103d71c23bbac24c382e698b7668bdd01')
    def test_live_candidate_structural_only(self):self.assertEqual(M.validate(M.compose(DATA,M.PROFILES[1]),DATA,M.PROFILES[1])['files'],20)
    def test_old_artifact_frozen(self):self.assertEqual(M.BASE.validate(M.BASE.compose(DATA),DATA)['zip_sha256'],'3b29223459feea42c05a72afc1970e7c286999b67273bd41f42fd934a7341865')
    def test_no_registration_or_window_change(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
        for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
    def test_mutation_denied(self):
        b=M.compose(DATA);b[M.CLIENT]+=b'\n// altered\n'
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_unknown_profile_denied(self):
        with self.assertRaises(RuntimeError):M.compose(DATA,'PRODUCTION_AUTHORITY')
    def test_no_recovery_display(self):
        b=M.compose(DATA)[M.OWNER];self.assertNotIn(b'id="recovery"',b);self.assertIn(b'id="seed" hidden',b)
    def test_unchanged_gates(self):
        for n in (M.G3.SERVICE,M.G3.CUSTODY,'vercel.json','public/index.html','public/app.js'):self.assertEqual(M.compose(DATA)[n],M.BASE.compose(DATA)[n])
    def test_no_external_qr_or_storage(self):
        b=M.compose(DATA)[M.CLIENT].decode()
        for x in ('toDataURL','sendBeacon','localStorage','sessionStorage','innerHTML','console.','navigator.clipboard','new Image'):self.assertNotIn(x,b)
        self.assertEqual(b.count("fetch('/api/diagnostic'"),1)
    def test_disabled_does_not_read_credentials_or_use_transport(self):
        self.run_node(r'''
import assert from 'node:assert/strict';import https from 'node:https';
import {createDiagnosticHandler} from './lib/server/diagnostic-service.js';
import {DEPLOYMENT} from './lib/server/deployment-input.js';
import {CODE_REVIEWED_LIVE_ENABLED,DEPLOYMENT_REGISTRATION_ENABLED} from './lib/server/pre-secret-policy.js';
assert.equal(DEPLOYMENT.mode,'FAKE_DISABLED');assert.equal(CODE_REVIEWED_LIVE_ENABLED,false);assert.equal(DEPLOYMENT_REGISTRATION_ENABLED,false);
const previous=process.env;process.env=new Proxy({}, {get(){throw Error('CREDENTIAL_READ');}});
https.request=()=>{throw Error('NETWORK_FORBIDDEN');};globalThis.fetch=()=>{throw Error('NETWORK_FORBIDDEN');};
const handler=createDiagnosticHandler();process.env=previous;
let body;const response={setHeader(){},end(x){body=JSON.parse(x);}};
await handler({url:'/api/diagnostic',method:'GET',headers:{host:'nexus-g3-qual.vercel.app'}},response);
assert.equal(body.adapter_mode,'FAKE_DISABLED');assert.equal(body.live_diagnostic_enabled,false);assert.equal(body.authority,'NONE');assert.equal(body.real_admission,'DISABLED');
''')
    def test_authenticated_one_use_html_and_replay(self):
        spec=importlib.util.spec_from_file_location('parser_tests',HERE/'tests/test_owner_form_parser_artifact.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
        script=p.RUNTIME.replace("assert.ok(response.text.includes('OFFLINE_TOTP_SEED'));","assert.ok(response.text.includes('id=\"seed\" hidden'));assert.ok(response.text.includes('id=\"totp-qr\"'));assert.equal(response.text.includes('OFFLINE_RECOVERY'),false);")
        self.run_node(script,'QUERYSTRING',M.PROFILES[1])

for variant in ('PAINT','CANCEL','CONFIRM','BAD_CODE','PAGEHIDE','UNLOAD','HIDDEN','VISIBLE','TIMEOUT','BAD_SEED','SHORT','OVERSIZE','LOWERCASE','PADDING','NO_CANVAS','BAD_CSRF','EXPIRED','BAD_DEADLINE','WRONG_ORIGIN','LIBRARY_FAILURE'):
    setattr(OwnerQrArtifact,'test_client_'+variant.lower(),lambda self,v=variant:self.run_node(CLIENT,v))
