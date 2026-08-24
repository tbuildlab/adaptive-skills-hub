"""Pure R5 Host-owned adaptive enhancement protocol helpers.

The local MCP server may rank only this small, allowlisted mapping registry and
emit a redacted intent. It never sees an artifact, calls a Host tool, writes a
file, invokes a Skill, or preserves an execution receipt. The Host validates
the primary R4 receipt, creates a checkpoint, performs a native action, and
validates the outcome independently.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, MutableSet

from .handoff import validate_host_receipt
from .host_mapping import (
    PRESENTATIONS_ENHANCEMENT_MAPPING_ID,
    PRESENTATIONS_MAPPING_ID,
    presentation_enhancement_profiles,
)
from .schemas import HostArtifactState


ENHANCEMENT_HANDOFF_SCHEMA_VERSION = "nexus.host-enhancement-handoff.v1"
HOST_ARTIFACT_STATE_SCHEMA_VERSION = "nexus.host-artifact-state.v1"
HOST_NATIVE_PRESENTATIONS_ENHANCEMENT_MODE = "host_native_presentations_enhancement"
ENHANCEMENT_HANDOFF_TTL_SECONDS = 300


@dataclass(frozen=True)
class EnhancementDecision:
    """A deterministic, bounded decision with no arbitrary candidate input."""

    status: str
    reason_codes: tuple[str, ...]
    profile: Mapping[str, Any] | None = None


def enhancement_issue_window(now: datetime | None = None) -> tuple[str, str]:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    expiry = current + timedelta(seconds=ENHANCEMENT_HANDOFF_TTL_SECONDS)
    return current.isoformat().replace("+00:00", "Z"), expiry.isoformat().replace("+00:00", "Z")


def select_enhancement(state: HostArtifactState) -> EnhancementDecision:
    """Select at most one reviewed enhancement profile without re-routing Skills."""
    if state.enhancement_pass >= 1:
        return EnhancementDecision("no_enhancement_needed", ("enhancement_pass_budget_exhausted",))
    observations = set(state.observations)
    matching = [
        profile for profile in presentation_enhancement_profiles()
        if observations.intersection(profile["eligible_observations"])
    ]
    if not matching:
        return EnhancementDecision("no_enhancement_needed", ("no_high_value_host_mapped_enhancement",))
    # Higher vetted priority wins; stable candidate ID is the deterministic tie break.
    profile = sorted(matching, key=lambda item: (-int(item["priority"]), str(item["candidate_id"])))[0]
    reasons = tuple(sorted(observations.intersection(profile["eligible_observations"])))
    return EnhancementDecision("enhancement_requested", reasons, profile)


def is_current_enhancement_handoff(handoff: Mapping[str, Any], now: datetime | None = None) -> bool:
    if handoff.get("schema_version") != ENHANCEMENT_HANDOFF_SCHEMA_VERSION:
        return False
    handoff_id = handoff.get("handoff_id")
    expires_at = handoff.get("expires_at")
    if not isinstance(handoff_id, str) or not handoff_id or not isinstance(expires_at, str):
        return False
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if expiry.tzinfo is None:
        return False
    return (now or datetime.now(timezone.utc)).astimezone(timezone.utc) < expiry.astimezone(timezone.utc)


def validate_enhancement_receipt(
    enhancement_handoff: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    base_handoff: Mapping[str, Any],
    base_receipt: Mapping[str, Any],
    seen_handoff_ids: MutableSet[str] | None = None,
    now: datetime | None = None,
) -> str:
    """Validate a Host-owned R5 receipt without accepting authority from MCP.

    ``base_handoff`` and ``base_receipt`` stay on the Host side. They are
    supplied only to this pure helper, never to a Nexus MCP tool. This makes a
    claimed artifact state insufficient to impersonate a validated R4 result.
    """
    if validate_host_receipt(base_handoff, base_receipt, now=now) != "EXECUTION_SUCCEEDED":
        return "BASE_RECEIPT_INVALID"
    if not is_current_enhancement_handoff(enhancement_handoff, now):
        return "ENHANCEMENT_HANDOFF_EXPIRED"
    allowed = {
        "handoff_id", "candidate_id", "host_capability", "host_execution_mapping_id",
        "states", "result_code", "checkpoint_created", "artifact_ref", "artifact_kind",
        "rollback_status", "validation_checks", "improvement_assessment",
    }
    if not isinstance(receipt, Mapping) or set(receipt) - allowed:
        return "ENHANCEMENT_RECEIPT_MALFORMED"
    handoff_id = enhancement_handoff.get("handoff_id")
    if receipt.get("handoff_id") != handoff_id:
        return "ENHANCEMENT_HANDOFF_MISMATCH"
    if seen_handoff_ids is not None and isinstance(handoff_id, str):
        if handoff_id in seen_handoff_ids:
            return "ENHANCEMENT_HANDOFF_REPLAYED"
        seen_handoff_ids.add(handoff_id)
    selected = enhancement_handoff.get("selected_candidate")
    profile = enhancement_handoff.get("host_execution_profile")
    if not isinstance(selected, Mapping) or not isinstance(profile, Mapping):
        return "ENHANCEMENT_RECEIPT_MALFORMED"
    if receipt.get("candidate_id") != selected.get("candidate_id"):
        return "ENHANCEMENT_SUBSTITUTION_REJECTED"
    if receipt.get("host_capability") != enhancement_handoff.get("logical_host_capability"):
        return "HOST_CAPABILITY_UNAVAILABLE"
    if profile.get("mapping_id") != PRESENTATIONS_ENHANCEMENT_MAPPING_ID or receipt.get("host_execution_mapping_id") != profile.get("mapping_id"):
        return "ENHANCEMENT_MAPPING_MISMATCH"
    if enhancement_handoff.get("base_mapping_id") != PRESENTATIONS_MAPPING_ID:
        return "BASE_RECEIPT_INVALID"
    base_profile = base_handoff.get("host_execution_profile")
    if not isinstance(base_profile, Mapping) or base_profile.get("mapping_id") != enhancement_handoff.get("base_mapping_id"):
        return "BASE_RECEIPT_INVALID"
    states = receipt.get("states")
    required_prefix = [
        "base_execution_verified", "artifact_state_verified", "enhancement_requested",
    ]
    if not isinstance(states, list) or not all(isinstance(item, str) for item in states) or states[:3] != required_prefix:
        return "ENHANCEMENT_RECEIPT_MALFORMED"
    result_code = receipt.get("result_code")
    if result_code == "HOST_CAPABILITY_UNAVAILABLE":
        return "HOST_CAPABILITY_UNAVAILABLE" if states == required_prefix else "ENHANCEMENT_RECEIPT_MALFORMED"
    if result_code == "EXECUTION_REFUSED":
        return "EXECUTION_REFUSED" if states == required_prefix else "ENHANCEMENT_RECEIPT_MALFORMED"
    if result_code == "HOST_ROLLBACK_UNAVAILABLE":
        return "HOST_ROLLBACK_UNAVAILABLE" if states == required_prefix + ["rollback_unavailable"] else "ENHANCEMENT_RECEIPT_MALFORMED"
    if receipt.get("checkpoint_created") is not True:
        return "HOST_ROLLBACK_UNAVAILABLE"
    if result_code == "ENHANCEMENT_FAILED":
        expected = required_prefix + ["checkpoint_created", "enhancement_started", "enhancement_failed", "rollback_restored"]
        if states != expected or receipt.get("rollback_status") != "restored":
            return "ENHANCEMENT_RECEIPT_MALFORMED"
        return "ENHANCEMENT_FAILED_ROLLBACK_RESTORED"
    if result_code == "VALIDATION_FAILED":
        expected = required_prefix + ["checkpoint_created", "enhancement_started", "enhancement_succeeded", "revalidation_failed", "rollback_restored"]
        if states != expected or receipt.get("rollback_status") != "restored":
            return "ENHANCEMENT_RECEIPT_MALFORMED"
        return "VALIDATION_FAILED_ROLLBACK_RESTORED"
    if result_code == "NO_IMPROVEMENT":
        expected = required_prefix + ["checkpoint_created", "enhancement_started", "enhancement_succeeded", "revalidation_passed", "rollback_restored"]
        if states != expected or receipt.get("rollback_status") != "restored" or receipt.get("improvement_assessment") != "not_improved":
            return "ENHANCEMENT_RECEIPT_MALFORMED"
        return "NO_IMPROVEMENT_ROLLBACK_RESTORED"
    if result_code != "ENHANCEMENT_SUCCEEDED":
        return "ENHANCEMENT_RECEIPT_MALFORMED"
    if states != required_prefix + ["checkpoint_created", "enhancement_started", "enhancement_succeeded", "revalidation_passed"]:
        return "ENHANCEMENT_RECEIPT_MALFORMED"
    checks = receipt.get("validation_checks")
    if not isinstance(checks, Mapping) or checks != {"artifact_editable": "passed", "presentation_open_render": "passed"}:
        return "ENHANCEMENT_RECEIPT_MALFORMED"
    if not isinstance(receipt.get("artifact_ref"), str) or not receipt["artifact_ref"] or receipt.get("artifact_kind") != "pptx":
        return "ARTIFACT_MISSING"
    if receipt.get("improvement_assessment") != "improved":
        return "IMPROVEMENT_UNVERIFIED"
    return "ENHANCEMENT_SUCCEEDED"
