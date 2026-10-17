"""Bounded, additive V1.2 capability planning.

This module deliberately does not replace the V1.1 discovery/router/execution
path.  It composes V1.1's metadata-only catalog and selected-Skill loader into
an explicit, auditable planning flow.  It has no model client, no network
access, no agent delegation, and no automatic command execution.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import os
from pathlib import Path
import re
from typing import Any, Callable, Iterable, Mapping
from uuid import uuid4

from .common import sha256_text, tokenize, utc_now, write_json
from .execution import load_selected_skills
from .reference_research import ReferenceResearchPlan, reference_research_plan
from .reusable_references import LibrarySnapshot, discover_references
from .semantic_domains import (
    CAPABILITY_NOT_COVERED,
    DOMAIN_EVIDENCE_MISSING,
    DOMAIN_MATCH,
    MINIMAL_SET_REDUNDANT,
    SEMANTIC_DOMAIN_MODEL_VERSION,
    SHA256_RE,
    SKILL_INTEGRITY_CHANGED,
    SKILL_INTEGRITY_EVIDENCE_MISSING,
    ApplicabilityDecision,
    SemanticRoutingError,
    TrustedApplicabilityRegistry,
    DOMAIN_TO_CAPABILITY,
    evaluate_applicability,
    load_trusted_applicability_registry,
    resolve_trusted_applicability,
    semantic_task_model,
)


SOFT_CONTEXT_FILES = 8
SOFT_CONTEXT_BYTES = 64 * 1024
HARD_CONTEXT_FILES = 50
HARD_CONTEXT_BYTES = 512 * 1024
SECRET_NAME_RE = re.compile(r"(^|[._-])(secret|token|password|credential|private|oauth)([._-]|$)", re.I)
EXPLICIT_PATH_RE = re.compile(r"(?<![\w.])(?:[\w.-]+[\\/])+[\w.-]+|(?<![\w.])[\w.-]+\.[a-z0-9]{1,12}(?![\w.])", re.I)

CAPABILITY_TERMS: dict[str, set[str]] = {
    "presentation": {"presentation", "powerpoint", "ppt", "pptx", "slides", "deck"},
    "spreadsheet": {"excel", "workbook", "spreadsheet", "xlsx", "xls", "formula", "formulas"},
    "document": {"document", "docx", "word", "memo", "letter"},
    "pdf": {"pdf"},
    "research": {"research", "evidence", "citation", "citations", "fact", "facts", "source", "sources", "verify", "verification"},
    "frontend": {"frontend", "react", "ui", "ux", "dashboard", "css", "html", "accessibility"},
    "backend": {"backend", "api", "endpoint", "server", "service", "http", "500", "database"},
    "testing": {"test", "tests", "testing", "regression", "reproduce", "reproduction", "validate", "validation", "qa"},
    "security": {"security", "secure", "authorization", "authz", "access", "cross-user", "cross user", "tenant", "invoice", "vulnerability", "vulnerabilities", "injection"},
}
# Resource identity terms are intentionally stricter than task-understanding
# terms.  A workflow that happens to say it can "verify" something must not
# become a research workflow, and a slide Skill that can export PDF must not
# become the canonical PDF workflow.
RESOURCE_CAPABILITY_TERMS: dict[str, set[str]] = {
    "presentation": {"presentation", "presentations", "powerpoint", "ppt", "pptx", "slides", "slide", "deck"},
    "spreadsheet": {"excel", "workbook", "spreadsheet", "spreadsheets", "xlsx", "xls"},
    "document": {"document", "documents", "docx", "word", "memo", "letter"},
    "pdf": {"pdf"},
    "research": {"research", "evidence", "citation", "citations", "fact", "facts", "source", "sources"},
    "frontend": {"frontend", "react", "ui", "ux", "accessibility", "css", "html"},
    "backend": {"backend", "api", "endpoint", "server", "service", "debug", "diagnose", "http"},
    "testing": {"test", "tests", "testing", "regression", "reproduce", "reproduction", "qa"},
    "security": {"security", "secure", "authorization", "authz", "appsec", "vulnerability"},
}
ARTIFACT_CAPABILITIES = {"presentation", "spreadsheet", "document", "pdf"}
INFORMATIONAL_QUERY_PREFIXES = ("what is ", "what are ", "what does ", "define ", "explain ")
SUBSTANTIVE_ACTION_TERMS = {
    "create", "prepare", "write", "build", "generate", "edit", "diagnose", "debug", "fix",
    "audit", "review", "plan", "verify", "validate", "test", "testing", "analyze", "analyse",
}
ACADEMIC_PLANNING_TERMS = {"assignment", "coursework", "rubric", "lecturer"}
RULE_FILENAMES = {"agents.md", "project_rules.md", "decisions.md", "frozen-decisions.md"}
CONTEXT_FILENAMES = (
    "AGENTS.md", "PROJECT_RULES.md", "DECISIONS.md", "FROZEN-DECISIONS.md", "README.md", "SKILL.md",
    "pyproject.toml", "package.json", "requirements.txt", "requirements-dev.txt", "setup.cfg", "tox.ini",
    "pytest.ini", "MANIFEST.json", "docs/architecture.md", "docs/decisions.md",
)


def _identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "general"


@dataclass
class TaskProfile:
    original_task: str
    primary_objective: str
    task_type: str = "general"
    domain_type: str = "general"
    deliverable: str | None = None
    artifact_type: str | None = None
    required_operations: list[str] = field(default_factory=list)
    explicit_constraints: list[str] = field(default_factory=list)
    inferred_constraints: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    validation_expectations: list[str] = field(default_factory=list)
    output_format_constraints: list[str] = field(default_factory=list)
    risk_relevance: str = "low"
    ambiguities: list[str] = field(default_factory=list)
    confidence: float = 0.5
    negative_evidence: list[str] = field(default_factory=list)
    extraction_source: str = "fallback_parser"
    semantic_domain_model_version: str = SEMANTIC_DOMAIN_MODEL_VERSION
    primary_domain: str = "general"
    secondary_domains: list[str] = field(default_factory=list)
    incompatible_domains: list[str] = field(default_factory=list)
    semantic_task_kinds: list[str] = field(default_factory=list)
    context_kinds: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContextItem:
    path: str
    kind: str
    trust: str
    sha256: str
    bytes: int
    reason: str
    content: str = field(repr=False, default="")

    def to_dict(self, include_content: bool = False) -> dict[str, Any]:
        result = asdict(self)
        if not include_content:
            result.pop("content", None)
        return result


@dataclass
class ProjectContext:
    root: str
    items: list[ContextItem] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    soft_file_budget: int = SOFT_CONTEXT_FILES
    soft_byte_budget: int = SOFT_CONTEXT_BYTES
    hard_file_ceiling: int = HARD_CONTEXT_FILES
    hard_byte_ceiling: int = HARD_CONTEXT_BYTES
    expansions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "items": [item.to_dict() for item in self.items],
            "skipped": self.skipped,
            "soft_file_budget": self.soft_file_budget,
            "soft_byte_budget": self.soft_byte_budget,
            "hard_file_ceiling": self.hard_file_ceiling,
            "hard_byte_ceiling": self.hard_byte_ceiling,
            "expansions": self.expansions,
        }


@dataclass
class Rule:
    rule_id: str
    source: str
    scope: str
    priority: int
    enforcement: str
    target: str
    value: str
    confidence: float = 1.0
    conflict_status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CapabilityRequirement:
    capability: str
    required: bool
    reason: str
    dependencies: list[str] = field(default_factory=list)
    ordering_constraints: list[str] = field(default_factory=list)
    validation_requirement: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceCandidate:
    resource_id: str
    name: str
    resource_type: str
    path: str
    coverage: list[str]
    score: float
    score_signals: list[str]
    trust: str
    provenance: dict[str, Any]
    runtime_compatibility: str
    status: str
    record: dict[str, Any] = field(repr=False, default_factory=dict)
    domain_coverage: list[str] = field(default_factory=list)
    applicability_evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "path": self.path,
            "coverage": self.coverage,
            "score": self.score,
            "score_signals": self.score_signals,
            "trust": self.trust,
            "provenance": self.provenance,
            "runtime_compatibility": self.runtime_compatibility,
            "status": self.status,
            "domain_coverage": self.domain_coverage,
            "applicability_evidence": self.applicability_evidence,
        }


@dataclass
class ExecutionStep:
    step_id: str
    capability: str
    selected_resource_id: str | None
    selected_resource_name: str | None
    resource_type: str
    reason: str
    dependencies: list[str]
    expected_output: str
    validation: list[str]
    fallback: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationPlan:
    checks: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {"checks": self.checks}


@dataclass
class DecisionEvidence:
    event: str
    detail: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReplanResult:
    status: str
    reason: str
    attempt: int
    plan: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reason": self.reason, "attempt": self.attempt, "plan": self.plan}


@dataclass
class ExecutionPlan:
    plan_id: str
    created_at_utc: str
    task_profile: TaskProfile
    project_context: ProjectContext
    rules: list[Rule]
    requirements: list[CapabilityRequirement]
    candidates: list[ResourceCandidate]
    selected: list[ResourceCandidate]
    rejected: list[dict[str, Any]]
    external_resources: list[dict[str, Any]]
    advisory_agents: list[ResourceCandidate]
    validation_plan: ValidationPlan
    steps: list[ExecutionStep]
    evidence: list[DecisionEvidence]
    fallback: dict[str, Any]
    reference_research: ReferenceResearchPlan
    replan_attempt: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "2.0",
            "plan_id": self.plan_id,
            "created_at_utc": self.created_at_utc,
            "task_profile": self.task_profile.to_dict(),
            "project_context": self.project_context.to_dict(),
            "rules": [rule.to_dict() for rule in self.rules],
            "requirements": [item.to_dict() for item in self.requirements],
            "candidates": [item.to_dict() for item in self.candidates],
            "selected": [item.to_dict() for item in self.selected],
            "rejected": self.rejected,
            "external_resources": self.external_resources,
            "advisory_agents": [item.to_dict() for item in self.advisory_agents],
            "validation_plan": self.validation_plan.to_dict(),
            "steps": [item.to_dict() for item in self.steps],
            "evidence": [item.to_dict() for item in self.evidence],
            "fallback": self.fallback,
            "reference_research": self.reference_research.to_dict(),
            "replan_attempt": self.replan_attempt,
        }


def validate_task_profile(value: Mapping[str, Any]) -> tuple[TaskProfile | None, list[str]]:
    errors: list[str] = []
    original = value.get("original_task")
    objective = value.get("primary_objective")
    if not isinstance(original, str) or not original.strip():
        errors.append("original_task must be a non-empty string")
    if not isinstance(objective, str) or not objective.strip():
        errors.append("primary_objective must be a non-empty string")
    for name in (
        "required_operations", "explicit_constraints", "inferred_constraints",
        "required_capabilities", "validation_expectations", "ambiguities",
        "negative_evidence", "secondary_domains", "incompatible_domains",
        "semantic_task_kinds", "context_kinds",
    ):
        if name in value and (not isinstance(value[name], list) or not all(isinstance(item, str) for item in value[name])):
            errors.append(f"{name} must be a list of strings")
    confidence = value.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        errors.append("confidence must be a number from 0 to 1")
    if errors:
        return None, errors
    permitted = {field.name for field in TaskProfile.__dataclass_fields__.values()}
    normalized = {key: value[key] for key in value if key in permitted}
    return TaskProfile(**normalized), []


def _fallback_task_profile(task: str) -> TaskProfile:
    raw = task.strip()
    tokens = tokenize(raw)
    lowered = raw.lower()
    information_only = lowered.startswith(INFORMATIONAL_QUERY_PREFIXES) and not bool(tokens & SUBSTANTIVE_ACTION_TERMS)
    repair = bool(tokens & {"fix", "debug", "diagnose", "error", "exception", "failure", "failed", "500"})
    artifact_type: str | None = None
    if not repair and not information_only:
        for artifact, terms in (("presentation", CAPABILITY_TERMS["presentation"]), ("spreadsheet", CAPABILITY_TERMS["spreadsheet"]), ("document", CAPABILITY_TERMS["document"]), ("pdf", CAPABILITY_TERMS["pdf"])):
            if tokens & terms:
                artifact_type = artifact
                break
    task_type = "general"
    if tokens & CAPABILITY_TERMS["backend"] and repair:
        task_type = "backend"
    elif tokens & CAPABILITY_TERMS["frontend"]:
        task_type = "frontend"
    elif not information_only and tokens & ({"research", "evidence", "citation", "citations", "fact", "facts", "source", "sources"} | ACADEMIC_PLANNING_TERMS):
        task_type = "research"
    elif artifact_type:
        task_type = "artifact"
    operations: list[str] = []
    if repair:
        operations.append("repair")
    if tokens & {"create", "prepare", "write", "build", "generate"}:
        operations.append("create")
    if not information_only and tokens & (CAPABILITY_TERMS["research"] | ACADEMIC_PLANNING_TERMS):
        operations.append("research")
    if tokens & CAPABILITY_TERMS["testing"]:
        operations.append("test")
    if tokens & {"validate", "verify", "inspect", "review", "formulas", "formula"}:
        operations.append("validate")
    if not operations:
        operations.append("analyse")
    explicit: list[str] = []
    if "do not install" in lowered or "no install" in lowered:
        explicit.append("no_install")
    if "offline" in lowered or "no network" in lowered:
        explicit.append("no_network")
    if "do not publish" in lowered or "no external write" in lowered or re.search(r"\bdo not\b[^.;]*\bpublish\b", lowered):
        explicit.append("no_external_write")
    capabilities: list[str] = []
    if artifact_type:
        capabilities.append(artifact_type)
    if task_type in {"backend", "frontend", "research"}:
        capabilities.append(task_type)
    if "test" in operations and (task_type == "backend" or "security" in capabilities):
        capabilities.append("testing")
    if task_type == "research" and artifact_type:
        capabilities = ["research", artifact_type]
    security_evidence = {"authorization", "authz", "cross-user", "tenant", "invoice", "vulnerability", "vulnerabilities", "injection"}
    if not information_only and (tokens & security_evidence or "another user's" in lowered):
        capabilities.append("security")
    if "test" in operations and "security" in capabilities and "testing" not in capabilities:
        capabilities.append("testing")
    capabilities = list(dict.fromkeys(capabilities))
    negative: list[str] = []
    if information_only:
        negative.append("informational query has no substantive deliverable or capability-planning requirement")
    if repair and any(term in tokens for term in CAPABILITY_TERMS["presentation"] | CAPABILITY_TERMS["document"] | CAPABILITY_TERMS["spreadsheet"] | CAPABILITY_TERMS["pdf"]):
        negative.append("artifact terminology appears inside a repair request and is not an artifact-production requirement")
    if task_type != "frontend":
        negative.append("frontend/UI resources are not required")
    if "security" not in capabilities:
        negative.append("security review is not required without explicit security or cross-user access evidence")
    validations = ["plan_coverage"]
    if "testing" in capabilities:
        validations.append("targeted_regression_test")
    if artifact_type:
        validations.append(f"{artifact_type}_integrity")
    if task_type == "research":
        validations.append("evidence_ledger")
    output_format_constraints = _infer_output_format_constraints(tokens, artifact_type)
    return TaskProfile(
        original_task=raw,
        primary_objective=raw,
        task_type=task_type,
        domain_type=task_type,
        deliverable=artifact_type,
        artifact_type=artifact_type,
        required_operations=operations,
        explicit_constraints=explicit,
        inferred_constraints=["no_automatic_install", "no_automatic_external_write"],
        required_capabilities=capabilities,
        validation_expectations=validations,
        output_format_constraints=output_format_constraints,
        risk_relevance="high" if "security" in capabilities else "medium" if repair else "low",
        confidence=0.55,
        negative_evidence=negative,
        extraction_source="fallback_parser",
    )


def _infer_output_format_constraints(tokens: set[str], artifact_type: str | None) -> list[str]:
    """Extract portable artifact constraints without adding new public tags.

    A request for a PowerPoint/PPTX artifact names a native file family.  When
    it also asks for editing, that is a required property of the deliverable,
    not merely a generic presentation preference.  Keep this representation
    internal to V1.2 planning so existing discovery tags and R1/R2 envelopes
    remain unchanged.
    """
    constraints: list[str] = []
    if artifact_type == "presentation" and tokens & {"powerpoint", "pptx"}:
        constraints.append("native_pptx")
        if tokens & {"editable", "edit", "editing"}:
            constraints.append("editable")
    return constraints


def _apply_output_format_constraints(profile: TaskProfile) -> TaskProfile:
    """Backfill deterministic constraints for both fallback and semantic profiles."""
    inferred = _infer_output_format_constraints(tokenize(profile.original_task), profile.artifact_type)
    profile.output_format_constraints = list(dict.fromkeys([
        *profile.output_format_constraints,
        *inferred,
    ]))
    return profile


def _apply_semantic_task_model(profile: TaskProfile) -> TaskProfile:
    """Bind every extractor result to the deterministic Slice 3A model.

    Optional structured extraction may improve the older V2 fields, but it
    cannot manufacture authoritative semantic domains.  The original task is
    always reclassified locally and the ambiguous ``document`` capability is
    removed unless the task names a genuine document artifact.
    """
    model = semantic_task_model(profile.original_task)
    profile.semantic_domain_model_version = model.schema_version
    profile.primary_domain = model.primary_domain
    profile.secondary_domains = list(model.secondary_domains)
    profile.incompatible_domains = list(model.incompatible_domains)
    profile.semantic_task_kinds = list(model.task_kinds)
    profile.context_kinds = list(model.context_kinds)
    profile.domain_type = model.primary_domain
    if model.primary_domain in ARTIFACT_CAPABILITIES:
        profile.task_type = "artifact"
    elif model.primary_domain == "backend_repair":
        profile.task_type = "backend"
    elif model.primary_domain in {"frontend_implementation", "visual_design_qa"}:
        profile.task_type = "frontend"
    elif model.primary_domain in {
        "product_ux_research", "software_research", "architecture_review",
        "security_review", "general_research",
    }:
        profile.task_type = "research"
    elif model.primary_domain == "general":
        profile.task_type = "general"

    artifacts = list(model.artifact_families)
    if profile.artifact_type in ARTIFACT_CAPABILITIES and profile.artifact_type not in artifacts:
        profile.required_capabilities = [item for item in profile.required_capabilities if item != profile.artifact_type]
        if profile.deliverable == profile.artifact_type:
            profile.deliverable = None
        profile.artifact_type = None
    if artifacts:
        profile.artifact_type = artifacts[0]
        profile.deliverable = profile.deliverable or artifacts[0]

    semantic_capabilities = [
        DOMAIN_TO_CAPABILITY[domain]
        for domain in model.required_domains
        if DOMAIN_TO_CAPABILITY.get(domain) != "general"
    ]
    modeled_capabilities = set(DOMAIN_TO_CAPABILITY.values()) - {"general"}
    unmodeled_capabilities = [
        item for item in profile.required_capabilities
        if item not in modeled_capabilities
    ]
    profile.required_capabilities = list(dict.fromkeys([
        *semantic_capabilities,
        *unmodeled_capabilities,
    ]))
    if not model.required_domains and profile.required_capabilities == ["document"]:
        profile.required_capabilities = []
    return profile


def task_profile_for(task: str, semantic_extractor: Callable[[str], Mapping[str, Any]] | None = None) -> tuple[TaskProfile, list[DecisionEvidence]]:
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be a non-empty string")
    evidence: list[DecisionEvidence] = []
    if semantic_extractor is not None:
        try:
            proposed = dict(semantic_extractor(task))
            # The optional extractor may structure the task, but it cannot
            # replace the user-authored text that drives deterministic domains.
            proposed["original_task"] = task
            proposed.setdefault("primary_objective", task)
            proposed["extraction_source"] = "codex_structured_semantic_extraction"
            profile, errors = validate_task_profile(proposed)
            if profile is not None:
                profile = _apply_output_format_constraints(_apply_semantic_task_model(profile))
                evidence.append(DecisionEvidence("task_profile", "accepted schema-valid Codex structured semantic extraction", {"source": profile.extraction_source}))
                return profile, evidence
            evidence.append(DecisionEvidence("task_profile", "rejected invalid structured extraction; used conservative fallback", {"errors": errors}))
        except Exception as exc:  # boundary: extractor is an optional runtime integration
            evidence.append(DecisionEvidence("task_profile", "structured extraction unavailable; used conservative fallback", {"error": type(exc).__name__}))
    profile = _apply_output_format_constraints(_apply_semantic_task_model(_fallback_task_profile(task)))
    evidence.append(DecisionEvidence("task_profile", "used minimal deterministic fallback parser", {"source": profile.extraction_source}))
    return profile, evidence


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _context_candidates(root: Path, task: str) -> list[tuple[Path, str, str]]:
    seen: set[Path] = set()
    result: list[tuple[Path, str, str]] = []
    for name in CONTEXT_FILENAMES:
        path = root / name
        if path.exists() and path.is_file():
            kind = "project_rule" if path.name.casefold() in RULE_FILENAMES else "project_evidence"
            reason = "governing project instruction" if kind == "project_rule" else "known project context"
            seen.add(path.resolve())
            result.append((path, kind, reason))
    for raw in EXPLICIT_PATH_RE.findall(task):
        candidate = (root / raw.replace("\\", os.sep)).resolve()
        if candidate.exists() and candidate.is_file() and _inside(root, candidate) and candidate not in seen:
            seen.add(candidate)
            result.append((candidate, "explicit_task_file", "explicitly named by task"))
    return result


def discover_project_context(
    project_root: Path,
    task: str,
    *,
    soft_file_budget: int = SOFT_CONTEXT_FILES,
    soft_byte_budget: int = SOFT_CONTEXT_BYTES,
    hard_file_ceiling: int = HARD_CONTEXT_FILES,
    hard_byte_ceiling: int = HARD_CONTEXT_BYTES,
) -> ProjectContext:
    root = project_root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root is not a directory: {project_root}")
    if soft_file_budget < 1 or hard_file_ceiling < soft_file_budget or soft_byte_budget < 1 or hard_byte_ceiling < soft_byte_budget:
        raise ValueError("context budgets require positive soft defaults within hard ceilings")
    context = ProjectContext(str(root), soft_file_budget=soft_file_budget, soft_byte_budget=soft_byte_budget, hard_file_ceiling=hard_file_ceiling, hard_byte_ceiling=hard_byte_ceiling)
    for raw in EXPLICIT_PATH_RE.findall(task):
        requested = (root / raw.replace("\\", os.sep)).resolve()
        if requested.exists() and not _inside(root, requested):
            context.skipped.append({"path": raw, "reason": "explicit path escapes project root"})
    total = 0
    for path, kind, reason in _context_candidates(root, task):
        relative = str(path.resolve().relative_to(root))
        if path.is_symlink() and not _inside(root, path):
            context.skipped.append({"path": relative, "reason": "symlink escapes project root"})
            continue
        if SECRET_NAME_RE.search(path.name):
            context.skipped.append({"path": relative, "reason": "secret-looking file name excluded"})
            continue
        try:
            size = path.stat().st_size
        except OSError:
            context.skipped.append({"path": relative, "reason": "unreadable file"})
            continue
        if size > hard_byte_ceiling:
            context.skipped.append({"path": relative, "reason": "file exceeds hard context byte ceiling"})
            continue
        if len(context.items) >= hard_file_ceiling or total + size > hard_byte_ceiling:
            context.skipped.append({"path": relative, "reason": "hard context ceiling reached"})
            continue
        try:
            raw = path.read_bytes()
            if b"\0" in raw[:4096]:
                context.skipped.append({"path": relative, "reason": "binary file excluded"})
                continue
            content = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            context.skipped.append({"path": relative, "reason": "non-UTF-8 or unreadable file excluded"})
            continue
        needs_expansion = len(context.items) >= soft_file_budget or total + size > soft_byte_budget
        if needs_expansion:
            context.expansions.append({"path": relative, "reason": reason, "files_before": len(context.items), "bytes_before": total, "soft_file_budget": soft_file_budget, "soft_byte_budget": soft_byte_budget})
        trust = "project_instruction" if kind == "project_rule" else "project_evidence"
        context.items.append(ContextItem(relative, kind, trust, sha256_text(content), size, reason, content))
        total += size
    return context


def _rule_from_line(line: str, source: str, priority: int) -> Rule | None:
    normalized = " ".join(line.strip().split())
    lowered = normalized.casefold()
    if not normalized or normalized.startswith("#"):
        return None
    prohibited = re.search(r"\b(must not|do not|don't|never|prohibit(?:ed)?)\b\s+(.+)", lowered)
    required = re.search(r"\b(must|require(?:d)?|always)\b\s+(.+)", lowered)
    if prohibited:
        target = _identifier(re.sub(r"^(use|select|load)\s+", "", prohibited.group(2)))
        return Rule(f"{_identifier(source)}_prohibit_{target}", source, "project", priority, "prohibit", target, "false")
    if required:
        target = _identifier(required.group(2))
        return Rule(f"{_identifier(source)}_require_{target}", source, "project", priority, "require", target, "true")
    return None


def extract_rules(profile: TaskProfile, context: ProjectContext, user_requirements: Iterable[str] = ()) -> tuple[list[Rule], list[dict[str, Any]]]:
    rules: list[Rule] = [
        Rule("system_no_auto_install", "system", "system", 100, "prohibit", "automatic_install", "false"),
        Rule("system_no_auto_delegation", "system", "system", 100, "prohibit", "automatic_agent_delegation", "false"),
    ]
    for constraint in [*profile.explicit_constraints, *user_requirements]:
        target = _identifier(constraint.removeprefix("no_"))
        enforcement = "prohibit" if constraint.startswith("no_") else "require"
        rules.append(Rule(f"user_{enforcement}_{target}", "current_user", "user", 90, enforcement, target, "false" if enforcement == "prohibit" else "true"))
    for item in context.items:
        if item.kind != "project_rule":
            continue
        for line in item.content.splitlines():
            rule = _rule_from_line(line, item.path, 80)
            if rule:
                rules.append(rule)
    conflicts: list[dict[str, Any]] = []
    by_target: dict[str, list[Rule]] = {}
    for rule in rules:
        by_target.setdefault(rule.target, []).append(rule)
    for target, group in by_target.items():
        highest = max(item.priority for item in group)
        leaders = [item for item in group if item.priority == highest]
        enforcement = {item.enforcement for item in leaders}
        if len(enforcement) > 1:
            for item in leaders:
                item.conflict_status = "conflict"
            conflicts.append({"target": target, "sources": [item.source for item in leaders], "reason": "equal-priority incompatible rules"})
        else:
            for item in group:
                if item.priority < highest:
                    item.conflict_status = "overridden"
    return sorted(rules, key=lambda item: (-item.priority, item.rule_id)), conflicts


def capability_requirements(profile: TaskProfile, rules: list[Rule]) -> list[CapabilityRequirement]:
    requested = list(profile.required_capabilities)
    if profile.artifact_type and profile.artifact_type not in requested:
        requested.append(profile.artifact_type)
    if profile.task_type in {"backend", "frontend", "research"} and profile.task_type not in requested:
        requested.append(profile.task_type)
    if not requested:
        requested.append("general")
    requirements: list[CapabilityRequirement] = []
    for capability in dict.fromkeys(requested):
        dependencies: list[str] = []
        ordering: list[str] = []
        if capability == "testing" and "backend" in requested:
            dependencies.append("backend")
            ordering.append("after:backend")
        if capability == "security" and "backend" in requested:
            dependencies.append("backend")
            ordering.append("after:backend")
        if capability in {"document", "pdf", "presentation", "spreadsheet"} and "research" in requested:
            dependencies.append("research")
            ordering.append("after:research")
        validation = f"{capability}_validation" if capability in ARTIFACT_CAPABILITIES else None
        requirements.append(CapabilityRequirement(capability, True, f"TaskProfile requires {capability}", dependencies, ordering, validation))
    return requirements


def _candidate_tokens(record: Mapping[str, Any]) -> set[str]:
    return tokenize(" ".join([str(record.get("name", "")), str(record.get("description", "")), " ".join(record.get("tags", [])), str(record.get("path", ""))]))


def _resource_identity_tokens(record: Mapping[str, Any]) -> set[str]:
    """Stable identity used for hard coverage, excluding inferred broad tags.

    V1 discovery tags intentionally make broad catalog discovery convenient, but
    they are inferred from descriptive prose and are therefore not strong enough
    to prove a V2 required capability.  Future Skills may declare explicit
    ``metadata.capabilities``; until then their name is the conservative source.
    """
    metadata = record.get("metadata", {})
    declared = metadata.get("capabilities", []) if isinstance(metadata, Mapping) else []
    if isinstance(metadata, Mapping) and not declared and isinstance(metadata.get("metadata"), Mapping):
        declared = metadata["metadata"].get("capabilities", [])
    if isinstance(declared, str):
        declared = [declared]
    return tokenize(" ".join([str(record.get("name", "")), *[str(item) for item in declared if isinstance(item, str)]]))


def _required_semantic_domains(profile: TaskProfile) -> tuple[str, ...]:
    return tuple(
        domain for domain in (profile.primary_domain, *profile.secondary_domains)
        if domain != "general"
    )


def _coverage_for_domains(
    decision: ApplicabilityDecision, requirements: list[CapabilityRequirement],
) -> list[str]:
    required_capabilities = {item.capability for item in requirements if item.required}
    coverage: list[str] = []
    for domain in decision.matched_domains:
        capability = DOMAIN_TO_CAPABILITY.get(domain)
        if capability in required_capabilities and capability not in coverage:
            coverage.append(capability)
    return coverage


def _supports_native_pptx(record: Mapping[str, Any], *, require_editable: bool) -> bool:
    """Return whether a Skill explicitly describes native PowerPoint/PPTX work.

    This is deliberately based on the Skill's own name/description/declared
    metadata, not broad discovery tags.  A Canva or web/HTML presentation may
    be a good generic presentation workflow, but it cannot satisfy a native
    PPTX requirement merely because it is tagged ``presentation``.
    """
    tokens = _candidate_tokens(record)
    if not tokens & {"powerpoint", "pptx"}:
        return False
    if tokens & {"canva", "html", "web"}:
        return False
    return not require_editable or bool(tokens & {"editable", "edit", "editing"})


def _eligible_skill(record: Mapping[str, Any], profile: TaskProfile, rules: list[Rule]) -> tuple[bool, str | None]:
    if record.get("status") != "available":
        return False, f"not executable: {record.get('status')}"
    skill_path = Path(str(record.get("skill_md_path", "")))
    # A package's root SKILL.md is the runtime entry point.  Nested SKILL.md
    # files below it are supporting instructions/fixtures, not peer candidates.
    try:
        for parent in list(skill_path.parents)[1:6]:
            if (parent / "SKILL.md").exists():
                return False, "nested SKILL.md belongs to an enclosing Skill package"
    except OSError:
        return False, "unable to verify Skill package boundary"
    if record.get("duplicate_role") in {"shadowed", "conflict"}:
        return False, f"duplicate is {record.get('duplicate_role')}"
    name = str(record.get("name", "")).casefold()
    canonical_name = _identifier(name)
    for rule in rules:
        if rule.conflict_status == "active" and rule.enforcement == "prohibit" and rule.target == canonical_name:
            return False, f"prohibited by {rule.source}"
    if name == "excel-live-control" and "live" not in tokenize(profile.original_task):
        return False, "excel-live-control requires an explicit live Excel-session task"
    if name.startswith("gsap-") and not (tokenize(profile.original_task) & {"animation", "animate", "motion", "scroll", "transition", "timeline", "tween"}):
        return False, "GSAP requires an explicit frontend animation/motion task"
    if name.startswith("artifact-template-") and "template" not in tokenize(profile.original_task):
        return False, "artifact template requires an explicit template request"
    output_constraints = set(profile.output_format_constraints)
    is_presentation_candidate = bool(_resource_identity_tokens(record) & RESOURCE_CAPABILITY_TERMS["presentation"])
    if "native_pptx" in output_constraints and is_presentation_candidate and not _supports_native_pptx(
        record, require_editable="editable" in output_constraints,
    ):
        return False, "native editable PPTX requirement is not explicitly supported by this Skill"
    if "threat-model" in name and "threat_model" not in profile.required_operations and "threat" not in tokenize(profile.original_task):
        return False, "threat-model workflow requires an explicit threat-model task"
    if "security" in name and "security" not in profile.required_capabilities:
        return False, "security workflow rejected by negative evidence"
    if any(rule.conflict_status == "conflict" for rule in rules):
        return False, "unresolved higher-priority rule conflict"
    return True, None


def rank_resources(
    index: Mapping[str, Any],
    profile: TaskProfile,
    requirements: list[CapabilityRequirement],
    rules: list[Rule],
    excluded_ids: set[str] | None = None,
    *,
    applicability_registry: TrustedApplicabilityRegistry | None = None,
) -> tuple[list[ResourceCandidate], list[dict[str, Any]]]:
    excluded_ids = excluded_ids or set()
    candidates: list[ResourceCandidate] = []
    rejected: list[dict[str, Any]] = []
    task_tokens = tokenize(profile.original_task)
    registry_error = False
    if applicability_registry is None:
        try:
            applicability_registry = load_trusted_applicability_registry()
        except SemanticRoutingError:
            # Registry failure is deliberately non-executable and redacted.
            # Nexus can still use its honest native fallback.
            registry_error = True
            applicability_registry = None
    for record in index.get("skills", []):
        if record.get("id") in excluded_ids:
            rejected.append({"name": record.get("name"), "reason": "excluded by bounded re-plan", "reason_code": DOMAIN_EVIDENCE_MISSING})
            continue
        eligible, reason = _eligible_skill(record, profile, rules)
        if not eligible:
            rejected.append({"name": record.get("name"), "reason": reason})
            continue
        content_sha256 = record.get("content_sha256")
        if not isinstance(content_sha256, str) or not SHA256_RE.fullmatch(content_sha256.casefold()):
            rejected.append({
                "name": record.get("name"),
                "reason": "stable Skill content-integrity evidence is missing",
                "reason_code": SKILL_INTEGRITY_EVIDENCE_MISSING,
            })
            continue
        try:
            applicability = resolve_trusted_applicability(record, applicability_registry)
        except SemanticRoutingError:
            applicability = None
        if applicability is None:
            rejected.append({
                "name": record.get("name"),
                "reason": "trusted semantic applicability evidence is missing",
                "reason_code": DOMAIN_EVIDENCE_MISSING,
                "registry_status": "integrity_unavailable" if registry_error else "no_matching_rule",
            })
            continue
        model = semantic_task_model(profile.original_task)
        decision = evaluate_applicability(model, applicability)
        if not decision.allowed:
            rejected.append({
                "name": record.get("name"),
                "reason": "Skill is outside the task's trusted semantic applicability",
                "reason_code": decision.reason_code,
                "matched_domains": list(decision.matched_domains),
            })
            continue
        coverage = _coverage_for_domains(decision, requirements)
        if not coverage and decision.matched_domains:
            rejected.append({
                "name": record.get("name"),
                "reason": "semantic domain match does not cover a required capability",
                "reason_code": DOMAIN_EVIDENCE_MISSING,
            })
            continue
        tokens = _candidate_tokens(record)
        signals: list[str] = []
        score = float(len(coverage) * 100 + len(decision.matched_domains) * 120)
        signals.append(f"{DOMAIN_MATCH}: {', '.join(decision.matched_domains)}")
        signals.append(f"exact capability coverage: {', '.join(coverage)}")
        overlap = task_tokens & tokens
        if overlap:
            score += len(overlap) * 8
            signals.append(f"TaskProfile relevance: {', '.join(sorted(overlap))}")
        if profile.artifact_type in coverage:
            score += 25
            signals.append("artifact match")
        if "native_pptx" in profile.output_format_constraints and "presentation" in coverage:
            score += 40
            signals.append("native PPTX format match")
        if "editable" in profile.output_format_constraints and "presentation" in coverage:
            score += 20
            signals.append("editable artifact match")
        provenance = dict(record.get("provenance", {}))
        precedence = int(provenance.get("precedence", 0))
        if precedence:
            score += precedence / 5
            signals.append("trust/provenance")
        if record.get("scope") == "project":
            score += 5
            signals.append("project-rule compatibility")
        if record.get("metadata", {}).get("execution_compatibility") == "reference_only":
            rejected.append({"name": record.get("name"), "reason": "reference-only resource is not executable"})
            continue
        specificity = len(set(record.get("tags", [])) & set(CAPABILITY_TERMS.get(profile.task_type, set())))
        score += min(8, specificity)
        registry_digest = applicability_registry.registry_sha256 if applicability_registry is not None else "nexus_internal"
        candidates.append(ResourceCandidate(
            resource_id=str(record.get("id")),
            name=str(record.get("name")),
            resource_type="skill",
            path=str(record.get("skill_md_path", record.get("path", ""))),
            coverage=sorted(coverage),
            score=round(score, 2),
            score_signals=signals,
            trust=str(provenance.get("source_scope", "local")),
            provenance=provenance,
            runtime_compatibility=str(record.get("metadata", {}).get("execution_compatibility", "directly_usable_by_codex")),
            status=str(record.get("status")),
            record=dict(record),
            domain_coverage=list(decision.matched_domains),
            applicability_evidence={
                "reason_code": decision.reason_code,
                "model_version": applicability.model_version,
                "applicability_version": applicability.applicability_version,
                "provenance": applicability.provenance,
                "registry_sha256": registry_digest,
                "matched_task_kinds": list(decision.matched_task_kinds),
            },
        ))
    candidates.sort(key=lambda item: (-item.score, item.name.casefold(), item.path.casefold()))
    return candidates, rejected


def greedy_select(
    candidates: list[ResourceCandidate],
    requirements: list[CapabilityRequirement],
    required_domains: Iterable[str] = (),
) -> tuple[list[ResourceCandidate], list[dict[str, Any]]]:
    required_capabilities = {item.capability for item in requirements if item.required}
    required_domain_set = set(required_domains)
    required = {f"capability:{item}" for item in required_capabilities} | {f"domain:{item}" for item in required_domain_set}
    selected: list[ResourceCandidate] = []
    covered: set[str] = set()
    evidence: list[dict[str, Any]] = []
    remaining = list(candidates)
    while required - covered:
        def units(item: ResourceCandidate) -> set[str]:
            return (
                {f"capability:{value}" for value in item.coverage if value in required_capabilities}
                | {f"domain:{value}" for value in item.domain_coverage if value in required_domain_set}
            )

        choices = [item for item in remaining if units(item) - covered]
        if not choices:
            break
        choices.sort(key=lambda item: (-len(units(item) - covered), -item.score, item.name.casefold(), item.path.casefold()))
        choice = choices[0]
        contribution = sorted(units(choice) - covered)
        selected.append(choice)
        covered.update(units(choice))
        remaining.remove(choice)
        evidence.append({"name": choice.name, "reason": "greedy semantic contribution", "reason_code": DOMAIN_MATCH, "coverage": contribution})
    # Redundancy elimination is a bounded reverse pass over the selected list.
    for candidate in list(reversed(selected)):
        other_coverage = set().union(*(units(item) for item in selected if item is not candidate)) if len(selected) > 1 else set()
        if required <= other_coverage:
            selected.remove(candidate)
            evidence.append({"name": candidate.name, "reason": "removed as redundant after semantic coverage check", "reason_code": MINIMAL_SET_REDUNDANT})
    return selected, evidence


def _advisory_agents(index: Mapping[str, Any], profile: TaskProfile, requirements: list[CapabilityRequirement]) -> list[ResourceCandidate]:
    task_tokens = tokenize(profile.original_task)
    architecture_intent = bool(task_tokens & {"architecture", "architect"})
    if not (task_tokens & {"architecture", "architect", "agent", "agents", "threat", "threats", "review"}):
        return []
    candidates: list[ResourceCandidate] = []
    for record in index.get("agents", []):
        tokens = _resource_identity_tokens(record)
        overlap = task_tokens & tokens
        architecture_specialist = architecture_intent and bool(tokens & {"architecture", "architect", "systems", "orchestration", "multi"})
        if not overlap and not architecture_specialist:
            continue
        if architecture_intent and not tokens & {"architecture", "architect", "systems", "orchestration", "multi"}:
            continue
        coverage = [item.capability for item in requirements if tokens & RESOURCE_CAPABILITY_TERMS.get(item.capability, set())]
        if not coverage and architecture_intent and tokens & {"architecture", "architect", "agent", "systems", "ai"}:
            coverage = ["advisory_architecture"]
        if not coverage:
            continue
        score = float(max(1, len(overlap)) * 8 + len(coverage) * 20)
        signals = ["advisory specialist relevance"]
        # This is intentionally limited to advisory routing.  An AI research
        # assistant architecture has a materially closer fit with a named
        # multi-agent/systems architect than with generic automation advice.
        if task_tokens & {"ai", "assistant", "research"} and tokens & {"multi", "agent", "systems"}:
            score += 18
            signals.append("AI/research-assistant architecture fit")
        candidates.append(ResourceCandidate(str(record.get("id")), str(record.get("name")), "agent", str(record.get("path", "")), coverage, score, signals, "advisory", {}, "advisory_only", str(record.get("status")), dict(record)))
    candidates.sort(key=lambda item: (-item.score, item.name.casefold()))
    return candidates[:1]


def classify_external_resources(sources: Iterable[Mapping[str, Any]], profile: TaskProfile) -> list[dict[str, Any]]:
    """Keep references/frameworks visible without promoting them to Skills."""
    task_tokens = tokenize(profile.original_task)
    result: list[dict[str, Any]] = []
    for source in sources:
        kind = str(source.get("kind", "reference"))
        source_tokens = tokenize(" ".join([str(source.get("id", "")), " ".join(source.get("categories", [])), " ".join(source.get("use_for", []))]))
        overlap = sorted(task_tokens & source_tokens)
        if kind == "framework":
            reason = "framework is reference-only in V1.2; no runtime dependency or orchestration is introduced"
        elif kind == "reference":
            reason = "external reference is not executable and is not loaded as a Skill"
        elif kind == "agent":
            reason = "external Agent catalog is advisory reference only; Hub does not spawn or delegate Agents"
        else:
            reason = "external source is not an installed executable Skill"
        result.append({"id": source.get("id"), "kind": kind, "overlap": overlap, "status": "reference_only", "reason": reason})
    return result


def validation_plan_for(profile: TaskProfile, requirements: list[CapabilityRequirement]) -> ValidationPlan:
    checks: list[dict[str, Any]] = [{"kind": "plan_coverage", "reason": "all required capabilities must have a selected resource or explicit fallback", "side_effect_free": True}]
    capabilities = {item.capability for item in requirements}
    mapping = {
        "backend": ("targeted_test", "run focused reproduction/regression checks only when relevant"),
        "testing": ("regression_test", "task explicitly requires regression/testing evidence"),
        "presentation": ("presentation_open_render", "editable deck requires structural/readback and visual validation where tooling exists"),
        "spreadsheet": ("workbook_formula_integrity", "workbook task requires formula/error integrity checks"),
        "document": ("document_render", "editable document requires structural and render validation where available"),
        "pdf": ("pdf_structure_render", "PDF requires structural/extraction and render inspection where available"),
        "research": ("evidence_ledger", "research claims require source/evidence and unsupported-claim checks"),
        "frontend": ("ui_behavior_accessibility", "frontend task requires behavior/accessibility and visual review where available"),
        "security": ("security_boundary_review", "explicit authorization/cross-user evidence requires security review"),
    }
    for capability in sorted(capabilities):
        if capability in mapping:
            kind, reason = mapping[capability]
            checks.append({"kind": kind, "reason": reason, "side_effect_free": True})
    return ValidationPlan(checks)


def _ordered_selected(selected: list[ResourceCandidate], requirements: list[CapabilityRequirement]) -> list[ResourceCandidate]:
    required_order = {item.capability: position for position, item in enumerate(requirements)}
    return sorted(selected, key=lambda item: (min((required_order.get(cap, 999) for cap in item.coverage), default=999), -item.score, item.name.casefold()))


def execution_steps_for(
    selected: list[ResourceCandidate], requirements: list[CapabilityRequirement], validation: ValidationPlan,
    reference_research: ReferenceResearchPlan | None = None,
) -> list[ExecutionStep]:
    ordered = _ordered_selected(selected, requirements)
    requirement_by_capability = {item.capability: item for item in requirements}
    steps: list[ExecutionStep] = []
    for position, resource in enumerate(ordered, start=1):
        capabilities = [capability for capability in resource.coverage if capability in requirement_by_capability]
        if not capabilities:
            # The separately modeled reference-research Skill is bound to the
            # pre-build stage below; it is not a second project capability.
            continue
        primary = capabilities[0] if capabilities else "general"
        dependencies = sorted({dependency for capability in capabilities for dependency in requirement_by_capability[capability].dependencies})
        if reference_research and reference_research.status in {"required", "reduced"}:
            dependencies.append("reference-research")
        relevant_checks = [item["kind"] for item in validation.checks if primary in item["kind"] or item["kind"] == "plan_coverage"]
        steps.append(ExecutionStep(
            f"step-{position}", primary, resource.resource_id, resource.name, resource.resource_type,
            f"selected for {', '.join(capabilities)} coverage", dependencies,
            f"complete {primary} task contribution", relevant_checks,
            "use native Codex capability or return explicit blocker if the selected Skill cannot be used",
        ))
    if reference_research and reference_research.status in {"required", "reduced"}:
        research_resource = next((item for item in selected if "research" in item.coverage), None)
        steps.insert(0, ExecutionStep(
            "reference-research", "reference_research",
            research_resource.resource_id if research_resource else None,
            research_resource.name if research_resource else None,
            "research_stage",
            "compare bounded public references and synthesize findings before implementation",
            [], "reference intelligence brief", ["reference_research_synthesis"],
            "if no suitable reference is found within budget, record that result, prefer official sources and verified capabilities, distinguish reference-derived ideas from Nexus-designed choices, then continue PLAN/BUILD/TEST/VERIFY",
        ))
    return steps


def plan_task(
    task: str,
    index: Mapping[str, Any],
    project_root: Path,
    *,
    semantic_extractor: Callable[[str], Mapping[str, Any]] | None = None,
    user_requirements: Iterable[str] = (),
    excluded_resource_ids: set[str] | None = None,
    replan_attempt: int = 0,
    context_options: Mapping[str, int] | None = None,
    context_reader: Callable[..., ProjectContext] | None = None,
    sources: Iterable[Mapping[str, Any]] = (),
    reference_library_reader: Callable[[], LibrarySnapshot] | None = None,
) -> ExecutionPlan:
    context_options = dict(context_options or {})
    profile, evidence = task_profile_for(task, semantic_extractor)
    semantic_model = semantic_task_model(profile.original_task)
    evidence.append(DecisionEvidence(
        "semantic_domain",
        "classified task with the bounded Slice 3A semantic-domain model",
        semantic_model.to_dict(),
    ))
    reader = context_reader or discover_project_context
    context = reader(project_root, task, **context_options)
    rules, conflicts = extract_rules(profile, context, user_requirements)
    reference_research = reference_research_plan(task)
    reference_research = replace(reference_research, reusable_references=discover_references(
        task, reference_research, project_root, hold=bool(conflicts), reader=reference_library_reader,
    ))
    for conflict in conflicts:
        evidence.append(DecisionEvidence("rule_conflict", "unresolved equal-priority rule conflict", conflict))
    requirements = capability_requirements(profile, rules)
    candidates, rejected = rank_resources(index, profile, requirements, rules, excluded_resource_ids)
    external_resources = classify_external_resources(sources, profile)
    if conflicts:
        selected: list[ResourceCandidate] = []
        rejected.append({"name": "all", "reason": "selection blocked by unresolved higher-priority rule conflict"})
        selection_evidence: list[dict[str, Any]] = []
    else:
        selected, selection_evidence = greedy_select(candidates, requirements, semantic_model.required_domains)
        selected = _ordered_selected(selected, requirements)
    if reference_research.status in {"required", "reduced"} and not conflicts:
        # Reuse the existing trusted semantic Skill selector for the separate
        # research stage without changing project-domain coverage.
        research_profile, _ = task_profile_for(
            "Research software implementation patterns using GitHub and official documentation"
        )
        research_requirements = [CapabilityRequirement(
            "research", True, "default pre-build reference research stage",
        )]
        research_candidates, research_rejected = rank_resources(
            index, research_profile, research_requirements, rules, excluded_resource_ids,
        )
        research_resource = next((item for item in research_candidates if "research" in item.coverage), None)
        if research_resource and all(item.resource_id != research_resource.resource_id for item in selected):
            selected.insert(0, research_resource)
            evidence.append(DecisionEvidence(
                "reference_research_skill",
                "selected one compatible research Skill through the existing trusted applicability registry",
                {"resource_id": research_resource.resource_id, "name": research_resource.name},
            ))
        else:
            evidence.append(DecisionEvidence(
                "reference_research_skill",
                "no compatible research Skill was selected; the bounded stage remains a Host-side/native fallback",
                {"reason_code": research_rejected[0].get("reason_code") if research_rejected else CAPABILITY_NOT_COVERED},
            ))
    for item in selection_evidence:
        evidence.append(DecisionEvidence("selection", item["reason"], item))
    selected_ids = {item.resource_id for item in selected}
    selected_domains = set().union(*(set(item.domain_coverage) for item in selected)) if selected else set()
    selected_capabilities = set().union(*(set(item.coverage) for item in selected)) if selected else set()
    for candidate in candidates:
        if candidate.resource_id in selected_ids:
            continue
        if set(candidate.domain_coverage) <= selected_domains and set(candidate.coverage) <= selected_capabilities:
            rejected.append({
                "name": candidate.name,
                "reason": "compatible candidate adds no required semantic coverage beyond the selected minimum set",
                "reason_code": MINIMAL_SET_REDUNDANT,
                "matched_domains": candidate.domain_coverage,
            })
    covered = set().union(*(set(item.coverage) for item in selected)) if selected else set()
    missing = [item.capability for item in requirements if item.required and item.capability not in covered]
    covered_domains = set().union(*(set(item.domain_coverage) for item in selected)) if selected else set()
    missing_domains = [domain for domain in semantic_model.required_domains if domain not in covered_domains]
    if missing or missing_domains:
        fallback = {
            "kind": "native_codex_fallback",
            "status": "needed",
            "reason_code": CAPABILITY_NOT_COVERED,
            "missing_capabilities": missing,
            "missing_domains": missing_domains,
            "reason": "no compatible installed Skill covers every required semantic domain and capability",
        }
        evidence.append(DecisionEvidence("fallback", "native Codex fallback required for uncovered semantic requirements", fallback))
    else:
        fallback = {
            "kind": "native_codex_fallback",
            "status": "not_needed",
            "reason_code": DOMAIN_MATCH,
            "missing_capabilities": [],
            "missing_domains": [],
            "reason": "selected Skills cover required semantic domains and capabilities",
        }
    validation = validation_plan_for(profile, requirements)
    steps = execution_steps_for(selected, requirements, validation, reference_research)
    agents = _advisory_agents(index, profile, requirements)
    if agents:
        evidence.append(DecisionEvidence("advisory_agent", "Agent recommendation is advisory only and is not delegated by the Hub", {"agents": [item.name for item in agents]}))
    for expansion in context.expansions:
        evidence.append(DecisionEvidence("context_expansion", "soft context budget expanded with evidence", expansion))
    return ExecutionPlan(str(uuid4()), utc_now(), profile, context, rules, requirements, candidates, selected, rejected, external_resources, agents, validation, steps, evidence, fallback, reference_research, replan_attempt)


def load_plan_skills(
    plan: ExecutionPlan,
    *,
    path_guard: Callable[[Path], None] | None = None,
    read_guard: Callable[[Path], bytes] | None = None,
    max_file_bytes: int | None = None,
    max_total_bytes: int | None = None,
) -> list[dict[str, Any]]:
    """Use V1.1's actual loader for selected Skills only; never load candidates."""
    selected = [candidate for candidate in plan.selected if candidate.resource_type == "skill"]
    route = {"selected_skills": [candidate.record for candidate in selected]}
    loaded = load_selected_skills(
        route,
        path_guard=path_guard,
        read_guard=read_guard,
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
    )
    # The applicability registry is bound to the exact discovered SKILL.md
    # bytes.  Recheck that digest after the guarded load so an on-disk change
    # between selection and loading cannot inherit the earlier applicability.
    for candidate, item in zip(selected, loaded):
        if "load_error" in item:
            continue
        expected = candidate.record.get("content_sha256")
        observed = item.get("sha256")
        if (
            not isinstance(expected, str)
            or not SHA256_RE.fullmatch(expected.casefold())
            or not isinstance(observed, str)
            or observed.casefold() != expected.casefold()
        ):
            item.clear()
            item.update({
                "name": candidate.name,
                "load_error": "selected Skill changed after applicability verification",
                "reason_code": SKILL_INTEGRITY_CHANGED,
            })
    return loaded


