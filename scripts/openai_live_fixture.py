#!/usr/bin/env python3
"""Prepare one non-secret first-live-test fixture. NO PROVIDER REQUESTS."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ash.openai_hosted import BUG, TESTS, SPEC, MODEL, prepare_openai, serialize_request
from ash.managed_execution import _directory
from ash.openai_cli import summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="New disposable directory outside a Git repository")
    args = parser.parse_args()
    root = _directory(Path(args.directory))
    if root.exists():
        parser.error("preserve prior fixture; directory must be new")
    project = root / "project"
    project.mkdir(parents=True)
    (project / "calculator.py").write_bytes(BUG)
    (project / "test_calculator.py").write_bytes(TESTS)
    spec = {"schema": SPEC, "category": "coding", "files": ["calculator.py", "test_calculator.py"],
        "effects": ["output_artifacts"], "artifacts": [{"path": "calculator.py", "verification": "owner_review", "expected_sha256": None}],
        "ttl_seconds": 3600, "verification": "python_add_fixture_v1",
        "provider": {"model": MODEL, "reasoning": "high", "max_polls": 10, "max_output_tokens": 2048,
                     "max_tool_calls": 6, "soft_spend_usd": 0.10}}
    (root / "spec.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    state = prepare_openai("Fix calculator.py so existing tests pass. Do not change tests. Return corrected source and shell evidence.",
                           project, spec, root / "execution")
    body = serialize_request(state)
    (root / "prepared-request.json").write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**summary(state), "demonstration": "PREPARATION_ONLY_NO_DISPATCH",
                      "task_directory": str(root / "execution")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
