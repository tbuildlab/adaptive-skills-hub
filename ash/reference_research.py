"""Bounded reference-research policy for the existing Nexus plan/handoff path.

This module classifies whether a project task needs a pre-build research stage
and emits a data-only brief. It does not access the network, select a runtime,
or execute research itself.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re

from .common import tokenize


PROJECT_TYPES = frozenset({
    "website", "webapp", "web", "app", "application", "desktop", "mobile",
    "cli", "tool", "plugin", "mcp", "agent", "workflow", "automation",
    "developer", "github", "portfolio", "internal", "data", "dashboard",
    "api", "service", "architecture", "library", "component", "system",
    "project", "product", "software",
})
PROJECT_ACTIONS = frozenset({
    "create", "build", "develop", "implement", "design", "start", "launch",
    "refactor", "restructure", "rearchitect", "redesign", "overhaul",
    "rewrite", "extend", "expand", "modernize", "rebuild",
})
SUBSTANTIAL_MARKERS = frozenset({
    "major", "substantial", "significant", "large", "extensive", "complex",
    "architecture", "rearchitecture", "client", "customer", "refactor", "restructure", "redesign",
    "overhaul", "rewrite", "rebuild", "expand", "extensively",
})
SIMPLE_TASK_MARKERS = frozenset({
    "typo", "typos", "color", "colour", "button", "label", "wording",
    "copy", "one-line", "small", "tiny", "simple", "minor", "quick",
})
OPT_OUT_PATTERNS = (
    r"\bdo not (?:search|research|browse)\b",
    r"\bdon['’]t (?:search|research|browse|reference)\b",
    r"\bdo not (?:use )?(?:github|external|other|public)? ?references?\b",
    r"\bno (?:github|external|reference) research\b",
    r"\bskip (?:the )?(?:github|reference|external) research\b",
    r"\bwithout (?:github|external) research\b",
    r"不要(?:搜索|搜寻|浏览|研究|参考)(?:一下)?\s*(?:github|外部资料|公开资料|其他项目)?",
    r"不需要(?:搜索|研究|参考)\s*(?:github|外部资料|公开资料)?",
)
COMPLETE_SPEC_PATTERNS = (
    r"\b(?:complete|full|exact|detailed) (?:project )?spec(?:ification)?\b",
    r"\bacceptance criteria\b",
    r"\bprovided (?:architecture|design|reference implementation)\b",
    r"\bexact (?:library|framework|stack|implementation)\b",
    r"\b(?:use|using|built with|based on|framework:|library:) ?(?:react|next\.?js|vue|angular|svelte|python|django|fastapi|flask|laravel|swift|kotlin|flutter|electron|tauri|rust|node\.?js|express|postgres(?:ql)?|sqlite|mysql|mongodb|aws|azure|gcp)\b",
    r"(?:完整|详细)(?:项目)?(?:规范|规格|方案|架构)",
    r"验收标准|指定(?:的)?(?:架构|设计|框架|技术栈)",
)


@dataclass(frozen=True)
class ReferenceResearchPlan:
    status: str
    trigger: str
    reason: str
    sources: tuple[str, ...] = ()
    minimum_reference_set: tuple[str, ...] = ()
    candidate_limit: int = 6
    single_repository_policy: str = "never_clone_or_rebrand_one_reference; compare_multiple_sources_and_synthesize"
    stop_when_answered: tuple[str, ...] = ()
    comparison_dimensions: tuple[str, ...] = ()
    synthesis_fields: tuple[str, ...] = ()
    license_policy: str = "unknown_or_unclear_license_means_patterns_only_no_code_reuse"
    security_policy: str = "no_permission_expansion; material_conflict_requires_owner_decision"
    security_conflict_outcome: str = "HOLD_owner_decision"
    implementation_gate: str = "synthesis_before_build"
    no_suitable_reference_fallback: str = "record_no_suitable_reference; prefer_official_docs_and_verified_capabilities; label_reference_derived_vs_nexus_designed; continue_plan_build_test_verify"

    def to_dict(self) -> dict:
        return asdict(self)


SKIP = ReferenceResearchPlan(
    status="skipped",
    trigger="none",
    reason="task is simple, non-project work, or the user opted out",
    candidate_limit=0,
    single_repository_policy="not_applicable",
    implementation_gate="not_applicable",
)


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def reference_research_plan(task: str) -> ReferenceResearchPlan:
    """Return the bounded default research decision for a new plan."""
    if not isinstance(task, str) or not task.strip():
        return SKIP
    text = _normalized(task)
    tokens = tokenize(text)
    if any(re.search(pattern, text) for pattern in OPT_OUT_PATTERNS):
        return ReferenceResearchPlan("skipped", "user_opt_out", "the user explicitly prohibited external research", candidate_limit=0, single_repository_policy="not_applicable", implementation_gate="not_applicable")

    actions = tokens & PROJECT_ACTIONS
    if re.search(r"\b(create|make)\b", text):
        actions.add("create")
    chinese_action = re.search(r"创建|新建|开发|构建|实现|设计|重构|重做|改造|扩展|做一个|做个", text)
    if chinese_action:
        actions.add("create")
    project = bool(tokens & PROJECT_TYPES) or bool(re.search(
        r"网站|网页|应用|软件|工具|插件|智能体|工作流|自动化|桌面|移动端|仪表板|项目|产品|架构|系统", text,
    ))
    substantial = bool(tokens & SUBSTANTIAL_MARKERS) or bool(re.search(
        r"新(?:建|项目|产品|能力|网站|工具|应用|服务|插件|工作流|架构)|大改|大幅|大型|重大|复杂|重构|重做|改造|架构|客户交付|交付给客户", text,
    ))
    tiny = bool(tokens & SIMPLE_TASK_MARKERS) or bool(re.search(
        r"错别字|拼写错误|按钮颜色|调整颜色|改颜色|小改|简单修复|小型改动|一处文案", text,
    ))
    repair = bool(tokens & {"fix", "debug", "diagnose", "bug", "error", "failure"})
    if not project or not actions:
        return SKIP
    if tiny and not substantial:
        return ReferenceResearchPlan("skipped", "small_change", "small presentation or copy change does not need reference research", candidate_limit=0, single_repository_policy="not_applicable", implementation_gate="not_applicable")
    if repair and not substantial and not (tokens & {"refactor", "restructure", "rearchitect", "redesign", "overhaul", "rewrite", "rebuild"}) and not re.search(r"重构|重做|大改|改造", text):
        return ReferenceResearchPlan("skipped", "simple_repair", "focused bug repair does not need default reference research", candidate_limit=0, single_repository_policy="not_applicable", implementation_gate="not_applicable")
    if not substantial and not (tokens & {"new", "scratch", "customer", "client", "deliverable", "production"}):
        # Scope is deliberately conservative when the request only mentions a
        # project noun and a generic action such as "edit" or "review".
        return SKIP

    reduced = any(re.search(pattern, text) for pattern in COMPLETE_SPEC_PATTERNS)
    return ReferenceResearchPlan(
        status="reduced" if reduced else "required",
        trigger="complete_spec_missing_points" if reduced else "substantial_project_work",
        reason="user supplied an exact or complete specification; research is limited to unresolved compatibility, implementation, or risk points" if reduced else "new or materially changed project work defaults to reference research before build",
        sources=("official_documentation", "github_repositories", "public_products_and_projects", "community_evidence_when_useful"),
        minimum_reference_set=("one_relevant_mature_project", "one_alternative_implementation", "one_official_or_authoritative_source"),
        candidate_limit=6,
        stop_when_answered=("mature_patterns", "best_fit_direction", "material_pitfalls", "reuse_and_license_constraints"),
        comparison_dimensions=("relevance", "maintenance", "documentation", "release_and_tests", "license", "compatibility", "security_posture", "operational_cost"),
        synthesis_fields=("problem", "references_and_tradeoffs", "reusable_patterns", "approaches_to_avoid", "license_constraints", "technical_risks", "recommended_direction", "fit_to_user_scope", "what_will_differ", "reference_derived_vs_nexus_designed"),
    )
