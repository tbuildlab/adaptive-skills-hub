"""Fixed PUBLIC data/protocol negatives; no candidate execution or private input."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch

from ash import g6_native_binding as binding, g6_private_completion as private


class LocalRetentionTests(unittest.TestCase):
    def test_current_source_join_is_a_real_three_record_report(self):
        self.assertEqual(private.expected_report(),
                         b'attempt,outcome,action,bytes\nv1,QUARANTINE,KEEP,312\n'
                         b'v2,QUARANTINE,KEEP,2540\nv3,PUBLIC_ONLY_PASS,KEEP,2196\n')
        self.assertTrue(all(row['retired'] for row in private.rows()))

    def test_wrong_changed_or_missing_source_denies(self):
        for raw in (b'{}', b'PUBLIC_CHANGED', b'{"status":"PASS"}'):
            with patch.object(private, 'stable_read_bytes', return_value=raw):
                with self.assertRaisesRegex(binding.BindingHold, 'RETENTION_SOURCE_IDENTITY'):
                    private.rows()
        with patch.object(private, 'stable_read_bytes', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                private.rows()

    def test_source_unknown_retirement_authority_and_type_do_not_default_to_pass(self):
        good = {'status': 'QUARANTINE', 'retired': True, 'automatic_retry': False,
                'real_admission': 'NO', 'retained_bytes': 12}
        for changes in ({'status': 'UNKNOWN'}, {'retired': False}, {'automatic_retry': True},
                        {'real_admission': 'YES'}, {'retained_bytes': True},
                        {'retained_bytes': -1}, {'retained_bytes': 65537}):
            raw = json.dumps({**good, **changes}).encode()
            source = (('v1', 'PUBLIC_SOURCE', hashlib.sha256(raw).hexdigest()),)
            with patch.object(private, 'SOURCES', source), \
                 patch.object(private, 'stable_read_bytes', return_value=raw):
                with self.assertRaises(binding.BindingHold):
                    private.rows()

    def test_prompt_contains_only_selected_public_fields_and_fixed_template(self):
        content = private.prompt()
        self.assertTrue(content.startswith(b'<|im_start|>user\n'))
        self.assertTrue(content.endswith(b'<|im_start|>assistant\n<think>\n\n</think>\n\n\n'))
        data = json.loads(content.split(b'Source records: ', 1)[1].split(b'\n/no_think', 1)[0])
        self.assertEqual(data, private.rows())
        self.assertTrue(all(set(row) == {'attempt', 'status', 'retired', 'retained_bytes'} for row in data))
        self.assertNotIn(b'launcher_pid', content)
        self.assertNotIn(b'filesystem', content)
        self.assertNotIn(private.expected_report(), content)

    def test_exact_csv_protocol_rejects_noise_wrong_rows_actions_and_missing_data(self):
        good = private.expected_report() + private.END
        self.assertEqual(private.verified_report(good + b'\r\n'), private.expected_report())
        for raw in (b'EXTRA\n' + good, good + b'EXTRA', good.replace(b'KEEP', b'DELETE'),
                    good.replace(b'2196', b'2197'), good.replace(b'PUBLIC_ONLY_PASS', b'PASS'),
                    good.replace(b'v2,QUARANTINE,KEEP,2540\n', b''),
                    private.END, good + good, b'```csv\n' + good + b'\n```'):
            self.assertIsNone(private.verified_report(raw))

    def test_native_plan_preserves_loader_model_limits_and_exact_file_scope(self):
        before = binding.native_plan()
        plan = binding.native_plan('private')
        for key in ('members', 'model', 'runtime_sha256', 'host_material', 'environment_names',
                    'telemetry_overrides', 'limits', 'network', 'max_attempts', 'automatic_retry'):
            self.assertEqual(plan[key], before[key])
        self.assertEqual(plan['candidate_arguments'][:-1], before['candidate_arguments'][:-1])
        self.assertEqual(plan['candidate_arguments'][-1], private.END.decode())
        binary = Path(plan['cwd'])
        self.assertEqual((binary / plan['candidate_arguments'][3]).resolve(), Path(plan['input']).resolve())
        self.assertEqual(plan['filesystem'][Path(plan['input']).as_posix()], 'read')
        self.assertNotIn(Path(plan['input']).parent.as_posix(), plan['filesystem'])
        self.assertNotIn(str(binding.PYTHON.parent), plan['filesystem'])
        self.assertEqual(plan['input_sha256'], hashlib.sha256(private.prompt()).hexdigest())

    def test_native_command_uses_private_closed_plan_not_old_prompt_or_python(self):
        plan = private.native_plan()
        binary = Path(plan['cwd'])
        args, fs = binding._arguments(binary, binary.parent / 'input', binary.parent / 'result',
                                      'qualification', 0, 0, role='private')
        self.assertEqual(args[args.index('--') + 1:], [plan['executable'], *plan['candidate_arguments']])
        self.assertEqual(fs, plan['filesystem'])
        self.assertNotIn(str(binding.PYTHON), args)
        with self.assertRaises(binding.BindingHold):
            binding.native_plan('arbitrary')

    def test_new_subject_and_purpose_cannot_reuse_any_old_decision(self):
        intent = private.owner_intent()
        for version in (1, 2, 3):
            raw = (binding.ROOT / f'research/nexus-g6-native-owner-decision-v{version}.json').read_bytes()
            self.assertNotEqual(json.loads(raw)['subject_id'], intent['subject_id'])
            with patch.object(private, 'owner_intent', return_value=intent), \
                 patch.object(binding, 'stable_read_bytes', return_value=raw):
                with self.assertRaisesRegex(binding.BindingHold, 'OWNER_EXACT_SUBJECT'):
                    binding._verify_native_owner('private')

    def test_consumed_local_retention_decision_rejects_new_snapshot_subject(self):
        intent = private.owner_intent()
        raw = (binding.ROOT / 'research/nexus-g6-local-retention-owner-decision-v1.json').read_bytes()
        self.assertNotEqual(json.loads(raw)['subject_id'], intent['subject_id'])
        with patch.object(private, 'owner_intent', return_value=intent), \
             patch.object(binding, 'stable_read_bytes', return_value=raw):
            with self.assertRaisesRegex(binding.BindingHold, 'OWNER_EXACT_SUBJECT'):
                binding._verify_native_owner('private')

    def test_snapshot_paths_are_only_same_pinned_two_hosts_without_installed_fallback(self):
        self.assertEqual(binding.HOST.parent, binding.RUNNER.parent)
        self.assertEqual(binding.HOST.parent, binding.ROOT / 'output/g6-fixed-host-snapshot-v1/bin')
        self.assertEqual(binding.HOST.name, 'codex.exe')
        self.assertEqual(binding.RUNNER.name, 'codex-command-runner.exe')
        self.assertIn('research/nexus-g6-fixed-host-snapshot-provenance-v1.json',
                      private.owner_intent()['material'])

    def test_multilink_snapshot_denies_before_use_and_releases_open_file(self):
        with tempfile.TemporaryDirectory() as folder:
            host = Path(folder) / 'public-host'
            raw = b'PUBLIC_HOST_FIXTURE'
            host.write_bytes(raw)
            with patch.object(binding, 'HOST', host), \
                 patch.object(binding, 'HOST_SHA', hashlib.sha256(raw).hexdigest()), \
                 patch.object(binding.storage, '_win_identity', return_value=(1, b'PUBLIC_ID', len(raw), 100, 2)):
                entered = False
                with self.assertRaisesRegex(binding.BindingHold, 'HOST_SNAPSHOT_SINGLE_LINK'):
                    with binding._held_installed_host(host, binding.HOST_SHA):
                        entered = True
                self.assertFalse(entered)
            host.unlink()  # No leaked stable file handle after this denial.

    def test_generation_format_repair_preserves_the_original_exact_acceptance(self):
        prompt = private.prompt()
        self.assertIn(b'Never output backticks', prompt)
        self.assertIn(b'No spaces before or after commas', prompt)
        self.assertNotIn(private.expected_report(), prompt)
        exact = private.expected_report() + private.END
        for changed in (b'```csv\n' + exact, exact.replace(b',', b', '), b'PUBLIC_EXTRA\n' + exact):
            self.assertIsNone(private.verified_report(changed))

    def test_changed_loaded_private_code_denies_before_source_observation(self):
        with patch.object(binding, 'normalized_sha', return_value='0' * 64), \
             patch.object(private, 'stable_read_bytes') as read:
            with self.assertRaisesRegex(binding.BindingHold, 'LOADED_PRIVATE_REVISION_CHANGED'):
                private.rows()
            read.assert_not_called()

    def test_missing_signature_denies_before_new_reservation_or_materialization(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding, 'ROOT', Path(folder)), \
             patch.object(binding, '_prepare_native') as prepare:
            with self.assertRaises((OSError, ValueError)):
                private.attempt()
            prepare.assert_not_called()
            self.assertFalse((Path(folder) / private.WORK).exists())

    def test_reserved_private_attempt_cannot_run_even_with_test_only_proof(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding, 'ROOT', Path(folder)), \
             patch.object(binding, '_verify_native_owner', return_value=('TEST_ONLY', 1, 2, 3)), \
             patch.object(binding, '_prepare_native') as prepare:
            reserved = Path(folder) / private.WORK
            reserved.mkdir(parents=True)
            with self.assertRaisesRegex(binding.BindingHold, 'ATTEMPT_RESERVED_NO_REPLAY'):
                private.attempt()
            prepare.assert_not_called()

    def test_partial_public_transport_preserves_original_and_uses_its_own_reservation(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding, 'ROOT', Path(folder)):
            directory = Path(folder) / private.PUBLIC_WORK / 'retention_report'
            directory.mkdir(parents=True)
            original = b'{"schema":'
            (directory / 'disposition.json').write_bytes(original)
            record = binding.reconcile_public('retention_report')
            self.assertEqual(record['status'], 'QUARANTINE')
            self.assertFalse(record['automatic_retry'])
            self.assertEqual((directory / 'disposition.json').read_bytes(), original)
            self.assertTrue((directory / 'reconciliation.json').is_file())

    def test_private_receipt_requires_settled_accepted_output_and_reopens_artifact(self):
        public_rows = private.rows()
        with tempfile.TemporaryDirectory() as folder, patch.object(private, 'ROOT', Path(folder)), \
             patch.object(private, 'rows', return_value=public_rows):
            directory = Path(folder) / private.WORK / 'result'
            directory.mkdir(parents=True)
            stdout = private.expected_report() + private.END
            (directory / 'stdout.bin').write_bytes(stdout)
            result = {'status': 'LOCAL_RETENTION_RESULT_OBSERVED', 'retired': True,
                      'job_active_after_termination': 0, 'stdout_sha256': hashlib.sha256(stdout).hexdigest()}
            with patch.object(binding, '_fixed_attempt', return_value=result):
                receipt = private.attempt()
            self.assertEqual(receipt['status'], 'LOCAL_RETENTION_ARTIFACT_VERIFIED')
            self.assertEqual((directory / 'retention-index.csv').read_bytes(), private.expected_report())
            self.assertEqual(json.loads((directory / 'report-receipt.json').read_bytes()), receipt)

    def test_unknown_or_changed_output_cannot_create_report_or_restore_authority(self):
        public_rows = private.rows()
        for changes in ({'status': 'QUARANTINE'}, {'job_active_after_termination': 1},
                        {'retired': False}, {'stdout_sha256': '0' * 64}):
            with tempfile.TemporaryDirectory() as folder, patch.object(private, 'ROOT', Path(folder)), \
                 patch.object(private, 'rows', return_value=public_rows):
                directory = Path(folder) / private.WORK / 'result'
                directory.mkdir(parents=True)
                stdout = private.expected_report() + private.END
                (directory / 'stdout.bin').write_bytes(stdout)
                result = {'status': 'LOCAL_RETENTION_RESULT_OBSERVED', 'retired': True,
                          'job_active_after_termination': 0, 'stdout_sha256': hashlib.sha256(stdout).hexdigest()}
                with patch.object(binding, '_fixed_attempt', return_value={**result, **changes}):
                    receipt = private.attempt()
                self.assertEqual(receipt['status'], 'QUARANTINE')
                self.assertTrue(receipt['retired'])
                self.assertFalse((directory / 'retention-index.csv').exists())


if __name__ == '__main__':
    unittest.main()
