#!/usr/bin/env python3
"""Adaptive Skills Hub V1.1 command line entry point."""
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

from ash.common import read_json, write_json  # noqa: E402
from ash.discovery import build_index  # noqa: E402
from ash.execution import execute_route, write_packet  # noqa: E402
from ash.router import route_task  # noqa: E402


def _workspace(value: str | None) -> Path:
    return Path(value).resolve() if value else ROOT.parent.resolve()


def _sources() -> list[dict]:
    return read_json(ROOT / "sources.json", {"sources": []}).get("sources", [])


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
    cli = argparse.ArgumentParser(description="Adaptive Skills Hub V1.1")
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
    sub.add_parser("status", help="Show current local index counts")
    return cli


def main() -> int:
    args = parser().parse_args()
    workspace = _workspace(args.workspace)
    if args.command == "rescan":
        index = rescan(workspace, args.extra_root)
        print(f"Rescanned {workspace}")
        print(f"Skills: {len(index['skills'])}; agents: {len(index['agents'])}")
        return 0
    index = load_index(workspace, args.extra_root, refresh=False)
    if args.command == "status":
        print(f"Workspace: {index.get('workspace_root', workspace)}")
        print(f"Skills: {len(index.get('skills', []))}; agents: {len(index.get('agents', []))}")
        return 0
    route = route_task(args.task, index, _sources(), args.max_skills)
    if args.command == "route":
        write_json(ROOT / "state" / "last-route.json", route)
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
    print("Loaded skills:")
    for item in result["loaded_skills"]:
        print(f"- {item['name']}: {'failed' if 'load_error' in item else 'loaded'}")
    for item in result["execution"]:
        print(f"- {item['name']}: {item['status']}")
    return 0 if not any(item["status"] in {"load_failed", "command_failed"} for item in result["execution"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
