"""Versioned, bounded semantic applicability for V2 Skill routing.

The task classifier in this module is deterministic and side-effect free.  It
does not grant execution authority.  A Skill can pass the compatibility gate
only through a manifest-protected Nexus registry entry or an in-memory
``TrustedSkillApplicability`` object created by Nexus itself (used by bounded
internal callers and deterministic fixtures). Raw Skill text and discovery
metadata are never treated as applicability evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping
import unicodedata

from .common import tokenize


SEMANTIC_DOMAIN_MODEL_VERSION = "nexus.semantic-task-domain.v1"
TRUSTED_APPLICABILITY_SCHEMA_VERSION = "nexus.trusted-skill-applicability.v1"
SEMANTIC_APPLICABILITY_REGISTRY_VERSION = "nexus.skill-applicability-registry.v1"
MAX_TASK_DOMAINS = 6
MAX_TASK_KINDS = 8
MAX_CONTEXT_KINDS = 8
MAX_REGISTRY_RULES = 256
MAX_SEMANTIC_TASK_BYTES = 8 * 1024
MAX_SEMANTIC_TASK_CHARS = 8 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CONTROL_PLANE_FIELD_RE = re.compile(
    r'''["']?\b(?:schema_version|model_version|semantic_domain_model_version|'''
    r'''primary_domain|secondary_domains|required_domains|domain_type|task_type|'''
    r'''semantic_task_kinds|task_kinds|context_kinds|supported_domains|'''
    r'''incompatible_domains|supported_task_kinds|required_context|artifact_families|'''
    r'''required_capabilities|required_operations|artifact_type|deliverable|'''
    r'''output_format_constraints|applicability_evidence|domain_coverage|reason_code|'''
    r'''execution_authority|selected_skills|selected_skill|host_eligible|execution_requested)'''
    r'''\b["']?\s*[:=]\s*(?:\[[^\]\n]{0,8192}\]|[^.;\n]{0,8192})''',
)

KNOWN_DOMAINS = frozenset({
    "product_ux_research",
    "software_research",
    "architecture_review",
    "security_review",
    "code_review",
    "visual_design_qa",
    "presentation",
    "document",
    "spreadsheet",
    "pdf",
    "general_research",
    # Existing V2 engineering roles remain explicit rather than being folded
    # into broad research/review labels.
    "backend_repair",
    "software_testing",
    "frontend_implementation",
    "general",
})
KNOWN_TASK_KINDS = frozenset({
    "research",
    "review",
    "architecture_design",
    "security_review",
    "code_review",
    "visual_review",
    "create_artifact",
    "edit_artifact",
    "read_artifact",
    "software_debug",
    "software_test",
    "implementation",
    "animation",
    "code_documentation",
    "analysis",
})
KNOWN_CONTEXT_KINDS = frozenset({
    "product_experience",
    "software_ecosystem",
    "software_system",
    "source_code",
    "rendered_visual",
    "office_artifact",
    "general_evidence",
})
KNOWN_ARTIFACT_FAMILIES = frozenset({"presentation", "document", "spreadsheet", "pdf"})

DOMAIN_TO_CAPABILITY: dict[str, str] = {
    "product_ux_research": "research",
    "software_research": "research",
    "architecture_review": "research",
    "security_review": "security",
    "code_review": "general",
    "visual_design_qa": "frontend",
    "presentation": "presentation",
    "document": "document",
    "spreadsheet": "spreadsheet",
    "pdf": "pdf",
    "general_research": "research",
    "backend_repair": "backend",
    "software_testing": "testing",
    "frontend_implementation": "frontend",
    "general": "general",
}

DOMAIN_MATCH = "DOMAIN_MATCH"
DOMAIN_INCOMPATIBLE = "DOMAIN_INCOMPATIBLE"
DOMAIN_EVIDENCE_MISSING = "DOMAIN_EVIDENCE_MISSING"
TASK_KIND_INCOMPATIBLE = "TASK_KIND_INCOMPATIBLE"
MINIMAL_SET_REDUNDANT = "MINIMAL_SET_REDUNDANT"
CAPABILITY_NOT_COVERED = "CAPABILITY_NOT_COVERED"
SKILL_INTEGRITY_EVIDENCE_MISSING = "SKILL_INTEGRITY_EVIDENCE_MISSING"
SKILL_INTEGRITY_CHANGED = "SKILL_INTEGRITY_CHANGED"


class SemanticRoutingError(RuntimeError):
    """Fail-closed error for malformed or unverifiable applicability data."""


def _ordered_unique(values: Iterable[str], *, limit: int, allowed: frozenset[str]) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or value not in allowed:
            raise SemanticRoutingError("semantic evidence contains an unsupported value")
        if value not in result:
            result.append(value)
        if len(result) > limit:
            raise SemanticRoutingError("semantic evidence exceeds its bounded list limit")
    return tuple(result)


@dataclass(frozen=True)
class SemanticTaskModel:
    schema_version: str
    primary_domain: str
    secondary_domains: tuple[str, ...]
    incompatible_domains: tuple[str, ...]
    task_kinds: tuple[str, ...]
    context_kinds: tuple[str, ...]
    artifact_families: tuple[str, ...]
    evidence_codes: tuple[str, ...]

    @property
    def required_domains(self) -> tuple[str, ...]:
        values = (self.primary_domain, *self.secondary_domains)
        return tuple(value for value in values if value != "general")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "primary_domain": self.primary_domain,
            "secondary_domains": list(self.secondary_domains),
            "incompatible_domains": list(self.incompatible_domains),
            "task_kinds": list(self.task_kinds),
            "context_kinds": list(self.context_kinds),
            "artifact_families": list(self.artifact_families),
            "evidence_codes": list(self.evidence_codes),
        }


@dataclass(frozen=True)
class TrustedSkillApplicability:
    schema_version: str
    model_version: str
    supported_domains: tuple[str, ...]
    incompatible_domains: tuple[str, ...]
    supported_task_kinds: tuple[str, ...]
    required_context: tuple[str, ...]
    artifact_families: tuple[str, ...]
    provenance: str
    applicability_version: str

    def to_public_evidence(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "model_version": self.model_version,
            "supported_domains": list(self.supported_domains),
            "incompatible_domains": list(self.incompatible_domains),
            "supported_task_kinds": list(self.supported_task_kinds),
            "required_context": list(self.required_context),
            "artifact_families": list(self.artifact_families),
            "provenance": self.provenance,
            "applicability_version": self.applicability_version,
        }


@dataclass(frozen=True)
class ApplicabilityDecision:
    allowed: bool
    reason_code: str
    matched_domains: tuple[str, ...] = ()
    unmatched_domains: tuple[str, ...] = ()
    matched_task_kinds: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class _RegistryRule:
    skill_name: str
    metadata_fingerprint: str
    skill_content_sha256: str
    source_scopes: tuple[str, ...]
    applicability: TrustedSkillApplicability


@dataclass(frozen=True)
class TrustedApplicabilityRegistry:
    rules: tuple[_RegistryRule, ...]
    registry_sha256: str

    def resolve(self, record: Mapping[str, Any]) -> TrustedSkillApplicability | None:
        name = str(record.get("name", "")).casefold()
        fingerprint = str(record.get("metadata_fingerprint", "")).casefold()
        content_sha256 = str(record.get("content_sha256", "")).casefold()
        provenance = record.get("provenance", {})
        scope = str(provenance.get("source_scope", "")) if isinstance(provenance, Mapping) else ""
        matches = [
            rule for rule in self.rules
            if rule.skill_name.casefold() == name
            and rule.metadata_fingerprint == fingerprint
            and rule.skill_content_sha256 == content_sha256
            and scope in rule.source_scopes
        ]
        if len(matches) > 1:
            raise SemanticRoutingError("trusted applicability identity is ambiguous")
        return matches[0].applicability if matches else None


def make_trusted_applicability(
    *,
    supported_domains: Iterable[str],
    supported_task_kinds: Iterable[str],
    incompatible_domains: Iterable[str] = (),
    required_context: Iterable[str] = (),
    artifact_families: Iterable[str] = (),
    provenance: str = "nexus_internal",
    applicability_version: str = "1",
) -> TrustedSkillApplicability:
    supported = _ordered_unique(supported_domains, limit=MAX_TASK_DOMAINS, allowed=KNOWN_DOMAINS)
    incompatible = _ordered_unique(incompatible_domains, limit=MAX_TASK_DOMAINS, allowed=KNOWN_DOMAINS)
    task_kinds = _ordered_unique(supported_task_kinds, limit=MAX_TASK_KINDS, allowed=KNOWN_TASK_KINDS)
    contexts = _ordered_unique(required_context, limit=MAX_CONTEXT_KINDS, allowed=KNOWN_CONTEXT_KINDS)
    artifacts = _ordered_unique(artifact_families, limit=4, allowed=KNOWN_ARTIFACT_FAMILIES)
    if not supported or not task_kinds:
        raise SemanticRoutingError("trusted applicability requires positive domain and task-kind evidence")
    if set(supported) & set(incompatible):
        raise SemanticRoutingError("trusted applicability is internally contradictory")
    if not isinstance(provenance, str) or not provenance or len(provenance) > 80:
        raise SemanticRoutingError("trusted applicability provenance is invalid")
    if not isinstance(applicability_version, str) or not applicability_version or len(applicability_version) > 32:
        raise SemanticRoutingError("trusted applicability version is invalid")
    return TrustedSkillApplicability(
        TRUSTED_APPLICABILITY_SCHEMA_VERSION,
        SEMANTIC_DOMAIN_MODEL_VERSION,
        supported,
        incompatible,
        task_kinds,
        contexts,
        artifacts,
        provenance,
        applicability_version,
    )


def _normalized_text(task: str) -> str:
    if (
        not isinstance(task, str)
        or len(task) > MAX_SEMANTIC_TASK_CHARS
        or len(task.encode("utf-8")) > MAX_SEMANTIC_TASK_BYTES
    ):
        raise SemanticRoutingError("semantic task exceeds the bounded input limit")
    return " ".join(unicodedata.normalize("NFKC", task).casefold().split())


def semantic_task_model(task: str) -> SemanticTaskModel:
    """Classify a task with bounded, reusable semantic constraints.

    The classifier deliberately requires action/context pairs.  Generic words
    such as ``document``, ``research``, ``review``, and ``design`` never grant
    a Skill match by themselves.
    """
    text = _normalized_text(task)
    # Treat serialized applicability claims inside the user task as data, not
    # routing authority.  This covers common prompt-injection/protocol-shaping
    # forms while leaving ordinary natural-language intent intact.
    text = CONTROL_PLANE_FIELD_RE.sub(" ", text)
    text = " ".join(text.split())
    tokens = tokenize(text)
    informational = text.startswith(("what is ", "what are ", "what does ", "define ", "explain "))
    artifact_action = bool(re.search(
        r"\b(create|prepare|write|build|generate|edit|redline|format|read|inspect|review|validate|verify)\b",
        text,
    )) and not bool(tokens & {"fix", "debug", "diagnose", "failure", "failed", "exception"})

    artifact_families: list[str] = []
    if not informational and artifact_action and tokens & {"presentation", "powerpoint", "ppt", "pptx", "slides", "deck"}:
        artifact_families.append("presentation")
    if not informational and artifact_action and tokens & {"spreadsheet", "spreadsheets", "excel", "workbook", "xlsx", "xls"}:
        artifact_families.append("spreadsheet")
    if not informational and artifact_action and tokens & {"pdf"}:
        artifact_families.append("pdf")
    document_phrase = bool(re.search(
        r"\b(create|prepare|write|edit|redline|format|generate|read|inspect|review|validate|verify)\b.{0,48}\b(word document|word report|docx|memo|letter|document artifact)\b",
        text,
    ))
    explicit_document_file = bool(tokens & {"docx"}) or "microsoft word" in text or "word document" in text
    code_documentation = bool(
        tokens & {"documentation", "readme", "docstring", "docstrings"}
        or re.search(r"\bdocument\s+(the|this|that|our|my|api|code|function|class|behavior|behaviour|root cause|implementation)\b", text)
    )
    if not informational and artifact_action and not code_documentation and (document_phrase or explicit_document_file):
        artifact_families.append("document")

    research_intent = bool(tokens & {
        "research", "investigate", "evidence", "sources", "survey", "landscape",
        "assignment", "coursework", "rubric", "lecturer",
    }) and not informational
    review_intent = bool(tokens & {"review", "audit", "assess", "evaluate", "acceptance", "critique", "inspect", "compare"}) and not informational
    security_intent = (
        bool(tokens & {"security", "secure", "vulnerability", "vulnerabilities", "threat", "threats", "attack", "injection", "authorization", "authz", "permission", "permissions", "ssrf", "xss", "csrf", "secrets"})
        or "cross-user" in text
        or "cross user" in text
        or "another user's" in text
        or "another user’s" in text
    )
    architecture_intent = bool(tokens & {"architecture", "architectural", "protocol", "interoperability"}) or "system design" in text or "security boundaries" in text
    source_code_context = bool(tokens & {"code", "python", "javascript", "typescript", "implementation", "diff", "commit", "function", "class", "repository", "repositories", "codebase"})
    visual_context = bool(tokens & {"visual", "rendered", "screenshot", "pixel", "layout", "mockup", "prototype"}) or "approved design" in text or "design qa" in text
    ux_context = (
        bool(tokens & {"ux", "onboarding", "friction", "journey", "usability"})
        or "user pain" in text
        or "product experience" in text
        or (research_intent and bool(tokens & {"user", "users"}) and bool(tokens & {"product", "workflow", "support", "complaints"}))
    )
    software_context = bool(tokens & {"github", "repository", "repositories", "codebase", "library", "libraries", "framework", "frameworks", "package", "packages", "dependency", "dependencies", "mcp", "runtime", "software"})
    backend_repair = bool(tokens & {"fix", "debug", "diagnose", "failure", "failed", "exception", "error", "500"}) and bool(tokens & {"backend", "api", "endpoint", "server", "service", "http", "database"})
    testing_intent = bool(tokens & {"test", "tests", "testing", "regression", "reproduce", "reproduction"})
    frontend_implementation = bool(tokens & {"frontend", "react", "css", "html", "ui"}) and bool(re.search(r"\b(build|implement|fix|create|improve)\b", text)) and not research_intent

    domains: list[str] = []
    if research_intent and ux_context:
        domains.append("product_ux_research")
    if research_intent and software_context:
        domains.append("software_research")
    if architecture_intent and (review_intent or research_intent or tokens & {"design"}):
        domains.append("architecture_review")
    if security_intent and (review_intent or research_intent or source_code_context or backend_repair):
        domains.append("security_review")
    if source_code_context and review_intent:
        domains.append("code_review")
    if visual_context and review_intent:
        domains.append("visual_design_qa")
    if research_intent and not any(domain in domains for domain in ("product_ux_research", "software_research", "architecture_review", "security_review")):
        domains.append("general_research")
    if backend_repair:
        domains.append("backend_repair")
    if testing_intent:
        domains.append("software_testing")
    if frontend_implementation:
        domains.append("frontend_implementation")
    domains.extend(artifact_families)
    if backend_repair and "backend_repair" in domains:
        domains.remove("backend_repair")
        domains.insert(0, "backend_repair")
    domains = list(_ordered_unique(domains, limit=MAX_TASK_DOMAINS, allowed=KNOWN_DOMAINS))
    if not domains:
        domains = ["general"]

    task_kinds: list[str] = []
    if research_intent:
        task_kinds.append("research")
    if review_intent:
        task_kinds.append("review")
    if architecture_intent:
        task_kinds.append("architecture_design" if not review_intent else "review")
    if security_intent and (review_intent or source_code_context or backend_repair):
        task_kinds.append("security_review")
    if source_code_context and review_intent:
        task_kinds.append("code_review")
    if visual_context and review_intent:
        task_kinds.append("visual_review")
    if artifact_families:
        task_kinds.append(
            "edit_artifact" if re.search(r"\b(edit|redline|format)\b", text)
            else "read_artifact" if re.search(r"\b(read|inspect|review|validate|verify)\b", text) and not re.search(r"\b(create|prepare|write|build|generate)\b", text)
            else "create_artifact"
        )
    if backend_repair:
        task_kinds.append("software_debug")
    if testing_intent:
        task_kinds.append("software_test")
    if frontend_implementation:
        task_kinds.append("implementation")
    if tokens & {"animation", "animate", "motion", "scroll", "transition", "timeline", "tween"}:
        task_kinds.append("animation")
    if code_documentation:
        task_kinds.append("code_documentation")
    if not task_kinds:
        task_kinds.append("analysis")
    task_kinds = list(_ordered_unique(task_kinds, limit=MAX_TASK_KINDS, allowed=KNOWN_TASK_KINDS))

    contexts: list[str] = []
    if ux_context:
        contexts.append("product_experience")
    if software_context:
        contexts.append("software_ecosystem")
    if source_code_context or backend_repair or code_documentation:
        contexts.extend(("software_system", "source_code"))
    elif security_intent or architecture_intent:
        contexts.append("software_system")
    if visual_context:
        contexts.append("rendered_visual")
    if artifact_families:
        contexts.append("office_artifact")
    if research_intent:
        contexts.append("general_evidence")
    contexts = list(_ordered_unique(contexts, limit=MAX_CONTEXT_KINDS, allowed=KNOWN_CONTEXT_KINDS))

    required = set(domains)
    incompatible: list[str] = []
    if required & {"software_research", "architecture_review", "security_review", "code_review", "backend_repair", "software_testing"}:
        incompatible.extend(("product_ux_research", "visual_design_qa"))
    elif "product_ux_research" in required:
        incompatible.extend(("software_research", "security_review", "code_review", "visual_design_qa"))
    elif "visual_design_qa" in required:
        incompatible.extend(("software_research", "architecture_review", "security_review", "code_review"))
    incompatible = [item for item in dict.fromkeys(incompatible) if item not in required][:MAX_TASK_DOMAINS]

    evidence: list[str] = []
    if artifact_families:
        evidence.append("EXPLICIT_ARTIFACT_ACTION")
    if research_intent:
        evidence.append("EXPLICIT_RESEARCH_INTENT")
    if review_intent:
        evidence.append("EXPLICIT_REVIEW_INTENT")
    if code_documentation:
        evidence.append("CODE_DOCUMENTATION_NOT_DOCX")
    if domains == ["general"]:
        evidence.append("NO_SPECIALIZED_DOMAIN_EVIDENCE")

    return SemanticTaskModel(
        SEMANTIC_DOMAIN_MODEL_VERSION,
        domains[0],
        tuple(domains[1:]),
        tuple(incompatible),
        tuple(task_kinds),
        tuple(contexts),
        tuple(artifact_families),
        tuple(evidence),
    )


def evaluate_applicability(model: SemanticTaskModel, applicability: TrustedSkillApplicability) -> ApplicabilityDecision:
    if applicability.schema_version != TRUSTED_APPLICABILITY_SCHEMA_VERSION or applicability.model_version != SEMANTIC_DOMAIN_MODEL_VERSION:
        return ApplicabilityDecision(False, DOMAIN_EVIDENCE_MISSING)
    try:
        verified = make_trusted_applicability(
            supported_domains=applicability.supported_domains,
            incompatible_domains=applicability.incompatible_domains,
            supported_task_kinds=applicability.supported_task_kinds,
            required_context=applicability.required_context,
            artifact_families=applicability.artifact_families,
            provenance=applicability.provenance,
            applicability_version=applicability.applicability_version,
        )
    except SemanticRoutingError:
        return ApplicabilityDecision(False, DOMAIN_EVIDENCE_MISSING)
    if verified != applicability:
        return ApplicabilityDecision(False, DOMAIN_EVIDENCE_MISSING)
    required = set(model.required_domains)
    supported = set(applicability.supported_domains)
    matched = tuple(domain for domain in model.required_domains if domain in supported)
    unmatched = tuple(domain for domain in model.required_domains if domain not in supported)
    if not matched:
        if required & set(applicability.incompatible_domains) or supported & set(model.incompatible_domains):
            return ApplicabilityDecision(False, DOMAIN_INCOMPATIBLE, (), unmatched)
        return ApplicabilityDecision(False, DOMAIN_EVIDENCE_MISSING, (), unmatched)
    matched_task_kinds = tuple(kind for kind in model.task_kinds if kind in applicability.supported_task_kinds)
    if not matched_task_kinds or not set(applicability.required_context).issubset(model.context_kinds):
        return ApplicabilityDecision(False, TASK_KIND_INCOMPATIBLE, matched, unmatched)
    if model.artifact_families and applicability.artifact_families:
        if not set(model.artifact_families) & set(applicability.artifact_families):
            return ApplicabilityDecision(False, DOMAIN_INCOMPATIBLE, matched, unmatched, matched_task_kinds)
    return ApplicabilityDecision(True, DOMAIN_MATCH, matched, unmatched, matched_task_kinds)


def _stable_bytes(path: Path) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("not a regular file")
        before = path.stat()
        contents = path.read_bytes()
        after = path.stat()
    except OSError as exc:
        raise SemanticRoutingError("semantic applicability metadata is unavailable") from exc
    fingerprint = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
    if fingerprint(before) != fingerprint(after) or len(contents) != after.st_size:
        raise SemanticRoutingError("semantic applicability metadata changed during verification")
    return contents


def load_trusted_applicability_registry(
    *, root: Path | None = None, integrity_manifest_path: Path | None = None,
) -> TrustedApplicabilityRegistry:
    root = (root or Path(__file__).resolve().parents[1]).resolve()
    registry_path = root / "config" / "skill-applicability.json"
    release_manifest = root / "release-manifest.json"
    manifest_path = integrity_manifest_path or (release_manifest if release_manifest.is_file() else root / "MANIFEST.json")
    manifest_raw = _stable_bytes(manifest_path)
    try:
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SemanticRoutingError("semantic applicability integrity manifest is invalid") from exc
    if not isinstance(manifest, Mapping):
        raise SemanticRoutingError("semantic applicability integrity manifest is invalid")
    is_release = "files" in manifest
    entries = manifest.get("files") if is_release else manifest
    if not isinstance(entries, Mapping):
        raise SemanticRoutingError("semantic applicability integrity manifest is invalid")
    try:
        relative = registry_path.resolve(strict=True).relative_to(root).as_posix()
    except (OSError, ValueError) as exc:
        raise SemanticRoutingError("semantic applicability registry is outside its integrity root") from exc
    metadata = entries.get(relative)
    registry_raw = _stable_bytes(registry_path)
    digest_bytes = registry_raw if is_release else registry_raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    if (
        not isinstance(metadata, Mapping)
        or not isinstance(metadata.get("sha256"), str)
        or not SHA256_RE.fullmatch(str(metadata["sha256"]))
        or hashlib.sha256(digest_bytes).hexdigest() != metadata["sha256"]
        or (is_release and metadata.get("size") != len(registry_raw))
        or (not is_release and metadata.get("bytes") != len(digest_bytes))
    ):
        raise SemanticRoutingError("semantic applicability registry integrity check failed")
    try:
        payload = json.loads(registry_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SemanticRoutingError("semantic applicability registry is invalid") from exc
    if (
        not isinstance(payload, Mapping)
        or set(payload) != {"schema_version", "model_version", "rules"}
        or payload.get("schema_version") != SEMANTIC_APPLICABILITY_REGISTRY_VERSION
        or payload.get("model_version") != SEMANTIC_DOMAIN_MODEL_VERSION
    ):
        raise SemanticRoutingError("semantic applicability registry version is invalid")
    raw_rules = payload.get("rules")
    if not isinstance(raw_rules, list) or len(raw_rules) > MAX_REGISTRY_RULES:
        raise SemanticRoutingError("semantic applicability registry is invalid or unbounded")
    rules: list[_RegistryRule] = []
    identities: set[tuple[str, str, str, tuple[str, ...]]] = set()
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, Mapping):
            raise SemanticRoutingError("semantic applicability registry rule is invalid")
        if set(raw_rule) != {
            "skill_name", "metadata_fingerprint", "skill_content_sha256",
            "source_scopes", "applicability",
        }:
            raise SemanticRoutingError("semantic applicability registry rule schema is invalid")
        name = raw_rule.get("skill_name")
        fingerprint = raw_rule.get("metadata_fingerprint")
        content_sha256 = raw_rule.get("skill_content_sha256")
        scopes = raw_rule.get("source_scopes")
        applicability_raw = raw_rule.get("applicability")
        if (
            not isinstance(name, str) or not name or len(name) > 128
            or not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint)
            or not isinstance(content_sha256, str) or not SHA256_RE.fullmatch(content_sha256)
            or not isinstance(scopes, list) or not scopes or len(scopes) > 8
            or not all(isinstance(item, str) and item and len(item) <= 64 for item in scopes)
            or len(scopes) != len(set(scopes))
            or not isinstance(applicability_raw, Mapping)
        ):
            raise SemanticRoutingError("semantic applicability registry rule identity is invalid")
        if set(applicability_raw) != {
            "supported_domains", "incompatible_domains", "supported_task_kinds",
            "required_context", "artifact_families", "provenance",
            "applicability_version",
        }:
            raise SemanticRoutingError("semantic applicability rule schema is invalid")
        provenance = applicability_raw.get("provenance")
        applicability_version = applicability_raw.get("applicability_version")
        if not isinstance(provenance, str) or not isinstance(applicability_version, str):
            raise SemanticRoutingError("semantic applicability rule metadata is invalid")
        applicability = make_trusted_applicability(
            supported_domains=applicability_raw.get("supported_domains", ()),
            incompatible_domains=applicability_raw.get("incompatible_domains", ()),
            supported_task_kinds=applicability_raw.get("supported_task_kinds", ()),
            required_context=applicability_raw.get("required_context", ()),
            artifact_families=applicability_raw.get("artifact_families", ()),
            provenance=provenance,
            applicability_version=applicability_version,
        )
        identity = (name.casefold(), fingerprint, content_sha256, tuple(sorted(scopes)))
        if identity in identities:
            raise SemanticRoutingError("semantic applicability registry contains a duplicate identity")
        identities.add(identity)
        rules.append(_RegistryRule(name, fingerprint, content_sha256, tuple(scopes), applicability))
    return TrustedApplicabilityRegistry(tuple(rules), hashlib.sha256(registry_raw).hexdigest())


def resolve_trusted_applicability(
    record: Mapping[str, Any], registry: TrustedApplicabilityRegistry | None,
) -> TrustedSkillApplicability | None:
    # Discovery cannot create Python dataclass instances from frontmatter or
    # Scout metadata, so this path is reserved for Nexus-owned mappings/tests.
    direct = record.get("_nexus_trusted_applicability")
    if isinstance(direct, TrustedSkillApplicability):
        return direct
    return registry.resolve(record) if registry is not None else None
