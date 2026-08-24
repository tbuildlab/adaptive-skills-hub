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
from .redaction import safe_catalog, safe_enhancement_handoff, safe_health, safe_host_handoff, safe_plan
from .schemas import (
    NexusMcpError,
    parse_discover_request,
    parse_plan_request,
    parse_prepare_enhancement_handoff_request,
    parse_prepare_host_handoff_request,
)

ROOT = Path(__file__).resolve().parents[2]
MAX_SELECTED_SKILL_BYTES = 128 * 1024
MAX_SELECTED_SKILLS_BYTES = 256 * 1024
SOFT_PLANNING_SECONDS = 15.0
R4_HOST_CAPABILITY_PREFIX = "r4_host_capability:"
R4_PRESENTATIONS_CONSTRAINT = "r4_host_capability:presentations"


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
        # ``build_index`` always scans ``workspace_root`` itself.  Passing that
        # same root again as an additional source produces equal-authority
        # duplicate records for every project Skill, which then fail closed as
        # ``duplicate_conflict`` and cannot be selected by the planner.
        roots = [path for path in [codex_home / "skills", codex_home / "plugins" / "cache"] if path.exists()]
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

    @staticmethod
    def _catalog_for_request(index: Mapping[str, Any], request: Any) -> Mapping[str, Any]:
        """Apply the narrow R4 host capability allowlist, if explicitly requested.

        This does not alter V1.2 ranking for ordinary plans.  The R4 Desktop
        Skill adds the constraint only when it is asking for a host-owned
        Presentations execution handoff.  No caller can use this mechanism to
        select an arbitrary Skill: the sole supported value is Presentations.
        """
        host_constraints = [
            item.casefold() for item in request.constraints
            if item.casefold().startswith(R4_HOST_CAPABILITY_PREFIX)
        ]
        if not host_constraints:
            return index
        if host_constraints != [R4_PRESENTATIONS_CONSTRAINT]:
            raise NexusMcpError("INVALID_REQUEST", "R4 host capability constraint is unsupported")
        skills = index.get("skills")
        if not isinstance(skills, list):
            raise NexusMcpError("NEXUS_UNAVAILABLE", "capability catalog is unavailable")
        restricted = [item for item in skills if str(item.get("name", "")).casefold() == "presentations"]
        return {**index, "skills": restricted}

    def _plan_and_load(self, request: Any) -> tuple[Any, list[dict[str, Any]], dict[str, Any]]:
        workspace = self.authorizer.resolve(request.workspace_id)
        index = self.catalog_builder()
        if not isinstance(index.get("skills"), list) or len(index["skills"]) > 1024:
            raise NexusMcpError("NEXUS_UNAVAILABLE", "capability catalog is unavailable")
        index = self._catalog_for_request(index, request)
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
        return plan, loads, validation

    @staticmethod
    def _load_fingerprint(loads: list[Mapping[str, Any]]) -> tuple[tuple[str, str, int], ...]:
        """Keep internal loader evidence stable without exposing paths externally."""
        evidence: list[tuple[str, str, int]] = []
        for item in loads:
            path, digest, characters = item.get("path"), item.get("sha256"), item.get("characters")
            if not isinstance(path, str) or not isinstance(digest, str) or not isinstance(characters, int):
                raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill load evidence could not be verified")
            evidence.append((path.casefold(), digest, characters))
        return tuple(sorted(evidence))

    def plan(self, arguments: Any) -> dict[str, Any]:
        plan, loads, validation = self._plan_and_load(parse_plan_request(arguments))
        return safe_plan(plan, loads, validation, str(uuid4()))

    def prepare_host_handoff(self, arguments: Any) -> dict[str, Any]:
        """Issue a read-only R4 intent after an independent plan/load recheck."""
        plan, first_loads, _ = self._plan_and_load(parse_prepare_host_handoff_request(arguments))
        # Do not trust an earlier in-memory load result when preparing a host
        # action.  A second guarded read catches an on-disk replacement between
        # selection and handoff without saving state or disclosing the file.
        verified_loads = load_plan_skills(
            plan, read_guard=self._read_selected_skill,
            max_file_bytes=MAX_SELECTED_SKILL_BYTES, max_total_bytes=MAX_SELECTED_SKILLS_BYTES,
        )
        if self._load_fingerprint(first_loads) != self._load_fingerprint(verified_loads):
            raise NexusMcpError("SKILL_INTEGRITY_FAILED", "selected Skill changed before host handoff")
        validation = validate_plan(plan, verified_loads)
        return safe_host_handoff(plan, verified_loads, validation)

    def prepare_enhancement_handoff(self, arguments: Any) -> dict[str, Any]:
        """Issue a read-only R5 intent from a fixed redacted Host state.

        This path intentionally does not re-run the planner or load a Skill.
        It has no artifact, workspace, subprocess, network, or execution
        authority. The Desktop Host must independently bind the result to its
        current validated R4 receipt before it can attempt an enhancement.
        """
        return safe_enhancement_handoff(parse_prepare_enhancement_handoff_request(arguments))
