"""Additive catalog metadata; real registry identity, no permission grants."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from ash.mcp.adapter import NexusMcpRuntime
from ash.mcp.redaction import safe_catalog, MAX_CATALOG_DESCRIPTION_CHARS
from ash.mcp.schemas import MAX_RESPONSE_BYTES, MAX_SAFE_ENVELOPE_BYTES
from ash.semantic_domains import SemanticRoutingError, load_trusted_applicability_registry


class CatalogMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = NexusMcpRuntime._build_catalog()["skills"]
        cls.core = next(r for r in cls.records if r["id"] == "skill:099d20aa14905c87")
        cls.registry = load_trusted_applicability_registry()
        assert cls.registry.resolve(cls.core) is not None

    def item(self, record):
        return safe_catalog([record], ())["capabilities"][0]

    def test_real_description_and_registry_match(self):
        item = self.item(self.core)
        self.assertEqual(item["description"], self.core["description"])
        self.assertEqual(item["description_status"], "available")
        self.assertEqual(item["trust_status"], "verified_trusted")
        self.assertIn("Official GSAP skill", item["description"])

    def test_unregistered_and_forged_trust_are_not_trusted(self):
        record = copy.deepcopy(self.core)
        record.update(name="not-registered", trusted=True, trust_status="verified_trusted")
        record["_nexus_trusted_applicability"] = self.registry.resolve(self.core)
        self.assertEqual(self.item(record)["trust_status"], "unverified")

    def test_identity_mismatches_never_trusted(self):
        for key, value in (("name", "other"), ("metadata_fingerprint", "0" * 64),
                           ("content_sha256", "0" * 64), ("id", "skill:forged"),
                           ("skill_md_path", "different/SKILL.md"), ("kind", "agent"),
                           ("provenance", {"source_scope": "unregistered"})):
            with self.subTest(key=key):
                record = dict(self.core, **{key: value})
                self.assertEqual(self.item(record)["trust_status"], "unverified")

    def test_duplicate_ids_fail_closed_even_across_tag_filter(self):
        other = dict(self.core, tags=["other"])
        payload = safe_catalog([self.core, other], ("animation",))
        self.assertEqual(payload["capability_count"], 1)
        self.assertEqual(payload["capabilities"][0]["trust_status"], "unverified")
        duplicate = safe_catalog([self.core, self.core], ())
        self.assertEqual(len(duplicate["capabilities"]), 2)
        self.assertTrue(all(r["trust_status"] == "unverified" for r in duplicate["capabilities"]))

    def test_unavailable_and_duplicate_status_preserved(self):
        for status in ("unavailable", "inaccessible", "malformed", "duplicate_conflict", "shadowed"):
            with self.subTest(status=status):
                item = self.item(dict(self.core, status=status))
                self.assertEqual(item["availability"], status)
                self.assertEqual(item["trust_status"], "unverified")

    def test_registry_failure_is_unknown_not_trusted(self):
        with patch("ash.mcp.redaction.load_trusted_applicability_registry",
                   side_effect=SemanticRoutingError("registry integrity failed")):
            item = self.item(self.core)
        self.assertEqual(item["trust_status"], "unknown")
        self.assertEqual(item["description"], self.core["description"])

    def test_ambiguous_registry_identity_is_not_trusted(self):
        ambiguous = type(self.registry)(self.registry.rules * 2, self.registry.registry_sha256)
        with patch("ash.mcp.redaction.load_trusted_applicability_registry", return_value=ambiguous):
            self.assertEqual(self.item(self.core)["trust_status"], "unverified")

    def test_missing_descriptions_are_not_invented(self):
        for value in (None, "", "  ", {"description": "invented"}):
            item = self.item(dict(self.core, description=value))
            self.assertIsNone(item["description"])
            self.assertEqual(item["description_status"], "missing")

    def test_description_redaction(self):
        for text in (r"Read C:\private\SKILL.md", r"Read \\private\share", "Read /home/private/key",
                     "Read ~/private/key", "[private](/home/private/key)", "file:///private/key", "api_key=SECRET_SENTINEL",
                     "password: SECRET_SENTINEL", "https://owner:secret@example.test/", "unsafe\x00text"):
            with self.subTest(text=text):
                item = self.item(dict(self.core, description=text))
                self.assertIsNone(item["description"])
                self.assertEqual(item["description_status"], "redacted")

    def test_description_is_source_prefix_and_explicitly_truncated(self):
        source = "植物动画" * MAX_CATALOG_DESCRIPTION_CHARS
        item = self.item(dict(self.core, description=source))
        self.assertEqual(item["description"], source[:MAX_CATALOG_DESCRIPTION_CHARS])
        self.assertEqual(item["description_status"], "truncated")

    def test_legacy_fields_and_no_permission_or_raw_content(self):
        payload = safe_catalog([self.core], ())
        item = payload["capabilities"][0]
        expected = {"resource_id": self.core["id"], "display_name": self.core["name"],
                    "resource_kind": self.core["kind"], "capability_tags": sorted(set(self.core["tags"])),
                    "availability": self.core["status"], "source_scope": self.core["provenance"]["source_scope"],
                    "runtime_compatibility": self.core.get("runtime_compatibility", "directly_usable_by_codex")}
        self.assertEqual({key: item[key] for key in expected}, expected)
        self.assertEqual(payload["metadata_authority"], "none")
        self.assertEqual(payload["host_inventory_authority"], "none")
        self.assertEqual(payload["description_trust"], "untrusted_resource_metadata")
        encoded = json.dumps(payload)
        for forbidden in ("skill_md_path", self.core["skill_md_path"], "instructions", "execution_authority"):
            self.assertNotIn(forbidden, encoded)

    def test_response_size_filter_and_empty_result(self):
        records = [dict(self.core, id=f"skill:{i}", name=f"plant-{i}", description="植物" * 1000)
                   for i in range(500)]
        payload = safe_catalog(records, ("animation",))
        self.assertEqual(payload["available_capability_count"], 500)
        self.assertTrue(payload["truncated"])
        self.assertLessEqual(len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()), MAX_SAFE_ENVELOPE_BYTES)
        wire = {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]}
        self.assertLess(len(json.dumps(wire).encode()), MAX_RESPONSE_BYTES)
        empty = safe_catalog(records, ("does-not-match",))
        self.assertEqual(empty["capabilities"], [])
        self.assertFalse(empty["truncated"])


if __name__ == "__main__":
    unittest.main()
