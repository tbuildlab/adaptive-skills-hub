"""Allowlisted host-execution mappings for Nexus Runtime R4 and R5.

Mappings are descriptive, redacted profiles.  They are not commands and do
not give the local MCP server authority to execute a host capability.  Keeping
this registry separate from routing lets later R4 slices add a reviewed mapping
without changing Nexus V1.2's normal Skill ranking.
"""
from __future__ import annotations

from typing import Any


PRESENTATIONS_MAPPING_ID = "nexus.host-map.presentations.v1"
PRESENTATIONS_ENHANCEMENT_MAPPING_ID = "nexus.host-map.presentations.enhancement.v1"
DIRECT_HOST_TOOL_BINDING = "direct_host_tool"
HOST_SKILL_WORKFLOW_BINDING = "host_skill_workflow"
NO_EXECUTION_BINDING = "none"

# Canonical Host provenance, not a display-name match.  The public OpenAI
# Presentations plugin manifest identifies the plugin as ``presentations`` and
# the Host source namespace exposes it from ``openai-primary-runtime``.  A
# caller-controlled label can never satisfy this tuple.
PRESENTATIONS_HOST_PROVIDER_ID = "openai-primary-runtime"
PRESENTATIONS_HOST_CAPABILITY_ID = "presentations"
PRESENTATIONS_HOST_RESOURCE_KIND = "skill"


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


def presentation_enhancement_profiles() -> tuple[dict[str, Any], ...]:
    """Return the small, reviewed R5 enhancement registry.

    These entries are descriptive Host intents, not Skills, commands, or a
    second routing pass. The Host alone decides whether it has the native
    Presentations capability and performs any copy-on-write edit. Keeping these
    data-only profiles here makes future artifact kinds additive without
    granting Nexus arbitrary tool or Skill invocation authority.
    """
    return (
        {
            "candidate_id": "presentation_layout_polish.v1",
            "mapping_id": PRESENTATIONS_ENHANCEMENT_MAPPING_ID,
            "logical_host_capability": "chatgpt.presentations",
            "requested_execution_mode": "host_native_presentations_enhancement",
            "eligible_observations": ("layout_density_high", "visual_hierarchy_weak"),
            "priority": 20,
            "operation_scope": ("refine_layout", "improve_visual_hierarchy"),
            "validation_requirements": ("artifact_editable", "presentation_open_render"),
        },
        {
            "candidate_id": "presentation_legibility_polish.v1",
            "mapping_id": PRESENTATIONS_ENHANCEMENT_MAPPING_ID,
            "logical_host_capability": "chatgpt.presentations",
            "requested_execution_mode": "host_native_presentations_enhancement",
            "eligible_observations": ("text_legibility_low", "contrast_needs_review"),
            "priority": 10,
            "operation_scope": ("improve_legibility", "improve_contrast"),
            "validation_requirements": ("artifact_editable", "presentation_open_render"),
        },
    )
