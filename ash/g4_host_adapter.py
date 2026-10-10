"""Pure OpenAI/Host G4 preparation seam. Never dispatches or grants permission.

StructuralSession owns only bounded in-process test consumption. Restart does
not restore eligibility; real recovery belongs to existing G2/D03 contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any
from uuid import uuid4
from threading import RLock

from .g1_profiles import G1Error, exact, integer, sha, tokens, enum
from .g3_authorization import EligibilityDecision
from .managed_execution import ExecutionStatus
from .g4_contracts import G4Error, binding, canonical, digest, parse, require, validate_domain_bundle

REQUEST_SCHEMA = "nexus.g4.openai-execution-request.v1"
RESULT_SCHEMA = "nexus.g4.openai-execution-result.v1"
FIXTURE_SCHEMA = "nexus.g4.structural-authority.v1"
BASIS = "TEST_ONLY_STRUCTURAL_FIXTURE_NON_AUTHORITATIVE"
MAX_ACTIONS = 64
MAX_AGE = 300
_STATUS = {
    "COMPLETED": ExecutionStatus.VERIFICATION_REQUIRED.value,
    "FAILED": ExecutionStatus.FAILED.value,
    "CANCELLED": ExecutionStatus.CANCEL_REQUESTED.value,
    "UNKNOWN": ExecutionStatus.OUTCOME_UNKNOWN.value,
}


class RecoveryFencePort(Protocol):
    """Future qualified seam; current responses cannot enable positive admission."""
    def status(self, binding_sha256: str) -> str: ...


@dataclass(frozen=True, slots=True)
class UnqualifiedRecoveryFence:
    def status(self, binding_sha256: str) -> str:
        return "UNQUALIFIED"


def request(value: Any) -> dict:
    try:
        canonical(value)
        exact(value, {"schema_version", "binding", "operations", "expires_at", "requires_recovery"})
        require(value["schema_version"] == REQUEST_SCHEMA)
        binding(value["binding"])
        operations = tokens(value["operations"], nonempty=True)
        require(set(operations) <= {"read", "write", "execute", "network", "delegate"})
        integer(value["expires_at"])
        require(type(value["requires_recovery"]) is bool)
        return parse(canonical({**value, "operations": operations}))
    except (G1Error, KeyError, TypeError):
        raise G4Error("G4_INVALID_INPUT") from None


def _decision(reason: str, *, structural: bool = False) -> dict:
    return {"schema_version": "nexus.g4.gate-decision.v1",
            "status": "ALLOW_STRUCTURAL_TEST_ONLY" if structural else "DENY",
            "reason": reason, "basis": BASIS if structural else "REAL_ADMISSION_DISABLED",
            "dispatch_authority": "none", "real_admission_enabled": False}


def pre_execution_gate(value: Any, g3_authority: EligibilityDecision | None = None, *, now: int) -> dict:
    """Production API accepts typed G3 evidence only; every path returns DENY."""
    try:
        r = request(value)
        integer(now)
        if now >= r["expires_at"]:
            return _decision("G4_REQUEST_EXPIRED")
        if g3_authority is None:
            return _decision("G4_G3_AUTHORITY_MISSING")
        if type(g3_authority) is not EligibilityDecision:
            return _decision("G4_G3_AUTHORITY_MALFORMED")
        # Revalidate even manually forged dataclass instances before inspecting.
        g3_authority.__post_init__()
        if g3_authority.basis == "TEST_FIXTURE_ONLY":
            return _decision("G4_PRODUCTION_FIXTURE_REJECTED")
        return _decision("G4_G3_INCOMPLETE")
    except (G4Error, G1Error, ValueError, TypeError, AttributeError):
        return _decision("G4_INVALID_INPUT")


def structural_fixture(value: Any, *, now: int, session_id: str) -> dict:
    """Data fixture only. It is explicitly rejected by pre_execution_gate."""
    r = request(value)
    try:
        integer(now)
        require(now < r["expires_at"] <= now + MAX_AGE)
        from .g1_profiles import token
        token(session_id)
        return {"schema_version": FIXTURE_SCHEMA, "basis": BASIS, "session_id": session_id,
                "binding": r["binding"], "operations": r["operations"],
                "issued_at": now, "expires_at": r["expires_at"], "dispatch_authority": "none"}
    except G1Error:
        raise G4Error("G4_INVALID_INPUT") from None


def result(value: Any, expected_binding: dict, *, now: int) -> dict:
    """Closed evidence projection; raw stdout, prose, metadata and secrets refused."""
    try:
        canonical(value)
        exact(value, {"schema_version", "basis", "binding", "status", "observed_at", "evidence"})
        require(value["schema_version"] == RESULT_SCHEMA and value["basis"] == BASIS)
        binding(value["binding"])
        require(value["binding"] == expected_binding, "G4_BINDING_MISMATCH")
        enum(value["status"], _STATUS)
        integer(now)
        integer(value["observed_at"])
        require(0 <= now - value["observed_at"] <= MAX_AGE, "G4_EVIDENCE_STALE")
        require(type(value["evidence"]) is list and 1 <= len(value["evidence"]) <= 64)
        seen = set()
        for evidence in value["evidence"]:
            exact(evidence, {"type", "source", "sha256", "ref", "observed_at", "result"})
            enum(evidence["type"], {"artifact", "validation", "failure", "cancellation", "unknown"})
            enum(evidence["source"], {"OPENAI_HOST", "LOCAL_CHECK", "STRUCTURAL_FIXTURE"})
            enum(evidence["result"], {"PASS", "FAIL", "UNKNOWN", "REQUESTED", "ACKNOWLEDGED"})
            sha(evidence["sha256"])
            sha(evidence["ref"])
            integer(evidence["observed_at"])
            require(0 <= now - evidence["observed_at"] <= MAX_AGE, "G4_EVIDENCE_STALE")
            require(evidence["observed_at"] <= value["observed_at"], "G4_EVIDENCE_STALE")
            require(evidence["ref"] not in seen)
            seen.add(evidence["ref"])
        status = value["status"]
        required_type = {"COMPLETED": "artifact", "FAILED": "failure", "CANCELLED": "cancellation", "UNKNOWN": "unknown"}[status]
        expected_results = {"COMPLETED": {"PASS"}, "FAILED": {"FAIL"}, "CANCELLED": {"REQUESTED", "ACKNOWLEDGED"}, "UNKNOWN": {"UNKNOWN"}}[status]
        require(any(e["type"] == required_type and e["result"] in expected_results for e in value["evidence"]), "G4_RESULT_EVIDENCE_MISSING")
        require(status != "COMPLETED" or all(e["result"] == "PASS" and e["type"] not in {"failure", "unknown", "cancellation"} for e in value["evidence"]), "G4_RESULT_CONTRADICTION")
        return {"schema_version": "nexus.g4.sanitized-execution-record.v1", "basis": BASIS,
                "binding_sha256": digest(expected_binding), "result_sha256": digest(value),
                "status": _STATUS[status], "host_reported_status": status,
                "evidence_refs": sorted(seen), "dispatch_authority": "none",
                "verification": "STRUCTURAL_ONLY_NOT_RUNTIME_QUALIFIED"}
    except (G1Error, KeyError, TypeError):
        raise G4Error("G4_INVALID_INPUT") from None


class StructuralSession:
    """Test-only consumption ledger, not an execution session or durable authority.

    No callback/dispatcher, restoration, retry, renewal or production promotion.
    The owner/host must independently perform any authorized work.
    """
    def __init__(self, recovery: RecoveryFencePort | None = None):
        self._recovery = recovery if recovery is not None else UnqualifiedRecoveryFence()
        self._session_id = "structural-" + uuid4().hex
        self._lock = RLock()
        self._seen: set[str] = set()
        self._pending: dict[str, tuple[dict, int]] = {}

    def fixture(self, value: Any, *, now: int) -> dict:
        return structural_fixture(value, now=now, session_id=self._session_id)

    def check(self, value: Any, fixture: Any, *, now: int) -> dict:
        with self._lock:
            return self._check(value, fixture, now=now)

    def check_domain(self, value: Any, fixture: Any, *, bundle: dict, now: int) -> dict:
        """Compose the accepted pack checks with this same request's test gate."""
        with self._lock:
            try:
                r = request(value)
                require(type(bundle) is dict)
                require(bundle.get("expected_binding") == r["binding"] and bundle.get("now") == now,
                        "G4_BINDING_MISMATCH")
                verdict = validate_domain_bundle(**bundle)
                decision = self._check(r, fixture, now=now)
                if decision["status"] == "ALLOW_STRUCTURAL_TEST_ONLY":
                    return {**decision, "domain_pack_ref": verdict["pack_ref"]}
                return decision
            except G4Error as exc:
                return _decision(str(exc))
            except (G1Error, TypeError):
                return _decision("G4_INVALID_INPUT")

    def _check(self, value: Any, fixture: Any, *, now: int) -> dict:
        try:
            r = request(value)
            canonical(fixture)
            exact(fixture, {"schema_version", "basis", "session_id", "binding", "operations", "issued_at", "expires_at", "dispatch_authority"})
            require(fixture["session_id"] == self._session_id, "G4_SESSION_MISMATCH")
            integer(now)
            integer(fixture["issued_at"])
            integer(fixture["expires_at"])
            require(fixture["schema_version"] == FIXTURE_SCHEMA and fixture["basis"] == BASIS and fixture["dispatch_authority"] == "none")
            binding(fixture["binding"])
            require(fixture["binding"] == r["binding"], "G4_BINDING_MISMATCH")
            require(tokens(fixture["operations"]) == r["operations"], "G4_SCOPE_MISMATCH")
            require(fixture["issued_at"] <= now < fixture["expires_at"] == r["expires_at"] <= fixture["issued_at"] + MAX_AGE, "G4_AUTHORITY_EXPIRED")
            if r["requires_recovery"]:
                # Observe only the seam; even a mock QUALIFIED cannot qualify D03.
                try:
                    self._recovery.status(digest(r["binding"]))
                except Exception:
                    pass
                return _decision("G4_RECOVERY_FENCE_UNQUALIFIED")
            # Action is one-use across execution IDs, generations and incarnations.
            action = digest({k: r["binding"][k] for k in ("workspace_id", "project_id", "task_id", "action_id")})
            require(action not in self._seen, "G4_ACTION_REPLAY")
            require(len(self._seen) < MAX_ACTIONS, "G4_SESSION_LIMIT")
            self._seen.add(action)
            request_ref = digest(r)
            self._pending[request_ref] = (r["binding"], now)
            return {**_decision("G4_STRUCTURAL_CONTRACT_VALID", structural=True), "request_ref": request_ref}
        except G4Error as exc:
            return _decision(str(exc))
        except (G1Error, KeyError, TypeError):
            return _decision("G4_INVALID_INPUT")

    def record_result(self, request_ref: str, value: Any, *, now: int) -> dict:
        with self._lock:
            return self._record_result(request_ref, value, now=now)

    def _record_result(self, request_ref: str, value: Any, *, now: int) -> dict:
        try:
            sha(request_ref)
            integer(now)
            require(request_ref in self._pending, "G4_REQUEST_NOT_CURRENT")
            expected, admitted_at = self._pending[request_ref]
            projected = result(value, expected, now=now)
            # Authority freshness gates starting new work, not retaining late
            # outcomes of an already-started attempt. No renewal is issued.
            require(value["observed_at"] >= admitted_at, "G4_EVIDENCE_STALE")
            del self._pending[request_ref]
            return {**projected, "request_ref": request_ref}
        except G1Error:
            raise G4Error("G4_INVALID_INPUT") from None

    def restart_snapshot(self) -> bytes:
        """Evidence only: pending state is not serializable into a new session."""
        with self._lock:
            return canonical({"schema_version": "nexus.g4.restart-evidence.v1", "basis": BASIS,
                              "pending_request_refs": sorted(self._pending),
                              "recovery_fence_status": "UNQUALIFIED", "resume": "DENY",
                              "dispatch_authority": "none"})
