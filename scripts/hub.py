#!/usr/bin/env python3
"""Nexus CLI, preserving Adaptive Skills Hub V1.1/V1.2 compatibility."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PRODUCT_NAME = "Nexus"
PRODUCT_SUBTITLE = "Adaptive AI Capability Hub"

from ash.common import read_json, sha256_text, write_json  # noqa: E402
from ash.discovery import build_index  # noqa: E402
from ash.execution import execute_route, write_packet  # noqa: E402
from ash.router import route_task  # noqa: E402
from ash.semantic_domains import SemanticRoutingError  # noqa: E402
from ash.v2 import load_plan_skills, plan_task, validate_plan, write_plan_packet  # noqa: E402


def _workspace(value: str | None) -> Path:
    return Path(value).resolve() if value else ROOT.parent.resolve()


def _sources() -> list[dict]:
    return read_json(ROOT / "sources.json", {"sources": []}).get("sources", [])


def _print_product_header() -> None:
    print(PRODUCT_NAME)
    print(PRODUCT_SUBTITLE)


def _friendly_task_label(task_type: str, original_task: str) -> str:
    lowered = original_task.casefold()
    if task_type == "backend":
        return "Backend defect repair" if {"fix", "bug", "error", "failure", "debug"} & set(lowered.replace(".", " ").split()) else "Backend task"
    labels = {
        "frontend": "Frontend/UI task",
        "research": "Research task",
        "artifact": "Artifact creation",
        "general": "General task",
    }
    return labels.get(task_type, task_type.replace("_", " ").title())


def _friendly_validation_label(kind: str) -> str:
    labels = {
        "plan_coverage": "capability coverage",
        "targeted_test": "reproduce and verify the focused failure",
        "regression_test": "targeted regression tests",
        "presentation_open_render": "presentation structure and render checks",
        "workbook_formula_integrity": "workbook formula integrity",
        "document_render": "document structure and render checks",
        "pdf_structure_render": "PDF structure and render checks",
        "evidence_ledger": "evidence ledger",
        "ui_behavior_accessibility": "UI behavior and accessibility review",
        "security_boundary_review": "security boundary review",
    }
    return labels.get(kind, kind.replace("_", " "))


def _normalized_skill_path(path: str) -> str:
    """Return a local, canonical identity for matching selected Skill loads."""
    return os.path.normcase(str(Path(path).resolve(strict=False)))


def _governance_advisory(plan, context_path: str) -> dict:
    """Review only an explicitly selected, already captured non-secret record.

    No file read or evidence adjudication happens here. Even a coherent source
    retains unknown freshness and unverified provenance, coverage and scope.
    """
    result = {
        "authority": "none",
        "dispatch_requested": False,
        "handling": "PRESERVE_UNKNOWN",
        "source_evidence_status": "UNVERIFIED",
        "selection_completeness": "UNVERIFIED",
        "freshness": "UNKNOWN",
        "subject_scope_binding": "UNVERIFIED",
        "binding_scope": "captured_project_context_bytes_only",
        "consumer": "governance_assessment_offline_v1",
        "source_context_position": None,
        "source_sha256": None,
        "report": None,
        "diagnostic": "SOURCE_SELECTION_INVALID",
    }
    if (
        type(context_path) is not str or not context_path or len(context_path) > 512
        or "\\" in context_path or ":" in context_path
        or any(part in {"", ".", ".."} for part in context_path.split("/"))
        or any(ord(char) < 32 or ord(char) == 127 for char in context_path)
    ):
        return result
    matches = [
        (position, item) for position, item in enumerate(plan.project_context.items)
        if item.path.replace("\\", "/") == context_path
    ]
    if len(matches) != 1:
        result["diagnostic"] = "SOURCE_MISSING_OR_AMBIGUOUS"
        return result
    position, item = matches[0]
    if item.kind != "explicit_task_file" or item.trust != "project_evidence":
        result["diagnostic"] = "SOURCE_NOT_EXPLICIT_PROJECT_EVIDENCE"
        return result
    if type(item.content) is not str:
        result["diagnostic"] = "SOURCE_CAPTURE_INVALID"
        return result
    try:
        data = item.content.encode("utf-8")
    except UnicodeEncodeError:
        result["diagnostic"] = "SOURCE_CAPTURE_INVALID"
        return result
    if (
        len(data) > 1_048_576 or type(item.bytes) is not int
        or len(data) != item.bytes or sha256_text(item.content) != item.sha256
    ):
        result["diagnostic"] = "SOURCE_CAPTURE_BINDING_MISMATCH"
        return result
    result.update(source_context_position=position, source_sha256=item.sha256)
    try:
        from prototypes.governance_assessment_offline_v1 import review_bytes
    except ImportError:
        result["diagnostic"] = "EVALUATOR_UNAVAILABLE"
        return result
    except Exception:
        result["diagnostic"] = "EVALUATOR_FAILED"
        return result
    try:
        report = review_bytes(data)
        # Fixed v1 output envelope: future/additional fields must not silently
        # enter the redacted handoff. This checks compatibility, not truth.
        fields = {"input_sha256", "authority", "dispatch_requested", "handling", "structure", "diagnostics"}
        if type(report) is dict and report.get("structure") == "CONSISTENT":
            fields.update({
                "declared_checks", "unresolved_required_checks", "declared_fail_checks",
                "unresolved_applicability_checks", "unknown_profile_facts", "unverified_pass_claims",
            })
        if (
            type(report) is not dict or set(report) != fields
            or report.get("structure") not in {"CONSISTENT", "INVALID"}
            or report.get("authority") != "none"
            or report.get("dispatch_requested") is not False
            or report.get("handling") not in {"REJECT_RECORD", "PRESERVE_UNKNOWN", "REQUIRE_REVIEW"}
            or report.get("input_sha256") != item.sha256
        ):
            result["diagnostic"] = "EVALUATOR_RESULT_INVALID"
            return result
    except Exception:
        # Optional advice must not print exception/source values or fail open.
        result["diagnostic"] = "EVALUATOR_FAILED"
        return result
    result.update(report=report, diagnostic="DERIVED_ADVISORY_ONLY")
    return result


def _plan_handoff(plan, loaded: list[dict], validation: dict, project: Path, *, governance_advisory_context: str | None = None) -> dict:
    """Return a redacted, stdout-safe R1 host handoff.

    Full plan packets retain selected Skill instructions for a same-user local
    handoff. Restricted Codex sandboxes can lack a usable temporary packet
    location, so this optional view carries only metadata needed to open the
    selected files. It never serializes instructions, project context, or
    credentials.
    """
    loaded_by_path: dict[str, list[dict]] = {}
    for item in loaded:
        path = item.get("path")
        if isinstance(path, str) and path:
            loaded_by_path.setdefault(_normalized_skill_path(path), []).append(item)
    selected_skills = []
    for resource in plan.selected:
        if resource.resource_type != "skill":
            continue
        matches = loaded_by_path.get(_normalized_skill_path(resource.path), [])
        item = matches[0] if len(matches) == 1 else {}
        sha256 = item.get("sha256")
        characters = item.get("characters")
        if not matches:
            load_status = "missing_load_evidence"
            loaded_successfully = False
        elif len(matches) != 1:
            load_status = "ambiguous_load_evidence"
            loaded_successfully = False
        elif "load_error" in item:
            load_status = "load_failed"
            loaded_successfully = False
        elif isinstance(sha256, str) and sha256 and isinstance(characters, int) and characters >= 0:
            load_status = "loaded"
            loaded_successfully = True
        else:
            load_status = "invalid_load_evidence"
            loaded_successfully = False
        selected_skills.append({
            "resource_id": resource.resource_id,
            "name": resource.name,
            "skill_md_path": resource.path,
            "sha256": sha256 if loaded_successfully else None,
            "characters": characters if loaded_successfully else None,
            "loaded": loaded_successfully,
            "load_status": load_status,
            "source_scope": resource.provenance.get("source_scope", resource.trust),
            "runtime_compatibility": resource.runtime_compatibility,
        })
    result = {
        "schema_version": "nexus.plan-handoff.v1",
        "product": {"name": PRODUCT_NAME, "subtitle": PRODUCT_SUBTITLE},
        "project_root": str(project),
        "task_profile": {
            "task_type": plan.task_profile.task_type,
            "required_capabilities": plan.task_profile.required_capabilities,
        },
        "selected_skills": selected_skills,
        "execution_steps": [
            {
                "step_id": step.step_id,
                "capability": step.capability,
                "selected_resource_name": step.selected_resource_name,
                "reason": step.reason,
                "dependencies": step.dependencies,
                "validation": step.validation,
            }
            for step in plan.steps
        ],
        "validation_checks": plan.validation_plan.checks,
        "advisory_agents": [item.name for item in plan.advisory_agents],
        "fallback": plan.fallback,
        "prohibited_operations": [
            "automatic_skill_install_or_update",
            "automatic_skill_command_execution",
            "automatic_agent_delegation",
            "cross_project_scanning",
            "credential_or_raw_skill_content_disclosure",
        ],
        "plan_validation": validation,
    }
    if governance_advisory_context is not None:
        result["governance_advisory"] = _governance_advisory(plan, governance_advisory_context)
    return result


def _v2_catalog(project: Path, extra_roots: list[str]) -> dict:
    """Build a fresh V2 catalog with the actual local Codex Skill locations.

    This is intentionally V2-only.  V1.1's cached rescan/route/run behaviour
    remains unchanged, while the explicit V2 planner must not accidentally rely
    on a stale index created with an old --extra-root argument.
    """
    codex_home = Path.home() / ".codex"
    defaults = [ROOT.parent, codex_home / "skills", codex_home / "plugins" / "cache"]
    roots = [path for path in [*defaults, *[Path(item) for item in extra_roots]] if path.exists()]
    return build_index(project, ROOT, roots)


def rescan(workspace: Path, extra_roots: list[str]) -> dict:
    index = build_index(workspace, ROOT, [Path(item) for item in extra_roots])
    write_json(ROOT / "state" / "installed-skills.json", {key: index[key] for key in ("schema_version", "generated_at_utc", "workspace_root", "scan_roots", "skills", "duplicate_resolutions")})
    write_json(ROOT / "state" / "installed-agents.json", {key: index[key] for key in ("schema_version", "generated_at_utc", "workspace_root", "scan_roots", "agents")})
    return index


def load_index(workspace: Path, extra_roots: list[str], refresh: bool) -> dict:
    path = ROOT / "state" / "installed-skills.json"
    skills = read_json(path, {})
    agents = read_json(ROOT / "state" / "installed-agents.json", {})
    if refresh or not skills or skills.get("workspace_root") != str(workspace):
        return rescan(workspace, extra_roots)
    return {**skills, "agents": agents.get("agents", [])}


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Nexus — Adaptive AI Capability Hub (compatible Adaptive Skills Hub V1.1/V1.2 commands)")
    cli.add_argument("--workspace", help="Workspace to scan; defaults to the Hub parent directory")
    cli.add_argument("--extra-root", action="append", default=[], help="Additional local root to scan")
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("rescan", help="Discover local SKILL.md files and agent definitions")
    route = sub.add_parser("route", help="Rank local skills for a task without loading their full instructions")
    route.add_argument("task")
    route.add_argument("--max-skills", type=int, default=3)
    run = sub.add_parser("run", help="Route, fully load selected SKILL.md files, and execute explicit safe hooks")
    run.add_argument("task")
    run.add_argument("--max-skills", type=int, default=3)
    run.add_argument("--allow-skill-commands", action="store_true", help="Run selected skills' explicit hub_command arrays with shell disabled")
    run.add_argument("--packet", help="Write the full loaded work packet to this JSON path")
    plan = sub.add_parser("plan", help="V1.2: build an auditable capability plan without executing Skills")
    plan.add_argument("task")
    plan.add_argument("--project", help="Project root for bounded V1.2 context discovery; defaults to the current directory")
    plan.add_argument("--packet", help="Write the V1.2 plan/evidence packet to this JSON path; incompatible with --handoff")
    plan.add_argument("--handoff", action="store_true", help="Print a redacted, strictly stateless host handoff JSON; no packets or persistent plan state are written")
    plan.add_argument("--governance-advisory-context", help="Optional non-authoritative review of one non-secret project-relative file already named in the task and captured in context; requires --handoff")
    plan.add_argument("--no-state", action="store_true", help="Do not write state/last-plan.json; implied by --handoff")
    plan.add_argument("--soft-context-files", type=int, default=8, help="Initial soft project-context file budget")
    plan.add_argument("--soft-context-kib", type=int, default=64, help="Initial soft project-context byte budget in KiB")
    plan.add_argument("--hard-context-files", type=int, default=50, help="Hard project-context file ceiling")
    plan.add_argument("--hard-context-kib", type=int, default=512, help="Hard project-context byte ceiling in KiB")
    sub.add_parser("status", help="Show current local index counts")
    host = sub.add_parser("core-host-plan", help="Prepare one read-only Git Host workflow; no tools invoked")
    host.add_argument("task")
    host.add_argument("--project", required=True)
    host.add_argument("--file", action="append", required=True, dest="files")
    host.add_argument("--task-dir", required=True, help="Fresh output directory outside the inspected repository")
    for name in ("core-host-next", "core-host-observe", "core-host-status"):
        command = sub.add_parser(name, help="Local Host intent/observation bookkeeping; never executes Git")
        command.add_argument("task_dir")
    project_core = sub.add_parser("core", help="Prepare a reusable local project profile; explicit approval required")
    project_core.add_argument("task")
    project_core.add_argument("--project", required=True)
    project_core.add_argument("--profile", choices=("python", "static-web", "evidence"))
    project_core.add_argument("--task-dir", help="New task package root; defaults to project .nexus/tasks/<id>")
    project_core.add_argument("--json", action="store_true", help="Machine-readable approval/state view")
    project_core.add_argument("--total-seconds", type=float, default=600)
    project_core.add_argument("--step-seconds", type=float, default=30)
    core = sub.add_parser("core-plan", help="Prepare an internal-alpha local hook plan; no execution")
    core.add_argument("task")
    core.add_argument("--project", required=True)
    core.add_argument("--catalog", required=True, help="Reviewed, hash-bound local hook catalog")
    core.add_argument("--task-dir", required=True, help="New local task-state directory")
    core.add_argument("--max-commands", type=int, default=12)
    core.add_argument("--total-seconds", type=float, default=120)
    core.add_argument("--step-seconds", type=float, default=20)
    resume = sub.add_parser("core-run", help="Execute/resume the explicitly approved local hook plan")
    resume.add_argument("task_dir")
    resume.add_argument("--approve", help="Exact approval SHA-256 printed by core-plan")
    resume.add_argument("--max-steps", type=int, help="Pause after this many verified steps")
    resume.add_argument("--progress", action="store_true", help="Bounded progress on stderr; final JSON stays compatible")
    for name in ("core-status", "core-cancel"):
        command = sub.add_parser(name, help="Inspect/cancel a Core internal-alpha task")
        command.add_argument("task_dir")
    from ash.managed_cli import add_commands
    add_commands(sub)
    return cli


def main() -> int:
    cli = parser()
    args = cli.parse_args()
    if args.command.startswith("core-host-"):
        from ash import core_host_loop as host
        from ash.core import CoreError
        from ash.core_host import LocalHookError
        from ash.core_capabilities import closed_object
        try:
            if args.command == "core-host-plan":
                state = host.prepare(args.task, Path(args.project), args.files, Path(args.task_dir))
                result = host.status(Path(args.task_dir))
            elif args.command == "core-host-next":
                result = host.next_action(Path(args.task_dir))
            elif args.command == "core-host-observe":
                raw = sys.stdin.buffer.read(65537)
                if len(raw) > 65536:
                    raise CoreError("Host observation exceeds byte bound")
                observation = json.loads(raw, object_pairs_hook=closed_object,
                    parse_constant=lambda value: (_ for _ in ()).throw(CoreError("Non-finite Host observation")))
                host.observe(Path(args.task_dir), observation)
                result = host.status(Path(args.task_dir))
            else:
                result = host.status(Path(args.task_dir))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] in {"prepared", "waiting_host", "completed", "completed_with_findings"} else 1
        except (CoreError, LocalHookError, OSError, ValueError, KeyError, TypeError) as exc:
            cli.error(str(exc))
    if args.command.startswith("managed-"):
        from ash.managed_cli import run_command
        from ash.core_host import LocalHookError
        try:
            return run_command(args)
        except (ValueError, LocalHookError, OSError, KeyError, TypeError) as exc:
            cli.error(str(exc))
    if args.command == "core" or args.command.startswith("core-"):
        from ash.core import CoreBudget, CoreError, prepare_task, read_task, request_cancel, run_task
        from ash.core_host import LocalHookError
        from ash.core_profiles import approval_summary, disposition, prepare_project, progress_line
        try:
            if args.command == "core":
                state, directory = prepare_project(args.task, Path(args.project),
                    directory=Path(args.task_dir) if args.task_dir else None, profile=args.profile,
                    budget=CoreBudget(total_seconds=args.total_seconds, step_seconds=args.step_seconds))
                if not args.json:
                    print(approval_summary(state, directory))
                    return 0 if state["status"] == "prepared" else 1
            elif args.command == "core-plan":
                state = prepare_task(args.task, Path(args.project), Path(args.catalog), Path(args.task_dir),
                                     CoreBudget(max_commands=args.max_commands, total_seconds=args.total_seconds,
                                                step_seconds=args.step_seconds))
            elif args.command == "core-run":
                if args.max_steps is not None and args.max_steps < 1:
                    cli.error("--max-steps must be positive")
                def progress(event):
                    line = progress_line(event)
                    if line:
                        print(line, file=sys.stderr, flush=True)
                state = run_task(Path(args.task_dir), approval=args.approve, max_steps=args.max_steps,
                                 progress=progress if args.progress else None)
            else:
                if args.command == "core-cancel":
                    request_cancel(Path(args.task_dir))
                state = read_task(Path(args.task_dir))
            view = {key: state[key] for key in (
                "task_id", "task", "status", "approval_sha256", "commands_used", "budget",
                "replans", "completed_steps", "blocker", "artifacts", "receipt")}
            view["steps"] = [{key: step[key] for key in ("id", "name", "status", "attempts")} for step in state["steps"]]
            view["current_step"] = state["inflight"] or next((step["id"] for step in state["steps"] if step["status"] != "completed"), None)
            view["plan_id"] = state["plan"]["plan_id"]
            view["operator_action"] = disposition(state)
            execution_directory = directory if args.command == "core" else Path(args.task_dir)
            view["cancel_requested"] = (execution_directory / "cancel.request").exists()
            if view["cancel_requested"] and state["status"] != "completed":
                view["operator_action"] = "MANUAL REVIEW REQUIRED"
            if args.command == "core":
                view["task_directory"] = str(directory)
                view["approval_summary"] = approval_summary(state, directory)
            print(json.dumps(view, ensure_ascii=False, indent=2))
            if args.command in {"core-status", "core-cancel"}:
                return 0
            successful = {"prepared"} if args.command in {"core", "core-plan"} else {"paused", "completed"}
            return 0 if state["status"] in successful else 1
        except (CoreError, LocalHookError, OSError, ValueError, KeyError, TypeError) as exc:
            cli.error(str(exc))
    workspace = _workspace(args.workspace)
    if args.command == "rescan":
        index = rescan(workspace, args.extra_root)
        _print_product_header()
        print(f"Index refreshed: {workspace}")
        print(f"Skills: {len(index['skills'])}; agents: {len(index['agents'])}")
        return 0
    if args.command == "status":
        index = load_index(workspace, args.extra_root, refresh=False)
        _print_product_header()
        print(f"Workspace: {index.get('workspace_root', workspace)}")
        print(f"Skills: {len(index.get('skills', []))}; agents: {len(index.get('agents', []))}")
        return 0
    if args.command == "plan":
        if args.handoff and args.packet:
            cli.error("--handoff is strictly stateless and cannot be combined with --packet")
        if args.governance_advisory_context is not None and not args.handoff:
            cli.error("--governance-advisory-context requires the stateless --handoff view")
        project = Path(args.project).resolve() if args.project else Path.cwd().resolve()
        index = _v2_catalog(project, args.extra_root)
        context_options = {
            "soft_file_budget": args.soft_context_files,
            "soft_byte_budget": args.soft_context_kib * 1024,
            "hard_file_ceiling": args.hard_context_files,
            "hard_byte_ceiling": args.hard_context_kib * 1024,
        }
        try:
            v2_plan = plan_task(args.task, index, project, context_options=context_options, sources=_sources())
        except (ValueError, SemanticRoutingError) as exc:
            cli.error(str(exc))
        loaded = load_plan_skills(v2_plan)
        validation = validate_plan(v2_plan, loaded)
        if not (args.no_state or args.handoff):
            write_plan_packet(ROOT / "state" / "last-plan.json", v2_plan, loaded, validation)
        if args.packet:
            write_plan_packet(Path(args.packet), v2_plan, loaded, validation)
        _print_product_header()
        print(f"Task: {_friendly_task_label(v2_plan.task_profile.task_type, v2_plan.task_profile.original_task)}")
        if v2_plan.selected:
            print("Skills:")
            for resource in v2_plan.selected:
                print(f"- {resource.name}")
        else:
            print("Skills: none selected")
        if v2_plan.advisory_agents:
            print("Advisory Agents (not executed):")
            for agent in v2_plan.advisory_agents:
                print(f"- {agent.name}")
        if v2_plan.fallback["status"] == "needed":
            missing = list(dict.fromkeys([
                *v2_plan.fallback.get("missing_capabilities", []),
                *v2_plan.fallback.get("missing_domains", []),
            ]))
            print(f"Fallback: native Codex capability required for {', '.join(missing)}")
        print("Validation:")
        for check in v2_plan.validation_plan.checks:
            print(f"- {_friendly_validation_label(check['kind'])}")
        print(f"Status: {validation['status']}")
        if args.handoff:
            print("Handoff:")
            print(json.dumps(_plan_handoff(v2_plan, loaded, validation, project, governance_advisory_context=args.governance_advisory_context), ensure_ascii=False, sort_keys=True))
        return 0
    index = load_index(workspace, args.extra_root, refresh=False)
    route = route_task(args.task, index, _sources(), args.max_skills)
    if args.command == "route":
        write_json(ROOT / "state" / "last-route.json", route)
        _print_product_header()
        print(f"Capabilities: {', '.join(route['capabilities'])}")
        if route["selected_skills"]:
            for position, skill in enumerate(route["selected_skills"], start=1):
                print(f"{position}. {skill['name']} ({skill['score']}) -> {skill['skill_md_path']}")
        else:
            print("No matching installed executable skill; use native Codex reasoning/tools.")
        return 0
    result = execute_route(route, allow_skill_commands=args.allow_skill_commands)
    write_json(ROOT / "state" / "last-run.json", result)
    if args.packet:
        write_packet(Path(args.packet), result)
    _print_product_header()
    print("Loaded skills:")
    for item in result["loaded_skills"]:
        print(f"- {item['name']}: {'failed' if 'load_error' in item else 'loaded'}")
    for item in result["execution"]:
        print(f"- {item['name']}: {item['status']}")
    return 0 if not any(item["status"] in {"load_failed", "command_failed"} for item in result["execution"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
