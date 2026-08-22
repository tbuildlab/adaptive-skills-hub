"""Thin R2 adapter over the existing Nexus discovery/planning/loader interfaces."""
from __future__ import annotations

from pathlib import Path
import time
from typing import Any, Callable, Mapping
from uuid import uuid4

from ash.discovery import build_index
from ash.v2 import load_plan_skills, plan_task, validate_plan

from .authorization import WorkspaceAuthorizer, guard_regular_file, verify_unchanged
from .context import SafeContextReader
from .redaction import safe_catalog, safe_health, safe_plan
from .schemas import NexusMcpError, parse_discover_request, parse_plan_request

ROOT = Path(__file__).resolve().parents[2]
MAX_SELECTED_SKILL_BYTES = 128 * 1024
MAX_SELECTED_SKILLS_BYTES = 256 * 1024
SOFT_PLANNING_SECONDS = 15.0


class NexusMcpRuntime:
    def __init__(
        self,
        authorizer: WorkspaceAuthorizer,
        *,
        catalog_builder: Callable[[], Mapping[str, Any]] | None = None,
        skill_roots: list[Path] | None = None,
    ) -> None:
        self.authorizer = authorizer
        self.catalog_builder = catalog_builder or self._build_catalog
        codex_home = Path.home() / ".codex"
        self.skill_roots = skill_roots or [ROOT.parent, codex_home / "skills", codex_home / "plugins" / "cache"]

    @staticmethod
    def _build_catalog() -> Mapping[str, Any]:
        codex_home = Path.home() / ".codex"
        roots = [path for path in [ROOT.parent, codex_home / "skills", codex_home / "plugins" / "cache"] if path.exists()]
        return build_index(ROOT.parent, ROOT, roots)

    def health(self) -> dict[str, Any]:
        return safe_health()

    def discover_capabilities(self, arguments: Any) -> dict[str, Any]:
        tags = parse_discover_request(arguments)
        index = self.catalog_builder()
        records = index.get("skills", [])
        if not isinstance(records, list) or len(records) > 1024:
            raise NexusMcpError("NEXUS_UNAVAILABLE", "capability catalog is unavailable")
        return safe_catalog(records, tags)

    def _read_selected_skill(self, path: Path) -> bytes:
        safe_path, before = guard_regular_file(path, self.skill_roots)
        try:
            raw = safe_path.read_bytes()
        except OSError as exc:
            raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill could not be read") from exc
        verify_unchanged(safe_path, before)
        return raw

    def plan(self, arguments: Any) -> dict[str, Any]:
        request = parse_plan_request(arguments)
        workspace = self.authorizer.resolve(request.workspace_id)
        index = self.catalog_builder()
        if not isinstance(index.get("skills"), list) or len(index["skills"]) > 1024:
            raise NexusMcpError("NEXUS_UNAVAILABLE", "capability catalog is unavailable")
        started = time.monotonic()
        plan = plan_task(
            request.task, index, workspace.root,
            user_requirements=request.constraints,
            context_reader=SafeContextReader(workspace, request.project_context_mode),
        )
        elapsed = time.monotonic() - started
        # The core planner is synchronous and bounded; it is intentionally not moved
        # to a background worker because a timed-out worker would retain request data.
        if elapsed > SOFT_PLANNING_SECONDS:
            raise NexusMcpError("TIMEOUT", "planning exceeded the configured time limit")
        loads = load_plan_skills(
            plan, read_guard=self._read_selected_skill,
            max_file_bytes=MAX_SELECTED_SKILL_BYTES, max_total_bytes=MAX_SELECTED_SKILLS_BYTES,
        )
        validation = validate_plan(plan, loads)
        return safe_plan(plan, loads, validation, str(uuid4()))
