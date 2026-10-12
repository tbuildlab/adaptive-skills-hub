"""Simulated bootstrap contracts; never enrolled runtime or live AWS evidence."""
from contextlib import redirect_stdout
from email.message import Message
from io import BytesIO,StringIO
import json
import ast
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock

from ash import g3_n01_controller_bootstrap as boot
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from scripts import g3_n01_controller_bootstrap as service
from scripts import build_g3_n01_controller_bootstrap as builder


class ControllerBootstrapTests(unittest.TestCase):
    def setUp(self):
        service.OUTCOME=None
        self.clock=patch('time.time',return_value=(review.FROM_MS+1)/1000)
        self.clock.start();self.addCleanup(self.clock.stop)
        self.environment={'VERCEL_ENV':'production','VERCEL_PROJECT_ID':source.HOST_PROJECT,
            'VERCEL_URL':'nexus-g3-qual-abc123-tdy0225.vercel.app',
            'VERCEL_DEPLOYMENT_ID':'dpl_ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
    def headers(self):
        value=Message();value['Host']=self.environment['VERCEL_URL']
        value['x-vercel-oidc-token']='TEST_ONLY_NATIVE_INPUT_NOT_AUTHORITY'
        return value
    def call(self,path='/api/n01-controller',method='GET',headers=None):
        obj=object.__new__(service.handler);obj.path=path;obj.command=method
        obj.headers=self.headers() if headers is None else headers;obj.wfile=BytesIO()
        obj.send_response=lambda status:setattr(obj,'status',status)
        obj.send_header=lambda *args:None;obj.end_headers=lambda:None
        output=StringIO()
        with patch.dict(service.os.environ,self.environment,clear=True),redirect_stdout(output):obj.do_GET()
        result=json.loads(obj.wfile.getvalue())
        self.assertEqual(json.loads(output.getvalue())['n01_controller_bootstrap_readback'],result)
        return obj.status,result
    def test_wrong_native_deployment_environment_denies_before_io(self):
        with patch.object(boot,'bootstrap') as io:
            for field,value in (('VERCEL_ENV','preview'),('VERCEL_PROJECT_ID','other'),
                    ('VERCEL_DEPLOYMENT_ID','dpl_short'),('VERCEL_URL','nexus-g3-qual.vercel.app')):
                original=self.environment[field];self.environment[field]=value
                self.assertEqual(self.call()[0],403);self.environment[field]=original
            io.assert_not_called()
    def test_wrong_method_query_duplicate_headers_body_origin_denies(self):
        with patch.object(boot,'bootstrap') as io:
            self.assertEqual(self.call(method='POST')[0],403)
            self.assertEqual(self.call(path='/api/n01-controller?x=1')[0],403)
            for field,value in (('Host',self.environment['VERCEL_URL']),
                    ('x-vercel-oidc-token','SECOND_FIXTURE'),('Content-Length','1'),
                    ('Origin','https://example.invalid'),('Transfer-Encoding','chunked')):
                headers=self.headers();headers[field]=value;self.assertEqual(self.call(headers=headers)[0],403)
            headers=self.headers();headers['Content-Length']='0';headers['Content-Length']='1'
            self.assertEqual(self.call(headers=headers)[0],403)
            io.assert_not_called()
    def test_expiry_denies_cached_bootstrap_without_renewal(self):
        service.OUTCOME={'status':'NATIVE_PUBLIC_REVIEW_BOOTSTRAP_VERIFIED','authority':'NONE','real_admission':'NO'}
        with patch('time.time',return_value=review.UNTIL_MS/1000),patch.object(boot,'bootstrap') as io:
            self.assertEqual(self.call()[0],403);io.assert_not_called()
    def test_unknown_is_terminal_no_retry_or_exception_leak(self):
        with patch.object(service,'ARTIFACT_ROOT',Path('.')),patch.object(service,'EXPECTED_MANIFEST_SHA','0'*64),\
                patch.object(boot,'measure_artifact',return_value='0'*64),\
                patch.object(boot,'bootstrap',side_effect=RuntimeError('SECRET_SENTINEL')) as io:
            first=self.call();self.assertEqual(first,self.call());self.assertEqual(first[0],503)
            self.assertNotIn('SECRET_SENTINEL',json.dumps(first));self.assertEqual(io.call_count,1)
    def test_complete_artifact_measurement_and_source_tamper_denies(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata=builder.build(Path(tmp));root=Path(tmp)/'source'
            expected=metadata['files']['source-inventory.json']['sha256']
            loader=ast.parse((root/'api/n01-controller.py').read_text())
            handler=next(node for node in loader.body if isinstance(node,ast.ClassDef))
            self.assertEqual(handler.name,'handler')
            self.assertIn('BaseHTTPRequestHandler',[base.id for base in handler.bases if isinstance(base,ast.Name)])
            self.assertEqual(boot.measure_artifact(root,expected),metadata['artifact_inventory_sha256'])
            (root/'ash/g3_n01_public_review.py').write_bytes(b'changed')
            with self.assertRaises(ValueError):boot.measure_artifact(root,expected)
    def test_loader_manifest_and_path_traversal_are_measured_or_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata=builder.build(Path(tmp));root=Path(tmp)/'source'
            expected=metadata['files']['source-inventory.json']['sha256']
            (root/'api/n01-controller.py').write_bytes(b'changed loader')
            self.assertNotEqual(boot.measure_artifact(root,expected),metadata['artifact_inventory_sha256'])
            raw=b'{"../outside":{"bytes":0,"sha256":""}}'
            (root/'source-inventory.json').write_bytes(raw)
            with self.assertRaises(ValueError):boot.measure_artifact(root,boot.hashlib.sha256(raw).hexdigest())
    def test_public_transport_mutation_or_wrong_prefix_denies_and_unknown_retires(self):
        client=Mock();native=boot.PublicCustodyClient(client)
        kwargs={'Bucket':'nexus-d03-custody-862902859484-ap-southeast-1-v1','ExpectedBucketOwner':'862902859484'}
        for operation,key in (('put_object',review.PREFIX+'proposal.json'),('get_object','unrelated')):
            with self.assertRaises(ValueError):getattr(native,operation)(Key=key,**kwargs)
        self.assertEqual(native.attempts,0)
        client.get_object.side_effect=RuntimeError('SECRET_SENTINEL')
        with self.assertRaisesRegex(ValueError,'N01_BOOTSTRAP_CUSTODY_QUARANTINE'):
            native.get_object(Key=review.PREFIX+'proposal.json',**kwargs)
        self.assertTrue(native.retired)
        with self.assertRaises(ValueError):native.get_object(Key=review.PREFIX+'proposal.json',**kwargs)
        self.assertEqual(native.attempts,1)
    def test_bootstrap_has_no_identity_or_storage_authority(self):
        current=Mock(package_sha256=review.PACKAGE_SHA,acceptance_sha256=review.ACCEPTANCE_SHA,
                     valid_until_ms=review.UNTIL_MS)
        client=Mock(attempts=6)
        with patch.object(boot,'native_public_custody',return_value=client),\
                patch.object(review,'read_protected_review',return_value=current):
            result=boot.bootstrap('FIXTURE_NATIVE_ONLY',self.environment,'0'*64)
        self.assertEqual(result['authority'],'NONE');self.assertEqual(result['real_admission'],'NO')
        self.assertEqual(result['source_enrollment'],'NOT_PERFORMED');self.assertEqual(result['owner_context'],'NOT_CREATED')
        self.assertEqual(result['ddb_attempts'],0);client.close.assert_called_once()
        self.assertEqual(boot.storage_scope().genesis_sha256,
            '7fe0fb527ce2c8bb519a0f837124bfce22ce8e964008f2aa0fc7b4f1c9b036db')
