"""Runtime binding adversaries only; synthetic enrollment never grants authority."""
import copy
from dataclasses import replace
from pathlib import Path
import unittest
from unittest.mock import patch

from ash import g3_delegated_control_codec as codec
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from scripts import g3_n01_storage_contract as storage
from tests import test_g3_d03_s3_fence as fake

ROOT=Path(__file__).resolve().parents[1]


class SourceEnrollmentTests(unittest.TestCase):
    def setUp(self):
        proposal=codec.canonical(codec.decode((ROOT/'research/nexus-production-n01-pending-public-pin-review-v1.json').read_bytes().rstrip()))
        receipt=codec.canonical(codec.decode((ROOT/'research/nexus-production-n01-public-pin-owner-acceptance-v1.json').read_bytes().rstrip()))
        self.now=review.FROM_MS+1000;self.review=review.verify_review(proposal,receipt,now_ms=self.now)
        self.clock=patch('ash.g3_n01_source_enrollment.time.time',return_value=self.now/1000)
        self.clock.start();self.addCleanup(self.clock.stop)
        self.value=dict(schema_version='nexus.g3.n01.current-source-enrollment.v1',
            purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode='DELEGATED_EXECUTOR',
            authority_config_sha256=source.CONFIG,authority_instance='g3-n01-qualification-v1',
            application_generation=1,review_generation=1,service_revision='nexus-g3-n01-controller-v1',
            review_package_sha256=review.PACKAGE_SHA,review_acceptance_sha256=review.ACCEPTANCE_SHA,
            principal=dict(issuer='stytch.com/'+source.PROJECT,client_id=source.PROJECT,subject=source.OWNER),
            deployment_id='dpl_'+'A'*24,deployment_host='nexus-g3-qual-synthetic-tdy0225.vercel.app',
            host_project_id=source.HOST_PROJECT,artifact_inventory_sha256='c'*64,process_nonce='d'*64,
            source_kinds=['D01','D03','OWNER_ENROLLMENT'],issued_at_ms=review.FROM_MS,
            expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        self.env=dict(VERCEL_ENV='production',VERCEL_PROJECT_ID=source.HOST_PROJECT,
            VERCEL_DEPLOYMENT_ID=self.value['deployment_id'],VERCEL_URL=self.value['deployment_host'])
    def bind(self,value=None,**kw):
        args=dict(native_environment=self.env,artifact_inventory_sha256='c'*64,process_nonce='d'*64,now_ms=self.now)
        args.update(kw)
        return source.bind_source(codec.canonical(self.value if value is None else value),self.review,**args)
    def test_exact_source_binding_is_none_not_production_membership(self):
        bound=self.bind();self.assertEqual(bound.authority,'NONE')
        value=bound.value;value['real_admission']='YES'
        self.assertEqual(bound.value['real_admission'],'NO')
    def test_restart_deployment_project_or_host_mismatch_denies(self):
        for field in self.env:
            env=dict(self.env);env[field]='different'
            with self.subTest(field=field),self.assertRaises(ValueError):self.bind(native_environment=env)
        with self.assertRaises(ValueError):self.bind(process_nonce='e'*64)
        with self.assertRaises(ValueError):self.bind(artifact_inventory_sha256='e'*64)
    def test_unapproved_source_kind_generation_principal_or_admission_denies(self):
        for field,value in (('source_kinds',['D01','D04','OWNER_ENROLLMENT']),('review_generation',2),
            ('application_generation',True),('real_admission','YES'),('purpose','PRODUCTION'),
            ('principal',dict(issuer='stytch.com/'+source.PROJECT,client_id=source.PROJECT,subject='email'))):
            obj=copy.deepcopy(self.value);obj[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.bind(obj)
    def test_window_does_not_extend_or_accept_future_enrollment(self):
        for field,value in (('issued_at_ms',self.now+1),('expires_at_ms',review.UNTIL_MS+1)):
            obj=dict(self.value);obj[field]=value
            with self.assertRaises(ValueError):self.bind(obj)
        with self.assertRaises(ValueError):self.bind(now_ms=review.UNTIL_MS)
    def test_missing_unknown_or_noncanonical_enrollment_denies(self):
        for obj in (dict(self.value,unknown=1),{k:v for k,v in self.value.items() if k!='principal'}):
            with self.assertRaises(ValueError):self.bind(obj)
        with self.assertRaises(ValueError):source.bind_source(codec.canonical(self.value)+b'\n',self.review,
            native_environment=self.env,artifact_inventory_sha256='c'*64,process_nonce='d'*64,now_ms=self.now)
    def custody(self,mode=None):
        _,_,_,_,registration=storage.inputs(source.CONFIG,1)
        scope=replace(storage.scope(registration),generation=2)
        client=fake.MemoryS3();key=source.PREFIX+'registration.json'
        if mode!='missing':client.add(key,codec.canonical(self.value),retained=mode!='expired')
        if mode=='duplicate':client.add(key,codec.canonical(self.value),duplicate=True)
        if mode=='unavailable':client.mode='unavailable'
        return source.read_protected_source(client,scope,self.review,native_environment=self.env,
            artifact_inventory_sha256='c'*64,process_nonce='d'*64,now_ms=self.now),client
    def test_retained_source_read_never_mutates_or_upgrades_history(self):
        result,client=self.custody();self.assertEqual(result.authority,'NONE')
        self.assertFalse(any(call[0]=='put' for call in client.calls))
    def test_missing_ambiguous_expired_unavailable_source_custody_denies(self):
        for mode in ('missing','duplicate','expired','unavailable'):
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'N01_SOURCE_CUSTODY_QUARANTINE'):
                self.custody(mode)
    def test_expiry_during_source_read_or_clock_regression_denies(self):
        for finish in (review.UNTIL_MS,self.now-1):
            with patch('ash.g3_n01_source_enrollment.time.time',side_effect=[self.now/1000,finish/1000]),self.assertRaises(ValueError):
                self.custody()


if __name__=='__main__':unittest.main()
