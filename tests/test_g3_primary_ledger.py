"""Primary transport simulations and SDK shapes, never real DynamoDB proof."""
import copy
from types import SimpleNamespace
import unittest
from ash import g3_primary_ledger as m, g3_transition_protocol as p
from tests.test_g3_transition_protocol import vector


ARN='arn:aws:dynamodb:ap-southeast-1:175880707430:table/NexusG3AuthorityV1'


class MemoryClient:
    """Test-only atomic storage semantics; not imported by production code."""
    def __init__(self):
        self.meta=SimpleNamespace(config=SimpleNamespace(retries={'total_max_attempts':1}))
        self.items={};self.calls=[];self.drop_ack=False;self.drop_blob_ack=False;self.reject_write=False
    def get_item(self,**kw):
        self.calls.append(('get',kw));assert kw['ConsistentRead'] is True
        item=self.items.get(kw['Key']['sk']['S'])
        return {} if item is None else {'Item':copy.deepcopy(item)}
    def put_item(self,**kw):
        self.calls.append(('put',kw));key=kw['Item']['sk']['S']
        if key in self.items:raise ValueError('conflict')
        self.items[key]=copy.deepcopy(kw['Item'])
        if self.drop_blob_ack:raise TimeoutError('test only dropped blob ack')
        return {}
    def transact_write_items(self,**kw):
        self.calls.append(('transact',kw));before=copy.deepcopy(self.items)
        if self.reject_write:raise ValueError('test only condition failure')
        try:
            for operation in kw['TransactItems']:
                if 'Put' in operation:
                    item=operation['Put']['Item'];key=item['sk']['S']
                    if key in self.items:raise ValueError('conflict')
                    self.items[key]=copy.deepcopy(item)
                else:
                    op=operation['Update'];key=op['Key']['sk']['S'];item=self.items[key]
                    args=op['ExpressionAttributeValues']
                    if key=='HEAD':
                        if item['checkpoint']!=args[':old']:raise ValueError('stale')
                        if ':next' not in args:raise ValueError('missing')
                        if ':ready' in args and args[':ready']=={'S':'READY'} and ':sequence' in args:
                            if item['phase']=={'S':'READY'}:
                                item['phase']={'S':'PREPARED'};item['pending']=args[':next']
                            elif item['phase']=={'S':'PREPARED'} and item['pending']==args[':next']:
                                item['phase']={'S':'READY'};item['checkpoint']=args[':next']
                                item['sequence']=args[':sequence'];item.pop('pending')
                            else:raise ValueError('phase')
                        else:raise ValueError('phase')
                    else:
                        if item['phase']!={'S':'PREPARED'} or item['checkpoint']!=args[':next']:raise ValueError('reservation')
                        item['phase']={'S':'FINALIZED'}
            if self.drop_ack:raise TimeoutError('test only dropped ack')
        except TimeoutError:raise
        except Exception:self.items=before;raise
        return {}


