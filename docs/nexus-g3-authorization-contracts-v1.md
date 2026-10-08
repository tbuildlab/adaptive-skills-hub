# Nexus G3 Phase 2A authorization contracts

Date: 2026-10-08. Scope: pure data foundation and synthetic evaluation only.
Architecture input: [accepted Phase 1 survey](nexus-g3-reuse-survey-v1.md).
Phase 1 checkpoint: `f113b17885524f4cb6c452c3b30315dc280cc890`.
Accepted G2 ancestor: `5f2803f3581a5795232240490bb433a14ed3d0c5`.
Local branch: `nexus-v2-g3-development`.

## Implemented boundary

`ash/g3_authorization.py` provides four logical records: `Subject`,
`ApprovalGrant`, `Revocation`, and `EligibilityDecision`. There is no registration
database, Owner service, store, CLI, runtime gate, or dispatcher integration.
The public `evaluate_eligibility` always returns `NOT_ELIGIBLE`: valid inputs
produce `G3_APPROVAL_ORIGIN_UNVERIFIED`; malformed inputs produce
`G3_INVALID_INPUT`. No JSON, issuer string, evidence hash, or prior positive
decision can enable real admission.

The private predicate can evaluate synthetic issuer snapshots. Every result on
that path has `basis=TEST_FIXTURE_ONLY` and `dispatch_authority=none`. A positive
result is test evidence only. Decision construction itself refuses a positive
result labelled `REAL_ADMISSION_DISABLED` or any dispatch authority.

Existing closed Core/G2 consumers have no new import or call to this module.
Their current authority contracts remain the governing contracts. Future external
capability admission and coverage/migration remain separate authorized work.

## Exact reuse

| Existing primitive | Use in Phase 2A |
|---|---|
| `ash.capabilities.CAPABILITY_ID_RE` | Existing capability-ID syntax, with a 128-character G3 bound and known secret-pattern rejection |
| `ash.ecosystem_models.parse_json_bytes` | Strict bounded UTF-8 JSON, duplicate-key rejection, integer-only representation |
| `ash.ecosystem_models.canonical_json_bytes` | Deterministic object ordering and exact canonical bytes |
| `ash.ecosystem_models.validate_typed_id` | Preserve source/component-revision references in the local component envelope |
| `ash.g1_profiles` bounded/exact/token/sha/integer/tokens helpers | Closed shapes, graph/string limits, digest syntax, integer times, canonical sets |
| Existing source/revision/component builders | Component fixtures use `source_identity`, `build_revision_identity`, `build_component_identity`, `build_component_revision_identity` |
| `tests.g1_fixtures.NOW` | Shared explicit synthetic evaluation time |
| `scripts.build_manifest.build_manifest_bytes` | Isolated source-snapshot manifest regeneration; frozen guards unchanged |

`ash/mcp/authorization.py` was inspected. Its workspace allowlist and reparse/path
guards are a different responsibility, so G3 was added separately. G3 scope IDs
are opaque caller-bound IDs; they do not resolve paths or establish trustworthy
workspace identity. There is no duplication of OAuth, credential custody,
provider login, installation, MCP transport, G1 selection or G2 execution.

## Canonical records

Validated factories return frozen, slotted records holding canonical immutable
bytes and their ID. `to_dict()` returns a detached body for inspection, excluding
the derived ID; the dataclass carries that ID. Directly constructed or replaced
records are revalidated at evaluator entry. A malformed body or altered ID fails.

G3 uses the isolated ID formula:

```text
nexus.g3.<kind>.v1:hex(SHA256(UTF8("nexus.g3.<kind>.v1\0") || canonical_body))
```

Kinds are `subject`, `grant`, `revocation`. The `\0` denotes one NUL byte.
No Slice 3C typed-ID domain was changed. `subject_sha256` in a grant is the
domain-separated subject-ID digest, not the plain hash of its serialized body.
Record IDs prove deterministic byte binding, never authenticated origin.

Each body is at most 65,536 canonical bytes. Existing G1 graph bounds additionally
limit depth to 12, nodes to 16,000, collection members to 64, and strings to 512.
Numbers are nonnegative integers through `2^63-1`; floats, duplicate keys,
cycles, noncanonical Unicode, unsafe controls and container subclasses fail.
Evaluation accepts at most 64 grants and 64 revocations, with duplicate IDs denied.

