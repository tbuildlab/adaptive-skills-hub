from __future__ import annotations

import copy
import ctypes
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import struct
import tempfile
import time
from typing import Any
import unittest
from unittest.mock import patch
from uuid import UUID
import warnings
import zipfile

import ash.ecosystem_storage as ecosystem_storage
import ash.ecosystem_policy as ecosystem_policy
from ash.ecosystem_bridge import bridge_scout_candidate
from ash.ecosystem_intake import (
    _attempt_base,
    _attempt_record,
    _inventory_zip,
    _write_attempt,
    intake_pre_supplied_zip,
)
from ash.ecosystem_models import EcosystemError, typed_id, zero_authority
from ash.ecosystem_policy import _load_test_source_policy as load_trusted_source_policy
from ash.ecosystem_storage import (
    QuarantineStore,
    _open_test_quarantine_store,
    _is_within,
    _mountinfo_root_risk,
    _reject_posix_remote_or_alias_root,
    _validate_external_root,
    open_quarantine_store,
    open_stable_input,
)
from ash.scout import _authority_states, _base_candidate, _limits_receipt, _security_result


ROOT = Path(__file__).resolve().parents[1]
POLICY_RAW = (ROOT / "config" / "ecosystem-source-policy.json").read_bytes()
COMMIT = "10d5a603aecbd73a38f3a6576cce69a78f8d6f1d"


def policy_root(base: Path) -> Path:
    root = base / "policy-root"
    (root / "config").mkdir(parents=True)
    (root / "config" / "ecosystem-source-policy.json").write_bytes(POLICY_RAW)
    normalized = POLICY_RAW.decode().replace("\r\n", "\n").encode()
    manifest = {
        "config/ecosystem-source-policy.json": {
            "bytes": len(normalized),
            "sha256": hashlib.sha256(normalized).hexdigest(),
        }
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


def scout_receipt(
    *,
    disposition: str = "ADMITTED_FOR_REVIEW",
    repository: str = "openai/codex",
    commit: str = COMMIT,
) -> tuple[dict, str]:
    now = datetime(2026, 8, 28, tzinfo=timezone.utc)
    candidate = _base_candidate(
        capability_type="agent_skill_source",
        provider_id="openai",
        identity_key=f"github:{repository}",
        canonical_identity=f"github:{repository}@{commit}",
        canonical_url=f"https://github.com/{repository}",
        immutable_kind="git_commit",
        immutable_value=commit,
        immutable_verification="verified_at_research_snapshot",
        source_id="synthetic-review",
        discovered_at=now,
        evidence_observed_at=now,
        provenance_state="verified_research_snapshot",
        license_state="VERIFIED_COMPATIBLE",
        trust_state="candidate_research_evidence_only",
        compatibility_state="adaptable" if disposition != "REJECTED" else "incompatible",
        lifecycle_state={
            "ADMITTED_FOR_REVIEW": "classified",
            "REFERENCE_ONLY": "classified",
            "QUARANTINED": "quarantined",
            "REJECTED": "rejected",
            "INSUFFICIENT_EVIDENCE": "classified",
        }[disposition],
        claimed_tags=["skill"],
        verified_tags=["skill"],
        evidence_references=[],
        admission_disposition=disposition,
        reason_codes=["research_evidence_only"],
        declared_execution_mechanisms=["reference_source"],
    )
    if disposition == "ADMITTED_FOR_REVIEW":
        candidate["ranking"] = {"score": 1, "position": 1, "relation": "recommended"}
        recommended = [candidate["candidate_id"]]
        status = "recommendation_ready"
        result_code = "SCOUT_RECOMMENDATION_READY"
    elif disposition == "REFERENCE_ONLY":
        candidate["ranking"] = {"score": 0, "position": None, "relation": "reference_only"}
        recommended = []
        status = "evidence_only"
        result_code = "SCOUT_NO_ADMISSIBLE_RECOMMENDATION"
    else:
        recommended = []
        status = "evidence_only"
        result_code = "SCOUT_NO_ADMISSIBLE_RECOMMENDATION"
    receipt = {
        "schema_version": "nexus.candidate-scout-receipt.v1",
        "scout_id": "11111111-1111-4111-8111-111111111111",
        "issued_at": "2026-08-28T00:00:00Z",
        "runtime_decision_id": "22222222-2222-4222-8222-222222222222",
        "invoked_reason": "trusted_capability_gap_capability_not_covered",
        "capability_gap": {
            "task_category": "skill",
            "domains": ["skill"],
            "outputs": [],
            "validation_requirements": [],
        },
        "search_scope": {
            "source_ids": ["synthetic-review"],
            "queries": ["skill"],
            "limits": _limits_receipt(),
        },
        "source_results": [
            {
                "source_id": "synthetic-review",
                "kind": "research_snapshot",
                "status": "queried",
                "candidate_count": 1,
                "http_requests": 0,
                "execution_or_connection": "none",
            }
        ],
        "candidates": [candidate],
        "recommended_candidate_ids": recommended,
        "scout_version": "nexus.read-only-skill-mcp-scout.v1",
        "admission_version": "nexus.provenance-aware-admission.v1",
        "selector_version": "nexus.minimum-sufficient-selector.v1",
        "status": status,
        "result_code": result_code,
        "evidence_freshness": "fresh",
        "authority_states": _authority_states(),
        "security_result": _security_result(),
    }
    return receipt, candidate["candidate_id"]


def test_store(
    base: Path,
    *,
    policy: Any | None = None,
    name: str = "cas",
    max_cas_bytes: int = 64 * 1024 * 1024,
) -> QuarantineStore:
    trusted = policy or load_trusted_source_policy(root=policy_root(base))
    return _open_test_quarantine_store(
        base / name,
        policy=trusted,
        max_cas_bytes=max_cas_bytes,
    )


def zip_bytes(entries: list[tuple[str, bytes]], *, compression: int = zipfile.ZIP_DEFLATED) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=compression, allowZip64=False) as archive:
        for name, payload in entries:
            archive.writestr(name, payload)
    return buffer.getvalue()


