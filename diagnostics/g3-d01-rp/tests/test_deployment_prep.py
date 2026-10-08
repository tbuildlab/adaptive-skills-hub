"""Pure in-memory mutation tests; no real source/env/account state is changed."""
import copy,hashlib,importlib.util,json,re
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('owner_handoff',HERE/'scripts/prepare_owner_handoff.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
SOURCE={dst:(HERE/src).read_bytes().replace(b'\r\n',b'\n') for dst,src in M.VERIFIER.FILES.items()}
ROOT=HERE.parents[1]
OUTPUT=ROOT/'state/g3-d01-deployment-prep-20261009'
HANDOFF={p.relative_to(OUTPUT/'handoff').as_posix():p.read_bytes() for p in (OUTPUT/'handoff').rglob('*') if p.is_file()}
class DeploymentPrepTests(unittest.TestCase):
 def reject(self,blobs):
  with self.assertRaises(RuntimeError):M.validate_source(blobs)
 def injected(self,name,data=b'OFFLINE_CONTAMINATION'):
  value=dict(SOURCE);value[name]=data;self.reject(value)
 def changed(self,name,old,new):
  value=dict(SOURCE);self.assertIn(old,value[name]);value[name]=value[name].replace(old,new);self.reject(value)
 def test_15_extra_public_file(self):self.injected('public/extra.js')
 def test_16_env_file(self):self.injected('.env.local')
 def test_17_vercel_state(self):self.injected('.vercel/project.json')
 def test_18_oidc_token_artifact(self):self.injected('VERCEL_OIDC_TOKEN.txt')
 def test_19_route_d_contamination(self):self.injected('docs/nexus-route-d-unrelated.md')
 def test_20_nexus_authority_source(self):self.injected('ash/approval.py')
 def test_21_native_owner_id_client_leak(self):
  native=re.search(rb'"owner_user_id": "([^"]+)"',SOURCE['lib/server/deployment-input.js']).group(1)
  self.changed('public/app.js',b'let csrf=null;',b'let owner_user_id="'+native+b'";let csrf=null;')
 def test_22_secret_interface_client_leak(self):self.changed('public/app.js',b'let csrf=null;',b'let STYTCH_SECRET=process.env.STYTCH_SECRET;let csrf=null;')
 def test_23_session_bearer_client_leak(self):self.changed('public/app.js',b'let csrf=null;',b'let session_token="OFFLINE_BEARER_PLACEHOLDER";let csrf=null;')
 def test_24_bundle_deterministic(self):self.assertEqual(hashlib.sha256(M.frozen_zip(SOURCE)).hexdigest(),M.SOURCE_SHA256);self.assertEqual(M.frozen_zip(SOURCE),M.frozen_zip(dict(reversed(list(SOURCE.items())))))
 def test_25_source_modification_changes_digest_and_denies(self):
  value=dict(SOURCE);value['lib/server/owner-channel.js']+=b'\n// OFFLINE_MUTATION\n'
  self.assertNotEqual(hashlib.sha256(M.frozen_zip(value)).hexdigest(),M.SOURCE_SHA256);self.reject(value)
 def test_26_missing_server_module(self):
  value=dict(SOURCE);value.pop('lib/server/diagnostic-service.js');self.reject(value)
 def test_27_missing_loader(self):
  value=dict(SOURCE);value.pop('lib/server/credential-custody.js');self.reject(value)
 def test_28_missing_registration(self):self.changed('lib/server/deployment-input.js',b'registration_generation: 1, provider, keyset',b'registration_generation: 0, provider: null, keyset')
 def test_29_missing_jwks(self):self.changed('lib/server/deployment-input.js',b'registration_generation: 1, provider, keyset',b'registration_generation: 1, provider, keyset: null')
 def test_30_stale_generation(self):self.changed('lib/server/deployment-input.js',b'registration_generation: 1, provider, keyset',b'registration_generation: 2, provider, keyset')
 def test_31_checklist_has_no_values_and_keeps_hold(self):
  M.scan({'OWNER-CHECKLIST.md':HANDOFF['OWNER-CHECKLIST.md']})
  self.assertIn(b'SECRET_INJECTION_AUTHORIZED = NO',HANDOFF['OWNER-CHECKLIST.md'])
 def test_32_handoff_is_exact_and_secret_free(self):self.assertTrue(M.validate_handoff(HANDOFF,SOURCE))
 def test_33_runtime_support_not_assumed(self):
  config=M.config_review(SOURCE);self.assertEqual(config['actual_account_runtime_duration'],'OWNER_LIVE_REVIEW_REQUIRED')
  value=copy.deepcopy(HANDOFF);c=json.loads(value['deployment-config-summary.json']);c['actual_account_runtime_duration']='VERIFIED';value['deployment-config-summary.json']=M.stable_json(c)
  with self.assertRaises(RuntimeError):M.validate_handoff(value,SOURCE)
 def test_extra_function_denied(self):
  value=dict(SOURCE);config=json.loads(value['vercel.json']);config['functions']['api/admin.js']={'maxDuration':30};value['vercel.json']=M.stable_json(config);self.reject(value)
 def test_extra_redirect_or_rewrite_denied(self):
  for field in ('redirects','rewrites'):
   value=dict(SOURCE);config=json.loads(value['vercel.json']);config[field]=[];value['vercel.json']=M.stable_json(config);self.reject(value)
 def test_private_jwk_literal_denied(self):self.changed('lib/server/deployment-input.js',b'const registered = {',b'const untrusted = {"d":"OFFLINE_PRIVATE_PLACEHOLDER"};const registered = {')
 def test_handoff_extra_environment_rejected_before_content_read(self):
  value=dict(HANDOFF);value['.env']=b'OFFLINE_ENV_PLACEHOLDER'
  with self.assertRaises(RuntimeError):M.validate_handoff(value,SOURCE)
 def test_no_post_deployment_check_can_be_promoted_offline(self):
  value=dict(HANDOFF);e=json.loads(value['POST-DEPLOYMENT-EVIDENCE.json']);e['checks'][0]['status']='VERIFIED';value['POST-DEPLOYMENT-EVIDENCE.json']=M.stable_json(e)
  with self.assertRaises(RuntimeError):M.validate_handoff(value,SOURCE)
 def test_path_output_escape_denied(self):
  with self.assertRaises(RuntimeError):M.safe_output(ROOT/'public-output')
 def test_exact_original_source_passes(self):self.assertEqual(M.validate_source(SOURCE)['classification'],'PASS_SOURCE_INPUT_ONLY')
 def test_handoff_labels_cannot_enable_live_or_authority(self):
  for field,new in (('authority','OWNER'),('real_admission','ENABLED'),('live_diagnostic_enabled',True)):
   value=dict(HANDOFF);labels=json.loads(value['DISABLED-LABELS.json']);labels[field]=new;value['DISABLED-LABELS.json']=M.stable_json(labels)
   with self.assertRaises(RuntimeError):M.validate_handoff(value,SOURCE)
 def test_handoff_cannot_self_attest_modified_source(self):
  value=dict(SOURCE);value['lib/server/owner-channel.js']+=b'\n// UNREVIEWED\n'
  with self.assertRaises(RuntimeError):M.validate_handoff(HANDOFF,value)
 def test_handoff_cannot_duplicate_check_to_omit_evidence(self):
  value=dict(HANDOFF);e=json.loads(value['POST-DEPLOYMENT-EVIDENCE.json']);e['checks'][-1]=e['checks'][0];value['POST-DEPLOYMENT-EVIDENCE.json']=M.stable_json(e)
  with self.assertRaises(RuntimeError):M.validate_handoff(value,SOURCE)
 def test_handoff_cannot_add_hosted_authority_claim(self):
  value=dict(HANDOFF);e=json.loads(value['POST-DEPLOYMENT-EVIDENCE.json']);e['actual_build_verified']=True;value['POST-DEPLOYMENT-EVIDENCE.json']=M.stable_json(e)
  with self.assertRaises(RuntimeError):M.validate_handoff(value,SOURCE)
if __name__=='__main__':unittest.main()
