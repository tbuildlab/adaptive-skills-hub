"""Synthetic-only credential grammar tests, fixed custody and no IO."""
from pathlib import Path
import importlib.util, subprocess, tempfile, unittest
SPEC=importlib.util.spec_from_file_location('credential_artifact',Path(__file__).resolve().parents[1]/'scripts/verify_generation2.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.reviewed_public_input();PROFILE='LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT'

class CredentialFormatArtifact(unittest.TestCase):
 def test_exact_four_runtime_files(self):
  b=M.compose(PROFILE,DATA)
  self.assertEqual({n for n,v in M.originals().items() if v!=b[n]},{M.INPUT,M.POLICY,M.CUSTODY,M.SERVICE})
  self.assertEqual(M.validate(b,PROFILE,DATA)['files'],19)
 def test_earlier_profiles_keep_grammar(self):
  for p in ('DISABLED','LIVE_DIAGNOSTIC','LIVE_DIAGNOSTIC_READINESS','LIVE_DIAGNOSTIC_PROTOCOL_STATUS'):
   self.assertIn(b'/^secret-test-[A-Za-z0-9_-]{16,256}$/',M.compose(p,DATA)[M.CUSTODY])
 def test_no_profile_substitution(self):
  with self.assertRaises(RuntimeError):M.validate(M.compose(PROFILE,DATA),'LIVE_DIAGNOSTIC_PROTOCOL_STATUS',DATA)
 def runtime(self,variant,accept):
  with tempfile.TemporaryDirectory(prefix='nexus-g3-credential-grammar-offline-') as directory:
   root=Path(directory)
   for n,b in M.compose(PROFILE,DATA).items():
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   script=r"""
import {syncBuiltinESMExports} from 'node:module';import https from 'node:https';
https.request=()=>{throw Error('OFFLINE_NETWORK');};globalThis.fetch=https.request;syncBuiltinESMExports();
const {DEPLOYMENT:d}=await import('./lib/server/deployment-input.js');
const {registerReviewedDeployment}=await import('./lib/server/provider-registration.js');
const {loadServerCredentials,authorizeFixedRequest}=await import('./lib/server/credential-custody.js');
const variant=process.argv[1],accept=process.argv[2]==='true';
const prefix=['secret','test',''].join('-'),body='OFFLINE_SYNTHETIC_NOT_A_VALID_PROVIDER_CREDENTIAL';
const cases={UNPADDED:prefix+body,ONE_PAD:prefix+body+'=',TWO_PAD:prefix+body+'==',
 THREE_PAD:prefix+body+'===',MIDDLE_PAD:prefix+body.slice(0,20)+'='+body.slice(20),
 SPACE:prefix+body+' ',NEWLINE:prefix+body+'\n',CR:prefix+body+'\r',
 WRONG_ENV:['secret','live',body].join('-'),SHORT:prefix+'OFFLINE',OVERSIZE:prefix+'X'.repeat(256)+'=',
 INJECTION:prefix+body+'\r\nX-Test: OFFLINE'};
const secret=cases[variant];let reads=0;
process.env=new Proxy(Object.create(null),{get(_t,n){if(n==='STYTCH_PROJECT_ID'){reads++;return d.provider.project_id;}if(n==='STYTCH_SECRET'){reads++;return secret;}return undefined;},ownKeys(){throw Error('OFFLINE_ENV_ENUMERATION');}});
let handle=null,failure=null;try{handle=loadServerCredentials(d,d.provider);}catch(e){failure=e.code;}
if(reads!==2||!!handle!==accept||(!accept&&failure!=='SECRET_CONFIG_FORMAT'))throw Error('CREDENTIAL_GRAMMAR');
if(handle){
 const r=registerReviewedDeployment(d.provider),options={hostname:'test.stytch.com',protocol:'https:',port:443,method:'POST',path:'/v1/otps/email/send',servername:'test.stytch.com',rejectUnauthorized:true,headers:{}};
 authorizeFixedRequest(handle,options);
 const expected='Basic '+Buffer.from(d.provider.project_id+':'+secret).toString('base64');
 if(options.headers.Authorization!==expected)throw Error('OPAQUE_CREDENTIAL_MUTATED');
 const output=JSON.stringify(handle);if(output.includes(secret)||output.includes(body)||output.includes(d.provider.project_id))throw Error('CUSTODY_LEAK');
 handle.dispose();try{authorizeFixedRequest(handle,options);throw Error('DISPOSE_ACCEPTED');}catch(e){if(e.code!=='CREDENTIAL')throw e;}
}
"""
   environment={'SystemRoot':r'C:\Windows'} if Path(r'C:\Windows\System32').is_dir() else {}
   r=subprocess.run(['node','--input-type=module','-e',script,variant,str(accept).lower()],cwd=root,env=environment,capture_output=True)
   self.assertEqual(r.returncode,0,r.stderr.decode())
 def test_unpadded_verbatim(self):self.runtime('UNPADDED',True)
 def test_one_padding_verbatim(self):self.runtime('ONE_PAD',True)
 def test_two_padding_verbatim(self):self.runtime('TWO_PAD',True)
 def test_three_padding_denied(self):self.runtime('THREE_PAD',False)
 def test_middle_padding_denied(self):self.runtime('MIDDLE_PAD',False)
 def test_space_denied(self):self.runtime('SPACE',False)
 def test_newline_denied(self):self.runtime('NEWLINE',False)
 def test_carriage_return_denied(self):self.runtime('CR',False)
 def test_wrong_environment_denied(self):self.runtime('WRONG_ENV',False)
 def test_short_denied(self):self.runtime('SHORT',False)
 def test_oversize_denied(self):self.runtime('OVERSIZE',False)
 def test_header_injection_denied(self):self.runtime('INJECTION',False)

if __name__=='__main__':unittest.main()
