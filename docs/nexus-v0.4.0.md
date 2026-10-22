# Nexus Desktop 0.4.0 — Release Notes and Production Acceptance

Status on 2026-10-22: the Owner accepted the installed Desktop 0.4.0 production runtime against the original mandatory acceptance criteria. Public GitHub publication and source/tag operations still require separate final Owner authorization. The previous installed version is 0.3.2.

## Accepted scope

The implementation is unchanged from accepted 0.4.0-rc.3. Codex owns task understanding, native Skill selection and Agent coordination. Nexus provides capability discovery, source-backed descriptions, registry-grounded trust metadata, resource identity and integrity checks, and optional single-Skill guarded loading.

A native recommendation is untrusted. Existing workspace authorization, trusted applicability, identity, path and content checks remain mandatory. Discovery metadata grants no loading or execution authority; loading instructions grants no subsequent execution permission. Requests without a recommendation retain legacy behavior.

No new routing engine, dependency, Agent framework, registry or permission authority is included. Original Bloom Corner applicability remains unresolved and must retain the existing refusal boundary.

The accepted installer also preserves an existing workspace ID instead of reassigning it to another directory. A conflicting alias is refused before bootstrap extraction or installation writes. The official Host/CLI continues to own plugin registration, cache and enablement.

## Accepted production results

| Acceptance item | Result |
| --- | --- |
| RUNTIME_ACCEPTANCE | PASS |
| CATALOG_RUNTIME_BEHAVIOR | PASS |
| ORIGINAL_RELEASE_GATE for full catalog enumeration | NOT_MANDATORY |
| CATALOG_FULL_COVERAGE | NOT_VERIFIED |
| PRODUCTION_ACCEPTANCE under the original mandatory criteria | PASS |
| RELEASE_RECOMMENDATION | READY |

Real Desktop Host acceptance verified one enabled official 0.4.0 plugin registration, the release-owned 0.4.0 backend, MCP health, enriched animation-filtered catalog metadata, authorized gsap-core loading, native guarded handoff and the SHA-256 of its received instructions. Legacy behavior and the required unauthorized-workspace and invalid-binding refusals passed. The three workspace mappings and the high reasoning-effort preference were preserved. No mixed active version or unintended fallback to 0.3.2 was observed.

The original Windows ZIP, release manifest, PowerShell bootstrap and their three SHA-256 receipts are retained without rebuilding. Release-source bytes are checked against the accepted archive. A documentation-only closeout updates this note and its static source manifest; it changes no accepted runtime payload.

## Known limits

Catalog discovery returns a bounded metadata snapshot. Descriptions share the existing response budget; truncation and the reported pre-truncation count are part of the accepted interface. It has no pagination. Full enumeration and independent verification of all 167 matching records in this Host environment remain NOT_VERIFIED. This limitation was accepted by the Owner and is not relabelled PASS. See nexus-catalog-metadata.md.

The acceptance covers the tested runtime paths and security refusals. It does not certify every discovered resource as available, trustworthy, loadable or executable. Loading instructions grants no execution authority. The inherited Bloom Corner applicability limitation remains unchanged.

## Installation and recovery boundary

Use the existing versioned Windows package and verified receipts. Installation prepares the personal marketplace source; the official Host/CLI owns plugin registration, cache and enablement. Do not edit installed cache files.

For a future separately authorized upgrade, completely exit Desktop and active Nexus sessions before the existing installer and supported `codex plugin add nexus-desktop@personal-marketplace` refresh. Preserve the prior release, current configuration and all workspace mappings. Reuse the existing matching workspace alias and preserve user preferences, including `model_reasoning_effort = "high"` where configured. The accepted production installation does not need to be repeated.

Use Windows PowerShell 5.1 with its own Modules directory prepended only in the maintenance child process. Do not change global environment, execution policy, ACLs or profiles. Stop on failed integrity, workspace conflict, unexpected running Host, access/sharing error or uncertain recovery state; do not force or retry.

Nexus rollback restores Nexus-owned source/configuration/state, not Host registration/cache. If Host registration was changed, use the supported Host/CLI lifecycle while Desktop is closed, restore the prior source with the verified installer's rollback, then register 0.3.2 again. Retain both releases and evidence. Never reset unrelated user preferences or restore obsolete runtime pipe values from old configuration.

## Publication boundary

The production runtime acceptance is complete. Commit, push, tag creation and a GitHub Release remain pending final Owner authorization. Publish only the six reviewed versioned assets; do not attach local configuration, credentials, private Project Memory, Reference Library data, local acceptance packets or recovery backups. GitHub-generated source archives are not the Windows installer.
