"""Fixed Alpha 2 project hooks. Standard library only; trusted owner code, not isolation.

This file is copied byte-for-byte into a task's catalog and invoked with fixed
capability/phase/settings arguments. Natural-language task text is never code.
"""
from __future__ import annotations

import contextlib
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest

LIMIT = 262144
PROFILES = ("python", "static-web", "evidence")
IGNORED = {".git", ".nexus", "node_modules", ".venv", "venv", "__pycache__"}
PRIVATE = re.compile(r"(?:secret|credential|password|private[-_]key|cookie|oauth|token)", re.I)


class ScopeError(ValueError):
    pass


def closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ScopeError("duplicate configuration key")
        result[key] = value
    return result


def load_json(path: Path):
    if path.stat().st_size > LIMIT:
        raise ScopeError("configuration exceeds byte limit")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=closed_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ScopeError("non-finite value")))


def safe_path(root: Path, name: str) -> Path:
    if (not isinstance(name, str) or not name or len(name) > 240 or "\\" in name
            or ":" in name or any(ord(c) < 32 for c in name)):
        raise ScopeError("unsafe project-relative path")
    parts = name.split("/")
    if any(p in {"", ".", ".."} or p.startswith(".") or p.endswith((" ", "."))
           or PRIVATE.search(p) or p.split(".")[0].casefold() in {"con", "prn", "aux", "nul"}
           or re.fullmatch(r"(?:com|lpt)[1-9](?:\..*)?", p, re.I) for p in parts):
        raise ScopeError("private, reserved or traversing path refused")
    candidate = root / name
    for part in (candidate, *candidate.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ScopeError("reparse/linked project paths refused")
        if part == root:
            break
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ScopeError("project scope escaped")
    return candidate


def read_bytes(root, name):
    path = safe_path(root, name)
    if not path.is_file() or path.stat().st_size > LIMIT or path.stat().st_nlink > 1:
        raise ScopeError("input missing or exceeds byte limit")
    return path.read_bytes()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def python_files(root):
    """Bound source closure for ordinary small unittest projects; never inspect private files."""
    names = []
    for base, folders, files in os.walk(root, followlinks=False):
        folders[:] = sorted(f for f in folders if f not in IGNORED and not f.startswith("."))
        for folder in folders:
            safe_path(root, (Path(base) / folder).relative_to(root).as_posix())
        for name in sorted(files):
            if name.endswith(".py"):
                relative = (Path(base) / name).relative_to(root).as_posix()
                read_bytes(root, relative)
                names.append(relative)
                if len(names) > 64:
                    raise ScopeError("Python source closure exceeds 64 files")
    return sorted(names)


def config(root: Path, value: dict) -> dict:
    if not isinstance(value, dict) or set(value) - {"schema", "profile", "files", "patches", "tests", "checks", "output"}:
        raise ScopeError("unknown project configuration field; commands/executables forbidden")
    if value.get("schema") != "nexus.core.project.v1" or value.get("profile") not in PROFILES:
        raise ScopeError("unsupported project schema/profile")
    result = {"schema": value["schema"], "profile": value["profile"]}
    files = value.get("files", [])
    if (not isinstance(files, list) or not 1 <= len(files) <= 32
            or any(not isinstance(n, str) for n in files) or len({n.casefold() for n in files}) != len(files)):
        raise ScopeError("declare 1-32 distinct non-secret input files")
    for name in files:
        read_bytes(root, name).decode("utf-8")
    result["files"] = files
    output = value.get("output", "nexus-results")
    safe_path(root, output)
    if "/" in output or output.casefold() in {Path(n).parts[0].casefold() for n in files}:
        raise ScopeError("output must be a separate simple project directory")
    result["output"] = output
    patches = value.get("patches", [])
    if not isinstance(patches, list) or len(patches) > 8:
        raise ScopeError("at most eight exact text patches")
    paths = []
    for patch in patches:
        if not isinstance(patch, dict) or set(patch) != {"path", "old", "new"}:
            raise ScopeError("patch requires path/old/new only")
        if patch["path"] not in files or Path(patch["path"]).suffix not in {".py", ".html", ".css", ".txt", ".md"}:
            raise ScopeError("patch target must be a declared supported text input")
        if any(not isinstance(patch[k], str) or not 1 <= len(patch[k].encode("utf-8")) <= 8192 for k in ("old", "new")):
            raise ScopeError("patch replacement too large or empty")
        text = read_bytes(root, patch["path"]).decode("utf-8")
        if (patch["old"] == patch["new"] or not (
                text.count(patch["old"]) == 1 or (patch["old"] not in text and text.count(patch["new"]) == 1))):
            raise ScopeError("patch requires one original match or exactly the already-applied replacement")
        paths.append(patch["path"])
    if len(paths) != len(set(paths)):
        raise ScopeError("one patch per file required")
    result["patches"] = patches
    tests = value.get("tests", "tests")
    if value["profile"] == "python":
        safe_path(root, tests)
        if not (root / tests).is_dir() or not python_files(root):
            raise ScopeError("existing unittest directory/source required")
        if "checks" in value:
            raise ScopeError("HTML checks are not a Python capability")
        result["tests"] = tests
    elif "tests" in value:
        raise ScopeError("tests field is only supported by Python profile")
    checks = value.get("checks", [])
    if value["profile"] == "static-web":
        if not isinstance(checks, list) or not 1 <= len(checks) <= 16:
            raise ScopeError("declare 1-16 fixed HTML checks")
        for check in checks:
            if (not isinstance(check, dict) or set(check) != {"path", "contains"}
                    or check["path"] not in files or Path(check["path"]).suffix != ".html"
                    or not isinstance(check["contains"], str) or not 1 <= len(check["contains"]) <= 1024):
                raise ScopeError("HTML check requires declared .html path and bounded expected text")
        result["checks"] = checks
    elif "checks" in value:
        raise ScopeError("checks field is only supported by static-web profile")
    if value["profile"] == "evidence" and patches:
        raise ScopeError("evidence profile cannot edit inputs")
    return result


def snapshot(root, settings):
    names = set(settings["files"])
    if settings["profile"] == "python":
        names.update(python_files(root))
    if sum(len(read_bytes(root, n)) for n in names) > 1048576:
        raise ScopeError("project inputs exceed 1 MiB")
    inputs = {n: [sha(read_bytes(root, n))] for n in sorted(names)}
    for patch in settings["patches"]:
        text = read_bytes(root, patch["path"]).decode("utf-8")
        inputs[patch["path"]].append(sha(text.replace(patch["old"], patch["new"], 1).encode("utf-8")))
    return inputs


def check_inputs(root, settings):
    expected = settings["project_inputs"]
    if settings["profile"] == "python" and python_files(root) != settings["python_files"]:
        raise ScopeError("Python source membership changed after approval")
    for name, digests in expected.items():
        if sha(read_bytes(root, name)) not in digests:
            raise ScopeError("approved project input changed")


def write(root, name, data, *, replace=False):
    if len(data) > LIMIT:
        raise ScopeError("output too large")
    path = safe_path(root, name)
    if path.exists() and not replace:
        if path.is_file() and path.read_bytes() == data:
            return
        raise ScopeError("refusing to overwrite an existing artifact")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def patch_files(root, settings):
    # Validate every target before writing any; crash between writes still remains ambiguous.
    updates = []
    for patch in settings["patches"]:
        current = read_bytes(root, patch["path"])
        original = settings["project_inputs"][patch["path"]]
        if sha(current) == original[0]:
            updates.append((patch["path"], current.decode("utf-8").replace(patch["old"], patch["new"], 1).encode("utf-8")))
        elif sha(current) != original[-1]:
            raise ScopeError("patch target drift")
    for name, data in updates:
        write(root, name, data, replace=True)


def inventory(root, settings):
    return [{"path": name, "sha256": sha(read_bytes(root, name)),
             "lines": len(read_bytes(root, name).decode("utf-8").splitlines()),
             "bytes": len(read_bytes(root, name))} for name in settings["files"]]


def summary(root, settings):
    lines = ["# Local project evidence", "", "Deterministic source summary; no model inference.", ""]
    for entry in inventory(root, settings):
        first = next((line.strip() for line in read_bytes(root, entry["path"]).decode("utf-8").splitlines() if line.strip()), "(empty)")
        lines.extend([f"## {entry['path']}", f"Lines: {entry['lines']}; bytes: {entry['bytes']}",
                      f"SHA-256: {entry['sha256']}", f"First line: {first[:160]}", ""])
    return ("\n".join(lines) + "\n").encode("utf-8")


def python_check(root, settings):
    # Existing owner-reviewed tests execute in this isolated hook process, not a shell.
    # They retain same-user authority. This is not a sandbox for unknown test code.
    sys.path.insert(0, str(root))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        suite = unittest.defaultTestLoader.discover(str(root / settings["tests"]), pattern="test_*.py")
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    return {"runner": "stdlib.unittest", "tests": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped),
            "passed": result.testsRun > 0 and result.wasSuccessful() and len(result.skipped) < result.testsRun}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.duplicates, self.title = set(), [], False

    def handle_starttag(self, tag, attrs):
        self.title |= tag == "title"
        identity = dict(attrs).get("id")
        if identity in self.ids:
            self.duplicates.append(identity)
        if identity:
            self.ids.add(identity)