class PrimaryLedgerTests(unittest.TestCase):
    def setUp(self):
        before,after,head,*_=vector()
        self.head=head;self.before=before;self.client=MemoryClient()
        self.instance=p.r.parse_json(head)['authority_instance']
        self.ledger=m.DynamoReservations(self.client,table_arn=ARN,instance=self.instance,max_attempts=500)
        self.candidate=p.prepare_transition(before,after,head,group='T5',transition='INVALIDATE',record_refs=[])
    def enroll(self):self.ledger.enroll_genesis(self.head,self.before.snapshot)
    def ready(self):
        self.enroll();self.ledger.observe_current(independent_checkpoint=self.head)
    def test_enrollment_does_not_reopen_or_create_authority(self):
        result=self.ledger.enroll_genesis(self.head,self.before.snapshot)
        self.assertEqual(result.authority,'NONE');self.assertTrue(self.ledger.quarantined)
    def test_prepare_requires_current_independent_observation(self):
        self.enroll()
        with self.assertRaises(m.LedgerError):self.ledger.prepare(self.candidate)
    def test_exact_prepare_finalize_and_separate_recheck(self):
        self.ready();result=self.ledger.prepare(self.candidate)
        self.assertEqual(result.authority,'NONE');self.assertTrue(self.ledger.quarantined)
        final=self.ledger.finalize(self.candidate,independent_checkpoint=self.candidate.checkpoint)
        self.assertEqual(final.authority,'NONE');self.assertTrue(self.ledger.quarantined)
        self.ledger.observe_current(independent_checkpoint=self.candidate.checkpoint)
        self.assertFalse(self.ledger.quarantined)
    def test_unknown_prepare_is_one_transaction_and_quarantines(self):
        self.ready();self.client.drop_ack=True
        with self.assertRaises(m.LedgerError):self.ledger.prepare(self.candidate)
        self.assertTrue(self.ledger.quarantined)
        self.assertEqual(len([op for op,_ in self.client.calls if op=='transact']),1)
        with self.assertRaises(m.LedgerError):self.ledger.observe_current(independent_checkpoint=self.head)
    def test_unknown_finalize_preserves_consumption(self):
        self.ready();self.ledger.prepare(self.candidate);self.client.drop_ack=True
        with self.assertRaises(m.LedgerError):self.ledger.finalize(self.candidate,independent_checkpoint=self.candidate.checkpoint)
        self.assertEqual(self.client.items['HEAD']['checkpoint'],{'B':self.candidate.checkpoint})
        self.assertEqual(self.client.items['reservation#00000000000000000001']['phase'],{'S':'FINALIZED'})
        self.assertTrue(self.ledger.quarantined)
    def test_prepared_primary_cannot_be_reopened_by_old_head(self):
        self.ready();self.ledger.prepare(self.candidate)
        with self.assertRaises(m.LedgerError):self.ledger.observe_current(independent_checkpoint=self.head)
    def test_wrong_fence_candidate_is_rejected_without_write(self):
        self.ready();self.ledger.prepare(self.candidate);count=len(self.client.calls)
        with self.assertRaises(m.LedgerError):self.ledger.finalize(self.candidate,independent_checkpoint=self.head)
        self.assertEqual(len(self.client.calls),count)
    def test_second_instance_cannot_replace_existing_head(self):
        self.enroll();count=len([op for op,_ in self.client.calls if op=='put'])
        with self.assertRaises(m.LedgerError):self.enroll()
        self.assertEqual(len([op for op,_ in self.client.calls if op=='put']),count)
    def test_corrupt_immutable_blob_quarantines(self):
        self.ready();key='blob#'+p.c.digest(self.head);self.client.items[key]['body']={'B':b'{}'}
        with self.assertRaises(m.LedgerError):self.ledger.observe_current(independent_checkpoint=self.head)
        self.assertTrue(self.ledger.quarantined)
    def test_restart_does_not_restore_open_state(self):
        self.ready()
        fresh=m.DynamoReservations(self.client,table_arn=ARN,instance=self.instance,max_attempts=500)
        self.assertTrue(fresh.quarantined)
    def test_exhausted_attempt_budget_closes(self):
        self.ledger.max_attempts=1
        with self.assertRaises(m.LedgerError):self.enroll()
        self.assertEqual(self.ledger.attempts,1);self.assertTrue(self.ledger.quarantined)
    def test_sdk_retry_and_wrong_table_rejected(self):
        self.client.meta.config.retries['total_max_attempts']=2
        with self.assertRaises(m.LedgerError):m.DynamoReservations(self.client,table_arn=ARN,instance=self.instance,max_attempts=500)
        self.client.meta.config.retries['total_max_attempts']=1
        with self.assertRaises(m.LedgerError):m.DynamoReservations(self.client,table_arn=ARN.replace('175880707430','862902859484'),instance=self.instance,max_attempts=500)
    def test_actual_sdk_shapes_accept_the_fixed_requests_without_network(self):
        from botocore.session import get_session
        from botocore.validate import ParamValidator
        self.ready();self.ledger.prepare(self.candidate)
        self.ledger.finalize(self.candidate,independent_checkpoint=self.candidate.checkpoint)
        service=get_session().get_service_model('dynamodb')
        names={'get':'GetItem','put':'PutItem','transact':'TransactWriteItems'}
        for operation,request in self.client.calls:
            shape=service.operation_model(names[operation]).input_shape
            result=ParamValidator().validate(request,shape)
            self.assertFalse(result.has_errors(),result.generate_report())
    def test_unknown_blob_write_is_not_retried_or_resubmitted(self):
        self.ready();self.client.drop_blob_ack=True
        with self.assertRaises(m.LedgerError):self.ledger.prepare(self.candidate)
        self.assertTrue(self.ledger.quarantined)
        self.assertEqual(len([op for op,_ in self.client.calls if op=='transact']),0)
    def test_service_condition_failure_cannot_acknowledge_preparation(self):
        self.ready();self.client.reject_write=True
        with self.assertRaises(m.LedgerError):self.ledger.prepare(self.candidate)
        self.assertEqual(self.client.items['HEAD']['phase'],{'S':'READY'})
        self.assertTrue(self.ledger.quarantined)


if __name__=='__main__':unittest.main()
