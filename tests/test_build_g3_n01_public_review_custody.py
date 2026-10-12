"""Generated native operation contract; SDK simulations are never R evidence."""
import builtins
from contextlib import redirect_stdout
from datetime import datetime,timezone,timedelta
from io import StringIO
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import boto3
from scripts import build_g3_n01_public_review_custody as builder
from ash import g3_n01_public_review as review
from tests import test_g3_d03_s3_fence as fake


class PublicReviewOperationTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'operation.py';builder.build(self.path)
        self.code=self.path.read_text();self.client=fake.MemoryS3();self.native_calls=[]
    def execute(self,account='862902859484'):
        class Clock(datetime):
            @classmethod
            def now(cls,tz=None):return datetime(2026,10,12,0,0,0,tzinfo=timezone.utc)
        real_import=builtins.__import__
        def imported(name,*args,**kwargs):
            if name=='datetime':return SimpleNamespace(datetime=Clock,timezone=timezone,timedelta=timedelta)
            return real_import(name,*args,**kwargs)
        def client(service,**kwargs):
            self.native_calls.append(service)
            if service=='sts':return SimpleNamespace(get_caller_identity=lambda:dict(Account=account,Arn='arn:aws:iam::'+account+':root'))
            self.assertEqual(service,'s3');return self.client
        old=Path.cwd()
        try:
            import os
            os.chdir(self.folder.name)
            stream=StringIO()
            with patch('boto3.client',side_effect=client),patch('builtins.__import__',side_effect=imported),redirect_stdout(stream):
                try:exec(compile(self.code,str(self.path),'exec'),{})
                except SystemExit as error:self.assertEqual(error.code,2)
            return stream.getvalue()
        finally:os.chdir(old)
    def test_exact_operation_retains_only_two_public_documents_with_seven_day_bound(self):
        output=self.execute();self.assertIn('PUBLIC_REVIEW_INDEPENDENTLY_RETAINED',output)
        calls=[kwargs for operation,kwargs in self.client.calls if operation=='put']
        self.assertEqual(len(calls),2)
        self.assertEqual({call['Key'] for call in calls},{review.PREFIX+'proposal.json',review.PREFIX+'acceptance.json'})
        for call in calls:
            self.assertEqual(call['IfNoneMatch'],'*');self.assertEqual(call['ObjectLockMode'],'COMPLIANCE')
            self.assertEqual(call['ObjectLockRetainUntilDate'],datetime(2026,10,19,0,0,0,tzinfo=timezone.utc))
        self.assertIn('"authority": "NONE"',output);self.assertNotIn('Authorization',output)
    def test_wrong_account_denies_before_any_custody_operation(self):
        self.assertIn('QUARANTINE',self.execute(account='175880707430'))
        self.assertEqual(self.native_calls,['sts']);self.assertEqual(self.client.calls,[])
    def test_unknown_ack_never_retries_and_preserves_attempt_receipt(self):
        self.client.mode='unknown-after';self.assertIn('QUARANTINE',self.execute())
        receipt=Path(self.folder.name)/'n01-public-review-r-receipt.json';before=receipt.read_bytes()
        self.assertIn('ALREADY_ATTEMPTED_NO_REDISPATCH',self.execute())
        self.assertEqual(before,receipt.read_bytes())
        self.assertEqual(len([call for call in self.client.calls if call[0]=='put']),1)
    def test_unexpected_existing_key_denies_without_write(self):
        self.client.add(review.PREFIX+'unexpected.json',b'{}')
        self.assertIn('QUARANTINE',self.execute())
        self.assertFalse(any(call[0]=='put' for call in self.client.calls))
    def test_existing_exact_versions_are_read_without_rewriting(self):
        from ash import g3_delegated_control_codec as codec
        for name,target in (('nexus-production-n01-pending-public-pin-review-v1.json','proposal.json'),
                            ('nexus-production-n01-public-pin-owner-acceptance-v1.json','acceptance.json')):
            raw=codec.canonical(codec.decode((builder.ROOT/'research'/name).read_bytes().rstrip()))
            self.client.add(review.PREFIX+target,raw)
        self.assertIn('PUBLIC_REVIEW_INDEPENDENTLY_RETAINED',self.execute())
        self.assertFalse(any(call[0]=='put' for call in self.client.calls))


if __name__=='__main__':unittest.main()
