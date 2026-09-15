"""G1 closed data contracts and process-local observation provenance.

Profiles are untrusted data. Observations are separately assembled by reviewed
Host/test adapters, never deserialized into trust from profile or MCP input.
This is evidence integrity within a trusted Python process, not attestation or
an approval service. Nothing in this module grants execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
import weakref
from typing import Any

from .capabilities import MAX_CONSIDERED_CAPABILITIES, PERMISSIONS, EXECUTION_MECHANISMS
from .ecosystem_models import (
    EcosystemError, canonical_json_bytes, parse_json_bytes,
)
from .evaluation import SECRET_IDENTIFIER_RE

MODEL_SCHEMA = "nexus.model-capability-profile.v1"
HOST_SCHEMA = "nexus.host-capability-profile.v1"
CONFORMANCE_SCHEMA = "nexus.executor-conformance-record.v1"
CANDIDATE_SCHEMA = "nexus.executor-candidate.v1"
OBSERVATION_SCHEMA = "nexus.executor-observation.v1"
MAX_BYTES = 512 * 1024
MAX_DEPTH = 12
MAX_NODES = 16000
MAX_ITEMS = 64
MAX_STRING = 512
MAX_AGE = 86400
TOKEN = re.compile(r"[a-z0-9][a-z0-9._:-]{0,95}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
STATES = (
    "documented_possible", "visible_now", "permitted_now",
    "trusted_for_this_use", "binding_verified_now",
    "prerequisites_ready_now", "executable_now",
)
FACILITIES = (
    "filesystem", "shell", "network", "browser", "computer_use", "artifacts",
    "skills", "plugins", "mcp", "subagents", "checkpoint_resume",
    "long_running", "authentication_owned", "cancellation", "usage_visibility",
    "budget_visibility",
)
COST_PARTS = ("execution", "retries", "validation", "context", "tools", "human_recovery")
CLASSES = {"ADVISORY": 0, "GOVERNED_HANDOFF": 1, "ENFORCED_INTEGRATION": 2}
LAYERS = {
    "ADVISORY": {"instructions"},
    "GOVERNED_HANDOFF": {"host_handoff"},
    "ENFORCED_INTEGRATION": {"nexus_boundary", "host_boundary", "os_boundary", "provider_boundary"},
}


class G1Error(ValueError):
    """Closed G1 input/provenance failure; messages contain no input content."""


def fail(code: str = "G1_INVALID_INPUT") -> None:
    raise G1Error(code)


def bounded(value: Any) -> Any:
    """Bound the graph before canonical serialization, including cycles/subclasses."""
    stack = [(value, 0)]
    count = 0
    while stack:
        item, depth = stack.pop()
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            fail("G1_RESOURCE_LIMIT")
        if type(item) is dict:
            if len(item) > MAX_ITEMS or any(type(k) is not str for k in item):
                fail()
            stack.extend((k, depth + 1) for k in item)
            stack.extend((v, depth + 1) for v in item.values())
        elif type(item) is list:
            if len(item) > MAX_ITEMS:
                fail("G1_RESOURCE_LIMIT")
            stack.extend((v, depth + 1) for v in item)
        elif type(item) is str:
            if len(item) > MAX_STRING or any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or
                    c in "\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069" for c in item):
                fail()
        elif type(item) is int:
            if not 0 <= item <= 9_223_372_036_854_775_807:
                fail()
        elif item is not None and type(item) is not bool:
            fail()
    try:
        canonical_json_bytes(value, maximum_bytes=MAX_BYTES)
    except (EcosystemError, UnicodeError, RecursionError):
        fail()
    return value


def parse_input(raw: bytes) -> Any:
    try:
        return bounded(parse_json_bytes(raw, maximum_bytes=MAX_BYTES, label="G1 input"))
    except EcosystemError:
        fail()


def digest(value: Any) -> str:
    bounded(value)
    return hashlib.sha256(canonical_json_bytes(value, maximum_bytes=MAX_BYTES)).hexdigest()


def exact(value: Any, fields: set[str]) -> dict:
    if type(value) is not dict or set(value) != fields:
        fail()
    return value


def token(value: Any) -> str:
    if type(value) is not str or not TOKEN.fullmatch(value) or SECRET_IDENTIFIER_RE.fullmatch(value):
        fail()
    return value


def sha(value: Any) -> str:
    if type(value) is not str or not DIGEST.fullmatch(value):
        fail()
    return value


def tri(value: Any) -> None:
    if value is not None and type(value) is not bool:
        fail()


def integer(value: Any, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if type(value) is not int or not 0 <= value <= 9_223_372_036_854_775_807:
        fail()


def enum(value: Any, choices) -> None:
    if type(value) is not str or value not in choices:
        fail()


def tokens(values: Any, *, nonempty: bool = False) -> list[str]:
    if type(values) is not list or len(values) > MAX_ITEMS or (nonempty and not values):
        fail()
    result = [token(v) for v in values]
    if len(set(result)) != len(result):
        fail("G1_AMBIGUOUS_IDENTITY")
    return sorted(result)


def notes(value: Any) -> None:
    if type(value) is not list or len(value) > 16 or any(type(v) is not str for v in value):
        fail()


def window(value: dict) -> None:
    integer(value["observed_at"])
    integer(value["expires_at"])
    if not 0 < value["expires_at"] - value["observed_at"] <= MAX_AGE:
        fail()
    token(value["scope_id"])


def fresh(value: dict, now: int, scope_id: str) -> bool:
    return value["scope_id"] == scope_id and value["observed_at"] <= now < value["expires_at"]


def cost(value: Any) -> dict:
    exact(value, {"basis", "currency", "components", "evidence_refs"})
    enum(value["basis"], {"known", "estimated", "unknown"})
    if value["currency"] is not None:
        token(value["currency"])
    exact(value["components"], set(COST_PARTS))
    for v in value["components"].values():
        integer(v, nullable=True)
    tokens(value["evidence_refs"])
    if value["basis"] != "unknown" and (value["currency"] is None or
            any(v is None for v in value["components"].values()) or not value["evidence_refs"]):
        fail()
    if value["basis"] != "unknown":
        integer(sum(value["components"].values()))
    return value


COMMON = {"schema_version", "profile_id", "revision", "configuration_id", "adapter_sha256",
          "observed_at", "expires_at", "scope_id", "evidence_refs", "limitations", "uncertainty"}


def _profile(value: Any, fields: set[str], schema: str) -> dict:
    bounded(value)
    exact(value, COMMON | fields)
    if value["schema_version"] != schema:
        fail()
    for key in ("profile_id", "revision", "configuration_id"):
        token(value[key])
    sha(value["adapter_sha256"])
    window(value)
    tokens(value["evidence_refs"])
    notes(value["limitations"])
    notes(value["uncertainty"])
    return value


def model_profile(value: Any) -> dict:
    _profile(value, {"provider", "model_family", "model_id", "deployment_id", "deployment_kind",
                    "capabilities", "limits", "tool_use", "structured_output", "delegation",
                    "latency", "cost", "privacy"}, MODEL_SCHEMA)
    for key in ("provider", "model_family", "model_id", "deployment_id"):
        token(value[key])
    enum(value["deployment_kind"], {"local", "remote", "hybrid", "unknown"})
    exact(value["capabilities"], {"claimed", "measured", "host_reported", "runtime_observed"})
    for entries in value["capabilities"].values():
        if type(entries) is not list or len(entries) > 16:
            fail()
        seen = set()
        for entry in entries:
            exact(entry, {"capability_id", "task_classes", "evidence_refs"})
            identity = token(entry["capability_id"])
            if identity in seen:
                fail("G1_AMBIGUOUS_IDENTITY")
            seen.add(identity)
            tokens(entry["task_classes"], nonempty=True)
            tokens(entry["evidence_refs"])
    exact(value["limits"], {"context_tokens", "input_tokens", "output_tokens"})
    for v in value["limits"].values():
        integer(v, nullable=True)
    for key in ("tool_use", "structured_output", "delegation"):
        tri(value[key])
    latency = exact(value["latency"], {"basis", "p50_ms", "p95_ms", "evidence_refs"})
    enum(latency["basis"], {"known", "estimated", "unknown"})
    integer(latency["p50_ms"], nullable=True)
    integer(latency["p95_ms"], nullable=True)
    tokens(latency["evidence_refs"])
    cost(value["cost"])
    privacy = exact(value["privacy"], {"residency", "retention", "data_use", "evidence_refs"})
    tokens(privacy["residency"])
    token(privacy["retention"])
    token(privacy["data_use"])
    tokens(privacy["evidence_refs"])
    return value


def host_profile(value: Any) -> dict:
    _profile(value, {"host_id", "surface_id", "binding_id", "inventory_scope",
                    "inventory_completeness", "states", "facilities", "lifecycle",
                    "enforcement_mechanisms"}, HOST_SCHEMA)
    for key in ("host_id", "surface_id"):
        token(value[key])
    if value["binding_id"] is not None:
        token(value["binding_id"])
    enum(value["inventory_scope"], {"current_turn_host_visible_subset", "authorized_probe_visible_subset"})
    if value["inventory_completeness"] != "not_globally_enumerated":
        fail()
    exact(value["states"], set(STATES))
    exact(value["facilities"], set(FACILITIES))
    exact(value["lifecycle"], {"installed", "enabled", "loaded", "approved", "routable"})
    for field in ("states", "facilities", "lifecycle"):
        for v in value[field].values():
            tri(v)
    tokens(value["enforcement_mechanisms"])
    return value


def candidate(value: Any) -> dict:
    bounded(value)
    exact(value, {"schema_version", "candidate_id", "model", "host", "path", "cost", "required_permissions", "execution_mechanism"})
    if value["schema_version"] != CANDIDATE_SCHEMA:
        fail()
    token(value["candidate_id"])
    if not set(tokens(value["required_permissions"])) <= PERMISSIONS:
        fail()
    enum(value["execution_mechanism"], EXECUTION_MECHANISMS)
    if value["model"] is not None:
        model_profile(value["model"])
    host_profile(value["host"])
    path = exact(value["path"], {"complete", "host_native", "nodes"})
    tri(path["complete"])
    tri(path["host_native"])
    if type(path["nodes"]) is not list or not 1 <= len(path["nodes"]) <= 16:
        fail()
    ids = []
    for node in path["nodes"]:
        exact(node, {"node_id", "kind", "location", "provider", "delegated", "remote_mcp", "evidence_refs", "model_profile_sha256"})
        ids.append(token(node["node_id"]))
        enum(node["kind"], {"model", "host", "tool", "mcp", "proxy", "storage", "agent", "validation", "context"})
        enum(node["location"], {"local", "remote", "hybrid", "unknown"})
        token(node["provider"])
        tri(node["delegated"])
        tri(node["remote_mcp"])
        tokens(node["evidence_refs"])
        if node["kind"] == "model":
            model = value["model"]
            if model is None or (node["model_profile_sha256"] != digest(model) or
                    node["provider"] != model["provider"] or node["location"] != model["deployment_kind"]):
                fail("G1_MODEL_PATH_MISMATCH")
        elif node["model_profile_sha256"] is not None:
            fail("G1_MODEL_PATH_MISMATCH")
        if node["kind"] == "agent" and node["delegated"] is not True:
            fail("G1_PATH_CONTRADICTION")
        if node["kind"] in {"mcp", "proxy"} and node["location"] in {"remote", "hybrid"} and node["remote_mcp"] is False:
            fail("G1_PATH_CONTRADICTION")
    if len(ids) != len(set(ids)):
        fail("G1_AMBIGUOUS_IDENTITY")
    if sum(n["kind"] == "model" for n in path["nodes"]) != (1 if value["model"] is not None else 0):
        fail("G1_MODEL_PATH_MISMATCH")
    cost(value["cost"])
    return value


def binding_digest(value: dict) -> str:
    candidate(value)
    return digest({"schema_version": "nexus.executor-binding.v1", "model": value["model"],
                   "host": value["host"], "path": value["path"]})


def conformance(value: Any) -> dict:
    bounded(value)
    exact(value, {"schema_version", "record_id", "subject_sha256", "binding_sha256", "control_id",
                  "operations", "enforcing_layer", "classification", "probe_result", "evidence_refs",
                  "scope_id", "observed_at", "expires_at", "limitations"})
    if value["schema_version"] != CONFORMANCE_SCHEMA:
        fail()
    for key in ("record_id", "control_id"):
        token(value[key])
    for key in ("subject_sha256", "binding_sha256"):
        sha(value[key])
    enum(value["classification"], CLASSES)
    enum(value["enforcing_layer"], LAYERS[value["classification"]])
    enum(value["probe_result"], {"pass", "fail", "unknown", "not_run"})
    tokens(value["operations"], nonempty=True)
    tokens(value["evidence_refs"])
    notes(value["limitations"])
    window(value)
    return value


@dataclass(frozen=True, eq=False)
class TrustedObservations:
    """A non-serializable in-process evidence handle, never an execution token."""
    _payload: bytes


_OBSERVATIONS: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def _issue_observations(rows: list[dict], *, source: str) -> TrustedObservations:
    """Internal reviewed-adapter/test seam, NOT an admission API for caller JSON.

    Calling private Python functions or replacing trusted loaded code is outside
    the untrusted-data boundary, as with the existing validator registry seal.
    The only shipped real producer is the separately authorized pilot script.
    """
    token(source)
    bounded(rows)
    if type(rows) is not list or not rows or len(rows) > MAX_CONSIDERED_CAPABILITIES:
        fail()
    subjects = []
    for row in rows:
        exact(row, {"schema_version", "subject_sha256", "binding_sha256", "requirements_sha256", "policy_sha256",
                    "scope_id", "observed_at", "expires_at", "states", "task_classes", "capabilities",
                    "acceptance", "budget_eligible", "path_verified", "conformance_sha256", "evidence_refs"})
        if row["schema_version"] != OBSERVATION_SCHEMA:
            fail()
        for key in ("subject_sha256", "binding_sha256", "requirements_sha256", "policy_sha256"):
            sha(row[key])
        subjects.append(row["subject_sha256"])
        window(row)
        exact(row["states"], set(STATES))
        for v in row["states"].values():
            tri(v)
        for key in ("budget_eligible", "path_verified"):
            tri(row[key])
        for key in ("task_classes", "capabilities", "acceptance", "evidence_refs"):
            tokens(row[key])
        if type(row["conformance_sha256"]) is not list:
            fail()
        for item in row["conformance_sha256"]:
            sha(item)
        if len(set(row["conformance_sha256"])) != len(row["conformance_sha256"]):
            fail()
    if len(subjects) != len(set(subjects)):
        fail("G1_AMBIGUOUS_IDENTITY")
    raw = canonical_json_bytes({"source": source, "rows": rows}, maximum_bytes=MAX_BYTES)
    handle = TrustedObservations(raw)
    _OBSERVATIONS[handle] = raw
    return handle


def observations(handle: Any) -> dict:
    if type(handle) is not TrustedObservations:
        fail("G1_OBSERVATION_PROVENANCE_INVALID")
    baseline = _OBSERVATIONS.get(handle)
    if baseline is None or type(handle._payload) is not bytes or handle._payload != baseline:
        fail("G1_OBSERVATION_PROVENANCE_INVALID")
    return parse_input(baseline)
