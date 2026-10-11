"""D03 candidate counterexamples, not a fence implementation or qualification.

Git operations affect only a newly created disposable repository. No remote,
credential, user Git configuration, signing key file, or production grant is used.
Existing D03 fault/retirement tests remain the semantic qualification harness.
"""
from copy import deepcopy
from pathlib import Path
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

from ash import g4_host_adapter as g4, g6_host_adapter as g6
from ash.g3_authorization import EligibilityDecision
from scripts import g3_offline_control as model
from tests.g4_fixtures import request, NOW, SOURCE, ORIGINAL


class LocalGitCandidateTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory(prefix="nexus-d03-counterexample-")
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        self.git = shutil.which("git")
        self.assertIsNotNone(self.git, "Git is required to reproduce this candidate")
        # Explicit non-secret runtime inputs only; do not inherit Git/provider auth.
        self.env = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT", "TEMP", "TMP") if k in os.environ}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="Synthetic D03",
                        GIT_COMMITTER_NAME="Synthetic D03", GIT_AUTHOR_EMAIL="d03@example.invalid",
                        GIT_COMMITTER_EMAIL="d03@example.invalid",
                        GIT_AUTHOR_DATE="2000-01-01T00:00:00Z", GIT_COMMITTER_DATE="2000-01-01T00:00:00Z")
        (self.root / "empty-hooks").mkdir()
        self.call("init", "--quiet", "--object-format=sha1", "--initial-branch=counterexample")
        self.zero = "0" * 40
        self.first = self.commit(0)
        self.second = self.commit(1, self.first)
        self.ref = "refs/heads/counterexample"
        self.call("update-ref", self.ref, self.first, self.zero)
        self.call("update-ref", self.ref, self.second, self.first)

    def call(self, *args, data=None, check=True):
        result = subprocess.run([self.git, "-c", "core.hooksPath=" + str(self.root / "empty-hooks"),
                                 "-c", "commit.gpgsign=false", *args], cwd=self.root,
                                env=self.env, input=data, capture_output=True, timeout=15)
        if check:
            # Fixed diagnostics; do not project arbitrary subprocess stderr.
            self.assertEqual(result.returncode, 0, "Isolated Git probe failed")
        return result

    def commit(self, sequence, parent=None, variant="original"):
        body = json.dumps({"basis": "COUNTEREXAMPLE_ONLY_NO_AUTHORITY", "sequence": sequence,
                           "variant": variant}, sort_keys=True).encode()
        blob = self.call("hash-object", "-w", "--stdin", data=body).stdout.strip().decode()
        tree = self.call("mktree", data=f"100644 blob {blob}\tcheckpoint.json\n".encode()).stdout.strip().decode()
        args = ("-p", parent) if parent else ()
        return self.call("commit-tree", tree, *args, "-m", "Synthetic checkpoint").stdout.strip().decode()

    def head(self):
        return self.call("rev-parse", self.ref).stdout.strip().decode()

    def test_conditional_append_rejects_stale_expected_head(self):
        third = self.commit(2, self.second)
        self.assertNotEqual(self.call("update-ref", self.ref, third, self.first, check=False).returncode, 0)
        self.assertEqual(self.head(), self.second)
        self.call("update-ref", self.ref, third, self.second)
        self.assertEqual(self.head(), third)

    def test_valid_object_history_does_not_prevent_head_rollback(self):
        self.call("update-ref", self.ref, self.first, self.second)
        self.assertEqual(self.head(), self.first)
        self.call("fsck", "--full")
        self.assertNotEqual(self.head(), self.second)  # Only the retained observer detects this.

    def test_valid_fork_can_replace_head_under_same_custody(self):
        fork = self.commit(1, self.first, "fork")
        self.assertNotEqual(fork, self.second)
        self.call("update-ref", self.ref, fork, self.second)
        self.call("fsck", "--full")
        self.assertEqual(self.head(), fork)

    def test_git_ancestry_does_not_enforce_checkpoint_sequence_gaps(self):
        gap = self.commit(3, self.second)
        self.call("update-ref", self.ref, gap, self.second)
        self.call("fsck", "--full")
        self.assertEqual(self.call("rev-list", "--count", self.ref).stdout.strip(), b"3")
        body = json.loads(self.call("show", self.ref + ":checkpoint.json").stdout)
        self.assertEqual(body["sequence"], 3)  # Sequence 2 is absent despite valid Git ancestry.

    def test_create_only_reference_can_be_deleted_and_recreated_by_custodian(self):
        key = "refs/checkpoints/00000000000000000001"
        self.call("update-ref", key, self.second, self.zero)
        self.assertNotEqual(self.call("update-ref", key, self.first, self.zero, check=False).returncode, 0)
        self.call("update-ref", "-d", key, self.second)
        self.call("update-ref", key, self.first, self.zero)
        self.call("fsck", "--full")
        self.assertEqual(self.call("rev-parse", key).stdout.strip().decode(), self.first)


