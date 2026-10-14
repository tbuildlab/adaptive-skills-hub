"""Preparation/negative tests only; mocked signatures never qualify a real Owner."""
from pathlib import Path
from types import SimpleNamespace
import base64
import json
import tempfile
import unittest
from unittest.mock import patch

from scripts import verify_g3_owner_signature as verifier


class OwnerSigningProcedureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        directory = Path(self.temp.name)
        self.payload = directory / 'decision.json'
        self.raw = (verifier.ROOT / 'research/nexus-g3-owner-signing-decision-v1.json').read_bytes()
        self.payload.write_bytes(self.raw)
        self.signature = directory / 'decision.json.sig'
        self.signature.write_bytes(b'-----BEGIN SSH SIGNATURE-----\nSYNTHETIC_TEST_ONLY\n')
        self.public = directory / 'owner.pub'
        # Public-format fixture only. No private key is generated or opened.
        self.key = 'ssh-ed25519 ' + base64.b64encode(
            b'\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20' + bytes(range(32))).decode()
        self.public.write_text(self.key + ' public-format-fixture\n', encoding='ascii')
        self.profile = {'login': 'TDY0225', 'id': 223441940}
        self.keys = [{'id': 123, 'key': self.key}]
        body = json.loads(self.raw)
        self.now = body['effective_at'] + 1

    def check(self, expected=None, **changes):
        with patch.object(verifier, 'github', side_effect=lambda suffix:
                          self.profile if suffix == '' else self.keys), \
             patch.object(verifier.time, 'time', return_value=self.now), \
             patch.object(verifier.time, 'monotonic', side_effect=[10, changes.get('finished', 11)]), \
             patch.object(verifier.subprocess, 'run', return_value=SimpleNamespace(
                 returncode=changes.get('returncode', 0))) as process:
            if expected:
                with self.assertRaisesRegex(verifier.Denied, expected):
                    verifier.verify(self.payload, self.signature, changes.get('public', self.public))
                return
            result = verifier.verify(self.payload, self.signature, self.public)
            return result, process

    def test_mocked_success_is_nonbearer_and_uses_exact_stdin_bytes(self):
        with patch.dict('os.environ', {'WINDIR': r'C:\untrusted-caller-choice'}):
            result, process = self.check()
        self.assertEqual(result['record_kind'], 'READBACK_ONLY_NOT_BEARER_AUTHORITY')
        self.assertFalse(result['registration_created'])
        self.assertEqual(result['real_admission'], 'NO')
        self.assertEqual(process.call_args.kwargs['input'], self.raw)
        command = process.call_args.args[0]
        self.assertEqual(command[0], r'C:\Windows\System32\OpenSSH\ssh-keygen.exe')
        self.assertEqual(command[1:3], ['-Y', 'verify'])
        self.assertIn(verifier.NAMESPACE, command)
        self.assertIn(verifier.PRINCIPAL, command)

    def test_modified_signed_message_denies_before_crypto(self):
        self.payload.write_bytes(self.raw.replace(b'APPROVE', b'REVOKE', 1))
        self.check('PAYLOAD_DIGEST')

    def test_line_ending_change_denies(self):
        self.payload.write_bytes(self.raw.replace(b'\n', b'\r\n'))
        self.check('PAYLOAD_DIGEST')

    def test_wrong_immutable_account_id_denies(self):
        self.profile = {'login': 'TDY0225', 'id': 1}
        self.check('GITHUB_IDENTITY')

    def test_removed_or_unpublished_key_denies(self):
        self.keys = []
        self.check('SIGNING_KEY_REGISTRY')

    def test_provider_public_comment_does_not_change_key_identity(self):
        self.keys = [{'id': 123, 'key': self.key + ' owner-signing-comment'}]
        result, _ = self.check()
        self.assertEqual(result['github_signing_key_id'], 123)

    def test_wrong_or_ambiguous_key_denies(self):
        self.keys = [{'id': 1, 'key': self.key + 'wrong'}]
        self.check('SIGNING_KEY_MEMBERSHIP')
        self.keys = [{'id': 1, 'key': self.key}, {'id': 2, 'key': self.key}]
        self.check('SIGNING_KEY_MEMBERSHIP')

    def test_private_filename_never_opened(self):
        self.check('PUBLIC_FILE_REQUIRED', public=self.public.with_suffix(''))

    def test_non_ed25519_public_key_denies(self):
        self.public.write_text('ssh-rsa AAAA\n')
        self.check('KEY_TYPE')

    def test_plain_approved_is_not_a_signature(self):
        self.signature.write_bytes(b'approved')
        self.check('SIGNATURE_FORMAT')

    def test_failed_crypto_and_stale_source_deny(self):
        self.check('CRYPTOGRAPHIC_SIGNATURE', returncode=1)
        self.check('SOURCE_FRESHNESS', finished=41)

    def test_expired_exact_packet_denies(self):
        self.now = json.loads(self.raw)['expires_at']
        self.check('DECISION_VALIDITY')

    def test_changed_material_or_review_denies(self):
        original = verifier.files.read_bytes
        with patch.object(verifier.files, 'read_bytes', side_effect=lambda root, name:
                          b'changed' if name == 'ash/core_host_loop.py' else original(root, name)):
            self.check('CURRENT_COMPONENT_OR_REVIEW')


if __name__ == '__main__':
    unittest.main()
