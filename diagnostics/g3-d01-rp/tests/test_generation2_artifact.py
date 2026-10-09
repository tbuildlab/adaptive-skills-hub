"""In-memory adversarial mutation tests; no provider or credential use."""
from pathlib import Path
import copy, hashlib, importlib.util, unittest
SPEC=importlib.util.spec_from_file_location('g2artifact',Path(__file__).resolve().parents[1]/'scripts/verify_generation2.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.reviewed_public_input()

class Generation2Artifacts(unittest.TestCase):
 def setUp(self): self.disabled=M.compose('DISABLED',DATA)
 def reject(self,blobs,profile='DISABLED'):
  with self.assertRaises(RuntimeError): M.validate(blobs,profile,DATA)
 def mutate(self,name,old,new):
  blobs=dict(self.disabled);self.assertIn(old,blobs[name]);blobs[name]=blobs[name].replace(old,new);self.reject(blobs)
 def test_exact_inventory_19(self): self.assertEqual(M.validate(self.disabled,'DISABLED',DATA)['files'],19)
 def test_deterministic(self):
  self.assertEqual(M.HISTORICAL.frozen_zip(self.disabled),M.HISTORICAL.frozen_zip(dict(reversed(list(self.disabled.items())))))
 def test_distinct_from_historical(self): self.assertNotEqual(hashlib.sha256(M.HISTORICAL.frozen_zip(self.disabled)).hexdigest(),M.HISTORICAL.SOURCE_SHA256)
 def test_only_input_changes(self): self.assertEqual({n for n,b in M.originals().items() if b!=self.disabled[n]},{M.INPUT})
 def test_live_changes_only_two_files(self):
  live=M.compose('LIVE_DIAGNOSTIC',DATA)
  self.assertEqual({n for n,b in M.originals().items() if b!=live[n]},{M.INPUT,M.POLICY})
  self.assertEqual(M.validate(live,'LIVE_DIAGNOSTIC',DATA)['authority'],'NONE')
 def test_live_cannot_validate_as_disabled(self): self.reject(M.compose('LIVE_DIAGNOSTIC',DATA))
 def test_unsupported_profile(self):
  with self.assertRaises(RuntimeError): M.compose('PRODUCTION_AUTHORITY',DATA)
 def test_missing_module(self):
  blobs=dict(self.disabled);blobs.pop('lib/server/credential-custody.js');self.reject(blobs)
 def test_extra_env(self):
  blobs=dict(self.disabled);blobs['.env']=b'OFFLINE_CONTAMINATION';self.reject(blobs)
 def test_extra_authority(self):
  blobs=dict(self.disabled);blobs['ash/authority.py']=b'OFFLINE_CONTAMINATION';self.reject(blobs)
 def test_extra_route_d(self):
  blobs=dict(self.disabled);blobs['docs/nexus-route-d-test.md']=b'OFFLINE_CONTAMINATION';self.reject(blobs)
 def test_extra_vercel_state(self):
  blobs=dict(self.disabled);blobs['.vercel/project.json']=b'{}';self.reject(blobs)
 def test_changed_generation(self): self.mutate(M.INPUT,b'"registration_generation": 2',b'"registration_generation": 1')
 def test_changed_origin(self): self.mutate(M.INPUT,b'https://nexus-g3-qual.vercel.app',b'https://other.invalid')
 def test_changed_keyset(self): self.mutate(M.INPUT,b'"alg": "RS256"',b'"alg": "HS256"')
 def test_changed_expiry(self): self.mutate(M.INPUT,str(DATA['keyset']['valid_until']).encode(),b'9999999999999')
 def test_disabled_gate_mutation(self): self.mutate(M.POLICY,b'CODE_REVIEWED_LIVE_ENABLED = false',b'CODE_REVIEWED_LIVE_ENABLED = true')
 def test_public_owner_disclosure(self): self.mutate('public/app.js',b'let csrf=null;',b'let csrf=null;/*'+DATA['provider']['owner_user_id'].encode()+b'*/')
 def test_changed_transport(self): self.mutate('lib/server/stytch-transport.js',b'rejectUnauthorized: true',b'rejectUnauthorized: false')
 def test_changed_provider_route(self): self.mutate(M.POLICY,b'https://test.stytch.com',b'https://api.stytch.com')
 def test_changed_scope(self): self.mutate(M.INPUT,b'"session_max_minutes": 15',b'"session_max_minutes": 60')
 def test_arbitrary_project_input_rejected(self):
  data=copy.deepcopy(DATA);data['provider']['project_id']='project-test-other'
  with self.assertRaises(RuntimeError): M.compose('DISABLED',data)
 def test_arbitrary_owner_input_rejected(self):
  data=copy.deepcopy(DATA);data['provider']['owner_user_id']='user-test-other'
  with self.assertRaises(RuntimeError): M.compose('LIVE_DIAGNOSTIC',data)
 def test_arbitrary_review_window_rejected(self):
  data=copy.deepcopy(DATA);data['keyset']['valid_until']+=86400000
  with self.assertRaises(RuntimeError): M.compose('LIVE_DIAGNOSTIC',data)

if __name__=='__main__':unittest.main()
