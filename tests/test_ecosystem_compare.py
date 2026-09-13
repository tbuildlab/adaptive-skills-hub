from __future__ import annotations

import copy
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

from ash.ecosystem_bridge import bridge_scout_candidate
from ash.ecosystem_compare import (
    _SECURITY_CODES,
    _canonical_objects,
    _path_security_codes,
    compare_revisions,
    load_revision_comparison,
    persist_revision_comparison,
    validate_revision_comparison,
)
from ash.ecosystem_evidence import (
    build_provenance_evidence,
    classify_components,
    inspect_license_evidence,
)
from ash.ecosystem_intake import intake_pre_supplied_zip
from ash.ecosystem_models import (
    EcosystemError,
    typed_id,
    zero_authority,
)
from ash.ecosystem_policy import _load_test_source_policy as load_trusted_source_policy
from ash.ecosystem_storage import QuarantineStore, open_stable_input
from tests.test_ecosystem_storage_intake import policy_root, scout_receipt, test_store


ROOT = Path(__file__).resolve().parents[1]


class EcosystemComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.policy = load_trusted_source_policy(root=policy_root(base))
        self.base = base
        self.store = test_store(
            base,
            policy=self.policy,
            name="comparison-store",
            max_cas_bytes=64 * 1024 * 1024,
        )

    def _revision(
        self,
        entries: list[dict[str, object]],
        *,
        commit: str,
        source_key: str = "github/openai/codex",
    ) -> tuple[dict, dict, dict]:
        raw_stream = io.BytesIO()
        with zipfile.ZipFile(
            raw_stream, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=False
        ) as archive:
            for entry in entries:
                raw = entry["raw"]
                self.assertIs(type(raw), bytes)
                info = zipfile.ZipInfo(f"root/{entry['path']}")
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                executable = entry.get("mode") == "regular_executable"
                info.external_attr = (0o100755 if executable else 0o100644) << 16
                archive.writestr(info, raw)
        raw_zip = raw_stream.getvalue()
        repository = source_key.removeprefix("github/")
        receipt, candidate_id = scout_receipt(repository=repository, commit=commit)
        bridge = bridge_scout_candidate(
            scout_receipt=receipt,
            candidate_id=candidate_id,
            source_key=source_key,
            requested_input_sha256=hashlib.sha256(raw_zip).hexdigest(),
            requested_input_size=len(raw_zip),
            policy=self.policy,
        )
        archive_path = self.base / f"{commit}-{hashlib.sha256(raw_zip).hexdigest()[:8]}.zip"
        archive_path.write_bytes(raw_zip)
        with open_stable_input(archive_path, maximum_bytes=2 * 1024 * 1024) as stable:
            intake = intake_pre_supplied_zip(
                bridge=bridge,
                zip_input=stable,
                policy=self.policy,
                store=self.store,
            )
        self.assertEqual(intake["attempt"]["result"], "REVISION_CREATED")
        return intake["revision"], intake["tree"], intake["attempt"]

    def _inputs(
        self,
        old: tuple[dict, dict, dict],
        new: tuple[dict, dict, dict],
        *,
        complete_evidence: bool = True,
        **extra: object,
    ) -> dict:
        inputs = {
            "old_revision": old[0],
            "new_revision": new[0],
            "old_tree": old[1],
            "new_tree": new[1],
            "store": self.store,
            "policy": self.policy,
        }
        if complete_evidence:
            for prefix, value in (("old", old), ("new", new)):
                components, classifications, report = classify_components(
                    revision=value[0], tree=value[1], store=self.store, policy=self.policy
                )
                inputs[f"{prefix}_components"] = components
                inputs[f"{prefix}_classifications"] = classifications
                inputs[f"{prefix}_classification_report"] = report
                inputs[f"{prefix}_intake_attempt"] = value[2]
                inputs[f"{prefix}_provenance_evidence"] = build_provenance_evidence(
                    revision=value[0],
                    tree=value[1],
                    intake_attempt=value[2],
                    store=self.store,
                    policy=self.policy,
                )
                inputs[f"{prefix}_license_evidence"] = inspect_license_evidence(
                    subject_id=value[0]["revision_id"],
                    subject_record=value[0],
                    tree=value[1],
                    store=self.store,
                    policy=self.policy,
                )
        inputs.update(extra)
        return inputs

    def test_no_change_is_deterministic_zero_authority_and_revalidated(self) -> None:
        revision = self._revision(
            [{"path": "README.md", "raw": b"inert reference"}], commit="a" * 40
        )
        inputs = self._inputs(revision, revision)
        comparison = compare_revisions(**inputs)
        self.assertEqual(comparison["comparison_result"], "NO_TREE_CHANGE")
        self.assertEqual(comparison["ancestry_state"], "SAME")
        self.assertEqual(comparison["security_change_codes"], [])
        self.assertEqual(comparison["authority"], zero_authority())
        self.assertEqual(validate_revision_comparison(comparison, **inputs), comparison)
        for _index in range(100):
            self.assertEqual(compare_revisions(**inputs), comparison)

    def test_comparison_persistence_is_immutable_idempotent_and_revalidated(self) -> None:
        revision = self._revision(
            [{"path": "README.md", "raw": b"persisted inert reference"}],
            commit="9" * 40,
        )
        inputs = self._inputs(revision, revision)
        comparison = compare_revisions(**inputs)
        self.assertEqual(persist_revision_comparison(comparison, **inputs), comparison)
        self.assertEqual(persist_revision_comparison(comparison, **inputs), comparison)
        self.assertEqual(
            load_revision_comparison(comparison["comparison_id"], **inputs), comparison
        )
        names = self.store.list_record_names("comparisons/sha256", maximum_count=2)
        self.assertEqual(
            names, (f"{comparison['comparison_id'].split('/', 1)[1]}.json",)
        )
        path = self.store.root / "comparisons" / "sha256" / names[0]
        path.write_bytes(b"{}")
        with self.assertRaises(EcosystemError) as raised:
            load_revision_comparison(comparison["comparison_id"], **inputs)
        self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")

    def test_security_sensitive_matrix_is_closed_and_complete(self) -> None:
        old = self._revision(
            [
                {"path": "LICENSE", "raw": b"Apache License Version 2.0"},
                {"path": "package.json", "raw": b'{"scripts":{}}'},
                {"path": "skills/x/SKILL.md", "raw": b"inert skill"},
                {"path": "docs/a.md", "raw": b"old"},
                {"path": "remove.txt", "raw": b"removed"},
            ],
            commit="a" * 40,
            source_key="github/bytedance/deer-flow",
        )
        new = self._revision(
            [
                {"path": "LICENSE", "raw": b"changed license"},
                {
                    "path": "package.json",
                    "raw": b'{"scripts":{"postinstall":"fetch https://example.invalid; mcp"}}',
                },
                {"path": "skills/x/SKILL.md", "raw": b"grant agent authority and shell"},
                {
                    "path": "docs/a.md",
                    "raw": b"new",
                    "mode": "regular_executable",
                },
                {"path": ".github/workflows/ci.yml", "raw": b"run: inert"},
                {"path": "bin/tool", "raw": b"MZsynthetic"},
                {"path": "new.txt", "raw": b"added"},
            ],
            commit="b" * 40,
            source_key="github/bytedance/deer-flow",
        )
        comparison = compare_revisions(**self._inputs(old, new))
        self.assertEqual(comparison["comparison_result"], "SECURITY_SENSITIVE_CHANGE")
        expected = {
            "BINARY_ADDED",
            "DEPENDENCY_CHANGED",
            "EXECUTABLE_ADDED",
            "FILE_ADDED",
            "FILE_CONTENT_CHANGED",
            "FILE_MODE_CHANGED",
            "FILE_REMOVED",
            "HOOK_OR_INSTALLER_CHANGED",
            "LICENSE_CHANGED",
            "NETWORK_OR_CREDENTIAL_CHANGED",
            "PERMISSION_CHANGED",
            "POLICY_RELEVANT_FILE_CHANGED",
            "PROVENANCE_CHANGED",
            "SKILL_OR_AGENT_INSTRUCTION_CHANGED",
            "WORKFLOW_CHANGED",
        }
        self.assertTrue(expected <= set(comparison["security_change_codes"]))
        self.assertEqual(len(comparison["license_changes"]), 1)
        self.assertEqual(len(comparison["dependency_changes"]), 1)

    def test_component_changes_and_root_move_are_deterministic(self) -> None:
        old = self._revision(
            [{"path": "skills/old/SKILL.md", "raw": b"same"}],
            commit="a" * 40,
            source_key="github/shubhamsaboo/awesome-llm-apps",
        )
        new = self._revision(
            [{"path": "skills/new/SKILL.md", "raw": b"same"}],
            commit="b" * 40,
            source_key="github/shubhamsaboo/awesome-llm-apps",
        )
        comparison = compare_revisions(**self._inputs(old, new))
        self.assertEqual(
            {item["change_kind"] for item in comparison["component_changes"]},
            {"ADDED", "REMOVED"},
        )
        self.assertIn("COMPONENT_ROOT_CHANGED", comparison["security_change_codes"])

    def test_every_closed_security_change_code_is_reachable_and_exact(self) -> None:
        observed: set[str] = set()

        old = self._revision(
            [
                {"path": "LICENSE", "raw": b"Apache License Version 2.0"},
                {"path": "package.json", "raw": b'{"scripts":{}}'},
                {"path": "skills/x/SKILL.md", "raw": b"inert skill"},
                {"path": "docs/a.md", "raw": b"old"},
                {"path": "remove.txt", "raw": b"removed"},
            ],
            commit="1" * 40,
            source_key="github/bytedance/deer-flow",
        )
        new = self._revision(
            [
                {"path": "LICENSE", "raw": b"changed license"},
                {
                    "path": "package.json",
                    "raw": b'{"scripts":{"postinstall":"fetch https://example.invalid; mcp"}}',
                },
                {"path": "skills/x/SKILL.md", "raw": b"grant agent authority and shell"},
                {"path": "docs/a.md", "raw": b"new", "mode": "regular_executable"},
                {"path": ".github/workflows/ci.yml", "raw": b"run: inert"},
                {"path": "bin/tool", "raw": b"MZsynthetic"},
                {"path": "new.txt", "raw": b"added"},
            ],
            commit="2" * 40,
            source_key="github/bytedance/deer-flow",
        )
        observed.update(
            compare_revisions(**self._inputs(old, new))["security_change_codes"]
        )

        old = self._revision(
            [
                {"path": "skills/old/SKILL.md", "raw": b"same component"},
                {"path": "LICENSE-old", "raw": b"old license"},
                {"path": "Cargo.toml", "raw": b"[package]"},
                {"path": "Cargo.lock", "raw": b"old lock"},
                {"path": "type.bin", "raw": b"same type bytes"},
                {"path": "special.bin", "raw": b"same special bytes"},
                {"path": "control.txt", "raw": b"plain text"},
            ],
            commit="3" * 40,
            source_key="github/bytedance/deer-flow",
        )
        new = self._revision(
            [
                {"path": "skills/new/SKILL.md", "raw": b"same component"},
                {"path": "LICENSE-new", "raw": b"new license"},
                {"path": "requirements.txt", "raw": b"fixture==1"},
                {"path": "Cargo.lock", "raw": b"new lock"},
                {"path": "type.bin", "raw": b"PK\x03\x04synthetic nested archive"},
                {"path": "special.bin", "raw": b"same special bytes"},
                {"path": "control.txt", "raw": b"plain\x00text"},
            ],
            commit="4" * 40,
            source_key="github/bytedance/deer-flow",
        )
        observed.update(
            compare_revisions(**self._inputs(old, new))["security_change_codes"]
        )
        # Link/special entries can never enter an authoritative v1 ZIP intake.
        # Exercise that closed comparison rule through its pure, non-persisting
        # seam rather than manufacturing an impossible trusted revision.
        observed.update(
            _path_security_codes(
                "special.bin",
                {
                    "path": "special.bin",
                    "kind": "regular",
                    "mode": "regular_non_executable",
                    "size": 1,
                    "sha256": "1" * 64,
                },
                {
                    "path": "special.bin",
                    "kind": "special",
                    "mode": "special",
                    "size": 1,
                    "sha256": "1" * 64,
                },
                b"x",
                b"x",
            )
        )

        old = self._revision(
            [{"path": "README.md", "raw": b"same tree"}], commit="5" * 40
        )
        new = self._revision(
            [{"path": "README.md", "raw": b"same tree"}], commit="6" * 40
        )
        signature_inputs = self._inputs(old, new)
        signature_inputs["old_provenance_evidence"] = build_provenance_evidence(
            revision=old[0],
            tree=old[1],
            intake_attempt=old[2],
            store=self.store,
            policy=self.policy,
            signature_state="NOT_EVALUATED",
        )
        signature_digest, _signature_size = self.store.put_blob(
            io.BytesIO(b"synthetic unverified signature comparison evidence"),
            maximum_bytes=self.policy.resource_limits["max_text_evidence_bytes"],
        )
        signature_inputs["new_provenance_evidence"] = build_provenance_evidence(
            revision=new[0],
            tree=new[1],
            intake_attempt=new[2],
            store=self.store,
            policy=self.policy,
            signature_state="PRESENT_UNVERIFIED",
            signature_evidence_sha256=signature_digest,
        )
        observed.update(compare_revisions(**signature_inputs)["security_change_codes"])

        self.assertEqual(observed, _SECURITY_CODES)

    def test_wrong_source_cas_tamper_and_forged_comparison_fail_closed(self) -> None:
        old = self._revision(
            [{"path": "README.md", "raw": b"old"}], commit="a" * 40
        )
        other = self._revision(
            [{"path": "README.md", "raw": b"new"}],
            commit="b" * 40,
            source_key="github/bytedance/deer-flow",
        )
        with self.assertRaises(EcosystemError):
            compare_revisions(**self._inputs(old, other))

        new = self._revision(
            [{"path": "README.md", "raw": b"new"}], commit="b" * 40
        )
        inputs = self._inputs(old, new)
        comparison = compare_revisions(**inputs)
        forged = copy.deepcopy(comparison)
        forged["security_change_codes"] = []
        body = {
            key: value
            for key, value in forged.items()
            if key not in {"schema_version", "comparison_id"}
        }
        forged["comparison_id"] = typed_id("comparison", body)
        with self.assertRaises(EcosystemError):
            validate_revision_comparison(forged, **inputs)

        digest = new[1]["entries"][0]["sha256"]
        object_path = self.store.root / "objects" / "sha256" / digest[:2] / digest
        object_path.write_bytes(b"tampered")
        with self.assertRaises(EcosystemError) as raised:
            compare_revisions(**inputs)
        self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")

    def test_old_new_direction_changes_identity(self) -> None:
        old = self._revision([{"path": "a.txt", "raw": b"a"}], commit="a" * 40)
        new = self._revision([{"path": "b.txt", "raw": b"b"}], commit="b" * 40)
        forward = compare_revisions(**self._inputs(old, new))
        reverse = compare_revisions(**self._inputs(new, old))
        self.assertNotEqual(forward["comparison_id"], reverse["comparison_id"])
        self.assertEqual(forward["added_path_sha256s"], reverse["removed_path_sha256s"])

    def test_partial_or_omitted_supporting_evidence_never_looks_complete(self) -> None:
        old = self._revision([{"path": "a.txt", "raw": b"a"}], commit="a" * 40)
        new = self._revision([{"path": "b.txt", "raw": b"b"}], commit="b" * 40)
        incomplete = compare_revisions(
            **self._inputs(
                old,
                new,
                complete_evidence=False,
                old_components=classify_components(
                    revision=old[0], tree=old[1], store=self.store, policy=self.policy
                )[0],
            )
        )
        self.assertEqual(incomplete["comparison_result"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(incomplete["reason_codes"], ["PROVENANCE_INSUFFICIENT"])
        self.assertEqual(incomplete["component_changes"], [])

    def test_unbound_ancestry_claims_cannot_become_comparison_evidence(self) -> None:
        old = self._revision([{"path": "a.txt", "raw": b"a"}], commit="a" * 40)
        new = self._revision([{"path": "a.txt", "raw": b"a"}], commit="b" * 40)
        comparison = compare_revisions(**self._inputs(old, new))
        self.assertEqual(comparison["ancestry_state"], "UNKNOWN")
        for claim in ("SAME", "FAST_FORWARD", "REWIND", "DIVERGED"):
            with self.subTest(claim=claim), self.assertRaises(EcosystemError) as raised:
                compare_revisions(**self._inputs(old, new, ancestry_state=claim))
            self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")

    def test_dependency_manifest_count_and_byte_boundaries(self) -> None:
        old = self._revision(
            [{"path": "README.md", "raw": b"comparison base"}], commit="7" * 40
        )
        exact_count = self._revision(
            [
                {
                    "path": f"dependencies/{index:03d}/requirements.txt",
                    "raw": f"fixture-{index}==1\n".encode("ascii"),
                }
                for index in range(64)
            ],
            commit="8" * 40,
        )
        exact_comparison = compare_revisions(**self._inputs(old, exact_count))
        self.assertEqual(len(exact_comparison["dependency_changes"]), 64)

        too_many = self._revision(
            [
                {
                    "path": f"dependencies/{index:03d}/requirements.txt",
                    "raw": f"fixture-{index}==1\n".encode("ascii"),
                }
                for index in range(65)
            ],
            commit="9" * 40,
        )
        with self.subTest(case="65-dependency-manifests"), self.assertRaises(
            EcosystemError
        ) as raised:
            compare_revisions(**self._inputs(old, too_many))
        self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")

        block = b"".join(
            hashlib.sha256(str(index).encode("ascii")).digest()
            for index in range(32_768)
        )
        self.assertEqual(len(block), 1_048_576)
        exact_bytes = self._revision(
            [{"path": "requirements.txt", "raw": block}], commit="c" * 40
        )
        self.assertEqual(
            len(compare_revisions(**self._inputs(old, exact_bytes))["dependency_changes"]),
            1,
        )
        too_large = self._revision(
            [{"path": "requirements.txt", "raw": block + b"x"}], commit="d" * 40
        )
        with self.subTest(case="dependency-manifest-1MiB-plus-one"), self.assertRaises(
            EcosystemError
        ) as raised:
            compare_revisions(**self._inputs(old, too_large))
        self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")

    def test_comparison_collection_bound_is_exact_and_deterministic(self) -> None:
        exact = [{"value": 2}, {"value": 1}]
        self.assertEqual(
            _canonical_objects(copy.deepcopy(exact), 2, "synthetic comparison list"),
            [{"value": 1}, {"value": 2}],
        )
        with self.assertRaises(EcosystemError) as raised:
            _canonical_objects(
                [{"value": 3}, {"value": 2}, {"value": 1}],
                2,
                "synthetic comparison list",
            )
        self.assertEqual(raised.exception.reason_code, "RESOURCE_LIMIT_EXCEEDED")

    def test_comparison_nested_schema_and_aggregate_bounds_fail_closed(self) -> None:
        revision = self._revision(
            [{"path": "README.md", "raw": b"closed comparison"}], commit="e" * 40
        )
        inputs = self._inputs(revision, revision)
        comparison = compare_revisions(**inputs)
        mutations = {
            "result-wrong-type": lambda value: value.update(comparison_result={}),
            "ancestry-wrong-type": lambda value: value.update(ancestry_state=[]),
            "path-list-not-list": lambda value: value.update(added_path_sha256s=()),
            "path-list-bool": lambda value: value.update(added_path_sha256s=[True]),
            "path-list-duplicate": lambda value: value.update(
                added_path_sha256s=["a" * 64, "a" * 64]
            ),
            "path-list-aggregate-plus-one": lambda value: value.update(
                added_path_sha256s=[f"{index:064x}" for index in range(8193)]
            ),
            "component-change-extra": lambda value: value.update(
                component_changes=[
                    {
                        "component_id": typed_id("component", {"fixture": 1}),
                        "old_component_revision_id": None,
                        "new_component_revision_id": typed_id(
                            "component-revision", {"fixture": 1}
                        ),
                        "change_kind": "ADDED",
                        "unexpected": True,
                    }
                ]
            ),
            "dependency-change-invalid-shape": lambda value: value.update(
                dependency_changes=[
                    {
                        "path_sha256": "a" * 64,
                        "old_sha256": None,
                        "new_sha256": None,
                        "change_kind": "ADDED",
                    }
                ]
            ),
            "security-code-duplicate": lambda value: value.update(
                security_change_codes=["FILE_ADDED", "FILE_ADDED"]
            ),
            "security-code-unsupported": lambda value: value.update(
                security_change_codes=["APPROVED"]
            ),
        }
        for case, mutate in mutations.items():
            candidate = copy.deepcopy(comparison)
            mutate(candidate)
            with self.subTest(case=case), self.assertRaises(EcosystemError):
                validate_revision_comparison(candidate, **inputs)


if __name__ == "__main__":
    unittest.main()
