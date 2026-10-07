"""Core internal alpha: sequential, approved local hooks using the existing V2 planner.

This does not qualify a Host or implement production G2 governance. Hook code is
trusted owner-reviewed code; filesystem, process-tree and network isolation are
not provided. No arbitrary command is synthesized from natural language.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .common import utc_now
from .core_host import LocalHookError, exclusive_run, invoke
from .discovery import discover_skills
from .execution import _command_from_metadata
from .semantic_domains import make_trusted_applicability
from .v2 import load_plan_skills, plan_task, validate_plan

SCHEMA = "nexus.core.task.v1"
CATALOG_SCHEMA = "nexus.core.catalog.v1"
FINAL = {"completed", "failed", "blocked", "cancelled", "budget_exhausted", "ambiguous"}
HASH = re.compile(r"^[0-9a-f]{64}$")
_PROGRESS = ContextVar("core_progress", default=None)


class CoreError(ValueError):
    pass


@dataclass(frozen=True)
class CoreBudget:
    max_commands: int = 12
    total_seconds: float = 120
    step_seconds: float = 20
    max_attempts: int = 2
    max_replans: int = 1
    max_output_bytes: int = 65536
    max_artifact_bytes: int = 1048576

    def validate(self) -> None:
        for name in ("max_commands", "max_attempts", "max_replans", "max_output_bytes", "max_artifact_bytes"):
            value = getattr(self, name)
            if type(value) is not int or value < (0 if name == "max_replans" else 1):
                raise CoreError("invalid Core budget")
        if self.max_commands > 64 or self.max_attempts > 3 or self.max_replans > 1:
            raise CoreError("Core budget exceeds alpha ceilings")
        if self.max_output_bytes > 262144 or self.max_artifact_bytes > 8388608:
            raise CoreError("Core byte budget exceeds alpha ceilings")
        for value in (self.total_seconds, self.step_seconds):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 < value <= 600:
                raise CoreError("invalid Core deadline")
        if self.step_seconds > self.total_seconds:
            raise CoreError("step deadline exceeds total deadline")


def _bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _epoch(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _atomic(path: Path, data: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="core-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _save(directory: Path, state: dict) -> None:
    state["updated_at_utc"] = utc_now()
    payload = _bytes(state)
    _atomic(directory / "task.json", _bytes({"sha256": hashlib.sha256(payload).hexdigest(), "payload": state}) + b"\n")


def read_task(directory: Path) -> dict:
    try:
        if (directory / "task.json").stat().st_size > 33554432:
            raise ValueError("state too large")
        envelope = json.loads((directory / "task.json").read_text(encoding="utf-8"))
        state = envelope["payload"]
        if state["schema"] != SCHEMA or hashlib.sha256(_bytes(state)).hexdigest() != envelope["sha256"]:
            raise ValueError("integrity mismatch")
        CoreBudget(**state["budget"]).validate()
        return state
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CoreError("task state missing, malformed or corrupt; no execution allowed") from exc


def _event(state: dict, kind: str, **details: Any) -> None:
    state["events"].append({"sequence": len(state["events"]) + 1, "at_utc": utc_now(), "kind": kind, **details})
    observer = _PROGRESS.get()
    if observer is not None:
        step = next((s for s in state["steps"] if s["id"] == details.get("step")), {})
        observer({"kind": kind, "step": details.get("step"), "phase": details.get("phase"),
                  "status": state["status"], "commands_used": state["commands_used"],
                  "capability": step.get("name"), "attempt": step.get("attempts")})


def _bound(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ":" in relative:
        raise CoreError("a catalog/artifact path must be relative")
    candidate = root / relative
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise CoreError("path escaped its declared root")
    for part in [candidate, *candidate.parents]:
        if part == root.parent:
            break
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise CoreError("linked/reparse paths are not supported by Core")
    return candidate.resolve()


def _catalog(path: Path) -> tuple[dict, dict]:
    if path.stat().st_size > 262144:
        raise CoreError("catalog too large")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != CATALOG_SCHEMA or not isinstance(data.get("skills"), list) or not 1 <= len(data["skills"]) <= 32:
        raise CoreError("invalid Core catalog")
    records = discover_skills([path.parent], path.parent)
    by_path = {str(Path(record["skill_md_path"]).resolve()): record for record in records}
    skills = []
    for entry in data["skills"]:
        skill_path = _bound(path.parent, entry["skill"])
        record = by_path.get(str(skill_path))
        if record is None or record["status"] != "available":
            raise CoreError("declared Skill is unavailable")
        binding = entry.get("bindings")
        if not isinstance(binding, dict) or not binding or len(binding) > 32:
            raise CoreError("every Skill requires reviewed instruction/script byte bindings")
        for name, digest in binding.items():
            item = _bound(skill_path.parent, name)
            if not isinstance(digest, str) or not HASH.fullmatch(digest) or not item.is_file() or item.stat().st_size > 1048576 or _digest(item) != digest:
                raise CoreError("catalog artifact integrity changed")
        if "SKILL.md" not in binding:
            raise CoreError("Skill instruction binding missing")
        application = entry["applicability"]
        record["_nexus_trusted_applicability"] = make_trusted_applicability(**application, provenance="owner_approved_core_catalog")
        record["core_entry"] = entry
        skills.append(record)
    if len({item["id"] for item in skills}) != len(skills):
        raise CoreError("duplicate catalog Skill")
    return data, {"skills": skills, "agents": []}


def _command(record: dict, key: str) -> list[str]:
    root = Path(record["path"])
    command = _command_from_metadata(record["metadata"], key, root)
    # Fixed Python scripts only. -I excludes cwd/PYTHONPATH/user-site imports;
    # dependencies must be declared and reviewed in the same Skill package.
    if not command or len(command) < 2 or command[0] != sys.executable:
        raise CoreError(f"{key} must be an explicit Python script hook")
    script = _bound(root, command[1])
    if command[1] not in record["core_entry"]["bindings"] or script.suffix != ".py":
        raise CoreError("hook script is not byte-bound")
    return [sys.executable, "-I", "-X", "utf8", "-B", str(script), *command[2:]]


def _steps(plan: Any, index: dict) -> list[dict]:
    records = {item["id"]: item for item in index["skills"]}
    selected = {step.selected_resource_name for step in plan.steps}
    result = []
    for step in plan.steps:
        record = records[step.selected_resource_id]
        entry = record["core_entry"]
        dependencies = record["metadata"].get("hub_after", [])
        if not isinstance(dependencies, list) or any(not isinstance(name, str) or name not in selected for name in dependencies):
            raise CoreError("selected hook has an unresolved declared dependency")
        # Unsupported authority is represented, never executed or silently inferred.
        result.append({"id": step.step_id, "skill_id": record["id"], "name": record["name"],
                       "instruction_path": record["skill_md_path"], "bindings": entry["bindings"],
                       "authority": entry.get("authority", "missing"),
                       "retry_safe": entry.get("retry_safe") is True,
                       "after": dependencies,
                       "status": "pending", "attempts": 0, "result": None,
                       "command": _command(record, "hub_command"),
                       "validate": _command(record, "hub_validate"),
                       "repair": _command(record, "hub_repair") if "hub_repair" in record["metadata"] else None})
    ordered = []
    while result:
        ready = [item for item in result if set(item["after"]) <= {done["name"] for done in ordered}]
        if not ready:
            raise CoreError("cycle in selected hook dependencies")
        ordered.append(ready[0])
        result.remove(ready[0])
    return ordered


def prepare_task(task: str, project: Path, catalog: Path, directory: Path,
                 budget: CoreBudget | None = None, *, approval_context: dict | None = None) -> dict:
    budget = budget or CoreBudget()
    budget.validate()
    project, catalog = project.resolve(strict=True), catalog.resolve(strict=True)
    if not project.is_dir() or directory.exists():
        raise CoreError("project must exist and task directory must be new")
    _, index = _catalog(catalog)
    plan = plan_task(task, index, project)
    loaded = load_plan_skills(plan)
    validation = validate_plan(plan, loaded)
    hook_boundary = None
    try:
        steps = _steps(plan, index)
    except CoreError as exc:
        steps, hook_boundary = [], str(exc)
    state = {"schema": SCHEMA, "task_id": str(uuid4()), "task": task,
             "project": str(project), "catalog": str(catalog), "catalog_sha256": _digest(catalog),
             "interpreter": sys.executable, "interpreter_sha256": _digest(Path(sys.executable)),
             "created_at_utc": utc_now(), "updated_at_utc": utc_now(),
             "budget": asdict(budget), "commands_used": 0, "replans": 0,
             "status": "prepared", "plan": plan.to_dict(), "plan_validation": validation,
             "loaded_skills": [{k: v for k, v in item.items() if k != "instructions"} for item in loaded],
             "steps": steps, "completed_steps": [], "artifacts": [], "events": [],
             "blocker": None, "inflight": None, "receipt": None}
    if approval_context is not None:
        state["approval_context"] = approval_context
    state["approval_sha256"] = hashlib.sha256(_bytes({k: state[k] for k in (
        "task", "project", "catalog_sha256", "interpreter_sha256", "budget", "created_at_utc", "steps",
        *(["approval_context"] if approval_context is not None else []) )})).hexdigest()
    _event(state, "prepared", selected=[item["name"] for item in steps])
    if hook_boundary:
        _stop(state, "blocked", hook_boundary)
    elif validation["status"] != "passed" or not steps:
        _stop(state, "blocked", "plan has uncovered capabilities or instruction errors")
    elif any(item["authority"] != "owner_local" for item in steps):
        _stop(state, "blocked", "selected Skill needs unsupported or missing authority")
    directory.mkdir(parents=True)
    (directory / "temporary").mkdir()
    _save(directory, state)
    if state["status"] == "blocked":
        state["receipt"] = _receipt(state)
        _save(directory, state)
        _owner_decision(directory, state)
    return state


def _stop(state: dict, status: str, reason: str) -> None:
    state["status"], state["blocker"] = status, reason
    _event(state, "stop", status=status, reason=reason)


def _owner_decision(directory: Path, state: dict) -> None:
    if state["status"] in {"prepared", "paused"}:
        action = ("After reviewing the unchanged local task, approve only these bound hooks: "
                  f"`core-run \"{directory}\" --approve {state['approval_sha256']}`.")
    else:
        action = (f"Exact next authorization text: Inspect and reconcile Core task {state['task_id']} "
                  "using local non-secret evidence only. Preserve its counters and terminal result. "
                  "Do not replay it; propose a new reviewed local task only after resolving the "
                  "blocker and any unknown effects. No credential or unsupported authority is granted.")
    text = ("# Next Owner Decision\n\n"
            f"Blocker: {state['blocker']}\n\n"
            "No new task authority is inferred. Credential, payment, privilege, destructive, "
            "deployment and external effects are outside Core alpha.\n\n"
            "Smallest action: inspect the plan and reviewed local catalog, resolve the stated "
            "missing capability or approval in a separately authorized task. Do not retry an "
            "ambiguous effect.\n\n"
            f"{action}\n\n"
            "Risk: hooks run as the current user without a hostile-code sandbox. Review all "
            "bound scripts/dependencies and project scope first.\n")
    (directory / "NEXT-OWNER-DECISION.md").write_text(text, encoding="utf-8", newline="\n")


def request_cancel(directory: Path) -> None:
    read_task(directory)
    try:
        with (directory / "cancel.request").open("xb") as handle:
            handle.write(b"cancel\n")
    except FileExistsError:
        pass


def _artifacts(state: dict, result: dict) -> list[dict]:
    names = result.get("artifacts")
    if not isinstance(result.get("data"), dict) or not isinstance(names, list) or not 1 <= len(names) <= 32 or any(not isinstance(name, str) for name in names) or len(set(names)) != len(names):
        raise CoreError("successful hook must return structured data and distinct artifacts")
    artifacts = []
    for name in names:
        path = _bound(Path(state["project"]), name)
        if not path.is_file() or not 0 < path.stat().st_size <= state["budget"]["max_artifact_bytes"]:
            raise CoreError("artifact missing, empty or over budget")
        artifacts.append({"path": name, "bytes": path.stat().st_size, "sha256": _digest(path)})
    return artifacts


def _verify_artifacts(state: dict) -> None:
    for artifact in state["artifacts"]:
        path = _bound(Path(state["project"]), artifact["path"])
        if not path.is_file() or _digest(path) != artifact["sha256"]:
            raise CoreError("completed artifact changed; resume cannot trust the checkpoint")


def _dispatch(directory: Path, state: dict, step: dict, phase: str, command: list[str],
              context: dict, deadline: float) -> dict | None:
    if (directory / "cancel.request").exists():
        _stop(state, "cancelled", "operator cancellation requested")
        return None
    remaining = min(deadline - time.monotonic(),
                    _epoch(state["created_at_utc"]) + state["budget"]["total_seconds"] - time.time())
    if remaining <= 0 or state["commands_used"] >= state["budget"]["max_commands"]:
        _stop(state, "budget_exhausted", "pre-effect command/deadline budget exhausted")
        return None
    if _digest(Path(state["catalog"])) != state["catalog_sha256"]:
        raise CoreError("approved catalog changed")
    _catalog(Path(state["catalog"]))
    if state.get("approval_context", {}).get("schema") == "nexus.core.project-scope.v1":
        from .core_profiles import verify_scope
        verify_scope(Path(state["project"]), state["approval_context"])
    if sys.executable != state["interpreter"] or _digest(Path(sys.executable)) != state["interpreter_sha256"]:
        raise CoreError("approved interpreter changed")
    state["commands_used"] += 1  # Charge BEFORE dispatch; interruption never refunds it.
    state["inflight"] = {"step": step["id"], "phase": phase, "command_number": state["commands_used"]}
    _event(state, "dispatch_intent", **state["inflight"])
    _save(directory, state)
    remaining = min(deadline - time.monotonic(),
                    _epoch(state["created_at_utc"]) + state["budget"]["total_seconds"] - time.time())
    if remaining <= 0 or (directory / "cancel.request").exists():
        state["inflight"] = None  # Positively not dispatched; retain the conservative charge.
        _stop(state, "cancelled" if (directory / "cancel.request").exists() else "budget_exhausted",
              "final pre-effect cancellation/deadline gate refused dispatch")
        _save(directory, state)
        return None
    outcome = invoke(command, context, cwd=Path(state["project"]), temporary=directory / "temporary",
                     timeout=min(remaining, state["budget"]["step_seconds"]),
                     output_limit=state["budget"]["max_output_bytes"],
                     cancelled=lambda: (directory / "cancel.request").exists())
    state["inflight"] = None
    _event(state, "observation", step=step["id"], phase=phase, **outcome)
    if outcome.get("stop_reason"):
        # Direct child termination says nothing about escaped descendants or effect rollback.
        _stop(state, "cancelled" if outcome["stop_reason"] == "cancelled" else "ambiguous",
              f"{outcome['stop_reason']}; effects may be partial; automatic retry forbidden")
    elif outcome.get("result", {}).get("status") == "boundary":
        _stop(state, "blocked", f"{phase} hook reported an Owner-only boundary")
    _save(directory, state)
    return outcome


def _receipt(state: dict) -> dict:
    return {"schema": "nexus.core.receipt.v1", "task_id": state["task_id"], "status": state["status"],
            "task": state["task"], "completed_steps": state["completed_steps"],
            "commands_used": state["commands_used"], "budget": state["budget"],
            "replans": state["replans"], "artifacts": state["artifacts"], "blocker": state["blocker"],
            "scope": "trusted local hooks / internal alpha", "production_host_qualified": False,
            "g2": "HOLD"}


def run_task(directory: Path, *, approval: str | None, max_steps: int | None = None,
             progress=None) -> dict:
    """Optional progress only publishes bounded lifecycle metadata, never raw hook output."""
    token = _PROGRESS.set(progress)
    try:
        return _run_task(directory, approval=approval, max_steps=max_steps)
    finally:
        _PROGRESS.reset(token)


def _run_task(directory: Path, *, approval: str | None, max_steps: int | None = None) -> dict:
    """Resume completed checkpoints; unresolved dispatch intents STOP without re-execution."""
    if max_steps is not None and (type(max_steps) is not int or max_steps < 1):
        raise CoreError("max_steps must be a positive integer")
    directory = directory.resolve(strict=True)
    with exclusive_run(directory):
        state = read_task(directory)
        if state["status"] in FINAL:
            return state
        if approval != state["approval_sha256"]:
            # Approval is an explicit opt-in, not inferred from natural language or a tool result.
            state["blocker"] = "exact local catalog/plan approval required"
            _event(state, "approval_required")
            _save(directory, state)
            _owner_decision(directory, state)
            return state
        if state["inflight"] or state["status"] == "running":
            _stop(state, "ambiguous", "interrupted dispatch has unknown effects; inspect before a new task")
        elif time.time() < _epoch(state["updated_at_utc"]):
            _stop(state, "blocked", "wall clock moved backwards")
        try:
            _verify_artifacts(state)
            if state["status"] not in FINAL:
                state["status"], state["blocker"] = "running", None
                _event(state, "run_started")
                _save(directory, state)
                _continue(directory, state, max_steps)
        except (CoreError, LocalHookError, OSError, ValueError) as exc:
            _stop(state, "ambiguous" if state["inflight"] else "blocked", str(exc))
        except KeyboardInterrupt:
            _stop(state, "ambiguous" if state["inflight"] else "cancelled", "runner interrupted; no automatic retry")
        state["receipt"] = _receipt(state)
        _save(directory, state)
        if state["status"] in {"blocked", "ambiguous"}:
            _owner_decision(directory, state)
        return state


def _continue(directory: Path, state: dict, max_steps: int | None) -> None:
    deadline = time.monotonic() + max(0, _epoch(state["created_at_utc"]) + state["budget"]["total_seconds"] - time.time())
    completed_here = 0
    position = 0
    while position < len(state["steps"]):
        step = state["steps"][position]
        if step["status"] == "completed":
            position += 1
            continue
        if max_steps is not None and completed_here >= max_steps:
            state["status"] = "paused"
            _event(state, "checkpoint_pause")
            return
        inputs = {item["name"]: item["result"] for item in state["steps"] if item["status"] == "completed"}
        context = {"schema": "nexus.core.input.v1", "task": state["task"], "project": state["project"],
                   "task_id": state["task_id"], "inputs": inputs, "attempt": step["attempts"] + 1}
        step["attempts"] += 1
        observation = _dispatch(directory, state, step, "execute", step["command"], context, deadline)
        if observation is None or state["status"] in FINAL:
            return
        result = observation.get("result", {})
        success = observation["returncode"] == 0 and result.get("status") == "ok"
        if success:
            try:
                artifacts = _artifacts(state, result)
            except CoreError:
                success = False
                result = {"status": "error", "failure_kind": "incomplete_result", "retryable": False}
            else:
                verification = _dispatch(directory, state, step, "verify", step["validate"],
                                         {**context, "result": result}, deadline)
                if verification is None or state["status"] in FINAL:
                    return
                verified = verification.get("result", {})
                success = verification["returncode"] == 0 and verified.get("status") == "ok" and verified.get("verified") is True
                # Verifier must observe, not silently alter, the returned artifacts.
                if success and artifacts != _artifacts(state, result):
                    raise CoreError("validator changed the artifacts")
                if not success:
                    result = {"status": "error", "failure_kind": "verification_failed", "retryable": True}
        if success:
            step.update(status="completed", result=result)
            state["completed_steps"].append(step["id"])
            state["artifacts"].extend(artifacts)
            _event(state, "step_completed", step=step["id"])
            _save(directory, state)
            completed_here += 1
            position += 1
            continue
        kind = result.get("failure_kind", observation.get("result_error", "command_failure"))
        _event(state, "failure", step=step["id"], failure_kind=kind)
        if kind in {"wrong_resource", "missing_capability", "bad_plan"} and result.get("no_effect") is True and not state["completed_steps"]:
            if state["replans"] >= state["budget"]["max_replans"]:
                _stop(state, "failed", "bounded replan exhausted")
                return
            # Reuse V2 selection; exclude the failed resource, preserving other candidates.
            _, index = _catalog(Path(state["catalog"]))
            excluded = set(state.get("excluded_skills", [])) | {step["skill_id"]}
            state["excluded_skills"] = sorted(excluded)
            plan = plan_task(state["task"], index, Path(state["project"]), excluded_resource_ids=excluded, replan_attempt=1)
            loaded = load_plan_skills(plan)
            validation = validate_plan(plan, loaded)
            state["replans"] += 1
            if validation["status"] != "passed":
                _stop(state, "blocked", "replan needs an unavailable capability")
                return
            state["plan"], state["steps"] = plan.to_dict(), _steps(plan, index)
            if any(item["authority"] != "owner_local" for item in state["steps"]):
                _stop(state, "blocked", "replan needs unsupported authority")
                return
            _event(state, "replanned", excluded=sorted(excluded))
            _save(directory, state)
            position = 0
            continue
        if not step["retry_safe"] or result.get("retryable") is not True or step["attempts"] >= state["budget"]["max_attempts"]:
            _stop(state, "failed", f"{kind}; automatic retry unavailable or exhausted")
            return
        if step["repair"]:
            repair = _dispatch(directory, state, step, "repair", step["repair"], {**context, "failure": result}, deadline)
            if repair is None or state["status"] in FINAL:
                return
            if repair["returncode"] != 0 or repair.get("result", {}).get("status") != "ok":
                _stop(state, "failed", "approved repair hook failed")
                return
        _event(state, "retry", step=step["id"])
        _save(directory, state)
    _verify_artifacts(state)
    state["status"] = "completed"
    _event(state, "task_completed")