class RecoveryCustodyCounterexamples(unittest.TestCase):
    def test_joint_model_restore_erases_detection_anchor_without_creating_authority(self):
        original = model.FakeAuthorityModel()
        old = deepcopy(original)
        original.transact("CONFIRM", evidence=model.FakeSessionEvidence())
        original.transact("GRANT_MODEL", evidence=model.FakeSessionEvidence())
        original.transact("REVOKE_MODEL")
        # Restoring ALL fixture state is outside the independent-fence assumption.
        old._consistent()
        self.assertEqual(old.state.revoked, "NO")
        self.assertEqual(original.state.revoked, "YES")
        self.assertEqual(old.authority, "NONE")
        with self.assertRaises(model.OfflineError):
            old.promote_to_production()

    def test_local_readonly_attribute_is_reversible_by_same_writer(self):
        with tempfile.TemporaryDirectory(prefix="nexus-d03-attribute-") as directory:
            checkpoint = Path(directory) / "synthetic-head.json"
            checkpoint.write_bytes(b'{"basis":"NO_AUTHORITY","sequence":2}')
            checkpoint.chmod(stat.S_IREAD)
            try:
                checkpoint.chmod(stat.S_IREAD | stat.S_IWRITE)
                checkpoint.write_bytes(b'{"basis":"NO_AUTHORITY","sequence":1}')
                self.assertEqual(json.loads(checkpoint.read_bytes())["sequence"], 1)
            finally:
                checkpoint.chmod(stat.S_IREAD | stat.S_IWRITE)

    def test_valid_signed_old_checkpoint_is_not_proof_of_current_head(self):
        # Reuse Node's mature crypto. Ephemeral private key stays in process memory;
        # no export, serialization, file, log, provider, or external signer exists.
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required for the signed-journal counterexample")
        code = """
          const {generateKeyPairSync, sign, verify} = require('node:crypto');
          const {privateKey, publicKey} = generateKeyPairSync('ed25519');
          const old = Buffer.from('{"basis":"NO_AUTHORITY","sequence":1}');
          const current = Buffer.from('{"basis":"NO_AUTHORITY","sequence":2}');
          const oldSignature = sign(null, old, privateKey);
          const currentSignature = sign(null, current, privateKey);
          console.log(JSON.stringify({
            oldSignatureValid: verify(null, old, publicKey, oldSignature),
            currentSignatureValid: verify(null, current, publicKey, currentSignature),
            changedBodyRejected: !verify(null, current, publicKey, oldSignature)
          }));
        """
        env = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT", "TEMP", "TMP") if k in os.environ}
        result = subprocess.run([node, "-e", code], capture_output=True, env=env, timeout=15)
        self.assertEqual(result.returncode, 0, "In-memory signature probe failed")
        self.assertEqual(json.loads(result.stdout), {"oldSignatureValid": True,
                         "currentSignatureValid": True, "changedBodyRejected": True})

    def test_candidate_labels_and_forged_positive_fixture_cannot_open_g4_g6(self):
        positive = EligibilityDecision("ELIGIBLE", ("G3_ELIGIBLE",), "nexus.g3.subject.v1:" + SOURCE,
                                      "nexus.g3.grant.v1:" + ORIGINAL, SOURCE, NOW, "TEST_FIXTURE_ONLY")
        candidates = [None, positive, {"D03_STATUS": "CLOSED", "qualification": "PASS"},
                      {"signed_checkpoint": "valid", "independent": True}, b"malformed", {}]
        for candidate in candidates:
            with self.subTest(candidate=type(candidate).__name__):
                r = request(requires_recovery=True)
                for verdict in (g4.pre_execution_gate(r, candidate, now=NOW),
                                g6.release_gate(r, candidate, now=NOW)):
                    self.assertEqual(verdict["status"], "DENY")
                    self.assertEqual(verdict["dispatch_authority"], "none")
                    self.assertFalse(verdict["real_admission_enabled"])


if __name__ == "__main__":
    unittest.main()
