"""Native SDK shapes/bounds simulated only; no actual credentials or AWS calls."""
from types import SimpleNamespace
import pickle
import unittest
from unittest.mock import patch

from ash import g3_n01_native_transport as native
from ash import g3_n01_public_review as review


class SDK:
    def __init__(self,service,trace,wrong=False,account='175880707430'):
        self.service=service;self.trace=trace;self.wrong=wrong
        self.account=account
        self.meta=SimpleNamespace(config=SimpleNamespace(retries={'total_max_attempts':1}))
        self.closed=False;self.unknown=False
    def close(self):self.closed=True
    def invoke(self,name,kw):
        self.trace.append((self.service,name,kw))
        if self.unknown:raise TimeoutError('SYNTHETIC_SECRET_DO_NOT_EMIT')
        if name in ('assume_role_with_web_identity','assume_role'):
            return {'Credentials':{'AccessKeyId':'SYNTHETIC','SecretAccessKey':'SYNTHETIC','SessionToken':'SYNTHETIC'}}
        if name=='get_caller_identity':
            return ({'Account':'different','Arn':'different'} if self.wrong else
                {'Account':'175880707430','Arn':'arn:aws:sts::175880707430:assumed-role/NexusG3QualificationCaller/NexusG3N01Vercel'} if self.account=='175880707430' else
                {'Account':'862902859484','Arn':'arn:aws:sts::862902859484:assumed-role/NexusG3N01AppendRead/NexusG3N01Custody'})
        return {'ResponseMetadata':{'HTTPStatusCode':200}}
    def __getattr__(self,name):return lambda **kw:self.invoke(name,kw)


