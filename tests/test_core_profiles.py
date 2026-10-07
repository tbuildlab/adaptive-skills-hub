from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ash.core import CoreError, read_task, run_task
from ash.core_capabilities import ScopeError, safe_path
from ash.core_profiles import approval_summary, disposition, load_project, prepare_project
from unittest.mock import patch
from scripts.core_project_demo import ROOT, TASKS, fixture


class CoreProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def project(self, profile="python"):
        return fixture(self.root / "project", profile)

    def prepare(self, project, task=None):
        profile = json.loads((project / ".nexus.json").read_text("utf-8"))["profile"]
        return prepare_project(task or TASKS.get(profile, TASKS["python"]), project)

    def config(self, project, **updates):
        path = project / ".nexus.json"
        value = json.loads(path.read_text("utf-8"))
        value.update(updates)
        path.write_text(json.dumps(value), encoding="utf-8")

    def run_prepared(self, state, directory):
        return run_task(directory, approval=state["approval_sha256"])

    def test_normal_python_project_actual_tests_repair_and_independent_verify(self):
        project = self.project()
        state, directory = self.prepare(project)
        self.assertEqual(state["status"], "prepared", state["blocker"])
        self.assertIn("return amount - discount", (project / "shipping.py").read_text("utf-8"))
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "completed", result["blocker"])
        self.assertEqual(result["commands_used"], 4)
        self.assertEqual(result["steps"][0]["attempts"], 2)
        self.assertIn("repair", [e.get("phase") for e in result["events"]])
        self.assertEqual(result["steps"][0]["result"]["data"]["tests"], 3)
        self.assertIn("max(0", (project / "shipping.py").read_text("utf-8"))

    def test_static_web_content_edit_and_actual_local_checks(self):
        project = self.project("static-web")
        state, directory = self.prepare(project)
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "completed", result["blocker"])
        self.assertIn("Request a service quote", (project / "index.html").read_text("utf-8"))
        self.assertEqual(result["steps"][0]["result"]["data"]["checker"], "fixed-html.v1")

    def test_multifile_structured_handoff_resume_and_receipt(self):
        project = self.project("evidence")
        state, directory = self.prepare(project)
        paused = run_task(directory, approval=state["approval_sha256"], max_steps=1)
        self.assertEqual(paused["status"], "paused", paused["blocker"])
        self.assertEqual(disposition(paused), "SAFE TO RESUME")
        artifact = project / state["approval_context"]["output"] / "inventory.json"
        before = artifact.stat().st_mtime_ns
        result = self.run_prepared(read_task(directory), directory)
        self.assertEqual(result["status"], "completed", result["blocker"])
        self.assertEqual(before, artifact.stat().st_mtime_ns)
        self.assertEqual(result["commands_used"], 4)
        self.assertEqual(disposition(result), "TASK COMPLETE")
        self.assertFalse(result["receipt"]["production_host_qualified"])
        self.assertEqual(result["steps"][1]["result"]["data"]["sources"], ["README.md", "architecture.md", "notes.txt"])

    def test_bundle_reuse_does_not_require_manual_hash_catalog(self):
        project = self.project("static-web")
        first, one = self.prepare(project)
        second, two = self.prepare(project)
        self.assertNotEqual(one, two)
        self.assertNotEqual(first["approval_sha256"], second["approval_sha256"])
        a = Path(first["steps"][0]["command"][5]).read_bytes()
        b = Path(second["steps"][0]["command"][5]).read_bytes()
        self.assertEqual(a, b)
        self.assertEqual(first["approval_context"]["project_inputs"], second["approval_context"]["project_inputs"])

    def test_clear_approval_summary_has_scope_hooks_limits_verifier_and_digest(self):
        state, directory = self.prepare(self.project())
        text = approval_summary(state, directory)
        for required in ("[PLAN]", "[SELECT]", "Read scope:", "Exact reviewed edits:", "Artifact scope:",
                         "Budget", "Verifier:", "Repair:", state["approval_sha256"], "SAFE TO RESUME"):
            self.assertIn(required, text)

    def test_absent_approval_is_effect_free(self):
        project = self.project()
        state, directory = self.prepare(project)
        result = run_task(directory, approval=None)
        self.assertEqual(result["commands_used"], 0)
        self.assertFalse((project / "nexus-results").exists())
        self.assertIn("return amount - discount", (project / "shipping.py").read_text("utf-8"))

    def test_input_drift_blocks_before_dispatch(self):
        project = self.project()
        state, directory = self.prepare(project)
        (project / "shipping.py").write_text("changed outside approval\n", encoding="utf-8")
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 0)

    def test_config_drift_blocks_before_dispatch(self):
        project = self.project()
        state, directory = self.prepare(project)
        self.config(project, output="changed-output")
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 0)

    def test_settings_hash_drift_blocks_before_dispatch(self):
        state, directory = self.prepare(self.project())
        settings = next(directory.parent.glob("bundle/*/settings.json"))
        settings.write_text("{}", encoding="utf-8")
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 0)

    def test_added_python_dependency_refused(self):
        project = self.project()
        state, directory = self.prepare(project)
        (project / "other.py").write_text("x=1\n", encoding="utf-8")
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 0)

    def test_unsupported_task_has_no_fabricated_host_execution(self):
        state, directory = self.prepare(self.project("evidence"), "Create an editable PowerPoint presentation.")
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["commands_used"], 0)
        self.assertTrue((directory / "NEXT-OWNER-DECISION.md").is_file())
        self.assertEqual(disposition(state), "MANUAL REVIEW REQUIRED")

    def test_malformed_and_arbitrary_command_config_refused(self):
        project = self.project()
        for updates in ({"command": "echo forbidden"}, {"profile": "shell"}, {"files": ["../outside.txt"]},
                        {"files": [".env"]}, {"patches": [{"path": "undeclared.py", "old": "a", "new": "b"}]},
                        {"output": "../escape"}, {"output": "tests"}):
            with self.subTest(updates=updates):
                original = (project / ".nexus.json").read_bytes()
                self.config(project, **updates)
                with self.assertRaises((CoreError, ScopeError, OSError)):
                    self.prepare(project)
                (project / ".nexus.json").write_bytes(original)

    def test_duplicate_config_fields_refused(self):
        project = self.project()
        (project / ".nexus.json").write_text('{"profile":"python","profile":"evidence"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            load_project(project)

    def test_default_readonly_adapter_without_config(self):
        project = self.root / "default"
        project.mkdir()
        (project / "README.md").write_text("# Project\n", encoding="utf-8")
        state, directory = prepare_project("Research evidence in local project files.", project)
        self.assertEqual(state["approval_context"]["profile"], "evidence")
        self.assertEqual(self.run_prepared(state, directory)["status"], "completed")

    def test_existing_output_preserved(self):
        project = self.project()
        (project / "nexus-results").mkdir()
        path = project / "nexus-results/keep.txt"
        path.write_text("keep", encoding="utf-8")
        state, directory = self.prepare(project)
        self.assertEqual(self.run_prepared(state, directory)["status"], "completed")
        self.assertEqual(path.read_text("utf-8"), "keep")

    def test_repeat_tasks_reuse_config_and_do_not_overwrite_prior_artifacts(self):
        project = self.project("static-web")
        one, first = self.prepare(project)
        self.assertEqual(self.run_prepared(one, first)["status"], "completed")
        artifact = project / one["approval_context"]["output"] / "checks.json"
        before = artifact.read_bytes(), artifact.stat().st_mtime_ns
        two, second = self.prepare(project)
        self.assertEqual(self.run_prepared(two, second)["status"], "completed")
        self.assertNotEqual(one["approval_context"]["output"], two["approval_context"]["output"])
        self.assertEqual(before, (artifact.read_bytes(), artifact.stat().st_mtime_ns))

    def test_nonsecret_scope_paths_and_windows_aliases(self):
        for name in ("/absolute", "C:/outside", "a/../b", "a\\b", "private_key.txt", "cookies.txt", "AUX", "NUL.txt", "COM1.txt", ".env", "a."):
            with self.subTest(name=name), self.assertRaises(ScopeError):
                safe_path(self.root, name)

    def test_case_alias_and_hardlinked_inputs_refused(self):
        project = self.project()
        self.config(project, files=["shipping.py", "SHIPPING.py"])
        with self.assertRaises(ScopeError):
            self.prepare(project)
        self.config(project, files=["shipping.py", "tests/test_shipping.py"])
        os.link(project / "shipping.py", project / "alias.py")
        with self.assertRaises(ScopeError):
            self.prepare(project)

    def test_expired_checkpoint_is_not_reported_safe(self):
        state, directory = self.prepare(self.project())
        with patch("ash.core_profiles.time.time", return_value=10**12):
            self.assertEqual(disposition(state), "MANUAL REVIEW REQUIRED")

    def test_config_nonobject_and_profile_conflict_refused(self):
        project = self.project()
        with self.assertRaises(CoreError):
            prepare_project(TASKS["python"], project, profile="evidence")
        (project / ".nexus.json").write_text("[]", encoding="utf-8")
        with self.assertRaises(CoreError):
            prepare_project(TASKS["python"], project)

    def test_old_cli_cancel_status_and_no_effect_resume(self):
        project = self.project("static-web")
        state, directory = self.prepare(project)
        for verb in ("core-cancel", "core-status"):
            call = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/nexus.py"), verb, str(directory)],
                                  capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(call.returncode, 0, call.stderr)
            view = json.loads(call.stdout)
            self.assertTrue(view["cancel_requested"])
            self.assertEqual(view["operator_action"], "MANUAL REVIEW REQUIRED")
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["commands_used"], 0)
        self.assertFalse((project / "nexus-results").exists())

    def test_zero_test_all_skipped_and_load_error_never_trigger_patch(self):
        for test_source in ("# no tests\n", "raise ImportError('fixture unavailable dependency')\n",
                            "import unittest\n@unittest.skip('fixture skip')\nclass TestSkip(unittest.TestCase):\n    def test_skip(self): pass\n"):
            with self.subTest(source=test_source):
                project = fixture(self.root / str(len(list(self.root.iterdir()))), "python")
                (project / "tests/test_shipping.py").write_text(test_source, encoding="utf-8")
                before = (project / "shipping.py").read_bytes()
                state, directory = self.prepare(project)
                result = self.run_prepared(state, directory)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["commands_used"], 1)
                self.assertEqual(before, (project / "shipping.py").read_bytes())
                self.assertFalse(any(e.get("phase") == "repair" for e in result["events"]))

    def test_artifact_tampering_requires_manual_review(self):
        project = self.project("evidence")
        state, directory = self.prepare(project)
        run_task(directory, approval=state["approval_sha256"], max_steps=1)
        (project / state["approval_context"]["output"] / "inventory.json").write_text("[]", encoding="utf-8")
        result = self.run_prepared(state, directory)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 2)

    def test_progress_reports_real_repair_and_no_raw_errors(self):
        state, directory = self.prepare(self.project())
        events = []
        result = run_task(directory, approval=state["approval_sha256"], progress=events.append)
        self.assertEqual(result["status"], "completed")
        self.assertIn("repair", [e["phase"] for e in events])
        self.assertTrue(all(set(e) == {"kind", "step", "phase", "status", "commands_used", "capability", "attempt"} for e in events))

    def test_cli_one_command_prepare_then_progress_and_status(self):
        project = self.project("static-web")
        call = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/nexus.py"), "core", TASKS["static-web"],
                               "--project", str(project), "--json"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(call.returncode, 0, call.stderr)
        view = json.loads(call.stdout)
        self.assertFalse((project / "nexus-results").exists())
        call = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/nexus.py"), "core-run", view["task_directory"],
                               "--approve", view["approval_sha256"], "--progress"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(call.returncode, 0, call.stderr)
        self.assertEqual(json.loads(call.stdout)["operator_action"], "TASK COMPLETE")
        self.assertIn("[VERIFY]", call.stderr)
        self.assertIn("[DONE]", call.stderr)


if __name__ == "__main__":
    unittest.main()
