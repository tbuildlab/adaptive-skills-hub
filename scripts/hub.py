#!/usr/bin/env python3
"""Nexus CLI, preserving Adaptive Skills Hub V1.1/V1.2 compatibility."""
from __future__ import annotations

import argparse
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

from ash.common import read_json, write_json  # noqa: E402
from ash.discovery import build_index  # noqa: E402
from ash.execution import execute_route, write_packet  # noqa: E402
from ash.router import route_task  # noqa: E402
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
    plan.add_argument("--packet", help="Write the V1.2 plan/evidence packet to this JSON path")
    plan.add_argument("--no-state", action="store_true", help="Do not write state/last-plan.json")
    plan.add_argument("--soft-context-files", type=int, default=8, help="Initial soft project-context file budget")
    plan.add_argument("--soft-context-kib", type=int, default=64, help="Initial soft project-context byte budget in KiB")
    plan.add_argument("--hard-context-files", type=int, default=50, help="Hard project-context file ceiling")
    plan.add_argument("--hard-context-kib", type=int, default=512, help="Hard project-context byte ceiling in KiB")
    sub.add_parser("status", help="Show current local index counts")
    return cli


def main() -> int:
    cli = parser()
    args = cli.parse_args()
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
        except ValueError as exc:
            cli.error(str(exc))
        loaded = load_plan_skills(v2_plan)
        validation = validate_plan(v2_plan, loaded)
        if not args.no_state:
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
            print(f"Fallback: native Codex capability required for {', '.join(v2_plan.fallback['missing_capabilities'])}")
        print("Validation:")
        for check in v2_plan.validation_plan.checks:
            print(f"- {_friendly_validation_label(check['kind'])}")
        print(f"Status: {validation['status']}")
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
