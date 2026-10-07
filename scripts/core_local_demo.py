"""Create new synthetic projects; optionally execute three explicit safe Core demos."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ash.core import CoreBudget, prepare_task, run_task  # noqa: E402

TASKS = {
    "A": "Research evidence in local project files.",
    "B": "Fix the failing backend API regression tests.",
    "C": "Research local project evidence and review the software architecture.",
}


def create_fixture(destination: Path, scenario: str) -> tuple[Path, Path]:
    """The destination must be NEW; never modify an existing user project."""
    destination.mkdir(parents=True, exist_ok=False)
    project = destination / "project"
    project.mkdir()
    (project / "notes.txt").write_text("Nexus local evidence.\nA deterministic synthetic project.\n", encoding="utf-8")
    (project / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    hook = (ROOT / "scripts" / "core_local_hooks.py").read_bytes()
    specifications = [
        ("local-research", "research", ["general_research", "software_research"], ["research"], []),
        ("local-architecture", "architecture", ["architecture_review"], ["review"], ["local-research"]),
        ("local-backend", "backend", ["backend_repair"], ["software_debug"], []),
        ("local-testing", "testing", ["software_testing"], ["software_test"], ["local-backend"]),
    ]
    entries = []
    for name, kind, domains, task_kinds, after in specifications:
        if scenario == "A" and kind != "research" or scenario == "B" and kind not in {"backend", "testing"} or scenario == "C" and kind not in {"research", "architecture"}:
            continue
        folder = destination / "catalog" / name
        folder.mkdir(parents=True)
        metadata = (f"---\nname: {name}\ndescription: Fixed synthetic local {kind} task\n"
                    f"hub_command: {json.dumps(['{python}', 'hook.py', kind, 'execute'])}\n"
                    f"hub_validate: {json.dumps(['{python}', 'hook.py', kind, 'verify'])}\n"
                    f"hub_after: {json.dumps(after)}\n")
        if kind == "backend":
            metadata += f"hub_repair: {json.dumps(['{python}', 'hook.py', kind, 'repair'])}\n"
        (folder / "SKILL.md").write_text(metadata + "---\n\n# Fixed local demo\n\nUse only the synthetic project in this demo.\n", encoding="utf-8")
        (folder / "hook.py").write_bytes(hook)
        entries.append({"skill": f"{name}/SKILL.md", "authority": "owner_local", "retry_safe": kind == "backend",
                        "bindings": {file: hashlib.sha256((folder / file).read_bytes()).hexdigest() for file in ("SKILL.md", "hook.py")},
                        "applicability": {"supported_domains": domains, "supported_task_kinds": task_kinds}})
    catalog = destination / "catalog" / "catalog.json"
    catalog.write_text(json.dumps({"schema": "nexus.core.catalog.v1", "skills": entries}, indent=2) + "\n", encoding="utf-8")
    return project, catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--run", action="store_true", help="Explicitly authorize ONLY these reviewed synthetic local demos")
    args = parser.parse_args()
    results = {}
    for scenario, task in TASKS.items():
        root = args.destination / scenario
        project, catalog = create_fixture(root, scenario)
        state = prepare_task(task, project, catalog, root / "task", CoreBudget(total_seconds=180))
        if args.run:
            state = run_task(root / "task", approval=state["approval_sha256"])
        results[scenario] = state["receipt"] or {"status": state["status"], "approval_sha256": state["approval_sha256"]}
    print(json.dumps(results, indent=2))
    return 0 if all(item["status"] == ("completed" if args.run else "prepared") for item in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
