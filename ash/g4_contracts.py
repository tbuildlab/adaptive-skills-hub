"""G4 bounded domain evidence. Pure checks; no authority, memory service or I/O."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any

from .ecosystem_models import EcosystemError, canonical_json_bytes, parse_json_bytes
from .ecosystem_evidence import redact_public_summary
from .g1_profiles import G1Error, bounded, exact, integer, sha, token, tokens, enum

MAX_BYTES = 65536
RELATIONS = frozenset({"requires", "uses", "depends_on", "conflicts_with", "produces",
                       "validated_by", "available_through", "source_of"})
OPERATIONS = frozenset({"read", "write", "execute", "network", "delegate"})
PACK_EVIDENCE = {
    "website": frozenset({"interaction", "consumer_regression", "accessibility", "boundary", "artifact_inspection"}),
    "source_backed_report": frozenset({"source_claim", "uncertainty", "calculation", "artifact_inspection", "render"}),
}
FIELDS = {
    "project-decision": {"decision_key", "content_sha256", "source_refs", "approving_authority_ref", "valid_until",
                         "state", "supersedes", "retention", "obligations"},
    "context-manifest": {"sources", "recipients", "omissions", "disclosure_limits", "preserved_obligations"},
    "capability-relation": {"relation", "from_endpoint", "to_endpoint", "provenance_refs"},
    "change-impact": {"repository_id", "base_commit", "changed_surfaces", "dependencies", "consumers",
                      "shared_contracts", "validation_obligations", "unexamined"},
    "workflow-pack": {"pack", "version", "applicability", "required_capabilities", "allowed_operations", "required_evidence"},
}


class G4Error(ValueError):
    """Closed diagnostics never include untrusted text or raw Host output."""


def require(condition: bool, code: str = "G4_INVALID_INPUT") -> None:
    if not condition:
        raise G4Error(code)


def canonical(value: Any) -> bytes:
    try:
        bounded(value)
        # Reuse frozen public-evidence redaction patterns. Refuse rather than
        # retaining a changed secret-bearing identifier in canonical records.
        stack = [value]
        while stack:
            item = stack.pop()
            if type(item) is dict:
                stack.extend(item.keys())
                stack.extend(item.values())
            elif type(item) is list:
                stack.extend(item)
            elif type(item) is str:
                require(not redact_public_summary(item)[1])
        return canonical_json_bytes(value, maximum_bytes=MAX_BYTES)
    except (G1Error, EcosystemError, UnicodeError, RecursionError):
        raise G4Error("G4_INVALID_INPUT") from None


def parse(raw: bytes) -> Any:
    try:
        value = parse_json_bytes(raw, maximum_bytes=MAX_BYTES, label="G4 input")
        canonical(value)
        return value
    except (G1Error, EcosystemError, UnicodeError, RecursionError):
        raise G4Error("G4_INVALID_INPUT") from None


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def binding(value: Any) -> dict:
    exact(value, {"workspace_id", "project_id", "task_id", "action_id", "execution_id",
                  "generation", "incarnation", "input_sha256"})
    for key in ("workspace_id", "project_id", "task_id", "action_id", "execution_id", "incarnation"):
        token(value[key])
    integer(value["generation"])
    require(value["generation"] > 0)
    sha(value["input_sha256"])
    return value


def refs(value: Any, *, nonempty: bool = False) -> list[str]:
    require(type(value) is list and len(value) <= 64 and (bool(value) or not nonempty))
    result = [sha(item) for item in value]
    require(len(result) == len(set(result)))
    return sorted(result)


def endpoint(value: Any) -> dict:
    exact(value, {"ref", "version"})
    sha(value["ref"])
    token(value["version"])
    return value


@dataclass(frozen=True, slots=True)
class DomainRecord:
    kind: str
    canonical_body: bytes
    record_id: str

    def to_dict(self) -> dict:
        return parse(self.canonical_body)


def record(kind: str, value: Any) -> DomainRecord:
    """All records, including CONFIRMED, are evidence claims, never verified grants."""
    try:
        canonical(value)
        require(type(kind) is str and kind in FIELDS)
        exact(value, FIELDS[kind] | {"schema_version", "binding"})
        require(value["schema_version"] == "nexus.g4." + kind + ".v1")
        binding(value["binding"])
        v = parse(canonical(value))
        if kind == "project-decision":
            token(v["decision_key"])
            sha(v["content_sha256"])
            v["source_refs"] = refs(v["source_refs"], nonempty=True)
            v["obligations"] = refs(v["obligations"])
            if v["approving_authority_ref"] is not None:
                sha(v["approving_authority_ref"])
            integer(v["valid_until"])
            enum(v["state"], {"PROPOSED", "CONFIRMED", "SUPERSEDED", "DISPUTED"})
            if v["supersedes"] is not None:
                sha(v["supersedes"])
            enum(v["retention"], {"TASK", "PROJECT", "FORGET_AUTHORIZED"})
            require(v["state"] != "CONFIRMED" or v["approving_authority_ref"] is not None)
        elif kind == "context-manifest":
            require(type(v["sources"]) is list and 1 <= len(v["sources"]) <= 64)
            seen = set()
            for source in v["sources"]:
                exact(source, {"ref", "sha256", "project_id", "task_id", "transformation", "original_ref", "valid_until"})
                sha(source["ref"])
                sha(source["sha256"])
                token(source["project_id"])
                token(source["task_id"])
                enum(source["transformation"], {"ORIGINAL", "DERIVED"})
                integer(source["valid_until"])
                require(source["ref"] not in seen)
                seen.add(source["ref"])
                if source["transformation"] == "DERIVED":
                    sha(source["original_ref"])
                    require(source["original_ref"] != source["ref"])
                else:
                    require(source["original_ref"] is None)
            v["sources"].sort(key=lambda item: item["ref"])
            for key in ("recipients", "disclosure_limits"):
                v[key] = tokens(v[key], nonempty=True)
            for key in ("omissions", "preserved_obligations"):
                v[key] = refs(v[key])
            require(not (seen & set(v["omissions"])))
        elif kind == "capability-relation":
            enum(v["relation"], RELATIONS)
            endpoint(v["from_endpoint"])
            endpoint(v["to_endpoint"])
            v["provenance_refs"] = refs(v["provenance_refs"], nonempty=True)
        elif kind == "change-impact":
            token(v["repository_id"])
            require(type(v["base_commit"]) is str and re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", v["base_commit"]) is not None)
            for key in ("changed_surfaces", "dependencies", "consumers", "shared_contracts", "validation_obligations", "unexamined"):
                v[key] = tokens(v[key], nonempty=key in {"changed_surfaces", "validation_obligations"})
        else:
            enum(v["pack"], PACK_EVIDENCE)
            token(v["version"])
            for key in ("applicability", "required_capabilities", "allowed_operations", "required_evidence"):
                v[key] = tokens(v[key], nonempty=True)
            require(set(v["allowed_operations"]) <= OPERATIONS)
            require(set(v["required_evidence"]) == PACK_EVIDENCE[v["pack"]])
        raw = canonical(v)
        identity = hashlib.sha256(("nexus.g4." + kind + ".v1\0").encode() + raw).hexdigest()
        return DomainRecord(kind, raw, identity)
    except (G1Error, EcosystemError, KeyError, TypeError, UnicodeError, RecursionError):
        raise G4Error("G4_INVALID_INPUT") from None


def checked(item: DomainRecord, kind: str, expected_binding: dict) -> dict:
    require(type(item) is DomainRecord and item.kind == kind)
    rebuilt = record(kind, item.to_dict())
    require(rebuilt == item, "G4_EVIDENCE_CORRUPT")
    require(rebuilt.to_dict()["binding"] == expected_binding, "G4_BINDING_MISMATCH")
    return rebuilt.to_dict()


def validate_domain_bundle(*, pack: DomainRecord, context: DomainRecord, impact: DomainRecord,
                          decisions: tuple[DomainRecord, ...], relations: tuple[DomainRecord, ...],
                          expected_binding: dict, now: int, permitted_operations: list[str],
                          permitted_recipients: list[str], source_refs: list[str],
                          confirmation_refs: list[str], endpoint_versions: dict[str, str],
                          source_digests: dict[str, str], task_class: str,
                          expected_repository_id: str, expected_base_commit: str,
                          required_obligations: list[str], required_consumers: list[str],
                          required_validations: list[str], available_capabilities: list[str],
                          observations: dict[str, dict]) -> dict:
    """Offline coverage oracle. Supplied facts remain NON_AUTHORITATIVE.

    No retrieval, confirmation, forgetting, semantic analysis or execution occurs.
    Domain checks cannot manufacture completeness of Host-provided impact analysis.
    """
    try:
        canonical({"binding": expected_binding, "endpoints": endpoint_versions, "observations": observations,
                   "source_digests": source_digests})
        binding(expected_binding)
        integer(now)
        require(type(decisions) is tuple and len(decisions) <= 64)
        require(type(relations) is tuple and len(relations) <= 64)
        allowed = set(tokens(permitted_operations))
        recipients = set(tokens(permitted_recipients))
        sources = set(refs(source_refs))
        confirmations = set(refs(confirmation_refs))
        obligations = set(refs(required_obligations))
        consumers = set(tokens(required_consumers))
        validations = set(tokens(required_validations))
        capabilities = set(tokens(available_capabilities))
        token(task_class)
        token(expected_repository_id)
        require(type(expected_base_commit) is str and re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", expected_base_commit) is not None)
        for ref, source_digest in source_digests.items():
            sha(ref)
            sha(source_digest)
        for key, version in endpoint_versions.items():
            sha(key)
            token(version)
        p = checked(pack, "workflow-pack", expected_binding)
        c = checked(context, "context-manifest", expected_binding)
        i = checked(impact, "change-impact", expected_binding)
        require(task_class in p["applicability"], "G4_PACK_INAPPLICABLE")
        require(i["repository_id"] == expected_repository_id and i["base_commit"] == expected_base_commit, "G4_REPOSITORY_MISMATCH")
        require(set(p["allowed_operations"]) <= allowed, "G4_POLICY_EXPANSION")
        require(set(p["required_capabilities"]) <= capabilities, "G4_CAPABILITY_UNAVAILABLE")
        require(set(c["recipients"]) <= recipients and set(c["recipients"]) <= set(c["disclosure_limits"]), "G4_DISCLOSURE_DENIED")
        require(obligations <= set(c["preserved_obligations"]), "G4_REDUCTION_LOSS")
        included = {s["ref"] for s in c["sources"]}
        for s in c["sources"]:
            require(s["project_id"] == expected_binding["project_id"] and s["task_id"] == expected_binding["task_id"], "G4_NAMESPACE_MISMATCH")
            require(s["ref"] in sources and now < s["valid_until"], "G4_SOURCE_UNAVAILABLE")
            require(source_digests.get(s["ref"]) == s["sha256"], "G4_SOURCE_DIGEST_MISMATCH")
            require(s["transformation"] != "DERIVED" or s["original_ref"] in sources, "G4_ORIGINAL_REQUIRED")
        active_contents: dict[str, str] = {}
        decision_ids = {d.record_id for d in decisions if type(d) is DomainRecord}
        require(len(decision_ids) == len(decisions), "G4_DECISION_CONFLICT")
        superseded_ids = set()
        for d in decisions:
            v = checked(d, "project-decision", expected_binding)
            require(v["state"] == "CONFIRMED" and now < v["valid_until"], "G4_DECISION_NOT_CURRENT")
            require(v["approving_authority_ref"] in confirmations and set(v["source_refs"]) <= included, "G4_CONFIRMATION_UNVERIFIED")
            require(set(v["obligations"]) <= set(c["preserved_obligations"]), "G4_FORGET_UNRESOLVED")
            require(v["retention"] != "FORGET_AUTHORIZED" or not v["obligations"], "G4_FORGET_UNRESOLVED")
            if v["supersedes"] is not None:
                require(v["supersedes"] not in decision_ids and v["supersedes"] in sources, "G4_SUPERSESSION_INVALID")
                require(v["supersedes"] not in superseded_ids, "G4_DECISION_CONFLICT")
                superseded_ids.add(v["supersedes"])
            require(v["decision_key"] not in active_contents, "G4_DECISION_CONFLICT")
            active_contents[v["decision_key"]] = v["content_sha256"]
        graph: dict[str, set[str]] = {}
        for r in relations:
            v = checked(r, "capability-relation", expected_binding)
            require(set(v["provenance_refs"]) <= sources, "G4_RELATION_UNVERIFIED")
            for e in (v["from_endpoint"], v["to_endpoint"]):
                require(endpoint_versions.get(e["ref"]) == e["version"], "G4_ENDPOINT_MISMATCH")
            require(v["relation"] != "conflicts_with", "G4_RELATION_CONFLICT")
            if v["relation"] in {"requires", "depends_on"}:
                graph.setdefault(v["from_endpoint"]["ref"], set()).add(v["to_endpoint"]["ref"])
        visited: set[str] = set()
        def visit(node: str, ancestors: frozenset[str]) -> None:
            require(node not in ancestors, "G4_DEPENDENCY_CYCLE")
            if node in visited:
                return
            for child in graph.get(node, ()):
                visit(child, ancestors | {node})
            visited.add(node)
        for node in graph:
            visit(node, frozenset())
        require(consumers <= set(i["consumers"]) and validations <= set(i["validation_obligations"]), "G4_IMPACT_COVERAGE")
        require(not i["unexamined"], "G4_IMPACT_UNKNOWN")
        needed = set(p["required_evidence"]) | set(i["validation_obligations"])
        require(needed <= set(observations), "G4_ACCEPTANCE_COVERAGE")
        for name, observation in observations.items():
            token(name)
            exact(observation, {"status", "input_sha256", "artifact_sha256", "source_refs"})
            enum(observation["status"], {"PASS", "FAIL", "UNKNOWN", "CANCELLED"})
            sha(observation["input_sha256"])
            sha(observation["artifact_sha256"])
            refs(observation["source_refs"], nonempty=True)
            require(set(observation["source_refs"]) <= sources, "G4_OBSERVATION_SOURCE")
            require(observation["input_sha256"] == expected_binding["input_sha256"], "G4_BINDING_MISMATCH")
            require(observation["status"] == "PASS", "G4_OBSERVATION_NOT_PASS")
        require(len({o["artifact_sha256"] for o in observations.values()}) == 1, "G4_ARTIFACT_MISMATCH")
        return {"status": "PASS_STRUCTURAL_ONLY", "basis": "NON_AUTHORITATIVE", "dispatch_authority": "none",
                "pack_ref": pack.record_id, "binding_sha256": digest(expected_binding)}
    except G4Error:
        raise
    except (G1Error, EcosystemError, KeyError, TypeError, RecursionError):
        raise G4Error("G4_INVALID_INPUT") from None
