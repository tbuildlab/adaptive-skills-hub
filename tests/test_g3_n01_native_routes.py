"""Closed native route compatibility, never authentication or live authority."""
import ast
from pathlib import Path
import tempfile
import unittest
from scripts import g3_n01_owner_controller as service
from scripts import build_g3_n01_owner_controller as builder
from tests import test_build_g3_n01_owner_source_custody as old_builder_tests


class NativeRouteTests(unittest.TestCase):
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
            for invalid in (True,0,3,'2'):
                with self.assertRaises(ValueError):custody_builder.build(vector.observation,vector.deployment,path,now_ms=vector.vector.now,custody_revision=invalid)

    def test_revision_two_loader_pins_fixed_routes_and_preserves_default_artifact_contract(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            artifact=builder.build(root,delivery_email_sha256='a'*64,transport_revision=2)
            config=json.loads((root/'source/vercel.json').read_bytes())
            self.assertEqual(len(config['rewrites']),8)
            self.assertTrue(all('*' not in row['source'] and row['destination'].startswith('/api/n01-controller?n01_route=') for row in config['rewrites']))
            self.assertIn('service.CUSTODY_REVISION=2',(root/'source/api/n01-controller.py').read_text())
            self.assertEqual(artifact['authority'],'NONE')


if __name__=='__main__':unittest.main()
