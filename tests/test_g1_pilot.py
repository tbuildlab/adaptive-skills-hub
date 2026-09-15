from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import probe_g1_conformance as pilot


class G1PilotTests(unittest.TestCase):
    def test_existing_route_binding_real_probe_is_truthfully_narrow(self):
        report = pilot.run_probe()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["legacy_route_result"], "CAPABILITY_NOT_COVERED")
        self.assertEqual(report["decision"]["status"], "SELECTED")
        self.assertIsNone(report["candidate"]["model"])
        self.assertIsNone(report["decision"]["considered"][0]["cost"]["total_microunits"])
        self.assertEqual(report["unsupported_whole_host_result"], "UNSUPPORTED")
        self.assertEqual(set(report["observed_effects"].values()), {0})
        self.assertEqual(set(report["decision"]["authority"].values()), {"none"})
        self.assertEqual({r["control_id"] for r in report["conformance_records"]}, set(pilot.CONTROLS))
        self.assertTrue(all(r["operations"] == [pilot.OPERATION] for r in report["conformance_records"]))

    def test_changed_manifest_bound_source_is_not_qualified(self):
        original = pilot.RuntimeCapabilityAdapter._stable_bytes
        def altered(path):
            raw = original(path)
            return raw + b"\n# changed\n" if path.name == "g1_profiles.py" else raw
        with patch.object(pilot.RuntimeCapabilityAdapter, "_stable_bytes", side_effect=altered):
            with self.assertRaisesRegex(RuntimeError, "SOURCE_INTEGRITY_FAILED"):
                pilot.run_probe()

    def test_changed_binding_during_probe_fails(self):
        material = pilot._material()
        with patch.object(pilot, "_material", side_effect=[material, {**material, "local_roots": "changed"}]):
            report = pilot.run_probe()
        self.assertEqual(report["status"], "FAILED")
        self.assertFalse(report["checks"]["binding-unchanged"])

    def test_audit_observes_effect_without_preventing_it_to_manufacture_pass(self):
        original = pilot.NexusMcpRuntime.route_capabilities
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "owned-probe-test.txt"
            def with_owned_test_write(instance, args):
                target.write_text("test-owned effect", encoding="utf-8")
                return original(instance, args)
            with patch.object(pilot.NexusMcpRuntime, "route_capabilities", new=with_owned_test_write):
                report = pilot.run_probe()
            self.assertTrue(target.exists())
        self.assertEqual(report["status"], "FAILED")
        self.assertGreater(report["observed_effects"]["write"], 0)


if __name__ == "__main__":
    unittest.main()
