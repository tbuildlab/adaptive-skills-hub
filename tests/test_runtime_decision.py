from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from ash.capabilities import MAX_EXACT_SELECTION_CANDIDATES
from ash.mcp.handoff import strict_handoff_digest_for_execution_start
from ash.mcp.host_inventory import (
    HostCapability,
    HostCapabilitySnapshot,
    assess_host_capabilities,
)
from ash.mcp.host_mapping import (
    HOST_SKILL_WORKFLOW_BINDING,
    PRESENTATIONS_HOST_CAPABILITY_ID,
    PRESENTATIONS_HOST_PROVIDER_ID,
    PRESENTATIONS_MAPPING_ID,
)
from ash.runtime_decision import (
    RUNTIME_DECISION_SCHEMA_VERSION,
    RUNTIME_REQUIREMENTS_SCHEMA_VERSION,
    RuntimeCapabilityAdapter,
    RuntimeDecisionError,
    build_runtime_decision,
    host_runtime_decision,
    parse_runtime_requirements,
    prepare_catalog_runtime_candidates,
    validate_runtime_decision_envelope,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "capability-foundation.json"
UPSTREAM = ROOT / "config" / "upstream-source-registry.json"
LIBRARY = ROOT.parent / "adaptive-skills-library"


def requirements(
    *,
    category: str = "frontend",
    domains: list[str] | None = None,
    outputs: list[str] | None = None,
    validations: list[str] | None = None,
    permissions: list[str] | None = None,
    mechanisms: list[str] | None = None,
) -> dict:
    return {
        "schema_version": RUNTIME_REQUIREMENTS_SCHEMA_VERSION,
        "requirements_id": "req:test-001",
        "requirements_version": "1",
        "task_category": category,
        "domains": domains if domains is not None else ["frontend"],
        "outputs": outputs if outputs is not None else ["frontend_implementation"],
        "validation_requirements": validations if validations is not None else [
            "visual_review", "accessibility_review",
        ],
        "allowed_permissions": permissions if permissions is not None else [
            "read_skill_instructions", "write_artifact",
        ],
        "allowed_execution_mechanisms": mechanisms if mechanisms is not None else [
            "host_mediated_skill",
        ],
    }


def executable_capability(
    identifier: str,
    *,
    outputs: list[str],
    validations: list[str],
    roles: list[str],
) -> dict:
    return {
        "capability_id": identifier,
        "display_name": "Untrusted display label ignored",
        "capability_type": "skill",
        "lifecycle_state": "available",
        "trust": {"tier": "trusted_seed", "risk_status": "test fixture"},
        "compatibility": "compatible",
        "execution": {
            "mechanism": "host_mediated_skill",
            "directly_executable": True,
            "permissions": ["read_skill_instructions"],
        },
        "availability": {"state": "available", "reason": "test fixture"},
        "host_visibility": {
            "scope": "local_registry",
            "enumeration": "not_applicable",
            "observed_current_turn": False,
        },
        "provenance": {
            "source_id": f"source-{identifier}",
            "source_scope": "external_upstream",
            "repository": "example/repository",
            "commit": "a" * 40,
            "content_sha256": "b" * 64,
            "relative_path": "skills/SKILL.md",
            "import_mode": "referenced",
        },
        "dependencies": [],
        "inputs": ["bounded_reference"],
        "outputs": outputs,
        "domains": ["artifact"],
        "validation_requirements": validations,
        "roles_supported": roles,
        "update_strategy": "pin and review",
    }


def mapped_presentations_snapshot(*, include_unmapped: bool = False) -> HostCapabilitySnapshot:
    items = [
        HostCapability(
            capability_id=PRESENTATIONS_HOST_CAPABILITY_ID,
            provider_id=PRESENTATIONS_HOST_PROVIDER_ID,
            display_name="Presentation label is not authority",
            resource_kind="skill",
            availability="skill_workflow_ready_current_turn",
            evidence=(
                "current_turn_execution_substrate",
                "current_turn_skill_instructions",
                "current_turn_skill_metadata",
                "current_turn_tool_catalog",
            ),
            interfaces=("editable_pptx_create", "pptx_open_render_validate"),
            logical_capability="chatgpt.presentations",
            execution_binding_kind=HOST_SKILL_WORKFLOW_BINDING,
        )
    ]
    if include_unmapped:
        for capability_id in ("ppt-master", "dashai-ppt", "emil-design-eng"):
            items.append(HostCapability(
                capability_id=capability_id,
                provider_id="host-visible",
                display_name="Visible but unmapped",
                resource_kind="skill",
                availability="metadata_visible",
                evidence=("current_turn_skill_metadata",),
                interfaces=("presentation_review",),
                logical_capability="unmapped",
                execution_binding_kind="none",
            ))
    return HostCapabilitySnapshot(
        ticket_id="11111111-1111-4111-8111-111111111111",
        snapshot_id="22222222-2222-4222-8222-222222222222",
        host_surface="chatgpt_desktop",
        inventory_scope="current_turn_host_visible_subset",
        inventory_completeness="not_globally_enumerated",
        task_category="presentation",
        required_interfaces=("editable_pptx_create", "pptx_open_render_validate"),
        capabilities=tuple(items),
    )


class RuntimeDecisionTests(unittest.TestCase):
    def adapter(self, root: Path = LIBRARY) -> RuntimeCapabilityAdapter:
        return RuntimeCapabilityAdapter(
            CATALOG,
            UPSTREAM,
            local_roots={"emilkowalski-skills": root},
        )

    def test_verified_local_skill_is_selected_but_never_reported_executed(self) -> None:
        result = self.adapter().decide(parse_runtime_requirements(requirements()))
        self.assertEqual(result["schema_version"], RUNTIME_DECISION_SCHEMA_VERSION)
        self.assertEqual(result["result_code"], "RUNTIME_CAPABILITY_SELECTION_READY")
        self.assertEqual(
            [item["capability_id"] for item in result["selected_capabilities"]],
            ["skill/emil-design-eng"],
        )
        self.assertEqual(result["selected_capabilities"][0]["assigned_role"], "primary_creator")
        self.assertEqual(result["evidence_states"], {
            "selection": "selected",
            "execution": "not_executed",
            "validation": "not_validated",
        })
        self.assertEqual(result["security_result"]["mcp_execution_authority"], "none")
        self.assertLessEqual(
            len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")),
            24 * 1024,
        )

    def test_missing_or_changed_local_skill_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            missing = self.adapter(Path(temp)).decide(parse_runtime_requirements(requirements()))
            self.assertEqual(missing["selected_capabilities"], [])
            emil = next(
                item for item in missing["considered_capabilities"]
                if item["capability_id"] == "skill/emil-design-eng"
            )
            self.assertEqual(emil["availability_state"], "unavailable")

            root = Path(temp)
            target = root / "emil-design-eng" / "SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text("changed", encoding="utf-8")
            changed = self.adapter(root).decide(parse_runtime_requirements(requirements()))
            emil = next(
                item for item in changed["considered_capabilities"]
                if item["capability_id"] == "skill/emil-design-eng"
            )
            self.assertEqual(emil["assigned_role"], "rejected")
            self.assertEqual(emil["reason_code"], "lifecycle_quarantined")

    def test_changed_upstream_commit_is_quarantined_before_selection(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
        emil = next(item for item in catalog["capabilities"] if item["capability_id"] == "skill/emil-design-eng")
        emil["provenance"]["commit"] = "c" * 40
        prepared = prepare_catalog_runtime_candidates(
            catalog,
            upstream,
            local_roots={"emilkowalski-skills": LIBRARY},
        )
        changed = next(item for item in prepared if item["capability_id"] == "skill/emil-design-eng")
        self.assertEqual(changed["lifecycle_state"], "quarantined")
        self.assertFalse(changed["execution"]["directly_executable"])

    def test_catalog_or_registry_manifest_mismatch_blocks_runtime_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "config"
            config.mkdir()
            catalog = config / CATALOG.name
            upstream = config / UPSTREAM.name
            shutil.copyfile(CATALOG, catalog)
            shutil.copyfile(UPSTREAM, upstream)
            manifest = {
                path.relative_to(root).as_posix(): {
                    "bytes": len(path.read_bytes()),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for path in (catalog, upstream)
            }
            manifest_path = root / "MANIFEST.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            adapter = RuntimeCapabilityAdapter(
                catalog,
                upstream,
                local_roots={"emilkowalski-skills": root / "missing"},
                integrity_manifest_path=manifest_path,
            )
            request = parse_runtime_requirements(requirements(
                category="presentation",
                domains=["presentation"],
                outputs=["editable_pptx_create"],
                validations=["pptx_open_render_validate"],
                permissions=["write_artifact"],
                mechanisms=["host_native"],
            ))
            self.assertEqual(adapter.decide(request)["result_code"], "HOST_EVIDENCE_REQUIRED")
            catalog.write_text(catalog.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeDecisionError, "integrity check failed"):
                adapter.decide(request)

    def test_presentation_without_current_host_evidence_uses_explicit_r5_path(self) -> None:
        request = requirements(
            category="presentation",
            domains=["presentation"],
            outputs=["editable_pptx_create"],
            validations=["pptx_open_render_validate"],
            permissions=["write_artifact"],
            mechanisms=["host_native"],
        )
        result = self.adapter().decide(parse_runtime_requirements(request))
        self.assertEqual(result["result_code"], "HOST_EVIDENCE_REQUIRED")
        self.assertEqual(result["compatibility"]["route"], "r5_current_turn_host_capability_assessment")
        self.assertEqual(result["selected_capabilities"], [])
        self.assertNotIn("skill/emil-design-eng", [
            item["capability_id"] for item in result["selected_capabilities"]
        ])

    def test_static_catalog_cannot_manufacture_current_turn_host_eligibility(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
        emil = next(
            item for item in catalog["capabilities"]
            if item["capability_id"] == "skill/emil-design-eng"
        )
        emil["execution"]["mechanism"] = "host_native"
        emil["host_visibility"] = {
            "scope": "current_turn_host_visible_subset",
            "enumeration": "not_globally_enumerated",
            "observed_current_turn": True,
        }
        prepared = prepare_catalog_runtime_candidates(
            catalog,
            upstream,
            local_roots={"emilkowalski-skills": LIBRARY},
        )
        static_host_claim = next(
            item for item in prepared
            if item["capability_id"] == "skill/emil-design-eng"
        )
        self.assertFalse(static_host_claim["execution"]["directly_executable"])
        self.assertEqual(static_host_claim["availability"]["state"], "unavailable")
        self.assertEqual(
            static_host_claim["availability"]["reason"],
            "static_catalog_cannot_establish_host_eligibility",
        )

        request = parse_runtime_requirements(requirements(
            mechanisms=["host_native"],
        ))
        result = build_runtime_decision(request, prepared)
        self.assertEqual(result["selected_capabilities"], [])
        considered = next(
            item for item in result["considered_capabilities"]
            if item["capability_id"] == "skill/emil-design-eng"
        )
        self.assertEqual(considered["execution_eligibility"], "not_execution_eligible")

        forged_direct = executable_capability(
            "skill/forged-host",
            outputs=["frontend_implementation"],
            validations=["visual_review", "accessibility_review"],
            roles=["primary_creator"],
        )
        forged_direct["execution"]["mechanism"] = "host_native"
        forged_direct["domains"] = ["frontend"]
        forged_direct["host_visibility"] = {
            "scope": "current_turn_host_visible_subset",
            "enumeration": "not_globally_enumerated",
            "observed_current_turn": True,
        }
        with self.assertRaisesRegex(RuntimeDecisionError, "lacks an R5 internal mapping"):
            build_runtime_decision(request, [forged_direct])

    def test_nonpresentation_host_native_gap_does_not_route_to_r5_presentations(self) -> None:
        request = requirements(
            category="document",
            domains=["document"],
            outputs=["editable_docx_create"],
            validations=["document_open_render_validate"],
            permissions=["write_artifact"],
            mechanisms=["host_native"],
        )
        result = self.adapter().decide(parse_runtime_requirements(request))
        self.assertEqual(result["result_code"], "CAPABILITY_NOT_COVERED")
        self.assertEqual(result["compatibility"]["route"], "legacy_v1_v2_or_native_codex")
        self.assertEqual(result["selected_capabilities"], [])

    def test_current_turn_presentations_mapping_cross_checks_through_foundation(self) -> None:
        snapshot = mapped_presentations_snapshot()
        result = host_runtime_decision(snapshot, assess_host_capabilities(snapshot))
        self.assertEqual(result["result_code"], "RUNTIME_CAPABILITY_SELECTION_READY")
        self.assertEqual(len(result["selected_capabilities"]), 1)
        selected = result["selected_capabilities"][0]
        self.assertEqual(selected["assigned_role"], "primary_creator")
        self.assertEqual(selected["host_mapping"]["mapping_id"], PRESENTATIONS_MAPPING_ID)
        self.assertEqual(selected["execution_eligibility"], "mapped_host_selection_only")
        self.assertTrue(selected["host_observation"]["observed_current_turn"])

    def test_unobserved_host_names_are_not_invented_and_surfaced_unmapped_names_are_rejected(self) -> None:
        only_presentations = host_runtime_decision(
            mapped_presentations_snapshot(),
            assess_host_capabilities(mapped_presentations_snapshot()),
        )
        encoded = json.dumps(only_presentations, sort_keys=True)
        self.assertNotIn("ppt-master", encoded)
        self.assertNotIn("dashai-ppt", encoded)
        self.assertNotIn("emil-design-eng", encoded)

        surfaced = mapped_presentations_snapshot(include_unmapped=True)
        result = host_runtime_decision(surfaced, assess_host_capabilities(surfaced))
        rejected = {item["capability_id"]: item for item in result["rejected_capabilities"]}
        for capability_id in ("ppt-master", "dashai-ppt", "emil-design-eng"):
            item = rejected[f"host/host-visible/{capability_id}"]
            self.assertEqual(item["assigned_role"], "rejected")
            self.assertEqual(item["reason_code"], "insufficient_trust_state")

    def test_caller_cannot_supply_identity_provider_mapping_or_candidates(self) -> None:
        for field, value in (
            ("capability_id", "skill/forged"),
            ("provider_id", "attacker"),
            ("mapping_id", PRESENTATIONS_MAPPING_ID),
            ("candidate_capability_ids", ["skill/forged"]),
        ):
            forged = requirements()
            forged[field] = value
            with self.assertRaisesRegex(RuntimeDecisionError, "malformed"):
                parse_runtime_requirements(forged)

    def test_host_mapping_argument_is_internal_only(self) -> None:
        item = executable_capability(
            "skill/creator",
            outputs=["artifact"],
            validations=[],
            roles=["primary_creator"],
        )
        req = parse_runtime_requirements(requirements(
            category="artifact",
            domains=["artifact"],
            outputs=["artifact"],
            validations=[],
            permissions=["read_skill_instructions"],
        ))
        with self.assertRaisesRegex(RuntimeDecisionError, "R5 internal assessment"):
            build_runtime_decision(
                req,
                [item],
                host_mappings={
                    "skill/creator": {
                        "mapping_id": PRESENTATIONS_MAPPING_ID,
                        "provider_id": PRESENTATIONS_HOST_PROVIDER_ID,
                        "capability_id": PRESENTATIONS_HOST_CAPABILITY_ID,
                        "execution_binding_kind": HOST_SKILL_WORKFLOW_BINDING,
                    }
                },
            )

    def test_permission_and_mechanism_mismatch_are_incompatible(self) -> None:
        for permission_set, mechanisms in (
            (["read_skill_instructions"], ["host_mediated_skill"]),
            (["read_skill_instructions", "write_artifact"], ["nexus_local_read_plan"]),
        ):
            result = self.adapter().decide(parse_runtime_requirements(requirements(
                permissions=permission_set,
                mechanisms=mechanisms,
            )))
            emil = next(
                item for item in result["considered_capabilities"]
                if item["capability_id"] == "skill/emil-design-eng"
            )
            self.assertEqual(emil["assigned_role"], "incompatible")
            self.assertEqual(result["selected_capabilities"], [])

    def test_disabled_capability_is_unavailable_not_selected(self) -> None:
        item = executable_capability(
            "skill/disabled", outputs=["artifact"], validations=[], roles=["primary_creator"],
        )
        item["execution"]["directly_executable"] = False
        item["availability"] = {"state": "disabled", "reason": "explicitly disabled"}
        req = parse_runtime_requirements(requirements(
            category="artifact",
            domains=["artifact"],
            outputs=["artifact"],
            validations=[],
            permissions=["read_skill_instructions"],
        ))
        result = build_runtime_decision(req, [item])
        self.assertEqual(result["selected_capabilities"], [])
        self.assertEqual(result["considered_capabilities"][0]["assigned_role"], "unavailable")
        self.assertEqual(result["considered_capabilities"][0]["reason_code"], "disabled")

    def test_agents_remain_advisory_and_never_enter_selected_set(self) -> None:
        result = self.adapter().decide(parse_runtime_requirements(requirements(
            category="software_architecture",
            domains=["software_architecture"],
            outputs=["advisory_architecture_review"],
            validations=[],
            permissions=["read_metadata"],
            mechanisms=["advisory_only"],
        )))
        self.assertIn("agent/agency-agents/software-architect", result["advisory_capabilities"])
        self.assertEqual(result["selected_capabilities"], [])
        self.assertEqual(result["evidence_states"]["execution"], "not_executed")

    def test_reviewer_and_enhancer_roles_are_bounded_and_execution_deferred(self) -> None:
        creator = executable_capability(
            "skill/creator", outputs=["artifact"], validations=[], roles=["primary_creator"],
        )
        reviewer = executable_capability(
            "skill/reviewer", outputs=[], validations=["review"], roles=["reviewer"],
        )
        enhancer = executable_capability(
            "skill/enhancer", outputs=["enhanced_artifact"], validations=[], roles=["enhancer"],
        )
        req = parse_runtime_requirements(requirements(
            category="artifact",
            domains=["artifact"],
            outputs=["artifact", "enhanced_artifact"],
            validations=["review"],
            permissions=["read_skill_instructions"],
        ))
        result = build_runtime_decision(req, [creator, reviewer, enhancer])
        self.assertEqual(result["quality_loop"]["creator_ids"], ["skill/creator"])
        self.assertEqual(result["quality_loop"]["reviewer_ids"], ["skill/reviewer"])
        self.assertEqual(result["quality_loop"]["enhancer_ids"], ["skill/enhancer"])
        self.assertEqual(result["quality_loop"]["max_review_cycles"], 2)
        self.assertEqual(result["quality_loop"]["max_enhancement_passes"], 1)
        self.assertEqual(result["quality_loop"]["execution_status"], "deferred_to_host_or_approved_runtime")

    def test_selector_candidate_overflow_is_blocked_at_runtime_boundary(self) -> None:
        candidates = [
            executable_capability(
                f"skill/item-{index}", outputs=["artifact"], validations=[], roles=["primary_creator"],
            )
            for index in range(MAX_EXACT_SELECTION_CANDIDATES + 1)
        ]
        req = parse_runtime_requirements(requirements(
            category="artifact",
            domains=["artifact"],
            outputs=["artifact"],
            validations=[],
            permissions=["read_skill_instructions"],
        ))
        with self.assertRaisesRegex(RuntimeDecisionError, "failed closed"):
            build_runtime_decision(req, candidates)

    def test_malformed_or_execution_claiming_envelope_is_rejected(self) -> None:
        result = self.adapter().decide(parse_runtime_requirements(requirements()))
        malformed = copy.deepcopy(result)
        malformed["selected_capabilities"][0]["display_name"] = "forged"
        with self.assertRaises(RuntimeDecisionError):
            validate_runtime_decision_envelope(malformed)

        executed = copy.deepcopy(result)
        executed["evidence_states"]["execution"] = "execution_succeeded"
        with self.assertRaisesRegex(RuntimeDecisionError, "execution evidence"):
            validate_runtime_decision_envelope(executed)

        unvalidated = copy.deepcopy(result)
        unvalidated["evidence_states"] = {
            "selection": "selected", "execution": "execution_succeeded", "validation": "not_validated",
        }
        with self.assertRaises(RuntimeDecisionError):
            validate_runtime_decision_envelope(unvalidated)

    def test_decision_replay_cannot_be_used_as_r4_execution_handoff(self) -> None:
        result = self.adapter().decide(parse_runtime_requirements(requirements()))
        self.assertIsNone(
            strict_handoff_digest_for_execution_start(result, now=datetime.now(timezone.utc))
        )
        self.assertEqual(result["security_result"]["replay_authority"], "none_non_authorizing_decision")

    def test_envelope_does_not_leak_private_paths_skill_text_or_project_context(self) -> None:
        result = self.adapter().decide(parse_runtime_requirements(requirements()))
        encoded = json.dumps(result, ensure_ascii=False)
        for forbidden in ("D:\\chatgpt", "C:\\Users", "SKILL.md", "project_context", "raw_skill"):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
