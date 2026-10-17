"""Thin R2 adapter over the existing Nexus discovery/planning/loader interfaces."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
import time
from typing import Any, Callable, Mapping
from uuid import uuid4

from ash.discovery import build_index
from ash.runtime_decision import RuntimeCapabilityAdapter, RuntimeDecisionError, parse_runtime_requirements
from ash.scout import ScoutError, ScoutRuntimeAdapter, parse_scout_request
from ash.reusable_references import LibrarySnapshot
from ash.v2 import load_plan_skills, plan_task, validate_plan

from .authorization import WorkspaceAuthorizer, guard_regular_file, verify_unchanged
from .context import SafeContextReader
from .host_inventory import (
    HOST_INVENTORY_TTL_SECONDS,
    MAX_OUTSTANDING_HOST_INVENTORY_TICKETS,
    HostCapabilityTicket,
)
from .redaction import (
    safe_catalog,
    safe_enhancement_handoff,
    safe_health,
    safe_host_capability_assessment,
    safe_host_inventory_ticket,
    safe_host_handoff,
    safe_plan,
)
from .schemas import (
    NexusMcpError,
    ensure_response_limit,
    parse_discover_request,
    parse_host_capability_snapshot,
    parse_host_capability_ticket_request,
    parse_host_inventory_ticket_id,
    parse_plan_request,
    parse_memory_plan_request,
    parse_prepare_enhancement_handoff_request,
    parse_prepare_host_handoff_request,
    parse_runtime_requirements_request,
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
        clock: Callable[[], datetime] | None = None,
        monotonic_clock: Callable[[], float] | None = None,
        capability_adapter: RuntimeCapabilityAdapter | None = None,
        scout_adapter: ScoutRuntimeAdapter | None = None,
        reference_library_reader: Callable[[], LibrarySnapshot] | None = None,
        project_memory_reader: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self.authorizer = authorizer
        self.reference_library_reader = reference_library_reader
        self.project_memory_reader = project_memory_reader
        self.catalog_builder = catalog_builder or self._build_catalog
        codex_home = Path.home() / ".codex"
        self.skill_roots = skill_roots or [ROOT.parent, codex_home / "skills", codex_home / "plugins" / "cache"]
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._monotonic_clock = monotonic_clock or time.monotonic
        self._host_inventory_ticket_lock = Lock()
        self._host_inventory_tickets: dict[str, tuple[HostCapabilityTicket, bool]] = {}
        self.capability_adapter = capability_adapter or RuntimeCapabilityAdapter(
            ROOT / "config" / "capability-foundation.json",
            ROOT / "config" / "upstream-source-registry.json",
            local_roots={
                # This is a machine-independent source-root convention. The
                # exact Skill path remains relative metadata and is re-hashed
                # before it can be selected. A packaged install normally lacks
                # this sibling library and therefore reports it unavailable.
                "emilkowalski-skills": ROOT.parent / "adaptive-skills-library",
            },
        )
        self.scout_adapter = scout_adapter or ScoutRuntimeAdapter(
            self.capability_adapter,
            root=ROOT,
        )

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

    def route_capabilities(self, arguments: Any) -> dict[str, Any]:
        """Run the additive Capability Foundation selector without execution."""
        requirements = parse_runtime_requirements_request(arguments)
        try:
            return ensure_response_limit(self.capability_adapter.decide(requirements))
        except RuntimeDecisionError as exc:
            raise NexusMcpError(
                "RUNTIME_CAPABILITY_DECISION_BLOCKED",
                "runtime capability decision failed closed",
            ) from exc

    def scout_candidates(self, arguments: Any) -> dict[str, Any]:
        """Discover recommendation-only candidates after an independently rechecked gap."""
        try:
            request = parse_scout_request(arguments, parse_requirements=parse_runtime_requirements)
            return ensure_response_limit(self.scout_adapter.scout(request))
        except ScoutError as exc:
            raise NexusMcpError(
                "SCOUT_ADMISSION_BLOCKED",
                "read-only candidate Scout failed closed",
            ) from exc

    def _purge_expired_host_inventory_tickets(
        self, monotonic_now: float, *, except_id: str | None = None,
    ) -> None:
        for ticket_id, (ticket, _consumed) in list(self._host_inventory_tickets.items()):
            if ticket_id != except_id and monotonic_now >= ticket.monotonic_deadline:
                del self._host_inventory_tickets[ticket_id]

    def begin_host_capability_assessment(self, arguments: Any) -> dict[str, Any]:
        """Issue a bounded one-use ticket from this stdio runtime instance."""
        request = parse_host_capability_ticket_request(arguments)
        with self._host_inventory_ticket_lock:
            monotonic_now = self._monotonic_clock()
            self._purge_expired_host_inventory_tickets(monotonic_now)
            if len(self._host_inventory_tickets) >= MAX_OUTSTANDING_HOST_INVENTORY_TICKETS:
                raise NexusMcpError("HOST_INVENTORY_BUSY", "Host inventory ticket capacity is temporarily exhausted")
            issued_at = self._clock().astimezone(timezone.utc)
            ticket = HostCapabilityTicket(
                ticket_id=str(uuid4()),
                issued_at=issued_at,
                expires_at=issued_at + timedelta(seconds=HOST_INVENTORY_TTL_SECONDS),
                monotonic_issued_at=monotonic_now,
                monotonic_deadline=monotonic_now + HOST_INVENTORY_TTL_SECONDS,
                host_surface=request.host_surface,
                inventory_scope=request.inventory_scope,
                inventory_completeness=request.inventory_completeness,
                task_category=request.task_category,
                required_interfaces=request.required_interfaces,
            )
            self._host_inventory_tickets[ticket.ticket_id] = (ticket, False)
        return safe_host_inventory_ticket(ticket)

    def _claim_host_inventory_ticket(self, ticket_id: str) -> tuple[HostCapabilityTicket, datetime]:
        with self._host_inventory_ticket_lock:
            monotonic_now = self._monotonic_clock()
            record = self._host_inventory_tickets.get(ticket_id)
            self._purge_expired_host_inventory_tickets(monotonic_now, except_id=ticket_id)
            if record is None:
                raise NexusMcpError("HOST_INVENTORY_TICKET_INVALID", "Host inventory ticket is invalid for this runtime")
            ticket, consumed = record
            if monotonic_now >= ticket.monotonic_deadline:
                del self._host_inventory_tickets[ticket_id]
                raise NexusMcpError("HOST_INVENTORY_TICKET_EXPIRED", "Host inventory ticket has expired")
            if consumed:
                raise NexusMcpError("HOST_INVENTORY_TICKET_REPLAYED", "Host inventory ticket was already used")
            # Claim before parsing the remaining snapshot. Malformed submissions
            # therefore cannot retry or probe against the same freshness token.
            self._host_inventory_tickets[ticket_id] = (ticket, True)
            effective_now = ticket.issued_at + timedelta(
                seconds=max(0.0, monotonic_now - ticket.monotonic_issued_at),
            )
            return ticket, effective_now

    def assess_host_capabilities(self, arguments: Any) -> dict[str, Any]:
        """Assess only a bounded current-turn Host metadata assertion.

        This method never enumerates Host state or turns the assertion into
        execution authority.  It is separate from the local Skill catalog.
        """
        ticket_id = parse_host_inventory_ticket_id(arguments)
        ticket, effective_now = self._claim_host_inventory_ticket(ticket_id)
        snapshot = parse_host_capability_snapshot(arguments, ticket=ticket)
        return safe_host_capability_assessment(snapshot, ticket, now=effective_now)

    def _read_selected_skill(self, path: Path) -> bytes:
        safe_path, before = guard_regular_file(path, self.skill_roots)
        try:
            raw = safe_path.read_bytes()
        except OSError as exc:
            raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill could not be read") from exc
        verify_unchanged(safe_path, before)
        return raw

    @staticmethod
    def _r4_presentations_catalog(index: Mapping[str, Any]) -> Mapping[str, Any]:
        skills = index.get("skills")
        if not isinstance(skills, list):
            raise NexusMcpError("NEXUS_UNAVAILABLE", "capability catalog is unavailable")
        restricted: list[dict[str, Any]] = []
        for item in skills:
            if str(item.get("name", "")).casefold() != "presentations":
                continue
            # The frozen R4 mapping narrows the candidate set, but it must not
            # manufacture semantic authority from a display name.  The normal
            # V2 path below still requires a manifest-bound registry rule (or
            # an already-trusted Nexus-owned in-memory applicability object).
            restricted.append(dict(item))
        return {**index, "skills": restricted}

    @staticmethod
    def _catalog_for_request(index: Mapping[str, Any], request: Any) -> Mapping[str, Any]:
        """Apply the narrow R4 host capability allowlist, if explicitly requested.

        This does not alter V1.2 ranking for ordinary plans.  No caller can use
        this mechanism to select an arbitrary Skill: the sole supported value
        is the frozen Presentations Host mapping.
        """
        host_constraints = [
            item.casefold() for item in request.constraints
            if item.casefold().startswith(R4_HOST_CAPABILITY_PREFIX)
        ]
        if not host_constraints:
            return index
        if host_constraints != [R4_PRESENTATIONS_CONSTRAINT]:
            raise NexusMcpError("INVALID_REQUEST", "R4 host capability constraint is unsupported")
        return NexusMcpRuntime._r4_presentations_catalog(index)

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
            reference_library_reader=self.reference_library_reader,
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
        from ash.project_memory_context import unavailable
        request, project_id = parse_memory_plan_request(arguments)
        plan, loads, validation = self._plan_and_load(request)
        memory = unavailable("project_memory_disabled" if request.project_context_mode == "none" else "project_memory_unavailable")
        if request.project_context_mode != "none" and self.project_memory_reader is not None:
            try:
                memory = self.project_memory_reader(self.authorizer.resolve(request.workspace_id), request.task, project_id)
            except Exception:
                # Memory availability is never planner authorization or a HOLD.
                memory = unavailable("project_memory_unavailable")
        return safe_plan(plan, loads, validation, str(uuid4()), project_memory=memory)

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