class NativeTransportTests(unittest.TestCase):
    def setUp(self):
        self.trace=[];self.clients=[]
        self.clock=patch('time.time',return_value=(review.FROM_MS+1000)/1000)
        self.clock.start();self.addCleanup(self.clock.stop)
        self.budget=patch.object(native,'_BUDGET',dict(leases=0,ddb=0,s3=0,s3_writes=0,ddb_bytes=0,s3_bytes=0))
        self.budget.start();self.addCleanup(self.budget.stop)
        self.factory=patch('boto3.client',side_effect=self.client)
        self.factory.start();self.addCleanup(self.factory.stop)
    def client(self,service,**kw):
        cfg=kw['config'];self.assertEqual(cfg.retries['total_max_attempts'],1)
        ordinal=len([client for client in self.clients if client.service=='sts'])%3
        item=SDK(service,self.trace,account='862902859484' if service=='sts' and ordinal==2 else '175880707430')
        self.clients.append(item);return item
    def begin(self):return native.NativeTransport('SYNTHETIC_NATIVE_HEADER')
    def read_args(self):return dict(Bucket=native.boot.storage_scope().bucket,ExpectedBucketOwner='862902859484',
                                   Prefix=native.custody.NORMAL+'journal/',MaxKeys=128)
    def write_args(self):return dict(Bucket=native.boot.storage_scope().bucket,ExpectedBucketOwner='862902859484',
        Key=native.custody.NORMAL+'objects/'+'a'*64,Body=b'{}',IfNoneMatch='*',ContentType='application/json',ChecksumAlgorithm='SHA256')
    def enable(self,driver):
        with patch.object(native.source,'read_protected_source',return_value=SimpleNamespace(authority='NONE')) as reader:
            result=driver.enable_owner_storage(None,native_environment={},artifact_inventory_sha256='a'*64,process_nonce='b'*64)
        self.assertEqual(reader.call_count,1);self.assertEqual(result.authority,'NONE')
    def test_exact_native_chain_and_scoped_reads_remain_none(self):
        driver=self.begin();self.assertEqual(driver.sts_attempts,4)
        self.assertEqual(self.trace[0][2]['RoleArn'],native.boot.A)
        self.assertEqual(self.trace[2][2]['RoleArn'],native.boot.R)
        driver.custody.list_object_versions(**self.read_args())
        self.assertEqual(driver.s3_attempts,1);self.assertEqual(driver.authority,'NONE')
        with self.assertRaises(TypeError):pickle.dumps(driver)
        driver.close();self.assertTrue(all(client.closed for client in self.clients))
    def test_wrong_native_identity_never_constructs_data_plane_clients(self):
        def wrong(service,**kw):
            item=SDK(service,self.trace,wrong=True);self.clients.append(item);return item
        with patch('boto3.client',side_effect=wrong),self.assertRaisesRegex(ValueError,'^N01_NATIVE_TRANSPORT_QUARANTINE$'):
            self.begin()
        self.assertFalse(any(client.service in ('s3','dynamodb') for client in self.clients))
        self.assertTrue(all(client.closed for client in self.clients))
    def test_no_write_before_actual_source_reader_and_missing_source_retires(self):
        driver=self.begin();before=len(self.trace)
        with self.assertRaises(ValueError):driver.custody.put_object(**self.write_args())
        self.assertEqual(before,len(self.trace));self.assertTrue(driver.retired)
        driver=self.begin()
        with patch.object(native.source,'read_protected_source',side_effect=ValueError('missing')),self.assertRaises(ValueError):
            driver.enable_owner_storage(None,native_environment={},artifact_inventory_sha256='a'*64,process_nonce='b'*64)
        self.assertTrue(driver.retired)
    def test_source_enabled_write_still_cannot_expand_bucket_prefix_or_retention(self):
        for changes in ({'Bucket':'different'},{'Key':native.source.PREFIX+'registration.json'},
                        {'ObjectLockMode':'COMPLIANCE'},{'IfNoneMatch':'other'}):
            driver=self.begin();self.enable(driver);before=len(self.trace)
            with self.assertRaises(ValueError):driver.custody.put_object(**dict(self.write_args(),**changes))
            self.assertEqual(before,len(self.trace))
    def test_unknown_sdk_outcome_retires_all_without_retry_or_error_exposure(self):
        driver=self.begin();self.clients[-1].unknown=True
        with self.assertRaisesRegex(ValueError,'^N01_NATIVE_TRANSPORT_QUARANTINE$'):
            driver.custody.list_object_versions(**self.read_args())
        count=len(self.trace)
        with self.assertRaises(ValueError):driver.custody.list_object_versions(**self.read_args())
        self.assertEqual(count,len(self.trace));self.assertEqual(driver.s3_attempts,1)
    def test_shared_budget_survives_new_lease_and_exhaustion_denies_before_sdk(self):
        driver=self.begin();driver.custody.list_object_versions(**self.read_args())
        # A new lease's identity positions are simulated by resetting only the
        # test trace. The shared process service budget is deliberately retained.
        self.trace.clear();fresh=self.begin();self.assertEqual(fresh.s3_attempts,1)
        native._BUDGET['s3']=native.MAX_S3;before=len(self.trace)
        with self.assertRaises(ValueError):fresh.custody.list_object_versions(**self.read_args())
        self.assertEqual(before,len(self.trace))
    def test_wrong_table_partition_transaction_size_and_unsupported_operation_deny(self):
        driver=self.begin();self.enable(driver);before=len(self.trace)
        with self.assertRaises(ValueError):driver.primary.get_item(TableName=native.TABLE,ConsistentRead=True,Key={'pk':{'S':'other'}})
        self.assertEqual(before,len(self.trace))
        driver=self.begin();self.enable(driver);before=len(self.trace)
        item=dict(TableName=native.TABLE,Item={'pk':{'S':'authority#'+native.custody.INSTANCE},'body':{'B':b'x'*400000}},ConditionExpression='attribute_not_exists(pk)')
        with self.assertRaises(ValueError):driver.primary.put_item(**item)
        self.assertEqual(before,len(self.trace))
        self.assertFalse(hasattr(driver.primary,'delete_table'))
    def test_fixed_review_expiry_and_aggregate_retained_bytes_deny(self):
        with patch('time.time',return_value=review.UNTIL_MS/1000),self.assertRaises(ValueError):self.begin()
        self.assertEqual(self.trace,[])
        driver=self.begin();self.enable(driver);native._BUDGET['s3_bytes']=native.MAX_WRITE_BYTES
        before=len(self.trace)
        with self.assertRaises(ValueError):driver.custody.put_object(**self.write_args())
        self.assertEqual(before,len(self.trace))
        native._BUDGET['s3_bytes']=0
        driver=self.begin();self.enable(driver);native._BUDGET['s3_writes']=native.MAX_S3_WRITES
        before=len(self.trace)
        with self.assertRaises(ValueError):driver.custody.put_object(**self.write_args())
        self.assertEqual(before,len(self.trace))


if __name__=='__main__':unittest.main()
