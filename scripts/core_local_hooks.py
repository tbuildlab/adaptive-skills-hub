"""Reviewed synthetic local task hooks. No network, credentials or descendant launch.

Copied into each demo Skill by core_local_demo.py. Each verifier independently
reads the actual artifact/project rather than accepting the execution status.
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import unittest
from pathlib import Path


def emit(status: str, **fields: object) -> None:
    print(json.dumps({"status": status, **fields}))


def analysis(project: Path) -> dict:
    raw = (project / "notes.txt").read_bytes()
    if len(raw) > 65536:
        raise ValueError("fixture input too large")
    text = raw.decode("utf-8")
    return {"lines": len(text.splitlines()), "words": len(text.split()),
            "source_sha256": hashlib.sha256(raw).hexdigest()}


def test_project(project: Path) -> tuple[bool, int]:
    # Load ONLY this fixed synthetic module; arbitrary project discovery is not used.
    raw = (project / "calc.py").read_text(encoding="utf-8")
    if raw not in {"def add(a, b):\n    return a - b\n", "def add(a, b):\n    return a + b\n"}:
        raise ValueError("project is not the reviewed synthetic fixture")
    namespace = {}
    exec(compile(raw, str(project / "calc.py"), "exec"), namespace)

    class AdditionTests(unittest.TestCase):
        def test_positive(self):
            self.assertEqual(namespace["add"](2, 3), 5)

        def test_negative(self):
            self.assertEqual(namespace["add"](-2, 3), 1)

    result = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(AdditionTests))
    return result.wasSuccessful(), result.testsRun


def main() -> None:
    context = json.load(sys.stdin)
    project = Path(context["project"])
    kind, phase = sys.argv[1:3]
    if kind == "research":
        data = analysis(project)
        if phase == "verify":
            emit("ok", verified=json.loads((project / "analysis.json").read_text(encoding="utf-8")) == data)
        else:
            (project / "analysis.json").write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
            emit("ok", data=data, artifacts=["analysis.json"])
    elif kind == "architecture":
        previous = context["inputs"]["local-research"]["data"]
        current = analysis(project)
        text = f"# Local evidence review\n\nSource lines: {current['lines']}\nSource words: {current['words']}\n"
        text += "\nScope: synthetic local project; no external architecture claims.\n"
        if previous != current:
            raise ValueError("upstream output does not match source")
        if phase == "verify":
            emit("ok", verified=(project / "review.md").read_text(encoding="utf-8") == text)
        else:
            (project / "review.md").write_text(text, encoding="utf-8")
            emit("ok", data={"upstream_source": previous["source_sha256"]}, artifacts=["review.md"])
    elif kind == "backend":
        if phase == "repair":
            (project / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
            emit("ok", data={"repair": "fixed synthetic addition"})
        else:
            passed, count = test_project(project)
            if phase == "verify":
                emit("ok", verified=passed and count == 2)
            elif passed:
                emit("ok", data={"tests_run": count, "passed": passed}, artifacts=["calc.py"])
            else:
                emit("error", failure_kind="implementation_defect", retryable=True,
                     data={"tests_run": count, "passed": False})
    elif kind == "testing":
        passed, count = test_project(project)
        data = {"passed": passed, "tests_run": count}
        if phase == "verify":
            emit("ok", verified=passed and json.loads((project / "test-results.json").read_text(encoding="utf-8")) == data)
        else:
            (project / "test-results.json").write_text(json.dumps(data) + "\n", encoding="utf-8")
            emit("ok" if passed else "error", data=data, artifacts=["test-results.json"], retryable=False)
    else:
        raise ValueError("unsupported fixed fixture operation")


if __name__ == "__main__":
    main()
