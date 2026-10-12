"""Closed native route compatibility, never authentication or live authority."""
import ast
from pathlib import Path
import tempfile
import unittest
from scripts import g3_n01_owner_controller as service
from scripts import build_g3_n01_owner_controller as builder
from tests import test_build_g3_n01_owner_source_custody as old_builder_tests


class NativeRouteTests(unittest.TestCase):
    def test_native_original_path_with_exact_matching_rewrite_selector_only(self):
        for route in ('start','login','confirm','status','recover','enroll','decision','revoke'):
            self.assertEqual(service.canonical_route('/api/n01/'+route+'?n01_route='+route),'/api/n01/'+route)
        for raw in ('/api/n01/start?n01_route=recover','/api/n01/start?n01_route=start&x=1',
                    '/api/n01/start?n01_route=start&n01_route=start','/api/n01/start?n01_route=%73tart'):
            self.assertEqual(service.canonical_route(raw),raw)

    def test_revision_two_cannot_fall_back_to_old_independent_source(self):
        from dataclasses import replace
        from ash import g3_n01_source_enrollment as source
        from ash import g3_checkpoint_custody as custody
        from ash import g3_delegated_control_codec as codec
        from scripts import g3_n01_storage_contract as storage
        from tests import test_g3_n01_source_enrollment as vectors
        from tests import test_g3_d03_s3_fence as fake
        vector=vectors.SourceEnrollmentTests();vector.setUp();self.addCleanup(vector.doCleanups)
        _,_,_,_,registration=storage.inputs(source.CONFIG,1)
        scope=replace(storage.scope(registration),generation=2)
        client=fake.MemoryS3();raw=codec.canonical(vector.value)
        client.add(source.PREFIX+'registration.json',raw)
        args=dict(native_environment=vector.env,artifact_inventory_sha256='c'*64,process_nonce='d'*64,now_ms=vector.now,custody_revision=2)
        with self.assertRaises(ValueError):source.read_protected_source(client,scope,vector.review,**args)
        key=custody.APPROVALS+'current-source-controller-v2/registration.json';client.add(key,raw)
        self.assertEqual(source.read_protected_source(client,scope,vector.review,**args).authority,'NONE')
        with self.assertRaises(ValueError):source.read_protected_source(client,scope,vector.review,**dict(args,process_nonce='e'*64))

    def test_only_exact_fixed_internal_selector_maps_to_existing_closed_routes(self):
        for route in ('start','login','confirm','status','recover','enroll','decision','revoke'):
            self.assertEqual(service.canonical_route('/api/n01-controller?n01_route='+route),'/api/n01/'+route)
        for raw in ('/api/n01-controller?x=start','/api/n01-controller?n01_route=start&n01_route=start',
                    '/api/n01-controller?n01_route=%73tart','/api/n01-controller?n01_route=start&authority=PASS',
                    '/api/n01-controller?n01_route=unknown','https://evil.invalid/api/n01/start'):
            self.assertEqual(service.canonical_route(raw),raw)

    def test_revision_two_has_two_new_fixed_prefixes_and_distinct_attempt_receipt(self):
        from scripts import build_g3_n01_owner_source_custody as custody_builder
        from ash import g3_checkpoint_custody as custody
        vector=old_builder_tests.OwnerSourceBuilderTests();vector.setUp()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'r.py'
            result=custody_builder.build(vector.observation,vector.deployment,path,now_ms=vector.vector.now,custody_revision=2)
            tree=ast.parse(path.read_text())
            payload=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and node.targets[0].id=='PAYLOAD')
            self.assertEqual(set(payload),{custody.APPROVALS+'current-source-controller-v2/registration.json',
                custody.APPROVALS+'owner-controller-recovery-v2/00000000000000000003/authorization.json'})
            self.assertIn('n01-owner-source-v2-r-receipt.json',path.read_text())
            self.assertEqual(result['authority'],'NONE')
            for invalid in (True,0,4,'2'):
                with self.assertRaises(ValueError):custody_builder.build(vector.observation,vector.deployment,path,now_ms=vector.vector.now,custody_revision=invalid)

    def test_form_origin_correction_keeps_historical_header_contract_and_exact_origin_required(self):
        from io import BytesIO
        from ash import g3_n02_presentation as presentation
        obj=object.__new__(service.handler);obj.send_response=lambda x:None;headers={};obj.send_header=lambda k,v:headers.update({k:v})
        obj._headers(html=True)
        self.assertEqual(headers['Referrer-Policy'],'same-origin')
        self.assertEqual(presentation.response_headers()['Referrer-Policy'],'no-referrer')
        self.assertIn("form-action 'self'",headers['Content-Security-Policy'])
        from tests import test_g3_n01_owner_controller as vectors
        vector=vectors.OwnerControllerTests();vector.setUp();self.addCleanup(vector.doCleanups)
        for origin in ('null','https://evil.invalid'):
            hdr=vector.headers(True);hdr.replace_header('Origin',origin)
            self.assertFalse(service.request_allowed('/api/n01/recover','POST',hdr,vector.env))

    def test_revision_three_is_independent_of_prior_retained_attempts(self):
        from scripts import build_g3_n01_owner_source_custody as custody_builder
        from ash import g3_checkpoint_custody as custody
        vector=old_builder_tests.OwnerSourceBuilderTests();vector.setUp()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'r.py'
            custody_builder.build(vector.observation,vector.deployment,path,now_ms=vector.vector.now,custody_revision=3)
            tree=ast.parse(path.read_text())
            payload=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and node.targets[0].id=='PAYLOAD')
            self.assertEqual(set(payload),{custody.APPROVALS+'current-source-controller-v3/registration.json',
                custody.APPROVALS+'owner-controller-recovery-v3/00000000000000000003/authorization.json'})
            self.assertIn('n01-owner-source-v3-r-receipt.json',path.read_text())

    def test_revision_three_uses_one_existing_hobby_region_near_the_bound_data_plane(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);builder.build(root,delivery_email_sha256='a'*64,transport_revision=3)
            config=json.loads((root/'source/vercel.json').read_bytes())
            self.assertEqual(config['regions'],['sin1']);self.assertNotIn('functionFailoverRegions',config)
            request=json.loads((root/'exact-body.json').read_bytes())
            self.assertEqual(request['projectSettings']['serverlessFunctionRegion'],'sin1')
            self.assertIn('service.CUSTODY_REVISION=3',(root/'source/api/n01-controller.py').read_text())

    def test_revision_two_loader_pins_fixed_routes_and_preserves_default_artifact_contract(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            artifact=builder.build(root,delivery_email_sha256='a'*64,transport_revision=2)
            config=json.loads((root/'source/vercel.json').read_bytes())
            self.assertEqual(len(config['rewrites']),8)
            self.assertEqual(config['functions']['api/n01-controller.py']['maxDuration'],300)
            self.assertTrue(all('*' not in row['source'] and row['destination'].startswith('/api/n01-controller?n01_route=') for row in config['rewrites']))
            self.assertIn('service.CUSTODY_REVISION=2',(root/'source/api/n01-controller.py').read_text())
            self.assertEqual(artifact['authority'],'NONE')


if __name__=='__main__':unittest.main()
