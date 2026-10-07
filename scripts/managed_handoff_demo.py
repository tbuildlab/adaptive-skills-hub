#!/usr/bin/env python3
"""Real offline handoff demonstration. Does not simulate provider execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ash.managed_execution import _directory, execution_summary, export_handoff, prepare_execution
from ash.core_capabilities import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="New fixture/handoff directory")
    args = parser.parse_args()
    base = _directory(Path(args.directory))
    if base.exists():
        parser.error("demo directory must be new; preserve existing evidence")
    project = base / "project"
    project.mkdir(parents=True)
    (project / "README.md").write_text("Non-secret G2-OPENAI artifact-only handoff fixture.\n", encoding="utf-8", newline="\n")
    expected = b"Nexus owns verification.\n"
    spec = {"schema": "nexus.execution.spec.v1", "category": "coding", "files": ["README.md"],
            "effects": ["output_artifacts"], "artifacts": [{"path": "report.txt", "verification": "sha256",
            "expected_sha256": sha(expected)}], "ttl_seconds": 3600}
    (base / "spec.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    state = prepare_execution('Return report.txt containing exactly "Nexus owns verification." followed by LF.',
                              project, spec, base / "execution")
    # This script explicitly approves only the fixed fixture above; no user project.
    state = export_handoff(base / "execution", state["request_digest"])
    summary = execution_summary(state)
    summary.update(demonstration="REAL_OFFLINE_HANDOFF_ONLY", provider_execution="NOT_ATTEMPTED",
                   handoff=str(base / "execution" / "handoff-1.json"))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
