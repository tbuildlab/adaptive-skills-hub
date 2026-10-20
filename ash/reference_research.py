"""Bounded reference-research policy for the existing Nexus plan/handoff path.

This module classifies whether a project task needs a pre-build research stage
and emits a data-only brief. It does not access the network, select a runtime,
or execute research itself.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from typing import Iterable

from .common import tokenize
from .semantic_domains import task_intent_text


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
    r"\b(?:do not|don['’]t|never|skip|omit|without|no)\s+(?:(?:perform|conduct|carry out|use)\s+)?(?:(?:the|any)\s+)?(?:(?:external|public|github|reference)\s+)*(?:research|search|browsing)\b",
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
    work_category: str = "none"
    reusable_references: dict = field(default_factory=dict)

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


def _research_opt_out(text: str) -> bool:
    text = _normalized(text)
    for pattern in OPT_OUT_PATTERNS:
        for match in re.finditer(pattern, text):
            # A prohibition on skipping/omitting research requests the positive
            # research path; the embedded opt-out verb is not itself an opt-out.
            if re.match(r"(?:skip|omit)\b", match.group()) and re.search(
                r"\b(?:do not|don['’]t|never)\s+$", text[:match.start()],
            ):
                continue
            return True
    return False


@dataclass(frozen=True)
class SubstantialWork:
    category: str = "none"
    skip_reason: str = "none"
    reduced: bool = False


def classify_substantial_work(task: str) -> SubstantialWork:
    """One side-effect-free eligibility boundary for research and library reuse."""
    if not isinstance(task, str) or not task.strip():
        return SubstantialWork()
    text = _normalized(task)
    tokens = tokenize(text)
    if _research_opt_out(text):
        return SubstantialWork(skip_reason="user_opt_out")

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
    repair = repair or bool(re.search(r"修复|排障|故障", text))
    extension = (bool(tokens & {"extend", "expand", "add"})
                 or bool(tokens & {"implement", "develop", "introduce"} and tokens & {"feature", "features", "functionality"})
                 or bool(re.search(r"扩展|新增|增加", text)))
    meaningful_extension = extension and (
        substantial or bool(tokens & {"feature", "features", "functionality", "reporting", "integration"})
        or bool(re.search(r"功能|模块|集成", text))
    )
    if (repair and substantial) or meaningful_extension:
        actions.add("implement")
    if not project or not actions:
        return SubstantialWork()
    # A content-size adjective does not make whole-website creation a tiny edit.
    # Require the website itself as the creation object, not a component for it
    # or a compound component name such as "website header".
    whole_website_creation = tiny and not substantial and bool(re.search(
        r"\b(?:create|make|build|develop|design|implement)\s+"
        r"(?:(?!(?:for|on|in|of|to|with|inside|within|from|and|or|without)\b)[\w-]+\s+){0,8}"
        r"(?:website|webapp)(?=$|[.,;:!?]|\s+(?:for|with|from|using|that|which|where|to|and)\b)",
        task_intent_text(text),
    ))
    if tiny and not substantial and not whole_website_creation:
        return SubstantialWork(skip_reason="small_change")
    if repair and not substantial and not (tokens & {"refactor", "restructure", "rearchitect", "redesign", "overhaul", "rewrite", "rebuild"}) and not re.search(r"重构|重做|大改|改造", text):
        return SubstantialWork(skip_reason="simple_repair")
    # Website creation is project work even without a literal "new" marker.
    # The opt-out, tiny-change and focused-repair guards above still apply.
    website_creation = (
        bool(tokens & {"website", "webapp"} or re.search(r"网站|网页", text))
        and bool(actions & {"create", "build", "develop", "design", "implement"})
    )
    if not substantial and not website_creation and not meaningful_extension and not (tokens & {"new", "scratch", "customer", "client", "deliverable", "production"}):
        # Scope is deliberately conservative when the request only mentions a
        # project noun and a generic action such as "edit" or "review".
        return SubstantialWork()

    reduced = any(re.search(pattern, text) for pattern in COMPLETE_SPEC_PATTERNS)
    category = "creation"
    if tokens & {"refactor", "restructure", "rearchitect"} or re.search(r"重构", text):
        category = "refactor"
    elif tokens & {"redesign", "overhaul", "rewrite", "rebuild", "modernize"} or re.search(r"重做|改造|重新设计", text):
        category = "redesign"
    elif repair:
        category = "substantial_fix"
    elif extension:
        category = "meaningful_extension"
    return SubstantialWork(category, reduced=reduced)


def reference_research_plan(task: str, *, constraints: Iterable[str] = ()) -> ReferenceResearchPlan:
    """Consume the shared classification; never perform I/O or grant authority."""
    if any(_research_opt_out(item) for item in constraints if isinstance(item, str)):
        return ReferenceResearchPlan("skipped", "user_opt_out", "user opted out",
            candidate_limit=0, single_repository_policy="not_applicable", implementation_gate="not_applicable")
    work = classify_substantial_work(task)
    if work.category == "none":
        if work.skip_reason == "none":
            return SKIP
        return ReferenceResearchPlan("skipped", work.skip_reason,
            "user opted out" if work.skip_reason == "user_opt_out" else "small change or focused repair",
            candidate_limit=0, single_repository_policy="not_applicable", implementation_gate="not_applicable")
    reduced = work.reduced
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
        work_category=work.category,
    )
