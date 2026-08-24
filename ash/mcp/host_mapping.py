"""Allowlisted host-execution mappings for Nexus Runtime R4.

Mappings are descriptive, redacted profiles.  They are not commands and do
not give the local MCP server authority to execute a host capability.  Keeping
this registry separate from routing lets later R4 slices add a reviewed mapping
without changing Nexus V1.2's normal Skill ranking.
"""
from __future__ import annotations

from typing import Any


PRESENTATIONS_MAPPING_ID = "nexus.host-map.presentations.v1"


def presentation_profile() -> dict[str, Any]:
    """Return the one approved R4 profile, with no user/project content.

    Values resolve only ordinary presentation defaults.  A host must still ask
    when a required detail is genuinely non-inferable or an approval boundary
    applies; it must never treat this profile as permission to substitute a
    different Skill or invoke an arbitrary tool.
    """
    return {
        "mapping_id": PRESENTATIONS_MAPPING_ID,
        "continuation_policy": "continue_with_safe_defaults",
        "clarification_policy": "ask_only_for_required_noninferable_input",
        "default_profile": "business_presentation.v1",
        "resolved_defaults": {
            "audience": "business professionals and decision-makers",
            "purpose": "a clear, actionable overview of the requested topic",
            "deck_length": "concise_standard_deck",
            "visual_direction": "professional_modern_neutral",
            "artifact_format": "editable_pptx",
        },
    }