## Subject envelopes

Common required fields: `schema_version=nexus.g3.subject.v1`, `capability_id`,
`kind`, `provider`, `action`. The remaining fields are closed per kind:

| Kind | Required material fields |
|---|---|
| `local_adapter` | `source_ref`, `revision`, `content_sha256`, `config_sha256` |
| `local_component` | Existing `source_id`, existing `component_revision_id`, `config_sha256` |
| `mcp_tool` | `server_ref`, exact case-sensitive `tool_name`, `revision`, `contract_sha256`, `config_sha256`, `account_context` |

Only the optional bounded `display_title` is explicitly cosmetic and excluded
from the material body. Key order and serialization whitespace are nonmaterial.
All other accepted fields are material. Unknown fields, including description,
telemetry and icon fields, are rejected rather than guessed to be harmless.
Credentials have no field in these contracts; known credential-shaped identifiers
are rejected. Pattern checks are bounded safeguards, not a general secret detector.

A declared revision or a well-shaped component ID is still supplied data. This
module does not inspect implementation bytes, prove remote immutability, prove
the source ancestry of a supplied hash, or authenticate provider/account context.
Those observations and applicable provenance must come from a future accepted
adapter. Unsupported/unresolved live subjects remain unadmitted.

## Grant and review

`schema_version=nexus.g3.grant.v1`; required body fields are `capability_id`,
`subject_id`, matching `subject_sha256`, `scope`, `effective_at`, `expires_at`,
`issuer_ref`, and `decision_evidence={ref,sha256}`. `expires_at=null` explicitly
means no time expiry. A finite expiry must be later than `effective_at`.
Grant ID binds the entire canonical body, including issuer and evidence.

Optional `review={subject_id,evidence,provenance_ref}` must refer to the exact
grant subject. Local component fixture eligibility requires this review.
Review shape and hashes do not prove review quality or provenance authenticity.
Other supported kinds have no fabricated intake-policy prerequisite.

`issuer_ref=owner` does not authenticate an Owner. A shape-valid grant remains
candidate data. The public evaluator denies grants even with the test marker.

## Revocation and validity

`schema_version=nexus.g3.revocation.v1`; body fields are exact `grant_id`,
`effective_at`, `issuer_ref`, `decision_evidence={ref,sha256}`, and bounded token
`reason`. There is no wildcard, future-subject ban, renewal or remote cancel call.

At explicit `now`, a trusted synthetic revocation with `effective_at <= now`
denies that grant. The validity interval is `[effective_at, expires_at)`.
Expiry is derived on every evaluation. A revoked grant remains revoked on later
evaluations containing that revocation; another grant body produces another ID
and must be independently trusted. Unrelated revocations do not poison a valid
grant. An untrusted revocation snapshot denies evaluation instead of being ignored.

The pure evaluator cannot discover an omitted revocation, time rollback, stale
store snapshot, generation change or hostile filesystem rollback. No generation
field or `G3_ADMISSION_STALE` behavior is claimed. A real accepted store, trusted
time, fresh generation and atomic revoke/admit ordering remain U1/U5 work.

## Scope and conjunction

Required scope: exact `workspace_id`, exact `project_id`, nonempty explicit
`task_classes` and `operations`. Optional `task_id` narrows to one task; optional
`account_context` narrows to one account. MCP subject, grant and invocation must
all contain the same account context. Project basename and account display label
are not independently trusted identities.

Supported operations: `read`, `write`, `execute`, `network`, `delegate`.
These are classifications for the future interface, not activated capabilities.
Task classes and operations are sorted unique sets. Empty sets permit no positive
admission and are rejected in the first usable-grant contract. No glob, regex,
wildcard, roles, tenant policy language or union of partial grants is supported.

One grant must cover the entire invocation. A request outside any required
scope dimension is denied. After one valid covering grant, independent supplied
facts `technical_available`, `task_authorized`, `host_authorized`, `g1_passed`,
`g2_passed` must all be concrete `True`. Each predicate is understood to cover
the entire normalized invocation, not a generic project-wide permission. G3
cannot override a failed task/Host/G1/G2 predicate. These booleans are explicit
pure-test inputs, not runtime observations or authority sourced by this module.

## Decision and reasons

