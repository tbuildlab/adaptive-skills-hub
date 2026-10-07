"""Create ordinary small local projects for Alpha 2; --run approves these fixtures only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ash.core import read_task, run_task  # noqa: E402
from ash.core_profiles import prepare_project  # noqa: E402

TASKS = {"python": "Fix the failing backend regression tests.",
         "static-web": "Improve HTML UI content and run regression tests.",
         "evidence": "Research local project evidence and review the software architecture."}


def fixture(root: Path, profile: str) -> Path:
    """New directory only; no user project is changed by fixture preparation."""
    root.mkdir(parents=True, exist_ok=False)
    if profile == "python":
        (root / "tests").mkdir()
        (root / "shipping.py").write_text("def net_total(amount, discount):\n    return amount - discount\n", encoding="utf-8")
        (root / "tests/test_shipping.py").write_text(
            "import unittest\nfrom shipping import net_total\n\n"
            "class ShippingTests(unittest.TestCase):\n"
            "    def test_normal_discount(self):\n        self.assertEqual(net_total(100, 20), 80)\n"
            "    def test_discount_cannot_make_total_negative(self):\n        self.assertEqual(net_total(10, 20), 0)\n"
            "    def test_zero(self):\n        self.assertEqual(net_total(0, 0), 0)\n", encoding="utf-8")
        value = {"files": ["shipping.py", "tests/test_shipping.py"], "tests": "tests",
                 "patches": [{"path": "shipping.py", "old": "return amount - discount", "new": "return max(0, amount - discount)"}]}
    elif profile == "static-web":
        (root / "index.html").write_text(
            '<!doctype html>\n<html lang="en"><head><title>Service page</title></head>\n'
            '<body><h1 id="service">Local service</h1><button id="quote">Book a consultation</button></body></html>\n', encoding="utf-8")
        value = {"files": ["index.html"],
                 "patches": [{"path": "index.html", "old": "Book a consultation", "new": "Request a service quote"}],
                 "checks": [{"path": "index.html", "contains": "Request a service quote"}]}
    elif profile == "evidence":
        for name, text in {"README.md": "# Sample project\nA local evidence fixture.\n",
                           "architecture.md": "# Architecture\nInput files feed one deterministic report.\n",
                           "notes.txt": "Known limitation: no external execution.\n"}.items():
            (root / name).write_text(text, encoding="utf-8")
        value = {"files": ["README.md", "architecture.md", "notes.txt"]}
    else:
        raise ValueError("unsupported fixture")
    value.update(schema="nexus.core.project.v1", profile=profile)
    (root / ".nexus.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return root


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("destination", type=Path)
    cli.add_argument("--run", action="store_true")
    args = cli.parse_args()
    result = {}
    for profile, task in TASKS.items():
        project = fixture(args.destination / profile, profile)
        state, directory = prepare_project(task, project)
        paused = None
        if args.run:
            if profile == "evidence":
                paused = run_task(directory, approval=state["approval_sha256"], max_steps=1)
                artifact = project / state["approval_context"]["output"] / "inventory.json"
                before = artifact.stat().st_mtime_ns
                state = run_task(directory, approval=read_task(directory)["approval_sha256"])
                assert before == artifact.stat().st_mtime_ns
            else:
                state = run_task(directory, approval=state["approval_sha256"])
        result[profile] = {"task_directory": str(directory), "status": state["status"],
                           "paused_status": paused["status"] if paused else None,
                           "receipt": state["receipt"], "events": state["events"]}
    args.destination.mkdir(parents=True, exist_ok=True)
    (args.destination / "alpha2-e2e-results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {"status": v["status"], "paused_status": v["paused_status"]} for k, v in result.items()}, indent=2))
    return 0 if all(v["status"] == ("completed" if args.run else "prepared") for v in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
