"""Closed, bounded project-local facts. No execution, network or G4 semantics."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import PurePosixPath
import re
import unicodedata
from urllib.parse import urlsplit

MAX_PROJECTS = 128
MAX_REVISIONS = 32
MAX_REVISION_BYTES = 32 * 1024
MAX_BUNDLE_BYTES = 1152 * 1024
MAX_STORE_BYTES = 160 * 1024 * 1024
MAX_CORE_BYTES = 4096
MAX_CONTEXT_BYTES = 8192
CONFIG_NAME = "project-memory-config.json"
ROOT_MARKER = ".nexus-project-memory-root.json"
PROJECT_ID = r"^[a-f0-9]{32}$"
DIGEST = r"^[a-f0-9]{64}$"
IDENTIFIER = r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,63}$"
CONFIDENCE = ["verified", "observed", "inferred", "unverified"]


class MemoryError(ValueError):
    """Content-free error code; never echo a rejected value."""


def require(condition, code="project_memory_invalid"):
    if not condition:
        raise MemoryError(code)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def parse(raw, limit):
    require(type(raw) is bytes and len(raw) <= limit, "project_memory_size_limit")
    def closed(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result)
            result[key] = value
        return result
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=closed,
                          parse_constant=lambda _: require(False))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise MemoryError("project_memory_invalid") from exc


def string(limit=1024, pattern=None):
    result = {"type": "string", "maxLength": limit, "x-maxUtf8Bytes": limit}
    if pattern:
        result["pattern"] = pattern
    return result


def enum(values):
    return {"type": "string", "enum": values}


def array(item, maximum):
    return {"type": "array", "items": item, "maxItems": maximum}


def obj(**properties):
    return {"type": "object", "additionalProperties": False,
            "required": list(properties), "properties": properties}


def ref(name):
    return {"$ref": "#/$defs/" + name}


ID = string(64, IDENTIFIER)
SHA = string(64, DIGEST)
IDS = array(ID, 8)
BOOL = {"type": "boolean"}
NULL = {"type": "null"}
TIME = {"anyOf": [string(40), NULL]}
FACT = obj(id=ID, text=string(512), confidence=enum(CONFIDENCE), evidence_refs=IDS)
DECISION = obj(id=ID, kind=enum(["design", "architecture", "frozen"]), text=string(512),
               user_approved=BOOL, confidence=enum(CONFIDENCE), evidence_refs=IDS)
CHECK = obj(kind=enum(["build", "test", "lint", "visual", "other"]),
            status=enum(["passed", "failed", "not_applicable"]), confidence=enum(CONFIDENCE), evidence_refs=IDS)
CAPABILITY = obj(id=ID, name=string(128), version=string(128), source=string(512),
                 role=string(256), scope=string(256), selected=BOOL, used=BOOL,
                 result=enum(["effective", "partial", "ineffective", "fallback"]),
                 limitation=string(512), evidence_refs=IDS)
LESSON = obj(id=ID, kind=enum(["successful_pattern", "failed_attempt", "rejected_approach", "recovery"]),
             tags=array(string(64), 8), summary=string(512), confidence=enum(CONFIDENCE), evidence_refs=IDS,
             symptom=string(512), root_cause_status=enum(["known", "unknown", "not_applicable"]),
             root_cause=string(512), correction=string(512),
             validation_result=enum(["passed", "failed", "not_run"]), prevention=string(512))
STATE_FIELDS = ("requirements", "constraints", "exclusions", "completed_scope", "limitations", "technical_debt",
                "risks", "unfinished_work", "next_steps", "continuation_hints")
STATE = obj(stack=array(string(128), 8), decisions=array(DECISION, 16),
            **{key: array(FACT, 16) for key in STATE_FIELDS})
COMPLETION = obj(kind=enum(["project_completed", "validated_checkpoint", "incomplete", "failed"]),
                 scope=string(512), scope_complete=BOOL,
                 automated_validation=enum(["passed", "failed", "not_run"]),
                 user_acceptance=enum(["accepted", "rejected", "not_obtained"]),
                 validated_at=TIME, receipt_id={"anyOf": [ID, NULL]}, checks=array(CHECK, 16), evidence_refs=IDS)
EVIDENCE = obj(id=ID, kind=enum(["execution_validation", "artifact", "observation", "user_acceptance"]),
               locator=string(512), sha256={"anyOf": [SHA, NULL]}, confidence=enum(CONFIDENCE), summary=string(256))
IDENTITY = obj(project_id=string(32, PROJECT_ID), name=string(128), purpose=string(),
               workspace_binding=SHA, project_locator=string(512))
PROPOSAL_FIELDS = dict(identity=IDENTITY, state=STATE, completion=COMPLETION,
    artifacts=array(obj(id=ID, locator=string(512), sha256={"anyOf": [SHA, NULL]}), 16),
    evidence=array(EVIDENCE, 32),
    references_used=array(obj(reference_id=ID, reason=string(256), influenced_area=string(256),
                              pattern_adopted=BOOL, evidence_refs=IDS), 16),
    capabilities_used=obj(skills=array(CAPABILITY, 8), agents=array(CAPABILITY, 4),
                          workflows=array(CAPABILITY, 8), fallbacks=array(FACT, 8)),
    lessons=array(LESSON, 16), environment=array(FACT, 8),
    supersessions=array(obj(decision_id=ID, previous_sha256=SHA, replacement_sha256={"anyOf": [SHA, NULL]},
                            reason=string(512), evidence_refs=IDS), 32))
SCHEMAS = {
    "config": obj(schema_version={"const": "nexus.project-memory.config.v1"}, enabled=BOOL,
                  root=string(512), required_drive={"const": "D:"}),
    "proposal": obj(schema_version={"const": "nexus.project-memory.proposal.v1"}, **PROPOSAL_FIELDS),
    "revision": obj(schema_version={"const": "nexus.project-memory.revision.v1"},
        number={"type": "integer", "minimum": 1, "maximum": MAX_REVISIONS},
        previous_digest={"anyOf": [SHA, NULL]}, revision_digest=SHA,
        written_at=string(40), authorization_ref=ID, **PROPOSAL_FIELDS),
    "bundle": obj(schema_version={"const": "nexus.project-memory.bundle.v1"},
        project_id=string(32, PROJECT_ID), workspace_binding=SHA, current_digest=SHA,
        revisions=array(ref("revision"), MAX_REVISIONS)),
    "write_receipt": obj(schema_version={"const": "nexus.project-memory.write-receipt.v1"},
        status={"const": "persisted"}, project_id=string(32, PROJECT_ID), workspace_binding=SHA,
        revision={"type": "integer", "minimum": 1, "maximum": MAX_REVISIONS},
        previous_digest={"anyOf": [SHA, NULL]}, revision_digest=SHA, bundle_digest=SHA,
        authorization_ref=ID),
    "validation_receipt": obj(schema_version={"const": "nexus.project-validation.v1"},
        project_id=string(32, PROJECT_ID), workspace_binding=SHA, scope=string(512), scope_complete=BOOL,
        automated_validation=enum(["passed", "failed", "not_run"]), validated_at=string(40),
        checks=array(CHECK, 16), artifact_digests=array(obj(locator=string(512), sha256=SHA), 16)),
}
CONTEXT_STATUS = ["project_memory_loaded", "project_memory_disabled", "project_memory_unavailable",
                  "project_memory_missing", "project_memory_ambiguous", "project_memory_invalid",
                  "project_memory_invalid_root", "project_memory_unsafe_file", "project_memory_size_limit",
                  "project_memory_capacity_reached", "project_memory_unauthorized_workspace",
                  "project_memory_unsafe_locator", "project_memory_invalid_time", "project_memory_context_overflow",
                  "project_memory_secret_rejected", "project_memory_content_rejected", "project_memory_private_path_rejected",
                  "project_memory_core_limit", "project_memory_completion_unverified"]
CONTEXT_STATUS += ["project_memory_supersession_required", "project_memory_owner_decision_required", "project_memory_acceptance_unverified"]
CONTEXT_BASE = dict(schema_version={"const": "nexus.project-memory.context.v1"}, status=enum(CONTEXT_STATUS),
                    authority={"const": "none"}, scope={"const": "project_local"},
                    content_trust={"const": "untrusted_historical_data"})
SCHEMAS["context"] = obj(**CONTEXT_BASE, project_id=string(32, PROJECT_ID),
    revision={"type": "integer", "minimum": 1, "maximum": MAX_REVISIONS}, revision_digest=SHA,
    current_state=obj(project_id=string(32, PROJECT_ID), name=string(128), purpose=string(), state=STATE, completion=COMPLETION),
    artifacts=PROPOSAL_FIELDS["artifacts"],
    capabilities_used=PROPOSAL_FIELDS["capabilities_used"], references_used=PROPOSAL_FIELDS["references_used"],
    environment=PROPOSAL_FIELDS["environment"], evidence=PROPOSAL_FIELDS["evidence"],
    lessons=array(obj(id=ID, kind=LESSON["properties"]["kind"], summary=string(512), confidence=enum(CONFIDENCE),
        root_cause_status=LESSON["properties"]["root_cause_status"], root_cause=string(512), correction=string(512),
        validation_result=LESSON["properties"]["validation_result"], prevention=string(512), evidence_refs=IDS,
        match_reasons=array(string(128), 4), source_revision={"type": "integer", "minimum": 1, "maximum": MAX_REVISIONS},
        source_revision_digest=SHA), 4),
    omitted_lesson_count={"type": "integer", "minimum": 0, "maximum": MAX_REVISIONS * 16},
    omitted_sections=array(enum(["lessons", "environment", "capabilities_used", "references_used", "evidence", "artifacts"]), 6))
SCHEMAS["context"]["required"] = list(CONTEXT_BASE)


def _validate(value, schema):
    if "$ref" in schema:
        return _validate(value, SCHEMAS[schema["$ref"].split("/")[-1]])
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                _validate(value, option)
                return
            except MemoryError:
                pass
        raise MemoryError("project_memory_invalid")
    if "const" in schema:
        require(type(value) is type(schema["const"]) and value == schema["const"])
        return
    kind = schema.get("type")
    require(type(value) is {"object": dict, "array": list, "string": str, "boolean": bool,
                           "integer": int, "null": type(None)}[kind])
    if kind == "object":
        require(set(schema["required"]) <= set(value) <= set(schema["properties"]))
        for key, child in value.items():
            _validate(child, schema["properties"][key])
    elif kind == "array":
        require(len(value) <= schema["maxItems"], "project_memory_size_limit")
        for child in value:
            _validate(child, schema["items"])
    elif kind == "string":
        require(len(value.encode("utf-8")) <= schema.get("x-maxUtf8Bytes", 1024), "project_memory_size_limit")
        require(unicodedata.normalize("NFC", value) == value and not any(ord(c) < 32 or ord(c) == 127 or c in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069" for c in value))
        if "pattern" in schema:
            require(re.fullmatch(schema["pattern"], value) is not None)
    elif kind == "integer":
        require(schema["minimum"] <= value <= schema["maximum"])
    if "enum" in schema:
        require(value in schema["enum"])


def validate(value, kind):
    try:
        _validate(value, SCHEMAS[kind])
    except (UnicodeError, RecursionError, TypeError, KeyError) as exc:
        raise MemoryError("project_memory_invalid") from exc
    return value


SECRET = re.compile(r"(?i)(-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:sk-[a-z0-9_-]{16,}|gh[pousr]_[a-z0-9]{20,}|AKIA[A-Z0-9]{16})\b|\b(?:password|api[_-]?key|secret|token|cookie|credential|authorization|recovery[_-]?code)\s*[\"']?\s*[:=]\s*\S+|\beyJ[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,})")
PROHIBITED = re.compile(r"(?im)(```|^\s*(?:system|assistant|user)\s*:|\b(?:hidden chain.of.thought|private model reasoning)\b|^\s*(?:def |class |import |function |const |export |<script|Traceback \())")
PRIVATE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\|/(?:home|Users|etc|tmp)/)")


def screen(value, key=""):
    if type(value) is dict:
        for name, child in value.items():
            screen(child, name)
    elif type(value) is list:
        for child in value:
            screen(child, key)
    elif type(value) is str:
        require(not SECRET.search(value), "project_memory_secret_rejected")
        require(not PROHIBITED.search(value), "project_memory_content_rejected")
        if key != "project_locator":
            require(not PRIVATE_PATH.search(value), "project_memory_private_path_rejected")
        if "https://" in value:
            for url in re.findall(r"https://[^\s]+", value):
                parsed = urlsplit(url)
                require(not parsed.username and not parsed.password and not parsed.query and not parsed.fragment,
                        "project_memory_unsafe_locator")


def safe_locator(value):
    require(type(value) is str and bool(value) and len(value.encode("utf-8")) <= 512)
    path = PurePosixPath(value)
    require(not path.is_absolute() and "\\" not in value and ":" not in value and "%" not in value
            and all(part not in {"", ".", ".."} and not part.endswith((".", " "))
                    and not re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
                    for part in value.split("/")), "project_memory_unsafe_locator")
    return value


def timestamp(value):
    require(type(value) is str)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None and parsed <= datetime.now(timezone.utc), "project_memory_invalid_time")
    except ValueError as exc:
        raise MemoryError("project_memory_invalid_time") from exc


def core_context(value):
    identity = value["identity"]
    return {"project_id": identity["project_id"], "name": identity["name"], "purpose": identity["purpose"],
            "state": value["state"], "completion": value["completion"]}


def validate_proposal(value):
    validate(value, "proposal")
    require(len(encoded(value)) <= MAX_REVISION_BYTES, "project_memory_size_limit")
    screen(value)
    state = value["state"]
    require(sum(len(state[key]) for key in STATE_FIELDS) + len(state["decisions"]) <= 64,
            "project_memory_size_limit")
    evidence = {item["id"]: item for item in value["evidence"]}
    require(len(evidence) == len(value["evidence"]))
    for item in value["evidence"] + value["artifacts"]:
        safe_locator(item["locator"])
    def references(node):
        if type(node) is dict:
            if "evidence_refs" in node:
                refs = node["evidence_refs"]
                require(len(set(refs)) == len(refs) and set(refs) <= set(evidence))
                if node.get("confidence") == "verified":
                    require(refs and all(evidence[key]["confidence"] == "verified" and evidence[key]["sha256"] for key in refs))
            for child in node.values():
                references(child)
        elif type(node) is list:
            for child in node:
                references(child)
    references(value)
    acceptance_evidence = {key for key, item in evidence.items()
                           if item["kind"] == "user_acceptance" and item["confidence"] == "verified" and item["sha256"]}
    if value["completion"]["user_acceptance"] in {"accepted", "rejected"}:
        require(bool(set(value["completion"]["evidence_refs"]) & acceptance_evidence),
                "project_memory_acceptance_unverified")
    for decision in state["decisions"]:
        if decision["user_approved"]:
            require(bool(set(decision["evidence_refs"]) & acceptance_evidence), "project_memory_acceptance_unverified")
    for group in [state["decisions"], *[state[key] for key in STATE_FIELDS], value["lessons"], value["environment"],
                  *value["capabilities_used"].values()]:
        require(len({item["id"] for item in group}) == len(group))
    complete = value["completion"]
    if complete["validated_at"] is not None:
        timestamp(complete["validated_at"])
    if complete["kind"] in {"project_completed", "validated_checkpoint"}:
        require(complete["automated_validation"] == "passed" and complete["scope_complete"]
                and complete["validated_at"] and complete["receipt_id"] in evidence,
                "project_memory_completion_unverified")
        receipt = evidence[complete["receipt_id"]]
        require(receipt["kind"] == "execution_validation" and receipt["confidence"] == "verified" and receipt["sha256"],
                "project_memory_completion_unverified")
        checks = complete["checks"]
        require(checks and any(c["status"] == "passed" for c in checks)
                and all(c["status"] != "failed" and (c["status"] != "passed" or c["confidence"] == "verified" and c["evidence_refs"]) for c in checks),
                "project_memory_completion_unverified")
    if complete["kind"] == "project_completed":
        require(not state["unfinished_work"] and complete["user_acceptance"] != "rejected",
                "project_memory_completion_unverified")
    if complete["kind"] in {"incomplete", "failed"}:
        require(not state["completed_scope"], "project_memory_completion_unverified")
    require(all(f["confidence"] == "verified" and f["evidence_refs"] for f in state["completed_scope"]),
            "project_memory_completion_unverified")
    for group in ("skills", "agents", "workflows"):
        for capability in value["capabilities_used"][group]:
            require(capability["used"] or capability["result"] == "fallback")
            require(not capability["used"] or capability["evidence_refs"])
    for lesson in value["lessons"]:
        if lesson["root_cause_status"] == "unknown":
            require(not lesson["root_cause"])
        if lesson["root_cause_status"] == "known":
            require(lesson["root_cause"] and lesson["confidence"] == "verified" and lesson["evidence_refs"])
        if lesson["kind"] == "successful_pattern":
            require(lesson["confidence"] == "verified" and lesson["validation_result"] == "passed" and lesson["evidence_refs"])
    require(len(encoded(core_context(value))) <= MAX_CORE_BYTES, "project_memory_core_limit")
    return value


def proposal_from_revision(value):
    return {"schema_version": "nexus.project-memory.proposal.v1", **{key: value[key] for key in PROPOSAL_FIELDS}}


def validate_bundle(bundle):
    validate(bundle, "bundle")
    require(len(encoded(bundle)) <= MAX_BUNDLE_BYTES and bundle["revisions"], "project_memory_size_limit")
    previous = None
    identity = None
    prior_revision = None
    for number, revision in enumerate(bundle["revisions"], 1):
        validate_proposal(proposal_from_revision(revision))
        require(len(encoded(revision)) <= MAX_REVISION_BYTES, "project_memory_size_limit")
        require(revision["number"] == number and revision["previous_digest"] == previous)
        timestamp(revision["written_at"])
        require(revision["revision_digest"] == digest({k: v for k, v in revision.items() if k != "revision_digest"}))
        current_identity = revision["identity"]
        if identity is not None:
            require(all(current_identity[k] == identity[k] for k in ("project_id", "workspace_binding", "project_locator")))
            validate_supersessions(prior_revision, revision)
        else:
            require(not revision["supersessions"])
        identity = current_identity
        previous = revision["revision_digest"]
        prior_revision = revision
    require(bundle["current_digest"] == previous and bundle["project_id"] == identity["project_id"]
            and bundle["workspace_binding"] == identity["workspace_binding"])
    return bundle


def validate_supersessions(previous, proposal):
    old = {d["id"]: d for d in previous["state"]["decisions"]}
    new = {d["id"]: d for d in proposal["state"]["decisions"]}
    changes = {key for key in old if key not in new or old[key] != new[key]}
    supersessions = {s["decision_id"]: s for s in proposal["supersessions"]}
    require(len(supersessions) == len(proposal["supersessions"]) and set(supersessions) == changes,
            "project_memory_supersession_required")
    evidence = {e["id"]: e for e in proposal["evidence"]}
    for key in changes:
        item = supersessions[key]
        require(item["previous_sha256"] == digest(old[key])
                and item["replacement_sha256"] == (digest(new[key]) if key in new else None)
                and item["reason"] and item["evidence_refs"], "project_memory_supersession_required")
        if old[key]["kind"] == "frozen" or old[key]["user_approved"]:
            require(any(evidence[e]["kind"] == "user_acceptance" and evidence[e]["confidence"] == "verified"
                        for e in item["evidence_refs"]), "project_memory_owner_decision_required")


def public_schema():
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "nexus.project-memory.v1",
            "$defs": SCHEMAS, "oneOf": [ref(key) for key in SCHEMAS]}
