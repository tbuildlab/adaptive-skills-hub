"""Authenticated fixed-form decoding and adversarial checks; synthetic IO only."""
from pathlib import Path
import copy, importlib.util, subprocess, tempfile, unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('owner_form_parser',HERE/'scripts/verify_owner_form_parser.py')
M=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)
DATA=M.G3.reviewed_public_input()
PREFIX=(HERE/'tests/integration.test.js').read_text().split("test('01 current service mode")[0].replace("from '../", "from './")
PREFIX=PREFIX.replace("import { createCustodyDryRun } from './lib/server/custody-dry-run.js';",'')
RUNTIME=PREFIX+r'''
import {parse as parseQS} from 'node:querystring';
const variant=process.argv[1];
const f=fixture([sent(),reply(raw()),reply(raw()),enrollment(),reply(raw()),reply(raw())]);
const first=await request(f.handler),cookie=first.headers['Set-Cookie'].split(';')[0],csrf=first.json.csrf;
const headers={cookie,'x-g3-csrf':csrf};
for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_CREATE']) {
 const response=await request(f.handler,'POST',{action,...(action==='EMAIL_OTP_AUTHENTICATE'?{code:'000000'}:{})},headers);pass(response.json);
}
assert.equal(f.io.requestShapes().length,5);
let body={action:'OWNER_TOTP_DISPLAY',csrf},h={cookie,'content-type':'application/x-www-form-urlencoded'},bad=false;
if(variant==='QUERYSTRING'||variant==='HISTORICAL')body=parseQS(new URLSearchParams(body).toString());
if(variant==='NULL_PROTO')body=Object.assign(Object.create(null),body);
if(variant==='STRING')body=new URLSearchParams(body).toString();
if(variant==='DUPLICATE')body=parseQS(new URLSearchParams(body).toString()+'&csrf='+csrf);
if(variant==='RAW_DUPLICATE')body=new URLSearchParams(body).toString()+'&csrf='+csrf;
if(variant==='DUPLICATE_ACTION')body=parseQS(new URLSearchParams(body).toString()+'&action=OWNER_TOTP_DISPLAY');
if(variant==='EXTRA')body.extra='offline-invalid';
if(variant==='SYMBOL')body[Symbol('offline')]='invalid';
if(variant==='GETTER')Object.defineProperty(body,'csrf',{get(){throw Error('GETTER_MUST_NOT_RUN');},enumerable:true});
if(variant==='NONENUMERABLE')Object.defineProperty(body,'csrf',{value:csrf,enumerable:false});
if(variant==='CUSTOM_PROTO')Object.setPrototypeOf(body,{inherited:'offline'});
if(variant==='INHERITED')body=Object.create(body);
if(variant==='PROTOTYPE_KEY')body=parseQS(new URLSearchParams(body).toString()+'&__proto__=offline');
if(variant==='NUMERIC')body.csrf=0;
if(variant==='ARRAY_VALUE')body.csrf=[csrf];
if(variant==='ARRAY_BODY')body=[body];
if(variant==='NULL')body=null;
if(variant==='MISSING')delete body.csrf;
if(variant==='WRONG_ACTION')body.action='TOTP_AUTHENTICATE';
if(variant==='WRONG_CSRF')body.csrf='0'.repeat(64);
if(variant==='OVERSIZE')body.csrf='x'.repeat(1025);
if(variant==='RAW_OVERSIZE')body='x'.repeat(1025);
if(variant==='WRONG_ORIGIN')h.origin='https://other.invalid';
if(variant==='NULL_ORIGIN')h.origin='null';
if(variant==='MISSING_ORIGIN')h.origin=undefined;
if(variant==='CROSS_SITE')h['sec-fetch-site']='cross-site';
if(variant==='CONTENT_TYPE')h['content-type']='text/plain';
if(variant==='EXPIRED')f.time(T+300000);
const response=await request(f.handler,'POST',body,h);
const valid=['QUERYSTRING','NULL_PROTO','STRING','OBJECT'].includes(variant);
if(valid){
 assert.equal(response.statusCode,200);assert.equal(response.headers['Content-Type'],'text/html; charset=utf-8');
 assert.equal(response.headers['Referrer-Policy'],'no-referrer');assert.equal(response.headers['Cache-Control'],'no-store');
 assert.ok(response.text.includes('OFFLINE_TOTP_SEED'));assert.equal(f.io.requestShapes().length,6);
 const again=await request(f.handler,'POST',body,h);deny(again.json);assert.equal(again.json.context_expires_at,null);
}else{
 assert.equal(response.statusCode,403);deny(response.json);assert.equal(response.json.authority,'NONE');
 assert.equal(response.json.context_expires_at,null);assert.equal(response.json.csrf,null);
 assert.equal(f.io.requestShapes().length,5);assert.equal(response.text.includes('OFFLINE_TOTP_SEED'),false);
 if(variant==='HISTORICAL')assert.equal(response.json.error_class,'REQUEST');
 else if(['WRONG_ORIGIN','NULL_ORIGIN','CROSS_SITE'].includes(variant))assert.equal(response.json.error_class,'REQUEST_ORIGIN');
 else if(['MISSING_ORIGIN','EXPIRED'].includes(variant))assert.equal(response.json.error_class,'RETIRED');
 else if(variant==='CONTENT_TYPE')assert.equal(response.json.error_class,'REQUEST_CSRF');
 else assert.equal(response.json.error_class,variant==='WRONG_CSRF'?'REQUEST_FORM_CSRF':variant.includes('OVERSIZE')?'REQUEST_FORM_SIZE':'REQUEST_FORM_SCHEMA');
}
assert.equal(networkCalls,0);f.backend.retire();
'''

