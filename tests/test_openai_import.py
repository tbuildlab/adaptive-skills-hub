"""FIXTURE / NOT PROVIDER QUALIFICATION; original live data never used by tests."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_openai_hosted as fixture
from ash.core import _bytes
from ash.core_capabilities import sha
from ash.managed_execution import read_execution, _save, ExecutionError
from ash.openai_hosted import FIX, OpenAIHTTPS, ProviderError
from ash.openai_import import ImportRefusal
from ash.openai_reconciliation import reconcile_original


class ImportDiagnosticsTests(unittest.TestCase):
    setUp = fixture.OpenAIHostedTests.setUp
    prepare = fixture.OpenAIHostedTests.prepare
    response = fixture.OpenAIHostedTests.response
    submit = fixture.OpenAIHostedTests.submit

    def refusal(self):
        files = sorted(self.directory.glob('import-refusal-*.json'))
        self.assertTrue(files)
        return json.loads(files[-1].read_text())

    def test_inventory_contract_refusal_is_durable_before_content_read(self):
        self.submit(); self.http.output_path = '/mnt/data/calculator.py'
        with self.assertRaises(ImportRefusal) as error: self.backend.import_result()
        self.assertEqual(error.exception.code, 'IMPORT_ARTIFACT_CONTRACT')
        record = self.refusal()
        self.assertEqual(record['stage'], 'artifact_contract')
        self.assertEqual(record['expected']['paths'], ['calculator.py'])
        self.assertEqual(record['observed']['paths'], [])
        self.assertEqual(record['observed']['files'][0]['path'], '/mnt/data/calculator.py')
        self.assertEqual(read_execution(self.directory)['provider']['artifact_reads'], 0)
        inventory = json.loads((self.directory/'provider-inventory.json').read_text())
        self.assertEqual(inventory['metadata']['count'], 1)
        self.assertEqual(inventory['response_id'], 'resp_fixture')

    def test_cross_container_refusal_has_expected_and_observed(self):
        self.submit(); self.http.extra = [{'id':'cfile_other','container_id':'cntr_other','path':'/mnt/data/x','bytes':1}]
        with self.assertRaises(ImportRefusal): self.backend.import_result()
        r = self.refusal()
        self.assertEqual(r['code'], 'IMPORT_INVENTORY_BINDING')
        self.assertEqual(r['expected']['container_id'], 'cntr_fixture')
        self.assertEqual(r['observed']['container_id'], 'cntr_other')

    def test_paginated_malformed_and_nonobject_inventory_refused_and_recorded(self):
        self.submit(); real = self.http.call
        with patch.object(self.http, 'call', side_effect=lambda *a,**k:_bytes({'data':[42],'has_more':False})):
            with self.assertRaises(ImportRefusal): self.backend.import_result()
        self.assertEqual(self.refusal()['code'], 'IMPORT_INVENTORY_ENTRY')
        self.assertFalse(any(c[1].endswith('/content') for c in self.http.calls))

    def test_path_traversal_is_observed_not_normalized_to_basename(self):
        self.submit(); self.http.output_path = self.http.output_path.replace('/calculator.py','/../calculator.py')
        with self.assertRaises(ImportRefusal): self.backend.import_result()
        self.assertEqual(self.refusal()['code'], 'IMPORT_PATH_OR_INPUT_BOUNDARY')
        self.assertEqual(self.refusal()['stage'], 'path_confinement')

    def test_size_mismatch_records_counts_without_artifact_text(self):
        self.submit(); real = self.http.call
        def mismatch(method,path,*a,**kw):
            return FIX+b' ' if path.endswith('/content') else real(method,path,*a,**kw)
        with patch.object(self.http,'call',side_effect=mismatch),self.assertRaises(ImportRefusal): self.backend.import_result()
        r=self.refusal(); self.assertEqual(r['code'],'IMPORT_ARTIFACT_SIZE')
        self.assertEqual(r['expected']['bytes'],len(FIX)); self.assertEqual(r['observed']['bytes'],len(FIX)+1)
        self.assertNotIn('return a + b',json.dumps(r))

    def test_transport_detail_is_never_saved(self):
        self.submit(); self.http.error=RuntimeError('private exception should not be saved')
        with self.assertRaises(ExecutionError):self.backend.import_result()
        self.assertEqual(self.refusal()['code'],'IMPORT_PROVIDER_READ_FAILED')
        self.assertNotIn('private exception',json.dumps(self.refusal()))

    def test_provider_failure_status_is_recorded_without_http_body(self):
        self.submit();self.http.error=ProviderError('HTTP_FAILURE',http_status=404)
        with self.assertRaises(ExecutionError):self.backend.import_result()
        self.assertEqual(self.refusal()['observed']['http_status'],404)
        self.assertEqual(self.refusal()['observed']['provider_failure_code'],'HTTP_FAILURE')

    def test_diagnostic_metadata_redaction_and_field_allowlist(self):
        self.submit(); self.http.extra=[{'container_id':'cntr_other','path':'Bearer fake-sensitive-value','Authorization':'private header','bytes':1}]
        with self.assertRaises(ImportRefusal):self.backend.import_result()
        combined=(self.directory/'provider-inventory.json').read_text()+json.dumps(self.refusal())
        self.assertNotIn('private header',combined); self.assertNotIn('fake-sensitive-value',combined)
        self.assertIn('REDACTED_METADATA',combined)

    def test_earlier_refusal_and_inventory_are_not_overwritten(self):
        self.submit(); self.http.output_path+='wrong'
        with self.assertRaises(ImportRefusal):self.backend.import_result()
        before=(self.directory/'import-refusal-0001.json').read_bytes()
        inventory=(self.directory/'provider-inventory.json').read_bytes()
        with self.assertRaises(ImportRefusal):self.backend.import_result()
        self.assertEqual(before,(self.directory/'import-refusal-0001.json').read_bytes())
        self.assertEqual(inventory,(self.directory/'provider-inventory.json').read_bytes())
        self.assertEqual(self.refusal()['code'],'IMPORT_INVENTORY_ALREADY_READ')

    def test_staging_refusal_has_subject_and_stage(self):
        self.submit();(self.directory/'provider-download').mkdir()
        with self.assertRaises(ImportRefusal):self.backend.import_result()
        self.assertEqual(self.refusal()['code'],'IMPORT_STAGING_EXISTS')
        self.assertEqual(self.refusal()['subject'],'provider-download')

    def test_local_verifier_failure_returns_failed_state_with_durable_reason(self):
        self.submit();self.http.content=b'print("not reviewed")\n'
        state=self.backend.import_result()
        self.assertEqual(state['status'],'VERIFICATION_FAILED')
        self.assertEqual(self.refusal()['code'],'IMPORT_LOCAL_VERIFIER_FAILED')
        self.assertEqual(self.refusal()['stage'],'local_verifier')


class OriginalReconciliationTests(unittest.TestCase):
    setUp = fixture.OpenAIHostedTests.setUp
    prepare = fixture.OpenAIHostedTests.prepare
    response = fixture.OpenAIHostedTests.response
    submit = fixture.OpenAIHostedTests.submit
    def original(self):
        self.spec['provider']['max_polls']=10
        self.submit();self.backend.observe('resp_fixture');self.backend.observe('resp_fixture')
        state=read_execution(self.directory);state['provider']['list_reads']=1
        _save(self.directory,state)
        self.snapshot=(self.directory/'execution.json').read_bytes()
        self.calls_before=len(self.http.calls)
        return state

    def test_original_result_imports_in_new_layer_no_dispatch_original_unchanged(self):
        self.original();state=reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        layer=self.directory.parent/'original-result-reconciliation-v1'
        self.assertEqual(state['status'],'TASK_VERIFIED_COMPLETE')
        self.assertEqual(state['provider']['dispatch_count'],1)
        self.assertEqual(state['provider']['poll_count'],2)
        self.assertEqual(state['provider']['list_reads'],2)
        self.assertEqual(state['provider']['artifact_reads'],1)
        self.assertEqual(state['reconciliation']['additional_get_count'],2)
        self.assertEqual(state['reconciliation']['original_execution_sha256'],sha(self.snapshot))
        self.assertEqual((self.directory/'execution.json').read_bytes(),self.snapshot)
        self.assertTrue((layer/'reconciliation-receipt.json').exists())
        self.assertEqual([c[0] for c in self.http.calls[self.calls_before:]],['GET','GET'])
        self.assertEqual((self.project/'calculator.py').read_bytes(),fixture.BUG)

    def test_missing_credential_does_not_create_layer_or_read(self):
        self.original();self.http.available=False
        with self.assertRaisesRegex(ExecutionError,'CREDENTIAL_REQUIRED'):
            reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        self.assertEqual(len(self.http.calls),self.calls_before)
        self.assertFalse((self.directory.parent/'original-result-reconciliation-v1').exists())

    def test_existing_layer_cannot_be_replaced_or_reread(self):
        self.original();reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        count=len(self.http.calls)
        with self.assertRaises(FileExistsError):reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        self.assertEqual(len(self.http.calls),count)

    def test_changed_original_input_and_exhausted_budget_refuse_before_read(self):
        self.original();state=read_execution(self.directory);state['provider']['poll_count']=8;_save(self.directory,state)
        with self.assertRaisesRegex(ExecutionError,'allowance'):
            reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        self.assertEqual(len(self.http.calls),self.calls_before)

    def test_foreign_cited_content_cannot_be_downloaded(self):
        self.original();self.http.extra=[{'id':'cfile_other','container_id':'cntr_fixture','path':self.http.output_path+'extra','bytes':1}]
        with self.assertRaises(ExecutionError):reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        self.assertEqual([c[0] for c in self.http.calls[self.calls_before:]],['GET'])
        layer=self.directory.parent/'original-result-reconciliation-v1'
        self.assertEqual(json.loads((layer/'import-refusal-0001.json').read_text())['code'],'IMPORT_ARTIFACT_CONTRACT')
        self.assertEqual((self.directory/'execution.json').read_bytes(),self.snapshot)

    def test_original_drift_before_get_fails_and_is_recorded(self):
        self.original()
        from ash.openai_reconciliation import read_bytes as real
        calls=0
        def changed(root,name):
            nonlocal calls
            data=real(root,name)
            if Path(root).resolve()==self.directory.resolve() and name=='execution.json':
                calls+=1
                if calls>1:return data+b' '
            return data
        with patch('ash.openai_reconciliation.read_bytes',side_effect=changed),self.assertRaises(ExecutionError):
            reconcile_original(self.directory,allow_provider_access=True,transport=self.http)
        self.assertEqual(len(self.http.calls),self.calls_before)


if __name__=='__main__':unittest.main()
