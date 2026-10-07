from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from ash.core import CoreBudget, CoreError, _save, prepare_task, read_task, request_cancel, run_task
from ash.core_host import LocalHookError, exclusive_run
from scripts.core_local_demo import ROOT, TASKS, create_fixture


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def fixture(self, scenario="A"):
        return create_fixture(self.root / "demo", scenario)

    def rewrite(self, catalog, *, source=None, metadata=None, authority=None, retry_safe=None):
        data = json.loads(catalog.read_text(encoding="utf-8"))
        entry = data["skills"][0]
        folder = (catalog.parent / entry["skill"]).parent
        if source is not None:
            (folder / "hook.py").write_text(source, encoding="utf-8")
        if metadata is not None:
            (folder / "SKILL.md").write_text(metadata, encoding="utf-8")
        if authority is not None:
            entry["authority"] = authority
        if retry_safe is not None:
            entry["retry_safe"] = retry_safe
        entry["bindings"] = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in entry["bindings"]}
        catalog.write_text(json.dumps(data), encoding="utf-8")

    def prepare(self, project, catalog, **kwargs):
        return prepare_task(TASKS[kwargs.pop("scenario", "A")], project, catalog, self.root / "task", **kwargs)

    def run_state(self, state, **kwargs):
        return run_task(self.root / "task", approval=state["approval_sha256"], **kwargs)

    def test_planning_selection_loading_and_real_execution(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        self.assertEqual(state["plan_validation"]["status"], "passed")
        self.assertEqual([s["name"] for s in state["steps"]], ["local-research"])
        self.assertTrue(state["loaded_skills"][0]["sha256"])
        self.assertFalse((project / "analysis.json").exists())
        result = self.run_state(state)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["commands_used"], 2)
        self.assertEqual(json.loads((project / "analysis.json").read_text())["lines"], 2)
        self.assertFalse(result["receipt"]["production_host_qualified"])

    def test_real_repair_and_regression_chain(self):
        project, catalog = self.fixture("B")
        state = self.prepare(project, catalog, scenario="B")
        result = self.run_state(state)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["steps"][0]["attempts"], 2)
        self.assertEqual(result["commands_used"], 6)
        self.assertIn("return a + b", (project / "calc.py").read_text())
        self.assertTrue(json.loads((project / "test-results.json").read_text())["passed"])
        self.assertIn("repair", [e.get("phase") for e in result["events"]])

    def test_multiskill_outputs_and_persisted_resume_skip_completed_step(self):
        project, catalog = self.fixture("C")
        state = self.prepare(project, catalog, scenario="C")
        paused = self.run_state(state, max_steps=1)
        self.assertEqual(paused["status"], "paused")
        first = (project / "analysis.json").stat().st_mtime_ns
        resumed = self.run_state(read_task(self.root / "task"))
        self.assertEqual(resumed["status"], "completed")
        self.assertEqual(resumed["commands_used"], 4)
        self.assertEqual(first, (project / "analysis.json").stat().st_mtime_ns)
        self.assertEqual(resumed["steps"][1]["result"]["data"]["upstream_source"], resumed["steps"][0]["result"]["data"]["source_sha256"])

    def test_missing_approval_does_not_execute_and_can_be_supplied_later(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        result = run_task(self.root / "task", approval=None)
        self.assertEqual(result["commands_used"], 0)
        self.assertFalse((project / "analysis.json").exists())
        self.assertTrue((self.root / "task/NEXT-OWNER-DECISION.md").exists())
        self.assertEqual(self.run_state(state)["status"], "completed")

    def test_unsupported_authority_stops_before_effect(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, authority="credential")
        state = self.prepare(project, catalog)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(self.run_state(state)["commands_used"], 0)
        self.assertFalse((project / "analysis.json").exists())
        text = (self.root / "task/NEXT-OWNER-DECISION.md").read_text(encoding="utf-8")
        self.assertIn("Do not replay", text)
        self.assertNotIn("--approve", text)

    def test_tool_boundary_is_terminal(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, source="print('{\"status\":\"boundary\"}')\n")
        state = self.prepare(project, catalog)
        result = self.run_state(state)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 1)

    def test_verifier_and_repair_boundaries_stop_before_any_retry(self):
        for scenario, phase in (("A", "verify"), ("B", "repair")):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                project, catalog = create_fixture(root / "demo", scenario)
                folder = catalog.parent / ("local-research" if scenario == "A" else "local-backend")
                source = (folder / "hook.py").read_text(encoding="utf-8")
                if scenario == "A":
                    source = source.replace('emit("ok", verified=', 'emit("boundary", verified=')
                else:
                    source = source.replace('emit("ok", data={"repair"', 'emit("boundary", data={"repair"')
                self.rewrite(catalog, source=source, retry_safe=True)
                state = prepare_task(TASKS[scenario], project, catalog, root / "task")
                result = run_task(root / "task", approval=state["approval_sha256"])
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["commands_used"], 2)
                self.assertTrue((root / "task/NEXT-OWNER-DECISION.md").exists())
                self.assertFalse(any(e["kind"] == "retry" for e in result["events"]))

    def test_command_failure_and_malformed_output_never_complete(self):
        for source in ("raise RuntimeError('synthetic failure')\n", "print('not json')\n",
                       "print('{\"status\":\"ok\",\"data\":{\"n\":NaN}}')\n",
                       "print('{\"status\":\"ok\",\"status\":\"error\"}')\n",
                       "print('{\"status\":[]}')\n",
                       "print('{\"status\":\"error\",\"failure_kind\":[]}')\n",
                       "print('{\"status\":\"ok\",\"verified\":\"true\"}')\n"):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                project, catalog = create_fixture(root / "demo", "A")
                self.rewrite(catalog, source=source)
                state = prepare_task(TASKS["A"], project, catalog, root / "task")
                result = run_task(root / "task", approval=state["approval_sha256"])
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["commands_used"], 1)
                self.assertFalse(any("not json" in str(e) for e in result["events"]))

    def test_missing_executable_hook_and_dependency_create_owner_blocker(self):
        for replacement in ('hub_validate: []', 'hub_after: ["missing"]'):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                project, catalog = create_fixture(root / "demo", "A")
                source = (catalog.parent / "local-research/SKILL.md").read_text(encoding="utf-8")
                source = "\n".join(replacement if line.startswith(replacement.split(":")[0] + ":") else line for line in source.splitlines()) + "\n"
                self.rewrite(catalog, metadata=source)
                result = prepare_task(TASKS["A"], project, catalog, root / "task")
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["commands_used"], 0)
                self.assertTrue((root / "task/NEXT-OWNER-DECISION.md").exists())

    def test_cancel_before_dispatch_consumes_no_command(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        request_cancel(self.root / "task")
        result = self.run_state(state)
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["commands_used"], 0)

    def test_output_overflow_refuses_completion(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, source="print('x' * 70000)\n")
        result = self.run_state(self.prepare(project, catalog))
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["commands_used"], 1)

    def test_expiry_does_not_reset_when_resuming_checkpoint(self):
        project, catalog = self.fixture("C")
        state = self.prepare(project, catalog, scenario="C", budget=CoreBudget(total_seconds=2, step_seconds=1))
        paused = self.run_state(state, max_steps=1)
        self.assertEqual(paused["status"], "paused")
        time.sleep(2)
        resumed = self.run_state(paused)
        self.assertEqual(resumed["status"], "budget_exhausted")
        self.assertEqual(resumed["commands_used"], 2)
        self.assertFalse((project / "review.md").exists())

    def test_success_without_actual_artifact_is_failure(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, source="print('{\"status\":\"ok\",\"data\":{},\"artifacts\":[\"missing.txt\"]}')\n")
        self.assertEqual(self.run_state(self.prepare(project, catalog))["status"], "failed")

    def test_independent_verifier_can_reject_success(self):
        project, catalog = self.fixture()
        folder = catalog.parent / "local-research"
        source = (folder / "hook.py").read_text(encoding="utf-8")
        source = source.replace('verified=json.loads((project / "analysis.json").read_text(encoding="utf-8")) == data', 'verified=False')
        self.rewrite(catalog, source=source)
        state = self.run_state(self.prepare(project, catalog))
        self.assertEqual(state["status"], "failed")
        self.assertEqual(state["completed_steps"], [])

    def test_retry_exhaustion_is_bounded(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, retry_safe=True, source="print('{\"status\":\"error\",\"failure_kind\":\"temporary_tool_failure\",\"retryable\":true}')\n")
        result = self.run_state(self.prepare(project, catalog))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["commands_used"], 2)
        self.assertEqual(result["steps"][0]["attempts"], 2)

    def test_single_replan_routes_to_real_alternative(self):
        project, catalog = self.fixture()
        data = json.loads(catalog.read_text(encoding="utf-8"))
        old = catalog.parent / "local-research"
        alternate = catalog.parent / "z-alternative"
        alternate.mkdir()
        for name in ("SKILL.md", "hook.py"):
            raw = (old / name).read_bytes()
            if name == "SKILL.md":
                raw = raw.replace(b"name: local-research", b"name: z-alternative")
            (alternate / name).write_bytes(raw)
        entry = dict(data["skills"][0], skill="z-alternative/SKILL.md")
        entry["bindings"] = {name: hashlib.sha256((alternate / name).read_bytes()).hexdigest() for name in ("SKILL.md", "hook.py")}
        data["skills"].append(entry)
        catalog.write_text(json.dumps(data), encoding="utf-8")
        self.rewrite(catalog, source="print('{\"status\":\"error\",\"failure_kind\":\"wrong_resource\",\"no_effect\":true}')\n")
        state = self.prepare(project, catalog)
        self.assertEqual(state["steps"][0]["name"], "local-research")
        result = self.run_state(state)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["replans"], 1)
        self.assertEqual(result["steps"][0]["name"], "z-alternative")

    def test_budget_refuses_second_effect_without_refunding_charge(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog, budget=CoreBudget(max_commands=1))
        result = self.run_state(state)
        self.assertEqual(result["status"], "budget_exhausted")
        self.assertEqual(result["commands_used"], 1)
        self.assertTrue((project / "analysis.json").exists())
        self.assertEqual(result["completed_steps"], [])

    def test_pre_dispatch_expiry_never_runs_hook(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog, budget=CoreBudget(total_seconds=0.03, step_seconds=0.01))
        time.sleep(0.04)
        result = self.run_state(state)
        self.assertEqual(result["status"], "budget_exhausted")
        self.assertEqual(result["commands_used"], 0)

    def test_cancel_before_and_during_execution(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, source="import time\ntime.sleep(2)\nprint('{\"status\":\"ok\"}')\n")
        state = self.prepare(project, catalog)
        cancel = threading.Timer(0.15, request_cancel, args=[self.root / "task"])
        cancel.start()
        result = self.run_state(state)
        cancel.join()
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["commands_used"], 1)
        self.assertIn("partial", result["blocker"])
        self.assertEqual(self.run_state(result)["commands_used"], 1)

    def test_timeout_is_ambiguous_not_a_retry(self):
        project, catalog = self.fixture()
        self.rewrite(catalog, retry_safe=True, source="import time\ntime.sleep(2)\n")
        state = self.prepare(project, catalog, budget=CoreBudget(step_seconds=0.15))
        result = self.run_state(state)
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["commands_used"], 1)

    def test_fault_after_intent_has_no_automatic_reexecution(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        with patch("ash.core.invoke", side_effect=KeyboardInterrupt):
            result = self.run_state(state)
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(self.run_state(result)["commands_used"], 1)
        self.assertFalse((project / "analysis.json").exists())

    def test_running_checkpoint_without_inflight_still_needs_reconciliation(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        state["status"] = "running"
        state["commands_used"] = 1
        _save(self.root / "task", state)
        result = self.run_state(state)
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["commands_used"], 1)

    def test_changed_checkpoint_artifact_refuses_resume(self):
        project, catalog = self.fixture("C")
        state = self.prepare(project, catalog, scenario="C")
        state = self.run_state(state, max_steps=1)
        (project / "analysis.json").write_text("changed", encoding="utf-8")
        result = self.run_state(state)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse((project / "review.md").exists())

    def test_changed_catalog_bytes_refuse_dispatch(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        (catalog.parent / "local-research/hook.py").write_text("print('changed')", encoding="utf-8")
        result = self.run_state(state)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["commands_used"], 0)

    def test_corrupt_state_never_runs(self):
        project, catalog = self.fixture()
        self.prepare(project, catalog)
        path = self.root / "task/task.json"
        content = json.loads(path.read_text(encoding="utf-8"))
        content["payload"]["commands_used"] = 0.5
        path.write_text(json.dumps(content), encoding="utf-8")
        with self.assertRaises(CoreError):
            run_task(self.root / "task", approval="anything")

    def test_concurrent_runner_cannot_acquire_task(self):
        project, catalog = self.fixture()
        state = self.prepare(project, catalog)
        with exclusive_run(self.root / "task"):
            with self.assertRaises(LocalHookError):
                self.run_state(state)

    def test_invalid_numeric_budgets(self):
        for budget in (CoreBudget(max_attempts=4), CoreBudget(total_seconds=float("nan")), CoreBudget(max_commands=True)):
            with self.assertRaises(CoreError):
                budget.validate()

    def test_cli_existing_entry_supports_prepare_run_status(self):
        project, catalog = self.fixture()
        command = [sys.executable, "-B", str(ROOT / "scripts/nexus.py")]
        prepared = subprocess.run(command + ["core-plan", TASKS["A"], "--project", str(project), "--catalog", str(catalog), "--task-dir", str(self.root / "task")], capture_output=True, encoding="utf-8", timeout=20)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        approval = json.loads(prepared.stdout)["approval_sha256"]
        denied = subprocess.run(command + ["core-run", str(self.root / "task")], capture_output=True, encoding="utf-8", timeout=20)
        self.assertEqual(denied.returncode, 1, denied.stderr)
        self.assertEqual(json.loads(denied.stdout)["commands_used"], 0)
        result = subprocess.run(command + ["core-run", str(self.root / "task"), "--approve", approval], capture_output=True, encoding="utf-8", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "completed")
        status = subprocess.run(command + ["core-status", str(self.root / "task")], capture_output=True, encoding="utf-8", timeout=20)
        self.assertEqual(json.loads(status.stdout)["commands_used"], 2)
        self.assertEqual(json.loads(status.stdout)["steps"][0]["attempts"], 1)


if __name__ == "__main__":
    unittest.main()
