"""Text-only existing-file patches and a fixed disposable local coding verifier.

No general provider command execution or automatic live-project application.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .core import _atomic
from .core_capabilities import read_bytes, safe_path, sha
from .managed_execution import ExecutionError


def stage_patch(baseline: dict[str, bytes], patch: bytes, allowed: list[str]) -> dict[str, bytes]:
    """Strict unified diff: existing UTF-8 files only, exact contexts, no fuzz.

    The return value is a proposed replacement inventory, not a write capability.
    Full-file deletions, additions, binary patches, Git metadata and CRLF ambiguity
    are refused; returned replacements still need their approved verifier.
    """
    from .openai_hosted import _clean
    if len(patch) > 262144 or b"\r" in patch:
        raise ExecutionError("patch budget/newline constraint")
    _clean(patch)
    lines = patch.decode().splitlines(keepends=True)
    result, i = {}, 0
    while i < len(lines):
        if not lines[i].startswith("--- a/") or i + 1 >= len(lines) or not lines[i + 1].startswith("+++ b/"):
            raise ExecutionError("unsupported patch header/addition/deletion/binary")
        name = lines[i][6:].rstrip("\n")
        if lines[i + 1][6:].rstrip("\n") != name:
            raise ExecutionError("rename refused")
        safe_path(Path.cwd(), name)
        if name not in allowed or name not in baseline or name in result:
            raise ExecutionError("patch escaped approved existing-file scope")
        original = baseline[name].decode("utf-8").splitlines(keepends=True)
        output, cursor, hunks = [], 0, 0
        i += 2
        while i < len(lines) and lines[i].startswith("@@ "):
            match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n", lines[i])
            if not match:
                raise ExecutionError("malformed patch hunk")
            old, oldn, new, newn = [int(v) if v is not None else 1 for v in match.groups()]
            start = old - 1
            if start < cursor or start > len(original):
                raise ExecutionError("overlapping/out-of-baseline hunk")
            output.extend(original[cursor:start]); cursor = start
            if new - 1 != len(output):
                raise ExecutionError("new-file hunk position mismatch")
            before = after = 0; i += 1
            while i < len(lines) and lines[i][:1] in {" ", "+", "-"} and not lines[i].startswith("--- a/"):
                line = lines[i]
                if line[0] in {" ", "-"}:
                    if cursor >= len(original) or original[cursor] != line[1:]:
                        raise ExecutionError("patch baseline/context mismatch")
                    cursor += 1; before += 1
                if line[0] in {" ", "+"}:
                    output.append(line[1:]); after += 1
                i += 1
            if (before, after) != (oldn, newn):
                raise ExecutionError("patch hunk counts mismatch")
            hunks += 1
        output.extend(original[cursor:])
        replacement = "".join(output).encode()
        if not hunks or not replacement or len(replacement) > 262144:
            raise ExecutionError("empty/deleted/oversized replacement")
        _clean(replacement)
        result[name] = replacement
    if not result:
        raise ExecutionError("empty patch")
    return result


def verify_add_fixture(state, directory):
    """Only an independently reviewed AST may run; provider tests never execute.

    This verifier is deliberately limited to the first tiny coding workflow.
    General untrusted Python and arbitrary patches remain owner-review only.
    """
    from .openai_hosted import BUG, FIX, TESTS
    project = Path(state["project"])
    if (read_bytes(project, "calculator.py") != BUG or read_bytes(project, "test_calculator.py") != TESTS or
            state["request"]["project_scope"]["inputs"] != {"calculator.py": sha(BUG), "test_calculator.py": sha(TESTS)}):
        raise ExecutionError("fixed fixture baseline/test drift")
    raw = read_bytes(directory / "artifacts-1", "calculator.py")
    try:
        # Parse bytes, exactly as Python's file compiler does: encoding cookies
        # must not make execution differ from a UTF-8 string-only AST review.
        if ast.dump(ast.parse(raw), include_attributes=False) != ast.dump(ast.parse(FIX), include_attributes=False):
            raise ExecutionError("provider code exceeds fixed reviewed add-function AST")
    except (SyntaxError, UnicodeError):
        raise ExecutionError("invalid provider source") from None
    stage = safe_path(directory, "local-verification")
    if stage.exists():
        raise ExecutionError("verification interrupted; no silent rerun")
    stage.mkdir()
    _atomic(stage / "calculator.py", raw)
    _atomic(stage / "test_calculator.py", TESTS)
    runner = ("import sys,unittest; sys.path.insert(0,'.'); "
              "r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('.',pattern='test_calculator.py')); "
              "sys.exit(not r.wasSuccessful())")
    # No API credentials, arbitrary env inheritance, site hooks, stdin or shell.
    env = {k: os.environ[k] for k in ("SystemRoot", "WINDIR") if k in os.environ}
    process = subprocess.run([sys.executable, "-I", "-B", "-c", runner], cwd=stage,
        env=env, capture_output=True, stdin=subprocess.DEVNULL, timeout=10, close_fds=True)
    record = {"schema": "nexus.openai.local-verification.v1", "verifier": "python_add_fixture_v1",
        "source_sha256": sha(raw), "tests_sha256": sha(TESTS), "exit_code": process.returncode,
        "stdout_sha256": sha(process.stdout), "stderr_sha256": sha(process.stderr), "provider_commands_run_locally": False}
    _atomic(directory / "local-verification.json", (json.dumps(record, sort_keys=True) + "\n").encode())
    if process.returncode != 0:
        raise ExecutionError("local fixture tests failed")
    return "INDEPENDENT_FIXED_AST_AND_LOCAL_TESTS_PASSED"
