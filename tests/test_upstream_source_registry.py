from __future__ import annotations

import copy
from pathlib import Path
import unittest

from ash.upstream import UpstreamRegistryError, component_state_summary, load_upstream_registry, validate_upstream_registry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "upstream-source-registry.json"


class UpstreamSourceRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = load_upstream_registry(REGISTRY)

    def test_user_approved_sources_are_pinned_and_classified_without_runtime_authority(self) -> None:
        sources = {source["source_id"]: source for source in self.payload["sources"]}
        self.assertEqual(sources["agency-agents-canonical"]["commit"], "ebe9c99acb5c96f9468de368d8bead775387d1a7")
        self.assertEqual(sources["agency-agents-zh-overlay"]["commit"], "83248ab15a78f9ddad897369c8d0be873653574a")
        self.assertEqual(sources["emilkowalski-skills"]["commit"], "d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7")
        self.assertEqual(sources["awesome-llm-apps"]["commit"], "11a4bc330e4b0b1509577db4581c5cfbcf6ea6a0")
        self.assertEqual(sources["liquid-glass-react"]["state"], "reference_only")
        self.assertEqual(sources["deer-flow"]["state"], "reference_only")
        self.assertEqual(sources["greensock-gsap"]["state"], "license_decision_required")
        self.assertEqual(sources["green-github-org-unresolved"]["state"], "rejected_unresolved")
        policy = self.payload["registry_policy"].casefold()
        self.assertIn("no automatic clone", policy)
        self.assertIn("no automatic", policy)
        self.assertIn("agent delegation", policy)

    def test_verified_local_emil_skill_retains_content_hash_without_a_machine_path(self) -> None:
        source = next(item for item in self.payload["sources"] if item["source_id"] == "emilkowalski-skills")
        component = next(item for item in source["accepted_components"] if item["component_id"] == "emil-design-eng")
        self.assertEqual(component["state"], "locally_usable_verified")
        self.assertEqual(component["content_sha256"], "e71de849347050c2c573c1cf24d742d5a13459557ecffa6e562f08006f46b5b7")
        self.assertNotIn(":\\", str(component))

    def test_agent_overlay_is_advisory_and_not_a_skill_or_host_mapping(self) -> None:
        sources = {source["source_id"]: source for source in self.payload["sources"]}
        for source_id in ("agency-agents-canonical", "agency-agents-zh-overlay"):
            source = sources[source_id]
            self.assertEqual(source["state"], "approved_advisory_only")
            self.assertTrue(all(component["state"] == "advisory_only" for component in source["accepted_components"]))
        self.assertNotIn("host_execution_mapping", str(sources["agency-agents-canonical"]))

    def test_registry_rejects_unpinned_or_duplicate_or_unsafe_records(self) -> None:
        unpinned = copy.deepcopy(self.payload)
        unpinned["sources"][0]["commit"] = "main"
        with self.assertRaises(UpstreamRegistryError):
            validate_upstream_registry(unpinned)
        duplicate = copy.deepcopy(self.payload)
        duplicate["sources"][1]["source_id"] = duplicate["sources"][0]["source_id"]
        with self.assertRaises(UpstreamRegistryError):
            validate_upstream_registry(duplicate)
        unsafe = copy.deepcopy(self.payload)
        unsafe["sources"][0]["accepted_components"][0]["upstream_path"] = "C:/unsafe/SKILL.md"
        with self.assertRaises(UpstreamRegistryError):
            validate_upstream_registry(unsafe)
        bad_unresolved = copy.deepcopy(self.payload)
        unresolved = next(item for item in bad_unresolved["sources"] if item["source_id"] == "green-github-org-unresolved")
        unresolved["repository"] = "green/frontend"
        with self.assertRaises(UpstreamRegistryError):
            validate_upstream_registry(bad_unresolved)

    def test_state_summary_has_a_final_nonexecuting_disposition_for_each_component(self) -> None:
        summary = component_state_summary(self.payload)
        self.assertGreater(summary["advisory_only"], 0)
        self.assertGreater(summary["locally_usable_verified"], 0)
        self.assertGreater(summary["reference_only"], 0)
        self.assertGreater(summary["rejected_incompatible"], 0)
        self.assertGreater(summary["license_decision_required"], 0)
        self.assertGreater(summary["unresolved"], 0)
