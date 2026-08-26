from __future__ import annotations

import copy
from pathlib import Path
import unittest

from ash.capabilities import (
    CapabilityCatalogError,
    CapabilitySelectionError,
    MAX_CONSIDERED_CAPABILITIES,
    MAX_EXACT_SELECTION_CANDIDATES,
    load_capability_catalog,
    select_minimum_sufficient_capabilities,
    updated_revision_state,
    validate_capability,
    validate_lifecycle_transition,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "capability-foundation.json"


def capability(
    identifier: str,
    *,
    domains: list[str],
    outputs: list[str],
    validations: list[str],
    roles: list[str],
    permissions: list[str] | None = None,
) -> dict:
    return {
        "capability_id": identifier,
        "display_name": f"Display {identifier}",
        "capability_type": "skill",
        "lifecycle_state": "available",
        "trust": {"tier": "trusted_seed", "risk_status": "test fixture"},
        "compatibility": "compatible",
        "execution": {
            "mechanism": "host_mediated_skill",
            "directly_executable": True,
            "permissions": permissions or ["read_skill_instructions"],
        },
        "availability": {"state": "available", "reason": "test fixture is available"},
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
        "inputs": ["task_reference"],
        "outputs": outputs,
        "domains": domains,
        "validation_requirements": validations,
        "roles_supported": roles,
        "update_strategy": "pin and review",
    }


class CapabilityFoundationTests(unittest.TestCase):
    def test_catalog_loads_and_preserves_all_twelve_requested_sources(self) -> None:
        payload = load_capability_catalog(CATALOG)
        self.assertEqual(len(payload["capabilities"]), 12)
        source_ids = {item["provenance"]["source_id"] for item in payload["capabilities"]}
        self.assertEqual(
            source_ids,
            {
                "agency-agents-canonical",
                "agency-agents-zh-overlay",
                "awesome-llm-apps",
                "emilkowalski-skills",
                "liquid-glass-react",
                "deer-flow",
                "greensock-gsap",
                "openai-codex",
                "deepseek-harness",
                "revfactory-harness",
                "edict",
                "nuwa-skill",
            },
        )
        gsap = next(item for item in payload["capabilities"] if item["capability_id"] == "library/gsap")
        self.assertEqual(gsap["capability_type"], "library")
        self.assertFalse(gsap["execution"]["directly_executable"])
        emil = next(item for item in payload["capabilities"] if item["capability_id"] == "skill/emil-design-eng")
        self.assertEqual(emil["provenance"]["content_sha256"], "e71de849347050c2c573c1cf24d742d5a13459557ecffa6e562f08006f46b5b7")

    def test_exact_minimum_selection_assigns_creator_and_reviewer_and_rejects_redundancy(self) -> None:
        creator = capability(
            "skill/creator",
            domains=["presentations"],
            outputs=["editable_pptx"],
            validations=["artifact_exists"],
            roles=["primary_creator"],
        )
        reviewer = capability(
            "skill/reviewer",
            domains=[],
            outputs=[],
            validations=["render_review"],
            roles=["reviewer"],
        )
        redundant = capability(
            "skill/redundant",
            domains=["presentations"],
            outputs=["editable_pptx"],
            validations=["artifact_exists"],
            roles=["primary_creator"],
            permissions=["read_skill_instructions", "write_artifact"],
        )
        result = select_minimum_sufficient_capabilities(
            [creator, reviewer, redundant],
            {
                "domains": ["presentations"],
                "outputs": ["editable_pptx"],
                "validation_requirements": ["artifact_exists", "render_review"],
                "allowed_permissions": ["read_skill_instructions", "write_artifact"],
                "allowed_execution_mechanisms": ["host_mediated_skill"],
            },
        )
        self.assertEqual(result["status"], "MINIMUM_SUFFICIENT_SET_SELECTED")
        self.assertEqual(result["selected"], ["skill/creator", "skill/reviewer"])
        dispositions = {item["capability_id"]: item for item in result["dispositions"]}
        self.assertEqual(dispositions["skill/creator"]["role"], "primary_creator")
        self.assertEqual(dispositions["skill/reviewer"]["role"], "reviewer")
        self.assertEqual(dispositions["skill/redundant"]["role"], "redundant")

    def test_display_name_does_not_grant_selection_authority(self) -> None:
        item = capability("skill/not-presentation", domains=["frontend"], outputs=["web_ui"], validations=[], roles=["primary_creator"])
        item["display_name"] = "Presentations Ultimate PPT Creator"
        result = select_minimum_sufficient_capabilities(
            [item],
            {
                "domains": ["presentations"],
                "outputs": ["editable_pptx"],
                "validation_requirements": [],
                "allowed_permissions": ["read_skill_instructions"],
                "allowed_execution_mechanisms": ["host_mediated_skill"],
            },
        )
        self.assertEqual(result["status"], "CAPABILITY_NOT_COVERED")
        self.assertEqual(result["selected"], [])

    def test_agent_is_advisory_and_never_enters_executable_set(self) -> None:
        item = load_capability_catalog(CATALOG)["capabilities"][0]
        result = select_minimum_sufficient_capabilities(
            [item],
            {
                "domains": ["software_architecture"],
                "outputs": ["advisory_architecture_review"],
                "validation_requirements": [],
                "allowed_permissions": ["read_metadata"],
                "allowed_execution_mechanisms": ["advisory_only"],
            },
        )
        self.assertEqual(result["selected"], [])
        self.assertEqual(result["dispositions"][0]["role"], "advisory")

    def test_host_native_requires_fresh_current_turn_observation(self) -> None:
        item = capability("skill/host", domains=["presentations"], outputs=["editable_pptx"], validations=[], roles=["primary_creator"])
        item["execution"]["mechanism"] = "host_native"
        with self.assertRaises(CapabilityCatalogError):
            validate_capability(item)
        item["host_visibility"] = {
            "scope": "current_turn_host_visible_subset",
            "enumeration": "not_globally_enumerated",
            "observed_current_turn": True,
        }
        self.assertEqual(validate_capability(item)["host_visibility"]["scope"], "current_turn_host_visible_subset")

    def test_unsafe_authority_and_paths_fail_closed(self) -> None:
        item = capability("skill/unsafe", domains=["code"], outputs=["patch"], validations=[], roles=["primary_creator"])
        item["execution"]["permissions"].append("shell")
        with self.assertRaises(CapabilityCatalogError):
            validate_capability(item)
        item = capability("skill/path", domains=["code"], outputs=["patch"], validations=[], roles=["primary_creator"])
        item["provenance"]["relative_path"] = "C:/Users/private/SKILL.md"
        with self.assertRaises(CapabilityCatalogError):
            validate_capability(item)

    def test_lifecycle_is_monotonic_and_revision_changes_quarantine_approval(self) -> None:
        self.assertEqual(validate_lifecycle_transition("tested", "approved"), "approved")
        with self.assertRaises(CapabilityCatalogError):
            validate_lifecycle_transition("classified", "approved")
        previous = capability("skill/revision", domains=["code"], outputs=["patch"], validations=[], roles=["primary_creator"])
        candidate = copy.deepcopy(previous)
        candidate["provenance"]["commit"] = "c" * 40
        self.assertEqual(updated_revision_state(previous, candidate), "quarantined")

    def test_exact_selection_is_bounded(self) -> None:
        items = [
            capability(f"skill/item-{index}", domains=["domain"], outputs=["output"], validations=[], roles=["primary_creator"])
            for index in range(MAX_EXACT_SELECTION_CANDIDATES + 1)
        ]
        with self.assertRaises(CapabilitySelectionError):
            select_minimum_sufficient_capabilities(
                items,
                {
                    "domains": ["domain"],
                    "outputs": ["output"],
                    "validation_requirements": [],
                    "allowed_permissions": ["read_skill_instructions"],
                    "allowed_execution_mechanisms": ["host_mediated_skill"],
                },
            )

    def test_untrusted_or_unpinned_capability_cannot_claim_execution_authority(self) -> None:
        untrusted = capability(
            "skill/untrusted",
            domains=["code"],
            outputs=["patch"],
            validations=[],
            roles=["primary_creator"],
        )
        untrusted["trust"]["tier"] = "untrusted"
        with self.assertRaisesRegex(CapabilityCatalogError, "trust is insufficient"):
            validate_capability(untrusted)

        unpinned = capability(
            "skill/unpinned",
            domains=["code"],
            outputs=["patch"],
            validations=[],
            roles=["primary_creator"],
        )
        unpinned["provenance"]["content_sha256"] = None
        with self.assertRaisesRegex(CapabilityCatalogError, "pinned content integrity"):
            validate_capability(unpinned)

    def test_selector_rejects_duplicate_ids_and_unbounded_considered_input(self) -> None:
        item = capability(
            "skill/duplicate",
            domains=["code"],
            outputs=["patch"],
            validations=[],
            roles=["primary_creator"],
        )
        requirements = {
            "domains": ["code"],
            "outputs": ["patch"],
            "validation_requirements": [],
            "allowed_permissions": ["read_skill_instructions"],
            "allowed_execution_mechanisms": ["host_mediated_skill"],
        }
        with self.assertRaisesRegex(CapabilitySelectionError, "ID is duplicated"):
            select_minimum_sufficient_capabilities([item, copy.deepcopy(item)], requirements)

        too_many = [
            capability(
                f"skill/considered-{index}",
                domains=[],
                outputs=[],
                validations=[],
                roles=["alternative"],
            )
            for index in range(MAX_CONSIDERED_CAPABILITIES + 1)
        ]
        with self.assertRaisesRegex(CapabilitySelectionError, "bounded consideration"):
            select_minimum_sufficient_capabilities(too_many, requirements)


if __name__ == "__main__":
    unittest.main()
