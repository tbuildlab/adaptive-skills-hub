"""Reusable fixed project profiles and operator views over the existing Core planner."""
from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

from .core import CoreBudget, CoreError, _epoch, prepare_task
from . import core_capabilities as hooks

PROFILE_VERSION = "nexus.core.bundles.v1"


def load_project(project: Path, profile: str | None = None) -> tuple[dict, str | None]:
    project = project.resolve(strict=True)
    filename = project / ".nexus.json"
    if filename.is_symlink() or (filename.exists() and getattr(filename.lstat(), "st_file_attributes", 0) & 0x400):
        raise CoreError("linked project configuration refused")
    if filename.exists():
        value = hooks.load_json(filename)
        if not isinstance(value, dict):
            raise CoreError("project configuration must be an object")
        if profile is not None and value.get("profile") != profile:
            raise CoreError("CLI profile contradicts project configuration")
        return hooks.config(project, value), hooks.sha(filename.read_bytes())
    if profile not in (None, "evidence"):
        raise CoreError("editing/testing profiles require a bounded .nexus.json; no commands inferred")
    # Useful zero-config non-secret analysis, with explicit inputs in approval view.
    names = [name for name in ("README.md", "pyproject.toml", "package.json", "index.html") if (project / name).is_file()]
    if not names:
        raise CoreError("no supported default input; declare non-secret files in .nexus.json")
    return hooks.config(project, {"schema": "nexus.core.project.v1", "profile": "evidence", "files": names}), None


def verify_scope(project, scope):
    try:
        if scope["config_sha256"] is not None:
            path = project / ".nexus.json"
            if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400 or hooks.sha(path.read_bytes()) != scope["config_sha256"]:
                raise CoreError("approved project configuration changed")
        elif (project / ".nexus.json").exists():
            raise CoreError("project configuration added after preparation")
        hooks.check_inputs(project, scope)
    except (hooks.ScopeError, OSError, ValueError, KeyError) as exc:
        raise CoreError("approved project scope drift; no dispatch") from exc


