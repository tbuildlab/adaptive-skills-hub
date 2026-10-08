# Nexus G3 Phase 2B offline Host approval bridge contract v1

Date: 2026-10-08. Accepted parent:
`dd88eea017e7906c45977d44bb3fe9b26c0ee4ef` on `nexus-v2-g3-development`.
Architecture inputs: [Phase 2A contracts](nexus-g3-authorization-contracts-v1.md)
and [U1 reuse probe](nexus-g3-u1-openai-host-reuse-probe-v1.md).

## Purpose and implemented boundary

[The adapter](../ash/g3_host_approval_bridge.py) proves normalization and
correlation using synthetic Host transcripts. It provides three frozen records:
`HostApprovalProposal`, `HostApprovalEvent`, `HostApprovalCorrelation`.
It does not start App Server, authenticate an Owner, invoke a provider, issue a
Grant, persist an approval store, or integrate with runtime admission.

An exact explicit acceptable decision can produce immutable
`HostDecisionEvidenceCandidate` bytes within a correlation result. This candidate
always carries `basis=OFFLINE_CONTRACT_ONLY`, `owner_authenticated=false`,
`approval_authority=none`, and `dispatch_authority=none`. Result validation rejects
claims of authenticated ownership or dispatch authority. Copied candidates/results
are not bearer grants. Phase 2A's public real-admission denial is byte-unchanged.

## Installed interface reuse

The source is the already-inspected `codex-cli 0.160.1` schema export under ignored
`state/g3-phase2a-20261008/app-server-schema/`. No version command, schema re-export,
App Server startup, account status, OAuth or connector operation was performed
in Phase 2B. All 21 prior selected schema records were rechecked against their
recorded byte lengths and hashes; metadata inventory SHA-256:
`65a9c9c78866f00e9ada94607751fde9a482c659ee3801a3fc00f86bd82f13f8`.
This proves equality with the reviewed snapshot, not the current desktop protocol.

The adapter supports a deliberately closed subset of native command approval:

| Existing schema / field | Offline use |
|---|---|
| `ServerRequest`: `id`, `method`, `params` | Original request envelope; `item/commandExecution/requestApproval` only |
| Command params: `threadId`, `turnId`, `itemId`, `startedAtMs` | Exact pending context; timestamp is material supplied data, not trusted time |
| Command params: `command`, `cwd` | Required nonempty bounded strings for this subset; both are material |
| Command params: nullable `approvalId`, `environmentId` | Preserve exact opaque context; absent/null normalize together |
| Command params: `kind` | Omitted/default `command` normalize together; `writeStdin` is unsupported |
| Command params: `reason` | Explicitly presentation-only, bounded/validated, excluded from identity |
| Command response: `decision` | Preserve native `accept`, `decline`, `cancel`, `acceptForSession` |
| JSON-RPC response envelope: `id`, `result` | Response request ID must match in value and concrete type |
| `ServerRequestResolvedNotification`: `threadId`, `requestId` | Native resolution correlation; resolution alone proves no approval |

No extra G3 fields are added to the native wire message. Nexus binding and declared
observation metadata are separate envelope fields. Native replies do not contain
subject/scope/turn/item proof: the adapter associates the reply with its pending
request snapshot. This association is synthetic contract evidence, not a protected
Host-origin assertion.

Command actions, network approval context, policy amendments, permissions, file
changes, stdin and connector-specific flows are unsupported in this slice and
fail closed. Session approval is a native recognized decision but remains
`UNKNOWN` for G3, with no candidate. This adapter cannot translate it into a
session or persistent grant. There is no generic event bus or parallel approval
request/response protocol.

## Canonical Nexus proposal

`proposal(native_request, Subject, requested_scope, effect_summary)` revalidates
the existing G3 Subject, normalizes scope using the Phase 2A helper, and detaches
caller-owned structures through bounded parsing. Its closed canonical body binds:

- `schema_version=nexus.g3.host-approval-proposal.v1`;
- exact normalized native request, including request/thread/turn/item/callback IDs;
- exact `subject_id`, containing the domain-separated subject digest;
- exact normalized G3 scope plus its canonical `scope_sha256`;
- `requested_action` from the Subject;
- `effect_summary={operations,targets_sha256}`.

Effect operations must equal the scope operation set; target digest pins the
declared effect target summary. Workspace/project/task/account constraints remain
inside exact scope. Account-dependent subjects must match scope account context.
Changing material identifiers, subject, scope, command/cwd, action or effects
changes the proposal ID. Only explicit cosmetic subject title, request reason,
JSON key order, serialization whitespace and reviewed set ordering are nonmaterial.
Unknown fields are rejected; no semantic inference from display text occurs.

The proposal ID uses the existing isolated G3 ID helper with domain
`nexus.g3.host-approval-proposal.v1`. Event ID likewise uses
`nexus.g3.host-approval-event.v1`. Scope/target hashes and IDs are nonsecret data
references, never proof that effects, provenance or identity are truthful.

## Event observation and classification

`event(bound_proposal, native_message, observation=...)` binds native response or
resolution to the pending proposal/subject/scope and complete identity tuple.
The separately supplied observation is exactly `{reviewer,resolution}`:
reviewer is `user`, `auto_review`, or `unknown`; resolution is `explicit`,
`auto_resolved`, `cleared`, `timed_out`, or `unknown`. Omitted observation defaults
to unknown. These are declared synthetic observations, not authenticated facts.

