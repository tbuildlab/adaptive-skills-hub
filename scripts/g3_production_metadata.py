"""Isolated D05 structural preparation. Every result is UNTRUSTED metadata.

No authority state, issuance, positive decision, token handling, I/O or dispatch.
Protected semantic joins and source qualification are deliberately NOT performed.
No public admission consumer imports this module. See the readiness plan.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
import unicodedata
from typing import Any

from ash import g3_authorization as legacy
from ash import g3_host_approval_bridge as bridge

PREFIX = "nexus.g3.production."
KINDS = ("authority-challenge", "presentation-view", "owner-decision",
         "trusted-decision-receipt", "admission-intent", "dispatch-attempt",
         "recovery-checkpoint")
DOMAINS = frozenset(PREFIX + kind + ".v1" for kind in KINDS)
INLINE_DOMAINS = frozenset(PREFIX + kind + ".v1" for kind in
                         ("proposal-material", "presentation-material", "dispatch-material", "ledger-commit"))
MAX_BYTES = 65536
MAX_INT = 2**63 - 1
GATE_KINDS = ("D01_IDENTITY_CONTEXT", "D03_RECOVERY_FRESHNESS", "D04_EXECUTOR_EXCLUSION",
              "TECHNICAL", "TASK", "HOST", "G1", "G2")
FAILURE_CODES = frozenset(("INVALID_INPUT", "VERSION_REJECTED", "ORIGIN_UNVERIFIED",
    "BINDING_STALE", "CONTEXT_STALE", "EXPIRED", "MATERIAL_MISMATCH", "NONCE_CONSUMED",
    "OWNER_DENIED", "GRANT_UNTRUSTED", "GRANT_REVOKED", "GATE_FAILED", "GATE_UNKNOWN",
    "STATE_STALE", "FENCE_UNCERTAIN", "RECOVERY_MISMATCH", "ALREADY_CLAIMED",
    "OUTCOME_UNKNOWN", "FAILED", "RETIRED"))
_TOKEN = re.compile(r"[a-z0-9][a-z0-9._:-]{0,95}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_BIDI = frozenset(chr(c) for c in (0x061c, 0x200e, 0x200f, *range(0x202a, 0x202f), *range(0x2066, 0x206a)))


class MetadataError(ValueError):
    """Fixed diagnostic; caller values never appear."""


def _require(condition: bool) -> None:
    if not condition:
        raise MetadataError("G3_PRODUCTION_METADATA_INVALID")


def _text(value: Any, limit: int = 512) -> None:
    _require(type(value) is str and 0 < len(value) <= limit)
    _require(unicodedata.normalize("NFC", value) == value)
    _require(not any(ord(c) < 32 or ord(c) == 127 or c in _BIDI for c in value))
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        raise MetadataError("G3_PRODUCTION_METADATA_INVALID") from None


def _integer(value: Any, minimum: int = 0) -> None:
    _require(type(value) is int and minimum <= value <= MAX_INT)


def _token(value: Any) -> None:
    _require(type(value) is str and _TOKEN.fullmatch(value) is not None)


def _sha(value: Any) -> None:
    _require(type(value) is str and _HEX.fullmatch(value) is not None)


def _closed(value: Any, fields: str, optional: str = "") -> None:
    required, allowed = set(fields.split()), set(optional.split())
    _require(type(value) is dict and required <= set(value) <= required | allowed)


def canonical_bytes(value: Any) -> bytes:
    """D05 graph/canonical byte rules only; never source authentication."""
    seen: set[int] = set()
    nodes = 0

    def walk(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        _require(nodes <= 16000 and depth <= 12)
        if item is None:
            return
        if type(item) is int:
            _integer(item)
        elif type(item) is str:
            # Field validators enforce ordinary/explicit exception limits.
            if item:
                _text(item, 16384)
        elif type(item) in (dict, list):
            _require(len(item) <= 64 and id(item) not in seen)
            seen.add(id(item))
            if type(item) is dict:
                for key, child in item.items():
                    _text(key)
                    walk(key, depth + 1)
                    walk(child, depth + 1)
            else:
                for child in item:
                    walk(child, depth + 1)
            seen.remove(id(item))
        else:
            _require(False)

    walk(value, 0)
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    _require(len(raw) <= MAX_BYTES)
    return raw


def parse_json(raw: bytes) -> Any:
    """Strict bytes input; duplicate keys/BOM/nonconcrete JSON types denied."""
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and not raw.startswith(b"\xef\xbb\xbf"))

    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result)
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs)
        canonical_bytes(value)
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise MetadataError("G3_PRODUCTION_METADATA_INVALID") from None


def domain_digest(domain: str, value: Any) -> str:
    _require(type(domain) is str and domain in DOMAINS | INLINE_DOMAINS)
    return hashlib.sha256(domain.encode("utf-8") + b"\0" + canonical_bytes(value)).hexdigest()


def record_id(body: Any) -> str:
    _require(type(body) is dict and type(body.get("schema_version")) is str and body["schema_version"] in DOMAINS)
    domain = body["schema_version"]
    # Integrity identifier only, not a schema/provenance validation function.
    return domain + ":" + domain_digest(domain, body)


def _typed(value: Any, kind: str, *, old: bool = False) -> None:
    prefix = ("nexus.g3." if old else PREFIX) + kind + ".v1:"
    _require(type(value) is str and len(value) <= 128 and value.startswith(prefix))
    _sha(value[len(prefix):])


def _ref(value: Any, kind: str, *, old: bool = False) -> None:
    _closed(value, "id body_sha256")
    _typed(value["id"], kind, old=old)
    _sha(value["body_sha256"])


def _evidence(value: Any) -> None:
    _closed(value, "ref sha256")
    _token(value["ref"])
    _sha(value["sha256"])


def _evidence_list(value: Any, minimum: int = 1) -> None:
    _require(type(value) is list and minimum <= len(value) <= 8)
    for item in value:
        _evidence(item)
    refs = [item["ref"] for item in value]
    _require(refs == sorted(set(refs)))


def _principal(value: Any) -> None:
    _closed(value, "issuer client_id subject")
    for item in value.values():
        _text(item)


def _binding(value: Any) -> None:
    _closed(value, "owner owner_generation workspace_id project_id binding_id binding_generation")
    _principal(value["owner"])
    for key in ("owner_generation", "binding_generation"):
        _integer(value[key], 1)
    for key in ("workspace_id", "project_id", "binding_id"):
        _token(value[key])


def _stamp(value: Any) -> None:
    _closed(value, "authority_instance authority_epoch incarnation base_recovery_sequence base_checkpoint")
    _token(value["authority_instance"])
    _token(value["incarnation"])
    _integer(value["authority_epoch"], 1)
    _integer(value["base_recovery_sequence"])
    _ref(value["base_checkpoint"], "recovery-checkpoint")


def _context(value: Any) -> None:
    _closed(value, "context_id context_generation authenticated_at_ms context_expires_at_ms identity_evidence session_evidence")
    _token(value["context_id"])
    _integer(value["context_generation"], 1)
    start, end = value["authenticated_at_ms"], value["context_expires_at_ms"]
    _integer(start)
    _integer(end)
    _require(start < end <= start + 300000)
    _evidence(value["identity_evidence"])
    _evidence(value["session_evidence"])


def _json_evidence(value: Any) -> None:
    _closed(value, "contract_ref contract_sha256 canonical_utf8 content_sha256 source_evidence")
    _token(value["contract_ref"])
    _sha(value["contract_sha256"])
    _sha(value["content_sha256"])
    text = value["canonical_utf8"]
    _text(text, 16384)
    raw = text.encode("utf-8")
    _require(len(raw) <= 16384 and canonical_bytes(parse_json(raw)) == raw)
    _require(hashlib.sha256(raw).hexdigest() == value["content_sha256"])
    _evidence(value["source_evidence"])
    # No executor-selected contract resolver; semantic payload validation absent.


def _material(value: Any) -> None:
    _closed(value, "subject subject_id scope scope_sha256 requested_action operations targets effect_summary effect_explanation dispatch_payload dispatch_material_sha256 source_evidence")
    _require(type(value["subject"]) is dict and "display_title" not in value["subject"])
    try:
        requested = legacy.subject(value["subject"])
        scope = legacy._scope(value["scope"])
    except legacy.G3Error:
        raise MetadataError("G3_PRODUCTION_METADATA_INVALID") from None
    _require(requested.subject_id == value["subject_id"] and "task_id" in scope)
    _require(scope == value["scope"] and value["requested_action"] == value["subject"]["action"])
    _require(value["operations"] == scope["operations"])
    _require(hashlib.sha256(canonical_bytes(scope)).hexdigest() == value["scope_sha256"])
    _json_evidence(value["targets"])
    _json_evidence(value["dispatch_payload"])
    _closed(value["effect_summary"], "operations targets_sha256")
    _require(value["effect_summary"] == {"operations": value["operations"], "targets_sha256": value["targets"]["content_sha256"]})
    _text(value["effect_explanation"], 4096)
    _require(len(value["effect_explanation"].encode("utf-8")) <= 4096)
    _require(value["dispatch_material_sha256"] == domain_digest(PREFIX + "dispatch-material.v1", value["dispatch_payload"]))
    _evidence_list(value["source_evidence"])


def _facts(value: Any, *, all_pass: bool = False) -> None:
    _require(type(value) is list and len(value) == 8)
    for kind, fact in zip(GATE_KINDS, value):
        _closed(fact, "kind verdict observed_at_ms valid_until_ms source_evidence")
        _require(fact["kind"] == kind and fact["verdict"] in ("PASS", "FAIL", "UNKNOWN"))
        _require(not all_pass or fact["verdict"] == "PASS")
        _integer(fact["observed_at_ms"])
        _integer(fact["valid_until_ms"])
        _require(fact["observed_at_ms"] < fact["valid_until_ms"])
        _evidence(fact["source_evidence"])


def _revocation_read(value: Any) -> None:
    _closed(value, "grant index_generation read_at_ms revocations")
    _ref(value["grant"], "grant", old=True)
    _integer(value["index_generation"], 1)
    _integer(value["read_at_ms"])
    rows = value["revocations"]
    _require(type(rows) is list and len(rows) <= 64)
    for row in rows:
        _ref(row, "revocation", old=True)
    ids = [row["id"] for row in rows]
    _require(ids == sorted(set(ids)))


_FIELDS = {
 "authority-challenge": "schema_version stamp binding material proposal_id nonce issued_at_ms expires_at_ms",
 "presentation-view": "schema_version stamp challenge owner_context view_key template_revision render_evidence presentation_sha256 issued_at_ms expires_at_ms",
 "owner-decision": "schema_version stamp challenge view binding owner_context proposal_id nonce presentation_sha256 decision observed_at_ms origin_evidence",
 "trusted-decision-receipt": "schema_version stamp challenge view owner_decision binding owner_context proposal_id nonce presentation_sha256 decision accepted_at_ms confirmation_expires_at_ms legacy_time_basis provenance_evidence",
 "admission-intent": "schema_version stamp receipt challenge binding owner_context proposal_id subject_id scope_sha256 dispatch_material_sha256 grant revocation_read gate_facts disposition reason_codes evaluated_at_ms use_until_ms executor_environment intent_key",
 "dispatch-attempt": "schema_version stamp phase attempt_key intent grant dispatch_material_sha256",
 "recovery-checkpoint": "schema_version authority_instance authority_epoch incarnation recovery_sequence previous_checkpoint transition_kind record_refs ledger_commit_sha256 time_high_water_ms",
}


def _envelope(body: Any) -> None:
    _require(type(body) is dict and type(body.get("schema_version")) is str and body["schema_version"] in DOMAINS)
    kind = body["schema_version"][len(PREFIX):-3]
    fields = _FIELDS[kind]
    if kind == "dispatch-attempt":
        _require(body.get("phase") in ("CLAIM", "RESULT"))
        fields += (" claimed_at_ms handoff_until_ms gate_facts revocation_read executor_environment" if body["phase"] == "CLAIM"
                   else " claim observed_at_ms outcome outcome_evidence")
    _closed(body, fields, "host_proposal" if kind == "authority-challenge" else "")
    for key, value in body.items():
        if key.endswith("_ms"):
            _integer(value)
        elif key.endswith("_sha256") or key in ("nonce", "template_revision"):
            _sha(value)
    if "stamp" in body:
        _stamp(body["stamp"])
    if "binding" in body:
        _binding(body["binding"])
    if "owner_context" in body:
        _context(body["owner_context"])
    for key, refkind in (("challenge", "authority-challenge"), ("view", "presentation-view"),
                         ("owner_decision", "owner-decision"), ("receipt", "trusted-decision-receipt"),
                         ("intent", "admission-intent"), ("claim", "dispatch-attempt")):
        if key in body:
            _ref(body[key], refkind)
    if "proposal_id" in body:
        _typed(body["proposal_id"], "proposal-material")
    if "subject_id" in body:
        _typed(body["subject_id"], "subject", old=True)
    if "decision" in body:
        _require(body["decision"] in ("CONFIRM", "DENY"))
    for key in ("view_key", "intent_key", "attempt_key", "executor_environment"):
        if key in body:
            _token(body[key])
    for key in ("render_evidence", "origin_evidence"):
        if key in body:
            _evidence(body[key])
    if kind == "authority-challenge":
        _require(body["issued_at_ms"] < body["expires_at_ms"] <= body["issued_at_ms"] + 300000)
        _material(body["material"])
        _require(body["proposal_id"] == PREFIX + "proposal-material.v1:" + domain_digest(PREFIX + "proposal-material.v1", body["material"]))
        if "host_proposal" in body:
            _closed(body["host_proposal"], "body proposal_id")
            _typed(body["host_proposal"]["proposal_id"], "host-approval-proposal", old=True)
            host = body["host_proposal"]["body"]
            checked = bridge._proposal_body(host)
            _require(checked == host)
            host_bytes = legacy._canonical(host)
            _require(body["host_proposal"]["proposal_id"] == legacy._id("host-approval-proposal", host_bytes))
            for key in ("subject_id", "scope", "scope_sha256", "requested_action", "effect_summary"):
                _require(host[key] == body["material"][key])
    elif kind == "presentation-view":
        _require(body["owner_context"]["authenticated_at_ms"] <= body["issued_at_ms"])
        _require(body["issued_at_ms"] < body["expires_at_ms"] <= body["owner_context"]["context_expires_at_ms"])
    elif kind == "owner-decision":
        _require(body["owner_context"]["authenticated_at_ms"] <= body["observed_at_ms"] < body["owner_context"]["context_expires_at_ms"])
    elif kind == "trusted-decision-receipt":
        _require(body["legacy_time_basis"] == "UNIX_MS")
        _require(body["owner_context"]["authenticated_at_ms"] <= body["accepted_at_ms"])
        _require(body["accepted_at_ms"] < body["confirmation_expires_at_ms"] <= min(body["accepted_at_ms"] + 600000, body["owner_context"]["context_expires_at_ms"]))
        _evidence_list(body["provenance_evidence"])
    elif kind == "admission-intent":
        _require(body["disposition"] in ("DENIED", "ADMIT_PENDING"))
        positive_shape = body["disposition"] == "ADMIT_PENDING"
        _facts(body["gate_facts"], all_pass=positive_shape)
        _require((body["grant"] is None) == (body["revocation_read"] is None))
        if body["grant"] is not None:
            _ref(body["grant"], "grant", old=True)
            _revocation_read(body["revocation_read"])
            _require(body["grant"] == body["revocation_read"]["grant"])
        reasons = body["reason_codes"]
        _require(type(reasons) is list and 1 <= len(reasons) <= 8)
        _require(all(type(code) is str for code in reasons) and reasons == sorted(set(reasons)))
        if positive_shape:
            _require(body["grant"] is not None and reasons == ["INTENT_PENDING"])
            _require(body["owner_context"]["authenticated_at_ms"] <= body["evaluated_at_ms"])
            _require(all(fact["observed_at_ms"] <= body["evaluated_at_ms"] for fact in body["gate_facts"]))
            _require(body["evaluated_at_ms"] < body["use_until_ms"] <= min(body["evaluated_at_ms"] + 60000, body["owner_context"]["context_expires_at_ms"], *(fact["valid_until_ms"] for fact in body["gate_facts"])))
        else:
            _require(set(reasons) <= FAILURE_CODES and body["use_until_ms"] == body["evaluated_at_ms"])
    elif kind == "dispatch-attempt":
        _ref(body["grant"], "grant", old=True)
        if body["phase"] == "CLAIM":
            _facts(body["gate_facts"], all_pass=True)
            _revocation_read(body["revocation_read"])
            _require(body["grant"] == body["revocation_read"]["grant"])
            _require(all(fact["observed_at_ms"] <= body["claimed_at_ms"] for fact in body["gate_facts"]))
            _require(body["claimed_at_ms"] < body["handoff_until_ms"] <= min(fact["valid_until_ms"] for fact in body["gate_facts"]))
        else:
            _require(body["outcome"] in ("COMPLETED", "FAILED", "UNKNOWN"))
            _evidence_list(body["outcome_evidence"], 0 if body["outcome"] == "UNKNOWN" else 1)
    elif kind == "recovery-checkpoint":
        for key in ("authority_instance", "incarnation"):
            _token(body[key])
        _integer(body["authority_epoch"], 1)
        _integer(body["recovery_sequence"])
        _require(body["transition_kind"] in ("GENESIS", "CHALLENGE", "CONFIRM", "DENY", "EVALUATE", "CLAIM", "RESULT", "INVALIDATE", "REVOKE", "RECOVER"))
        genesis = body["transition_kind"] == "GENESIS"
        _require((body["previous_checkpoint"] is None) == genesis)
        _require((body["recovery_sequence"] == 0) == genesis)
        if not genesis:
            _ref(body["previous_checkpoint"], "recovery-checkpoint")
        refs = body["record_refs"]
        _require(type(refs) is list and len(refs) <= 64)
        for ref in refs:
            _closed(ref, "id body_sha256")
            _sha(ref["body_sha256"])
            _require(type(ref["id"]) is str and len(ref["id"]) <= 128)
            domain, sep, sha = ref["id"].rpartition(":")
            _require(sep == ":" and domain in DOMAINS | {legacy.GRANT_SCHEMA, legacy.REVOCATION_SCHEMA})
            _sha(sha)
        ids = [ref["id"] for ref in refs]
        _require(ids == sorted(set(ids)))


@dataclass(frozen=True, slots=True)
class UntrustedMetadata:
    canonical_body: bytes
    record_id: str
    body_sha256: str

    @property
    def basis(self) -> str:
        return "OFFLINE_UNTRUSTED_METADATA"

    @property
    def authority(self) -> str:
        return "NONE"

    @property
    def semantic_validation(self) -> str:
        return "NOT_PERFORMED"

    def to_dict(self) -> dict:
        return parse_json(self.canonical_body)


def parse_metadata(raw: bytes) -> UntrustedMetadata:
    """Check closed structural metadata only, never trusted receipt acceptance.

    Unresolved: full retained-record joins, actual native Host request provenance,
    payload contract semantics, protected membership/provenance, current time,
    issuer/session/render/nonce/revocation completeness and recovery/exclusion.
    """
    try:
        body = parse_json(raw)
        _envelope(body)
        encoded = canonical_bytes(body)
        return UntrustedMetadata(encoded, record_id(body), hashlib.sha256(encoded).hexdigest())
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError, UnicodeError):
        raise MetadataError("G3_PRODUCTION_METADATA_INVALID") from None
