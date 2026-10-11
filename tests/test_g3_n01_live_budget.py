"""Cost/request wrapper contract; mocked transport is not AWS qualification."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from scripts import g3_n01_storage_live as m


class SDK:
    meta=SimpleNamespace(config=SimpleNamespace(retries={'total_max_attempts':1}))
    def __init__(self):self.calls=[]
    def get_item(self,**kw):
        self.calls.append(kw)
        return dict(ResponseMetadata={'HTTPStatusCode':200,'RequestId':'test-request'})


class LiveBudgetTests(unittest.TestCase):
    def setUp(self):
        self.sdk=SDK();self.wrapper=m.BoundedService(self.sdk,'DDB',2)
        self.request=dict(TableName=m.TABLE,Key={'pk':{'S':'authority#test'},'sk':{'S':'HEAD'}},ConsistentRead=True)
    def test_attempt_bound_includes_injected_ack_loss_and_no_retry(self):
        with patch.object(m,'emit'):
            self.wrapper.drop_operation='get_item'
            with self.assertRaises(ValueError):self.wrapper.get_item(**self.request)
            self.wrapper.get_item(**self.request)
            with self.assertRaises(ValueError):self.wrapper.get_item(**self.request)
        self.assertEqual(len(self.sdk.calls),2);self.assertEqual(self.wrapper.attempts,2)
    def test_wrong_resource_and_oversized_transaction_never_call_sdk(self):
        with self.assertRaises(ValueError):self.wrapper.get_item(**dict(self.request,TableName='other'))
        with self.assertRaises(ValueError):self.wrapper.transact_write_items(TransactItems=[{}, {}, {}])
        self.assertEqual(self.wrapper.attempts,0);self.assertEqual(self.sdk.calls,[])
    def test_oversized_item_denies_before_consuming_service_attempt(self):
        with self.assertRaises(ValueError):
            self.wrapper.put_item(TableName=m.TABLE,Item={'body':{'B':b'x'*(400*1024)}})
        self.assertEqual(self.wrapper.attempts,0)
        self.assertEqual(self.sdk.calls,[])
    def test_fixed_error_does_not_copy_backend_private_message(self):
        def fail(**kw):raise RuntimeError('private backend credentials must not appear')
        self.sdk.get_item=fail
        with patch.object(m,'emit') as emitted:
            with self.assertRaisesRegex(ValueError,'^N01_STORAGE_QUARANTINE$'):
                self.wrapper.get_item(**self.request)
        self.assertEqual(emitted.call_args.args[0]['error_code'],'UNAVAILABLE')
        self.assertNotIn('private',str(emitted.call_args))


if __name__=='__main__':unittest.main()