class OwnerFormParserArtifact(unittest.TestCase):
    def runtime(self,variant):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-form-parser-offline-') as directory:
            root=Path(directory); blobs=M.BASE.compose(DATA) if variant=='HISTORICAL' else M.compose(DATA)
            for n,b in blobs.items():
                p=root/n; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',RUNTIME,variant],cwd=root,
                env={'SystemRoot':r'C:\Windows'},capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stderr.decode())
    def test_exact_inventory(self):self.assertEqual(M.validate(M.compose(DATA),DATA)['files'],19)
    def test_three_file_delta(self):
        self.assertEqual({n for n,b in M.compose(DATA).items() if b!=M.BASE.compose(DATA)[n]}, {M.G3.INPUT,M.G3.SERVICE,M.G3.POLICY})
    def test_previous_artifact_frozen(self):self.assertEqual(M.BASE.validate(M.BASE.compose(DATA),DATA)['zip_sha256'],'4cce45ae9dd5a11e72a9cdb8c36bd9c93b5dfb4ed2e8057b4059b087b623c626')
    def test_public_and_private_assets_unchanged(self):
        for n in ('public/index.html','public/app.js','public/owner-transient.js','vercel.json'):
            self.assertEqual(M.compose(DATA)[n],M.BASE.compose(DATA)[n])
    def test_no_pin_or_deadline_change(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
        for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):
            self.assertEqual(old[k],new[k])
    def test_mutation_rejected(self):
        b=M.compose(DATA);b[M.G3.SERVICE]=b[M.G3.SERVICE].replace(b'h.origin!==ORIGIN',b'false')
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_other_owner_rejected(self):
        d=copy.deepcopy(DATA);d['provider']['owner_user_id']='offline-other'
        with self.assertRaises(RuntimeError):M.compose(d)

for variant in ('QUERYSTRING','NULL_PROTO','STRING','OBJECT','HISTORICAL','DUPLICATE','RAW_DUPLICATE',
    'DUPLICATE_ACTION','EXTRA','SYMBOL','GETTER','NONENUMERABLE','CUSTOM_PROTO','INHERITED',
    'PROTOTYPE_KEY','NUMERIC','ARRAY_VALUE','ARRAY_BODY','NULL','MISSING','WRONG_ACTION','WRONG_CSRF',
    'OVERSIZE','RAW_OVERSIZE','WRONG_ORIGIN','NULL_ORIGIN','MISSING_ORIGIN','CROSS_SITE','CONTENT_TYPE','EXPIRED'):
    setattr(OwnerFormParserArtifact,'test_runtime_'+variant.lower(),lambda self,v=variant:self.runtime(v))

if __name__=='__main__':unittest.main()
