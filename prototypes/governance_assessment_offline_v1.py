"""Offline review candidate only. No evidence access, policy evaluation or grants.

This module is not registered with Nexus and has no CLI or production caller.
Textual claims remain inert. CONSISTENT concerns structure, not acceptance.
"""
from __future__ import annotations

import hashlib
import json
import math

MAX_BYTES = 1_048_576
MAX_ITEMS = 512
MAX_ID = 512
_APPLICABILITY = frozenset({"REQUIRED", "OPTIONAL", "NOT_APPLICABLE", "DEFERRED"})
_OUTCOMES = frozenset({"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"})
_BASES = frozenset({"PROVIDED", "OBSERVED", "DERIVED", "ASSUMED", "UNKNOWN"})
_DIMENSIONS = frozenset({"INSTALLED", "CALLABLE", "EXECUTED", "APPLIED"})
_CONCERNS = frozenset({"observation", "reproduction", "cause", "disposition", "remediation", "validation"})


class _Invalid(Exception):
    def __init__(self, code: str, location: str):
        self.code = code
        self.location = location


def _fail(code: str, location: str) -> None:
    raise _Invalid(code, location)


def _object(value: object, required: set[str], optional: set[str], location: str) -> dict:
    if type(value) is not dict:
        _fail("OBJECT_REQUIRED", location)
    if not required <= value.keys():
        _fail("REQUIRED_MEMBER_MISSING", location)
    if not value.keys() <= required | optional:
        _fail("UNKNOWN_MEMBER", location)
    return value


