"""FIXTURE / NOT PROVIDER QUALIFICATION. No credential or provider call occurs."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from ash.core import _bytes
from ash.core_capabilities import ScopeError, sha
from ash.managed_execution import ExecutionError, read_execution, retry_execution
from ash.openai_hosted import (BACKEND, MODEL, SPEC, BUG, FIX, TESTS, OpenAIHostedExecutionBackend,
    OpenAIHTTPS, ProviderError, input_package, parse_response, prepare_openai, request_object, serialize_request)
from ash.openai_staging import stage_patch


class FixtureHTTP:
    evidence_source = "FIXTURE_NOT_PROVIDER_QUALIFICATION"

    def __init__(self):
        self.calls = []
        self.available = True
        self.response = None
        self.content = FIX
        self.extra = []
        self.error = None
        self.callback = None

    def credential_available(self):
        return self.available

    def call(self, method, path, payload=None, **kwargs):
        self.calls.append((method, path, payload))
        if self.callback:
            self.callback(method, path)
        if self.error:
            raise self.error
        if path.endswith('/content'):
            return self.content
        if path.startswith('/containers/'):
            value = {"has_more": False, "data": [{"id": "cfile_fixture", "container_id": "cntr_fixture",
                "path": self.output_path, "bytes": len(self.content)}] + self.extra}
        else:
            value = self.response
        return _bytes(value)


class OpenAIHostedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'; self.project.mkdir()
        (self.project/'calculator.py').write_bytes(BUG)
        (self.project/'test_calculator.py').write_bytes(TESTS)
        self.directory = self.root/'execution'
        self.spec = {"schema": SPEC, "category": "coding", "files": ["calculator.py", "test_calculator.py"],
            "effects": ["output_artifacts"], "artifacts": [{"path": "calculator.py", "verification": "owner_review", "expected_sha256": None}],
            "ttl_seconds": 3600, "verification": "python_add_fixture_v1",
            "provider": {"model": MODEL, "reasoning": "high", "max_polls": 2, "max_output_tokens": 2048,
                         "max_tool_calls": 6, "soft_spend_usd": 0.10}}
        self.http = FixtureHTTP()

    def prepare(self):
        state = prepare_openai('Fix only calculator.py. Preserve tests.', self.project, self.spec, self.directory)
        self.backend = OpenAIHostedExecutionBackend(self.directory, self.http)
        self.http.output_path = '/mnt/data/nexus-output/'+state['request']['task_id']+'/calculator.py'
        self.http.response = self.response(state)
        return state

    def response(self, state, status='completed'):
        return {"id": "resp_fixture", "model": MODEL, "status": status,
            "metadata": {"nexus_task_id": state['request']['task_id'], "nexus_request_digest": state['request_digest'], "nexus_backend": BACKEND},
            "usage": {"input_tokens": 123, "output_tokens": 234, "output_tokens_details": {"reasoning_tokens": 12}},
            "output": [
                {"type": "shell_call", "call_id": "call_fixture", "action": {"commands": ['python -m unittest']}},
                {"type": "shell_call_output", "call_id": "call_fixture", "output": [{"stdout": 'provider claims', "stderr": '', "outcome": {"type": "exit", "exit_code": 0}}]},
                {"type": "message", "content": [{"type": "output_text", "text": 'untrusted completion claim',
                    "annotations": [{"type": "container_file_citation", "container_id": "cntr_fixture", "file_id": "cfile_fixture", "filename": 'calculator.py'}]}]}]}

    def submit(self, state=None):
        state = state or self.prepare()
        return self.backend.submit(request_object(state), approval=state['request_digest'], allow_live=True)

    def test_request_exact_supported_schema_network_and_model(self):
        state = self.prepare(); body = serialize_request(state)
        self.assertEqual(body['model'], MODEL)
        self.assertEqual(body['reasoning'], {'effort': 'high'})
        self.assertEqual(body['tools'], [{'type':'shell','environment':{'type':'container_auto','memory_limit':'1g','network_policy':{'type':'disabled'}}}])
        self.assertTrue(body['background']); self.assertFalse(body['parallel_tool_calls'])
        self.assertEqual(body['max_tool_calls'],6)
        self.assertEqual(self.http.calls, [])

    def test_input_package_has_only_approved_bytes_and_no_local_paths(self):
        state=self.prepare(); package=input_package(state)
        self.assertEqual([f['path'] for f in package['files']],self.spec['files'])
        self.assertNotIn(str(self.project),json.dumps(serialize_request(state)))
        self.assertEqual(sha(_bytes(package)),state['request']['input_package_sha256'])
        self.assertIsNone(package['baseline'])

    def test_model_reasoning_and_budget_not_silent_substitutions(self):
        for key,val in [('model','other'),('reasoning','low'),('max_polls',True),('max_polls',21),('max_output_tokens',15),('max_tool_calls',17),('soft_spend_usd',float('nan')),('soft_spend_usd',0),('soft_spend_usd',True)]:
            with self.subTest(key=key,val=val),self.assertRaises(ExecutionError):
                spec=copy.deepcopy(self.spec);spec['provider'][key]=val
                prepare_openai('Fixture',self.project,spec,self.directory)
        self.assertFalse(self.directory.exists())

    def test_credential_absence_does_not_consume_dispatch_slot(self):
        state=self.prepare();self.http.available=False
        with self.assertRaisesRegex(ProviderError,'CREDENTIAL_REQUIRED'):self.submit(state)
        self.assertEqual(read_execution(self.directory)['provider']['dispatch_count'],0)
        self.assertEqual(self.http.calls,[])

    def test_explicit_live_authority_and_digest_required(self):
        state=self.prepare()
        for approve,live in [(state['request_digest'],False),('0'*64,True)]:
            with self.assertRaises(ExecutionError):self.backend.submit(request_object(state),approval=approve,allow_live=live)
        self.assertEqual(self.http.calls,[])

    def test_changed_request_object_refused(self):
        state=self.prepare(); bad=copy.deepcopy(state);bad['request']['task']='unapproved'
        with self.assertRaises(ExecutionError):self.backend.submit(request_object(bad),approval=state['request_digest'],allow_live=True)

    def test_git_baseline_and_input_drift_refused_before_dispatch(self):
        state=self.prepare()
        with patch('ash.openai_hosted._baseline',return_value='b'*40),self.assertRaises(ExecutionError):self.submit(state)
        (self.project/'calculator.py').write_bytes(FIX)
        with self.assertRaises(ExecutionError):self.submit(state)
        self.assertEqual(self.http.calls,[])

    def test_expired_and_changed_adapter_refused(self):
        state=self.prepare()
        with patch('ash.openai_hosted.time.time',return_value=state['request']['expires_at']),self.assertRaises(ExecutionError):self.submit(state)
        with patch('ash.openai_hosted._source_digest',return_value='0'*64),self.assertRaises(ExecutionError):self.submit(state)
        self.assertEqual(self.http.calls,[])

    def test_intent_persisted_before_effect(self):
        state=self.prepare()
        def inspect(method,path):
            actual=read_execution(self.directory)
            self.assertEqual(actual['status'],'DISPATCH_INTENT')
            self.assertEqual(actual['provider']['dispatch_count'],1)
            self.assertIsNotNone(actual['provider']['request_sha256'])
        self.http.callback=inspect;self.submit(state)

    def test_dispatch_id_persisted_before_malformed_binding_refusal(self):
        state=self.prepare();self.http.response['metadata']={}
        with self.assertRaisesRegex(ProviderError,'DISPATCH_OUTCOME_UNKNOWN'):self.submit(state)
        actual=read_execution(self.directory)
        self.assertEqual(actual['provider_reference'],'resp_fixture')
        self.assertEqual(actual['status'],'OUTCOME_UNKNOWN')
        self.http.response=self.response(state)
        self.backend.observe('resp_fixture')
        self.assertEqual(read_execution(self.directory)['status'],'PROVIDER_TERMINAL')

    def test_ambiguous_dispatch_no_blind_replay(self):
        state=self.prepare();self.http.error=TimeoutError('sensitive fixture detail')
        with self.assertRaisesRegex(ProviderError,'DISPATCH_OUTCOME_UNKNOWN'):self.submit(state)
        actual=read_execution(self.directory)
        self.assertEqual(actual['provider']['dispatch_count'],1);self.assertIsNone(actual['provider_reference'])
        with self.assertRaises(ExecutionError):self.submit(state)
        with self.assertRaises(ExecutionError):retry_execution(self.directory,state['request_digest'])
        self.assertEqual(len(self.http.calls),1)

    def test_http_429_and_500_preserve_unknown(self):
        for index,code in enumerate((429,500)):
            self.directory=self.root/f'execution-{index}';state=self.prepare()
            self.http.error=ProviderError('HTTP_RATE_LIMIT' if code==429 else 'HTTP_FAILURE')
            with self.assertRaises(ProviderError):self.submit(state)
            self.assertEqual(read_execution(self.directory)['status'],'OUTCOME_UNKNOWN')
            self.http.error=None

    def test_secret_exception_not_in_public_error_or_ledger(self):
        state=self.prepare();self.http.error=RuntimeError('private fixture detail')
        with self.assertRaises(ProviderError) as caught:self.submit(state)
        self.assertNotIn('private fixture detail',str(caught.exception))
        self.assertNotIn('private fixture detail',(self.directory/'execution.json').read_text())

    def test_real_transport_absence_without_network(self):
        with patch.dict(os.environ,{},clear=True),patch('urllib.request.build_opener') as opener:
            with self.assertRaisesRegex(ProviderError,'CREDENTIAL_REQUIRED'):OpenAIHTTPS().call('POST','/responses',{})
            opener.assert_not_called()

    def test_real_transport_rejects_arbitrary_origin_path(self):
        for path in ['https://evil.example','/responses/../../accounts','/containers/cntr_x/delete']:
            with self.assertRaises(ProviderError):OpenAIHTTPS().call('GET',path)

    def test_real_transport_redacts_headers_and_http_body(self):
        sentinel='fixture-authorization-value'
        captured=[]
        class Opener:
            def open(self,req,timeout):
                captured.append(req)
                raise urllib.error.HTTPError(req.full_url,429,'private error',{},None)
        with patch.dict(os.environ,{'OPENAI_API_KEY':sentinel}),patch('urllib.request.build_opener',return_value=Opener()):
            with self.assertRaisesRegex(ProviderError,'HTTP_RATE_LIMIT') as caught:OpenAIHTTPS().call('POST','/responses',{})
        self.assertNotIn(sentinel,str(caught.exception));self.assertIsNone(captured[0].get_header('Authorization'))

    def test_provider_success_is_not_nexus_completion(self):
        self.submit();state=read_execution(self.directory)
        self.assertEqual(state['status'],'PROVIDER_TERMINAL')
        self.assertEqual(state['verification'],'NOT_STARTED')
        self.assertFalse((self.directory/'artifacts-1').exists())

    def test_parser_usage_shell_and_citation_evidence(self):
        state=self.prepare();view=parse_response(_bytes(self.http.response),state)
        self.assertEqual(view['usage'],{'input_tokens':123,'output_tokens':234})
        self.assertTrue(view['shell_evidence_complete'])
        self.assertNotIn('stdout',json.dumps(view))
        self.assertEqual(view['files'][0]['container_id'],'cntr_fixture')

    def test_missing_usage_remains_unknown(self):
        state=self.prepare();self.http.response['usage']=None
        self.assertIsNone(parse_response(_bytes(self.http.response),state)['usage'])

    def test_malformed_json_duplicate_keys_and_nonfinite(self):
        state=self.prepare()
        for raw in (b'{',b'{"id":1,"id":2}',b'{"usage":NaN}',b'[]'):
            with self.assertRaises(ProviderError):parse_response(raw,state)

    def test_binding_reference_model_status_usage_refused(self):
        state=self.prepare()
        for key,value in [('id','../../x'),('model','other'),('status','mystery'),('metadata',{}),('usage',{'input_tokens':True,'output_tokens':1})]:
            body=copy.deepcopy(self.http.response);body[key]=value
            with self.subTest(key=key),self.assertRaises(ProviderError):parse_response(_bytes(body),state)

    def test_unknown_tool_is_not_expanded_authority(self):
        state=self.prepare();self.http.response['output'].append({'type':'computer_call'})
        with self.assertRaises(ProviderError):parse_response(_bytes(self.http.response),state)

    def test_missing_shell_pairs_block_import(self):
        state=self.prepare();self.http.response['output'].pop(1);self.submit(state)
        with self.assertRaises(ExecutionError):self.backend.import_result()

    def test_shell_failure_is_observed_without_running_provider_commands(self):
        state=self.prepare();self.http.response['output'][1]['output'][0]['outcome']['exit_code']=1
        view=parse_response(_bytes(self.http.response),state)
        self.assertEqual(view['shell_calls'][0]['outcomes'][0]['exit_code'],1)

    def test_poll_bound_persists_across_resume(self):
        state=self.prepare();self.http.response=self.response(state,'in_progress');self.submit(state)
        other=OpenAIHostedExecutionBackend(self.directory,self.http)
        other.observe('resp_fixture');other.observe('resp_fixture')
        with self.assertRaisesRegex(ExecutionError,'poll budget'):other.observe('resp_fixture')
        self.assertEqual(read_execution(self.directory)['provider']['poll_count'],2)
        self.assertEqual(sum(c[0]=='POST' for c in self.http.calls),1)

    def test_transient_retrieval_error_keeps_reference_and_count(self):
        self.submit();self.http.error=ProviderError('HTTP_RATE_LIMIT')
        with self.assertRaises(ProviderError):self.backend.observe('resp_fixture')
        state=read_execution(self.directory)
        self.assertEqual(state['provider_reference'],'resp_fixture');self.assertEqual(state['provider']['poll_count'],1)
        self.http.error=None;self.backend.observe('resp_fixture')

    def test_retrieve_different_response_and_unknown_reference_refused(self):
        self.submit()
        with self.assertRaises(ExecutionError):self.backend.observe('resp_other')
        self.http.response['id']='resp_other'
        with self.assertRaises(ProviderError):self.backend.observe('resp_fixture')
        self.assertEqual(read_execution(self.directory)['provider_reference'],'resp_fixture')

    def test_cancel_api_acceptance_is_not_remote_cessation(self):
        state=self.prepare();self.http.response=self.response(state,'in_progress');self.submit(state)
        self.backend.cancel('resp_fixture');actual=read_execution(self.directory)
        self.assertEqual(actual['status'],'CANCEL_API_ACCEPTED')
        self.assertEqual(actual['provider']['cost_reconciliation'],'UNKNOWN')
        self.assertIsNone(actual['provider']['terminal_state'])
        with self.assertRaises(ExecutionError):self.backend.import_result()

    def test_cancellation_terminal_does_not_accept_late_success(self):
        self.submit();self.backend.cancel('resp_fixture');final=self.backend.import_result()
        self.assertEqual(final['status'],'RESULT_RECONCILED')
        self.assertIn('TAIL_UNKNOWN',final['verification'])
        self.assertFalse((self.directory/'artifacts-1').exists())

    def test_cancel_unknown_preserves_intent_and_no_replay(self):
        self.submit();self.http.error=TimeoutError()
        with self.assertRaises(ProviderError):self.backend.cancel('resp_fixture')
        state=read_execution(self.directory);self.assertTrue(state['cancel_requested'])
        self.assertEqual(state['provider']['cancel_phase'],'CANCEL_REQUESTED')
        with self.assertRaises(ExecutionError):self.backend.cancel('resp_fixture')

    def test_failed_incomplete_cancelled_not_complete_or_retry(self):
        for index,status in enumerate(('failed','incomplete','cancelled')):
            self.directory=self.root/f'failure-{index}';state=self.prepare();self.http.response=self.response(state,status)
            self.submit(state);final=self.backend.import_result()
            self.assertNotEqual(final['status'],'TASK_VERIFIED_COMPLETE');self.assertFalse(final['retry_eligible'])
            if status in {'failed','incomplete'}:
                self.assertEqual(final['receipt']['failure'],{'kind':'provider_failure','no_effects_confirmed':False})
                self.assertTrue(final['receipt']['ambiguity'])
                self.assertEqual(final['provider']['receipt_sha256'],sha(_bytes(final['receipt'])))

    def test_complete_fixture_e2e_independent_local_tests_and_no_project_apply(self):
        self.submit();final=self.backend.import_result()
        self.assertEqual(final['status'],'TASK_VERIFIED_COMPLETE')
        self.assertEqual(final['verification'],'INDEPENDENT_FIXED_AST_AND_LOCAL_TESTS_PASSED')
        self.assertEqual((self.project/'calculator.py').read_bytes(),BUG)
        self.assertEqual((self.directory/'local-verification/calculator.py').read_bytes(),FIX)
        self.assertEqual(final['provider']['provenance'],'FIXTURE_NOT_PROVIDER_QUALIFICATION')
        self.assertEqual(final['provider']['receipt_sha256'],sha(_bytes(final['receipt'])))
        self.assertEqual(final['provider']['cost_reconciliation'],'UNKNOWN')

    def test_provider_code_cannot_execute_arbitrary_local_effect(self):
        self.prepare();self.http.content=b'import os\nos.system("echo forbidden")\n';self.submit(read_execution(self.directory))
        with patch('ash.openai_staging.subprocess.run') as run:
            final=self.backend.import_result();run.assert_not_called()
        self.assertEqual(final['status'],'VERIFICATION_FAILED')

    def test_source_encoding_cookie_cannot_change_reviewed_ast(self):
        self.prepare()
        self.http.content=b'# coding: unicode_escape\n'+FIX+b'# hidden\\nraise RuntimeError("forbidden")\n'
        self.submit(read_execution(self.directory))
        with patch('ash.openai_staging.subprocess.run') as run:
            final=self.backend.import_result();run.assert_not_called()
        self.assertEqual(final['status'],'VERIFICATION_FAILED')

    def test_arbitrary_replacement_remains_owner_review(self):
        self.spec['verification']='artifact_contract';self.prepare();self.submit(read_execution(self.directory))
        final=self.backend.import_result();self.assertEqual(final['status'],'VERIFICATION_REQUIRED')

    def test_local_verifier_test_drift_fails(self):
        self.submit();(self.project/'test_calculator.py').write_bytes(b'changed tests')
        final=self.backend.import_result();self.assertEqual(final['status'],'VERIFICATION_FAILED')

    def test_extra_missing_traversing_binary_secret_and_duplicate_artifacts_refused(self):
        for index,kind in enumerate(('extra','missing','traversing','binary','secret','duplicate')):
            self.directory=self.root/f'bad-{index}';self.http=FixtureHTTP();self.prepare();self.submit(read_execution(self.directory))
            if kind=='extra':self.http.extra=[{'container_id':'cntr_fixture','path':self.http.output_path+'extra','id':'cfile_other','bytes':1}]
            if kind=='missing':self.http.output_path+='.other'
            if kind=='traversing':self.http.output_path=self.http.output_path.replace('/calculator.py','/../calculator.py')
            if kind=='binary':self.http.content=b'\x00data'
            if kind=='secret':self.http.content=b'sk-'+b'x'*30
            if kind=='duplicate':self.http.extra=[{'container_id':'cntr_fixture','path':self.http.output_path.upper().replace('/MNT/DATA/NEXUS-OUTPUT/','/mnt/data/nexus-output/').replace(read_execution(self.directory)['request']['task_id'].upper(),read_execution(self.directory)['request']['task_id']),'id':'cfile_other','bytes':1}]
            with self.subTest(kind=kind),self.assertRaises((ExecutionError,ScopeError)):self.backend.import_result()

    def test_cross_container_or_uncited_artifact_refused(self):
        self.submit();self.http.extra=[{'container_id':'cntr_other','path':'/mnt/data/x','id':'cfile_other','bytes':1}]
        with self.assertRaises(ExecutionError):self.backend.import_result()

    def test_interrupted_import_cannot_redownload_or_dispatch(self):
        self.submit();self.http.error=TimeoutError()
        with self.assertRaises(ProviderError):self.backend.import_result()
        self.http.error=None
        with self.assertRaises(ExecutionError):self.backend.import_result()
        with self.assertRaises(ExecutionError):self.submit(read_execution(self.directory))

    def test_local_verifier_minimal_environment_and_fixed_argv(self):
        self.submit();real=subprocess.run;captured=[]
        def inspect(*args,**kwargs):
            captured.append(kwargs);return real(*args,**kwargs)
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fixture-not-a-real-key'}),patch('ash.openai_staging.subprocess.run',side_effect=inspect):
            self.backend.import_result()
        self.assertNotIn('OPENAI_API_KEY',captured[0]['env']);self.assertTrue(captured[0]['close_fds'])

    def test_secret_like_input_refused_offline(self):
        self.spec['verification']='artifact_contract';(self.project/'calculator.py').write_bytes(b'sk-'+b'x'*30)
        with self.assertRaises(ExecutionError):self.prepare()
        self.assertEqual(self.http.calls,[])

    def test_prepare_fixture_cli_never_dispatches(self):
        repo=Path(__file__).resolve().parents[1]
        result=subprocess.run([sys.executable,'-B',str(repo/'scripts/openai_live_fixture.py'),str(self.root/'prepared')],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['DISPATCH'],0)
        self.assertIn('PREPARATION_ONLY',result.stdout)


class PatchStagingTests(unittest.TestCase):
    def test_fixed_patch_to_replacement(self):
        patch=b'--- a/calculator.py\n+++ b/calculator.py\n@@ -1,2 +1,2 @@\n def add(a, b):\n-    return a - b\n+    return a + b\n'
        self.assertEqual(stage_patch({'calculator.py':BUG},patch,['calculator.py']),{'calculator.py':FIX})

    def test_patch_invalid_scope_baseline_addition_deletion_binary_and_counts(self):
        original=b'--- a/calculator.py\n+++ b/calculator.py\n@@ -1,2 +1,2 @@\n def add(a, b):\n-    return a - b\n+    return a + b\n'
        cases=[original.replace(b'calculator.py',b'../x'),original.replace(b'calculator.py',b'unapproved.py'),original.replace(b'--- a/calculator.py',b'--- /dev/null'),original.replace(b'+++ b/calculator.py',b'+++ /dev/null'),b'GIT binary patch\n',original.replace(b'-1,2',b'-1,9'),original.replace(b'return a - b',b'return 123'),original+b'diff --git x\n']
        for raw in cases:
            with self.subTest(raw=raw),self.assertRaises((ExecutionError,ScopeError)):
                stage_patch({'calculator.py':BUG},raw,['calculator.py'])


if __name__=='__main__':
    unittest.main()
