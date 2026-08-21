from __future__ import annotations

from collections import defaultdict
from typing import Any

from .common import tokenize

DOMAIN_SIGNALS: dict[str, set[str]] = {
    "frontend": {"react", "frontend", "ui", "ux", "dashboard", "css", "html", "component", "accessibility", "animation"},
    "backend": {"backend", "api", "server", "endpoint", "database", "bug", "python", "service"},
    "research": {"research", "architecture", "agent", "ai", "llm", "rag", "workflow", "orchestration", "fact", "facts", "evidence", "citation", "citations"},
    "testing": {"test", "testing", "validate", "validation", "qa", "bug", "regression"},
    "spreadsheet": {"excel", "workbook", "spreadsheet", "xlsx", "xls", "formula", "formulas", "csv"},
    "document": {"document", "report", "docx", "word", "letter", "memo"},
    "presentation": {"presentation", "ppt", "powerpoint", "slide", "slides", "deck"},
    "pdf": {"pdf"},
    "security": {"security", "threat", "vulnerability", "appsec", "abuse", "authentication", "authorization", "auth", "secrets", "privacy"},
}
# A Skill may use a different, but genuinely equivalent, vocabulary from the
# task.  For example, a React dashboard task should be able to select a UI
# design Skill whose description says "UI polish" rather than "dashboard".
# Keep this set domain-specific: generic words such as "report" or "review"
# must not make a security Skill look like a Word-document Skill.
SKILL_CAPABILITY_SIGNALS: dict[str, set[str]] = {
    "frontend": {"react", "frontend", "ui", "ux", "dashboard", "css", "html", "component", "accessibility", "animation"},
    "backend": {"backend", "api", "server", "endpoint", "database", "service"},
    "research": {"research", "evidence", "fact", "facts", "citation", "citations", "agent", "ai", "llm", "rag", "orchestration"},
    "testing": {"test", "testing", "qa", "regression", "validation"},
    "spreadsheet": {"excel", "workbook", "spreadsheet", "xlsx", "xls", "formula", "formulas", "csv"},
    "document": {"document", "documentation", "docx", "word", "letter", "memo"},
    "presentation": {"presentation", "ppt", "powerpoint", "slide", "slides", "deck"},
    "pdf": {"pdf"},
    "security": {"security", "threat", "vulnerability", "appsec", "abuse", "authentication", "authorization", "auth", "secrets", "privacy"},
}
WEAK_OVERLAP_TOKENS = {"review", "verify", "inspect", "improve", "report", "create", "use", "current", "existing"}
EXTERNAL_COMPLEXITY = {"multi-agent", "multi agent", "long-horizon", "long horizon", "delegate", "orchestration"}
TASK_ALIASES = {
    "powerpoint": {"ppt", "presentation", "slides"},
    "presentation": {"ppt", "powerpoint", "slides"},
    "slides": {"ppt", "powerpoint", "presentation"},
    "frontend": {"ui", "ux"},
    "dashboard": {"ui", "ux"},
    "api": {"backend", "endpoint"},
    "architect": {"architecture"},
    "multi-agent": {"orchestration"},
}
CODE_REPAIR_SIGNALS = {"fix", "bug", "error", "debug", "exception", "failure", "failed", "fails"}
BACKEND_EXECUTION_SIGNALS = {
    "fix", "debug", "diagnose", "failure", "failed", "fails", "error", "exception",
    "http", "endpoint", "request", "response", "server", "service", "database",
    "validation", "trace", "tracing",
}
REGRESSION_TEST_SIGNALS = {
    "regression", "reproduce", "reproduction", "recurrence", "unit", "integration",
    "failure", "failed", "fails", "bug", "fix", "error", "boundary", "testcase", "testcases",
}
ARTIFACT_CAPABILITIES = {"presentation", "document", "spreadsheet", "pdf"}


def _expand_task_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded.update(TASK_ALIASES.get(token, set()))
    return expanded


def capabilities_for_task(task: str) -> list[str]:
    tokens = tokenize(task)
    found = [name for name, cues in DOMAIN_SIGNALS.items() if tokens & cues]
    return found or ["general"]


