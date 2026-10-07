"""Deterministic contract tests only; not provider qualification."""
import copy
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from ash.core import _bytes
from ash.core_capabilities import sha
from ash.managed_execution import ExecutionError, read_execution, retry_execution
from ash.openai_hosted import (BACKEND, BUG, FIX, MODEL, SPEC, TESTS,
    OpenAIHostedExecutionBackend, ProviderError, prepare_openai, request_object, serialize_request)
from ash.openai_structured import SCHEMA, validate_result

DIFF = '--- a/calculator.py\n+++ b/calculator.py\n@@ -1,2 +1,2 @@\n def add(a, b):\n-    return a - b\n+    return a + b\n'
RESULT = {'status': 'fixed', 'changed_files': ['calculator.py'], 'patch': DIFF, 'provider_test_status': 'passed'}


class HTTP:
    evidence_source = 'FIXTURE_NOT_PROVIDER_QUALIFICATION'
    def __init__(self):
        self.calls = []; self.response = None; self.available = True; self.error = None
    def credential_available(self): return self.available
    def call(self, method, path, payload=None, **kwargs):
        self.calls.append((method, path))
        if self.error: raise self.error
        return _bytes(self.response)


class StructuredTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.project = self.root/'project'; self.project.mkdir()
        (self.project/'calculator.py').write_bytes(BUG); (self.project/'test_calculator.py').write_bytes(TESTS)
        self.directory = self.root/'execution'
        spec = {'schema': SPEC, 'category': 'coding', 'files': ['calculator.py','test_calculator.py'],
            'effects': ['output_artifacts'], 'artifacts': [{'path':'calculator.py','verification':'owner_review','expected_sha256':None}],
            'ttl_seconds':3600, 'verification':'python_add_structured_v3', 'provider': {
                'model':MODEL,'reasoning':'high','max_polls':3,'max_output_tokens':3072,'max_tool_calls':6,'soft_spend_usd':.1}}
        self.state = prepare_openai('Fix calculator.py only; preserve tests.',self.project,spec,self.directory)
        self.http = HTTP(); self.backend = OpenAIHostedExecutionBackend(self.directory,self.http)
        self.http.response = {'id':'resp_fixture','model':MODEL,'status':'completed',
            'metadata': {'nexus_task_id':self.state['request']['task_id'],'nexus_request_digest':self.state['request_digest'],'nexus_backend':BACKEND},
            'usage': {'input_tokens':123,'output_tokens':234,'input_tokens_details':{'cached_tokens':0,'cache_write_tokens':0},
                      'output_tokens_details':{'reasoning_tokens':12},'total_tokens':357},'service_tier':'default',
            'output': [
                {'type':'shell_call','call_id':'call_before','action':{'commands':['untrusted provider command']}},
                {'type':'shell_call_output','call_id':'call_before','output':[{'outcome':{'type':'exit','exit_code':1}}]},
                {'type':'shell_call','call_id':'call_after','action':{'commands':['another provider command']}},
                {'type':'shell_call_output','call_id':'call_after','output':[{'outcome':{'type':'exit','exit_code':0}}]},
                {'type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':json.dumps(RESULT),'annotations':[]}]}]}
    def submit(self):
        return self.backend.submit(request_object(self.state),approval=self.state['request_digest'],allow_live=True)
    def output(self, value): self.http.response['output'][-1]['content'][0]['text'] = json.dumps(value)
    def refused(self, value, code):
        self.output(value); self.submit()
        with self.assertRaisesRegex(ProviderError,code): self.backend.import_result()
        state=read_execution(self.directory)
        self.assertEqual(state['provider']['last_status'],'completed')
        self.assertEqual(state['provider']['dispatch_count'],1)
        self.assertEqual(self.http.calls,[('POST','/responses')])
        self.assertEqual(state['structured_import']['failure_code'],code)
        self.assertEqual((self.project/'calculator.py').read_bytes(),BUG)
    def test_valid_strict_result(self): self.assertEqual(validate_result(_bytes(RESULT)),RESULT)
    def test_network_disabled_and_exact_minimum_input(self):
        body=serialize_request(self.state)
        self.assertEqual(body['tools'][0]['environment']['network_policy'],{'type':'disabled'})
        self.assertEqual(body['text']['format'],{'type':'json_schema','name':'nexus_coding_result_v3','strict':True,'schema':SCHEMA})
        content=json.loads(body['input'][0]['content'][0]['text'])
        self.assertEqual(set(content),{'task','files'})
        self.assertEqual([f['path'] for f in content['files']],['calculator.py','test_calculator.py'])
        self.assertNotIn(str(self.project),json.dumps(body)); self.assertNotIn('request',content)
    def test_local_verifier_pass_and_scope_hashes(self):
        self.submit(); state=self.backend.import_result()
        self.assertEqual(state['status'],'TASK_VERIFIED_COMPLETE')
        self.assertEqual(state['verification'],'INDEPENDENT_FIXED_AST_AND_LOCAL_TESTS_PASSED')
        self.assertEqual((self.directory/'patch-staging/calculator.py').read_bytes(),FIX)
        self.assertEqual((self.directory/'patch-staging/test_calculator.py').read_bytes(),TESTS)
        self.assertEqual(self.http.calls,[('POST','/responses')])
        self.assertTrue((self.directory/'nexus-completion-receipt.json').exists())
        self.assertEqual(json.loads((self.directory/'nexus-completion-receipt.json').read_bytes())['classification'],
                         'FIXTURE_CONTRACT_VERIFIED_NOT_PROVIDER_QUALIFICATION')
        self.backend.import_result(); self.assertEqual(len(self.http.calls),1)
    def test_missing_field(self):
        v=copy.deepcopy(RESULT); del v['status']; self.refused(v,'PROVIDER_RESPONSE_SCHEMA_INVALID')
    def test_extra_field(self): self.refused(dict(RESULT,command='run'),'PROVIDER_RESPONSE_SCHEMA_INVALID')
    def test_oversized_patch(self): self.refused(dict(RESULT,patch='x'*4097),'PROVIDER_RESPONSE_SCHEMA_INVALID')
    def test_empty_success(self): self.refused(dict(RESULT,patch=''),'PROVIDER_RESPONSE_SCHEMA_INVALID')
    def test_unexpected_changed_file(self): self.refused(dict(RESULT,changed_files=['evil.py']),'PROVIDER_RESPONSE_SCHEMA_INVALID')
    def test_malformed_json_completed_not_accepted(self):
        self.http.response['output'][-1]['content'][0]['text']='{invalid'
        self.submit()
        with self.assertRaisesRegex(ProviderError,'SCHEMA_INVALID'): self.backend.import_result()
        self.assertEqual(read_execution(self.directory)['provider']['last_status'],'completed')
    def test_duplicate_key(self):
        with self.assertRaisesRegex(ProviderError,'SCHEMA_INVALID'): validate_result(b'{"status":"fixed","status":"fixed"}')
    def test_provider_failed(self):
        self.http.response['status']='failed'; self.submit()
        with self.assertRaisesRegex(ProviderError,'PROVIDER_EXECUTION_FAILED'): self.backend.import_result()
    def test_provider_unable(self): self.refused({'status':'unable_to_fix','changed_files':[],'patch':'','provider_test_status':'failed'},'PROVIDER_EXECUTION_FAILED')
    def test_wrong_role(self):
        self.http.response['output'][-1]['role']='user'; self.submit()
        with self.assertRaisesRegex(ProviderError,'SCHEMA_INVALID'): self.backend.import_result()
    def test_provider_reports_pass_but_wrong_ast(self):
        self.refused(dict(RESULT,patch=DIFF.replace('return a + b','return a * b')),'LOCAL_VERIFIER_FAILED')
    def test_provider_reports_pass_but_local_tests_fail(self):
        self.submit()
        with patch('ash.openai_staging.subprocess.run') as run:
            run.return_value.returncode=1;run.return_value.stdout=b'';run.return_value.stderr=b'fixed failure'
            with self.assertRaisesRegex(ProviderError,'LOCAL_VERIFIER_FAILED'): self.backend.import_result()
        self.assertNotEqual(read_execution(self.directory)['status'],'TASK_VERIFIED_COMPLETE')
    def test_no_shell_execution_evidence(self):
        self.http.response['output']=self.http.response['output'][-1:];self.submit()
        with self.assertRaisesRegex(ProviderError,'SHELL_EVIDENCE'):self.backend.import_result()
    def test_one_dispatch_and_restart_replay_refused(self):
        self.submit();self.backend=OpenAIHostedExecutionBackend(self.directory,self.http)
        with self.assertRaisesRegex(ExecutionError,'replay'):self.submit()
        self.assertEqual(self.http.calls,[('POST','/responses')])
    def test_ambiguous_dispatch_never_retried(self):
        self.http.error=ProviderError('TRANSPORT_OUTCOME_UNKNOWN')
        with self.assertRaisesRegex(ProviderError,'DISPATCH_OUTCOME_UNKNOWN'):self.submit()
        with self.assertRaises(ExecutionError):self.submit()
        with self.assertRaises(ExecutionError):retry_execution(self.directory,self.state['request_digest'])
        self.assertEqual(len(self.http.calls),1)
        self.assertEqual(read_execution(self.directory)['provider']['dispatch_failure']['code'],'TRANSPORT_OUTCOME_UNKNOWN')
    def test_original_response_get_only_after_restart(self):
        self.http.response['status']='in_progress';self.submit()
        self.http.response['status']='completed';self.backend=OpenAIHostedExecutionBackend(self.directory,self.http)
        self.backend.observe('resp_fixture');self.backend.import_result()
        self.assertEqual(self.http.calls,[('POST','/responses'),('GET','/responses/resp_fixture')])
    def test_changed_response_binding(self):
        self.submit();self.http.response['id']='resp_other'
        with self.assertRaisesRegex(ProviderError,'RETRIEVAL_UNKNOWN'):self.backend.observe('resp_fixture')
        self.assertEqual(read_execution(self.directory)['provider_reference'],'resp_fixture')
        self.assertEqual(read_execution(self.directory)['provider']['retrieval_failure']['code'],'RESPONSE_ID_CHANGED')
    def test_secret_redaction_no_candidate_persisted(self):
        secret='sk-'+'X'*30
        self.output(dict(RESULT,patch=secret));self.submit()
        self.assertNotIn(secret,(self.directory/'execution.json').read_text())
        with self.assertRaisesRegex(ProviderError,'SCHEMA_INVALID'):self.backend.import_result()
        self.assertNotIn(secret,(self.directory/'structured-refusal.json').read_text())
    def test_credential_absence_slot_not_consumed(self):
        self.http.available=False
        with self.assertRaisesRegex(ProviderError,'CREDENTIAL_REQUIRED'):self.submit()
        self.assertEqual(read_execution(self.directory)['provider']['dispatch_count'],0);self.assertEqual(self.http.calls,[])
    def test_expired_request(self):
        with patch('ash.openai_hosted.time.time',return_value=self.state['request']['expires_at']+1):
            with self.assertRaisesRegex(ExecutionError,'expired'):self.submit()
        self.assertEqual(self.http.calls,[])
    def test_preserve_detailed_usage(self):
        self.submit();v=read_execution(self.directory)['provider']['observation']
        self.assertEqual(v['usage_details']['reasoning_tokens'],12);self.assertEqual(v['usage_details']['total_tokens'],357)
    def test_staging_collision(self):
        self.submit();(self.directory/'patch-staging').mkdir()
        with self.assertRaisesRegex(ProviderError,'STAGING_APPLY_FAILED'):self.backend.import_result()
    def wrapped(self):
        before=self.http.response['output'][1]['output'][0]
        after=self.http.response['output'][3]['output'][0]
        before.update(outcome={'type':'exit','exit_code':0},stdout='Test hash '+sha(TESTS)+'\nPRE_REPAIR_TEST_EXIT=1\n',stderr='FAIL: test_add (test_calculator.AddTests.test_add)\nRan 1 test\nFAILED (failures=1)\n')
        after.update(stdout='POST_REPAIR_TEST_EXIT=0\nTest hash unchanged: '+sha(TESTS)+'\n',stderr='Ran 1 test in 0.002s\n\nOK\n')
        return before,after
    def test_expected_failure_wrapped_in_successful_shell(self):
        self.wrapped();self.submit();self.assertEqual(self.backend.import_result()['status'],'TASK_VERIFIED_COMPLETE')
    def test_wrapped_success_without_test_evidence_refused(self):
        for i in (1,3):self.http.response['output'][i]['output'][0]['outcome']['exit_code']=0
        self.submit()
        with self.assertRaisesRegex(ProviderError,'SHELL_EVIDENCE_INVALID'):self.backend.import_result()
    def test_wrong_wrapped_initial_exit_refused(self):
        b,a=self.wrapped();b['stdout']=b['stdout'].replace('EXIT=1','EXIT=0');self.submit()
        with self.assertRaisesRegex(ProviderError,'SHELL_EVIDENCE_INVALID'):self.backend.import_result()
    def test_wrapped_modified_tests_hash_refused(self):
        b,a=self.wrapped();a['stdout']=a['stdout'].replace(sha(TESTS),'0'*64);self.submit()
        with self.assertRaisesRegex(ProviderError,'SHELL_EVIDENCE_INVALID'):self.backend.import_result()
    def test_wrapped_duplicate_exit_marker_refused(self):
        b,a=self.wrapped();b['stdout']+='PRE_REPAIR_TEST_EXIT=1\n';self.submit()
        with self.assertRaisesRegex(ProviderError,'SHELL_EVIDENCE_INVALID'):self.backend.import_result()
    def test_wrapped_provider_claim_still_requires_local_pass(self):
        self.wrapped();self.submit()
        with patch('ash.openai_staging.subprocess.run') as run:
            run.return_value.returncode=1;run.return_value.stdout=b'';run.return_value.stderr=b'failure'
            with self.assertRaisesRegex(ProviderError,'LOCAL_VERIFIER_FAILED'):self.backend.import_result()
    def test_bounded_wrapped_evidence(self):
        b,a=self.wrapped();b['stdout']='x'*8193
        with self.assertRaisesRegex(ProviderError,'DISPATCH_OUTCOME_UNKNOWN'):self.submit()
        self.assertEqual(read_execution(self.directory)['provider_reference'],'resp_fixture')


def patch_case(value):
    def test(self): self.refused(dict(RESULT,patch=value),'STRUCTURED_PATCH_REJECTED')
    return test

for name, value in {
    'test_modification':DIFF.replace('calculator.py','test_calculator.py'),
    'path_traversal':DIFF.replace('calculator.py','../calculator.py'),
    'absolute_path':DIFF.replace('calculator.py','/calculator.py'),
    'windows_path':DIFF.replace('calculator.py','C:/calculator.py'),
    'deletion':DIFF.replace('+++ b/calculator.py','+++ /dev/null'),
    'rename':DIFF.replace('+++ b/calculator.py','+++ b/other.py'),
    'binary_diff':'GIT binary patch\nliteral 32\n',
    'malformed_diff':DIFF.replace('@@ -1,2 +1,2 @@','@@ broken @@'),
    'baseline_mismatch':DIFF.replace('-    return a - b','-    return wrong'),
    'unexpected_file':DIFF.replace('calculator.py','evil.py'),
}.items(): setattr(StructuredTests,'test_patch_'+name,patch_case(value))

if __name__=='__main__':unittest.main()