| Disposition | Deterministic condition / evidence |
|---|---|
| `EXPLICIT_APPROVE` | Matching native `accept`, declared reviewer `user`, explicit resolution; candidate only |
| `EXPLICIT_DENY` | Matching explicit user `decline` or `cancel`; no candidate |
| `AUTO_RESOLVED` | Auto-resolution or auto-review, including an auto-review `accept` labelled explicit |
| `CLEARED` | Matching declared cleared lifecycle; no candidate |
| `TIMED_OUT` | Matching declared timeout; no candidate |
| `DUPLICATE` | Previously consumed request, callback or exact event identity |
| `MISMATCH` | Changed proposal/subject/scope/tuple/callback/native request ID or resolution thread |
| `UNKNOWN` | Inadequate observation, bare resolution, session decision, or replay-set capacity exhausted |

Duplicate detection precedes mismatch. Clear/timeout take precedence over later
native accept; automatic review cannot be classified as explicit human approval.
A resolved notification may mean answered or cleared, so an explicit declaration
alone without a native decision remains unknown. Malformed/unsupported shapes
raise bounded `G3_INVALID_INPUT` without echoing input values.

## Offline replay semantics

`correlate(pending_proposal, observed_event, consumed_tokens)` requires an explicit
immutable replay set. There is no implicit new/reset trace. The returned
correlation contains the next set; callers must carry it forward within the same
offline trace. Tokens bind typed request ID, optional callback ID and event ID.
Integer `1` differs from string `"1"`. Native callback IDs are optional for ordinary
commands; the normalized event context must still contain `approval_id`, using
explicit null when absent and the exact pending ID when present.

Matching terminal outcomes consume IDs: approve, deny, clear, timeout, auto and
unknown. A late accept or changed reviewer/decision cannot reuse consumed IDs.
Same request with a different callback and same callback with a different request
are both duplicates. Moving the same event to another subject, broader scope or
changed tuple is rejected. Foreign/mismatched messages do not consume another
pending request; they remain rejected until an independently matching event arrives.

The set is capped at 192 digest tokens. There is no silent eviction or renewal;
capacity exhaustion returns unknown with the original set and no candidate.
Input bounds and canonicalization reuse Phase 2A (64 KiB body, G1 graph/string
limits, strict duplicate-key-safe integer-only JSON). Records are detached immutable
bytes; altered content/IDs are revalidated at correlation entry.

This proves one-use behavior only when the caller carries the complete set.
Caller reset/rollback/omission, concurrent lost updates and new connection/session
namespaces are not protected. No store, lock, process authority or production
replay resistance is claimed.

## Validation and compatibility

[Focused tests](../tests/test_g3_host_approval_bridge.py) include all requested
synthetic transcripts: explicit approve/deny, subject/broader-scope mismatch,
duplicates, clear, timeout, auto-resolution, missing identity, wrong thread/turn/
item, changed proposal digest and successful-consumption replay. Additional
checks cover callback reuse, typed IDs, effects, cosmetic stability, immutable
detachment, bounded replay state and copied-candidate rejection.

Native fixture messages were independently validated offline against the pinned
Draft 7 schemas: nine request/decision/resolution cases passed. All references
were checked to be schema-local before validation, prohibiting external schema
resolution. This validation uses an already-installed library only in disposable
local evidence tooling; no runtime dependency or SDK replacement was added.

Positive and negative transcripts run under traps for HTTP, credential/environment
access, subprocess/Host startup, dispatch/intent writes, handoff and external hooks.
Repackaging candidate evidence into a shape-valid G3 Grant still produces
`G3_APPROVAL_ORIGIN_UNVERIFIED` through the unchanged public evaluator. Existing
Grant, Revocation and EligibilityDecision contracts are reused in those compatibility
checks; the bridge never calls a grant/revocation factory or issuer fixture.

The existing isolation test now permits exactly this offline module as a G3
consumer and checks both modules for forbidden runtime/test imports. Every other
`ash` consumer remains prohibited from importing the new bridge or authorization
module. The real-admission rejection tests remain intact. Existing Core/G2 source,
G1 and frozen identity domains are unchanged.

## Exact U1 properties still unresolved

Offline PASS does not authenticate a person. An executor can fabricate a
`reviewer=user` declaration and these ordinary bytes; real admission stays denied.
After Phase 2B, the following remain unresolved:

| U1 property | Remaining boundary |
|---|---|
| Trusted Owner/profile/workspace identity | `UNKNOWN`; no authenticated context chain or live bridge tested |
| Executor write exclusion | `UNKNOWN`; no transport/store privilege separation established |
| Durable protected approval storage | `BUILD_GAP`; no authority store implemented or evidenced |
| Durable protected revocation storage | `BUILD_GAP`; no protected exact-grant revocation ledger |
| Rollback/freshness generation | `BUILD_GAP`; caller-owned replay set is resettable ordinary data |
| Atomic revoke/admit serialization | `BUILD_GAP`; no final real admission boundary exists |

Protected immutable decision evidence and production anti-replay also remain U1
gaps. The offline proposal/subject/scope/event-correlation portion has progressed;
the corresponding live trusted bindings and full enforcement coverage have not.
No IAM, OAuth/IdP, vault, PKI/TPM, broker/service, ACL/account redesign, VM, Root R,
Route D or generic approval service was built.

```text
G3_PHASE_2B_HOST_BRIDGE_CONTRACT_COMPLETE
HOST_INTERACTION_REUSE = VERIFIED_AT_CONTRACT_LEVEL
PROPOSAL_BINDING = VERIFIED_OFFLINE
SUBJECT_BINDING = VERIFIED_OFFLINE
SCOPE_BINDING = VERIFIED_OFFLINE
DUPLICATE_REPLAY_REJECTION = VERIFIED_OFFLINE
REAL_OWNER_APPROVAL_ADMISSION = DISABLED_UNTIL_U1
U1_REAL_ADMISSION_READY = NO
PROVIDER_EXECUTIONS_ADDED = 0
HISTORICAL_PROVIDER_EXECUTIONS = 3
CREDENTIAL_OPERATIONS = NONE
```