def prepare_project(task: str, project: Path, *, directory: Path | None = None,
                    profile: str | None = None, budget: CoreBudget | None = None) -> tuple[dict, Path]:
    for path in (project.absolute(), *project.absolute().parents):
        if path.is_symlink() or (path.exists() and getattr(path.lstat(), "st_file_attributes", 0) & 0x400):
            raise CoreError("linked project root refused")
    project = project.resolve(strict=True)
    budget = budget or CoreBudget(total_seconds=600, step_seconds=30)
    budget.validate()
    settings, config_digest = load_project(project, profile)
    inputs = hooks.snapshot(project, settings)
    task_key = uuid4().hex
    output_root = hooks.safe_path(project, settings["output"])
    if output_root.exists() and not output_root.is_dir():
        raise CoreError("artifact output root must be a directory")
    settings["output"] += "/" + task_key
    settings.update({"schema": "nexus.core.project-scope.v1", "bundle_version": PROFILE_VERSION,
                     "project_inputs": inputs, "config_sha256": config_digest,
                     "python_files": hooks.python_files(project) if settings["profile"] == "python" else []})
    # Never overwrite old output/user files as a side effect of a convenience command.
    output = hooks.safe_path(project, settings["output"])
    if output.exists():
        raise CoreError("output already exists; preserve it and choose a fresh output name")
    base = (directory or project / ".nexus" / "tasks" / task_key).absolute()
    if base.exists():
        raise CoreError("task directory must be new")
    for parent in (base, *base.parents):
        if parent.is_symlink() or (parent.exists() and getattr(parent.lstat(), "st_file_attributes", 0) & 0x400):
            raise CoreError("linked task-state directory refused")
    if base.resolve().is_relative_to(output.resolve()):
        raise CoreError("task state cannot be inside artifact output")
    catalog = base / "bundle"
    catalog.mkdir(parents=True)
    source = Path(hooks.__file__).read_bytes()
    if settings["profile"] == "evidence":
        specs = [("inspect", ["general_research", "software_research"], ["research", "analysis"], []),
                 ("report", ["architecture_review"], ["review", "architecture_design"], ["core-inspect"])]
    elif settings["profile"] == "python":
        specs = [("python", ["backend_repair", "software_testing"], ["software_debug", "software_test"], [])]
    else:
        specs = [("static-web", ["frontend_implementation", "software_testing"], ["implementation", "software_test"], [])]
    entries = []
    for capability, domains, kinds, after in specs:
        name = "core-" + capability
        folder = catalog / name
        folder.mkdir()
        instruction = (f"---\nname: {name}\ndescription: Reviewed fixed {capability} project capability\n"
                       f"hub_command: {json.dumps(['{python}', 'hook.py', capability, 'execute', str(folder / 'settings.json')])}\n"
                       f"hub_validate: {json.dumps(['{python}', 'hook.py', capability, 'verify', str(folder / 'settings.json')])}\n"
                       f"hub_after: {json.dumps(after)}\n")
        if capability == "python" and settings["patches"]:
            instruction += f"hub_repair: {json.dumps(['{python}', 'hook.py', capability, 'repair', str(folder / 'settings.json')])}\n"
        instruction += ("---\n\n# Reviewed local capability\n\n"
                        f"Bundle: {PROFILE_VERSION}. Scope: declared non-secret project inputs only.\n"
                        "Run fixed phases only; task prose cannot supply commands. Same-user trusted code, not a sandbox.\n")
        (folder / "SKILL.md").write_text(instruction, encoding="utf-8", newline="\n")
        (folder / "hook.py").write_bytes(source)
        (folder / "settings.json").write_text(json.dumps(settings, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        entries.append({"skill": f"{name}/SKILL.md", "authority": "owner_local", "retry_safe": capability == "python",
                        "bindings": {n: hooks.sha((folder / n).read_bytes()) for n in ("SKILL.md", "hook.py", "settings.json")},
                        "applicability": {"supported_domains": domains, "supported_task_kinds": kinds}})
    path = catalog / "catalog.json"
    path.write_text(json.dumps({"schema": "nexus.core.catalog.v1", "skills": entries}, indent=2) + "\n", encoding="utf-8", newline="\n")
    state_dir = base / "execution"
    state = prepare_task(task, project, path, state_dir, budget, approval_context=settings)
    # A report is a fixed dependency consumer; if planner selected only inspection it
    # remains inspection only. No hidden extra steps are appended to planner output.
    return state, state_dir


def disposition(state):
    if state["status"] == "completed":
        return "TASK COMPLETE"
    if (state["status"] in {"prepared", "paused"} and not state["inflight"]
            and _epoch(state["updated_at_utc"]) <= time.time() < _epoch(state["created_at_utc"]) + state["budget"]["total_seconds"]):
        return "SAFE TO RESUME"
    return "MANUAL REVIEW REQUIRED"


def approval_summary(state, directory):
    scope = state.get("approval_context", {})
    rows = ["[PLAN] " + state["task"], "Project: " + state["project"],
            "Profile: " + scope.get("profile", "custom reviewed catalog"),
            "Bundle version: " + scope.get("bundle_version", "custom"),
            "Scope: trusted same-user local code; no hostile-code sandbox.",
            "[SELECT] " + ", ".join(s["name"] for s in state["steps"])]
    for step in state["steps"]:
        rows.extend([f"Capability: {step['name']} ({step['authority']})", "Hook: " + json.dumps(step["command"]),
                     "Verifier: " + json.dumps(step["validate"]), "Repair: " + json.dumps(step["repair"]),
                     "Reviewed byte bindings: " + json.dumps(step["bindings"], sort_keys=True)])
    rows.extend(["Read scope: " + json.dumps(list(scope.get("project_inputs", {}))),
                 "Exact reviewed edits: " + json.dumps(scope.get("patches", []), ensure_ascii=False),
                 "Artifact scope: " + scope.get("output", "declared by custom hooks"),
                 "Expected effects: declared text patches and artifacts; Python profile also runs existing owner-reviewed tests.",
                 "Budget (from preparation, never reset on resume): " + json.dumps(state["budget"]),
                 "Input, settings, hook and runtime hashes are bound to this task's approval.",
                 "SAFE TO RESUME is conditional on dispatch-time integrity/budget checks; ambiguity never replays.",
                 "Approval SHA-256: " + state["approval_sha256"], "Task directory: " + str(directory),
                 "Status: " + disposition(state)])
    if state["blocker"]:
        rows.append("Blocker: " + state["blocker"])
    rows.append(f'Run after review: core-run "{directory}" --approve {state["approval_sha256"]} --progress')
    return "\n".join(rows)


def progress_line(event):
    labels = {"run_started": "PLAN", "dispatch_intent": "STEP", "step_completed": "VERIFY",
              "retry": "RETRY", "checkpoint_pause": "CHECKPOINT", "task_completed": "DONE", "stop": "STOP"}
    if event["kind"] == "dispatch_intent" and event["phase"] in {"verify", "repair"}:
        label = event["phase"].upper()
    else:
        label = labels.get(event["kind"])
    return (f"[{label}] capability={event['capability'] or '-'} step={event['step'] or '-'} "
            f"attempt={event['attempt'] or '-'} status={event['status']} calls={event['commands_used']}") if label else None
