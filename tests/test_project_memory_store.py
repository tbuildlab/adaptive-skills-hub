from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from ash import project_memory as m
from ash.project_memory_store import MemoryStore, validate_supersessions
from ash.reusable_references import LibrarySnapshot
from tests.test_project_memory import fact, fixture, temporary


class MemoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = temporary()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proposal, self.workspace = fixture(self.root)
        if not self.root.drive.casefold() == "d:":
            drive = patch("ash.project_memory_store._require_d_drive")
            drive.start()
            self.addCleanup(drive.stop)
        self.store = MemoryStore(dict(schema_version="nexus.project-memory.config.v1", enabled=True,
            root=str(self.root / "memory"), required_drive="D:"))
        self.store.initialize(self.workspace, authorized=True, authorization_ref="test-owner")

    def persist(self, value=None, expected=None, **kwargs):
        return self.store.persist(value or self.proposal, self.workspace, authorized=True,
            privacy_reviewed=True, authorization_ref="test-owner", expected_previous_digest=expected, **kwargs)

    def metadata(self):
        return {p.name: (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
                for p in (self.store.path / "projects").iterdir() if p.is_file()}

    def test_explicit_write_latest_revision_and_no_read_mutation(self):
        first = self.persist()
        second = self.persist(expected=first["revision_digest"])
        before = self.metadata()
        bundle = self.store.lookup(self.workspace)
        self.assertEqual(bundle["current_digest"], second["revision_digest"])
        self.assertEqual(len(bundle["revisions"]), 2)
        self.assertEqual(len(list((self.store.path / "projects").iterdir())), 1)
        self.assertEqual(self.metadata(), before)

    def test_unauthorized_digest_writer_and_atomic_failure(self):
        with self.assertRaises(m.MemoryError):
            self.store.persist(self.proposal, self.workspace, authorized=False, privacy_reviewed=True,
                authorization_ref="test-owner", expected_previous_digest=None)
        first = self.persist()
        before = self.metadata()
        with self.assertRaises(m.MemoryError):
            self.persist(expected="0" * 64)
        with patch("ash.project_memory_store.os.replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                self.persist(expected=first["revision_digest"])
        self.assertEqual(self.metadata(), before)
        lock = self.store.path / ".write.lock"
        lock.write_text("other writer", encoding="utf-8")
        with self.assertRaises(m.MemoryError):
            self.persist(expected=first["revision_digest"])
        self.assertEqual(lock.read_text(encoding="utf-8"), "other writer")
        self.assertEqual(self.metadata(), before)

    def test_evidence_staleness_and_forged_completion(self):
        (self.workspace.root / "artifact.txt").write_text("changed", encoding="utf-8")
        with self.assertRaises(m.MemoryError):
            self.persist()

    def test_host_cli_and_config_are_explicit_and_bundle_only(self):
        config = self.root / "workspaces.json"
        config.write_bytes(m.encoded({"schema_version": "nexus.mcp.workspace.v1",
            "workspaces": {"project": {"root": str(self.workspace.root)}}}))
        script = Path(__file__).resolve().parents[1] / "scripts/project_memory.py"
        base = [sys.executable, "-B", str(script)]
        args = ["--workspace-config", str(config), "--workspace-id", "project"]
        denied = subprocess.run(base + ["initialize", *args, "--root", str(self.store.path)], capture_output=True)
        self.assertEqual(denied.returncode, 2)
        initialized = subprocess.run(base + ["initialize", *args, "--root", str(self.store.path), "--authorize", "--authorization-ref", "owner"], capture_output=True)
        self.assertEqual(initialized.returncode, 0, initialized.stdout)
        result = subprocess.run(base + ["persist", *args, "--authorize", "--privacy-reviewed", "--authorization-ref", "owner"],
                                input=m.encoded(self.proposal), capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(len(list((self.store.path / "projects").iterdir())), 1)

    def test_project_capacity_corrupt_chain_and_prior_history(self):
        first = self.persist()
        with patch.object(m, "MAX_PROJECTS", 0):
            with self.assertRaises(m.MemoryError):
                self.persist(expected=first["revision_digest"])
        bundle = self.store.lookup(self.workspace)
        bundle["revisions"][0]["state"]["stack"] = ["Unapproved change"]
        path = next((self.store.path / "projects").iterdir())
        path.write_bytes(m.encoded(bundle))
        with self.assertRaises(m.MemoryError):
            self.store.lookup(self.workspace)

    def test_unsafe_root_overlap_and_hardlink_rejected(self):
        original = self.store.path
        self.store.path = self.workspace.root / "memory"
        with self.assertRaises(m.MemoryError):
            self.store.root(self.workspace, allow_missing=True)
        self.store.path = original
        self.persist()
        path = next((self.store.path / "projects").iterdir())
        link = self.root / "linked-record"
        os.link(path, link)
        with self.assertRaises(m.MemoryError):
            self.store.lookup(self.workspace)

    def test_unknown_reference_and_unavailable_library_preserve_prior_state(self):
        first = self.persist()
        before = self.metadata()
        self.proposal["references_used"] = [dict(reference_id="unknown", reason="Task relevant", influenced_area="layout",
            pattern_adopted=False, evidence_refs=[])]
        with self.assertRaises(m.MemoryError):
            self.persist(expected=first["revision_digest"], reference_reader=lambda: LibrarySnapshot("unavailable"))
        self.assertEqual(self.metadata(), before)

    def test_supersession_retains_history_and_owner_evidence_required(self):
        decision = dict(id="stack", kind="architecture", text="HTML", user_approved=False,
                        confidence="observed", evidence_refs=[])
        self.proposal["state"]["decisions"] = [decision]
        first = self.persist()
        value = deepcopy(self.proposal)
        replacement = {**decision, "text": "Next.js"}
        value["state"]["decisions"] = [replacement]
        with self.assertRaises(m.MemoryError):
            self.persist(value, first["revision_digest"])
        value["supersessions"] = [dict(decision_id="stack", previous_sha256=m.digest(decision),
            replacement_sha256=m.digest(replacement), reason="Verified implementation requirement", evidence_refs=["validation"])]
        self.persist(value, first["revision_digest"])
        bundle = self.store.lookup(self.workspace)
        self.assertEqual(bundle["revisions"][0]["state"]["decisions"][0]["text"], "HTML")
        prior = deepcopy(self.proposal)
        prior["state"]["decisions"][0]["kind"] = "frozen"
        with self.assertRaises(m.MemoryError):
            validate_supersessions(prior, value)

    def test_real_junction_root_is_rejected(self):
        if os.name != "nt":
            self.skipTest("Windows junction fixture")
        alias = self.root / "memory-link"
        result = subprocess.run([os.environ.get("COMSPEC", "cmd.exe"), "/c", "mklink", "/J", str(alias), str(self.store.path)],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        try:
            linked = MemoryStore(dict(schema_version="nexus.project-memory.config.v1", enabled=True,
                root=str(alias), required_drive="D:"))
            with self.assertRaises(ValueError):
                linked.lookup(self.workspace)
        finally:
            os.rmdir(alias)

    def test_store_and_bundle_size_caps_preserve_old_state(self):
        first = self.persist()
        before = self.metadata()
        with patch.object(m, "MAX_STORE_BYTES", 1):
            with self.assertRaises(m.MemoryError):
                self.persist(expected=first["revision_digest"])
        with patch.object(m, "MAX_BUNDLE_BYTES", 1):
            with self.assertRaises(m.MemoryError):
                self.store.lookup(self.workspace)
        self.assertEqual(self.metadata(), before)

    def test_reference_id_validation_does_not_write_library(self):
        self.proposal["references_used"] = [dict(reference_id="known", reason="Task relevant", influenced_area="layout",
            pattern_adopted=False, evidence_refs=[])]
        snapshot = LibrarySnapshot("loaded", ({"id": "known", "workspace": self.proposal["identity"]["workspace_binding"],
                                               "acceptance": "accepted"},), "0" * 64)
        first = self.persist(reference_reader=lambda: snapshot)
        self.proposal["references_used"][0]["reference_id"] = "unknown"
        with self.assertRaises(m.MemoryError):
            self.persist(expected=first["revision_digest"], reference_reader=lambda: snapshot)

    def test_isolation_ambiguity_and_malformed(self):
        self.persist()
        foreign_root = self.root / "foreign"
        foreign_root.mkdir()
        _, foreign = fixture(foreign_root)
        with self.assertRaises(m.MemoryError):
            self.store.lookup(foreign)
        second = deepcopy(self.proposal)
        second["identity"]["project_id"] = "b" * 32
        second["completion"].update(kind="incomplete", automated_validation="not_run")
        second["state"]["completed_scope"] = []
        self.persist(second)
        with self.assertRaisesRegex(m.MemoryError, "ambiguous"):
            self.store.lookup(self.workspace)
        self.assertEqual(self.store.lookup(self.workspace, "a" * 32)["project_id"], "a" * 32)
        path = next(p for p in (self.store.path / "projects").iterdir() if p.name.endswith("a" * 32 + ".json"))
        path.write_bytes(b"{}")
        with self.assertRaises(m.MemoryError):
            self.store.lookup(self.workspace, "a" * 32)

    def test_root_and_revision_capacity(self):
        for root in ("relative", r"\\server\share\memory", "C:/memory", "D:/bad/../memory", "D:/bad:stream"):
            with self.assertRaises((m.MemoryError, ValueError)):
                MemoryStore(dict(schema_version="nexus.project-memory.config.v1", enabled=True, root=root, required_drive="D:"))
        first = self.persist()
        with patch.object(m, "MAX_REVISIONS", 1):
            with self.assertRaises(m.MemoryError):
                self.persist(expected=first["revision_digest"])


if __name__ == "__main__":
    unittest.main()
