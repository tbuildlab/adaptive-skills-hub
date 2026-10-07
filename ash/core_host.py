"""Opt-in local command-hook client; not a sandbox or qualified production Host."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator


class LocalHookError(RuntimeError):
    pass


def _object(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate result field")
        value[key] = item
    return value


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON value")


@contextmanager
def exclusive_run(directory: Path) -> Iterator[None]:
    """OS-held lock: process death releases it; recovery never deletes a live lock."""
    path = directory / "run.lock"
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise LocalHookError("another Core runner owns this task") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def invoke(command: list[str], context: dict, *, cwd: Path, temporary: Path,
           timeout: float, output_limit: int, cancelled: Callable[[], bool]) -> dict:
    """Only the bound Python script form is supported; no shell, PATH search or model."""
    if len(command) < 2 or command[0] != sys.executable:
        raise LocalHookError("only explicit current-Python script hooks are supported")
    environment = {name: os.environ[name] for name in ("SystemRoot", "WINDIR") if name in os.environ}
    environment.update({"TEMP": str(temporary), "TMP": str(temporary),
                        "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
    # Stdout/stderr spool to bounded, transient local files rather than an unbounded pipe.
    raw_input = json.dumps(context, ensure_ascii=False).encode("utf-8")
    if len(raw_input) > 262144:
        raise LocalHookError("hook input exceeded the bounded handoff size")
    with tempfile.TemporaryFile(dir=temporary) as stdin, tempfile.TemporaryFile(dir=temporary) as stdout, tempfile.TemporaryFile(dir=temporary) as stderr:
        stdin.write(raw_input)
        stdin.seek(0)
        process = subprocess.Popen(command, cwd=cwd, env=environment, shell=False,
                                   close_fds=True, stdin=stdin, stdout=stdout, stderr=stderr)
        started = time.monotonic()
        reason = None
        try:
            while process.poll() is None:
                if cancelled():
                    reason = "cancelled"
                elif time.monotonic() - started >= timeout:
                    reason = "timeout"
                elif os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size > output_limit:
                    reason = "output_limit"
                if reason:
                    process.terminate()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=1)
                    break
                time.sleep(0.02)
            if os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size > output_limit:
                reason = reason or "output_limit"
            stdout.seek(0)
            raw = stdout.read(output_limit)
            # Do not persist raw stderr or malformed stdout (potentially sensitive).
            outcome = {"returncode": process.returncode, "stop_reason": reason,
                       "elapsed_seconds": time.monotonic() - started}
            if reason:
                return outcome
            try:
                value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object, parse_constant=_reject_constant)
                if not isinstance(value, dict) or not isinstance(value.get("status"), str) or value["status"] not in {"ok", "error", "boundary"}:
                    raise ValueError("invalid hook result")
                if "failure_kind" in value and (not isinstance(value["failure_kind"], str) or not 1 <= len(value["failure_kind"]) <= 80):
                    raise ValueError("invalid failure classification")
                if any(key in value and type(value[key]) is not bool for key in ("retryable", "no_effect", "verified")):
                    raise ValueError("invalid result flags")
                outcome["result"] = value
            except (UnicodeDecodeError, ValueError, RecursionError):
                outcome["result_error"] = "malformed_result"
            return outcome
        except BaseException:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=1)
            raise