def _score(record: dict[str, Any], task_tokens: set[str], capabilities: list[str]) -> tuple[float, list[str]]:
    text_tokens = _expand_task_tokens(tokenize(" ".join([
        record.get("name", ""), record.get("description", ""), " ".join(record.get("tags", [])),
        record.get("path", ""),
    ])))
    overlap = task_tokens & text_tokens
    score = float(len(overlap) * 9)
    reasons = [f"keyword overlap: {', '.join(sorted(overlap))}"] if overlap else []
    for capability in capabilities:
        cues = DOMAIN_SIGNALS.get(capability, set())
        task_matched = cues & task_tokens
        skill_matched = SKILL_CAPABILITY_SIGNALS.get(capability, cues) & text_tokens
        if task_matched and skill_matched:
            score += 16 + min(4, len(skill_matched)) * 2
            reasons.append(f"{capability} capability match: {', '.join(sorted(skill_matched))}")
    if record.get("scope") == "project":
        score += 3
        reasons.append("project-local")
    if record.get("status") != "available":
        score -= 100
        reasons.append(f"not executable: {record.get('status')}")
    # Procedure that states an explicit domain is more specific than generic wording.
    score += min(8, len(set(record.get("tags", [])) & set().union(*[DOMAIN_SIGNALS.get(c, set()) for c in capabilities])))
    return score, reasons


