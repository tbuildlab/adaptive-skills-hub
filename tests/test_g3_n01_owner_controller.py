"""Synthetic controller boundaries only; no native identity or AWS authority."""
from contextlib import redirect_stdout
from email.message import Message
from io import BytesIO,StringIO
import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock
from scripts import g3_n01_owner_controller as service
from scripts import build_g3_n01_owner_controller as builder
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_controller_bootstrap as boot
from ash import g3_delegated_control_codec as codec
from ash import g3_checkpoint_custody as custody
from ash import g3_n01_owner_context as owner
from ash import g3_n02_presentation as presentation
from ash.g3_primary_ledger import DelegatedDynamoReservations
from scripts import g3_n01_storage_contract as storage
from tests import test_g3_n01_checkpoint_custody as custody_fixture
from tests import test_g3_primary_ledger as ledger_fixture


class OwnerControllerTests(unittest.TestCase):
    def setUp(self):
        service.CONTROLLER=None;service.PROBE_USED=False
        self.clock=patch('time.time',return_value=(review.FROM_MS+1000)/1000)
        self.clock.start();self.addCleanup(self.clock.stop)
        self.env=dict(VERCEL_ENV='production',VERCEL_PROJECT_ID=source.HOST_PROJECT,
            VERCEL_URL='nexus-g3-qual-abc123-tdy0225.vercel.app',VERCEL_DEPLOYMENT_ID='dpl_ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    def headers(self,post=False):
        headers=Message();headers['Host']=self.env['VERCEL_URL'];headers['x-vercel-oidc-token']='SYNTHETIC_ONLY_NOT_AUTHORITY'
        if post:
            headers['Origin']='https://'+self.env['VERCEL_URL'];headers['Content-Type']='application/x-www-form-urlencoded'
            headers['Content-Length']='17';headers['Cookie']='SYNTHETIC_ONLY_NOT_AUTHORITY'
        return headers
    def call(self,path='/api/n01-controller',method='GET',headers=None,body=b'operation=recover'):
        obj=object.__new__(service.handler);obj.path=path;obj.command=method
        obj.headers=self.headers(method=='POST') if headers is None else headers;obj.wfile=BytesIO();obj.rfile=BytesIO(body)
        obj.statuses=[];obj.send_response=lambda value:obj.statuses.append(value)
        obj.send_header=lambda *args:None;obj.end_headers=lambda:None
        output=StringIO()
        with patch.dict(service.os.environ,self.env,clear=True),redirect_stdout(output):
            obj.do_POST() if method=='POST' else obj.do_GET()
        return obj.statuses,obj.wfile.getvalue(),output.getvalue()
    def test_exact_http_identity_and_closed_route_origin_cardinality_before_any_probe(self):
        with patch.object(service,'OwnerController') as native:
            for path in ('/api/n01-controller?x=1','/api/n01/recover','/api/n01/missing'):
                self.assertEqual(self.call(path=path)[0],[403])
            for key,value in (('Host',self.env['VERCEL_URL']),('Origin','https://evil.invalid'),
                ('x-vercel-oidc-token','SYNTHETIC_DUPLICATE'),('Content-Length','1'),('Transfer-Encoding','chunked')):
                headers=self.headers();headers[key]=value;self.assertEqual(self.call(headers=headers)[0],[403])
            headers=self.headers(True);headers['Origin']='https://'+self.env['VERCEL_URL']
            self.assertEqual(self.call('/api/n01/recover','POST',headers)[0],[403])
            with patch('time.time',return_value=review.UNTIL_MS/1000):self.assertEqual(self.call()[0],[403])
            native.assert_not_called()
    def test_unknown_probe_has_no_automatic_retry_or_exception_leak(self):
        with patch.object(boot,'measure_artifact',return_value='a'*64),patch.object(service,'OwnerController',side_effect=RuntimeError('SECRET_SENTINEL')) as native:
            first=self.call();second=self.call()
        self.assertEqual(first[:2],second[:2]);self.assertEqual(first[0],[403]);self.assertEqual(native.call_count,1)
        self.assertNotIn('SECRET_SENTINEL',str(first));self.assertTrue(service.PROBE_USED)
    def test_no_cold_post_or_status_restores_context_or_invokes_storage(self):
        with patch.object(service,'OwnerController') as native:
            self.assertEqual(self.call('/api/n01/status')[0],[403])
            self.assertEqual(self.call('/api/n01/recover','POST')[0],[403]);native.assert_not_called()
    def test_successful_probe_reuses_same_process_and_only_public_proposal(self):
        fake=Mock();fake.proposal.return_value=dict(status='SOURCE_PROPOSAL_READY_NONE',authority='NONE',real_admission='NO')
        with patch.object(boot,'measure_artifact',return_value='a'*64),patch.object(service,'OwnerController',return_value=fake) as native:
            self.assertEqual(self.call()[0],[200]);self.assertEqual(self.call()[0],[200]);self.assertEqual(native.call_count,1)
        self.assertIs(service.CONTROLLER,fake)
    def test_form_shape_duplicate_extra_malformed_oversize_denies(self):
        self.assertEqual(service.form(b'operation=recover',('operation',)),{'operation':'recover'})
        for raw in (b'operation=recover&operation=enroll',b'operation=recover&authority=PASS',b'operation=%zz',b'\xff',b'x'*4097,b''):
            with self.assertRaises(ValueError):service.form(raw,('operation',))
    def test_render_failure_returns_one_deny_without_partial_form_or_secret(self):
        fake=Mock();fake.display.side_effect=RuntimeError('SECRET_SENTINEL');service.CONTROLLER=fake
        result=self.call('/api/n01/confirm')
        self.assertEqual(result[0],[403]);self.assertNotIn(b'SECRET_SENTINEL',result[1])
    def test_exact_artifact_measures_complete_controller_without_fixtures_credentials_or_old_d01(self):
        with tempfile.TemporaryDirectory() as temp:
            result=builder.build(Path(temp),delivery_email_sha256='a'*64);root=Path(temp)/'source'
            self.assertEqual(boot.measure_artifact(root,result['files']['source-inventory.json']['sha256']),result['artifact_inventory_sha256'])
            names=set(result['files']);self.assertTrue(set(builder.OWNER_MODULES)<=names)
            self.assertFalse(any(name.startswith(('tests/','public/','lib/')) or '.env' in name for name in names))
            self.assertEqual(result['real_admission'],'NO');self.assertEqual(result['grant_issuance'],'NOT_IMPLEMENTED')
            config=json.loads((root/'vercel.json').read_bytes())
            self.assertEqual(config['rewrites'],[{'source':'/api/n01/:path*','destination':'/api/n01-controller'}])
            for name in names:
                if name.endswith('.py'):
                    tree=ast.parse((root/name).read_text())
                    self.assertFalse(any(isinstance(node,ast.ImportFrom) and (node.module or '').startswith('tests') for node in ast.walk(tree)))
            (root/'ash/g3_n01_owner_protocol.py').write_bytes(b'changed')
            with self.assertRaises(ValueError):boot.measure_artifact(root,result['files']['source-inventory.json']['sha256'])
    def prepared_controller(self):
        vector=custody_fixture.N01CustodyTests();vector.setUp();vector.client.rows.clear()
        vector.before,vector.head,vector.descriptor,vector.next,vector.registration=storage.inputs(source.CONFIG,1)
        vector.scope=storage.scope(vector.registration)
        vector.install(vector.head,vector.before.snapshot,vector.descriptor,0)
        old_head,registration=vector.recovery()
        scope_patch=patch.object(boot,'storage_scope',return_value=storage.scope(registration))
        scope_patch.start();self.addCleanup(scope_patch.stop)
        primary=ledger_fixture.MemoryClient()
        ledger=DelegatedDynamoReservations(primary,table_arn=ledger_fixture.ARN,instance=custody.INSTANCE,max_attempts=256)
        # Synthetic previous READY state only; not a restoration API or authority.
        primary.items['HEAD']=dict(ledger._key('HEAD'),phase={'S':'READY'},checkpoint={'B':old_head.checkpoint},sequence={'N':'2'})
        primary.items['blob#'+codec.digest(old_head.checkpoint)]=dict(ledger._key('blob#'+codec.digest(old_head.checkpoint)),body={'B':old_head.checkpoint})
        root=Path(__file__).resolve().parents[1]
        proposal=codec.canonical(codec.decode((root/'research/nexus-production-n01-pending-public-pin-review-v1.json').read_bytes().rstrip()))
        acceptance=codec.canonical(codec.decode((root/'research/nexus-production-n01-public-pin-owner-acceptance-v1.json').read_bytes().rstrip()))
        public=review.verify_review(proposal,acceptance,now_ms=review.FROM_MS+1000)
        transport=Mock(primary=primary,custody=vector.client,ddb_attempts=0,s3_attempts=0)
        with patch.object(service.native,'NativeTransport',return_value=transport),patch.object(review,'read_protected_review',return_value=public),redirect_stdout(StringIO()):
            controller=service.OwnerController('SYNTHETIC_ONLY',self.env,'a'*64)
        value=controller.proposal()['source_proposal']
        enrolled=source.bind_source(codec.canonical(value),public,native_environment=self.env,
            artifact_inventory_sha256='a'*64,process_nonce=boot.PROCESS_NONCE,now_ms=review.FROM_MS+1000)
        transport.enable_owner_storage.return_value=enrolled
        authorization=controller.proposal()['recovery_authorization']
        vector.client.add(service.persistence.RECOVERY_PREFIX+'00000000000000000003/authorization.json',codec.canonical(authorization))
        headers=Message();headers['Cookie']='__Host-NexusN01Maintenance=SYNTHETIC_ONLY'
        # Authentication/source injection exists only in tests; native runtime
        # has no interchangeable transports or caller-supplied verdict routes.
        return controller,transport,primary,headers,enrolled
    def test_real_durability_composition_model_finalizes_recovery_and_source_as_none(self):
        controller,transport,primary,headers,enrolled=self.prepared_controller()
        with patch.object(service.OwnerController,'_OwnerController__maintenance_gate'),\
            patch.object(service.persistence.source,'read_protected_source',return_value=enrolled),redirect_stdout(StringIO()):
            self.assertEqual(controller.maintain('recover',headers,'SYNTHETIC_ONLY'),'RECOVERED_OWNER_LINEAGE_NONE')
            self.assertEqual(controller.maintain('enroll',headers,'SYNTHETIC_ONLY'),'OWNER_SOURCE_ENROLLED_NONE')
        self.assertEqual(primary.items['HEAD']['sequence'],{'N':'4'})
        for sequence in (3,4):self.assertEqual(primary.items[f'reservation#{sequence:020d}']['phase'],{'S':'FINALIZED'})
        self.assertEqual(controller.status()['authority'],'NONE');self.assertEqual(controller.status()['execution'],'DENY')
    def test_missing_independent_source_quarantines_before_mutation_without_retry(self):
        controller,transport,primary,headers,enrolled=self.prepared_controller()
        transport.enable_owner_storage.side_effect=ValueError('SECRET_SENTINEL')
        before=len(primary.calls)
        with patch.object(service.OwnerController,'_OwnerController__maintenance_gate'):
            for _ in range(2):
                with self.assertRaisesRegex(ValueError,'^N01_NATIVE_OWNER_MAINTENANCE_QUARANTINE$'):
                    controller.maintain('recover',headers,'SYNTHETIC_ONLY')
        self.assertEqual(len(primary.calls),before);self.assertEqual(transport.enable_owner_storage.call_count,1)
        self.assertEqual(controller.phase,'QUARANTINE')
    def test_complete_owner_only_durability_stays_inside_original_backend_bounds(self):
        controller,transport,primary,headers,enrolled=self.prepared_controller()
        source_reads=[]
        def read_source(*args,**kwargs):source_reads.append(4);return enrolled
        with patch.object(service.OwnerController,'_OwnerController__maintenance_gate'),\
            patch.object(service.persistence.source,'read_protected_source',side_effect=read_source),redirect_stdout(StringIO()):
            controller.maintain('recover',headers,'SYNTHETIC_ONLY');controller.maintain('enroll',headers,'SYNTHETIC_ONLY')
            now=review.FROM_MS+1000
            projection=owner.OwnerProjection(owner.PROJECT,owner.OWNER,
                'session-test-12345678-1234-1234-1234-123456789012',now-50,now+900000,'a'*64)
            history=controller._OwnerController__history
            candidate,objects,challenge,view=service.protocol.prepare_challenge(history,enrolled,projection,
                deadline_ms=now+200000,nonce='b'*64,now_ms=now)
            controller._commit(candidate,objects)
            shown=presentation.render(challenge,view,csrf='c'*64,now_ms=now)
            decision=presentation.UntrustedDecision('CONFIRM',shown.challenge_id,shown.view_id,shown.proposal_id,shown.nonce,shown.presentation_sha256)
            candidate,objects=service.protocol.prepare_decision(controller._OwnerController__history,enrolled,decision,projection,now_ms=now)
            controller._commit(candidate,objects)
            candidate,objects=service.protocol.prepare_revoke_after_consumption(controller._OwnerController__history,enrolled,
                remote_result='EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY',now_ms=now)
            controller._commit(candidate,objects)
        self.assertEqual(primary.items['HEAD']['sequence'],{'N':'7'})
        self.assertLessEqual(len(primary.calls),service.native.MAX_DDB)
        self.assertLessEqual(len(transport.custody.calls)+sum(source_reads),service.native.MAX_S3)


if __name__=='__main__':unittest.main()
