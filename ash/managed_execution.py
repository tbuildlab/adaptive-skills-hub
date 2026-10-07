"""G2-OPENAI offline artifact handoff. No provider calls or command execution.

The local same-user trust model and atomic checkpoint/lock primitives match Core
Alpha 2. Checksums are corruption detection, not authentication or attestation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Protocol
from uuid import uuid4

from .core import _atomic, _bytes
from .core_capabilities import ScopeError, load_json, read_bytes, safe_path, sha
from .core_host import exclusive_run

SCHEMA = "nexus.execution.request.v1"
STATE_SCHEMA = "nexus.execution.state.v1"
RECEIPT_SCHEMA = "nexus.execution.receipt.v1"
HASH = re.compile(r"[a-f0-9]{64}\Z")
OWNER_EFFECTS = {"credentials", "payments", "destructive", "account_creation",
                 "deployment", "elevation", "irreversible", "high_cost", "unsupported_authority"}


class ExecutionError(ValueError):
    pass


class ExecutionStatus(str, Enum):
    PREPARED = "PREPARED"
    HANDOFF_INTENT = "HANDOFF_INTENT"
    HANDOFF_PREPARED = "HANDOFF_PREPARED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    TASK_VERIFIED_COMPLETE = "TASK_VERIFIED_COMPLETE"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    FAILED = "FAILED"
    AMBIGUOUS = "AMBIGUOUS"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    PROVIDER_ACKNOWLEDGED = "PROVIDER_ACKNOWLEDGED"
    EXECUTION_STOPPED = "EXECUTION_STOPPED"
    RESULT_RECONCILED = "RESULT_RECONCILED"


@dataclass(frozen=True)
class ExecutionCapability:
    capability_id: str = "artifact-handoff"
    version: str = "1"
    subject_sha256: str = ""


@dataclass(frozen=True)
class ExecutionBoundary:
    allowed_effects: tuple[str, ...] = ("output_artifacts",)
    owner_approval_required: bool = True
    remote_enforcement: str = "HOST_REVIEW_REQUIRED"


@dataclass(frozen=True)
class ExecutionBudget:
    max_attempts: int = 2
    max_replans: int = 1
    max_artifact_bytes: int = 1048576
    cost_class: str = "NO_PAID_DISPATCH_AUTHORIZED"
    declared_provider_budget: float | None = None
    hard_financial_cap: bool = False


@dataclass(frozen=True)
class ExecutionRequest:
    task_id: str
    task: str
    category: str
    backend_id: str
    capability: dict
    project_scope: dict
    boundary: dict
    artifacts: list[dict]
    budget: dict
    retry_policy: dict
    expires_at: float
    attempt: int = 1
    schema: str = SCHEMA

    def digest(self) -> str:
        return sha(_bytes(asdict(self)))


@dataclass(frozen=True)
class ExecutionArtifact:
    path: str
    sha256: str
    bytes: int


@dataclass(frozen=True)
class ExecutionFailure:
    kind: str
    no_effects_confirmed: bool


@dataclass(frozen=True)
class ExecutionReceipt:
    data: dict


class ExecutionBackend(Protocol):
    """A future reviewed transport must implement these, with real API evidence."""
    backend_id: str

    def submit(self, request: ExecutionRequest) -> ExecutionReceipt: ...
    def observe(self, execution_id: str) -> ExecutionReceipt: ...
    def cancel(self, execution_id: str) -> ExecutionReceipt: ...


def route_backend(category: str, effects: list[str], *, local_supported=False,
                  managed_supported=False, host_supported=False) -> dict:
    if set(effects) & OWNER_EFFECTS:
        return {"backend": "OWNER_BOUNDARY", "reason": "OWNER_AUTHORITY_REQUIRED"}
    if set(effects) != {"output_artifacts"}:
        return {"backend": "UNSUPPORTED", "reason": "EFFECT_CLASS_UNSUPPORTED"}
    if category == "local" and local_supported:
        return {"backend": "LOCAL_CORE", "reason": "EXISTING_REVIEWED_CORE_PROFILE"}
    if category == "coding" and managed_supported:
        return {"backend": "OPENAI_MANAGED", "reason": "REVIEWED_CALLABLE_ADAPTER"}
    if category in {"coding", "browser", "app"} and host_supported:
        return {"backend": "HOST_HANDOFF", "reason": "DIRECT_PROVIDER_ADAPTER_UNAVAILABLE"}
    return {"backend": "UNSUPPORTED", "reason": "EXECUTION_SURFACE_UNSUPPORTED"}


def _closed(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise ExecutionError("unknown or missing contract fields")


def _text(value, limit=160):
    if type(value) is not str or not value or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ExecutionError("invalid bounded text")


def _list(value, limit=32):
    if type(value) is not list or len(value) > limit:
        raise ExecutionError("invalid bounded list")


def _hash(value):
    if type(value) is not str or not HASH.fullmatch(value):
        raise ExecutionError("invalid SHA-256")


def _directory(path: Path) -> Path:
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ExecutionError("linked state/project directory refused")
    return path.resolve()


def _baseline(project):
    # Read-only, fixed argv. No remote URL, credentials or Git configuration read.
    try:
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=project,
                                capture_output=True, timeout=5, check=False)
        if result.returncode:
            return None
        if Path(result.stdout.decode().strip()).resolve() != project:
            raise ExecutionError("use the repository root to bind its exact baseline")
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project,
                                capture_output=True, timeout=5, check=False)
        value = result.stdout.decode().strip()
        if result.returncode or not re.fullmatch(r"[a-f0-9]{40,64}", value):
            raise ExecutionError("repository baseline unavailable")
        return value
    except FileNotFoundError:
        if (project / ".git").exists():
            raise ExecutionError("Git baseline cannot be bound")
        return None
    except (subprocess.TimeoutExpired, UnicodeError) as exc:
        raise ExecutionError("repository baseline unavailable") from exc


def _save(directory, state):
    _atomic(directory / "execution.json", _bytes({"sha256": sha(_bytes(state)), "payload": state}) + b"\n")


def _event(state, status):
    state["status"] = status
    state["events"].append({"sequence": len(state["events"]) + 1, "status": status})


def read_execution(directory: Path) -> dict:
    directory = _directory(directory)
    try:
        path = safe_path(directory, "execution.json")
        if path.stat().st_nlink > 1:
            raise ExecutionError("hard-linked ledger refused")
        value = load_json(path)
        _closed(value, {"sha256", "payload"})
        state = value["payload"]
        if state["schema"] != STATE_SCHEMA or sha(_bytes(state)) != value["sha256"]:
            raise ExecutionError("state checksum/schema mismatch")
        if sha(_bytes(state["request"])) != state["request_digest"]:
            raise ExecutionError("request binding mismatch")
        if state["status"] not in {s.value for s in ExecutionStatus} | {"BLOCKED"}:
            raise ExecutionError("unknown execution state")
        return state
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ExecutionError("execution state missing, corrupt or malformed; no replay") from exc


def prepare_execution(task: str, project: Path, spec: dict, directory: Path) -> dict:
    _text(task, 4000)
    _closed(spec, {"schema", "category", "files", "effects", "artifacts", "ttl_seconds"})
    if spec["schema"] != "nexus.execution.spec.v1":
        raise ExecutionError("unsupported execution spec")
    _text(spec["category"])
    _list(spec["files"])
    _list(spec["effects"], 10)
    _list(spec["artifacts"], 8)
    if not spec["files"] or not spec["artifacts"]:
        raise ExecutionError("explicit inputs and artifact expectations required")
    if type(spec["ttl_seconds"]) is not int or not 1 <= spec["ttl_seconds"] <= 86400:
        raise ExecutionError("invalid expiry budget")
    for effect in spec["effects"]:
        _text(effect)
    project, directory = _directory(project), _directory(directory)
    if not project.is_dir() or directory.exists():
        raise ExecutionError("project must exist and state directory must be new")
    for name in spec["files"]:
        safe_path(project, name)
    names = [a["path"] for a in spec["artifacts"] if type(a) is dict and "path" in a]
    for name in names:
        safe_path(directory, name)
    for group in (spec["files"], names):
        if len({n.casefold() for n in group}) != len(group):
            raise ExecutionError("duplicate/colliding path")
    if any(b.casefold().startswith(a.casefold() + "/") for a in names for b in names if a != b):
        raise ExecutionError("artifact file/directory collision")
    for artifact in spec["artifacts"]:
        _closed(artifact, {"path", "verification", "expected_sha256"})
        if artifact["verification"] == "sha256":
            _hash(artifact["expected_sha256"])
        elif artifact["verification"] != "owner_review" or artifact["expected_sha256"] is not None:
            raise ExecutionError("unsupported artifact verifier")
    routing = route_backend(spec["category"], spec["effects"], host_supported=True)
    # Unsupported/Owner-boundary requests never read project content.
    inputs = {name: sha(read_bytes(project, name)) for name in spec["files"]} if routing["backend"] == "HOST_HANDOFF" else {}
    if sum(len(read_bytes(project, name)) for name in inputs) > 262144:
        raise ExecutionError("input transfer exceeds total budget")
    capability = ExecutionCapability(subject_sha256=sha(Path(__file__).read_bytes()))
    request = ExecutionRequest(str(uuid4()), task, spec["category"], "openai-host-handoff.v1",
        asdict(capability), {"project_id": project.name, "baseline_commit": _baseline(project), "inputs": inputs},
        asdict(ExecutionBoundary(tuple(spec["effects"]))), spec["artifacts"], asdict(ExecutionBudget()),
        {"retry_safe": True, "automatic_retry": False, "ambiguous_replay": False},
        time.time() + spec["ttl_seconds"])
    state = {"schema": STATE_SCHEMA, "project": str(project), "request": json.loads(_bytes(asdict(request))),
             "request_digest": request.digest(), "routing": routing, "status": "PREPARED",
             "attempts": 0, "replans": 0, "provider_reference": None, "receipt": None,
             "artifacts": [], "verification": "NOT_STARTED", "ambiguity": None,
             "retry_eligible": False, "cancel_requested": False, "events": []}
    _event(state, "PREPARED" if routing["backend"] == "HOST_HANDOFF" else "BLOCKED")
    directory.mkdir(parents=True)
    _save(directory, state)
    return state


def _scope(state):
    request = state["request"]
    if time.time() >= request["expires_at"]:
        raise ExecutionError("request expired; deadline cannot reset on resume")
    if request["capability"]["subject_sha256"] != sha(Path(__file__).read_bytes()):
        raise ExecutionError("reviewed capability changed; new plan required")
    project = _directory(Path(state["project"]))
    if _baseline(project) != request["project_scope"]["baseline_commit"]:
        raise ExecutionError("Git baseline changed")
    for name, digest in request["project_scope"]["inputs"].items():
        if sha(read_bytes(project, name)) != digest:
            raise ExecutionError("approved input changed")


def export_handoff(directory: Path, approval: str) -> dict:
    directory = _directory(directory)
    with exclusive_run(directory):
        state = read_execution(directory)
        if approval != state["request_digest"]:
            raise ExecutionError("exact request approval required")
        if state["status"] != "PREPARED" or state["cancel_requested"] or state["routing"]["backend"] != "HOST_HANDOFF":
            raise ExecutionError("handoff is not eligible; no blind replay")
        _scope(state)
        project = Path(state["project"])
        inputs = {n: read_bytes(project, n).decode("utf-8") for n in state["request"]["project_scope"]["inputs"]}
        handoff = {"schema": "nexus.execution.handoff.v1", "request": state["request"],
                   "request_digest": state["request_digest"], "inputs": inputs,
                   "dispatch": "HOST_AUTHORITY_AND_REAL_SURFACE_REVIEW_REQUIRED",
                   "provider_execution_started": False}
        # Intent first: a failed/crashed file write may not authorize re-export.
        state["attempts"] += 1
        _event(state, "HANDOFF_INTENT")
        _save(directory, state)
        target = safe_path(directory, f"handoff-{state['request']['attempt']}.json")
        if target.exists():
            raise ExecutionError("handoff output already exists")
        _atomic(target, _bytes(handoff) + b"\n")
        _event(state, "HANDOFF_PREPARED")
        _save(directory, state)
        return state


def parse_receipt(value: dict, request: dict, digest: str) -> ExecutionReceipt:
    _closed(value, {"schema", "execution_id", "backend_id", "task_id", "request_digest", "attempt",
                    "start_status", "end_status", "artifacts", "changed_files", "checks", "exit_status",
                    "warnings", "ambiguity", "continuation_reference", "provider_metadata", "usage",
                    "failure", "cancel_phase", "actual_effects"})
    if (value["schema"] != RECEIPT_SCHEMA or value["backend_id"] != request["backend_id"]
            or value["task_id"] != request["task_id"] or value["request_digest"] != digest
            or type(value["attempt"]) is not int or value["attempt"] != request["attempt"]):
        raise ExecutionError("receipt request/attempt binding mismatch")
    _text(value["execution_id"])
    if value["start_status"] not in {"NOT_STARTED", "STARTED"} or value["end_status"] not in {"completed", "failed", "ambiguous", "cancelled"}:
        raise ExecutionError("invalid provider status")
    if value["end_status"] == "completed" and (value["start_status"] != "STARTED" or value["exit_status"] != 0 or type(value["exit_status"]) is not int):
        raise ExecutionError("inconsistent completed receipt")
    if value["exit_status"] is not None and type(value["exit_status"]) is not int:
        raise ExecutionError("invalid exit status")
    for field, limit in (("artifacts", 8), ("changed_files", 32), ("checks", 32), ("warnings", 8), ("actual_effects", 10)):
        _list(value[field], limit)
    if value["changed_files"] or set(value["actual_effects"]) - {"output_artifacts"}:
        raise ExecutionError("reported effects exceed artifact-only authority")
    for text in value["checks"] + value["warnings"]:
        _text(text)
    if type(value["ambiguity"]) is not bool:
        raise ExecutionError("ambiguity must be explicit")
    if value["continuation_reference"] is not None:
        _text(value["continuation_reference"])
    if type(value["provider_metadata"]) is not dict or set(value["provider_metadata"]) - {"model", "response_id", "environment_id"}:
        raise ExecutionError("unsupported provider metadata")
    for text in value["provider_metadata"].values():
        _text(text)
    # No monetary telemetry is invented: only explicit provider token counts.
    if value["usage"] is not None:
        _closed(value["usage"], {"input_tokens", "output_tokens"})
        if any(type(n) is not int or n < 0 for n in value["usage"].values()):
            raise ExecutionError("invalid usage evidence")
    if value["failure"] is not None:
        _closed(value["failure"], {"kind", "no_effects_confirmed"})
        if value["failure"]["kind"] not in {"transient_provider", "implementation", "wrong_capability", "missing_capability", "owner_boundary", "provider_unavailable", "verification"} or type(value["failure"]["no_effects_confirmed"]) is not bool:
            raise ExecutionError("invalid failure classification")
    if (value["end_status"] == "failed") != (value["failure"] is not None):
        raise ExecutionError("inconsistent failure receipt")
    if value["cancel_phase"] not in {None, "PROVIDER_ACKNOWLEDGED", "EXECUTION_STOPPED", "RESULT_RECONCILED"}:
        raise ExecutionError("unknown cancellation evidence")
    if (value["end_status"] == "cancelled") != (value["cancel_phase"] is not None):
        raise ExecutionError("inconsistent cancellation receipt")
    if value["end_status"] == "cancelled" and (value["artifacts"] or value["actual_effects"]):
        raise ExecutionError("cancellation effects require separate manual reconciliation")
    names = []
    for artifact in value["artifacts"]:
        _closed(artifact, {"path", "sha256", "bytes"})
        safe_path(Path.cwd(), artifact["path"])
        _hash(artifact["sha256"])
        if type(artifact["bytes"]) is not int or not 0 <= artifact["bytes"] <= 262144:
            raise ExecutionError("artifact byte ceiling exceeded")
        names.append(artifact["path"].casefold())
    if len(set(names)) != len(names) or sum(a["bytes"] for a in value["artifacts"]) > request["budget"]["max_artifact_bytes"]:
        raise ExecutionError("duplicate artifact or total byte ceiling exceeded")
    if value["start_status"] == "NOT_STARTED" and (value["artifacts"] or value["actual_effects"]):
        raise ExecutionError("pre-execution failure reports effects")
    return ExecutionReceipt(value)


def receive_execution(directory: Path, receipt_path: Path, artifact_root: Path) -> dict:
    directory, artifact_root = _directory(directory), _directory(artifact_root)
    with exclusive_run(directory):
        state = read_execution(directory)
        if state["status"] not in {"HANDOFF_INTENT", "HANDOFF_PREPARED", "CANCEL_REQUESTED", "PROVIDER_ACKNOWLEDGED", "EXECUTION_STOPPED"}:
            raise ExecutionError("late/replayed receipt or no handoff")
        _directory(receipt_path.parent)
        if receipt_path.is_symlink() or getattr(receipt_path.lstat(), "st_file_attributes", 0) & 0x400 or receipt_path.stat().st_nlink > 1:
            raise ExecutionError("linked receipt refused")
        value = parse_receipt(load_json(receipt_path), state["request"], state["request_digest"]).data
        if state["provider_reference"] is not None and value["execution_id"] != state["provider_reference"]:
            raise ExecutionError("provider execution reference changed during reconciliation")
        cancellation = ["CANCEL_REQUESTED", "PROVIDER_ACKNOWLEDGED", "EXECUTION_STOPPED", "RESULT_RECONCILED"]
        if state["status"] in cancellation and value["cancel_phase"] is not None:
            if cancellation.index(value["cancel_phase"]) <= cancellation.index(state["status"]):
                raise ExecutionError("cancellation evidence cannot replay or regress")
        # Late evidence may reconcile effects after expiry; never renew dispatch.
        state["receipt"] = value
        state["provider_reference"] = value["execution_id"]
        state["ambiguity"] = value["ambiguity"]
        if value["ambiguity"] or value["end_status"] == "ambiguous":
            _event(state, "AMBIGUOUS")
        elif state["cancel_requested"]:
            phase = value["cancel_phase"]
            _event(state, phase if phase else "CANCEL_REQUESTED")
        elif value["end_status"] == "cancelled":
            raise ExecutionError("unsolicited cancellation receipt")
        elif value["end_status"] == "failed":
            failure = value["failure"]
            state["retry_eligible"] = (failure["kind"] in {"transient_provider", "provider_unavailable"}
                and failure["no_effects_confirmed"] and value["start_status"] == "NOT_STARTED"
                and not value["warnings"] and state["attempts"] < state["request"]["budget"]["max_attempts"])
            _event(state, "FAILED")
        else:
            _event(state, "EXECUTION_COMPLETED")
            _save(directory, state)
            expected = {a["path"]: a for a in state["request"]["artifacts"]}
            actual = {a["path"]: a for a in value["artifacts"]}
            verified, pending = [], False
            try:
                if set(actual) != set(expected) or value["warnings"] or value["actual_effects"] != ["output_artifacts"]:
                    raise ExecutionError("missing/extra output, effect mismatch or warning")
                data = {}
                for name, artifact in actual.items():
                    content = read_bytes(artifact_root, name)
                    if len(content) != artifact["bytes"] or sha(content) != artifact["sha256"]:
                        raise ExecutionError("returned artifact integrity mismatch")
                    check = expected[name]
                    if check["verification"] == "sha256" and sha(content) != check["expected_sha256"]:
                        raise ExecutionError("independent expected artifact verification failed")
                    pending |= check["verification"] == "owner_review"
                    data[name] = content
                    verified.append(artifact)
                output = safe_path(directory, f"artifacts-{state['request']['attempt']}")
                if output.exists():
                    raise ExecutionError("task output already exists; reconciliation required")
                output.mkdir()
                for name, content in data.items():
                    target = safe_path(output, name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    _atomic(target, content)
                state["artifacts"] = verified
                state["verification"] = "OWNER_REVIEW_REQUIRED" if pending else "EXPECTED_HASHES_PASSED"
                _event(state, "VERIFICATION_REQUIRED" if pending else "TASK_VERIFIED_COMPLETE")
            except (ExecutionError, ScopeError, OSError):
                state["verification"] = "FAILED"
                state["ambiguity"] = "OUTPUT_RECONCILIATION_REQUIRED"
                _event(state, "VERIFICATION_FAILED")
        _save(directory, state)
        return state


def retry_execution(directory: Path, approval: str) -> dict:
    directory = _directory(directory)
    with exclusive_run(directory):
        state = read_execution(directory)
        if approval != state["request_digest"] or state["status"] != "FAILED" or not state["retry_eligible"] or state["cancel_requested"]:
            raise ExecutionError("retry refused: approval, failure or ambiguity boundary")
        _scope(state)
        if state["attempts"] >= state["request"]["budget"]["max_attempts"]:
            raise ExecutionError("attempt ceiling reached")
        state["request"]["attempt"] += 1
        state["request_digest"] = sha(_bytes(state["request"]))
        state.update(receipt=None, provider_reference=None, retry_eligible=False)
        _event(state, "PREPARED")
        _save(directory, state)
        return state


def cancel_execution(directory: Path) -> dict:
    directory = _directory(directory)
    with exclusive_run(directory):
        state = read_execution(directory)
        if state["status"] in {"TASK_VERIFIED_COMPLETE", "VERIFICATION_REQUIRED", "VERIFICATION_FAILED", "FAILED", "AMBIGUOUS", "RESULT_RECONCILED", "BLOCKED"}:
            return state
        if not state["cancel_requested"]:
            state["cancel_requested"] = True
            _event(state, "CANCEL_REQUESTED")
            _save(directory, state)
        return state


def execution_summary(state: dict) -> dict:
    return {"BACKEND": state["routing"]["backend"], "CAPABILITIES": state["request"]["capability"],
            "EXPECTED_EFFECTS": state["request"]["boundary"]["allowed_effects"],
            "APPROVAL": state["request_digest"], "STATUS": state["status"],
            "ARTIFACTS": state["artifacts"], "VERIFICATION": state["verification"],
            "FINAL_RESULT": "TASK_VERIFIED_COMPLETE" if state["status"] == "TASK_VERIFIED_COMPLETE" else "NOT_COMPLETE",
            "provider_reference": state["provider_reference"], "retry_eligible": state["retry_eligible"],
            "cancel_requested": state["cancel_requested"], "attempts": state["attempts"],
            "direct_provider_execution": "UNAVAILABLE",
            "provider_provenance": "HOST_REPORTED_UNAUTHENTICATED" if state["receipt"] else "NOT_OBSERVED",
            "hard_financial_cap": False, "production_positive_host_binding": "ABSENT"}