class StorageAndBridgeTests(unittest.TestCase):
    def test_store_construction_and_writer_capabilities_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))

            with self.assertRaises(EcosystemError) as raised:
                open_quarantine_store(policy=trusted)
            self.assertEqual(raised.exception.reason_code, "POLICY_UNTRUSTED")

            # The production factory exposes no caller-selected root, repository,
            # quota, mode, or construction token.  Direct construction cannot
            # manufacture the external seal even with self-consistent digests.
            with self.assertRaises(EcosystemError):
                QuarantineStore(
                    base / "forged-cas",
                    repository_root=base / "forged-repository",
                    max_cas_bytes=1,
                    policy_semantic_sha256=trusted.policy_semantic_sha256,
                    integrity_manifest_sha256=trusted.integrity_manifest_sha256,
                    construction_mode="production",
                )
            with self.assertRaises(TypeError):
                open_quarantine_store(policy=trusted, root=base / "redirected")  # type: ignore[call-arg]
            with self.assertRaises(EcosystemError):
                _open_test_quarantine_store(
                    base / "oversized-cas",
                    policy=trusted,
                    max_cas_bytes=trusted.resource_limits["max_cas_bytes"] + 1,
                )

            store = test_store(base, policy=trusted, max_cas_bytes=1_000_000)
            locator = "evidence/sha256/" + ("0" * 64) + ".json"
            copied_writer = copy.copy(ecosystem_storage._INTAKE_RECORD_WRITER)
            self.assertIsNot(copied_writer, ecosystem_storage._INTAKE_RECORD_WRITER)
            forged_tokens = (
                object(),
                copied_writer,
                ecosystem_storage._COMPARISON_RECORD_WRITER,
            )
            for writer in forged_tokens:
                with self.subTest(writer=writer), self.assertRaises(EcosystemError) as raised:
                    store._publish_record(locator, {}, maximum_bytes=100, writer_token=writer)
                self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")

            # The lowest staging primitive repeats capability and closed-locator
            # checks; it is not an alternate arbitrary-file publication seam.
            arbitrary = store.root / "evidence" / "sha256" / (("0" * 64) + ".json")
            with self.assertRaises(EcosystemError):
                store._put_record_staged(
                    store.root / "tmp" / (("0" * 32) + ".record"),
                    arbitrary,
                    b"{}\n",
                    record_parts=("evidence", "sha256", ("0" * 64) + ".json"),
                    relative_parent="evidence/sha256",
                    maximum_bytes=100,
                    writer_token=object(),
                )
            self.assertFalse(arbitrary.exists())
            self.assertEqual(list((store.root / "tmp").iterdir()), [])

            tree_payload = {
                "schema_version": "nexus.ecosystem-tree.v1",
                "tree_id": typed_id("tree", {"fixture": "writer-domain"}),
            }
            tree_digest = tree_payload["tree_id"].split("/", 1)[1]
            wrong_domain = f"revisions/sha256/{tree_digest}.json"
            with self.assertRaises(EcosystemError) as raised:
                store._publish_record(
                    wrong_domain,
                    tree_payload,
                    maximum_bytes=1_000,
                    writer_token=ecosystem_storage._INTAKE_RECORD_WRITER,
                )
            self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")

            correct_domain = f"trees/sha256/{tree_digest}.json"
            with self.assertRaises(EcosystemError) as raised:
                store._publish_record(
                    correct_domain,
                    tree_payload,
                    maximum_bytes=1_000,
                    writer_token=ecosystem_storage._STATE_RECORD_WRITER,
                )
            self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")

            raw = ecosystem_storage.canonical_json_bytes(tree_payload)
            with self.assertRaises(EcosystemError) as raised:
                store._put_record_staged(
                    store.root / "tmp" / (("1" * 32) + ".record"),
                    store.root / wrong_domain,
                    raw,
                    record_parts=("revisions", "sha256", f"{tree_digest}.json"),
                    relative_parent="revisions/sha256",
                    maximum_bytes=1_000,
                    writer_token=ecosystem_storage._INTAKE_RECORD_WRITER,
                )
            self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")
            self.assertEqual(list((store.root / "tmp").iterdir()), [])

            # Even direct fixture-byte placement is rejected on authoritative
            # reread when a schema is stored under another record domain.
            misplaced = store.root / wrong_domain
            misplaced.write_bytes(raw)
            with self.assertRaises(EcosystemError) as raised:
                store.read_record(wrong_domain, maximum_bytes=1_000)
            self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")

            production = ecosystem_policy.load_trusted_source_policy()
            with patch.object(
                ecosystem_storage,
                "_production_store_root",
                return_value=base / "production-cas",
            ):
                production_store = open_quarantine_store(policy=production)
            production_store._require_policy(production)

    def test_posix_mount_projection_rejects_network_and_bind_aliases(self) -> None:
        local = "36 25 8:1 / / rw,relatime - ext4 /dev/sda1 rw"
        network = local + "\n40 36 0:52 / /mnt/share rw - nfs4 server:/share rw"
        alias = local + "\n41 36 8:1 /source /mnt/alias rw - ext4 /dev/sda1 rw"
        root_alias = local + "\n42 36 8:1 / /mnt/root-alias rw - ext4 /dev/sda1 rw"
        unknown_fuse = local + "\n43 36 0:61 / /mnt/bucket rw - fuse.s3fs bucket rw"
        self.assertIsNone(_mountinfo_root_risk(Path("/tmp/nexus"), local))
        self.assertEqual(_mountinfo_root_risk(Path("/mnt/share/nexus"), network), "network")
        self.assertEqual(_mountinfo_root_risk(Path("/mnt/alias/nexus"), alias), "alias")
        self.assertEqual(_mountinfo_root_risk(Path("/mnt/root-alias/nexus"), root_alias), "alias")
        self.assertEqual(
            _mountinfo_root_risk(Path("/mnt/bucket/nexus"), unknown_fuse), "unverifiable"
        )
        self.assertEqual(_mountinfo_root_risk(Path("/missing/nexus"), ""), "unverifiable")

    def test_posix_locality_proof_fails_closed_before_store_publication(self) -> None:
        with patch.object(
            ecosystem_storage,
            "_runtime_platform_identity",
            return_value=("posix", "darwin"),
        ), self.assertRaises(EcosystemError) as raised:
            _reject_posix_remote_or_alias_root(Path("/Users/example/nexus/ecosystem/v1"))
        self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "network-backed-xdg" / "nexus" / "ecosystem" / "v1"
            production = ecosystem_policy.load_trusted_source_policy()
            with patch.object(
                ecosystem_storage,
                "_production_store_root",
                return_value=target,
            ), patch.object(
                ecosystem_storage,
                "_runtime_platform_identity",
                return_value=("posix", "linux"),
            ), patch.object(
                ecosystem_storage,
                "_read_linux_mountinfo",
                return_value="40 36 0:52 / /mnt/network rw - nfs4 server:/share rw",
            ), patch.object(
                ecosystem_storage,
                "_mountinfo_root_risk",
                return_value="network",
            ), self.assertRaises(EcosystemError) as raised:
                open_quarantine_store(policy=production)
            self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")
            self.assertFalse(target.exists())

    def test_failed_blob_and_record_paths_leave_no_staging_residue(self) -> None:
        class NonBytes:
            def read(self, _size: int = -1) -> str:
                return "not-bytes"

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            store = test_store(base, max_cas_bytes=1_000_000)
            failures = (
                lambda: store.put_blob(io.BytesIO(b"too-large"), maximum_bytes=1),
                lambda: store.put_blob(
                    io.BytesIO(b"digest"), maximum_bytes=10, expected_sha256="0" * 64
                ),
                lambda: store.put_blob(
                    io.BytesIO(b"size"), maximum_bytes=10, expected_size=5
                ),
                lambda: store.put_blob(
                    io.BytesIO(b"deadline"), maximum_bytes=10, deadline=time.monotonic() - 1
                ),
                lambda: store.put_blob(NonBytes(), maximum_bytes=10),
            )
            for failure in failures:
                with self.subTest(failure=failure), self.assertRaises(EcosystemError):
                    failure()
                self.assertEqual(list((store.root / "tmp").iterdir()), [])

            self.assertFalse(hasattr(store, "put_record"))
            with self.assertRaises(EcosystemError):
                store._publish_record(
                    "evidence/sha256/" + ("0" * 64) + ".json",
                    {"value": 1},
                    maximum_bytes=100,
                    writer_token=object(),
                )
            self.assertEqual(list((store.root / "tmp").iterdir()), [])

            with patch("ash.ecosystem_storage.os.link", side_effect=OSError("synthetic")):
                with self.assertRaises(EcosystemError):
                    store.put_blob(io.BytesIO(b"publication"), maximum_bytes=20)
                self.assertEqual(list((store.root / "tmp").iterdir()), [])

    def test_stable_input_ignores_unrelated_sibling_directory_churn(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            held = base / "held.zip"
            held.write_bytes(b"stable")
            with open_stable_input(held, maximum_bytes=100) as stable:
                (base / "unrelated.tmp").write_bytes(b"sibling")
                stable.verify_unchanged()
                self.assertEqual(stable.read(), b"stable")

    def test_target_mutation_or_replacement_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            held = base / "held.zip"
            held.write_bytes(b"stable")
            with open_stable_input(held, maximum_bytes=100) as stable:
                try:
                    held.write_bytes(b"mutated target")
                except PermissionError:
                    # Windows share-mode protection can reject the mutation
                    # before identity verification; that is also fail-closed.
                    self.assertEqual(stable.read(), b"stable")
                else:
                    with self.assertRaises(EcosystemError) as raised:
                        stable.verify_unchanged()
                    self.assertEqual(raised.exception.reason_code, "INPUT_UNSTABLE")

    def test_ancestor_replacement_or_identity_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            parent = base / "parent"
            parent.mkdir()
            held = parent / "held.zip"
            held.write_bytes(b"stable")
            with open_stable_input(held, maximum_bytes=100) as stable:
                moved = base / "moved"
                try:
                    parent.rename(moved)
                except PermissionError:
                    self.assertEqual(stable.read(), b"stable")
                else:
                    parent.mkdir()
                    (parent / "held.zip").write_bytes(b"replacement")
                    with self.assertRaises(EcosystemError) as raised:
                        stable.verify_unchanged()
                    self.assertEqual(raised.exception.reason_code, "INPUT_UNSTABLE")

    def test_store_seal_and_forbidden_runtime_roots_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            for relative in (Path(".codex/skills"), Path(".codex/plugins/cache/child")):
                target = base / relative
                target.mkdir(parents=True)
                with self.subTest(relative=relative), self.assertRaises(EcosystemError) as raised:
                    _open_test_quarantine_store(
                        target, policy=trusted, max_cas_bytes=100
                    )
                self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")
            store = test_store(base, policy=trusted, max_cas_bytes=100)
            store.root = base / "redirected"
            with self.assertRaises(EcosystemError) as raised:
                store.put_blob(io.BytesIO(b"x"), maximum_bytes=1)
            self.assertEqual(raised.exception.reason_code, "CAS_ROOT_INVALID")

    def test_immutable_cas_reuses_exact_bytes_and_detects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = test_store(Path(temporary), max_cas_bytes=1_000_000)
            digest, size = store.put_blob(io.BytesIO(b"inert bytes"), maximum_bytes=100)
            self.assertEqual(size, 11)
            self.assertEqual(store.put_blob(io.BytesIO(b"inert bytes"), maximum_bytes=100), (digest, size))
            self.assertEqual(store.read_blob(digest, maximum_bytes=100), b"inert bytes")
            object_path = store.root / "objects" / "sha256" / digest[:2] / digest
            object_path.write_bytes(b"mutated")
            with self.assertRaises(EcosystemError) as raised:
                store.read_blob(digest, maximum_bytes=100)
            self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")

    def test_cas_object_link_count_mutation_fails_on_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = test_store(Path(temporary), max_cas_bytes=1_000_000)
            digest, _size = store.put_blob(io.BytesIO(b"held object"), maximum_bytes=100)
            object_path = store.root / "objects" / "sha256" / digest[:2] / digest
            alias = Path(temporary) / "second-link"
            os.link(object_path, alias)
            with self.assertRaises(EcosystemError) as raised:
                store.read_blob(digest, maximum_bytes=100)
            self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")

    def test_full_cas_reuses_identical_object_but_rejects_new_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = test_store(Path(temporary), max_cas_bytes=4)
            digest, size = store.put_blob(
                io.BytesIO(b"full"), maximum_bytes=4, expected_size=4
            )
            self.assertEqual(
                store.put_blob(
                    io.BytesIO(b"full"),
                    maximum_bytes=4,
                    expected_sha256=digest,
                    expected_size=size,
                ),
                (digest, size),
            )
            with self.assertRaises(EcosystemError) as raised:
                store.put_blob(io.BytesIO(b"x"), maximum_bytes=1, expected_size=1)
            self.assertEqual(raised.exception.reason_code, "CAS_QUOTA_EXCEEDED")
            self.assertEqual(list((store.root / "tmp").iterdir()), [])

    def test_attempt_replay_with_different_terminal_result_conflicts_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            receipt, candidate_id = scout_receipt()
            bridge = bridge_scout_candidate(
                scout_receipt=receipt,
                candidate_id=candidate_id,
                source_key="github/openai/codex",
                requested_input_sha256="a" * 64,
                requested_input_size=1,
                policy=trusted,
            )
            store = test_store(base, policy=trusted, max_cas_bytes=1_000_000)
            attempt_base = _attempt_base(bridge.record(), trusted)
            first = _attempt_record(
                attempt_base,
                result="REJECTED_BEFORE_REVISION",
                tree_id=None,
                revision_id=None,
                reason_codes=["ARCHIVE_INVALID"],
            )
            conflicting = _attempt_record(
                attempt_base,
                result="INSUFFICIENT_BEFORE_REVISION",
                tree_id=None,
                revision_id=None,
                reason_codes=["RESOURCE_LIMIT_EXCEEDED"],
            )
            maximum = trusted.resource_limits["max_record_bytes"]
            _write_attempt(store, first, maximum)
            before = store.list_record_names(
                "intake-attempts/sha256/" + first["attempt_id"].split("/", 1)[1],
                maximum_count=2,
            )
            stored_path = (
                store.root
                / "intake-attempts"
                / "sha256"
                / first["attempt_id"].split("/", 1)[1]
                / (first["attempt_result_id"].split("/", 1)[1] + ".json")
            )
            first_bytes = stored_path.read_bytes()
            replay = _attempt_record(
                attempt_base,
                result="REJECTED_BEFORE_REVISION",
                tree_id=None,
                revision_id=None,
                reason_codes=["ARCHIVE_INVALID"],
            )
            self.assertEqual(replay["attempt_id"], first["attempt_id"])
            self.assertEqual(replay["attempt_result_id"], first["attempt_result_id"])
            _write_attempt(store, replay, maximum)
            self.assertEqual(
                store.list_record_names(
                    "intake-attempts/sha256/" + first["attempt_id"].split("/", 1)[1],
                    maximum_count=2,
                ),
                before,
            )
            self.assertEqual(stored_path.read_bytes(), first_bytes)
            with self.assertRaises(EcosystemError) as raised:
                _write_attempt(store, conflicting, maximum)
            self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")
            self.assertEqual(
                store.list_record_names(
                    "intake-attempts/sha256/" + first["attempt_id"].split("/", 1)[1],
                    maximum_count=2,
                ),
                before,
            )
            stored = store.read_record(
                "intake-attempts/sha256/"
                + first["attempt_id"].split("/", 1)[1]
                + "/"
                + first["attempt_result_id"].split("/", 1)[1]
                + ".json",
                maximum_bytes=maximum,
            )
            self.assertEqual(stored, first)

    def test_cas_root_filesystem_unc_link_identity_and_stale_lock_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            filesystem_root = Path(Path.cwd().anchor)
            with self.subTest(case="filesystem-root"), self.assertRaises(EcosystemError):
                _validate_external_root(filesystem_root, ROOT)
            with self.subTest(case="unc-network"), self.assertRaises(EcosystemError):
                _validate_external_root(Path(r"\\synthetic-server\share\nexus"), ROOT)

            real_root = base / "real-cas"
            real_root.mkdir()
            linked_root = base / "linked-cas"
            if os.name == "nt":
                from tests._windows_junction import create_junction

                create_junction(linked_root, real_root)
            else:
                os.symlink(real_root, linked_root, target_is_directory=True)
            with self.subTest(case="symlink-or-reparse-root"), self.assertRaises(EcosystemError):
                _open_test_quarantine_store(
                    linked_root, policy=trusted, max_cas_bytes=1_000_000
                )

            store = test_store(base, policy=trusted, name="identity-cas", max_cas_bytes=1_000_000)
            identity_function = "_win_identity" if os.name == "nt" else "_posix_directory_identity"
            synthetic_identity = (9_999, 9_999)
            with patch.object(ecosystem_storage, identity_function, return_value=synthetic_identity):
                with self.subTest(case="root-file-identity-mutation"), self.assertRaises(EcosystemError):
                    store.put_blob(io.BytesIO(b"identity"), maximum_bytes=100)

            stale = store.root / "locks" / "cas.lock"
            stale.write_bytes(b"\0")
            digest, size = store.put_blob(io.BytesIO(b"stale-lock-safe"), maximum_bytes=100)
            self.assertEqual(store.read_blob(digest, maximum_bytes=100), b"stale-lock-safe")
            self.assertEqual(size, len(b"stale-lock-safe"))

            forged_revision = {
                "schema_version": "nexus.ecosystem-revision.v1",
                "revision_id": typed_id("revision", {"cross-source": True}),
                "source_key": "github/bytedance/deer-flow",
                "source_id": typed_id("source", {"cross-source": True}),
            }
            locator = (
                "revisions/sha256/"
                + forged_revision["revision_id"].split("/", 1)[1]
                + ".json"
            )
            with self.subTest(case="cross-source-untrusted-publication"), self.assertRaises(EcosystemError):
                store._publish_record(
                    locator,
                    forged_revision,
                    maximum_bytes=1_000,
                    writer_token=object(),
                )
            self.assertFalse(store.root.joinpath(*locator.split("/")).exists())

    def test_concurrent_identical_writers_are_idempotent_and_store_has_no_gc_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            root = base / "cas"
            first = _open_test_quarantine_store(
                root, policy=trusted, max_cas_bytes=1_000_000
            )
            second = _open_test_quarantine_store(
                root, policy=trusted, max_cas_bytes=1_000_000
            )
            payload = b"concurrent immutable bytes"

            def write(store: QuarantineStore) -> tuple[str, int]:
                return store.put_blob(
                    io.BytesIO(payload), maximum_bytes=1_000_000, expected_size=len(payload)
                )

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(write, (first, second)))
            self.assertEqual(results[0], results[1])
            digest, size = results[0]
            self.assertEqual(size, len(payload))
            self.assertEqual(first.read_blob(digest, maximum_bytes=1_000_000), payload)
            self.assertEqual(list((root / "tmp").iterdir()), [])
            self.assertFalse(hasattr(first, "gc"))
            self.assertFalse(hasattr(first, "evict"))
            first.close()
            second.close()

            reopened = _open_test_quarantine_store(
                root, policy=trusted, max_cas_bytes=1_000_000
            )
            self.assertEqual(reopened.read_blob(digest, maximum_bytes=1_000_000), payload)
            reopened.close()

    def test_revision_capacity_accepts_eight_and_rejects_ninth(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            store = test_store(base, policy=trusted, max_cas_bytes=1_000_000)
            results = []
            for index in range(9):
                commit = f"{index + 1:040x}"
                raw = zip_bytes([("root/value.txt", f"revision-{index}".encode())])
                receipt, candidate_id = scout_receipt(commit=commit)
                bridge = bridge_scout_candidate(
                    scout_receipt=receipt,
                    candidate_id=candidate_id,
                    source_key="github/openai/codex",
                    requested_input_sha256=hashlib.sha256(raw).hexdigest(),
                    requested_input_size=len(raw),
                    policy=trusted,
                )
                archive = base / f"revision-{index}.zip"
                archive.write_bytes(raw)
                with open_stable_input(archive, maximum_bytes=1_000_000) as stable:
                    results.append(
                        intake_pre_supplied_zip(
                            bridge=bridge,
                            zip_input=stable,
                            policy=trusted,
                            store=store,
                        )
                    )
            self.assertTrue(
                all(item["attempt"]["result"] == "REVISION_CREATED" for item in results[:8])
            )
            self.assertEqual(results[8]["attempt"]["result"], "INSUFFICIENT_BEFORE_REVISION")
            self.assertEqual(results[8]["attempt"]["reason_codes"], ["RESOURCE_LIMIT_EXCEEDED"])

    def test_cas_root_rejects_repository_and_forged_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            with self.assertRaises(EcosystemError):
                _open_test_quarantine_store(
                    ROOT / "state" / "ecosystem", policy=trusted, max_cas_bytes=100
                )
            root = base / "cas"
            root.mkdir()
            (root / ".nexus-ecosystem-root.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(EcosystemError):
                _open_test_quarantine_store(root, policy=trusted, max_cas_bytes=100)

    @unittest.skipUnless(os.name == "nt", "Windows filesystem alias regression")
    def test_windows_short_and_long_repository_paths_are_the_same_boundary(self) -> None:
        buffer = ctypes.create_unicode_buffer(32_768)
        written = ctypes.windll.kernel32.GetShortPathNameW(
            str(ROOT), buffer, len(buffer)
        )
        if not written or written >= len(buffer) or buffer.value.casefold() == str(ROOT).casefold():
            # New test volumes/directories may have 8.3 name generation
            # disabled. Keep the regression deterministic instead of silently
            # dropping the alias assertion: model the filesystem's canonical
            # real-path answer for two textual names of the same directory.
            short_root = ROOT.parent / "NEXUS~1"
            short_prefix = os.path.abspath(short_root)
            long_prefix = os.path.abspath(ROOT)
            original_realpath = ecosystem_storage.os.path.realpath

            def canonical_alias(value: os.PathLike[str] | str) -> str:
                absolute = os.path.abspath(value)
                folded = os.path.normcase(absolute)
                short_folded = os.path.normcase(short_prefix)
                if folded == short_folded or folded.startswith(short_folded + os.sep):
                    return long_prefix + absolute[len(short_prefix):]
                return original_realpath(value)

            with patch.object(
                ecosystem_storage.os.path, "realpath", side_effect=canonical_alias
            ):
                self.assertTrue(_is_within(ROOT / "state" / "ecosystem", short_root))
                self.assertTrue(_is_within(short_root / "state" / "ecosystem", ROOT))
            return
        short_root = Path(buffer.value)
        self.assertTrue(_is_within(ROOT / "state" / "ecosystem", short_root))
        self.assertTrue(_is_within(short_root / "state" / "ecosystem", ROOT))

    def test_bridge_revalidates_scout_and_never_grants_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trusted = load_trusted_source_policy(root=policy_root(Path(temporary)))
            receipt, candidate_id = scout_receipt()
            bridge = bridge_scout_candidate(
                scout_receipt=receipt,
                candidate_id=candidate_id,
                source_key="github/openai/codex",
                requested_input_sha256="a" * 64,
                requested_input_size=123,
                policy=trusted,
            )
            record = bridge.record()
            self.assertTrue(bridge.accepted)
            self.assertEqual(record["bridge_result"], "QUARANTINE_REQUEST_ACCEPTED")
            self.assertEqual(record["authority"], zero_authority())
            forged = copy.deepcopy(receipt)
            forged["candidates"][0]["immutable_reference"]["value"] = "b" * 40
            with self.assertRaises(EcosystemError):
                bridge_scout_candidate(
                    scout_receipt=forged,
                    candidate_id=candidate_id,
                    source_key="github/openai/codex",
                    requested_input_sha256="a" * 64,
                    requested_input_size=123,
                    policy=trusted,
                )

    def test_bridge_dispositions_and_immutable_source_bindings_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trusted = load_trusted_source_policy(root=policy_root(Path(temporary)))
            for disposition in (
                "ADMITTED_FOR_REVIEW",
                "REFERENCE_ONLY",
                "QUARANTINED",
                "REJECTED",
                "INSUFFICIENT_EVIDENCE",
            ):
                with self.subTest(disposition=disposition):
                    receipt, candidate_id = scout_receipt(disposition=disposition)
                    bridge = bridge_scout_candidate(
                        scout_receipt=receipt,
                        candidate_id=candidate_id,
                        source_key="github/openai/codex",
                        requested_input_sha256="a" * 64,
                        requested_input_size=123,
                        policy=trusted,
                    )
                    self.assertEqual(
                        bridge.accepted,
                        disposition in {"ADMITTED_FOR_REVIEW", "REFERENCE_ONLY"},
                    )
                    self.assertEqual(bridge.record()["authority"], zero_authority())

            receipt, candidate_id = scout_receipt()
            invalid_cases = []
            for field, value in (
                ("kind", "branch"),
                ("verification_state", "mutable_or_missing"),
                ("value", "a" * 39),
            ):
                mutated = copy.deepcopy(receipt)
                mutated["candidates"][0]["immutable_reference"][field] = value
                invalid_cases.append((f"immutable-{field}", mutated, candidate_id, "github/openai/codex"))
            invalid_cases.extend(
                (
                    ("wrong-candidate", receipt, "candidate/not-present", "github/openai/codex"),
                    ("wrong-source", receipt, candidate_id, "github/bytedance/deer-flow"),
                )
            )
            for label, mutated, selected_id, source_key in invalid_cases:
                with self.subTest(label=label), self.assertRaises(EcosystemError):
                    bridge_scout_candidate(
                        scout_receipt=mutated,
                        candidate_id=selected_id,
                        source_key=source_key,
                        requested_input_sha256="a" * 64,
                        requested_input_size=123,
                        policy=trusted,
                    )

    def test_self_consistent_post_seal_bridge_rewrite_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trusted = load_trusted_source_policy(root=policy_root(Path(temporary)))
            receipt, candidate_id = scout_receipt()
            bridge = bridge_scout_candidate(
                scout_receipt=receipt,
                candidate_id=candidate_id,
                source_key="github/openai/codex",
                requested_input_sha256="a" * 64,
                requested_input_size=123,
                policy=trusted,
            )
            bridge._record["requested_input_size"] = 124
            body = {
                key: value
                for key, value in bridge._record.items()
                if key not in {"schema_version", "bridge_id"}
            }
            bridge._record["bridge_id"] = typed_id("bridge", body)
            with self.assertRaises(EcosystemError) as raised:
                bridge.record()
            self.assertEqual(raised.exception.reason_code, "SCOUT_RECEIPT_INVALID")

    def test_blocked_scout_disposition_cannot_start_intake(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trusted = load_trusted_source_policy(root=policy_root(Path(temporary)))
            receipt, candidate_id = scout_receipt(disposition="REJECTED")
            bridge = bridge_scout_candidate(
                scout_receipt=receipt,
                candidate_id=candidate_id,
                source_key="github/openai/codex",
                requested_input_sha256="a" * 64,
                requested_input_size=1,
                policy=trusted,
            )
            self.assertFalse(bridge.accepted)
            self.assertEqual(bridge.record()["reason_codes"], ["SCOUT_DISPOSITION_BLOCKED"])

    def test_legacy_update_observations_never_become_bridge_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            store = test_store(base, policy=trusted, max_cas_bytes=1_000_000)
            _receipt, candidate_id = scout_receipt()
            observations = {
                "valid-looking-legacy-observation": {
                    "repository": "openai/codex",
                    "branch": "main",
                    "sha": COMMIT,
                    "checked_at": "2026-08-28T00:00:00Z",
                },
                "legacy-network-failure": {
                    "repository": "openai/codex",
                    "branch": "main",
                    "sha": None,
                    "error": "synthetic offline failure",
                },
                "malformed-legacy-sha": {
                    "repository": "openai/codex",
                    "branch": "main",
                    "sha": "not-a-commit",
                },
                "malformed-legacy-source": {
                    "repository": "../private",
                    "branch": "main",
                    "sha": COMMIT,
                },
                "tampered-legacy-observation": {
                    "repository": "bytedance/deer-flow",
                    "branch": "main",
                    "sha": COMMIT,
                },
                "unknown-future-schema": {
                    "schema_version": "nexus.upstream-observation.v99",
                    "repository": "openai/codex",
                    "branch": "main",
                    "sha": COMMIT,
                },
            }
            def record_snapshot() -> tuple[str, ...]:
                return tuple(
                    sorted(
                        path.relative_to(store.root).as_posix()
                        for path in store.root.rglob("*.json")
                    )
                )

            before = record_snapshot()
            for case, observation in observations.items():
                with self.subTest(case=case), self.assertRaises(EcosystemError):
                    bridge_scout_candidate(
                        scout_receipt=observation,
                        candidate_id=candidate_id,
                        source_key="github/openai/codex",
                        requested_input_sha256="a" * 64,
                        requested_input_size=1,
                        policy=trusted,
                    )
            self.assertEqual(record_snapshot(), before)


class ZipIntakeTests(unittest.TestCase):
    def _context(self, raw: bytes) -> tuple[object, object, Path, QuarantineStore]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        trusted = load_trusted_source_policy(root=policy_root(base))
        receipt, candidate_id = scout_receipt()
        bridge = bridge_scout_candidate(
            scout_receipt=receipt,
            candidate_id=candidate_id,
            source_key="github/openai/codex",
            requested_input_sha256=hashlib.sha256(raw).hexdigest(),
            requested_input_size=len(raw),
            policy=trusted,
        )
        archive = base / "synthetic.zip"
        archive.write_bytes(raw)
        store = test_store(
            base, policy=trusted, max_cas_bytes=8 * 1024 * 1024
        )
        return trusted, bridge, archive, store

    def _run_with_store(self, raw: bytes) -> tuple[dict, QuarantineStore]:
        trusted, bridge, archive, store = self._context(raw)
        with open_stable_input(archive, maximum_bytes=1024 * 1024) as stable:
            result = intake_pre_supplied_zip(
                bridge=bridge, zip_input=stable, policy=trusted, store=store
            )
        return result, store

    def _run(self, raw: bytes) -> dict:
        return self._run_with_store(raw)[0]

    def test_valid_zip_streams_inert_files_and_creates_quarantined_revision(self) -> None:
        raw = zip_bytes(
            [
                ("synthetic-root/docs/README.md", b"Synthetic architecture text."),
                ("synthetic-root/data/value.json", b'{"value":1}\n'),
            ]
        )
        result = self._run(raw)
        self.assertEqual(result["attempt"]["result"], "REVISION_CREATED")
        self.assertTrue(result["revision"]["revision_id"].startswith("revision/"))
        self.assertEqual(result["state"]["state"]["disposition"], "QUARANTINED")
        self.assertEqual(result["state"]["authority"], zero_authority())
        self.assertEqual([item["path"] for item in result["tree"]["entries"]], ["data/value.json", "docs/README.md"])

    def test_observed_force_push_creates_a_new_quarantined_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            store = test_store(base, policy=trusted, max_cas_bytes=4 * 1024 * 1024)

            def intake(raw: bytes, commit: str, name: str) -> dict:
                receipt, candidate_id = scout_receipt(commit=commit)
                bridge = bridge_scout_candidate(
                    scout_receipt=receipt,
                    candidate_id=candidate_id,
                    source_key="github/openai/codex",
                    requested_input_sha256=hashlib.sha256(raw).hexdigest(),
                    requested_input_size=len(raw),
                    policy=trusted,
                )
                archive = base / name
                archive.write_bytes(raw)
                with open_stable_input(archive, maximum_bytes=1_000_000) as stable:
                    return intake_pre_supplied_zip(
                        bridge=bridge,
                        zip_input=stable,
                        policy=trusted,
                        store=store,
                    )

            prior = intake(
                zip_bytes([("root/README.md", b"prior observed bytes")]),
                "a" * 40,
                "prior.zip",
            )
            rewritten = intake(
                zip_bytes([("root/README.md", b"force-pushed observed bytes")]),
                "b" * 40,
                "rewritten.zip",
            )
            self.assertNotEqual(
                prior["revision"]["revision_id"], rewritten["revision"]["revision_id"]
            )
            self.assertNotEqual(prior["tree"]["tree_id"], rewritten["tree"]["tree_id"])
            for result in (prior, rewritten):
                self.assertEqual(result["state"]["state"]["disposition"], "QUARANTINED")
                self.assertEqual(result["state"]["authority"], zero_authority())

    def test_bridge_requested_digest_and_size_must_match_the_stable_zip(self) -> None:
        raw = zip_bytes([("root/a.txt", b"a")])
        for digest, size in (("0" * 64, len(raw)), (hashlib.sha256(raw).hexdigest(), len(raw) + 1)):
            with self.subTest(digest=digest[:8], size=size), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary)
                trusted = load_trusted_source_policy(root=policy_root(base))
                receipt, candidate_id = scout_receipt()
                bridge = bridge_scout_candidate(
                    scout_receipt=receipt,
                    candidate_id=candidate_id,
                    source_key="github/openai/codex",
                    requested_input_sha256=digest,
                    requested_input_size=size,
                    policy=trusted,
                )
                archive = base / "candidate.zip"
                archive.write_bytes(raw)
                store = test_store(
                    base, policy=trusted, max_cas_bytes=1_000_000
                )
                with open_stable_input(archive, maximum_bytes=1_000_000) as stable:
                    with self.assertRaises(EcosystemError) as raised:
                        intake_pre_supplied_zip(
                            bridge=bridge, zip_input=stable, policy=trusted, store=store
                        )
                self.assertEqual(raised.exception.reason_code, "INPUT_DIGEST_MISMATCH")
                self.assertEqual(list((store.root / "tmp").iterdir()), [])
                self.assertEqual(list((store.root / "incoming").iterdir()), [])

    def test_structural_path_attacks_reject_before_revision(self) -> None:
        for path in (
            "synthetic-root/../escape.txt",
            "synthetic-root/C:/ads.txt",
            "synthetic-root/CON.txt",
            "synthetic-root/dir/name:stream",
        ):
            with self.subTest(path=path):
                result = self._run(zip_bytes([(path, b"x")]))
                self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
                self.assertIsNone(result["attempt"]["tree_id"])
                self.assertIsNone(result["attempt"]["revision_id"])

    def test_case_and_unicode_normalization_collisions_reject(self) -> None:
        cases = (
            [("root/A.txt", b"a"), ("root/a.txt", b"b")],
            [("root/caf\u00e9.txt", b"a"), ("root/cafe\u0301.txt", b"b")],
        )
        for entries in cases:
            with self.subTest(entries=entries):
                result = self._run(zip_bytes(entries))
                self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
                self.assertIn("PATH_COLLISION", result["attempt"]["reason_codes"])

    def test_member_inventory_rejects_unindexed_bytes_and_file_ancestors(self) -> None:
        raw = zip_bytes([("root/a.txt", b"a"), ("root/b.txt", b"b")])
        first_end = raw.find(b"PK\x03\x04", 4)
        self.assertGreater(first_end, 0)
        with_gap = raw[:first_end] + b"hidden" + raw[first_end:]
        central_offset = with_gap.find(b"PK\x01\x02")
        eocd_offset = with_gap.rfind(b"PK\x05\x06")
        mutated = bytearray(with_gap)
        # Repair the central local offsets and EOCD central offset so the only
        # remaining defect is the unindexed gap in the local-record region.
        cursor = central_offset
        for index in range(2):
            name_length = int.from_bytes(mutated[cursor + 28 : cursor + 30], "little")
            extra_length = int.from_bytes(mutated[cursor + 30 : cursor + 32], "little")
            comment_length = int.from_bytes(mutated[cursor + 32 : cursor + 34], "little")
            if index == 1:
                offset = int.from_bytes(mutated[cursor + 42 : cursor + 46], "little")
                mutated[cursor + 42 : cursor + 46] = (offset + 6).to_bytes(4, "little")
            cursor += 46 + name_length + extra_length + comment_length
        mutated[eocd_offset + 16 : eocd_offset + 20] = central_offset.to_bytes(4, "little")
        result = self._run(bytes(mutated))
        self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
        self.assertEqual(result["attempt"]["reason_codes"], ["ARCHIVE_INTEGRITY_INVALID"])

        result = self._run(zip_bytes([("root/a", b"file"), ("root/a/b.txt", b"child")]))
        self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
        self.assertEqual(result["attempt"]["reason_codes"], ["PATH_COLLISION"])

    def test_directory_attribute_must_match_member_name(self) -> None:
        raw = bytearray(zip_bytes([("root/a.txt", b"a")]))
        central_offset = raw.find(b"PK\x01\x02")
        self.assertGreater(central_offset, 0)
        attributes = int.from_bytes(raw[central_offset + 38 : central_offset + 42], "little")
        raw[central_offset + 38 : central_offset + 42] = (attributes | 0x10).to_bytes(4, "little")
        result = self._run(bytes(raw))
        self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
        self.assertEqual(result["attempt"]["reason_codes"], ["ARCHIVE_UNSAFE_ENTRY"])

    def test_directory_limit_counts_implicit_parent_directories(self) -> None:
        limits = copy.deepcopy(json.loads(POLICY_RAW)["resource_limits"])
        limits["max_directories"] = 1
        raw = zip_bytes([("root/one/x.txt", b"x"), ("root/two/y.txt", b"y")])
        with self.assertRaises(EcosystemError) as raised:
            _inventory_zip(raw, limits)
        self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")

    def test_archive_entry_file_aggregate_and_ratio_limit_boundaries(self) -> None:
        canonical_limits = copy.deepcopy(json.loads(POLICY_RAW)["resource_limits"])

        two_entries = zip_bytes(
            [("root/a.txt", b"aa"), ("root/b.txt", b"bb")],
            compression=zipfile.ZIP_STORED,
        )
        exact_entries = {**canonical_limits, "max_entries": 2}
        self.assertEqual(len(_inventory_zip(two_entries, exact_entries)[1]), 2)
        with self.subTest(case="entry-count-plus-one"), self.assertRaises(EcosystemError):
            _inventory_zip(two_entries, {**canonical_limits, "max_entries": 1})

        one_file = zip_bytes([("root/a.txt", b"abcd")], compression=zipfile.ZIP_STORED)
        self.assertEqual(
            _inventory_zip(
                one_file,
                {**canonical_limits, "max_file_bytes": 4, "max_expanded_bytes": 4},
            )[1][0].expanded_size,
            4,
        )
        for case, limits in (
            ("per-file-plus-one", {**canonical_limits, "max_file_bytes": 3}),
            ("aggregate-expanded-plus-one", {**canonical_limits, "max_expanded_bytes": 3}),
        ):
            with self.subTest(case=case), self.assertRaises(EcosystemError) as raised:
                _inventory_zip(one_file, limits)
            self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")

        ratio_one = {**canonical_limits, "max_aggregate_compression_ratio": 1}
        self.assertEqual(len(_inventory_zip(one_file, ratio_one)[1]), 1)
        entry_ratio_one = {
            **canonical_limits,
            "max_entry_compression_ratio": 1,
            "max_aggregate_compression_ratio": 100,
        }
        self.assertEqual(len(_inventory_zip(one_file, entry_ratio_one)[1]), 1)
        with self.subTest(case="per-entry-ratio-plus-one"), self.assertRaises(EcosystemError) as raised:
            _inventory_zip(
                one_file,
                {**entry_ratio_one, "max_entry_compression_ratio": 0},
            )
        self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")
        with self.subTest(case="aggregate-ratio-plus-one"), self.assertRaises(EcosystemError) as raised:
            _inventory_zip(
                one_file,
                {**canonical_limits, "max_aggregate_compression_ratio": 0},
            )
        self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")

    def test_declared_size_overlap_and_exact_duplicate_member_matrix(self) -> None:
        ordinary = bytearray(
            zip_bytes([("root/a.txt", b"a")], compression=zipfile.ZIP_STORED)
        )
        central = ordinary.find(b"PK\x01\x02")
        # Keep local and central headers self-consistent while lying about the
        # expanded size. Streaming must still detect the actual byte count.
        ordinary[22:26] = (2).to_bytes(4, "little")
        ordinary[central + 24 : central + 28] = (2).to_bytes(4, "little")
        lied = self._run(bytes(ordinary))
        self.assertNotEqual(lied["attempt"]["result"], "REVISION_CREATED")
        self.assertIsNone(lied["attempt"]["revision_id"])

        overlap = bytearray(
            zip_bytes(
                [("root/a.txt", b"a"), ("root/b.txt", b"b")],
                compression=zipfile.ZIP_STORED,
            )
        )
        first_central = overlap.find(b"PK\x01\x02")
        first_name_length = int.from_bytes(overlap[first_central + 28 : first_central + 30], "little")
        first_extra_length = int.from_bytes(overlap[first_central + 30 : first_central + 32], "little")
        first_comment_length = int.from_bytes(overlap[first_central + 32 : first_central + 34], "little")
        second_central = first_central + 46 + first_name_length + first_extra_length + first_comment_length
        overlap[second_central + 42 : second_central + 46] = (0).to_bytes(4, "little")
        overlapped = self._run(bytes(overlap))
        self.assertNotEqual(overlapped["attempt"]["result"], "REVISION_CREATED")
        self.assertIsNone(overlapped["attempt"]["revision_id"])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            duplicate = zip_bytes(
                [("root/a.txt", b"first"), ("root/a.txt", b"second")],
                compression=zipfile.ZIP_STORED,
            )
        duplicated = self._run(duplicate)
        self.assertNotEqual(duplicated["attempt"]["result"], "REVISION_CREATED")
        self.assertIn("PATH_COLLISION", duplicated["attempt"]["reason_codes"])

    def test_inventory_deadline_is_bounded_before_archive_scanning(self) -> None:
        limits = copy.deepcopy(json.loads(POLICY_RAW)["resource_limits"])
        raw = zip_bytes([("root/a.txt", b"a")])
        with self.assertRaises(EcosystemError) as raised:
            _inventory_zip(raw, limits, deadline=1.0, _clock=lambda: 2.0)
        self.assertEqual(raised.exception.reason_code, "TIME_LIMIT_EXCEEDED")

    def test_same_source_commit_cannot_bind_different_zip_or_tree(self) -> None:
        first_raw = zip_bytes([("root/a.txt", b"first")])
        second_raw = zip_bytes([("root/a.txt", b"second")])
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            receipt, candidate_id = scout_receipt()
            store = test_store(
                base, policy=trusted, max_cas_bytes=8 * 1024 * 1024
            )

            def intake(raw: bytes, name: str) -> dict:
                bridge = bridge_scout_candidate(
                    scout_receipt=receipt,
                    candidate_id=candidate_id,
                    source_key="github/openai/codex",
                    requested_input_sha256=hashlib.sha256(raw).hexdigest(),
                    requested_input_size=len(raw),
                    policy=trusted,
                )
                archive = base / name
                archive.write_bytes(raw)
                with open_stable_input(archive, maximum_bytes=1024 * 1024) as stable:
                    return intake_pre_supplied_zip(
                        bridge=bridge, zip_input=stable, policy=trusted, store=store
                    )

            first = intake(first_raw, "first.zip")
            second = intake(second_raw, "second.zip")
            self.assertEqual(first["attempt"]["result"], "REVISION_CREATED")
            self.assertEqual(second["attempt"]["result"], "INSUFFICIENT_BEFORE_REVISION")
            self.assertEqual(second["attempt"]["reason_codes"], ["PROVENANCE_CONFLICT"])
            self.assertIsNone(second["tree"])
            self.assertIsNone(second["revision"])
            self.assertEqual(
                len(store.list_record_names("revisions/sha256", maximum_count=8)), 1
            )
            self.assertEqual(
                len(store.list_record_names("quarantine", maximum_count=8)), 1
            )

    def test_symlink_member_rejects_without_materialization(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", allowZip64=False) as archive:
            info = zipfile.ZipInfo("root/link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, b"../../outside")
        result = self._run(buffer.getvalue())
        self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
        self.assertEqual(result["attempt"]["reason_codes"], ["ARCHIVE_UNSAFE_ENTRY"])

    def test_all_zip_link_and_special_member_modes_reject_before_revision(self) -> None:
        special_modes = (
            stat.S_IFLNK,
            stat.S_IFCHR,
            stat.S_IFBLK,
            stat.S_IFIFO,
            stat.S_IFSOCK,
        )
        for special_mode in special_modes:
            with self.subTest(special_mode=special_mode):
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", allowZip64=False) as archive:
                    info = zipfile.ZipInfo("root/special")
                    info.create_system = 3
                    info.external_attr = (special_mode | 0o777) << 16
                    archive.writestr(info, b"inert")
                result = self._run(buffer.getvalue())
                self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
                self.assertEqual(result["attempt"]["reason_codes"], ["ARCHIVE_UNSAFE_ENTRY"])
                self.assertIsNone(result["tree"])

    def test_hardlink_gitlink_reparse_and_sparse_entries_reject_before_revision(self) -> None:
        cases: list[tuple[str, zipfile.ZipInfo, str, str]] = []

        hardlink = zipfile.ZipInfo("root/hardlink")
        hardlink.extra = struct.pack("<HH", 0x756E, 4) + b"link"
        cases.append(
            (
                "hardlink-extra",
                hardlink,
                "INSUFFICIENT_BEFORE_REVISION",
                "UNSUPPORTED_INPUT",
            )
        )

        gitlink = zipfile.ZipInfo("root/submodule")
        gitlink.create_system = 3
        gitlink.external_attr = (0o160000 | 0o755) << 16
        cases.append(
            ("gitlink-submodule", gitlink, "REJECTED_BEFORE_REVISION", "ARCHIVE_UNSAFE_ENTRY")
        )

        sparse = zipfile.ZipInfo("root/sparse")
        sparse.create_system = 0
        sparse.external_attr = 0x0200
        cases.append(("windows-sparse", sparse, "REJECTED_BEFORE_REVISION", "ARCHIVE_UNSAFE_ENTRY"))

        reparse = zipfile.ZipInfo("root/reparse")
        reparse.create_system = 0
        reparse.external_attr = 0x0400
        cases.append(
            ("windows-reparse", reparse, "REJECTED_BEFORE_REVISION", "ARCHIVE_UNSAFE_ENTRY")
        )

        for case, info, terminal_result, reason in cases:
            with self.subTest(case=case):
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", allowZip64=False) as archive:
                    archive.writestr(info, b"inert")
                result = self._run(buffer.getvalue())
                self.assertEqual(result["attempt"]["result"], terminal_result)
                self.assertEqual(result["attempt"]["reason_codes"], [reason])
                self.assertIsNone(result["tree"])
                self.assertIsNone(result["revision"])

    def test_executable_and_lfs_pointer_bytes_remain_inert_cas_objects(self) -> None:
        buffer = io.BytesIO()
        lfs = b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 1\n"
        with zipfile.ZipFile(buffer, "w", allowZip64=False) as archive:
            executable = zipfile.ZipInfo("root/tool.sh")
            executable.create_system = 3
            executable.external_attr = (stat.S_IFREG | 0o755) << 16
            archive.writestr(executable, b"#!/bin/sh\nexit 0\n")
            archive.writestr("root/asset.bin", lfs)
        result, store = self._run_with_store(buffer.getvalue())
        entries = {entry["path"]: entry for entry in result["tree"]["entries"]}
        self.assertEqual(entries["tool.sh"]["mode"], "regular_executable")
        self.assertEqual(entries["asset.bin"]["mode"], "regular_non_executable")
        self.assertEqual(store.read_blob(entries["asset.bin"]["sha256"], maximum_bytes=1_000), lfs)
        for entry in entries.values():
            object_mode = stat.S_IMODE(store._object_path(entry["sha256"]).stat().st_mode)
            self.assertEqual(object_mode & 0o111, 0)

    def test_malformed_and_multi_root_archives_fail_closed(self) -> None:
        for raw in (
            b"not-a-zip",
            zip_bytes([("one/a.txt", b"a"), ("two/b.txt", b"b")]),
        ):
            with self.subTest(raw=raw[:20]):
                result = self._run(raw)
                self.assertEqual(result["attempt"]["result"], "REJECTED_BEFORE_REVISION")
                self.assertIsNone(result["tree"])

    def test_archive_format_feature_matrix_fails_closed_without_residue(self) -> None:
        ordinary = zip_bytes([("root/a.txt", b"a")])

        encrypted = bytearray(ordinary)
        central = encrypted.find(b"PK\x01\x02")
        encrypted[central + 8 : central + 10] = (
            int.from_bytes(encrypted[central + 8 : central + 10], "little") | 1
        ).to_bytes(2, "little")

        unsupported_method = bytearray(ordinary)
        central = unsupported_method.find(b"PK\x01\x02")
        unsupported_method[central + 10 : central + 12] = (12).to_bytes(2, "little")

        split = bytearray(ordinary)
        eocd = split.rfind(b"PK\x05\x06")
        split[eocd + 4 : eocd + 6] = (1).to_bytes(2, "little")

        crc_lie = bytearray(ordinary)
        central = crc_lie.find(b"PK\x01\x02")
        crc_lie[central + 16 : central + 20] = (0).to_bytes(4, "little")

        empty_buffer = io.BytesIO()
        with zipfile.ZipFile(empty_buffer, "w", allowZip64=False):
            pass

        cases = (
            ("gzip", b"\x1f\x8bsynthetic"),
            ("tar", (b"x" * 257) + b"ustar" + b"synthetic"),
            ("self-extracting", b"MZ" + ordinary),
            ("empty", empty_buffer.getvalue()),
            ("encrypted", bytes(encrypted)),
            ("unsupported-method", bytes(unsupported_method)),
            ("split", bytes(split)),
            ("crc-lie", bytes(crc_lie)),
        )
        for label, raw in cases:
            with self.subTest(label=label):
                result, store = self._run_with_store(raw)
                self.assertNotEqual(result["attempt"]["result"], "REVISION_CREATED")
                self.assertIsNone(result["tree"])
                self.assertIsNone(result["revision"])
                self.assertEqual(list((store.root / "tmp").iterdir()), [])
                self.assertEqual(list((store.root / "incoming").iterdir()), [])

    def test_stored_deflated_order_and_timestamp_are_deterministic_tree_inputs(self) -> None:
        for compression in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            with self.subTest(compression=compression):
                result = self._run(
                    zip_bytes(
                        [("root/b.txt", b"b"), ("root/a.txt", b"a")],
                        compression=compression,
                    )
                )
                self.assertEqual(result["attempt"]["result"], "REVISION_CREATED")
                self.assertEqual(
                    [entry["path"] for entry in result["tree"]["entries"]],
                    ["a.txt", "b.txt"],
                )

        def timestamped(year: int) -> bytes:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
                info = zipfile.ZipInfo("root/a.txt", date_time=(year, 1, 1, 0, 0, 0))
                archive.writestr(info, b"same")
            return buffer.getvalue()

        first = self._run(timestamped(2020))
        second = self._run(timestamped(2021))
        self.assertEqual(first["tree"]["tree_id"], second["tree"]["tree_id"])
        self.assertNotEqual(first["revision"]["revision_id"], second["revision"]["revision_id"])

    def test_failing_intake_paths_leave_no_tmp_or_incoming_residue(self) -> None:
        cases = (
            b"not-a-zip",
            zip_bytes([("root/../escape.txt", b"x")]),
            zip_bytes([("root/zeros.bin", b"0" * 100_000)]),
        )
        for raw in cases:
            with self.subTest(raw=raw[:20]):
                result, store = self._run_with_store(raw)
                self.assertNotEqual(result["attempt"]["result"], "REVISION_CREATED")
                self.assertEqual(list((store.root / "tmp").iterdir()), [])
                self.assertEqual(list((store.root / "incoming").iterdir()), [])

    def test_compression_ratio_exhaustion_is_insufficient_not_pass(self) -> None:
        raw = zip_bytes([("root/zeros.bin", b"0" * 100_000)])
        result = self._run(raw)
        self.assertEqual(result["attempt"]["result"], "INSUFFICIENT_BEFORE_REVISION")
        self.assertEqual(result["attempt"]["reason_codes"], ["RESOURCE_LIMIT_EXCEEDED"])

    def test_nested_archive_markers_remain_inert_and_are_not_outer_zip64_metadata(self) -> None:
        nested = b"PK\x03\x04synthetic-inert-memberPK\x06\x06not-an-outer-record"
        result = self._run(zip_bytes([("root/nested.zip", nested)]))
        self.assertEqual(result["attempt"]["result"], "REVISION_CREATED")
        self.assertEqual(result["tree"]["entries"][0]["kind"], "archive")
        self.assertEqual(result["tree"]["entries"][0]["size"], len(nested))

        exact_tar_magic = (b"x" * 257) + b"ustar"
        tar_result = self._run(
            zip_bytes([("root/archive.tar", exact_tar_magic)], compression=zipfile.ZIP_STORED)
        )
        self.assertEqual(tar_result["attempt"]["result"], "REVISION_CREATED")
        self.assertEqual(tar_result["tree"]["entries"][0]["kind"], "archive")

        outer_zip64 = bytearray(zip_bytes([("root/file.txt", b"inert")]))
        eocd = outer_zip64.rfind(b"PK\x05\x06")
        outer_zip64[eocd + 8 : eocd + 12] = b"\xff\xff\xff\xff"
        rejected = self._run(bytes(outer_zip64))
        self.assertEqual(rejected["attempt"]["result"], "REJECTED_BEFORE_REVISION")
        self.assertEqual(rejected["attempt"]["reason_codes"], ["ARCHIVE_INVALID"])

    def test_production_interface_rejects_unsealed_file_like_input(self) -> None:
        raw = zip_bytes([("root/a.txt", b"a")])
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            receipt, candidate_id = scout_receipt()
            bridge = bridge_scout_candidate(
                scout_receipt=receipt,
                candidate_id=candidate_id,
                source_key="github/openai/codex",
                requested_input_sha256=hashlib.sha256(raw).hexdigest(),
                requested_input_size=len(raw),
                policy=trusted,
            )
            store = test_store(
                base, policy=trusted, max_cas_bytes=1_000_000
            )
            with self.assertRaises(EcosystemError) as raised:
                intake_pre_supplied_zip(
                    bridge=bridge, zip_input=io.BytesIO(raw), policy=trusted, store=store  # type: ignore[arg-type]
                )
            self.assertEqual(raised.exception.reason_code, "UNSUPPORTED_INPUT")

    def test_production_interface_rejects_every_non_stable_zip_shape(self) -> None:
        raw = zip_bytes([("root/a.txt", b"a")])
        trusted, bridge, archive, store = self._context(raw)
        rejected_shapes = {
            "directory": archive.parent,
            "caller-tree-manifest": {"entries": []},
            "member-list": [("root/a.txt", b"a")],
            "extracted-path": archive.parent / "root" / "a.txt",
            "git-checkout-worktree": {"worktree": str(archive.parent)},
            "url": "https://example.invalid/candidate.zip",
            "repository-object": {"repository": "openai/codex"},
            "generic-archive": io.BytesIO(raw),
            "caller-iterator": iter([raw]),
        }
        for case, candidate in rejected_shapes.items():
            with self.subTest(case=case), self.assertRaises(EcosystemError) as raised:
                intake_pre_supplied_zip(
                    bridge=bridge,
                    zip_input=candidate,  # type: ignore[arg-type]
                    policy=trusted,
                    store=store,
                )
            self.assertEqual(raised.exception.reason_code, "UNSUPPORTED_INPUT")
        with self.subTest(case="test-mode-cannot-widen"), self.assertRaises(TypeError):
            intake_pre_supplied_zip(
                bridge=bridge,
                zip_input=archive,  # type: ignore[arg-type]
                policy=trusted,
                store=store,
                test_mode=True,  # type: ignore[call-arg]
            )

    def test_production_interface_rejects_zip_magic_extension_mismatch(self) -> None:
        raw = zip_bytes([("root/a.txt", b"a")])
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trusted = load_trusted_source_policy(root=policy_root(base))
            receipt, candidate_id = scout_receipt()
            bridge = bridge_scout_candidate(
                scout_receipt=receipt,
                candidate_id=candidate_id,
                source_key="github/openai/codex",
                requested_input_sha256=hashlib.sha256(raw).hexdigest(),
                requested_input_size=len(raw),
                policy=trusted,
            )
            archive = base / "candidate.tar"
            archive.write_bytes(raw)
            store = test_store(
                base, policy=trusted, max_cas_bytes=1_000_000
            )
            with open_stable_input(archive, maximum_bytes=1_000_000) as stable:
                with self.assertRaises(EcosystemError) as raised:
                    intake_pre_supplied_zip(
                        bridge=bridge, zip_input=stable, policy=trusted, store=store
                    )
            self.assertEqual(raised.exception.reason_code, "UNSUPPORTED_INPUT")
            self.assertEqual(list((store.root / "tmp").iterdir()), [])
            self.assertEqual(list((store.root / "incoming").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
