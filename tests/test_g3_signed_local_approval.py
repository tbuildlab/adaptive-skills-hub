"""Synthetic origin mocks test contracts only; no fixture is real Owner authority."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import g3_signed_local_approval as local
from scripts import verify_g3_owner_signature as origin


class SignedLocalApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nexus-g3-local-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = (origin.ROOT / 'research/nexus-g3-owner-signing-decision-v1.json').read_bytes()
        self.body = json.loads(self.raw)
        self.payload = self.root / 'approval.json'; self.payload.write_bytes(self.raw)
        root_patch = patch.object(origin, 'ROOT', self.root)
        root_patch.start(); self.addCleanup(root_patch.stop)
        proof_patch = patch.object(origin, 'verify', return_value={
            'status': 'TEST_ONLY_MOCKED_ORIGIN', 'dispatch_authority': 'none', 'real_admission': 'NO'})
        self.proof = proof_patch.start(); self.addCleanup(proof_patch.stop)
        # Synthetic origin/lifecycle cases only. The production-default spent
        # packet is permanently denied; no fixture override ships in the adapter.
        self.production_retirements = local.RETIRED_DECISIONS
        retire_patch = patch.object(local, 'RETIRED_DECISIONS', frozenset())
        retire_patch.start(); self.addCleanup(retire_patch.stop)
        clock_patch = patch.object(local.time, 'time', return_value=self.body['effective_at'] + 1)
        self.clock = clock_patch.start(); self.addCleanup(clock_patch.stop)

    def enroll(self):
        return local.LocalQualification(self.payload, self.root / 'approval.sig', self.root / 'owner.pub')

    def query(self, plane, **changes):
        return plane.eligibility(changes.get('subject', self.body['subject']),
                                 changes.get('scope', self.body['scope']),
                                 changes.get('registration', plane.registration()))

    def test_registration_is_exact_projection_and_never_execution_authority(self):
        plane = self.enroll()
        result = self.query(plane)
        self.assertEqual(result['status'], 'CAPABILITY_ELIGIBLE_ONLY')
        self.assertEqual(result['dispatch_authority'], 'none')
        self.assertEqual(result['real_admission'], 'NO')
        self.assertEqual(plane.registration()['scope'], self.body['scope'])
        self.assertEqual(plane.registration()['execution_authority'], 'none')
        self.assertEqual(self.proof.call_count, 2)  # enrollment and independent current query

    def test_changed_revision_and_dependency_or_license_review_bytes_cannot_inherit(self):
        plane = self.enroll()
        for field in ('revision', 'content_sha256', 'config_sha256'):
            subject = dict(self.body['subject']); subject[field] = '0' * (40 if field == 'revision' else 64)
            self.assertEqual(self.query(plane, subject=subject)['status'], 'DENY')
        with patch.object(origin, 'verify', side_effect=origin.Denied('CURRENT_COMPONENT_OR_REVIEW')):
            self.assertEqual(self.query(plane)['status'], 'DENY')

    def test_issuer_unverified_cannot_register_or_reserve(self):
        self.proof.side_effect = origin.Denied('GITHUB_IDENTITY')
        with self.assertRaises(origin.Denied): self.enroll()
        self.assertFalse((self.root / 'output').exists())

    def test_scope_wrong_task_workspace_project_operations_and_extra_fields_deny(self):
        plane = self.enroll()
        for key, value in [('task_id', 'other'), ('project_id', 'other'),
                           ('workspace_id', 'other'), ('operations', ['execute']),
                           ('account_context', 'invented')]:
            scope = dict(self.body['scope']); scope[key] = value
            self.assertEqual(self.query(plane, scope=scope)['status'], 'DENY')

    def test_registration_tamper_including_candidate_and_policy_substitution_denies(self):
        plane = self.enroll()
        for key in ('approval_id', 'subject_id', 'mechanism', 'capability_id'):
            record = plane.registration(); record[key] = 'candidate-controlled'
            self.assertEqual(self.query(plane, registration=record)['status'], 'DENY')
        record = plane.registration(); record['intake_policy'] = 'candidate-policy'
        self.assertEqual(self.query(plane, registration=record)['status'], 'DENY')
        (plane._directory / 'registration.json').write_text('{}')
        self.assertEqual(self.query(plane)['status'], 'DENY')

    def test_unavailable_current_origin_or_component_denies_without_cached_fallback(self):
        plane = self.enroll()
        for failure in (OSError('unavailable'), origin.Denied('SIGNING_KEY_MEMBERSHIP'),
                        subprocess.TimeoutExpired('verify', 5)):
            with patch.object(origin, 'verify', side_effect=failure):
                self.assertEqual(self.query(plane)['status'], 'DENY')

    def test_expired_and_not_effective_exact_approval_denies(self):
        plane = self.enroll()
        for now in (self.body['effective_at'] - 1, self.body['expires_at']):
            self.clock.return_value = now
            self.assertEqual(self.query(plane)['status'], 'DENY')

    def test_signed_revocation_blocks_later_eligibility_and_readback_is_not_authority(self):
        plane = self.enroll()
        self.assertEqual(self.query(plane)['status'], 'CAPABILITY_ELIGIBLE_ONLY')
        record = plane.revoke('verified-completion', 'a' * 64)
        self.assertEqual(record['decision_evidence']['sha256'], origin.PAYLOAD_SHA)
        self.assertEqual(self.query(plane)['status'], 'DENY')
        self.assertEqual(plane.revoke('verified-completion', 'a' * 64), record)
        self.assertFalse(hasattr(local.LocalQualification, 'restore'))
        with self.assertRaisesRegex(origin.Denied, 'ATTEMPT_ALREADY_RESERVED'): self.enroll()

    def test_crash_or_partial_reservation_cannot_restart_or_reset(self):
        plane = self.enroll()
        marker = plane._directory / (origin.PAYLOAD_SHA + '.reserved')
        marker.write_bytes(b'partial')
        with self.assertRaisesRegex(origin.Denied, 'ATTEMPT_ALREADY_RESERVED'): self.enroll()
        self.assertEqual(marker.read_bytes(), b'partial')

    def test_failed_revocation_write_cannot_leave_live_eligibility(self):
        plane = self.enroll()
        with patch.object(local.files, 'write', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError): plane.revoke('unknown', 'b' * 64)
        self.assertEqual(self.query(plane)['status'], 'DENY')
        with self.assertRaisesRegex(origin.Denied, 'ATTEMPT_ALREADY_RESERVED'): self.enroll()

    def test_malformed_inputs_and_projection_never_create_dispatch(self):
        plane = self.enroll()
        for value in (None, [], {}, 'approved', {'schema_version': 'invented'}):
            self.assertEqual(self.query(plane, subject=value)['status'], 'DENY')
        self.assertFalse(hasattr(plane, 'dispatch'))
        self.assertFalse(hasattr(plane, 'execute'))
        self.assertFalse(hasattr(plane, 'install'))

    def test_payload_reread_tamper_denies_even_if_origin_mock_claimed_success(self):
        self.payload.write_bytes(self.raw + b' ')
        with self.assertRaisesRegex(origin.Denied, 'PAYLOAD_DIGEST'): self.enroll()
        self.assertFalse((self.root / 'output').exists())

    def test_oversized_cyclic_and_nonfinite_inputs_fail_closed(self):
        plane = self.enroll()
        scope = dict(self.body['scope']); scope['extra'] = 'x' * 65537
        self.assertEqual(self.query(plane, scope=scope)['status'], 'DENY')
        scope['extra'] = scope
        self.assertEqual(self.query(plane, scope=scope)['status'], 'DENY')
        scope = dict(self.body['scope']); scope['extra'] = float('nan')
        self.assertEqual(self.query(plane, scope=scope)['status'], 'DENY')

    def test_production_retirement_blocks_fresh_relocated_checkout_before_any_io(self):
        alternate = self.root / 'other-checkout'; alternate.mkdir()
        with patch.object(origin, 'ROOT', alternate), \
             patch.object(local, 'RETIRED_DECISIONS', self.production_retirements), \
             patch.object(origin, 'bounded', side_effect=AssertionError('input read')):
            with self.assertRaisesRegex(origin.Denied, 'SIGNED_APPROVAL_RETIRED'):
                self.enroll()
        self.proof.assert_not_called()
        self.assertEqual(list(alternate.iterdir()), [])

    def test_retirement_blocks_existing_instance_even_when_marker_is_missing(self):
        plane = self.enroll()
        marker = plane._directory / (origin.PAYLOAD_SHA + '.reserved')
        marker.unlink()  # isolated synthetic Host record only
        calls = self.proof.call_count
        with patch.object(local, 'RETIRED_DECISIONS', self.production_retirements):
            self.assertEqual(self.query(plane)['status'], 'DENY')
            with self.assertRaisesRegex(origin.Denied, 'SIGNED_APPROVAL_RETIRED'):
                self.enroll()
        self.assertEqual(self.proof.call_count, calls)


if __name__ == '__main__':
    unittest.main()
