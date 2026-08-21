#!/usr/bin/env python3
"""Run V1.1's final read-only route/load smoke suite against the real index."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ash.common import utc_now, write_json  # noqa: E402
from ash.execution import execute_route, write_packet  # noqa: E402
from ash.router import route_task  # noqa: E402


CASES = [
    ("presentation", "Create an editable PowerPoint presentation about digital transformation in business.", ["presentation"], ["ppt-master"]),
    ("document", "Improve and format this Word report.", ["document"], ["documents"]),
    ("spreadsheet", "Inspect this Excel workbook and verify its formulas.", ["spreadsheet"], ["Spreadsheets"]),
    ("pdf", "Create and validate a PDF report.", ["testing", "document", "pdf"], ["pdf"]),
    ("frontend", "Improve accessibility in this React dashboard component.", ["frontend"], ["emil-design-eng"]),
    ("engineering_chain", "Diagnose an API HTTP 500 failure and add a regression test.", ["backend", "testing"], ["evidence-driven-backend-debugging", "regression-first-testing"]),
    ("security", "Review this Python API for authorization weaknesses.", ["backend", "security"], ["security-best-practices"]),
    ("research_architecture", "Design an architecture for an AI research assistant.", ["research"], ["evidence-first-research"]),
    ("research_document_chain", "Research and verify evidence for a business assignment, then create an editable Word report.", ["research", "document"], ["evidence-first-research", "documents"]),
    ("native_fallback", "Repair a COBOL mainframe batch job.", ["general"], []),
]


def main() -> int:
    skills_index = json.loads((ROOT / "state" / "installed-skills.json").read_text(encoding="utf-8"))
    agents_index = json.loads((ROOT / "state" / "installed-agents.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))["sources"]
    skills_index["agents"] = agents_index["agents"]
    out_dir = ROOT / "output" / "v1.1-final"
    packet_dir = out_dir / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []
    failures: list[str] = []
    for case_id, task, expected_capabilities, expected_skills in CASES:
        route = route_task(task, skills_index, sources)
        result = execute_route(route)
        selected = [item["name"] for item in route["selected_skills"]]
        statuses = [item["status"] for item in result["execution"]]
        passed = (
            route["capabilities"] == expected_capabilities
            and selected == expected_skills
            and all(status == "loaded_for_codex_execution" for status in statuses)
            and (route["no_matching_skill"] if not expected_skills else not route["no_matching_skill"])
        )
        if not passed:
            failures.append(case_id)
        write_packet(packet_dir / f"{case_id}.json", result)
        summaries.append({
            "id": case_id,
            "task": task,
            "expected_capabilities": expected_capabilities,
            "detected_capabilities": route["capabilities"],
            "expected_skills": expected_skills,
            "selected_skills": selected,
            "selected_agents": [item["name"] for item in route["selected_agents"]],
            "external_candidates": [item["id"] for item in route["external_candidates"]],
            "skipped_sources": route["skipped_sources"],
            "rejected_skills": route["rejected_skills"],
            "execution_statuses": statuses,
            "packet": str(packet_dir / f"{case_id}.json"),
            "passed": passed,
        })
    summary = {
        "generated_at_utc": utc_now(),
        "mode": "read-only full SKILL.md load; no Skill command hooks authorized",
        "case_count": len(summaries),
        "passed_count": len(summaries) - len(failures),
        "failed_cases": failures,
        "cases": summaries,
    }
    write_json(out_dir / "summary.json", summary)
    print(f"Final smoke: {summary['passed_count']}/{summary['case_count']} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