def _topological_order(selected: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    by_name = {item["name"].casefold(): item for item in selected}
    incoming: dict[str, set[str]] = {name: set() for name in by_name}
    outgoing: dict[str, set[str]] = defaultdict(set)
    warnings: list[str] = []
    for item in selected:
        after = item.get("metadata", {}).get("hub_after", [])
        if isinstance(after, str):
            after = [part.strip() for part in after.split(",") if part.strip()]
        if not isinstance(after, list):
            continue
        for dependency in after:
            key = str(dependency).casefold()
            current = item["name"].casefold()
            if key in by_name and key != current:
                incoming[current].add(key)
                outgoing[key].add(current)
            elif key not in by_name:
                warnings.append(f"{item['name']} requested absent chain dependency: {dependency}")
    ordered: list[dict[str, Any]] = []
    ready = sorted((name for name, needs in incoming.items() if not needs), key=lambda n: (-by_name[n]["score"], n))
    while ready:
        name = ready.pop(0)
        ordered.append(by_name[name])
        for next_name in sorted(outgoing[name]):
            incoming[next_name].discard(name)
            if not incoming[next_name]:
                ready.append(next_name)
        ready.sort(key=lambda n: (-by_name[n]["score"], n))
    if len(ordered) != len(selected):
        warnings.append("cycle in hub_after metadata; retaining ranking order for cyclic skills")
        present = {item["name"].casefold() for item in ordered}
        ordered.extend(item for item in selected if item["name"].casefold() not in present)
    return ordered, warnings


def _external_candidates(sources: list[dict[str, Any]], task_tokens: set[str], capabilities: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    candidates: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    complex_task = any(phrase in " ".join(task_tokens) for phrase in EXTERNAL_COMPLEXITY)
    for source in sources:
        source_tokens = tokenize(" ".join(source.get("categories", []) + source.get("use_for", []) + source.get("avoid_for", [])))
        match = task_tokens & source_tokens
        applicable = bool(match)
        if source["id"] == "deer-flow":
            applicable = "research" in capabilities and complex_task
            if not applicable:
                skipped.append({"id": source["id"], "reason": "framework cost is unjustified without complex orchestration"})
                continue
        if source["id"] == "liquid-glass-react" and "frontend" not in capabilities:
            skipped.append({"id": source["id"], "reason": "Liquid Glass is not relevant to this non-UI task"})
            continue
        if source["id"] == "emilkowalski-skills" and "frontend" not in capabilities:
            skipped.append({"id": source["id"], "reason": "its installed upstream catalog is UI/design focused, not backend or research execution"})
            continue
        if source["id"] == "awesome-llm-apps" and "research" not in capabilities:
            skipped.append({"id": source["id"], "reason": "AI application examples are not needed for this task domain"})
            continue
        if applicable:
            candidates.append({"id": source["id"], "kind": source["kind"], "score": len(match) * 8 + 4, "reasons": sorted(match)})
        else:
            skipped.append({"id": source["id"], "reason": "no material task-capability overlap"})
    return sorted(candidates, key=lambda item: (-item["score"], item["id"])), skipped


def _agent_is_domain_suitable(agent_tokens: set[str], capabilities: list[str]) -> bool:
    """Keep broad roles (for example grant writing) out of AI architecture routing."""
    if "research" in capabilities:
        ai_architecture_terms = {"ai", "llm", "rag", "agent", "architecture", "orchestration", "systems", "multi-agent"}
        return bool(agent_tokens & ai_architecture_terms)
    return True


def route_task(task: str, index: dict[str, Any], sources: list[dict[str, Any]], max_skills: int = 3) -> dict[str, Any]:
    raw_task_tokens = tokenize(task)
    task_tokens = _expand_task_tokens(raw_task_tokens)
    capabilities = capabilities_for_task(task)
    ranked: list[dict[str, Any]] = []
    for skill in index.get("skills", []):
        score, reasons = _score(skill, task_tokens, capabilities)
        candidate = dict(skill)
        candidate["score"] = round(score, 2)
        candidate["reasons"] = reasons
        ranked.append(candidate)
    ranked.sort(key=lambda item: (-item["score"], item["name"].casefold(), item["skill_md_path"]))
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    covered: set[str] = set()
    relevant_tag_space = set().union(*[
        SKILL_CAPABILITY_SIGNALS.get(capability, DOMAIN_SIGNALS.get(capability, set()))
        for capability in capabilities
    ]) if capabilities != ["general"] else set()
    declared_dependencies: set[str] = set()
    for candidate in ranked:
        after = candidate.get("metadata", {}).get("hub_after", [])
        if isinstance(after, str):
            after = [part.strip() for part in after.split(",")]
        if isinstance(after, list):
            declared_dependencies.update(str(item).casefold() for item in after)
    for candidate in ranked:
        overlap = task_tokens & _expand_task_tokens(tokenize(" ".join([
            candidate.get("name", ""), candidate.get("description", ""),
            " ".join(candidate.get("tags", [])), candidate.get("path", ""),
        ])))
        has_task_evidence = any(" capability match:" in reason for reason in candidate["reasons"])
        has_task_evidence = has_task_evidence or bool(overlap - WEAK_OVERLAP_TOKENS)
        if candidate["status"] != "available" or not has_task_evidence:
            continue
        is_presentation_skill = "ppt" in candidate.get("tags", []) or "ppt" in candidate["name"].casefold()
        is_security_skill = any(term in candidate["name"].casefold() for term in ("security", "threat"))
        is_codex_skin_skill = "skin" in candidate["name"].casefold()
        is_scope_creep_skill = "scope-creep" in candidate["name"].casefold()
        is_commit_archaeologist = "archaeologist" in candidate["name"].casefold()
        candidate_name = candidate["name"].casefold()
        is_document_skill = candidate_name == "documents"
        is_pdf_skill = candidate_name == "pdf"
        is_spreadsheet_skill = candidate_name == "spreadsheets"
        is_excel_live_skill = candidate_name == "excel-live-control"
        is_gsap_skill = candidate_name.startswith("gsap-")
        is_image_skill = candidate_name == "imagegen"
        is_openai_docs_skill = candidate_name == "openai-docs"
        is_dependency_skill = candidate_name == "dependency-doctor"
        is_evidence_skill = candidate_name == "evidence-first-research"
        is_emil_design_skill = candidate_name == "emil-design-eng"
        is_review_agent_skill = candidate_name == "review-agent"
        is_plugin_creator_skill = candidate_name == "plugin-creator"
        is_threat_model_skill = candidate_name == "security-threat-model"
        is_security_best_practices_skill = candidate_name == "security-best-practices"
        is_backend_debugging_skill = candidate_name == "evidence-driven-backend-debugging"
        is_regression_testing_skill = candidate_name == "regression-first-testing"
        if is_codex_skin_skill and not ({"codex"} <= task_tokens and task_tokens & {"skin", "theme", "appearance", "wallpaper"}):
            rejected.append({"name": candidate["name"], "reason": "Codex skin Skill requires an explicit Codex theme/skin task"})
            continue
        if is_scope_creep_skill and not (task_tokens & {"scope", "diff", "pr", "pull", "staged", "branch"}):
            rejected.append({"name": candidate["name"], "reason": "scope-creep Skill requires an explicit diff/PR/scope-review task"})
            continue
        if is_commit_archaeologist and not (task_tokens & {"git", "history", "blame", "introduced", "author", "origin", "why"}):
            rejected.append({"name": candidate["name"], "reason": "commit-archaeologist Skill requires an explicit code-history question"})
            continue
        if is_presentation_skill and "presentation" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "presentation Skill requires a deck/presentation task, not incidental frontend terminology"})
            continue
        if is_presentation_skill and task_tokens & CODE_REPAIR_SIGNALS:
            rejected.append({"name": candidate["name"], "reason": "presentation terminology appears inside a coding/repair request, not a deck-production request"})
            continue
        if is_document_skill and "document" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "documents Skill requires an explicit Word/DOCX/document task"})
            continue
        if is_document_skill and task_tokens & CODE_REPAIR_SIGNALS:
            rejected.append({"name": candidate["name"], "reason": "document terminology appears inside a coding/repair request, not a DOCX-production request"})
            continue
        if is_document_skill and "pdf" in capabilities and not (raw_task_tokens & {"document", "docx", "word", "letter", "memo"}):
            rejected.append({"name": candidate["name"], "reason": "PDF is the explicit requested artifact; documents is not selected from an incidental report term"})
            continue
        if is_pdf_skill and "pdf" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "pdf Skill requires an explicit PDF task"})
            continue
        if is_pdf_skill and task_tokens & CODE_REPAIR_SIGNALS:
            rejected.append({"name": candidate["name"], "reason": "PDF terminology appears inside a coding/repair request, not a PDF-production request"})
            continue
        if is_spreadsheet_skill and "spreadsheet" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "Spreadsheets Skill requires an explicit workbook/spreadsheet task"})
            continue
        if is_spreadsheet_skill and task_tokens & CODE_REPAIR_SIGNALS:
            rejected.append({"name": candidate["name"], "reason": "spreadsheet terminology appears inside a coding/repair request, not a workbook-production request"})
            continue
        if is_excel_live_skill and not ({"excel", "live"} <= task_tokens):
            rejected.append({"name": candidate["name"], "reason": "excel-live-control requires an explicit live Excel-session task"})
            continue
        if is_gsap_skill and not ("frontend" in capabilities and task_tokens & {"animation", "animate", "motion", "scroll", "transition", "timeline", "tween"}):
            rejected.append({"name": candidate["name"], "reason": "GSAP Skills require an explicit frontend animation task"})
            continue
        if is_image_skill and not (task_tokens & {"image", "images", "photo", "illustration", "bitmap", "texture", "sprite", "mockup"}):
            rejected.append({"name": candidate["name"], "reason": "imagegen requires an explicit raster-image task"})
            continue
        if is_openai_docs_skill and not (task_tokens & {"openai", "chatgpt", "codex"}):
            rejected.append({"name": candidate["name"], "reason": "openai-docs requires an explicit OpenAI/Codex product task"})
            continue
        if is_dependency_skill and not (task_tokens & {"dependency", "dependencies", "manifest", "package", "packages", "pin", "pins", "lockfile"}):
            rejected.append({"name": candidate["name"], "reason": "dependency-doctor requires an explicit dependency/manifest task"})
            continue
        if is_evidence_skill and "research" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "evidence-first-research requires an explicit research/fact-evidence task"})
            continue
        if is_evidence_skill and not (task_tokens & {"research", "fact", "facts", "evidence", "citation", "citations", "source", "sources", "verify", "verification"}):
            rejected.append({"name": candidate["name"], "reason": "evidence-first-research requires an explicit research/evidence request, not incidental architecture terminology"})
            continue
        if is_emil_design_skill and "frontend" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "emil-design-eng requires an explicit frontend/UI implementation or review task"})
            continue
        if is_review_agent_skill and not (task_tokens & {"diff", "commit", "pr", "pull", "change", "changes", "codebase", "code"}):
            rejected.append({"name": candidate["name"], "reason": "review-agent requires an explicit code-change review target"})
            continue
        if is_plugin_creator_skill and not (task_tokens & {"plugin", "plugins"}):
            rejected.append({"name": candidate["name"], "reason": "plugin-creator requires an explicit plugin-creation task"})
            continue
        if is_backend_debugging_skill and (
            "backend" not in capabilities or not (raw_task_tokens & BACKEND_EXECUTION_SIGNALS)
        ):
            rejected.append({"name": candidate["name"], "reason": "backend-debugging requires a concrete backend/API execution failure, not an explanatory or artifact task"})
            continue
        if is_backend_debugging_skill and (set(capabilities) & ARTIFACT_CAPABILITIES) and not (raw_task_tokens & {"fix", "debug", "diagnose", "error", "exception", "failure", "failed", "fails"}):
            rejected.append({"name": candidate["name"], "reason": "backend terminology appears in an artifact request, not a backend repair task"})
            continue
        if is_regression_testing_skill and (
            "testing" not in capabilities or not (raw_task_tokens & REGRESSION_TEST_SIGNALS)
        ):
            rejected.append({"name": candidate["name"], "reason": "regression-first-testing requires an explicit regression, reproduction, or focused failure-validation task"})
            continue
        if is_regression_testing_skill and (set(capabilities) & ARTIFACT_CAPABILITIES) and not (raw_task_tokens & {"regression", "reproduce", "reproduction", "recurrence", "unit", "integration"}):
            rejected.append({"name": candidate["name"], "reason": "testing terminology appears in an artifact request, not a software regression task"})
            continue
        if is_threat_model_skill and not (task_tokens & {"threat", "threats", "model", "abuse", "abuses", "attacker", "attackers"}):
            rejected.append({"name": candidate["name"], "reason": "security-threat-model requires an explicit threat/abuse-modeling task"})
            continue
        if is_security_best_practices_skill and not (task_tokens & {"security", "secure", "authorization", "authentication", "auth", "vulnerability", "appsec", "secrets", "privacy"}):
            rejected.append({"name": candidate["name"], "reason": "security-best-practices requires an explicit secure-coding or security-remediation task"})
            continue
        if is_security_skill and "security" not in capabilities:
            rejected.append({"name": candidate["name"], "reason": "security Skill requires an explicit security/threat-model task"})
            continue
        candidate_tags = set(candidate.get("tags", []))
        # A Skill must add coverage for the task's detected capabilities, not
        # merely advertise an unrelated extra output.  For example, a PPT Skill
        # that also mentions PDF must not turn a simple presentation request
        # into a two-Skill chain after the presentation capability is covered.
        candidate_tags &= relevant_tag_space
        marginal = candidate_tags - covered
        is_declared_dependency = candidate["name"].casefold() in declared_dependencies
        if selected and not marginal and not is_declared_dependency and candidate["score"] < selected[0]["score"] - 12:
            continue
        selected.append(candidate)
        covered |= candidate_tags
        if len(selected) >= max_skills:
            break
    selected, chain_warnings = _topological_order(selected)
    external, skipped_sources = _external_candidates(sources, task_tokens, capabilities)
    agent_candidates: list[dict[str, Any]] = []
    for agent in index.get("agents", []):
        score, reasons = _score(agent, task_tokens, capabilities)
        agent_tokens = _expand_task_tokens(
            tokenize(" ".join([agent["name"], agent.get("description", ""), " ".join(agent.get("tags", []))]))
        )
        exact = task_tokens & agent_tokens
        high_signal = {"research", "architecture", "llm", "rag", "orchestration", "backend", "api"}
        if score > 12 and _agent_is_domain_suitable(agent_tokens, capabilities) and (len(exact) >= 2 or bool(exact & high_signal)):
            agent_candidates.append({"name": agent["name"], "path": agent["path"], "score": round(score, 2), "reasons": reasons})
    agent_candidates.sort(key=lambda item: (-item["score"], item["name"]))
    return {
        "task": task, "capabilities": capabilities, "selected_skills": selected,
        # Agents are advisory roles, not executable Skills. Prefer one specific role
        # unless a later approved workflow supplies an explicit complementary need.
        "ranked_skills": ranked, "selected_agents": agent_candidates[:1],
        "rejected_skills": rejected,
        "external_candidates": external, "skipped_sources": skipped_sources,
        "chain_warnings": chain_warnings,
        "no_matching_skill": not bool(selected),
    }
