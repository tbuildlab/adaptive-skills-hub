"""Public deterministic data only; no source-bound attempt/auth/model execution."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import tempfile
import time
import unittest
from unittest.mock import patch

from ash import g6_native_binding as guard, g6_private_completion as task, g6_retention_substitution as binding
from ash import g3_grant_codec as codec

spec = importlib.util.spec_from_file_location('g6_public_retention_transform', binding.ROOT / binding.WORKER)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


def fixture(rows):
    return b'PUBLIC FINITE TASK\nSource records: ' + json.dumps(rows, sort_keys=True).encode('ascii') + b'\n/no_think'


class RetentionSubstitutionTests(unittest.TestCase):
    def test_public_actual_transform_not_expected_answer_lookup(self):
        self.assertEqual(worker.transform(fixture(binding.PUBLIC_ROWS)), binding.PUBLIC_EXPECTED)
        rows = copy.deepcopy(binding.PUBLIC_ROWS)
        rows[0].update(attempt='different', retained_bytes=123)
        result = worker.transform(fixture(rows))
        self.assertIn(b'different,QUARANTINE,KEEP,123\n', result)
        self.assertNotEqual(result, binding.PUBLIC_EXPECTED)

    def test_malformed_missing_oversized_or_ambiguous_data_reject(self):
        for raw in (b'', b'x'*16385, b'Source records: {\n/no_think',
                    fixture(binding.PUBLIC_ROWS)+b'\nSource records: []', fixture([])):
            with self.subTest(length=len(raw)), self.assertRaises((ValueError, TypeError)):
                worker.transform(raw)

    def test_unsafe_unretired_duplicate_or_unbounded_record_reject(self):
        for change in ({'attempt':'x,y'}, {'attempt':'../x'}, {'status':'PASS'}, {'status':'DELETE'},
                       {'retired':False}, {'retained_bytes':True}, {'retained_bytes':-1},
                       {'retained_bytes':65537}, {'extra':'PUBLIC'}):
            rows = copy.deepcopy(binding.PUBLIC_ROWS)
            rows[0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                worker.transform(fixture(rows))
        rows=copy.deepcopy(binding.PUBLIC_ROWS)
        rows[1]['attempt']=rows[0]['attempt']
        with self.assertRaises(ValueError):
            worker.transform(fixture(rows))

    def test_exact_same_task_input_and_acceptance_as_qualified_model_configuration(self):
        plan=binding.native_plan()
        self.assertEqual(plan['input_sha256'], hashlib.sha256(task.prompt()).hexdigest())
        old=json.loads((binding.ROOT/'research/nexus-g6-local-retention-owner-decision-v2.json').read_bytes())
        self.assertEqual(plan['input_sha256'], old['config']['input_sha256'])
        self.assertEqual(plan['source_files'], old['config']['source_files'])
        self.assertEqual(plan['limits'], old['config']['limits'])
        self.assertIsNone(plan['model_ref'])
        self.assertNotIn('model_blob', plan)
        self.assertEqual(plan['candidate_arguments'][:3], ['-I','-S','-B'])
        self.assertIn('zero inference', plan['local_model_only_interpretation'])

    def test_only_closed_deterministic_command_and_snapshot_not_installed_fallback(self):
        plan=binding.native_plan()
        binary=Path(plan['cwd'])
        args,fs=guard._arguments(binary,binary.parent/'input',binary.parent/'result','qualification',0,0,role='deterministic')
        self.assertEqual(args[args.index('--')+1:], [plan['executable'],*plan['candidate_arguments']])
        self.assertEqual(fs,plan['filesystem'])
        self.assertNotIn(str(guard.PYTHON),args)
        self.assertNotIn('model.gguf.blob',' '.join(args))
        self.assertEqual(fs[':root'],'deny')
        self.assertNotIn((binary.parent/'input').as_posix(),fs)
        self.assertFalse(plan['network'])

    def test_new_subject_rejects_all_consumed_native_and_local_decisions_before_authentication(self):
        expected=binding.owner_intent()
        names=[f'research/nexus-g6-native-owner-decision-v{v}.json' for v in (1,2,3)]
        names += [f'research/nexus-g6-local-retention-owner-decision-v{v}.json' for v in (1,2)]
        for name in names:
            raw=(binding.ROOT/name).read_bytes()
            self.assertNotEqual(json.loads(raw)['subject_id'], expected['subject_id'])
            with patch.object(binding,'owner_intent',return_value=expected), patch.object(guard,'stable_read_bytes',return_value=raw):
                with self.assertRaisesRegex(guard.BindingHold,'OWNER_EXACT_SUBJECT'):
                    guard._verify_native_owner('deterministic')

    def test_wrong_artifact_configuration_subject_or_input_reject_before_authentication(self):
        expected=binding.owner_intent()
        for change in ('artifact','configuration','subject','input'):
            body=copy.deepcopy(expected)
            if change=='artifact':body['config']['worker_sha256']='0'*64
            if change=='configuration':body['config']['network']=True
            if change=='subject':body['subject_id']='wrong-subject'
            if change=='input':body['config']['input_sha256']='0'*64
            body.update(effective_at=int(time.time())-60,expires_at=int(time.time())+60,review_sha256='0'*64)
            raw=codec._canonical(body)+b'\n'
            with patch.object(binding,'owner_intent',return_value=expected),patch.object(guard,'stable_read_bytes',return_value=raw):
                with self.subTest(change=change),self.assertRaisesRegex(guard.BindingHold,'OWNER_EXACT_SUBJECT'):
                    guard._verify_native_owner('deterministic')

    def test_expired_or_future_signature_window_rejects_before_review_or_dispatch(self):
        expected=binding.owner_intent()
        now=int(time.time())
        for begin,end in ((now-120,now-1),(now+60,now+120)):
            body=dict(expected,effective_at=begin,expires_at=end,review_sha256='0'*64)
            with patch.object(binding,'owner_intent',return_value=expected), \
                 patch.object(guard,'stable_read_bytes',return_value=codec._canonical(body)+b'\n') as read:
                with self.assertRaisesRegex(guard.BindingHold,'OWNER_WINDOW'):
                    guard._verify_native_owner('deterministic')
                self.assertEqual(read.call_count,1)

    def test_artifact_readback_failure_quarantines_without_second_dispatch(self):
        raw=b'PUBLIC_OUTPUT'
        result={'status':'DETERMINISTIC_RETENTION_RESULT_OBSERVED','retired':True,
                'job_active_after_termination':0,'stdout_sha256':hashlib.sha256(raw).hexdigest()}
        with tempfile.TemporaryDirectory() as folder,patch.object(binding,'ROOT',Path(folder)), \
             patch.object(guard,'_fixed_attempt',return_value=result) as dispatch, \
             patch.object(binding,'stable_read_bytes',side_effect=[raw,b'WRONG_PUBLIC_READBACK']), \
             patch.object(task,'verified_report',return_value=b'PUBLIC_ARTIFACT'):
            directory=Path(folder)/binding.WORK/'result';directory.mkdir(parents=True)
            receipt=binding.attempt()
            self.assertEqual(receipt['status'],'QUARANTINE')
            self.assertTrue(receipt['retired'])
            self.assertFalse(receipt['automatic_retry'])
            self.assertEqual((directory/'retention-index.csv').read_bytes(),b'PUBLIC_ARTIFACT')
            dispatch.assert_called_once_with('deterministic','qualification')

    def test_runtime_pins_changed_reject_before_any_plan(self):
        original=(binding.ROOT/binding.PINS).read_bytes()
        with patch.object(binding,'stable_read_bytes',return_value=original+b' '):
            with self.assertRaisesRegex(guard.BindingHold,'DETERMINISTIC_PINS_CHANGED'):
                binding.runtime_pins()

    def test_copied_worker_bytes_are_the_same_buffer_checked_before_write(self):
        with tempfile.TemporaryDirectory() as folder:
            binary=Path(folder)/'bin';data=Path(folder)/'input';binary.mkdir();data.mkdir()
            with patch.object(binding,'stable_read_bytes',return_value=b'PUBLIC_SUBSTITUTED_WORKER'):
                with self.assertRaisesRegex(guard.BindingHold,'DETERMINISTIC_WORKER_CHANGED'):
                    binding.prepare(binary,data,public_case='deterministic_report')
            self.assertEqual(list(binary.iterdir()),[])

    def test_changed_loaded_adapter_denies(self):
        with patch.object(guard,'normalized_sha',return_value='0'*64):
            with self.assertRaisesRegex(guard.BindingHold,'LOADED_DETERMINISTIC_REVISION_CHANGED'):
                binding.source_gate()

    def test_exact_snapshot_regular_singlelink_runtime_inventory(self):
        pins=binding.verify_runtime_inventory()
        self.assertEqual(len(pins),54)
        self.assertIn('python312._pth',{p['relative_path'] for p in pins})
        self.assertEqual((binding.RUNTIME/'python312._pth').read_bytes(),b'.\nLib\nDLLs\n')

    def test_corrupted_runtime_bytes_cannot_match_bound_pin(self):
        from ash.ecosystem_storage import open_stable_input
        from ash.g6_local_model_intake import _hash_input, SuccessorHold
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'public-module.py'
            path.write_bytes(b'PUBLIC_CORRUPTED')
            with open_stable_input(path,maximum_bytes=64) as held:
                with self.assertRaises(SuccessorHold):
                    _hash_input(held,{'bytes':15,'sha256':hashlib.sha256(b'PUBLIC_ORIGINAL').hexdigest()},0)

    def test_extra_missing_or_unknown_runtime_file_denies(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime=Path(folder)
            (runtime/'public').write_bytes(b'PUBLIC')
            pins=[{'relative_path':'public','bytes':6,'sha256':hashlib.sha256(b'PUBLIC').hexdigest()}]
            with patch.object(binding,'RUNTIME',runtime),patch.object(binding,'runtime_pins',return_value=pins):
                self.assertEqual(binding.verify_runtime_inventory(),pins)
                (runtime/'extra').write_bytes(b'PUBLIC')
                with self.assertRaisesRegex(guard.BindingHold,'DETERMINISTIC_RUNTIME_INVENTORY'):
                    binding.verify_runtime_inventory()
                (runtime/'extra').unlink();(runtime/'public').unlink()
                with self.assertRaisesRegex(guard.BindingHold,'DETERMINISTIC_RUNTIME_INVENTORY'):
                    binding.verify_runtime_inventory()

    def test_public_preparation_uses_different_records_and_no_owner_or_model(self):
        with tempfile.TemporaryDirectory() as folder:
            binary=Path(folder)/'bin';data=Path(folder)/'input'
            binary.mkdir();data.mkdir()
            binding.prepare(binary,data,public_case='deterministic_report')
            raw=(data/'task.txt').read_bytes()
            self.assertNotEqual(hashlib.sha256(raw).hexdigest(),binding.native_plan()['input_sha256'])
            self.assertEqual(worker.transform(raw),binding.PUBLIC_EXPECTED)
            self.assertNotIn(task.expected_report(),raw)
            self.assertEqual({f.name for f in binary.iterdir()},{'retention.py','probe.py'})

    def test_public_cancel_reconciliation_uses_own_prefix_and_never_restores_authority(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(guard,'ROOT',Path(folder)):
            directory=Path(folder)/binding.PUBLIC_WORK/'deterministic_cancel'
            directory.mkdir(parents=True)
            original=b'PUBLIC_PARTIAL'
            (directory/'disposition.json').write_bytes(original)
            value=guard.reconcile_public('deterministic_cancel')
            self.assertEqual(value['status'],'QUARANTINE')
            self.assertFalse(value['automatic_retry'])
            self.assertTrue(value['retired'])
            self.assertEqual((directory/'disposition.json').read_bytes(),original)

    def test_public_evidence_cannot_create_one_shot_authority_or_dispatch(self):
        intent=binding.owner_intent()
        self.assertEqual(intent['max_attempts'],1)
        self.assertFalse(intent['automatic_retry'])
        self.assertFalse(intent['capability_registration'])
        self.assertEqual(intent['real_admission'],'NO')
        with patch.object(guard,'_verify_native_owner',side_effect=guard.BindingHold('PUBLIC_NOT_AUTHORITY')), \
             patch.object(guard,'_prepare_native') as prepare:
            with self.assertRaisesRegex(guard.BindingHold,'PUBLIC_NOT_AUTHORITY'):
                binding.attempt()
            prepare.assert_not_called()

    def test_existing_reservation_rejects_before_preparation_even_with_fresh_signature(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(guard,'ROOT',Path(folder)), \
             patch.object(guard,'_verify_native_owner',return_value=('0'*64,0,1,0)), \
             patch.object(guard,'_prepare_native') as prepare:
            (Path(folder)/binding.WORK).mkdir(parents=True)
            with self.assertRaisesRegex(guard.BindingHold,'ATTEMPT_RESERVED_NO_REPLAY'):
                binding.attempt()
            prepare.assert_not_called()

if __name__=='__main__':unittest.main()
