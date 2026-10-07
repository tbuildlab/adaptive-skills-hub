# G2-OPENAI Managed Execution sprint v1 — source report

Baseline: `c283e6471daacaa076cf501180d195f82494cfc7` on
`nexus-v2-g2-development`, independently checked on 2026-10-07.
The baseline MANIFEST passed 305/305 checks. Core Alpha 2 code, its accepted
guide, prior G2 records, branch and HEAD are preserved. Changes are uncommitted.

## Delivered

- Owner-directed provider-trust architecture and current roadmap addendum.
- Provider-neutral typed concepts and closed request/receipt contracts.
- Structured routing including local, managed candidate, Host, unsupported and
  Owner-boundary decisions. Current CLI integration is offline Host handoff only.
- Explicit task/capability/version/scope/baseline/input/expiry/budget bindings,
  digest approval, normalized imported evidence and fresh task-owned artifacts.
- Independent expected-artifact hash verification; provider success alone never
  completes. Owner-review artifacts remain incomplete.
- Checksum checkpoints, intent-before-export, bounded pre-execution retry,
  no blind replay, distinct cancellation evidence and concise operator summary.
- Source package allowlist includes these documents. Installed Desktop and
  release installer remain unchanged.

## Validation evidence

- **249 targeted tests PASS** across isolated phases: 42 new managed contract
  tests and 207 existing Core/V2/CLI/R4/R5/inventory/package/desktop regressions.
  The combined static-source run passed 247 checks; its two package checks were
  then run separately on fresh static sources and both passed. Earlier behavioral
  tests had generated runtime state inside the combined source, correctly
  triggering the package guard. This is test-state isolation, not a guard bypass.
- **MANIFEST 312/312 PASS**, generated from the original 305 manifest-listed
  static files plus the seven explicit sprint files, in an isolated snapshot.
  Historical untracked drafts and mutable storage are outside that snapshot.
- `git diff --check` PASS; branch/HEAD unchanged; Git index unchanged.
- The three historical untracked draft SHA-256 values match the initial readback.
- Existing `ash/core*.py`, Core tests, Alpha 2 guide, installed plugin and legacy
  G2 evidence were not edited.

Local command evidence is retained under ignored
`state/g2-openai-sprint-validation/`; package tests use the preexisting MCP-capable
runtime, not a newly installed dependency. The source implementation contains no
provider network client. Passing fixtures do not qualify OpenAI infrastructure.

The actual demonstration created a non-secret standalone project and a real
`handoff-1.json`, with `STATUS = HANDOFF_PREPARED`, `FINAL_RESULT = NOT_COMPLETE`,
`provider_execution = NOT_ATTEMPTED`. No mock provider receipt was included in
this demonstration. The first fixture under the repository's ignored state
directory was refused by exact Git-root binding before export; its files remain.
Contract tests use synthetic receipts clearly identified as fixtures.

An initial broader test invocation with system Python encountered missing
`mcp`/`mcp_types`; the existing MCP-capable runtime was located and independently
checked. Direct package construction from the real repository was refused by
its existing mutable-storage guard. Final validation uses an isolated static
source snapshot; no stored data or guard was removed to pass.

## Remaining integration gaps

Direct provider dispatch/polling/cancellation, authenticated provider provenance,
account eligibility, enforceable provider financial limits, in-task replan,
general structured-output verification, automatic patch application/local check
reruns and installed single-command intake are not implemented. The documented
Responses hosted shell and hosted browser are candidates, not live qualified
adapters. A Host tool visible in this chat is not callable from the Nexus CLI.

No credentials, paid provider actions, VM operations, legacy Route D/Root R work,
push, merge, commit, tag, freeze, publishing or deployment occurred. There was no
actual Desktop/provider installation; existing tests exercised isolated temporary
fixture install/uninstall only.
No general G3 authorization or G4/G6 implementation was started.

Final classification: **G2_OPENAI_PARTIAL_PROVIDER_INTEGRATION_GAPS_REMAIN**.

`SELF_HOSTED_G2 = DEFERRED`

`PRODUCTION_POSITIVE_HOST_BINDING = ABSENT`
