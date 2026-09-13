from __future__ import annotations

import copy
import builtins
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ash.ecosystem_bridge import (
    _EXPECTED_VALIDATORS,
    adapt_evaluation_receipt,
    append_state_transition,
    bridge_scout_candidate,
    build_ecosystem_evaluation_request,
    load_state_lineage,
    persist_component_revisions,
    propose_evidence_outcome,
    propose_rejection,
    propose_snapshot_integrity_verified,
)
from ash.ecosystem_compare import compare_revisions
from ash.ecosystem_evidence import (
    analyze_static_evidence,
    build_provenance_evidence,
    classify_components,
    inspect_license_evidence,
)
from ash.ecosystem_models import (
    EcosystemError,
    StateVector,
    build_state_record,
    canonical_json_bytes,
    canonical_sha256,
    typed_id,
    validate_state_vector,
    zero_authority,
)
from ash.ecosystem_intake import intake_pre_supplied_zip
from ash.ecosystem_policy import _load_test_source_policy as load_trusted_source_policy
from ash.ecosystem_storage import QuarantineStore, open_stable_input
from ash.evaluation import (
    EvaluationError,
    _load_test_validator_registry as load_trusted_validator_registry,
    canonical_sha256 as evaluation_canonical_sha256,
    evaluate_contract,
)
from tests.test_ecosystem_storage_intake import scout_receipt, test_store, zip_bytes


ROOT = Path(__file__).resolve().parents[1]
POLICY_BYTES = (ROOT / "config" / "ecosystem-source-policy.json").read_bytes()
REGISTRY_BYTES = (ROOT / "config" / "validator-registry.json").read_bytes()
FROZEN_WIRE_LIFECYCLE = {
    "creation": "created",
    "selection": "not_selected",
    "execution": "not_executed",
    "review": "not_reviewed",
    "enhancement": "not_enhanced",
    "validation": "not_validated",
    "reporting": "not_reported",
}


def expected_wire_subject(
    *, subject_type: str, wire_prefix: str, subject_id: str, record: dict, creator: str
) -> dict:
    return {
        "subject_type": subject_type,
        "subject_id": wire_prefix + ":" + subject_id.split("/", 1)[1],
        "subject_sha256": canonical_sha256(record),
        "parent_subject_sha256": None,
        "lifecycle": dict(FROZEN_WIRE_LIFECYCLE),
        "stage_receipts": {
            "creator": creator,
            "execution": None,
            "reviewer": None,
            "enhancer": None,
            "reporter": None,
        },
    }


def trusted_root(base: Path) -> Path:
    root = base / "trusted-root"
    config = root / "config"
    config.mkdir(parents=True)
    files = {
        "config/ecosystem-source-policy.json": POLICY_BYTES,
        "config/validator-registry.json": REGISTRY_BYTES,
    }
    manifest: dict[str, dict[str, object]] = {}
    for relative, raw in files.items():
        normalized = raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
        (root / relative).write_bytes(raw)
        manifest[relative] = {
            "bytes": len(normalized),
            "sha256": hashlib.sha256(normalized).hexdigest(),
        }
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


class EcosystemEvaluationStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        root = trusted_root(self.base)
        self.policy = load_trusted_source_policy(root=root)
        self.registry = load_trusted_validator_registry(root=root)
        raw = zip_bytes(
            [
                ("root/LICENSE", b"Apache License Version 2.0"),
                ("root/docs/architecture.md", b"Synthetic inert architecture."),
                ("root/plain.txt", b"Synthetic inert data."),
            ]
        )
        receipt, candidate_id = scout_receipt()
        self.bridge = bridge_scout_candidate(
            scout_receipt=receipt,
            candidate_id=candidate_id,
            source_key="github/openai/codex",
            requested_input_sha256=hashlib.sha256(raw).hexdigest(),
            requested_input_size=len(raw),
            policy=self.policy,
        )
        self.scout_receipt = receipt
        archive = self.base / "fixture.zip"
        archive.write_bytes(raw)
        self.store = test_store(
            self.base,
            policy=self.policy,
            name="quarantine",
            max_cas_bytes=32 * 1024 * 1024,
        )
        with open_stable_input(archive, maximum_bytes=1024 * 1024) as stable:
            intake = intake_pre_supplied_zip(
                bridge=self.bridge,
                zip_input=stable,
                policy=self.policy,
                store=self.store,
            )
        self.revision = intake["revision"]
        self.tree = intake["tree"]
        self.attempt = intake["attempt"]
        snapshot = propose_snapshot_integrity_verified(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
        )
        append_state_transition(
            proposal=snapshot,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.tree, self.attempt],
            evaluation_receipts=[],
        )
        self.provenance = build_provenance_evidence(
            revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
        )
        self.license = inspect_license_evidence(
            subject_id=self.revision["revision_id"],
            subject_record=self.revision,
            tree=self.tree,
            store=self.store,
            policy=self.policy,
        )

        self.findings, self.static_report = analyze_static_evidence(
            subject_id=self.revision["revision_id"],
            subject_record=self.revision,
            tree=self.tree,
            store=self.store,
            policy=self.policy,
            provenance_evidence=self.provenance,
            license_evidence=self.license,
            intake_attempt=self.attempt,
        )
        self.components, self.classifications, self.classification_report = classify_components(
            revision=self.revision,
            tree=self.tree,
            store=self.store,
            policy=self.policy,
        )
        self.unavailable_static_report = analyze_static_evidence(
            subject_id=self.revision["revision_id"],
            subject_record=self.revision,
            tree=self.tree,
            store=self.store,
            policy=self.policy,
            analyzer_available=False,
        )[1]
        self.unavailable_classification_report = classify_components(
            revision=self.revision,
            tree=self.tree,
            store=self.store,
            policy=self.policy,
            classifier_available=False,
        )[2]
        self.common = {
            "subject_record": self.revision,
            "tree": self.tree,
            "intake_attempt": self.attempt,
            "store": self.store,
            "policy": self.policy,
            "registry": self.registry,
            "provenance_evidence": self.provenance,
            "license_evidence": self.license,
            "static_findings": self.findings,
            "static_report": self.static_report,
            "components": self.components,
            "classifications": self.classifications,
            "classification_report": self.classification_report,
        }

    def test_registry_must_share_the_store_policy_manifest_snapshot(self) -> None:
        root = Path(self.policy._repository_root)
        manifest_path = root / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docs/manifest-snapshot-drift.txt"] = {
            "bytes": 0,
            "sha256": "0" * 64,
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        drifted_registry = load_trusted_validator_registry(root=root)

        self.assertNotEqual(
            self.policy.integrity_manifest_sha256,
            drifted_registry._integrity_manifest_sha256,
        )
        with self.assertRaises(EcosystemError) as raised:
            self.store._require_registry(drifted_registry)
        self.assertEqual(raised.exception.reason_code, "POLICY_UNTRUSTED")
        self.store._require_registry(self.registry)

    def _receipt(
        self,
        profile_id: str,
        *,
        prior_receipts: list[dict] | None = None,
        prior_transitions: list[dict] | None = None,
    ) -> dict:
        request = build_ecosystem_evaluation_request(
            profile_id=profile_id,
            prior_evaluation_receipts=prior_receipts or [],
            prior_transition_receipts=prior_transitions or [],
            **self.common,
        )
        return evaluate_contract(request, registry=self.registry)

    def _fatal_subject(self) -> dict[str, object]:
        raw = zip_bytes(
            [
                ("root/LICENSE", b"Apache License Version 2.0"),
                ("root/.env", b"SYNTHETIC_VALUE=placeholder"),
            ]
        )
        receipt, candidate_id = scout_receipt()
        bridge = bridge_scout_candidate(
            scout_receipt=receipt,
            candidate_id=candidate_id,
            source_key="github/openai/codex",
            requested_input_sha256=hashlib.sha256(raw).hexdigest(),
            requested_input_size=len(raw),
            policy=self.policy,
        )
        archive = self.base / "fatal-fixture.zip"
        archive.write_bytes(raw)
        store = test_store(
            self.base,
            policy=self.policy,
            name="fatal-quarantine",
            max_cas_bytes=32 * 1024 * 1024,
        )
        with open_stable_input(archive, maximum_bytes=1024 * 1024) as stable:
            intake = intake_pre_supplied_zip(
                bridge=bridge,
                zip_input=stable,
                policy=self.policy,
                store=store,
            )
        provenance = build_provenance_evidence(
            revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=store,
            policy=self.policy,
        )
        license_evidence = inspect_license_evidence(
            subject_id=intake["revision"]["revision_id"],
            subject_record=intake["revision"],
            tree=intake["tree"],
            store=store,
            policy=self.policy,
        )
        findings, report = analyze_static_evidence(
            subject_id=intake["revision"]["revision_id"],
            subject_record=intake["revision"],
            tree=intake["tree"],
            store=store,
            policy=self.policy,
            provenance_evidence=provenance,
            license_evidence=license_evidence,
            intake_attempt=intake["attempt"],
        )
        return {
            "store": store,
            "revision": intake["revision"],
            "tree": intake["tree"],
            "attempt": intake["attempt"],
            "evidence": [provenance, license_evidence, *findings, report],
            "report": report,
        }

    def _apply(
        self,
        profile_id: str,
        receipt: dict,
        *,
        prior_receipts: list[dict] | None = None,
        prior_transitions: list[dict] | None = None,
    ) -> tuple[dict, dict]:
        proposal = adapt_evaluation_receipt(
            evaluation_receipt=receipt,
            profile_id=profile_id,
            prior_evaluation_receipts=prior_receipts or [],
            prior_transition_receipts=prior_transitions or [],
            **self.common,
        )
        self.assertIsNotNone(proposal)
        transition = proposal.record()
        if profile_id.endswith("provenance"):
            evidence = [self.provenance]
        elif profile_id.endswith("static-security"):
            evidence = [self.static_report]
        elif profile_id.endswith("classification"):
            evidence = [self.classification_report]
        elif profile_id.endswith("validation-bundle"):
            evidence = [self.provenance]
        else:
            evidence = list(prior_transitions or [])
        state = append_state_transition(
            proposal=proposal,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=evidence,
            evaluation_receipts=[receipt],
            registry=self.registry,
        )
        return transition, state

    def _advance_to_validation_complete(self) -> tuple[list[dict], list[dict], dict]:
        receipts: list[dict] = []
        transitions: list[dict] = []
        for profile_id in (
            "nexus.profile.ecosystem-provenance",
            "nexus.profile.ecosystem-static-security",
            "nexus.profile.ecosystem-classification",
            "nexus.profile.ecosystem-validation-bundle",
        ):
            required = receipts[:3] if profile_id.endswith("validation-bundle") else []
            receipt = self._receipt(profile_id, prior_receipts=required)
            transition, state = self._apply(profile_id, receipt, prior_receipts=required)
            receipts.append(receipt)
            transitions.append(transition)
        return receipts, transitions, state

    def _advance_to_terminal(self) -> tuple[list[dict], list[dict], dict]:
        receipts, transitions, state = self._advance_to_validation_complete()
        receipt = self._receipt(
            "nexus.profile.ecosystem-review-bundle",
            prior_receipts=receipts,
            prior_transitions=transitions,
        )
        transition, state = self._apply(
            "nexus.profile.ecosystem-review-bundle",
            receipt,
            prior_receipts=receipts,
            prior_transitions=transitions,
        )
        receipts.append(receipt)
        transitions.append(transition)
        return receipts, transitions, state

    def test_exact_five_profile_sequence_reaches_only_quarantined_terminal_pair(self) -> None:
        receipts, transitions, state = self._advance_to_terminal()
        self.assertEqual(len(receipts), 5)
        self.assertEqual(len(transitions), 5)
        self.assertEqual(
            state["state"],
            {
                "possession_state": "SNAPSHOT_INTEGRITY_VERIFIED",
                "review_state": "REVIEW_EVIDENCE_COMPLETE",
                "evidence_outcome": "COMPLETE",
                "disposition": "QUARANTINED",
            },
        )
        self.assertEqual(state["authority"], zero_authority())
        lineage = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
            registry=self.registry,
        )
        self.assertEqual(len(lineage), 7)

    def test_success_and_failure_paths_never_touch_authority_entrypoints(self) -> None:
        import importlib
        import os
        import runpy
        import socket
        import subprocess
        import sys
        import types
        import urllib.request

        import ash.agent_contract as agent_contract_module
        import ash.capabilities as capabilities_module
        import ash.execution as execution_module
        import ash.router as router_module
        import ash.runtime_decision as runtime_decision_module
        import scripts.desktop_marketplace as desktop_marketplace_module
        import scripts.package_nexus as package_module
        import scripts.release_install as release_install_module

        touched: list[str] = []
        real_import = builtins.__import__
        authority_import_tokens = {
            "activation",
            "agent_runtime",
            "approval",
            "checkpoint",
            "host",
            "mcp",
            "memory",
            "promotion",
            "router",
            "runtime_decision",
            "scheduler",
            "selection",
        }

        def forbidden(label: str):
            def fail(*_args: object, **_kwargs: object) -> None:
                touched.append(label)
                raise AssertionError(f"Slice 3C touched forbidden authority entrypoint: {label}")

            return fail

        def guarded_import(
            name: str,
            globals: object = None,
            locals: object = None,
            fromlist: tuple[str, ...] = (),
            level: int = 0,
        ) -> object:
            candidates = [part.casefold() for part in name.split(".") if part]
            effective_fromlist = fromlist or ()
            candidates.extend(str(part).casefold() for part in effective_fromlist)
            if any(candidate in authority_import_tokens for candidate in candidates):
                touched.append(f"import:{name}:{','.join(effective_fromlist)}")
                raise AssertionError("Slice 3C imported a forbidden authority module")
            return real_import(name, globals, locals, fromlist, level)

        mcp_package = types.ModuleType("ash.mcp")
        mcp_package.__path__ = []  # type: ignore[attr-defined]
        synthetic_modules: dict[str, types.ModuleType] = {"ash.mcp": mcp_package}
        for module_name, attributes in {
            "ash.mcp.server": ("create_server", "run_stdio"),
            "ash.mcp.handoff": ("validate_host_receipt",),
            "ash.mcp.host_inventory": ("claim_inventory_bound_execution_start",),
            "ash.mcp.host_mapping": ("presentation_profile",),
            "scripts.check_updates": ("main",),
        }.items():
            module = types.ModuleType(module_name)
            for attribute in attributes:
                setattr(module, attribute, forbidden(f"{module_name}.{attribute}"))
            synthetic_modules[module_name] = module

        targets = (
            (subprocess, "run", "subprocess.run"),
            (subprocess, "Popen", "subprocess.Popen"),
            (subprocess, "call", "subprocess.call"),
            (subprocess, "check_call", "subprocess.check_call"),
            (subprocess, "check_output", "subprocess.check_output"),
            (socket, "socket", "socket.socket"),
            (socket, "create_connection", "socket.create_connection"),
            (urllib.request, "urlopen", "urllib.request.urlopen"),
            (os, "system", "os.system"),
            (os, "popen", "os.popen"),
            (importlib, "import_module", "importlib.import_module"),
            (runpy, "run_module", "runpy.run_module"),
            (runpy, "run_path", "runpy.run_path"),
            (router_module, "route_task", "router.route_task"),
            (execution_module, "load_selected_skills", "execution.load_selected_skills"),
            (execution_module, "execute_route", "execution.execute_route"),
            (capabilities_module, "load_capability_catalog", "capabilities.load_catalog"),
            (
                capabilities_module,
                "select_minimum_sufficient_capabilities",
                "capabilities.select",
            ),
            (
                runtime_decision_module,
                "prepare_catalog_runtime_candidates",
                "runtime.prepare_candidates",
            ),
            (runtime_decision_module, "build_runtime_decision", "runtime.build_decision"),
            (runtime_decision_module, "host_runtime_decision", "runtime.host_decision"),
            (
                agent_contract_module,
                "validate_agent_task_contract",
                "agent.validate_delegation_contract",
            ),
            (release_install_module, "install", "release.install"),
            (release_install_module, "uninstall", "release.uninstall"),
            (desktop_marketplace_module, "install", "marketplace.install"),
            (desktop_marketplace_module, "uninstall", "marketplace.uninstall"),
            (package_module, "build_package", "package.build"),
        )

        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, synthetic_modules))
            stack.enter_context(patch.object(builtins, "__import__", new=guarded_import))
            for module, name, label in targets:
                stack.enter_context(patch.object(module, name, new=forbidden(label)))

            self.assertEqual(
                build_provenance_evidence(
                    revision=self.revision,
                    tree=self.tree,
                    intake_attempt=self.attempt,
                    store=self.store,
                    policy=self.policy,
                ),
                self.provenance,
            )
            _receipts, _transitions, state = self._advance_to_terminal()
            self.assertEqual(
                state["state"],
                {
                    "possession_state": "SNAPSHOT_INTEGRITY_VERIFIED",
                    "review_state": "REVIEW_EVIDENCE_COMPLETE",
                    "evidence_outcome": "COMPLETE",
                    "disposition": "QUARANTINED",
                },
            )
            self.assertEqual(state["authority"], zero_authority())

            forged_tree = copy.deepcopy(self.tree)
            forged_tree["entries"][0]["sha256"] = "0" * 64
            with self.assertRaises(EcosystemError):
                build_provenance_evidence(
                    revision=self.revision,
                    tree=forged_tree,
                    intake_attempt=self.attempt,
                    store=self.store,
                    policy=self.policy,
                )

        self.assertEqual(touched, [])

    def test_forbidden_authority_tokens_are_not_lifecycle_states(self) -> None:
        forbidden = (
            "APPROVAL_READY",
            "APPROVED",
            "ACTIVE",
            "ROUTABLE",
            "INSTALLED",
            "EXECUTABLE",
            "ENABLED",
            "HOST_ELIGIBLE",
        )
        base = [
            "MIRRORED_UNREVIEWED",
            "NOT_REVIEWED",
            "IN_PROGRESS",
            "QUARANTINED",
        ]
        for token in forbidden:
            for axis in range(4):
                with self.subTest(token=token, axis=axis):
                    candidate = list(base)
                    candidate[axis] = token
                    with self.assertRaises(EcosystemError) as raised:
                        validate_state_vector(StateVector(*candidate))
                    self.assertEqual(
                        raised.exception.reason_code, "STATE_TRANSITION_INVALID"
                    )

    def test_trivial_partial_pass_and_nonpass_cannot_advance_review(self) -> None:
        profile = "nexus.profile.ecosystem-static-security"
        full = build_ecosystem_evaluation_request(profile_id=profile, **self.common)
        partial = copy.deepcopy(full)
        partial["checks"] = partial["checks"][:1]
        partial_pass = evaluate_contract(partial, registry=self.registry)
        self.assertEqual(partial_pass["result"]["state"], "PASS")
        with self.assertRaises(EcosystemError) as raised:
            adapt_evaluation_receipt(
                evaluation_receipt=partial_pass, profile_id=profile, **self.common
            )
        self.assertEqual(raised.exception.reason_code, "EVALUATION_RECEIPT_INVALID")

        failing = copy.deepcopy(full)
        failing["checks"][0]["observed"] = "NOT_COMPLETE"
        failing["checks"][0]["evidence"]["content_sha256"] = hashlib.sha256(
            b'"NOT_COMPLETE"'
        ).hexdigest()
        failed_receipt = evaluate_contract(failing, registry=self.registry)
        self.assertEqual(failed_receipt["result"]["state"], "FAIL")
        with self.assertRaises(EcosystemError) as raised:
            adapt_evaluation_receipt(
                evaluation_receipt=failed_receipt, profile_id=profile, **self.common
            )
        self.assertEqual(raised.exception.reason_code, "EVALUATION_RESULT_BLOCKED")

    def test_adapter_rejects_missing_extra_optional_wrong_and_rewritten_checks(self) -> None:
        profile = "nexus.profile.ecosystem-static-security"
        request = build_ecosystem_evaluation_request(profile_id=profile, **self.common)
        canonical_receipt = evaluate_contract(request, registry=self.registry)
        state_before = self.store.list_record_names("state/sha256", maximum_count=100)

        request_mutations = {
            "missing-check": lambda value: value["checks"].pop(),
            "extra-check": lambda value: value["checks"].append(
                {
                    **copy.deepcopy(value["checks"][0]),
                    "check_id": "extra-check",
                    "evidence": {
                        **copy.deepcopy(value["checks"][0]["evidence"]),
                        "evidence_id": "extra-evidence",
                    },
                }
            ),
            "optional-check": lambda value: value["checks"][0].update(required=False),
            "wrong-check-id": lambda value: value["checks"][0].update(check_id="wrong-check"),
            "wrong-evidence-source": lambda value: value["checks"][0]["evidence"].update(
                evidence_id="wrong-evidence"
            ),
            "wrong-evidence-value": lambda value: (
                value["checks"][0].update(expected="FORGED", observed="FORGED"),
                value["checks"][0]["evidence"].update(
                    content_sha256=evaluation_canonical_sha256("FORGED")
                ),
            ),
        }
        for case, mutate in request_mutations.items():
            candidate_request = copy.deepcopy(request)
            mutate(candidate_request)
            with self.subTest(case=case):
                try:
                    candidate_receipt = evaluate_contract(
                        candidate_request, registry=self.registry
                    )
                except EvaluationError:
                    continue
                with self.assertRaises(EcosystemError):
                    adapt_evaluation_receipt(
                        evaluation_receipt=candidate_receipt,
                        profile_id=profile,
                        **self.common,
                    )

        reordered = copy.deepcopy(canonical_receipt)
        reordered["checks"].reverse()
        reordered_body = {
            key: value
            for key, value in reordered.items()
            if key != "evaluation_id"
        }
        reordered["evaluation_id"] = "evaluation:" + evaluation_canonical_sha256(
            reordered_body
        )
        with self.subTest(case="reordered-receipt-checks"), self.assertRaises(EcosystemError):
            adapt_evaluation_receipt(
                evaluation_receipt=reordered, profile_id=profile, **self.common
            )

        rewritten = copy.deepcopy(canonical_receipt)
        rewritten["evidence"]["items"][0]["summary"] = "self rewritten safe summary"
        rewritten_body = {
            key: value
            for key, value in rewritten.items()
            if key != "evaluation_id"
        }
        rewritten["evaluation_id"] = "evaluation:" + evaluation_canonical_sha256(
            rewritten_body
        )
        with self.subTest(case="self-rewritten-receipt"), self.assertRaises(EcosystemError):
            adapt_evaluation_receipt(
                evaluation_receipt=rewritten, profile_id=profile, **self.common
            )

        transition_mutation = copy.deepcopy(canonical_receipt)
        transition_mutation["state_transition"]["applied"] = True
        transition_body = {
            key: value
            for key, value in transition_mutation.items()
            if key != "evaluation_id"
        }
        transition_mutation["evaluation_id"] = (
            "evaluation:" + evaluation_canonical_sha256(transition_body)
        )
        with self.subTest(case="wrong-native-transition"), self.assertRaises(EcosystemError):
            adapt_evaluation_receipt(
                evaluation_receipt=transition_mutation,
                profile_id=profile,
                **self.common,
            )

        with self.subTest(case="wrong-profile"), self.assertRaises(EcosystemError):
            adapt_evaluation_receipt(
                evaluation_receipt=canonical_receipt,
                profile_id="nexus.profile.ecosystem-provenance",
                **self.common,
            )
        self.assertEqual(
            self.store.list_record_names("state/sha256", maximum_count=100),
            state_before,
        )

    def test_component_revision_wire_projection_and_wrong_parent_fail_closed(self) -> None:
        persist_component_revisions(
            components=self.components,
            classifications=self.classifications,
            classification_report=self.classification_report,
            revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
        )
        component = self.components[0]
        snapshot = propose_snapshot_integrity_verified(
            subject_record=component,
            parent_revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
        )
        append_state_transition(
            proposal=snapshot,
            subject_record=component,
            parent_revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[component],
            evaluation_receipts=[],
        )
        inputs = {
            **self.common,
            "subject_record": component,
            "parent_revision": self.revision,
        }
        request = build_ecosystem_evaluation_request(
            profile_id="nexus.profile.ecosystem-provenance", **inputs
        )
        self.assertEqual(
            request["subject"],
            expected_wire_subject(
                subject_type="ecosystem_component_revision",
                wire_prefix="ecosystem-component-revision",
                subject_id=component["component_revision_id"],
                record=component,
                creator=canonical_sha256(component),
            ),
        )
        receipt = evaluate_contract(request, registry=self.registry)
        self.assertIsNotNone(
            adapt_evaluation_receipt(
                evaluation_receipt=receipt,
                profile_id="nexus.profile.ecosystem-provenance",
                **inputs,
            )
        )

        wrong_parent = copy.deepcopy(self.revision)
        wrong_parent["commit_oid"] = "b" * 40
        with self.assertRaises(EcosystemError):
            build_ecosystem_evaluation_request(
                profile_id="nexus.profile.ecosystem-provenance",
                **{**inputs, "parent_revision": wrong_parent},
            )

    def test_source_revision_wire_projection_is_exact_and_independently_frozen(self) -> None:
        request = build_ecosystem_evaluation_request(
            profile_id="nexus.profile.ecosystem-provenance", **self.common
        )
        self.assertEqual(
            request["subject"],
            expected_wire_subject(
                subject_type="ecosystem_source_revision",
                wire_prefix="ecosystem-source-revision",
                subject_id=self.revision["revision_id"],
                record=self.revision,
                creator=canonical_sha256(self.attempt),
            ),
        )

    def test_stale_prior_state_and_post_seal_policy_mutation_cannot_advance(self) -> None:
        profile = "nexus.profile.ecosystem-provenance"
        receipt = self._receipt(profile)
        self._apply(profile, receipt)
        before = self.store.list_record_names("state/sha256", maximum_count=100)
        with self.subTest(case="stale-prior-state"), self.assertRaises(EcosystemError):
            adapt_evaluation_receipt(
                evaluation_receipt=receipt, profile_id=profile, **self.common
            )
        self.assertEqual(
            self.store.list_record_names("state/sha256", maximum_count=100), before
        )

        self.policy._policy["evaluation_profiles"][0]["required_checks"][0][
            "evidence_id"
        ] = "mutated-evidence"
        with self.subTest(case="post-seal-policy-profile-mutation"), self.assertRaises(EcosystemError):
            build_ecosystem_evaluation_request(profile_id=profile, **self.common)

    def test_each_native_nonpass_state_is_blocked_without_lineage_change(self) -> None:
        profile = "nexus.profile.ecosystem-static-security"
        full = build_ecosystem_evaluation_request(profile_id=profile, **self.common)
        requests: dict[str, dict] = {}

        failed = copy.deepcopy(full)
        failed["checks"][0]["observed"] = "NOT_COMPLETE"
        failed["checks"][0]["evidence"]["content_sha256"] = canonical_sha256(
            "NOT_COMPLETE"
        )
        requests["FAIL"] = failed

        insufficient = copy.deepcopy(full)
        insufficient["checks"][0]["evidence"] = None
        requests["INSUFFICIENT_EVIDENCE"] = insufficient

        invalid = copy.deepcopy(full)
        invalid["checks"] = []
        requests["INVALID_REQUEST"] = invalid

        not_applicable = copy.deepcopy(full)
        not_applicable["subject"]["subject_type"] = "artifact"
        requests["NOT_APPLICABLE"] = not_applicable

        before = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
            registry=self.registry,
        )
        for expected_state, request in requests.items():
            with self.subTest(expected_state=expected_state):
                receipt = evaluate_contract(request, registry=self.registry)
                self.assertEqual(receipt["result"]["state"], expected_state)
                with self.assertRaises(EcosystemError):
                    adapt_evaluation_receipt(
                        evaluation_receipt=receipt, profile_id=profile, **self.common
                    )
                self.assertEqual(
                    load_state_lineage(
                        store=self.store,
                        subject_id=self.revision["revision_id"],
                        subject_sha256=canonical_sha256(self.revision),
                        policy=self.policy,
                        registry=self.registry,
                    ),
                    before,
                )

        registry_payload = json.loads(REGISTRY_BYTES)
        target = next(
            item
            for item in registry_payload["validators"]
            if item["validator_id"] == "nexus.validator.ecosystem-static-security"
        )
        target["availability"] = "unavailable"
        raw = (json.dumps(registry_payload, indent=2) + "\n").encode("utf-8")
        unavailable_root = self.base / "unavailable-registry"
        (unavailable_root / "config").mkdir(parents=True)
        (unavailable_root / "config" / "validator-registry.json").write_bytes(raw)
        normalized = raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
        (unavailable_root / "MANIFEST.json").write_text(
            json.dumps(
                {
                    "config/validator-registry.json": {
                        "bytes": len(normalized),
                        "sha256": hashlib.sha256(normalized).hexdigest(),
                    }
                }
            ),
            encoding="utf-8",
        )
        unavailable_registry = load_trusted_validator_registry(root=unavailable_root)
        unavailable_receipt = evaluate_contract(full, registry=unavailable_registry)
        self.assertEqual(
            unavailable_receipt["result"]["state"], "VALIDATOR_UNAVAILABLE"
        )
        unavailable_common = {**self.common, "registry": unavailable_registry}
        with self.assertRaises(EcosystemError):
            adapt_evaluation_receipt(
                evaluation_receipt=unavailable_receipt,
                profile_id=profile,
                **unavailable_common,
            )
        self.assertEqual(
            load_state_lineage(
                store=self.store,
                subject_id=self.revision["revision_id"],
                subject_sha256=canonical_sha256(self.revision),
                policy=self.policy,
                registry=self.registry,
            ),
            before,
        )

    def test_review_bundle_requires_exact_ordered_receipts_and_edges(self) -> None:
        receipts, transitions, _state = self._advance_to_validation_complete()
        profile = "nexus.profile.ecosystem-review-bundle"
        review_receipt = self._receipt(
            profile,
            prior_receipts=receipts,
            prior_transitions=transitions,
        )
        before = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
            registry=self.registry,
        )

        receipt_variants: list[tuple[str, int, list[dict]]] = []
        for index in range(4):
            other = index + 1 if index < 3 else index - 1
            receipt_variants.append(("omit", index, receipts[:index] + receipts[index + 1 :]))
            duplicated = copy.deepcopy(receipts)
            duplicated[index] = copy.deepcopy(receipts[other])
            receipt_variants.append(("duplicate", index, duplicated))
            reordered = copy.deepcopy(receipts)
            reordered[index], reordered[other] = reordered[other], reordered[index]
            receipt_variants.append(("reorder", index, reordered))
            mutated = copy.deepcopy(receipts)
            mutated[index]["checks"][0]["reason_code"] = "EVIDENCE_MISSING"
            receipt_variants.append(("mutate", index, mutated))

        edge_variants: list[tuple[str, int, list[dict]]] = []
        for index in range(4):
            other = index + 1 if index < 3 else index - 1
            edge_variants.append(("omit", index, transitions[:index] + transitions[index + 1 :]))
            duplicated = copy.deepcopy(transitions)
            duplicated[index] = copy.deepcopy(transitions[other])
            edge_variants.append(("duplicate", index, duplicated))
            reordered = copy.deepcopy(transitions)
            reordered[index], reordered[other] = reordered[other], reordered[index]
            edge_variants.append(("reorder", index, reordered))
            mutated = copy.deepcopy(transitions)
            mutated[index]["policy_semantic_sha256"] = "f" * 64
            body = {
                key: value
                for key, value in mutated[index].items()
                if key not in {"schema_version", "transition_id"}
            }
            mutated[index]["transition_id"] = typed_id("transition", body)
            edge_variants.append(("mutate", index, mutated))

        cases = [
            ("evaluation_receipt", action, index, variant, transitions)
            for action, index, variant in receipt_variants
        ] + [
            ("transition_edge", action, index, receipts, variant)
            for action, index, variant in edge_variants
        ]
        for record_kind, action, review_edge_index, prior_receipts, prior_transitions in cases:
            with self.subTest(
                record_kind=record_kind,
                action=action,
                review_edge_index=review_edge_index,
            ), self.assertRaises(EcosystemError):
                adapt_evaluation_receipt(
                    evaluation_receipt=review_receipt,
                    profile_id=profile,
                    prior_evaluation_receipts=prior_receipts,
                    prior_transition_receipts=prior_transitions,
                    **self.common,
                )
            self.assertEqual(
                load_state_lineage(
                    store=self.store,
                    subject_id=self.revision["revision_id"],
                    subject_sha256=canonical_sha256(self.revision),
                    policy=self.policy,
                    registry=self.registry,
                ),
                before,
            )

    def test_forged_or_mutated_transition_cannot_manufacture_state(self) -> None:
        snapshot = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        snapshot._transition["reason_codes"] = ["PROVENANCE_INSUFFICIENT"]
        body = {
            key: value
            for key, value in snapshot._transition.items()
            if key not in {"schema_version", "transition_id"}
        }
        snapshot._transition["transition_id"] = typed_id("transition", body)
        with self.assertRaises(EcosystemError) as raised:
            append_state_transition(
                proposal=snapshot,
                subject_record=self.revision,
                tree=self.tree,
                intake_attempt=self.attempt,
                store=self.store,
                policy=self.policy,
                evidence_records=[self.unavailable_static_report],
                evaluation_receipts=[],
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")
        with self.assertRaises(EcosystemError):
            append_state_transition(  # type: ignore[arg-type]
                proposal={},
                subject_record=self.revision,
                tree=self.tree,
                intake_attempt=self.attempt,
                store=self.store,
                policy=self.policy,
                evidence_records=[],
                evaluation_receipts=[],
            )

    def test_replay_is_idempotent_and_same_head_competitor_is_stale(self) -> None:
        insufficient = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        alternate = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_classification_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        first = append_state_transition(
            proposal=insufficient,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            evaluation_receipts=[],
        )
        replay = append_state_transition(
            proposal=insufficient,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            evaluation_receipts=[],
        )
        self.assertEqual(replay, first)
        with self.assertRaises(EcosystemError) as raised:
            append_state_transition(
                proposal=alternate,
                subject_record=self.revision,
                tree=self.tree,
                intake_attempt=self.attempt,
                store=self.store,
                policy=self.policy,
                evidence_records=[self.unavailable_classification_report],
                evaluation_receipts=[],
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")

    def test_invalid_evidence_cannot_be_committed_then_fail_on_first_reload(self) -> None:
        body = {
            "subject_id": self.revision["revision_id"],
            "subject_sha256": canonical_sha256(self.revision),
            "analyzer_config_sha256": self.policy.static_analyzer_config_sha256,
            "reason_codes": ["ANALYZER_UNAVAILABLE"],
            "authority": zero_authority(),
        }
        forged = {
            "schema_version": "nexus.ecosystem-static-report.v1",
            "report_id": typed_id("static-report", body),
            **body,
        }
        before = self.store.list_record_names("state/sha256", maximum_count=100)
        with self.assertRaises(EcosystemError) as raised:
            propose_evidence_outcome(
                subject_record=self.revision,
                tree=self.tree,
                intake_attempt=self.attempt,
                store=self.store,
                policy=self.policy,
                evidence_records=[forged],
                to_outcome="INSUFFICIENT_EVIDENCE",
                reason_codes=["ANALYZER_UNAVAILABLE"],
            )
        self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")
        self.assertEqual(
            self.store.list_record_names("state/sha256", maximum_count=100), before
        )

    def test_self_consistent_static_metadata_cannot_reject(self) -> None:
        subject_sha256 = canonical_sha256(self.revision)
        finding_body = {
            "subject_id": self.revision["revision_id"],
            "subject_sha256": subject_sha256,
            "rule_id": "credential.filename",
            "rule_version": "1",
            "analyzer_id": "nexus.ecosystem-static",
            "analyzer_version": "1",
            "analyzer_config_sha256": self.policy.static_analyzer_config_sha256,
            "category": "NETWORK_OR_CREDENTIAL",
            "severity": "CRITICAL",
            "disposition": "REJECTS_CANDIDATE",
            "path_sha256": hashlib.sha256(b"forged/.env").hexdigest(),
            "evidence_sha256": "0" * 64,
            "reason_code": "STATIC_FINDING_REJECTED",
            "summary": "Synthetic self-consistent metadata only.",
            "redaction_applied": False,
            "truncation_applied": False,
            "authority": zero_authority(),
        }
        forged_finding = {
            "schema_version": "nexus.ecosystem-static-finding.v1",
            "finding_id": typed_id("finding", finding_body),
            **finding_body,
        }
        report_body = {
            "subject_id": self.revision["revision_id"],
            "subject_sha256": subject_sha256,
            "analyzer_id": "nexus.ecosystem-static",
            "analyzer_version": "1",
            "analyzer_config_sha256": self.policy.static_analyzer_config_sha256,
            "finding_ids": [forged_finding["finding_id"]],
            "counts": {"observed": 0, "requires_review": 0, "blocking": 0, "rejecting": 1},
            "analysis_status": "COMPLETE",
            "result": "REJECTED",
            "reason_codes": ["STATIC_FINDING_REJECTED"],
            "authority": zero_authority(),
        }
        forged_report = {
            "schema_version": "nexus.ecosystem-static-report.v1",
            "report_id": typed_id("static-report", report_body),
            **report_body,
        }
        before = self.store.list_record_names("state/sha256", maximum_count=100)
        with self.assertRaises(EcosystemError) as raised:
            propose_rejection(
                subject_record=self.revision,
                tree=self.tree,
                intake_attempt=self.attempt,
                store=self.store,
                policy=self.policy,
                evidence_records=[forged_finding, forged_report],
                reason_codes=["STATIC_FINDING_REJECTED"],
            )
        self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")
        self.assertEqual(
            self.store.list_record_names("state/sha256", maximum_count=100), before
        )

    def test_policy_defined_fatal_bundle_can_reject_and_is_terminal(self) -> None:
        fatal = self._fatal_subject()
        proposal = propose_rejection(
            subject_record=fatal["revision"],
            tree=fatal["tree"],
            intake_attempt=fatal["attempt"],
            store=fatal["store"],
            policy=self.policy,
            evidence_records=fatal["evidence"],
            reason_codes=["STATIC_FINDING_REJECTED"],
        )
        rejected = append_state_transition(
            proposal=proposal,
            subject_record=fatal["revision"],
            tree=fatal["tree"],
            intake_attempt=fatal["attempt"],
            store=fatal["store"],
            policy=self.policy,
            evidence_records=fatal["evidence"],
            evaluation_receipts=[],
        )
        self.assertEqual(rejected["state"]["disposition"], "REJECTED")
        lineage = load_state_lineage(
            store=fatal["store"],
            subject_id=fatal["revision"]["revision_id"],
            subject_sha256=canonical_sha256(fatal["revision"]),
            policy=self.policy,
        )
        self.assertEqual(lineage[-1]["state_record"], rejected)
        with self.assertRaises(EcosystemError) as raised:
            propose_evidence_outcome(
                subject_record=fatal["revision"],
                tree=fatal["tree"],
                intake_attempt=fatal["attempt"],
                store=fatal["store"],
                policy=self.policy,
                evidence_records=[fatal["evidence"][0]],
                to_outcome="IN_PROGRESS",
                reason_codes=[],
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")

    def test_insufficient_evidence_requires_exact_bundle_and_new_complete_evidence(self) -> None:
        insufficient = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        append_state_transition(
            proposal=insufficient,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            evaluation_receipts=[],
        )
        resumed = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.provenance],
            to_outcome="IN_PROGRESS",
            reason_codes=[],
        )
        state = append_state_transition(
            proposal=resumed,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.provenance],
            evaluation_receipts=[],
        )
        self.assertEqual(state["state"]["evidence_outcome"], "IN_PROGRESS")
        self.assertEqual(state["state"]["disposition"], "QUARANTINED")

    def test_failed_state_publication_leaves_lineage_and_staging_unchanged(self) -> None:
        proposal = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        before = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
        )
        original = QuarantineStore._publish_record

        def fail_state_record(instance, relative, payload, *, maximum_bytes, writer_token):
            if relative.startswith("state/sha256/"):
                raise EcosystemError("CAS_OBJECT_CONFLICT", "synthetic state publication failure")
            return original(
                instance,
                relative,
                payload,
                maximum_bytes=maximum_bytes,
                writer_token=writer_token,
            )

        with patch.object(QuarantineStore, "_publish_record", new=fail_state_record):
            with self.assertRaises(EcosystemError) as raised:
                append_state_transition(
                    proposal=proposal,
                    subject_record=self.revision,
                    tree=self.tree,
                    intake_attempt=self.attempt,
                    store=self.store,
                    policy=self.policy,
                    evidence_records=[self.unavailable_static_report],
                    evaluation_receipts=[],
                )
        self.assertEqual(raised.exception.reason_code, "CAS_OBJECT_CONFLICT")
        after = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
        )
        self.assertEqual(after, before)
        self.assertEqual(list((self.store.root / "tmp").iterdir()), [])

    def test_current_use_detects_terminal_evidence_tamper_without_demotion(self) -> None:
        self._advance_to_terminal()
        before = self.store.list_record_names("state/sha256", maximum_count=100)
        evidence_path = (
            self.store.root
            / "evidence"
            / "sha256"
            / f"{self.provenance['evidence_id'].split('/', 1)[1]}.json"
        )
        evidence_path.write_bytes(b"{}")
        with self.assertRaises(EcosystemError) as raised:
            load_state_lineage(
                store=self.store,
                subject_id=self.revision["revision_id"],
                subject_sha256=canonical_sha256(self.revision),
                policy=self.policy,
                registry=self.registry,
            )
        self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")
        self.assertEqual(
            self.store.list_record_names("state/sha256", maximum_count=100), before
        )

    def test_terminal_missing_or_unavailable_evidence_fails_without_state_write(self) -> None:
        self._advance_to_terminal()
        before = self.store.list_record_names("state/sha256", maximum_count=100)
        evidence_path = (
            self.store.root
            / "evidence"
            / "sha256"
            / f"{self.provenance['evidence_id'].split('/', 1)[1]}.json"
        )
        evidence_bytes = evidence_path.read_bytes()
        evidence_path.unlink()
        try:
            with self.subTest(case="missing-terminal-evidence"), self.assertRaises(
                EcosystemError
            ) as raised:
                load_state_lineage(
                    store=self.store,
                    subject_id=self.revision["revision_id"],
                    subject_sha256=canonical_sha256(self.revision),
                    policy=self.policy,
                    registry=self.registry,
                )
            self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")
        finally:
            evidence_path.write_bytes(evidence_bytes)

        with patch(
            "ash.ecosystem_evidence.analyze_static_evidence",
            side_effect=RuntimeError("synthetic analyzer unavailable"),
        ):
            with self.subTest(case="post-terminal-analyzer-unavailable"), self.assertRaises(
                EcosystemError
            ) as raised:
                load_state_lineage(
                    store=self.store,
                    subject_id=self.revision["revision_id"],
                    subject_sha256=canonical_sha256(self.revision),
                    policy=self.policy,
                    registry=self.registry,
                )
            self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")

        with self.subTest(case="post-terminal-registry-unavailable"), self.assertRaises(
            EcosystemError
        ) as raised:
            load_state_lineage(
                store=self.store,
                subject_id=self.revision["revision_id"],
                subject_sha256=canonical_sha256(self.revision),
                policy=self.policy,
            )
        self.assertEqual(raised.exception.reason_code, "PROVENANCE_INSUFFICIENT")
        self.assertEqual(
            self.store.list_record_names("state/sha256", maximum_count=100), before
        )

    def test_persisted_missing_parent_and_cycle_corruption_fail_closed(self) -> None:
        lineage = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
        )
        head = lineage[-1]
        maximum = self.policy.resource_limits["max_record_bytes"]
        missing_parent = "state-record/" + ("f" * 64)
        orphan = build_state_record(
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            previous_state_record_id=missing_parent,
            transition=head["transition"],
        )
        orphan_path = (
            self.store.root
            / "state"
            / "sha256"
            / f"{orphan['state_record_id'].split('/', 1)[1]}.json"
        )
        orphan_path.write_bytes(canonical_json_bytes(orphan, maximum_bytes=maximum))
        with self.subTest(case="persisted-missing-parent"), self.assertRaises(
            EcosystemError
        ) as raised:
            load_state_lineage(
                store=self.store,
                subject_id=self.revision["revision_id"],
                subject_sha256=canonical_sha256(self.revision),
                policy=self.policy,
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")
        orphan_path.unlink()

        head_record = copy.deepcopy(head["state_record"])
        head_path = (
            self.store.root
            / "state"
            / "sha256"
            / f"{head_record['state_record_id'].split('/', 1)[1]}.json"
        )
        original = head_path.read_bytes()
        head_record["previous_state_record_id"] = head_record["state_record_id"]
        head_path.write_bytes(canonical_json_bytes(head_record, maximum_bytes=maximum))
        try:
            with self.subTest(case="persisted-self-cycle"), self.assertRaises(
                EcosystemError
            ) as raised:
                load_state_lineage(
                    store=self.store,
                    subject_id=self.revision["revision_id"],
                    subject_sha256=canonical_sha256(self.revision),
                    policy=self.policy,
                )
            self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")
        finally:
            head_path.write_bytes(original)

    def test_same_transition_replay_with_different_result_bytes_conflicts(self) -> None:
        proposal = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        first = append_state_transition(
            proposal=proposal,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            evaluation_receipts=[],
        )
        first_path = (
            self.store.root
            / "state"
            / "sha256"
            / f"{first['state_record_id'].split('/', 1)[1]}.json"
        )
        first_bytes = first_path.read_bytes()
        conflicting = build_state_record(
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            previous_state_record_id="state-record/" + ("e" * 64),
            transition=proposal.record(),
        )
        conflict_path = (
            self.store.root
            / "state"
            / "sha256"
            / f"{conflicting['state_record_id'].split('/', 1)[1]}.json"
        )
        conflict_path.write_bytes(
            canonical_json_bytes(
                conflicting, maximum_bytes=self.policy.resource_limits["max_record_bytes"]
            )
        )
        with self.assertRaises(EcosystemError) as raised:
            append_state_transition(
                proposal=proposal,
                subject_record=self.revision,
                tree=self.tree,
                intake_attempt=self.attempt,
                store=self.store,
                policy=self.policy,
                evidence_records=[self.unavailable_static_report],
                evaluation_receipts=[],
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")
        self.assertEqual(first_path.read_bytes(), first_bytes)
        self.assertEqual(list((self.store.root / "tmp").iterdir()), [])

    def test_persisted_competing_branch_is_detected_fail_closed(self) -> None:
        lineage = load_state_lineage(
            store=self.store,
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            policy=self.policy,
        )
        parent_id = lineage[-1]["state_record"]["state_record_id"]
        insufficient = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        alternate = propose_evidence_outcome(
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_classification_report],
            to_outcome="INSUFFICIENT_EVIDENCE",
            reason_codes=["ANALYZER_UNAVAILABLE"],
        )
        append_state_transition(
            proposal=insufficient,
            subject_record=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[self.unavailable_static_report],
            evaluation_receipts=[],
        )
        competing_transition = alternate.record()
        competing_state = build_state_record(
            subject_id=self.revision["revision_id"],
            subject_sha256=canonical_sha256(self.revision),
            previous_state_record_id=parent_id,
            transition=competing_transition,
        )
        maximum = self.policy.resource_limits["max_record_bytes"]
        for relative, record in (
            (
                f"evidence/sha256/{competing_transition['transition_id'].split('/', 1)[1]}.json",
                competing_transition,
            ),
            (
                f"evidence/sha256/{self.unavailable_classification_report['report_id'].split('/', 1)[1]}.json",
                self.unavailable_classification_report,
            ),
            (
                f"state/sha256/{competing_state['state_record_id'].split('/', 1)[1]}.json",
                competing_state,
            ),
        ):
            path = self.store.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canonical_json_bytes(record, maximum_bytes=maximum))
        with self.assertRaises(EcosystemError) as raised:
            load_state_lineage(
                store=self.store,
                subject_id=self.revision["revision_id"],
                subject_sha256=canonical_sha256(self.revision),
                policy=self.policy,
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")

    def test_component_records_start_and_remain_quarantined(self) -> None:
        states = persist_component_revisions(
            components=self.components,
            classifications=self.classifications,
            classification_report=self.classification_report,
            revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
        )
        self.assertEqual(len(states), 1)
        component = self.components[0]
        self.assertEqual(states[0]["state"]["disposition"], "QUARANTINED")
        proposal = propose_snapshot_integrity_verified(
            subject_record=component,
            parent_revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
        )
        state = append_state_transition(
            proposal=proposal,
            subject_record=component,
            parent_revision=self.revision,
            tree=self.tree,
            intake_attempt=self.attempt,
            store=self.store,
            policy=self.policy,
            evidence_records=[component],
            evaluation_receipts=[],
        )
        self.assertEqual(state["state"]["possession_state"], "SNAPSHOT_INTEGRITY_VERIFIED")
        self.assertEqual(state["state"]["disposition"], "QUARANTINED")

    def test_policy_fatal_component_rejection_is_monotonic_and_terminal(self) -> None:
        raw = zip_bytes(
            [
                ("root/skills/demo/SKILL.md", b"Synthetic inert skill instructions."),
                ("root/skills/demo/secret.pem", b"synthetic non-secret fixture"),
            ]
        )
        receipt, candidate_id = scout_receipt(
            repository="mattpocock/skills", commit="c" * 40
        )
        bridge = bridge_scout_candidate(
            scout_receipt=receipt,
            candidate_id=candidate_id,
            source_key="github/mattpocock/skills",
            requested_input_sha256=hashlib.sha256(raw).hexdigest(),
            requested_input_size=len(raw),
            policy=self.policy,
        )
        archive = self.base / "fatal-component.zip"
        archive.write_bytes(raw)
        with open_stable_input(archive, maximum_bytes=1_000_000) as stable:
            intake = intake_pre_supplied_zip(
                bridge=bridge,
                zip_input=stable,
                policy=self.policy,
                store=self.store,
            )
        components, classifications, classification_report = classify_components(
            revision=intake["revision"],
            tree=intake["tree"],
            store=self.store,
            policy=self.policy,
        )
        persist_component_revisions(
            components=components,
            classifications=classifications,
            classification_report=classification_report,
            revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=self.store,
            policy=self.policy,
        )
        component = next(
            item for item in components if item["component_root"] == "skills/demo"
        )
        snapshot = propose_snapshot_integrity_verified(
            subject_record=component,
            parent_revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=self.store,
            policy=self.policy,
        )
        append_state_transition(
            proposal=snapshot,
            subject_record=component,
            parent_revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=self.store,
            policy=self.policy,
            evidence_records=[component],
            evaluation_receipts=[],
        )
        provenance = build_provenance_evidence(
            revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=self.store,
            policy=self.policy,
        )
        license_evidence = inspect_license_evidence(
            subject_id=component["component_revision_id"],
            subject_record=component,
            parent_revision=intake["revision"],
            tree=intake["tree"],
            store=self.store,
            policy=self.policy,
        )
        findings, report = analyze_static_evidence(
            subject_id=component["component_revision_id"],
            subject_record=component,
            parent_revision=intake["revision"],
            tree=intake["tree"],
            store=self.store,
            policy=self.policy,
            provenance_evidence=provenance,
            license_evidence=license_evidence,
            intake_attempt=intake["attempt"],
        )
        rejecting = [
            item for item in findings if item["disposition"] == "REJECTS_CANDIDATE"
        ]
        self.assertTrue(rejecting)
        evidence = [provenance, license_evidence, *findings, report]
        reasons = sorted({item["reason_code"] for item in rejecting})
        proposal = propose_rejection(
            subject_record=component,
            parent_revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=self.store,
            policy=self.policy,
            evidence_records=evidence,
            reason_codes=reasons,
        )
        rejected = append_state_transition(
            proposal=proposal,
            subject_record=component,
            parent_revision=intake["revision"],
            tree=intake["tree"],
            intake_attempt=intake["attempt"],
            store=self.store,
            policy=self.policy,
            evidence_records=evidence,
            evaluation_receipts=[],
        )
        self.assertEqual(rejected["state"]["disposition"], "REJECTED")
        self.assertEqual(rejected["authority"], zero_authority())
        with self.assertRaises(EcosystemError):
            propose_rejection(
                subject_record=component,
                parent_revision=intake["revision"],
                tree=intake["tree"],
                intake_attempt=intake["attempt"],
                store=self.store,
                policy=self.policy,
                evidence_records=evidence,
                reason_codes=reasons,
            )

    def test_registry_contains_exact_seven_zero_execution_ecosystem_validators(self) -> None:
        ecosystem = [
            item for item in self.registry.validators if item.validator_id.startswith("nexus.validator.ecosystem-")
        ]
        self.assertEqual(len(ecosystem), 7)
        self.assertTrue(all(item.requires_executed_subject is False for item in ecosystem))
        self.assertTrue(all(item.pass_transition == "validation_passed" for item in ecosystem))

    def test_exact_registry_definitions_and_manifest_bound_profile_digests_are_frozen(self) -> None:
        expected_digests = {
            "nexus.profile.ecosystem-classification": "0a87866888c4315f3788affcea0233f42501978984fc4d77e69cd43deafa486e",
            "nexus.profile.ecosystem-comparison-consistency": "75253e02654159d59ab8c5b096f009e7487c3f931ea0727ae3d89d0e3f5b798c",
            "nexus.profile.ecosystem-intake-bridge-consistency": "f3d69746c1f3245ea3958cefc0c6157f04e2f8e76f32a14472defe96343929a2",
            "nexus.profile.ecosystem-provenance": "170ae1805de21dda6ce03e0701923dc2325227f6fc63476139b128d947393db0",
            "nexus.profile.ecosystem-review-bundle": "41f9ba01df7b7f733c83ea60787f7da7e870d5cb24cd8cf41965e3a62e41d33e",
            "nexus.profile.ecosystem-static-security": "8c9d0cde8a7398c747cf159bdab0976b6bdae69bc46d90463734a137de401f41",
            "nexus.profile.ecosystem-validation-bundle": "d4542f12ba0d5e90371b07e09fe06579480614c9ddec5165e234bc45424bf87a",
        }
        expected_checks = {
            "nexus.profile.ecosystem-classification": [
                "classification-status",
                "classifier-config",
                "unresolved-paths",
            ],
            "nexus.profile.ecosystem-comparison-consistency": ["comparison-record"],
            "nexus.profile.ecosystem-intake-bridge-consistency": ["bridge-record"],
            "nexus.profile.ecosystem-provenance": ["subject-digest"],
            "nexus.profile.ecosystem-review-bundle": ["prior-review-state"],
            "nexus.profile.ecosystem-static-security": [
                "analysis-status",
                "analyzer-config",
                "blocking-findings",
                "rejecting-findings",
            ],
            "nexus.profile.ecosystem-validation-bundle": ["required-receipts"],
        }
        self.assertEqual(self.policy.evaluation_profile_sha256s, expected_digests)
        policy_profiles = self.policy.to_dict()["evaluation_profiles"]
        self.assertEqual(
            [item["validator_id"] for item in policy_profiles], sorted(_EXPECTED_VALIDATORS)
        )
        for profile in policy_profiles:
            validator_id = profile["validator_id"]
            profile_id = profile["profile_id"]
            definition = self.registry.resolve(validator_id, "1")
            expected_name, expected_type, expected_operators, expected_subjects = (
                _EXPECTED_VALIDATORS[validator_id]
            )
            self.assertEqual(definition.display_name, expected_name)
            self.assertEqual(definition.validator_type, expected_type)
            self.assertEqual(definition.operators, expected_operators)
            self.assertEqual(definition.subject_types, expected_subjects)
            self.assertEqual(definition.output_schema_version, "nexus.evaluation-contract.v1")
            self.assertEqual(definition.minimum_checks, 1)
            self.assertFalse(definition.requires_executed_subject)
            self.assertEqual(definition.pass_transition, "validation_passed")
            self.assertEqual(definition.availability, "available")
            self.assertEqual(definition.definition_source, "nexus_core")
            self.assertEqual(
                [check["check_id"] for check in profile["required_checks"]],
                expected_checks[profile_id],
            )
            loaded_profile, digest = self.policy.evaluation_profile(profile_id)
            self.assertEqual(loaded_profile, profile)
            self.assertEqual(digest, expected_digests[profile_id])

    def test_comparison_and_bridge_profiles_validate_without_creating_state(self) -> None:
        comparison_inputs = {
            "old_revision": self.revision,
            "new_revision": self.revision,
            "old_tree": self.tree,
            "new_tree": self.tree,
            "store": self.store,
            "policy": self.policy,
            "ancestry_state": "SAME",
            "old_components": self.components,
            "new_components": self.components,
            "old_classifications": self.classifications,
            "new_classifications": self.classifications,
            "old_classification_report": self.classification_report,
            "new_classification_report": self.classification_report,
            "old_license_evidence": self.license,
            "new_license_evidence": self.license,
            "old_provenance_evidence": self.provenance,
            "new_provenance_evidence": self.provenance,
            "old_intake_attempt": self.attempt,
            "new_intake_attempt": self.attempt,
        }
        comparison = compare_revisions(**comparison_inputs)
        comparison_profile = "nexus.profile.ecosystem-comparison-consistency"
        request = build_ecosystem_evaluation_request(
            profile_id=comparison_profile,
            subject_record=comparison,
            comparison_inputs=comparison_inputs,
            policy=self.policy,
            registry=self.registry,
        )
        self.assertEqual(
            request["subject"],
            expected_wire_subject(
                subject_type="ecosystem_revision_comparison",
                wire_prefix="ecosystem-revision-comparison",
                subject_id=comparison["comparison_id"],
                record=comparison,
                creator=canonical_sha256(comparison),
            ),
        )
        receipt = evaluate_contract(request, registry=self.registry)
        self.assertIsNone(
            adapt_evaluation_receipt(
                evaluation_receipt=receipt,
                profile_id=comparison_profile,
                subject_record=comparison,
                comparison_inputs=comparison_inputs,
                policy=self.policy,
                registry=self.registry,
            )
        )

        bridge_profile = "nexus.profile.ecosystem-intake-bridge-consistency"
        bridge_record = self.bridge.record()
        request = build_ecosystem_evaluation_request(
            profile_id=bridge_profile,
            subject_record=bridge_record,
            bridge=self.bridge,
            scout_receipt=self.scout_receipt,
            policy=self.policy,
            registry=self.registry,
        )
        scout_creator = hashlib.sha256(
            json.dumps(
                self.scout_receipt,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            request["subject"],
            expected_wire_subject(
                subject_type="ecosystem_intake_bridge",
                wire_prefix="ecosystem-intake-bridge",
                subject_id=bridge_record["bridge_id"],
                record=bridge_record,
                creator=scout_creator,
            ),
        )
        receipt = evaluate_contract(request, registry=self.registry)
        self.assertIsNone(
            adapt_evaluation_receipt(
                evaluation_receipt=receipt,
                profile_id=bridge_profile,
                subject_record=bridge_record,
                bridge=self.bridge,
                scout_receipt=self.scout_receipt,
                policy=self.policy,
                registry=self.registry,
            )
        )
        with self.assertRaises(EcosystemError):
            build_ecosystem_evaluation_request(
                profile_id=bridge_profile,
                subject_record=copy.deepcopy(bridge_record) | {"requested_input_size": 1},
                bridge=self.bridge,
                scout_receipt=self.scout_receipt,
                policy=self.policy,
                registry=self.registry,
            )

    def test_profile_request_and_receipt_are_deterministic_across_100_runs(self) -> None:
        profile = "nexus.profile.ecosystem-provenance"
        request = build_ecosystem_evaluation_request(profile_id=profile, **self.common)
        receipt = evaluate_contract(request, registry=self.registry)
        for _index in range(100):
            self.assertEqual(
                build_ecosystem_evaluation_request(profile_id=profile, **self.common), request
            )
            self.assertEqual(evaluate_contract(request, registry=self.registry), receipt)


if __name__ == "__main__":
    unittest.main()
