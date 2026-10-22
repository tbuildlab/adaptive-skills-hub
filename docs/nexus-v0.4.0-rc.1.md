# Nexus v0.4.0-rc.1 — Minimal Native Integration

Provisional isolated source candidate targeting v0.4.0; production remains v0.3.2. Owner approval is required before any merge, installation or publication.

## Responsibility split

Codex owns natural-language task understanding, native Skill recommendation, instruction application and native Agent coordination. Nexus offers bounded resource discovery and optional guarded instruction delivery. No new semantic router, Agent execution layer or Owner identity authority is introduced.

## Included changes

- Additive capability descriptions from existing metadata, plus registry-grounded trust status. See nexus-catalog-metadata.md. Catalog metadata grants no load or execution permission.
- Optional nexus.plan_task native_recommendation contract, version nexus.native-skill-recommendation.v1. It accepts one untrusted stable Skill ID and a request-binding digest. The existing registry/applicability selector must independently accept exactly that one resource before guarded loading.
- The successful handoff returns verified instruction text, resource ID, content hash and request binding, with recommendation_authority and execution_authority both none. Requests without recommendations retain the legacy branch.

The binding digest is SHA-256 of compact sorted-key UTF-8 JSON containing the exact original task, workspace_id, project_context_mode (default governance) and constraints (default empty list). It prevents accidental cross-request substitution; it does not authenticate an Owner or permission grant.

## Distinct routes

Native Skill use is controlled by the Host and is not Nexus-approved. The optional guarded Nexus route requires all existing admission checks. An ineligible native recommendation must be refused, not forced into selection or followed by a source-path read represented as approved loading. Native multi-Skill use and native Agents do not expand Nexus's single-Skill recommendation contract.

Instruction loading does not authorize edits, dependency installation, Agent execution or deployment. Trusted metadata is registry identity evidence, not current-task applicability or permission. Unknown trust remains unknown. Revalidate current path/content through the existing guarded loader before delivery.

## Limits and exclusions

Original Bloom Corner applicability remains unresolved. Existing trusted checks are intentionally preserved; no semantic-routing experiments, G3/remote approval work, new dependencies, resource migration or synchronization are included in this increment. Historical source components inherited from the v0.3.2 baseline are unchanged; their presence is not new development or activation.

This document describes the source candidate. It does not assert a built distributable, successful installation, production runtime smoke, universal routing reliability or a Nexus-verifiable Owner approval path. Use the separate candidate report for exact validation evidence.