def validate_plan(plan: ExecutionPlan, loaded: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    loaded = loaded or []
    selected_ids = {item.resource_id for item in plan.selected}
    duplicate = len(selected_ids) != len(plan.selected)
    missing = list(plan.fallback.get("missing_capabilities", []))
    missing_domains = list(plan.fallback.get("missing_domains", []))
    load_errors = [item["name"] for item in loaded if "load_error" in item]
    expected_loads = {item.name for item in plan.selected if item.resource_type == "skill"}
    observed_loads = {str(item.get("name")) for item in loaded}
    missing_loads = sorted(expected_loads - observed_loads)
    status = "passed" if not duplicate and not missing and not missing_domains and not load_errors and not missing_loads else "unvalidated"
    return {
        "status": status,
        "checks": [
            {"kind": "no_duplicate_selected_resource", "passed": not duplicate},
            {"kind": "required_capability_coverage", "passed": not missing, "missing": missing},
            {"kind": "required_semantic_domain_coverage", "passed": not missing_domains, "missing": missing_domains},
            {"kind": "selected_skill_load", "passed": not load_errors and not missing_loads, "load_errors": load_errors, "missing_loads": missing_loads},
        ],
    }


REPLAN_ELIGIBLE = {"wrong_resource", "missing_capability", "bad_plan"}


def replan_after_failure(plan: ExecutionPlan, failure_kind: str, index: Mapping[str, Any], project_root: Path) -> ReplanResult:
    if failure_kind not in {"implementation_defect", "wrong_resource", "missing_capability", "dependency_failure", "bad_plan", "project_rule_conflict"}:
        return ReplanResult("blocked", "unknown failure classification", plan.replan_attempt)
    if plan.replan_attempt >= 1:
        return ReplanResult("fallback", "maximum one re-plan reached; use native fallback, blocker, or honest failure", plan.replan_attempt)
    if failure_kind not in REPLAN_ELIGIBLE:
        return ReplanResult("no_replan", f"{failure_kind} does not require a planning change", plan.replan_attempt)
    excluded = {item.resource_id for item in plan.selected}
    amended = plan_task(plan.task_profile.original_task, index, project_root, excluded_resource_ids=excluded, replan_attempt=1)
    amended.evidence.append(DecisionEvidence("replan", "one bounded re-plan created after planning-relevant failure", {"failure_kind": failure_kind, "excluded_resource_ids": sorted(excluded)}))
    return ReplanResult("replanned", "created one bounded amended plan", 1, amended.to_dict())


def write_plan_packet(path: Path, plan: ExecutionPlan, loaded: list[dict[str, Any]] | None = None, validation: Mapping[str, Any] | None = None) -> None:
    payload = plan.to_dict()
    # Additive display metadata only: existing evidence keys and planning
    # semantics remain stable for Adaptive Skills Hub compatibility.
    payload["product_identity"] = {
        "display_name": "Nexus",
        "subtitle": "Adaptive AI Capability Hub",
        "system_name": "Adaptive Skills Hub",
    }
    payload["loaded_skills"] = loaded or []
    payload["plan_validation"] = dict(validation or validate_plan(plan, loaded))
    write_json(path, payload)
