"""Independent negative oracles for local readback; fixtures are not live evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ash import g4_contracts as c, g4_host_adapter as adapter
from scripts.verify_g4_local_evidence import verify
from tests.g4_fixtures import bundle, domain_body, NOW


class LocalG4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return c.digest(value)

    def fixture(self, pack="website"):
        args = bundle(pack)
        self.write("scope.json", {"scope": "TEST_FIXTURE_LOCAL_ONLY"})
        scope_ref = hashlib.sha256((self.root / "scope.json").read_bytes()).hexdigest()
        memory = {"schema": "nexus.g4.local-task-memory-entry.v1", "project_id": "fixture-project",
                  "task_id": "fixture-task", "rule": "Fixture assertion only", "source_ref": scope_ref,
                  "retention": "TASK", "state": "CONFIRMED_TASK_CONSTRAINT_ONLY", "dispatch_authority": "none"}
        self.write("memory.json", memory)
        (self.root / "artifact.md").write_text("Fixture artifact; no production authority.\n", encoding="utf-8")
        names = sorted(c.PACK_EVIDENCE[pack] | {"shared-control"})
        self.write("checks.json", {"schema": "nexus.g4.host-measurements.v1", "pack": pack,
                                  "checks": {name: {"status": "PASS", "measurements": {"fixture": True}}
                                             for name in names}})
        files = {name: {"bytes": (self.root / name).stat().st_size,
                        "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}
                 for name in ["scope.json", "memory.json", "artifact.md", "checks.json"]}
        inputs = ["memory.json", "scope.json"]
        input_digest = c.digest({name: files[name] for name in inputs})
        artifact_digest = c.digest({"artifact.md": files["artifact.md"]})
        binding = {**args["expected_binding"], "input_sha256": input_digest}
        records = {key: domain_body(kind, pack) for key, kind in
                   [("pack", "workflow-pack"), ("context", "context-manifest"), ("impact", "change-impact")]}
        records["decisions"] = [domain_body("project-decision", content_sha256=files["memory.json"]["sha256"],
                                source_refs=[scope_ref], approving_authority_ref=scope_ref)]
        records["relations"] = []
        sources = [files[name]["sha256"] for name in ["scope.json", "memory.json", "checks.json"]]
        records["context"]["sources"] = [{"ref": ref, "sha256": ref, "project_id": "fixture-project",
                                           "task_id": "fixture-task", "transformation": "ORIGINAL",
                                           "original_ref": None, "valid_until": NOW + 100} for ref in sources]
        for value in records.values():
            for body in value if isinstance(value, list) else [value]:
                body["binding"] = binding
        oracle = {key: value for key, value in args.items()
                  if key not in {"pack", "context", "impact", "decisions", "relations"}}
        oracle.update(expected_binding=binding, source_refs=sources, source_digests={ref: ref for ref in sources},
                      confirmation_refs=[scope_ref], endpoint_versions={}, observations={
                          name: {"status": "PASS", "input_sha256": input_digest,
                                 "artifact_sha256": artifact_digest,
                                 "source_refs": [files["checks.json"]["sha256"]]} for name in names})
        packet = {"schema": "nexus.g4.local-workflow-evidence.v1", "records": records, "oracle": oracle,
                  "files": files, "checks": {name: "checks.json" for name in names},
                  "input_paths": inputs, "artifact_paths": ["artifact.md"], "memory_path": "memory.json",
                  "scope": {"included": ["fixture-local-checks"], "excluded_unexamined": [
                      {"area": "production", "reason": "Fixture never qualifies production."}]}}
        self.write("packet.json", packet)
        return packet

    def reject(self, packet):
        self.write("packet.json", packet)
        with self.assertRaises((ValueError, OSError, TypeError, KeyError)):
            verify(self.root, "packet.json")

    def reseal_file(self, packet, name):
        """Simulate mutable caller metadata; checks must still reject false claims."""
        old = packet["files"][name]["sha256"]
        data = (self.root / name).read_bytes()
        new = hashlib.sha256(data).hexdigest()
        packet["files"][name] = {"bytes": len(data), "sha256": new}
        def swap(value):
            if isinstance(value, dict): return {swap(k): swap(v) for k, v in value.items()}
            if isinstance(value, list): return [swap(v) for v in value]
            return new if value == old else value
        packet = swap(packet)
        digest = c.digest({key: packet["files"][key] for key in sorted(packet["input_paths"])})
        packet["oracle"]["expected_binding"]["input_sha256"] = digest
        for value in packet["records"].values():
            for body in value if isinstance(value, list) else [value]: body["binding"]["input_sha256"] = digest
        for observation in packet["oracle"]["observations"].values(): observation["input_sha256"] = digest
        return packet

    def test_both_pack_readbacks_never_create_authority(self):
        for pack in c.PACK_EVIDENCE:
            self.fixture(pack)
            verdict = verify(self.root, "packet.json")
            self.assertEqual(verdict["status"], "LOCAL_ARTIFACT_AND_EVIDENCE_VERIFIED")
            self.assertEqual(verdict["contract_verdict"]["status"], "PASS_STRUCTURAL_ONLY")
            self.assertEqual(verdict["dispatch_authority"], "none")
            self.assertEqual(verdict["real_admission"], "NO")

    def test_source_and_artifact_corruption_or_removal_denies(self):
        for name in ("scope.json", "artifact.md", "checks.json", "memory.json"):
            packet = self.fixture(); (self.root / name).write_text("corrupted", encoding="utf-8")
            self.reject(packet)
        packet = self.fixture(); (self.root / "checks.json").unlink(); self.reject(packet)

    def test_resealed_cross_project_memory_and_authority_poisoning_denies(self):
        for field, value in [("project_id", "other-project"), ("task_id", "other-task"),
                             ("dispatch_authority", "production"), ("state", "PROPOSED")]:
            packet = self.fixture()
            memory = json.loads((self.root / "memory.json").read_text())
            memory[field] = value; self.write("memory.json", memory)
            self.reject(self.reseal_file(packet, "memory.json"))

    def test_wrong_confirmation_or_content_binding_denies(self):
        packet = self.fixture(); packet["oracle"]["confirmation_refs"] = []; self.reject(packet)
        packet = self.fixture(); packet["records"]["decisions"][0]["content_sha256"] = "0" * 64; self.reject(packet)

    def test_stale_or_cross_project_context_denies(self):
        packet = self.fixture(); packet["records"]["context"]["sources"][0]["project_id"] = "other"; self.reject(packet)
        packet = self.fixture(); packet["oracle"]["now"] = NOW + 100; self.reject(packet)

    def test_missing_shared_consumer_or_in_scope_unknown_denies(self):
        packet = self.fixture(); packet["records"]["impact"]["consumers"] = ["page"]; self.reject(packet)
        packet = self.fixture(); packet["records"]["impact"]["unexamined"] = ["shared-control"]; self.reject(packet)

    def test_excluded_area_cannot_hide_included_area(self):
        packet = self.fixture()
        packet["scope"]["excluded_unexamined"][0]["area"] = "fixture-local-checks"
        self.reject(packet)

    def test_reduction_preserves_mandatory_obligations(self):
        packet = self.fixture(); packet["records"]["context"]["preserved_obligations"] = []; self.reject(packet)

    def test_omitted_original_check_cannot_hide_optional_failure(self):
        packet = self.fixture(); del packet["checks"]["shared-control"]; self.reject(packet)
        packet = self.fixture()
        detail = json.loads((self.root / "checks.json").read_text())
        detail["checks"]["optional-failed-check"] = {"status": "FAIL", "measurements": {"fixture": True}}
        self.write("checks.json", detail)
        self.reject(self.reseal_file(packet, "checks.json"))

    def test_resealed_unknown_and_empty_original_measurements_denies(self):
        for change in ({"status": "UNKNOWN", "measurements": {"fixture": True}},
                       {"status": "PASS", "measurements": {}}):
            packet = self.fixture(); detail = json.loads((self.root / "checks.json").read_text())
            detail["checks"]["boundary"] = change; self.write("checks.json", detail)
            self.reject(self.reseal_file(packet, "checks.json"))

    def test_input_and_mixed_artifact_substitution_denies(self):
        packet = self.fixture(); packet["oracle"]["expected_binding"]["input_sha256"] = "0" * 64; self.reject(packet)
        packet = self.fixture(); packet["oracle"]["observations"]["boundary"]["artifact_sha256"] = "0" * 64; self.reject(packet)

    def test_paths_unknown_fields_and_unrepresented_files_denies(self):
        packet = self.fixture(); packet["files"]["../outside"] = packet["files"]["scope.json"]; self.reject(packet)
        packet = self.fixture(); packet["approval"] = "PASS"; self.reject(packet)
        packet = self.fixture(); packet["files"]["packet.json"] = packet["files"]["scope.json"]; self.reject(packet)

    def test_production_gate_stays_deny_for_local_evidence(self):
        packet = self.fixture()
        request = {"schema_version": adapter.REQUEST_SCHEMA, "binding": packet["oracle"]["expected_binding"],
                   "operations": ["read"], "expires_at": NOW + 100, "requires_recovery": False}
        self.assertEqual(adapter.pre_execution_gate(request, now=NOW)["status"], "DENY")

    def test_cli_closed_failure_and_no_source_mutation(self):
        self.fixture(); before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        script = Path(__file__).resolve().parents[1] / "scripts/verify_g4_local_evidence.py"
        result = subprocess.run([sys.executable, str(script), str(self.root), "packet.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        result = subprocess.run([sys.executable, str(script), str(self.root), "missing.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "DENY_OR_HOLD")


if __name__ == "__main__":
    unittest.main()
