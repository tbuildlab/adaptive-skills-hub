"""Bounded R2 governance-context reader; project text never grants authority."""
from __future__ import annotations

import re
from pathlib import Path

from ash.common import sha256_text
from ash.v2 import ContextItem, ProjectContext

from .authorization import AuthorizedWorkspace, guard_regular_file, verify_unchanged
from .schemas import NexusMcpError

MAX_CONTEXT_FILES = 12
MAX_CONTEXT_BYTES = 128 * 1024
MAX_CONTEXT_FILE_BYTES = 32 * 1024
GOVERNANCE_FILES = (
    "AGENTS.md", "PROJECT_RULES.md", "DECISIONS.md", "FROZEN-DECISIONS.md",
    "docs/architecture.md", "docs/decisions.md",
)
SECRET_VALUE_RE = re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token|credential|private[_-]?key)\b\s*(?:=|:)\s*[^\s#]{4,}")
SAFE_PROHIBITION_RE = re.compile(r"^\s*(?:must not|do not|don't|never|prohibit(?:ed)?)\b", re.I)


def _safe_rule_text(value: str) -> str:
    """Only negative governance constraints can influence the core planner."""
    lines = [line.strip() for line in value.splitlines() if SAFE_PROHIBITION_RE.match(line)]
    return "\n".join(lines)


class SafeContextReader:
    def __init__(self, workspace: AuthorizedWorkspace, mode: str) -> None:
        self.workspace = workspace
        self.mode = mode

    def __call__(self, project_root: Path, _task: str, **_options: int) -> ProjectContext:
        if project_root.resolve() != self.workspace.root:
            raise NexusMcpError("UNAUTHORIZED_WORKSPACE", "workspace is not authorized")
        context = ProjectContext(
            str(self.workspace.root),
            soft_file_budget=MAX_CONTEXT_FILES,
            soft_byte_budget=MAX_CONTEXT_BYTES,
            hard_file_ceiling=MAX_CONTEXT_FILES,
            hard_byte_ceiling=MAX_CONTEXT_BYTES,
        )
        if self.mode == "none":
            return context
        total = 0
        for relative in GOVERNANCE_FILES:
            candidate = self.workspace.root.joinpath(*relative.split("/"))
            if not candidate.exists():
                continue
            try:
                safe_path, before = guard_regular_file(candidate, [self.workspace.root])
                size = before.st_size
                if size > MAX_CONTEXT_FILE_BYTES:
                    context.skipped.append({"path": relative, "reason": "context_file_limit"})
                    continue
                if len(context.items) >= MAX_CONTEXT_FILES or total + size > MAX_CONTEXT_BYTES:
                    context.skipped.append({"path": relative, "reason": "context_aggregate_limit"})
                    continue
                raw = safe_path.read_bytes()
                verify_unchanged(safe_path, before)
                if b"\0" in raw[:4096]:
                    context.skipped.append({"path": relative, "reason": "binary_context_excluded"})
                    continue
                content = raw.decode("utf-8")
                if SECRET_VALUE_RE.search(content):
                    context.skipped.append({"path": relative, "reason": "secret_pattern_context_excluded"})
                    continue
            except NexusMcpError:
                context.skipped.append({"path": relative, "reason": "unsafe_context_excluded"})
                continue
            except (OSError, UnicodeDecodeError):
                context.skipped.append({"path": relative, "reason": "unreadable_context_excluded"})
                continue
            kind = "project_rule" if Path(relative).name.casefold() in {"agents.md", "project_rules.md", "decisions.md", "frozen-decisions.md"} else "project_evidence"
            planner_content = _safe_rule_text(content) if kind == "project_rule" else ""
            context.items.append(ContextItem(relative, kind, "project_instruction" if kind == "project_rule" else "project_evidence", sha256_text(content), size, "bounded_governance_context", planner_content))
            total += size
        return context
