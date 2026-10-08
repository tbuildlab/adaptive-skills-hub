# Nexus G3 U1 trusted approval admission architecture v1

Date: 2026-10-08. Deliverable: architecture and feasibility only.
Reviewed local checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`
on `nexus-v2-g3-development`.
Accepted G2 ancestor: `5f2803f3581a5795232240490bb433a14ed3d0c5`.

```text
U1_IMPLEMENTATION_READY = NO
REAL_ADMISSION_IMPLEMENTATION = BLOCKED
STOP_GATE = TRUSTED_OWNER_IDENTITY_OR_EXECUTOR_WRITE_EXCLUSION_NOT_PROVEN
```

Neither the complete trusted Owner identity chain nor executor write exclusion
has been demonstrated for an available Nexus/OpenAI Host facility. This triggers
the requested stop gate. The remaining sections complete the authorized
documentary design; they do not authorize or implement real admission.

## 1. Assessment and evidence rules

`VERIFIED` means the exact stated property has supporting evidence in the reviewed
scope. `BUILD_GAP` means a required contract or mechanism is absent from the
reviewed implementation. `UNKNOWN` means evidence does not establish the property;
it does not mean the platform cannot supply it. `BLOCKED` means a prerequisite or
authorization gate prevents proceeding. Documented product capabilities and
synthetic contract behavior cannot qualify the complete production property.

| # | Required property | Status | Established subset and unresolved condition |
|---|---|---|---|
| 1 | Trusted Owner/profile/workspace identity chain | UNKNOWN | A stable authenticated plugin profile contract is documented; an available, authenticated Owner-to-profile-to-Nexus-workspace decision chain is unproven. |
| 2 | Executor write exclusion | UNKNOWN | The reviewed local state uses a same-user trust model; no effective independent Host enforcement and custody boundary is evidenced. |
| 3 | Protected durable grant/revocation/decision-evidence storage | BUILD_GAP | G3 has immutable data records, but no protected production authority store or durable commit/recovery contract. Host availability is UNKNOWN. |
| 4 | Production replay protection and freshness generation | BUILD_GAP | Phase 2B has caller-supplied, process-local replay state; no protected durable consumption, trusted time or rollback-resistant generation exists in G3. |
| 5 | Atomic revoke/admit serialization | BUILD_GAP | Existing per-task locks and atomic file replacement do not serialize authoritative grant revocation with G3 admission and dispatch intent. |

The implementation consequence is `BLOCKED` for all dependent real-admission
work. No full property in this table is `VERIFIED`. Conditional feasibility is
different from implementation readiness: a thin adapter is feasible only if an
existing independent authority supplies the missing guarantees and is qualified.

## 2. Review scope and evidence register

Inputs are the [Phase 1 reuse survey](nexus-g3-reuse-survey-v1.md),
[Phase 2A contracts](nexus-g3-authorization-contracts-v1.md),
[U1 Host reuse probe](nexus-g3-u1-openai-host-reuse-probe-v1.md), and
[Phase 2B offline bridge contract](nexus-g3-host-approval-bridge-contract-v1.md).
Current code and the existing schema snapshot were read directly. Official pages
were refreshed on 2026-10-08. No account state, credentials, authentication files,
live Host approval event, protected production store or provider was accessed.

| Evidence | Current finding | Limit |
|---|---|---|
| [G3 evaluator](../ash/g3_authorization.py), public `evaluate_eligibility` | VERIFIED: valid real inputs remain denied with `G3_APPROVAL_ORIGIN_UNVERIFIED`; malformed inputs fail closed. | Fixture evaluation cannot establish production authority. |
| [Offline bridge](../ash/g3_host_approval_bridge.py), `correlate` | VERIFIED: explicit supplied replay state and exact transcript correlation; candidates retain `owner_authenticated=false`, `approval_authority=none`, `dispatch_authority=none`. | Supplied `reviewer=user` and transcript bytes do not authenticate a person. |
| [Workspace authorizer](../ash/mcp/authorization.py) | VERIFIED: startup workspace allowlisting and path/reparse checks. | An opaque workspace ID and configured path do not authenticate an Owner or establish authority custody. |
| [Core state writer](../ash/core.py), `_atomic` / `_save` | VERIFIED: checksum, file flush, `fsync`, replacement mechanics. | No independent writer authentication or rollback resistance follows. Full power-loss durability is not established here. |
| [Core lock](../ash/core_host.py), `exclusive_run`; [G2 handoff](../ash/managed_execution.py) | VERIFIED: OS-held per-task locking; G2 explicitly describes same-user trust and unauthenticated checksums. | No shared G3 revocation/admission transaction or hostile-executor qualification. |
| Prior CLI 0.160.1 static schema export | VERIFIED: all 21 selected files match their prior byte lengths and SHA-256 inventory. | Snapshot equality does not identify the running desktop version or prove behavior. |

Schema metadata inventory SHA-256:
`65a9c9c78866f00e9ada94607751fde9a482c659ee3801a3fc00f86bd82f13f8`.
Local audit inputs are under ignored `state/g3-phase2a-20261008/`; current static
verification is under ignored `state/g3-u1-architecture-20261008/`.

## 3. Existing OpenAI/Host facilities and the exact reuse limit

**Documented fact:** App Server transports approval requests to a client, which
returns a decision. `serverRequest/resolved` can also represent cleanup. The
initialization attestation interface returns an opaque upstream token; the
reviewed documentation does not specify a G3 proposal-bound human decision
verifier. These are useful transport seams, without a demonstrated U1 authority
receipt. [Official App Server documentation](https://learn.chatgpt.com/docs/app-server).

**Documented fact:** An authenticated plugin profile tool resolves one stable,
opaque profile ID from validated request credentials. The server must guarantee
correct scoping and stability; schema validation alone cannot prove them. This
is a reuse candidate for account/profile identification, conditional on a
qualified existing service. It does not itself map that profile to the human
authorized to approve a Nexus workspace. No profile tool was invoked.
[Official authentication documentation](https://developers.openai.com/plugins/build/auth).

**Documented fact:** Approval review may route to a human or an automatic reviewer;
routine permitted work may create no review request. The current session declares
`approval_policy=never` and `danger-full-access`. This is session configuration
evidence, not an independent isolation test or proof about every Host-internal
store. Native approval UI is therefore not an established mandatory U1 gate for
this session. [Official approvals documentation](https://learn.chatgpt.com/docs/agent-approvals-security).

**Documented fact:** Managed requirements constrain supported security settings;
defaults are overridable. Some managed hook error paths do not block a tool.
Consequently a generic hook cannot be assumed to enforce this fail-closed
admission design. Effective, instance-specific enforcement would need separate
evidence. No enterprise policy or local configuration was changed.
[Official managed configuration documentation](https://learn.chatgpt.com/docs/enterprise/managed-configuration).

**Documented fact:** MCP Events documents signed delivery and challenge checking
for subscriptions. That is a different event contract, with server-owned
credentials and lifecycle obligations. It supplies no demonstrated native
Owner-approval receipt or atomic G3 store. It is not installed or repurposed here.
[Official MCP Events documentation](https://developers.openai.com/plugins/build/mcp-events).

**Static interface finding:** In the pinned `GetAccountResponse` reachable account
variants, API-key mode identifies a type and ChatGPT mode exposes email/plan.
An unused `WorkspaceRouting` definition includes `chatgptAccountId`; it is not a
returned authenticated Owner/workspace decision chain in that schema.
`ChatgptAuthTokensRefreshParams.previousAccountId` is a routing hint.
`InitializeResponse` carries runtime/path metadata. `AttestationGenerateParams`
has no declared proposal-binding fields and its response is an opaque token.
None of these inspected shapes establishes the required human decision provenance,
Owner entitlement, protected writer, generation or atomic revocation semantics.
Opaque tokens were neither generated nor inspected. Absence from these reviewed
surfaces is not a claim that no private or future Host facility can exist.

## 4. Proposed trust boundary and reuse-first architecture

Everything in sections 4-9 is a **PROPOSAL**, not an available implementation.
The preferred route is an existing Host/operator-owned authority with a small
Nexus adapter. No new identity provider, credential vault, service, UI or database
is authorized by this document.

| Role | Required responsibility | Executor permissions |
|---|---|---|
| Existing identity authority | Validate authentication and establish immutable nonsecret principal/profile references. | Cannot supply or override the authenticated principal. |
| Existing workspace authority | Establish current Owner entitlement and the trusted Nexus workspace/project binding. | May request a workspace; cannot set the authoritative mapping or Owner role. |
| Trusted Host decision handler | Bind the displayed material proposal to an explicit human decision and authenticated context. | Submit untrusted proposals; cannot create authoritative approval events. |
| Protected authority store | Own grant/revocation/evidence records, replay tombstones, generations and admission intent. | Bounded reads/proposal submission only; no authoritative writes, deletes or restores. |
| Trusted admission/dispatch coordinator | Enforce one serialization order for revoke, context invalidation and admission; own the effective dispatch gate. | Cannot bypass the gate, rewrite its code/configuration, or invoke an alternate privileged dispatch route. |
| Existing Nexus data adapter and G2 workflow | Reuse canonical records and transcript correlation; preserve execution intent, ambiguous outcomes and reconciliation. | Produce data and permitted work; no authority inferred from copied decisions. |

The logical path is: untrusted proposal -> trusted context resolution -> trusted
human decision -> protected grant commit -> atomic admission/intent commit ->
existing bounded G2 execution handling. Revocation enters the same authority and
serialization domain. This diagram of responsibilities does not establish that
the Host currently offers the path.

An ordinary repository file, ignored state file, user-owned SQLite database,
checksum envelope or local Python process cannot qualify merely by being renamed
an authority store. A read-only flag or ACL shared with a principal that can
change it is insufficient. A separate OS principal or existing remote authority
could be investigated under a future bounded scope; neither is provisioned or
qualified here. A signature only helps if signer custody, verifier trust,
freshness and enforcement exclusion are independently established.

## 5. Trusted Owner/profile/workspace identity chain — UNKNOWN

The required chain is:

1. A known authority authenticates the human principal through Host-owned context.
2. Its stable principal is mapped to the selected authenticated service profile.
   The approval human and the capability account may differ; any permitted
   relationship must be explicit policy rather than assumed equality.
3. An independently maintained authorization mapping establishes that principal's
   current right to approve the exact Nexus workspace/project and capability scope.
4. The trusted handler binds that context to one pending proposal, including its
   Subject ID/digest, scope digest, operation/effect target and intended audience.
5. The authority records explicit human acceptance and its own context/generation;
   the trusted admission gate rechecks entitlement and context before committing.

Owner bootstrap is a prerequisite: the initial authorized Owner mapping must be
established by an already trusted operator/Host facility outside executor control.
Self-registering `issuer_ref`, setting `reviewer=user`, selecting a display email,
or returning a valid profile schema cannot bootstrap it. A repository path,
thread ID, CLI profile name, connected service account and ChatGPT organization
are distinct contexts; no automatic equality is allowed.

Needed evidence: authenticated decision-origin contract and verifier; stable
principal/profile mapping guarantees; independent Owner enrollment and removal;
trusted workspace/project resolution; selected-account binding; and behavior on
logout, account switch, role removal or workspace change. No credentials need to
appear in documentary evidence. An unavailable or ambiguous link must deny.

The missing chain is `UNKNOWN`; building a local identity wrapper would not turn
it into `VERIFIED`. Real admission remains `BLOCKED` at this prerequisite.

## 6. Executor write exclusion — UNKNOWN

The exclusion must cover more than grant files. The executor, its child processes,
plugins and writable tooling must be unable to mint, overwrite, delete, restore
or impersonate authoritative state or bypass enforcement. Required coverage:

| Protected surface | Required exclusion |
|---|---|
| Owner enrollment, profile/workspace mapping and policy | Executor cannot assign itself an Owner, swap the selected account or weaken scope. |
| Decision ingress and identity context | Executor cannot impersonate the trusted UI/handler, forge an accepted receipt or set authenticated context through ordinary client JSON. |
| Grant, revocation, evidence and replay/generation storage | Executor cannot replace records, suppress tombstones, restore old backups or reset counters. |
| Writer/verifier secrets or service identity | Executor cannot obtain usable authority credentials or impersonate the service through another API. |
| Gate code, launch configuration, dispatch path and recovery | Executor cannot modify or disable enforcement, substitute a process or use an unguarded execution path. |

The current local source explicitly uses same-user trust; the session allows
ordinary workspace writes. This supports rejecting executor-writable project
storage as an authoritative design. It does not prove the permissions or
vulnerability of a separate Host-internal service whose custody was not inspected.
No such independently protected service has been evidenced here.

Qualification requires the actual authority instance, effective process/service
identity and access rules, all writer/restore routes, protected enforcement
configuration, and controlled negative tests from the real executor context.
Tests must include overwrite/delete/replace, alternate transport, impersonation,
generation reset and gate bypass. Configuration descriptions and intended ACLs
alone are insufficient. Those live tests are not authorized or run in this phase.
This prerequisite remains `UNKNOWN`; real admission is `BLOCKED`.

## 7. Protected durable authority storage — BUILD_GAP

Reuse the existing closed `Subject`, `ApprovalGrant`, `Revocation` and
`EligibilityDecision` canonical records. Do not add unknown fields to their bodies
or reinterpret their hashes as signatures. Proposed authority metadata belongs
in a separately versioned, protected envelope/index maintained by the qualified
Host facility. No envelope or storage code is created here.

Minimum protected state is the exact canonical records plus: authenticated
authority/principal/profile/workspace references; proposal and material-context
digests; authenticated explicit-decision evidence; event namespace and nonce;
trusted creation/expiry observations; policy/context generation; current
revocation state; and transaction/admission-intent identities. Evidence should
retain only bounded nonsecret context needed to audit the decision. Grant effect
and validity remain exactly those in the accepted contract.

Only the qualified authority may commit a grant after verifying the trusted
decision. The untrusted bridge candidate is input data, never a credential for
that write. Revocation requires an authorized actor or independently enforced
policy invalidation, applies to an exact grant, and is durable before successful
acknowledgement. An expired or revoked grant cannot silently become active again;
fresh authorization must produce a distinct valid record and current context.

The store must commit decision evidence, nonce consumption and grant creation
atomically. Admission intent and its decision evidence must also be committed
together. Failed or ambiguous commits give no positive authority. Retries query
the same protected transaction identity; they cannot create replacement grants
or fresh dispatches merely because an acknowledgement was lost.

Historical authority records require logical append-only retention against the
executor. Indexes may evolve only through trusted transactions. Backup/restore,
compaction and repair must preserve revocation tombstones and freshness high-water
marks. Unknown rollback or incomplete recovery disables positive admission.
Checksums detect corruption; storing a hash beside writable evidence does not
authenticate its author. A hash chain alone does not detect restoration of an
older complete chain without an independent current checkpoint.

There is no implementation of these U1 store semantics in the reviewed G3 source.
Choosing a storage engine cannot resolve the unproven identity/exclusion boundary.
The contract is `BUILD_GAP`; implementing it now is `BLOCKED`.

## 8. Production replay protection and freshness — BUILD_GAP

Phase 2B's required `consumed_tokens` parameter is a verified offline seam. It
cannot prevent replay when a caller resets it, parallel callers lose updates or
the process restarts. A native request ID alone is not globally unique authority.

The proposed qualified authority must generate a fresh unpredictable nonce for
each pending approval, using its own secure randomness. It must namespace events
by authority instance/epoch, authenticated context and transport/pending-request
identity, preserving the distinction between numeric and string request IDs.
Bind the nonce to exact Subject, scope, effects, profile, workspace/project,
audience, policy generation and expiry. The client must not choose the trusted
nonce, epoch, current generation or evaluation time.

Consumption and the decision outcome commit in one protected transaction.
Concurrent callbacks for the same proposal permit at most one terminal decision;
duplicates cannot create a second grant. Conflicting terminal callbacks produce
no new authority and retain evidence for reconciliation. Denial, cancellation,
timeout, clearing and auto-resolution cannot become explicit human acceptance.
Session acceptance cannot be widened into a durable G3 grant by the adapter.

A current authority-owned context generation must advance on relevant Owner,
profile, workspace, policy or trust-boundary changes. Its trusted high-water mark
must survive restart and reject stale backups. Use an epoch change with protected
invalidation if continuity cannot be proved; never silently restart at zero and
reactivate old events. Relevant per-grant revocations and current policy must
still be checked under the admission transaction. Expiry requires trustworthy
time and an accepted skew bound; caller `now`, `startedAtMs`, file modification
time and a random process boot ID are insufficient substitutes. Uncertain time
or generation continuity must deny until independently recovered.

Consumed events remain rejected for their entire possible acceptance window.
Bounded cleanup is allowed only after the authority can prove the namespace/event
can no longer be accepted. Capacity exhaustion must deny, never evict live replay
protection. A consumed approval event may create one grant whose reuse follows
its declared scope/validity; every actual admission still needs its own unique
intent and current revocation check. Approval deduplication and dispatch
idempotency are separate requirements. All production mechanisms remain
`BUILD_GAP`, with implementation `BLOCKED` by sections 5-6.

## 9. Atomic revoke/admit serialization — BUILD_GAP

The proposed authority owns one serializable ordering for all state that can
change eligibility: grant/revocation, Owner entitlement, context/policy generation,
nonce consumption and admission intent. A per-task advisory lock or a read
followed by an independent file write cannot establish this order. A qualified
existing transactional facility is preferable to a new custom lock protocol.

Within one authoritative transaction, admission must: validate authenticated
context and current generation; resolve exact material Subject/scope/effects;
read the current grant and applicable revocations; check trusted time and
eligibility; reject a consumed admission identity; and durably commit the outcome,
evidence and unique dispatch intent. The trusted coordinator owns the gate through
dispatch handoff. Copied positive `EligibilityDecision` data cannot authorize a
later independent execution.

| Serialization case | Required result |
|---|---|
| Revocation commits before admission | Admission observes it and denies; no new intent is authorized. |
| Admission commits before revocation | That exact intent precedes revocation; subsequent admissions deny. It must not authorize additional or substitute work. |
| Operations overlap | The shared authority chooses one committed order; stale-snapshot acceptance is forbidden. |
| Context invalidation commits before admission | Stale proposal/grant context denies even if a previous decision was positive. |
| Crash before commit | No authorized intent; missing commit proof cannot be promoted to success. |
| Crash or lost acknowledgement after commit | Recover by the original transaction/intent ID; no fresh dispatch based on uncertainty. |
| Store unavailable, corrupt, rollback-suspect or contention unresolved | Deny or hold; never fallback to an executor-local approval copy. |

The linearization point is the protected admission/dispatch-intent commit, not a
UI click, earlier eligibility read, provider acknowledgement or completion.
Revocation is prospective from its authoritative commit. It does not prove an
already admitted remote effect was cancelled. Cancellation, running work,
unknown outcomes and reconciliation retain existing G2 handling and separately
authorized action boundaries. No exactly-once remote-effect guarantee is claimed.

If the required policy instead forbids starting any effect after a later revoke
commit, even for an earlier queued admission, the trusted dispatcher must recheck
or invalidate queued intents under the same ordering immediately before its
enforced start transition. A local preflight plus an uncontrolled executor does
not satisfy that stronger rule. No trusted dispatcher or such stronger rule has
been qualified. This phase implements neither interpretation; future acceptance
must explicitly select and evidence the required semantics.

## 10. Closure evidence and stop checkpoint

These are future qualification requirements, not tests run or authorization to
run them. Identity and exclusion must be proved first. A positive contract test
or new user approval to develop code cannot substitute for that proof.

| Gate | Minimum evidence required before status can become VERIFIED |
|---|---|
| U1-I: identity | Available authority/verifier contract; independent Owner enrollment; authenticated profile/workspace mapping; exact human proposal decision; switch/removal/forged-context denial. |
| U1-X: exclusion | Effective instance-specific custody/enforcement evidence and executor-context negative tests covering every protected write, restore, impersonation and bypass route. |
| U1-S: storage | Protected atomic grant/evidence/replay commit; exact durable revocation; independent recovery checkpoint; corruption and restore handling without positive fallback. |
| U1-F: freshness | Authority-generated nonce; durable concurrent consumption; restart/namespace/time/epoch rollback tests; bounded retention without replay reactivation. |
| U1-A: serialization | Concurrent revoke/admit and context-change histories with one demonstrable commit order; crash recovery by original intent; no stale positive decision dispatch. |

Evidence must identify the concrete Host/facility, version, effective policy and
executor context. A generic product description, package presence, CLI schema,
claimed ACL, approval screenshot or synthetic transcript is insufficient. No
positive Host binding or new provider qualification is inferred from accepted G2.

Resume only with a separately bounded investigation of an existing authority
facility that can resolve U1-I and U1-X. If it cannot supply these guarantees,
report `UNKNOWN` or `BLOCKED` and stop again. If it can, complete and qualify the
other three properties before requesting or using a separate authorization for
real admission implementation. This document grants none of that authority and
does not ask for credentials or a live login.

## 11. Documentary completion and unchanged boundaries

This phase adds this architecture document and its static manifest entry. The
333 prior manifest entries remain unchanged; the regenerated manifest has 334
entries. Regeneration uses the existing builder against an isolated source-only
snapshot, preserving its frozen guards. Static validation checks the five status
rows, explicit NO/BLOCKED gate, local document links, whitespace, bounded
secret-pattern checks, prior schema hashes, source equality and historical draft
hashes. These checks verify the documentary change, not production U1 behavior.

The public G3 fail-closed evaluator, offline bridge, Core/G2, tests, package rules,
plugin/MCP integration and accepted historical evidence remain byte-unchanged
apart from checkout line-ending normalization used for manifest comparison. The
three historical Route D successor drafts remain unchanged and untracked. No
real admission, grant issuer, protected store, new Host process, provider
execution, credential operation, policy change, installation, commit, push,
merge, tag, freeze or release is performed in this phase.

```text
U1_IMPLEMENTATION_READY = NO
REAL_ADMISSION_IMPLEMENTATION = BLOCKED
NEW_PROVIDER_EXECUTIONS = 0
CREDENTIAL_OPERATIONS = NONE
EXISTING_FAIL_CLOSED_BOUNDARY = UNCHANGED
```
