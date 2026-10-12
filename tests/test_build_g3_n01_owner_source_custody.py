"""Synthetic public-record builder only; never actual R enrollment."""
import ast
import copy
from pathlib import Path
import tempfile
import unittest
from scripts import build_g3_n01_owner_source_custody as builder
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_delegated_control_codec as codec
from tests import test_g3_n01_source_enrollment as fixture


class OwnerSourceBuilderTests(unittest.TestCase):
    def setUp(self):
        self.vector=fixture.SourceEnrollmentTests();self.vector.setUp();self.addCleanup(self.vector.doCleanups)
        enrolled=self.vector.bind();value=enrolled.value
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',
            authority_mode='DELEGATED_EXECUTOR',authority_config_sha256=source.CONFIG,source_enrollment_sha256=enrolled.enrollment_sha256,
            checkpoint=dict(id='nexus.g3.production.recovery-checkpoint.v2:'+'a'*64,body_sha256='b'*64),
            previous_checkpoint=dict(id=builder.boot.HEAD_ID,body_sha256='52dd16d2303656eec0f3c6413e5337f03cb1e64531b7acf8ace920bcaf89ad41'),
            authority_epoch=3,incarnation='n01-owner-'+value['process_nonce'][:32],application_generation=1,review_generation=1,
            expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        self.observation=dict(status='SOURCE_PROPOSAL_READY_NONE',source_proposal=value,source_sha256=enrolled.enrollment_sha256,
            recovery_authorization=authorization,recovery_authorization_sha256=codec.digest(codec.canonical(authorization)),
            public_review='EXACT_RETAINED_REVIEW_VERIFIED',current_owner='NOT_AUTHENTICATED',authority='NONE',real_admission='NO')
        count=len(set((*builder.builder.MODULES,*(name for name in builder.builder.EXTRA if name!='scripts/g3_n01_controller_bootstrap.py'),*builder.builder.OWNER_MODULES)))+6
        self.deployment=dict(readyState='READY',target='production',projectId=source.HOST_PROJECT,id=value['deployment_id'],
            url=value['deployment_host'],native_sso_protection='all_except_custom_domains',source_identity_matches=count)
    def build(self,observation=None,deployment=None):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'r.py'
            result=builder.build(self.observation if observation is None else observation,
                self.deployment if deployment is None else deployment,path,now_ms=self.vector.now)
            return result,path.read_text()
    def test_exact_two_public_prefixes_fixed_root_and_one_attempt_receipt(self):
        result,program=self.build();tree=ast.parse(program)
        payload=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and node.targets[0].id=='PAYLOAD')
        self.assertEqual(set(payload),{source.PREFIX+'registration.json',builder.persistence.RECOVERY_PREFIX+'00000000000000000003/authorization.json'})
        self.assertEqual((result['new_objects'],result['maximum_s3_attempts'],result['authority']),(2,16,'NONE'))
        self.assertIn('n01-owner-source-r-receipt.json',program)
        self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',program);self.assertIn("ObjectLockMode='COMPLIANCE'",program)
        self.assertIn("identity['Arn']=='arn:aws:iam::'+OWNER+':root'",program)
        self.assertLessEqual(result['maximum_public_bytes'],16384)
    def test_wrong_actual_deployment_artifact_identity_protection_or_window_denies(self):
        for key,value in (('readyState','ERROR'),('projectId','wrong'),('id','dpl_wrong'),('url','different'),
            ('native_sso_protection','disabled'),('source_identity_matches',1)):
            with self.assertRaises(ValueError):self.build(deployment=dict(self.deployment,**{key:value}))
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(ValueError):
            builder.build(self.observation,self.deployment,Path(tmp)/'r.py',now_ms=review.UNTIL_MS)
    def test_wrong_scope_principal_generation_digest_or_predecessor_denies(self):
        for key,value in (('real_admission','YES'),('current_owner','AUTHENTICATED'),('source_sha256','e'*64)):
            with self.assertRaises(ValueError):self.build(observation=dict(self.observation,**{key:value}))
        for key,value in (('purpose','PRODUCTION'),('authority_epoch',2),('expires_at_ms',review.UNTIL_MS+1),
            ('source_enrollment_sha256','e'*64),('previous_checkpoint',dict(self.observation['recovery_authorization']['previous_checkpoint'],body_sha256='f'*64))):
            observation=copy.deepcopy(self.observation);body=observation['recovery_authorization'];body[key]=value
            observation['recovery_authorization_sha256']=codec.digest(codec.canonical(body))
            with self.assertRaises(ValueError):self.build(observation=observation)
        observation=copy.deepcopy(self.observation);observation['source_proposal']['source_kinds']=['D01','TASK']
        observation['source_sha256']=codec.digest(codec.canonical(observation['source_proposal']))
        with self.assertRaises(ValueError):self.build(observation=observation)


if __name__=='__main__':unittest.main()
