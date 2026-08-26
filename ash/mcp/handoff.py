"""Pure, redacted R4 host-handoff lifecycle helpers.

The local MCP server only issues an execution *intent*.  It never receives an
artifact, invokes a host tool, or records host execution.  These helpers make
the short-lived intent explicit so the Desktop plugin can reject stale or
user-supplied copies before it asks the host to act.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Mapping, MutableSet
from uuid import UUID

from .host_mapping import PRESENTATIONS_MAPPING_ID, presentation_profile


HANDOFF_SCHEMA_VERSION = "nexus.host-handoff.v1"
PLAN_VERSION = "nexus.v2.plan.v1"
HOST_PRESENTATIONS_CAPABILITY = "chatgpt.presentations"
HOST_NATIVE_PRESENTATIONS_MODE = "host_native_presentations"
HANDOFF_TTL_SECONDS = 300
HANDOFF_VALIDATION_REQUIREMENTS = [
    "artifact_created", "artifact_editable", "presentation_open_render",
]
HANDOFF_FIELDS = {
    "schema_version", "handoff_id", "issued_at", "expires_at", "plan_version",
    "status", "task_category", "selected_skill", "logical_host_capability",
    "requested_execution_mode", "host_execution_profile",
    "validation_requirements", "fallback", "security_result",
}


HOST_ARTIFACT_REF_PREFIX = "host-artifact:"


def is_valid_opaque_artifact_ref(value: Any) -> bool:
    """Accept only a bounded Host-issued identifier, never a path or URL."""
    if not isinstance(value, str) or not value.startswith(HOST_ARTIFACT_REF_PREFIX):
        return False
    identifier = value[len(HOST_ARTIFACT_REF_PREFIX):]
    return (
        1 <= len(value) <= 256
        and bool(identifier)
        and identifier[0].isascii()
        and identifier[0].isalnum()
        and all(
            character.isascii()
            and (character.isalnum() or character in "._-")
            for character in identifier
        )
    )


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


def strict_handoff_digest_for_execution_start(
    handoff: Mapping[str, Any], now: datetime | None = None,
) -> str | None:
    """Validate and bind the complete allowlisted R4 intent before execution.

    Unlike :func:`is_current_handoff`, this checks every execution-critical
    field.  The digest is Host-local audit data, not an authorization token.
    """
    if not isinstance(handoff, Mapping) or set(handoff) != HANDOFF_FIELDS:
        return None
    if handoff.get("schema_version") != HANDOFF_SCHEMA_VERSION:
        return None
    handoff_id = handoff.get("handoff_id")
    issued_at = handoff.get("issued_at")
    expires_at = handoff.get("expires_at")
    if not all(isinstance(value, str) for value in (handoff_id, issued_at, expires_at)):
        return None
    try:
        UUID(handoff_id)
        issued = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if issued.tzinfo is None or expires.tzinfo is None:
        return None
    issued = issued.astimezone(timezone.utc)
    expires = expires.astimezone(timezone.utc)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not (
        issued <= current + timedelta(seconds=30)
        and issued < expires <= issued + timedelta(seconds=HANDOFF_TTL_SECONDS)
        and current < expires
    ):
        return None
    selected = handoff.get("selected_skill")
    if not isinstance(selected, Mapping) or set(selected) != {
        "resource_id", "name", "content_sha256", "load_verification_state",
    }:
        return None
    resource_id = selected.get("resource_id")
    content_sha256 = selected.get("content_sha256")
    if (
        not isinstance(resource_id, str) or not resource_id or len(resource_id) > 256
        or selected.get("name") != "Presentations"
        or selected.get("load_verification_state") != "loaded_verified"
        or not isinstance(content_sha256, str) or len(content_sha256) != 64
        or any(character not in "0123456789abcdef" for character in content_sha256.casefold())
    ):
        return None
    fallback = handoff.get("fallback")
    security = handoff.get("security_result")
    if (
        handoff.get("plan_version") != PLAN_VERSION
        or handoff.get("status") != "execution_requested"
        or handoff.get("task_category") != "artifact"
        or handoff.get("logical_host_capability") != HOST_PRESENTATIONS_CAPABILITY
        or handoff.get("requested_execution_mode") != HOST_NATIVE_PRESENTATIONS_MODE
        or handoff.get("host_execution_profile") != presentation_profile()
        or handoff.get("validation_requirements") != HANDOFF_VALIDATION_REQUIREMENTS
        or not isinstance(fallback, Mapping) or set(fallback) != {"kind", "status"}
        or fallback.get("kind") != "native_codex_fallback"
        or fallback.get("status") != "not_needed"
        or security != {"code": "HOST_HANDOFF_READY", "mcp_execution_authority": "none"}
    ):
        return None
    canonical = json.dumps(handoff, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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
    result_code = receipt.get("result_code")
    if result_code == "HOST_CAPABILITY_UNAVAILABLE":
        if receipt.get("host_capability") != "unavailable":
            return "HANDOFF_MALFORMED"
    elif receipt.get("host_capability") != handoff.get("logical_host_capability"):
        return "HOST_CAPABILITY_UNAVAILABLE"
    profile = handoff.get("host_execution_profile")
    if not isinstance(profile, Mapping) or profile.get("mapping_id") != PRESENTATIONS_MAPPING_ID:
        return "HANDOFF_MALFORMED"
    if receipt.get("host_execution_mapping_id") != profile.get("mapping_id"):
        return "HOST_MAPPING_MISMATCH"
    states = receipt.get("states")
    if not isinstance(states, list) or not all(isinstance(item, str) for item in states):
        return "HANDOFF_MALFORMED"
    if not isinstance(result_code, str):
        return "HANDOFF_MALFORMED"
    if (
        "input_resolution" in receipt
        and receipt.get("input_resolution") != "safe_defaults_applied"
    ):
        return "INPUT_RESOLUTION_UNVERIFIED"
    canonical_states = {
        "HOST_CAPABILITY_UNAVAILABLE": [
            "selected", "loaded_verified", "execution_requested",
            "host_capability_unavailable",
        ],
        "HOST_EXECUTION_BINDING_UNAVAILABLE": [
            "selected", "loaded_verified", "execution_requested",
            "host_execution_binding_unavailable",
        ],
        "EXECUTION_REFUSED": [
            "selected", "loaded_verified", "host_eligible",
            "execution_requested", "execution_refused",
        ],
        "ARTIFACT_GENERATION_FAILED": [
            "selected", "loaded_verified", "host_eligible",
            "execution_requested", "execution_started", "execution_failed",
        ],
        "VALIDATION_FAILED": [
            "selected", "loaded_verified", "host_eligible",
            "execution_requested", "execution_started", "execution_succeeded",
            "validation_failed",
        ],
        "EXECUTION_SUCCEEDED": [
            "selected", "loaded_verified", "host_eligible",
            "execution_requested", "execution_started", "execution_succeeded",
            "validation_passed",
        ],
    }
    expected_states = canonical_states.get(result_code)
    if expected_states is None:
        return "HANDOFF_MALFORMED"
    artifact_results = {"EXECUTION_SUCCEEDED", "VALIDATION_FAILED"}
    if result_code in artifact_results:
        if (
            not is_valid_opaque_artifact_ref(receipt.get("artifact_ref"))
            or receipt.get("artifact_kind") != "pptx"
        ):
            return "ARTIFACT_MISSING"
    elif "artifact_ref" in receipt or "artifact_kind" in receipt:
        return "HANDOFF_MALFORMED"
    if states != expected_states:
        return "HANDOFF_MALFORMED"
    if result_code != "EXECUTION_SUCCEEDED":
        return result_code
    if receipt.get("input_resolution") != "safe_defaults_applied":
        return "INPUT_RESOLUTION_UNVERIFIED"
    return "EXECUTION_SUCCEEDED"