def _text(value: object, location: str, *, identity: bool = False) -> str:
    if type(value) is not str or not value.strip():
        _fail("NONEMPTY_TEXT_REQUIRED", location)
    if identity and (len(value) > MAX_ID or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        _fail("IDENTITY_ENVELOPE", location)
    return value


def _list(value: object, location: str) -> list:
    if type(value) is not list or len(value) > MAX_ITEMS:
        _fail("LIST_ENVELOPE", location)
    return value


def _enum(value: object, allowed: frozenset, location: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if type(value) is not str or value not in allowed:
        _fail("UNSUPPORTED_VALUE", location)


def _index(items: list, location: str) -> dict[str, dict]:
    found = {}
    for position, item in enumerate(items):
        row_location = f"{location}[{position}]"
        if type(item) is not dict or "id" not in item:
            _fail("IDENTITY_REQUIRED", row_location)
        identity = _text(item["id"], row_location, identity=True)
        if identity in found:
            _fail("DUPLICATE_IDENTITY", row_location)
        found[identity] = item
    return found


def _refs(value: object, namespace: dict, location: str, *, kind: str | None = None) -> list[str]:
    items = _list(value, location)
    seen = set()
    for position, item in enumerate(items):
        where = f"{location}[{position}]"
        identity = _text(item, where, identity=True)
        if identity in seen:
            _fail("DUPLICATE_REFERENCE", where)
        seen.add(identity)
        if identity not in namespace:
            _fail("UNRESOLVED_REFERENCE", where)
        if kind is not None and namespace[identity]["kind"] != kind:
            _fail("REFERENCE_KIND_CONFLICT", where)
    return items


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("DUPLICATE_JSON_MEMBER", "json")
        result[key] = value
    return result


def _constant(value: str) -> None:
    _fail("NONFINITE_JSON_VALUE", "json")


def _inspect(record: object) -> dict:
    required = {"schema_version", "record_id", "basis", "subject", "purpose", "governance_refs", "profile", "checks", "references"}
    record = _object(record, required, {"diagnostic"}, "record")
    if record["schema_version"] != "1.0":
        _fail("UNSUPPORTED_VERSION", "schema_version")
    _text(record["record_id"], "record_id", identity=True)
    _enum(record["basis"], frozenset({"REAL", "ILLUSTRATIVE"}), "basis")
    _text(record["purpose"], "purpose")
    references = _list(record["references"], "references")
    refs = _index(references, "references")
    for position, ref in enumerate(references):
        where = f"references[{position}]"
        _object(ref, {"id", "kind", "locator", "source", "scope"}, {"selector", "revision", "captured_at", "valid_until", "integrity_sha256"}, where)
        _enum(ref["kind"], frozenset({"GOVERNANCE", "EVIDENCE"}), where)
        for key in ("locator", "source", "scope", "selector", "revision", "captured_at", "valid_until"):
            if key in ref:
                _text(ref[key], where)
        if ref["kind"] == "GOVERNANCE" and "revision" not in ref:
            _fail("GOVERNANCE_VERSION_UNBOUND", where)
        if "integrity_sha256" in ref:
            digest = ref["integrity_sha256"]
            if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
                _fail("INVALID_DIGEST_SHAPE", where)
    _refs(record["governance_refs"], refs, "governance_refs", kind="GOVERNANCE")
    subject = _object(record["subject"], {"id", "configuration_id", "criteria_refs"}, set(), "subject")
    _text(subject["id"], "subject.id", identity=True)
    _text(subject["configuration_id"], "subject.configuration_id", identity=True)
    _refs(subject["criteria_refs"], refs, "subject.criteria_refs")
    profile = _list(record["profile"], "profile")
    facts = _index(profile, "profile")
    for position, fact in enumerate(profile):
        where = f"profile[{position}]"
        _object(fact, {"id", "claim", "value", "basis", "refs"}, set(), where)
        _text(fact["claim"], where)
        _enum(fact["basis"], _BASES, where)
        value = fact["value"]
        if value is not None and type(value) not in {str, bool, int, float}:
            _fail("SCALAR_REQUIRED", where)
        if type(value) is float and not math.isfinite(value):
            _fail("NONFINITE_JSON_VALUE", where)
        if fact["basis"] == "UNKNOWN" and value is not None:
            _fail("UNKNOWN_FACT_HAS_VALUE", where)
        _refs(fact["refs"], refs, where)
        if fact["basis"] in {"OBSERVED", "DERIVED"} and not fact["refs"]:
            _fail("PROVENANCE_REFERENCE_MISSING", where)
    checks = _list(record["checks"], "checks")
    check_index = _index(checks, "checks")
    edges = {}
    for position, check in enumerate(checks):
        where = f"checks[{position}]"
        _object(check, {"id", "family", "governing_refs", "criterion", "applicability", "outcome"}, {"requires", "capability"}, where)
        _enum(check["family"], frozenset("ABCDEF"), where)
        _text(check["criterion"], where)
        _refs(check["governing_refs"], refs, where, kind="GOVERNANCE")
        app = _object(check["applicability"], {"state", "reason", "fact_refs"}, set(), where + ".applicability")
        _enum(app["state"], _APPLICABILITY, where, nullable=True)
        _text(app["reason"], where + ".applicability")
        _refs(app["fact_refs"], facts, where)
        out = _object(check["outcome"], {"state", "reason", "evidence_refs"}, set(), where + ".outcome")
        _enum(out["state"], _OUTCOMES, where, nullable=True)
        _text(out["reason"], where + ".outcome")
        _refs(out["evidence_refs"], refs, where, kind="EVIDENCE")
        if (app["state"] == "NOT_APPLICABLE") != (out["state"] == "NOT_APPLICABLE"):
            _fail("APPLICABILITY_OUTCOME_CONFLICT", where)
        if app["state"] == "NOT_APPLICABLE" and not app["fact_refs"]:
            _fail("EXCLUSION_BASIS_MISSING", where)
        if out["state"] == "PASS":
            if app["state"] not in {"REQUIRED", "OPTIONAL"}:
                _fail("PASS_APPLICABILITY_CONFLICT", where)
            if not out["evidence_refs"]:
                _fail("PASS_EVIDENCE_ASSOCIATION_MISSING", where)
        edges[check["id"]] = _refs(check.get("requires", []), check_index, where + ".requires")
        if "capability" in check:
            cap = _object(check["capability"], {"ref", "dimension"}, set(), where + ".capability")
            _refs([cap["ref"]], refs, where, kind="EVIDENCE")
            _enum(cap["dimension"], _DIMENSIONS, where)
    # Bounded acyclicity check only. No execution order or dispatch is produced.
    remaining = {identity: set(deps) for identity, deps in edges.items()}
    while remaining:
        roots = {identity for identity, deps in remaining.items() if not deps}
        if not roots:
            _fail("DEPENDENCY_CYCLE", "checks")
        remaining = {identity: deps - roots for identity, deps in remaining.items() if identity not in roots}
    for position, check in enumerate(checks):
        if check["outcome"]["state"] == "PASS":
            for dependency in edges[check["id"]]:
                premise = check_index[dependency]
                if premise["outcome"]["state"] != "PASS" or premise["applicability"]["state"] not in {"REQUIRED", "OPTIONAL"}:
                    _fail("PASS_REQUIRED_PREMISE_UNRESOLVED", f"checks[{position}]")
    if "diagnostic" in record:
        diag = _object(record["diagnostic"], set(_CONCERNS), set(), "diagnostic")
        for concern in sorted(_CONCERNS):
            note = _object(diag[concern], {"note", "refs"}, set(), "diagnostic." + concern)
            _text(note["note"], "diagnostic." + concern)
            _refs(note["refs"], refs, "diagnostic." + concern, kind="EVIDENCE")
    mandatory = {c["id"] for c in checks if c["applicability"]["state"] == "REQUIRED"}
    mandatory.update(dep for deps in edges.values() for dep in deps)
    unresolved = [i for i, c in enumerate(checks) if c["id"] in mandatory and c["outcome"]["state"] in {None, "UNKNOWN"}]
    return {
        "handling": "PRESERVE_UNKNOWN" if unresolved else "REQUIRE_REVIEW",
        "structure": "CONSISTENT",
        "diagnostics": [],
        "declared_checks": [{"position": i, "applicability": c["applicability"]["state"], "outcome": c["outcome"]["state"]} for i, c in enumerate(checks)],
        "unresolved_required_checks": unresolved,
        "declared_fail_checks": [i for i, c in enumerate(checks) if c["outcome"]["state"] == "FAIL"],
        "unresolved_applicability_checks": [i for i, c in enumerate(checks) if c["applicability"]["state"] is None],
        "unknown_profile_facts": [i for i, f in enumerate(profile) if f["basis"] == "UNKNOWN"],
        "unverified_pass_claims": [i for i, c in enumerate(checks) if c["outcome"]["state"] == "PASS"],
    }


def review_bytes(data: bytes) -> dict:
    """Return a zero-authority structural report; never adjudicate evidence truth."""
    digest = None
    try:
        if type(data) is not bytes or len(data) > MAX_BYTES:
            _fail("INPUT_ENVELOPE", "input")
        digest = hashlib.sha256(data).hexdigest()
        record = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
        report = _inspect(record)
    except _Invalid as exc:
        report = {"handling": "REJECT_RECORD", "structure": "INVALID", "diagnostics": [{"code": exc.code, "location": exc.location}]}
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        report = {"handling": "REJECT_RECORD", "structure": "INVALID", "diagnostics": [{"code": "INVALID_JSON_OR_RESOURCE", "location": "json"}]}
    return {"input_sha256": digest, "authority": "none", "dispatch_requested": False, **report}
