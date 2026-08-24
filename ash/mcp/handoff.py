"""Pure, redacted R4 host-handoff lifecycle helpers.

The local MCP server only issues an execution *intent*.  It never receives an
artifact, invokes a host tool, or records host execution.  These helpers make
the short-lived intent explicit so the Desktop plugin can reject stale or
user-supplied copies before it asks the host to act.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, MutableSet

from .host_mapping import PRESENTATIONS_MAPPING_ID


HANDOFF_SCHEMA_VERSION = "nexus.host-handoff.v1"
PLAN_VERSION = "nexus.v2.plan.v1"
HOST_PRESENTATIONS_CAPABILITY = "chatgpt.presentations"
HOST_NATIVE_PRESENTATIONS_MODE = "host_native_presentations"
HANDOFF_TTL_SECONDS = 300


def issue_window(now: datetime | None = None) -> tuple[str, str]:
    """Return UTC issue/expiry timestamps for one host execution intent."""
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    expiry = current + timedelta(seconds=HANDOFF_TTL_SECONDS)
    return current.isoformat().replace("+00:00", "Z"), expiry.isoformat().replace("+00:00", "Z")


def is_current_handoff(handoff: Mapping[str, Any], now: datetime | None = None) -> bool:
    """Validate only freshness/shape; a host must also require current tool provenance.

    This intentionally cannot turn a copied envelope into an authorization
    token.  The host must obtain the envelope from the current MCP tool result,
    rather than from user text or an earlier turn.
    """
    if handoff.get("schema_version") != HANDOFF_SCHEMA_VERSION:
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
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return current < expiry.astimezone(timezone.utc)


def validate_host_receipt(
    handoff: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    seen_handoff_ids: MutableSet[str] | None = None,
    now: datetime | None = None,
) -> str:
    """Validate a host-produced receipt without performing or authorizing work.

    This is a protocol validator for local integration tests and future host
    adapters.  It is deliberately not exposed as an MCP tool and does not
    persist receipt data.  A host may supply a per-chat ``seen_handoff_ids`` set
    to reject a second use of the same short-lived intent.
    """
    allowed = {
        "handoff_id", "selected_skill", "content_sha256", "host_capability",
        "host_execution_mapping_id", "input_resolution", "states", "result_code",
        "artifact_ref", "artifact_kind",
    }
    if not is_current_handoff(handoff, now) or not isinstance(receipt, Mapping) or set(receipt) - allowed:
        return "HANDOFF_MALFORMED" if is_current_handoff(handoff, now) else "HANDOFF_EXPIRED"
    handoff_id = handoff.get("handoff_id")
    if receipt.get("handoff_id") != handoff_id:
        return "HANDOFF_MISMATCH"
    if seen_handoff_ids is not None and isinstance(handoff_id, str):
        if handoff_id in seen_handoff_ids:
            return "HANDOFF_REPLAYED"
        seen_handoff_ids.add(handoff_id)
    selected = handoff.get("selected_skill")
    if not isinstance(selected, Mapping) or receipt.get("selected_skill") != selected.get("name") or receipt.get("content_sha256") != selected.get("content_sha256"):
        return "SKILL_SUBSTITUTION_REJECTED"
    if receipt.get("host_capability") != handoff.get("logical_host_capability"):
        return "HOST_CAPABILITY_UNAVAILABLE"
    profile = handoff.get("host_execution_profile")
    if not isinstance(profile, Mapping) or profile.get("mapping_id") != PRESENTATIONS_MAPPING_ID:
        return "HANDOFF_MALFORMED"
    if receipt.get("host_execution_mapping_id") != profile.get("mapping_id"):
        return "HOST_MAPPING_MISMATCH"
    states = receipt.get("states")
    if not isinstance(states, list) or not all(isinstance(item, str) for item in states):
        return "HANDOFF_MALFORMED"
    required_prefix = ["selected", "loaded_verified", "host_eligible", "execution_requested"]
    if states[:4] != required_prefix:
        return "HANDOFF_MALFORMED"
    result_code = receipt.get("result_code")
    if not isinstance(result_code, str):
        return "HANDOFF_MALFORMED"
    if result_code == "HOST_CAPABILITY_UNAVAILABLE":
        return "HOST_CAPABILITY_UNAVAILABLE"
    if result_code == "EXECUTION_REFUSED":
        return "EXECUTION_REFUSED"
    if result_code == "ARTIFACT_GENERATION_FAILED":
        return "ARTIFACT_GENERATION_FAILED"
    if result_code == "VALIDATION_FAILED":
        return "VALIDATION_FAILED"
    if result_code != "EXECUTION_SUCCEEDED":
        return "HANDOFF_MALFORMED"
    if receipt.get("input_resolution") != "safe_defaults_applied":
        return "INPUT_RESOLUTION_UNVERIFIED"
    if not isinstance(receipt.get("artifact_ref"), str) or not receipt["artifact_ref"] or receipt.get("artifact_kind") != "pptx":
        return "ARTIFACT_MISSING"
    if states[-2:] != ["execution_succeeded", "validation_passed"]:
        return "HANDOFF_MALFORMED"
    return "EXECUTION_SUCCEEDED"