def web_check(root, settings):
    checks = []
    for item in settings["checks"]:
        text = read_bytes(root, item["path"]).decode("utf-8")
        parser = Page()
        parser.feed(text)
        checks.append({"path": item["path"], "contains": item["contains"] in text,
                       "title_present": parser.title, "duplicate_ids": parser.duplicates})
    return {"checker": "fixed-html.v1", "checks": checks,
            "passed": all(c["contains"] and c["title_present"] and not c["duplicate_ids"] for c in checks)}


def main():
    capability, phase, filename = sys.argv[1:]
    settings = load_json(Path(filename))
    context = json.load(sys.stdin, object_pairs_hook=closed_object)
    root = Path(context["project"]).resolve(strict=True)
    try:
        check_inputs(root, settings)
        output = settings["output"]
        if phase == "repair":
            if capability != "python" or not settings["patches"]:
                raise ScopeError("repair unavailable")
            patch_files(root, settings)
            value = {"status": "ok"}
        elif capability in {"python", "static-web"}:
            if phase == "execute" and capability == "static-web":
                patch_files(root, settings)
            check = python_check(root, settings) if capability == "python" else web_check(root, settings)
            if not check["passed"]:
                if capability == "python" and (check["tests"] == 0 or check["errors"] or check["skips"] == check["tests"]):
                    value = {"status": "boundary", "failure_kind": "test_environment_or_coverage"}
                else:
                    value = {"status": "error", "failure_kind": "test_failure",
                             "retryable": capability == "python" and bool(settings["patches"]) and check["failures"] > 0}
            elif phase == "verify":
                name = f"{output}/checks.json"
                value = {"status": "ok", "verified": load_json(safe_path(root, name)) == check}
            else:
                name = f"{output}/checks.json"
                write(root, name, (json.dumps(check, sort_keys=True) + "\n").encode("utf-8"))
                value = {"status": "ok", "data": check, "artifacts": [name, *[p["path"] for p in settings["patches"]]]}
        elif capability == "inspect":
            name = f"{output}/inventory.json"
            expected = inventory(root, settings)
            if phase == "verify":
                value = {"status": "ok", "verified": load_json(safe_path(root, name)) == expected}
            else:
                write(root, name, (json.dumps(expected, sort_keys=True) + "\n").encode("utf-8"))
                value = {"status": "ok", "data": {"files": expected}, "artifacts": [name]}
        elif capability == "report":
            name = f"{output}/summary.md"
            expected = summary(root, settings)
            if context["inputs"].get("core-inspect", {}).get("data", {}).get("files") != inventory(root, settings):
                raise ScopeError("structured upstream inventory missing/mismatched")
            if phase == "verify":
                value = {"status": "ok", "verified": read_bytes(root, name) == expected}
            else:
                write(root, name, expected)
                value = {"status": "ok", "data": {"sources": settings["files"]}, "artifacts": [name]}
        else:
            raise ScopeError("unknown fixed capability")
    except (ScopeError, OSError, ValueError, KeyError) as exc:
        # No raw exception text, source, traceback or stderr is disclosed.
        value = {"status": "boundary", "failure_kind": "project_scope_or_environment"}
    print(json.dumps(value, ensure_ascii=False))
    return 0 if value["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