Decisions contain closed schema, status, unique ordered reason tuple, subject/grant
references, normalized scope `request_sha256`, explicit `evaluated_at`, basis and
`dispatch_authority=none`. Invalid input may leave unresolved references/time null.
Decisions are rebuilt data; no consumer accepts them as bearer grants.

Implemented reasons only:

| Reason | Behavior |
|---|---|
| `G3_INVALID_INPUT` | Closed parse, shape, type, bounds or identity validation failed |
| `G3_APPROVAL_ORIGIN_UNVERIFIED` | Public real path, or untrusted fixture grant/revocation |
| `G3_CAPABILITY_UNAPPROVED` | No grant or no same capability ID in the trusted fixture snapshot |
| `G3_CAPABILITY_SUBJECT_MISMATCH` | Same logical capability with a different exact subject |
| `G3_CAPABILITY_EVIDENCE_UNVERIFIED` | Local component has no same-subject review |
| `G3_CAPABILITY_REVOKED` | Exact grant has an effective fixture revocation |
| `G3_APPROVAL_NOT_EFFECTIVE` | Before grant effective time |
| `G3_CAPABILITY_EXPIRED` | At or after finite expiry |
| `G3_CAPABILITY_SCOPE_DENIED` | No single covering scope or MCP account mismatch |
| `G3_CAPABILITY_UNAVAILABLE` | Technical predicate failed |
| `G3_TASK_AUTHORITY_REQUIRED` | Independent task predicate failed |
| `G3_HOST_AUTHORITY_REQUIRED` | Independent Host predicate failed |
| `G3_G1_RESTRICTION_FAILED` | Existing G1 predicate failed |
| `G3_G2_RESTRICTION_FAILED` | Existing G2 predicate failed |
| `G3_ELIGIBLE` | All pure checks pass under the explicit test-only fixture |

Validation/origin failures stop dependent checks. Grants are considered in stable
ID order. Each grant fails independently; revoked or expired grants cannot defeat
another fully valid grant. Denial categories are deduplicated in that order.
The independent gate reasons have fixed technical/task/Host/G1/G2 ordering.

## Synthetic issuer protections and checks

`tests/g3_fixtures.py` is the only fixture issuer helper. It explicitly supplies
test-only exact grant/revocation ID sets for synthetic evidence with a test marker.
It is never imported by `ash`, automatically selected, exposed in a CLI, persisted
as production authority, or invoked by the public evaluator. This is a synthetic
trusted-process model; arbitrary Python code is not claimed to be isolated from
private functions. Even a directly called private predicate cannot return an
execution-authoritative decision or a real-admission-positive result.

The focused suite checks material substitutions, cosmetic stability, canonical
golden identity, malformed inputs, account/action mismatch, immutable detachment,
time boundaries, no renewal, exact/unrelated revocation, independent new grants,
scope widening and no union, missing approval, independent failed gates, copied
decisions, candidate JSON, fixture/Owner-string production rejection, and zero
HTTP/credential/intent/handoff/hook effects under mocks.

See [U1 probe](nexus-g3-u1-openai-host-reuse-probe-v1.md) for the separate reuse
assessment. This document is not Owner acceptance or G2 qualification.

Validation: 21 focused G3 tests, 60 existing capability/G1 tests, and 11 isolated
source/package tests pass. Syntax/AST, closed-reason documentation, local document
links, bounded secret-pattern scan and Git whitespace checks pass. The regenerated
manifest has 330 entries; all 325 Phase 1 entries retain their prior digests.
Portable package allowlists and source-boundary guards are unchanged. New G3
source/tests are included by the existing directory rule; these private G3 docs
remain outside the portable documentation allowlist.

Core/G2 execution regression suites were not rerun: no consumer/import integration
or existing source bytes changed. Negative-effect tests patch their actual effect
boundaries. All historical baseline source hashes and the three excluded Route D
draft hashes were checked; the drafts remain untracked and unchanged. Official
documentation and schema-only metadata research add zero provider executions.
No credential operation, push, merge, tag, freeze or release is part of this phase.

```text
G3_SUBJECT_CONTRACT = COMPLETE
G3_APPROVAL_CONTRACT = COMPLETE
G3_REVOCATION_CONTRACT = COMPLETE
G3_ELIGIBILITY_FOUNDATION = COMPLETE
REAL_OWNER_APPROVAL_ADMISSION = DISABLED_UNTIL_U1
```
