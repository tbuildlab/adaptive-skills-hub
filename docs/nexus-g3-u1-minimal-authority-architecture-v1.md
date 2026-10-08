# Nexus G3 U1 minimal authority architecture v1

Date: 2026-10-08. Phase: Minimal Nexus Authority Architecture Phase 1.
Reviewed source checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`
on `nexus-v2-g3-development`.

```text
MINIMAL_AUTHORITY_ARCHITECTURE = DEFINED
PREFERRED_AUTHORITY_OPTION = C
OWNER_BINDING_DESIGN = VERIFIED_EXTERNAL_PRINCIPAL_PLUS_AUTHORITY_OWNED_EXACT_WORKSPACE_PROJECT_BINDING
PROTECTED_STATE_DESIGN = SINGLE_REMOTE_TRANSACTIONAL_LEDGER_WITH_INDEPENDENT_RECOVERY_FENCE
ANTI_REPLAY_DESIGN = AUTHORITY_NONCE_DURABLE_CONSUMPTION_EPOCH_AND_NONROLLBACKABLE_RECOVERY_CHECKPOINT
ATOMIC_ADMISSION_DESIGN = ONE_SERIALIZED_REVOKE_ADMIT_DISPATCH_CLAIM_DOMAIN
EXECUTOR_EXCLUSION_DESIGN = DISTINCT_OWNER_AUTHORITY_AND_EXECUTOR_SECURITY_CONTEXTS_PLUS_GATE_COMPLETE_MEDIATION
NEW_TRUSTED_COMPONENT_COUNT = 2
U1_MINIMAL_IMPLEMENTATION_READY = NO
```

`DEFINED` means that the minimum responsibilities, boundaries, ordering rules,
and conditional deployment choice are specified. It does not mean that a concrete
Host, identity integration, storage service, or enforcement deployment is
qualified. The design names blockers instead of assuming those facilities exist.
The component count is planned new Nexus trusted code, not deployed components
and not the total infrastructure trusted computing base.

## 1. Authorization and evidence boundary

The latest Owner instruction permits a minimal Nexus-owned authority layer.
That changes the earlier prohibition on owning such a layer; it does not erase
the findings in the [trusted-admission assessment](nexus-g3-u1-trusted-admission-architecture-v1.md)
or the [Host qualification report](nexus-g3-u1-host-authority-qualification-v1.md).
Neither report established an available complete OpenAI Host authority for U1-I
and U1-X. Their bytes remain unchanged.

This deliverable designs exactly seven functions: Owner binding, bound approval
receipt, protected authority state, replay/freshness, revoke/admit serialization,
protected intent/dispatch, and executor exclusion. Identity issuance, account
administration, provider execution, a general policy engine, generic approval
workflows, and secret distribution are outside that authority.

No real admission, grant issuance, revocation issuance, identity enrollment,
credential access, provider execution, account/policy change, service deployment,
or permission change occurs in this phase. Existing public eligibility continues
to deny. No existing G3 canonical body changes.

Component classification has the requested meanings:

| Label | Meaning in this document |
|---|---|
| REUSE | Existing contract or infrastructure primitive reused for its limited documented purpose; concrete qualification may still be required. |
| NEW_MINIMAL | New Nexus code necessary for one of the seven responsibilities; proposed only. |
| NOT_NEEDED | Omitted from the minimum design. |
| BLOCKED | Required integration or guarantee has no qualified available implementation in the reviewed environment. |

Evidence and design claims are distinct. Local source facts below were inspected;
product facts are supported by linked official documentation; proposed guarantees
are requirements and engineering judgments. An unavailable or unproven feature
is not asserted to be impossible.

## 2. Existing contracts and compatibility

Primary local evidence is [G3 authorization](../ash/g3_authorization.py),
[the offline Host bridge](../ash/g3_host_approval_bridge.py), the
[Phase 2A contracts](nexus-g3-authorization-contracts-v1.md), and the
[Phase 2B bridge contract](nexus-g3-host-approval-bridge-contract-v1.md).

| Existing contract | Required reuse and preserved meaning |
|---|---|
| `Subject` | Preserve kind-specific identity, canonical bytes, domain-separated ID and cosmetic-field exclusions. Recompute from frozen material; a display name never identifies a capability. |
| `ApprovalGrant` | Preserve its closed v1 body, Subject binding, scope, effective/expiry times, `issuer_ref`, evidence reference/hash, and required local-component review semantics. Add no Owner, nonce, epoch or effect fields to this body. |
| `Revocation` | Preserve its closed v1 grant reference, time, issuer, evidence and reason. Link it to protected authority provenance through separate metadata. |
| `EligibilityDecision` | Preserve v1 `dispatch_authority=none` and the allowed `REAL_ADMISSION_DISABLED` / `TEST_FIXTURE_ONLY` bases. A positive fixture decision is never a production authorization. |
| `HostApprovalProposal` | Preserve proposal ID and canonical binding to native request, Subject, exact scope/hash, requested action and effect summary. Verify all joins; do not trust an executor-supplied digest without material. |
| `HostApprovalEvent` | Preserve explicit/automatic/unknown origin and resolution distinctions and the complete request identity tuple. An event body supplied by the executor is untrusted evidence input. |
| `HostDecisionEvidenceCandidate` | Preserve `OFFLINE_CONTRACT_ONLY`, `owner_authenticated=false`, `approval_authority=none`, `dispatch_authority=none`. Archive unchanged candidate bytes; never edit these flags to promote it. |

The bridge's candidate is canonical evidence bytes carried by its correlation
result, not an already trusted Owner receipt. Its caller-supplied consumed-token
set is an offline correlation aid, not production replay storage. Existing hashes
prove byte binding, not issuer authenticity. Existing per-task `exclusive_run`
and file replacement routines do not provide the proposed authority transaction.

The public v1 `evaluate_eligibility` returns `NOT_ELIGIBLE`; valid inputs reach
`G3_APPROVAL_ORIGIN_UNVERIFIED`. Reusing it cannot produce real admission. A later
explicitly reviewed, separately versioned production decision contract and gate
integration are required. This document does not authorize bypassing that denial,
calling the private fixture seam, accepting copied decision JSON, or changing v1
bases. The new receipt/intent metadata below are proposals for that future
contract review, not an implicit replacement of v1.

## 3. Smallest deployment options

All options require a trusted Owner confirmation path and complete mediation of
the specific effects Nexus admits. Locating a ledger elsewhere is insufficient
if the executor can bypass the dispatch gate or act as the Owner.

| Criterion | A: separate local OS service/principal | B: OpenAI primitive plus thin state | C: small remote authority |
|---|---|---|---|
| Executor exclusion | Conditional on three separated contexts: Owner/Host, service, executor; no administrator, impersonation or process-injection escape. | Host-side isolation is useful, but no qualified arbitrary Nexus Owner approval/state API was established. | Remote administrative and store permissions can be absent from the executor; Owner/Host ingress must also be separate. |
| Rollback resistance | Same-machine backups or VM snapshots can restore both ledger and counters. Needs an independent existing checkpoint facility or recovery quarantine. | No exposed Nexus consumption/epoch/recovery guarantee was qualified. | Can separate authority recovery from executor-host restoration; still needs independent recovery fencing for authority backups. |
| Operational complexity | OS installation, ACLs, protected dependencies, isolated executor and external recovery facility. | Lowest only if the missing Host authority API exists and is available; currently blocked. | One application, one existing transactional store and an existing independently administered recovery primitive; networking and deployment operations remain. |
| Portability | Windows/Linux principal, IPC, launch and process-protection qualification differ. | Portable only within an available documented Host contract. | Executor clients can remain thin; platform-specific Owner/Host protection still requires qualification. |
| Auditability | Local events must survive local administrative restoration; independent export needed. | Existing product logs cannot be assumed to bind Nexus canonical proposals. | One ordered authority ledger plus independent commit/recovery checkpoint; sanitized local mirrors are non-authoritative. |
| Recovery safety | Whole-host restoration is a major shared failure domain. | Not established for Nexus grants/revocations. | No automatic restore-and-resume; independently fenced recovery and fresh Owner confirmation are explicit requirements. |
| Minimum new trusted code | Authority core and protected approval adapter; independent checkpoint integration may increase infrastructure. | Thin adapter/state only in the hypothetical qualified case; cannot claim a smaller working option today. | Authority core and protected approval adapter; standard identity, storage, TLS and recovery infrastructure reused. |
| Phase 1 disposition | Conditional fallback; not selected. | BLOCKED as a complete authority option. | Preferred conditional architecture; concrete deployment remains BLOCKED. |

**Choose C as the target architecture.** This is an engineering judgment, not a
claim of an already provisioned service. Its advantage is custody and recovery
separation from the executor host, including the currently broad local execution
context. A qualified A must add that separation through an external checkpoint
and an isolated Owner context, reducing its apparent simplicity. C still cannot
claim whole-authority rollback resistance from an ordinary remote database alone.

No D is strictly simpler while meeting all seven responsibilities. A same-user
daemon, repository JSON, browser-local storage, an encrypted local file, or an
executor-held HMAC key fails exclusion or restoration requirements. A remote
ledger without a protected gate also fails. Do not select B based on a future
undocumented OpenAI capability.

If C's existing identity/Host/recovery dependencies cannot be qualified, stop;
do not silently build substitutes. Revisit A only through an explicit deployment
review that proves its additional boundaries. No option is installation-ready.

## 4. Component inventory and bounded trusted code

| ID | Classification | Component | Responsibility and limit |
|---|---|---|---|
| R01 | REUSE | G3 canonical contracts and strict parsers | Unchanged data binding/validation; no authority inference from hash or parser success. |
| R02 | REUSE | OpenAI/Codex interaction and native approval UI | Present requests and decisions where supported; native command consent is not automatically Nexus capability consent. |
| R03 | REUSE | Existing authenticated identity primitive | Candidate OpenAI verified identity or already operated enterprise identity; issuer creates identities, Nexus only consumes verified assertions. |
| R04 | REUSE | Host account/workspace/thread context | Auxiliary context only; explicit Nexus mapping is mandatory. |
| R05 | REUSE | Existing transaction engine | Protected remote ledger uses a qualified existing engine; no custom database. |
| R06 | REUSE | Existing deployment, OS isolation and standard TLS | Protect ingress, process closure, storage permissions and transport; no new PKI. |
| R07 | REUSE | Existing OpenAI execution facilities | Used only behind a separately qualified bounded dispatch gate, with existing G1/G2 restrictions. |
| N01 | NEW_MINIMAL | Nexus authority core | One remote process/code component owns exact binding, receipt validation, ledger transitions, nonce/epoch, revoke/admit serialization, bounded dispatch claims and recovery checks. No generic policy language or credential proxy. |
| N02 | NEW_MINIMAL | Protected Nexus-to-Host approval adapter | Fixed proposal presentation/callback integration in a trusted Owner/Host context. It binds explicit confirmation to the authority challenge and relays trusted context. No new generic UI, identity provider or approval service. |
| D01 | BLOCKED | Qualified identity access for Nexus | No registered/available OpenAI identity integration or alternative current principal chain has been demonstrated. |
| D02 | BLOCKED | Exact trusted Host confirmation integration | Protected callback origin, complete canonical presentation and lifecycle/session binding are not currently qualified. |
| D03 | BLOCKED | Independent recovery checkpoint/fence | No concrete existing facility with the required non-rollbackable write/read and recovery semantics is qualified. |
| D04 | BLOCKED | Complete enforcement deployment | Executor identity, process/Host separation, direct-route exclusion and protected provider dispatch are not demonstrated. |
| D05 | BLOCKED | Separately versioned production decision seam | v1 eligibility/candidate cannot carry positive authority. Future contract and integration review are required. |
| O01 | NOT_NEEDED | General IAM, roles platform or OAuth provider | One fixed Owner binding per workspace/project; no identity issuance, federation administration or role hierarchy. |
| O02 | NOT_NEEDED | Generic vault, policy platform or approval service | No arbitrary secret API, workflow engine, policy DSL or multi-application consent service. |
| O03 | NOT_NEEDED | Custom PKI / transferable signed grant tokens | Preferred model queries authority and dispatches through its protected gate. Existing TLS and issuer verification suffice conditionally. |
| O04 | NOT_NEEDED | New approval UI or extra broker daemon | Use a qualified existing Host surface through N02. If unavailable, block rather than invent a new UI or general broker. |

Exactly two **new Nexus trusted code components** are proposed: N01 and N02.
Ledger tables, recovery verification and the provider-specific dispatch function
belong to N01, not additional services. Database/TLS/identity/recovery platforms
remain part of the total trusted computing base. The count is not evidence that
these dependencies exist or that an unqualified checkpoint can be omitted.

OpenAI's website identity flow documents verified issuer/client/`sub` identity,
with signature, audience, expiry and nonce checks. It is an identity primitive,
not an approval for a Nexus Subject. The plugin integration is a limited trial
and describes separate identity and connector transactions; availability for
Nexus is unproven. Do not implement a connector OAuth server merely to exploit
that example. [Website identity](https://developers.openai.com/siwc/website),
[plugin identity](https://developers.openai.com/siwc/chatgpt-plugin).

The app-server documents client decision payloads, cleared requests, automatic
resolution, and MCP elicitation. These are interaction seams, not an authenticated
Nexus receipt. N02 requires a qualified protected integration, not raw JSON from
an executor-controlled app-server client. [App-server approvals](https://learn.chatgpt.com/docs/app-server).

## 5. Minimal authority records and rules

The names in this section are design labels for **new, separately versioned
metadata contracts to be reviewed later**. No schema, executable module, record,
grant, or receipt is created by this phase. Each metadata record references the
unchanged v1 canonical bodies by exact bytes and their existing IDs/hashes.

### 5.1 Owner binding and recovery root

One binding joins `(verified issuer, client/audience, stable subject)` to
`(Nexus authority instance, workspace_id, project_id, binding_generation)`.
Use an already existing OS/enterprise identity only if its realm and stable
principal identifier are authenticated independently of the executor. Never
substitute email, display name, a filesystem path, Host project title, thread ID,
plugin profile JSON, or a process ID for that identity proof.

The authenticated Owner must confirm the exact Nexus workspace/project. Workspace
registration records the designated protected dispatch environment/root identity;
paths are explanatory metadata and must be revalidated against that registration.
A copied checkout, rename, new worktree or a same-string `workspace_id` is not
automatically the registered project. No mutable repository marker is the root of
binding authority. Only the protected registration/mapping resolves this join.

First enrollment and later rebinding require an existing trusted administrator
or independently authenticated Owner enrollment ceremony outside executor control.
No trust-on-first-use enrollment from the executor is allowed. Recovery must
revalidate the current binding against the independent recovery root, not restore
an old binding table and accept the former Owner. First deployment is blocked
until that existing enrollment/recovery route is named and qualified.

The minimum has one active Owner per project, no delegation, no transferable
membership and no inference of Nexus ownership from an OpenAI workspace role.
Removing or replacing the Owner closes the binding generation and invalidates
all dependent pending approvals, grants and unclaimed intents.

### 5.2 Approval receipt and canonical joins

The protected receipt must bind all of the following in one authority-owned
record: verified Owner identity and session/context generation; binding ID and
generation; exact workspace/project; `proposal_id`; exact canonical Subject and
Subject ID; exact canonical scope and scope hash; requested action; complete effect
summary and target material/hash; nonce; authority instance/epoch; challenge
creation/expiry; explicit decision; trusted Host request identity and confirmation
origin; immutable evidence references and resulting grant ID when later issued.

Authority validates the proposal's exact bytes using the existing G3 rules and
derives all digests itself. The Host presentation must show the actual targets,
operations and effects, including the workspace/project, from those same frozen
bytes. Showing only a target hash, native command reason, or abbreviated title
does not establish informed exact-scope approval. Target material is separate
referenced evidence; it is not added to the v1 proposal body.

Only explicit Owner acceptance through the protected N02 path can satisfy the
receipt. Automatic acceptance, session-wide acceptance, policy amendment,
clearing, cancellation, timeout, missing origin, and plain conversation text do
not. N02 must not manufacture a harmless pending command to obtain consent for
an unrelated capability. Native request/action and approved Nexus effect must
match, and native execution must remain behind the protected gate.

`HostApprovalEvent` and `HostDecisionEvidenceCandidate` are retained unchanged as
correlation evidence. The new receipt obtains authority from independent verified
identity plus protected confirmation, not from relabeling the candidate.
The v1 grant's `decision_evidence` references the protected receipt bytes/hash;
its `issuer_ref` resolves to N01's protected instance registration. Those strings
alone cannot establish provenance outside the protected ledger.

No executor-readable bearer receipt authorizes effects. Receipt copies are audit
artifacts; authoritative reads and dispatch decisions occur at N01. The preferred
design therefore needs no custom receipt signing keys or custom PKI.

### 5.3 Protected state and freshness

Use one transaction domain containing binding generations, immutable G3 bodies,
receipt/evidence bytes, grant provenance, revocation tombstones, challenge/nonce
consumption, decision records, epochs, monotonic sequence, admission intents and
dispatch-attempt state. The authority is the only application writer. The executor
has no database account, backup/restore rights, cloud administrator role, object
write permission or maintenance endpoint.

Preserve revocation and consumption tombstones for at least the lifetime of every
recoverable record they invalidate; minimal v1 deletes none of them. Exports are
non-authoritative. Do not import grants from a repository, local mirror or backup
without the recovery procedure. Evidence hashes detect changes, not rollback.

Reuse a transactional engine with a tested durable commit configuration. SQLite
illustrates single-writer serialization and crash-atomic commit, but would require
qualified filesystem/durability and independent recovery protection; its mere
presence is not a C deployment choice. [Transactions](https://www.sqlite.org/lang_transaction.html),
[atomic commit](https://www.sqlite.org/atomiccommit.html).

N01 generates at least 256 random nonce bits through the platform CSPRNG and
enforces a unique nonce/challenge key. Nonces are unpredictable identifiers, not
secret approval credentials. The protected ledger consumes a nonce once in the
same transition that records its receipt and grant provenance. Duplicate or
conflicting decisions cannot reopen it. Minimal grants are short-lived, tied to
one exact task/scope and one dispatch intent; the v1 shape's broader/null-expiry
possibilities are not enabled by this authority design.

For the minimum target, a challenge expires within five minutes; a grant expires
within ten minutes of explicit confirmation and never outlives its authenticated
Owner context. Require an exact `task_id`, a single intended dispatch, and exact
scope equality at use, even though the unchanged v1 predicate supports broader
set coverage. Require matching `account_context` wherever the Subject/provider
uses an account. These are authority restrictions, not changes to canonical v1
validation. Pending expiry does not trigger automatic approval.

Use an authority-instance identifier, durable epoch and ordered sequence, plus a
fresh per-start incarnation. Pending confirmations and unclaimed intents do not
survive restart. Minimum recovery also retires pre-restart grants rather than
automatically reactivating them. Independently retained revocations, consumption
and binding-removal history remain authoritative. OS wall time is not supplied
by the executor; detect regression against protected time high-water evidence,
use monotonic elapsed time within an incarnation, and block uncertain expiry.

The recovery fence must be outside the authority database's restore domain and
outside executor administration. It retains instance, epoch, sequence and commit
digest, supports conditional advancement, and cannot be reset to an older value
by the ordinary restore path. This is a required existing infrastructure primitive,
not a proposed extra Nexus witness service. A second file/table in the same backup,
a hash chain alone, or a mutable counter restored with the database does not work.

Every authority-affecting commit must reach that fence before it is acknowledged
as durable or permits dispatch. If ledger and fence cannot commit atomically,
record a prepared transition, advance the independent fence conditionally, then
finalize locally; release no authority before both durable acknowledgments.
Any ambiguous interval or mismatch quarantines the instance. Do not automatically
advance the fence from restored database content or roll it back to match a backup.
This favors safe unavailability over claiming a distributed atomic commit.

Restoration of the executor host cannot restore C's remote authority. Restoration
of C's database must compare with the independent fence, require a current trusted
recovery ceremony, retire outstanding authority and reconcile external attempts.
If the entire authority and its supposedly independent fence can be rolled back
together, freshness is not proven and admission stays closed. The concrete fence
and provider recovery guarantees are D03, currently BLOCKED.

### 5.4 Atomic revoke, admit and dispatch

N01 owns one bounded serialization domain for all seven responsibilities. Minimum
v1 uses a single writer/dispatcher per authority instance; no distributed active-
active leader, split-brain failover, or executor-side decision cache is required.

Conceptual ordering, for later implementation review only:

1. Accept untrusted proposals without authority. Strictly validate and freeze
   bytes/material; create a challenge tied to current binding/epoch/context.
2. Receive protected Owner confirmation. Recheck identity and every join; atomically
   consume the challenge and record receipt, evidence and grant provenance.
3. On an admission request, re-read current binding, context, epoch, expiry,
   consumption and revocations in the write serialization domain. Independently
   obtain technical/task/Host/G1/G2 facts from their qualified sources. Never accept
   executor-supplied boolean assertions as observations.
4. A future separately reviewed production decision seam may create exactly one
   immutable intent with frozen Subject/scope/effects, grant/receipt references,
   executor environment identity and idempotency/attempt ID. Commit evidence and
   replay state before returning a reference; the reference grants no bearer rights.
5. Immediately before dispatch, recheck the same authority and current material.
   Atomically claim that intent once, consume its dispatch allowance and mark an
   attempt reserved. Complete the durable fence protocol before calling the
   existing provider through the protected bounded adapter.
6. Revocation uses the same serialization domain. Commit a tombstone and invalidate
   all dependent unclaimed intents before reporting completion. A revoke ordered
   before intent creation or dispatch claim prevents them. A grant issued later
   requires fresh explicit confirmation; old evidence cannot resurrect the grant.

Owner-issued revocation requires the same protected current principal/binding
checks as confirmation. N01 may deny/retire authority automatically on observed
context loss or fault; the executor can report a fault or cancel its own pending
request, but cannot create authoritative Owner revocation evidence. Minimal
issuance uses immediate revocation and immediate grant effectiveness only; no
future scheduling or policy workflow is needed.

The **dispatch claim**, after its durability/fence completion, is the authorization
linearization point for starting that attempt. Admission-intent creation alone
does not beat a later revoke that precedes the claim. Keep the serialization gate
through the bounded handoff attempt, with bounded timeouts; a revoke is acknowledged
only after its turn in that ordering. Pending revocation requests take priority
over new claims to avoid starvation.

A revoke after a claim prevents later claims, but cannot promise to undo an
already handed-off action or its later external effect. Record that distinction
in evidence. Database atomicity is not atomicity with an external provider.
After a crash, timeout or missing provider acknowledgment, classify the attempt
as uncertain, consume it permanently and deny automatic redispatch. Read-only
provider reconciliation, if separately authorized, can resolve the same attempt;
it cannot manufacture a replacement run. Exactly-once external execution is not
claimed. Any requested stronger cancellation guarantee is a separate blocker.

The dispatcher supports only the reviewed Nexus capability route and frozen
payload. It is not a general shell, arbitrary destination proxy, secret read API
or account administrator. Existing provider client code must run from a protected
dependency closure or qualified Host-side adapter. If the executor can change
the code/config/material after checking, subject binding fails and dispatch closes.

Each admitted operation/target must map to existing enforceable provider, tool or
OS restrictions in that route. A one-time grant to start arbitrary unrestricted
agent code is insufficient to enforce exact effects. Freeze executable/config
material and use qualified sandbox/tool permissions throughout execution; any
scope item lacking an enforcement mapping remains blocked. This requirement does
not enlarge a granted scope or replace existing G1/G2 restrictions.

## 6. Trust-boundary register

These nine boundaries cover the minimum design. Locations are logical deployment
requirements, not directories, services or accounts created during this phase.

### T01. Identity issuer to protected Owner/Host context

| Attribute | Requirement |
|---|---|
| Authoritative writer | Existing identity issuer authenticates the account; qualified protected Host supplies the active Owner/session context. N01 verifies assertions. |
| Authoritative reader | N01 identity ingress and N02 protected confirmation adapter. |
| Executor permissions | May request presentation; no identity/session token read, callback write, cookie access, Owner process injection or issuer administration. |
| Persistence location | Existing issuer; only verified identity mapping and bounded session/context metadata in remote protected state. No raw credentials in Nexus evidence. |
| Recovery semantics | Fresh verified identity and current binding are required after recovery; no restored browser/session cache grants authority. |
| Replay semantics | Verify signature/issuer/audience/expiry and identity-transaction nonce; separately validate the Nexus approval nonce. Identity sign-in nonce is not approval consent. |
| Revocation semantics | Owner session loss, logout, account switch or lost eligibility closes that session/context generation before another claim. |
| Failure mode | Identity unavailable, stale session, shared Owner/executor context or untrusted lifecycle signal. |
| Fail-closed behavior | No trusted receipt or dispatch claim. Token expiry alone cannot prove instantaneous logout invalidation; absent qualified lifecycle observation, readiness is blocked. |

### T02. Enrollment and exact workspace/project binding

| Attribute | Requirement |
|---|---|
| Authoritative writer | N01 after a qualified authenticated Owner/admin enrollment or rebinding ceremony; independent recovery root constrains restoration. |
| Authoritative reader | N01 receipt and dispatch validators; Owner receives a scoped readback. |
| Executor permissions | Submit workspace/project claims for comparison only; no mapping, registration, root identity or binding-generation write. |
| Persistence location | Remote protected binding/registration tables and independently retained recovery checkpoint. |
| Recovery semantics | Verify current mapping against the independent root; restored/deleted/replaced bindings never auto-reactivate. |
| Replay semantics | Every challenge/receipt/intent carries binding generation and exact registered project/environment identity. |
| Revocation semantics | Unbind, workspace switch, Owner replacement or relevant role removal closes the generation and all dependent authority. |
| Failure mode | Same label at a different root, copied workspace marker, forged Host context or missing current Owner proof. |
| Fail-closed behavior | Reject binding and all joins; do not bootstrap from an executor's claim. |

### T03. Protected approval UI/callback to receipt

| Attribute | Requirement |
|---|---|
| Authoritative writer | N01 records the receipt only after N02 conveys independently authenticated, explicit Owner confirmation of the authority-frozen proposal. |
| Authoritative reader | N02 obtains frozen presentation; N01 validates callback and all canonical joins. |
| Executor permissions | Submit proposals/correlation evidence and view permitted readbacks; cannot select the decision, replace rendered material or call protected confirmation as Owner. |
| Persistence location | Immutable receipt/proposal/event/candidate/evidence bytes in remote ledger; ephemeral presentation in protected Host context. |
| Recovery semantics | Pending UI decisions are retired on restart/recovery; require a new challenge and explicit confirmation. |
| Replay semantics | Single-use authority nonce, session/epoch/binding generation and exact proposal/request identity. |
| Revocation semantics | Context loss or binding change invalidates pending challenges; grant revocation invalidates derived use. |
| Failure mode | Automatic/cleared/timed-out response, generic command consent, hidden effects, spoofed callback or changed proposal. |
| Fail-closed behavior | Record denial/uncertainty if possible; issue no receipt authority. No qualified N02 integration means D02 remains blocked. |

### T04. Authority ledger and durable evidence custody

| Attribute | Requirement |
|---|---|
| Authoritative writer | N01's restricted application principal; separate trusted operator only for controlled maintenance/recovery. |
| Authoritative reader | N01; scoped Owner audit/export reads. Executor receives sanitized copies through status API. |
| Executor permissions | No direct store, journal, backup, restore, maintenance, retention-policy or cloud-account permissions. |
| Persistence location | One remote transactional store with protected evidence and all authority indexes in the same commit domain. |
| Recovery semantics | Recover complete transactions, verify independent checkpoint, quarantine ambiguous state; never resume from an arbitrary backup. |
| Replay semantics | Uniqueness/consumption/tombstones commit with decisions, receipts and intent changes. |
| Revocation semantics | Immutable revocation records and active deny indexes are transactionally joined; minimum design deletes no authority history. |
| Failure mode | Commit/fsync failure, corruption, missing evidence, stale replica, restore or uncertain write acknowledgment. |
| Fail-closed behavior | No acknowledged authority or dispatch. Audit-write failure blocks positive action, even if a hash matches. |

### T05. Epoch, consumption and independent recovery fence

| Attribute | Requirement |
|---|---|
| Authoritative writer | N01 generates nonce/incarnation and advances ordered authority transitions; existing independently administered fence conditionally records durable progress. |
| Authoritative reader | N01 startup, recovery and dispatch validation; trusted recovery operator. |
| Executor permissions | May know nonce/epoch labels; cannot generate authoritative challenges, reset consumption, advance/reset fence or restore epochs. |
| Persistence location | Consumption and epoch in ledger; checkpoint in an independently protected, non-co-restored existing facility. |
| Recovery semantics | Exact checkpoint reconciliation before reopening; new incarnation retires pending/grant/intent authority, preserves historical invalidation. Mismatch requires trusted recovery. |
| Replay semantics | Reject used nonce, stale epoch/incarnation, old binding/context generation, non-current sequence or duplicate attempt. |
| Revocation semantics | Revoke/Owner removal advances authority state and fence; restored pre-revoke history cannot authorize. |
| Failure mode | Whole-store rollback, fence reset/unavailability, clock regression, split brain or partial fence protocol. |
| Fail-closed behavior | Quarantine. Random epochs, checksums and hash chains do not replace independent freshness proof. |

### T06. Revoke/admit serialization and eligibility provenance

| Attribute | Requirement |
|---|---|
| Authoritative writer | N01's single serialized transition function; future production decision seam only after explicit contract approval. |
| Authoritative reader | N01 consumes current ledger and independently qualified technical/task/Host/G1/G2 evidence. |
| Executor permissions | Request evaluation/revocation routing and receive status; cannot supply authoritative gate booleans, transaction locks or production decisions. |
| Persistence location | Same protected transaction domain as grants, revocations, evidence, consumption and intent. |
| Recovery semantics | Committed transitions only; ambiguous or partially fenced transitions close the instance. No local cached decision after restart. |
| Replay semantics | Decisions bind exact request/material/current generation; positive decision copies have no bearer effect. |
| Revocation semantics | Revoke before admit denies; revoke before claim cancels pending intent; post-claim limits are recorded explicitly. |
| Failure mode | Lock/transaction error, stale read, missing prerequisite provenance, unreviewed v1-to-production promotion. |
| Fail-closed behavior | Deny and keep public v1 disabled. An authority receipt never overrides another G1/G2/task/Host restriction. |

### T07. Protected intent and existing execution dispatch

| Attribute | Requirement |
|---|---|
| Authoritative writer | N01 creates and claims an intent; qualified protected dispatcher records bounded handoff and subsequent outcome evidence. |
| Authoritative reader | N01 and its fixed dispatch adapter; existing provider accepts only the protected route/allowed operation. |
| Executor permissions | Request use of an intent reference and execute only the admitted payload in its designated environment; cannot create/alter/claim intent state or reach equivalent privileged routes directly. |
| Persistence location | Immutable intent and attempt records in ledger; provider's existing run state is external outcome evidence. |
| Recovery semantics | Unknown handoff remains uncertain and consumed; no retry/replacement. Unclaimed intents retire on restart. |
| Replay semantics | Unique claim and attempt ID, current fence/epoch and exact frozen payload. No transferable dispatch token or local cache. |
| Revocation semantics | Recheck at claim; earlier revoke blocks claim. Later revoke does not promise to undo an external action already ordered. |
| Failure mode | Timeout, provider ambiguity, bypass route, changed payload, local TOCTOU or unprotected dispatch adapter. |
| Fail-closed behavior | No call without durable claim; uncertain attempt never automatically redispatches. Any uncovered equivalent route blocks readiness. |

### T08. Executor versus code, Host processes and administrative control

| Attribute | Requirement |
|---|---|
| Authoritative writer | Trusted deployment operator installs N01/N02/dependencies and fixed permissions; approved release process only. |
| Authoritative reader | OS/runtime enforcement plus startup verification; N01 consumes protected registration. |
| Executor permissions | No administration, process injection, Owner impersonation, service-control/config/code/library writes, callback routing changes or credential custody. |
| Persistence location | Protected remote deployment and protected Owner/Host installation; executable/dependency/config closure outside executor-write roots. |
| Recovery semantics | Redeploy verified closure and requalify effective isolation before reopening; user-writable imports/config are disallowed. |
| Replay semantics | Older vulnerable service/config release cannot be selected through executor restore or downgrade. Version/fence mismatch quarantines. |
| Revocation semantics | Isolation failure, component replacement or loss of Host session protection closes all pending authority and future claims. |
| Failure mode | Same OS principal for Owner and executor, administrative token, leaked app credential, writable dependency or cross-environment escape. |
| Fail-closed behavior | Stop all admission. A different process ID, path ACL alone or a detached daemon does not prove exclusion. |

### T09. Maintenance, backup, export and disaster recovery

| Attribute | Requirement |
|---|---|
| Authoritative writer | Existing trusted recovery administrator, with authenticated current Owner participation where binding/approval must be renewed; N01 enforces the closed recovery protocol. |
| Authoritative reader | N01 checks immutable evidence against independent fence and current binding; Owner receives auditable recovery disposition. |
| Executor permissions | No backup import, export-to-authority promotion, fence maintenance, epoch reset, retention change or recovery completion. |
| Persistence location | Protected store backups plus separately administered checkpoint/history; sanitized repository exports remain non-authoritative. |
| Recovery semantics | Close first, compare latest independently retained history, reconcile uncertain attempts, retire old authority, re-establish current binding and require fresh approvals. |
| Replay semantics | Restored used/non-current records cannot become pending/usable. Entire fence/store co-rollback is unqualified and blocked. |
| Revocation semantics | Latest binding removal/revocation dominates recovery; lost or conflicting deny history prevents reopening. |
| Failure mode | Missing checkpoint, unexplained history gap, rollback of both domains, revoked Owner performing recovery or claimed successful run without provider evidence. |
| Fail-closed behavior | No restore-and-resume, no reset-to-empty authority, no recovery performed by the executor. |

## 7. Feasibility and rejection rules

For A, reuse OS-authenticated principal/IPC security, not a JSON `owner_id` or
same-user pipe. Windows supports token-based named-pipe access checks and client
impersonation; a secure design needs explicit DACLs and restricted instance-creation
rights. These primitives do not establish human intent or a Nexus binding by
themselves. No service/account/ACL is created here.
[Pipe security](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights),
[client identity](https://learn.microsoft.com/en-us/windows/win32/ipc/impersonating-a-named-pipe-client).

For C, existing OpenAI identity remains useful if available, but a fresh identity
assertion alone does not prove exact approval. N02 must run in a protected Owner
context that executor automation cannot control. Native account/workspace changes
must be observed through a qualified trusted lifecycle source; polling a caller's
claimed account name or relying only on JWT expiration does not meet immediate
invalidation. Relevant role eligibility must come from its authoritative source;
if unavailable, do not claim role-removal safety. Independent Nexus unbinding is
always serialized by N01.

Existing OpenAI isolation and restricted environment credentials can assist
execution separation. Documentation says agent code can read available environment
credentials and the restricted environment key; application keys must remain
outside that environment. This supports the required custody split, not proof
of the current deployment or its bypass resistance.
[Sandbox security](https://developers.openai.com/api/docs/guides/agents-api/environments/security).

| Required responsibility | Phase 1 design | Concrete feasibility blocker |
|---|---|---|
| 1. Owner/project binding | Exact verified principal and protected generation/mapping; no role inheritance | D01 and trusted enrollment/recovery route unqualified. |
| 2. Trusted exact receipt | Protected explicit confirmation plus authority challenge and all canonical joins | D02: trusted origin, complete display and lifecycle callbacks unqualified. |
| 3. Protected durable state | One remote transaction/evidence domain, restricted writer, deny-history retention | Store/deployment choice, effective permissions and durability not qualified. |
| 4. Replay/freshness | Authority randomness, durable consumption, incarnation/epoch and independent fence | D03: concrete independent recovery primitive unqualified. |
| 5. Atomic revoke/admit | Single serialized writer with production evidence provenance | D05 and deployment/fault qualification pending. |
| 6. Protected intent/dispatch | One-time claim, frozen payload, mediated provider route, uncertain-outcome closure | D04: every equivalent effectful route must be excluded. |
| 7. Executor exclusion | Separate Owner, authority and executor contexts; protected code/config/store | D04: no exact effective permission or hostile-executor proof. |

Reject an implementation proposal that hides any of these requirements in
executor-writable configuration, assumes native approval origin from JSON,
requires a new generic identity/approval/vault platform, treats SQLite/remote
storage as a rollback oracle, or moves a positive decision into v1 fixture code.

## 8. Required evidence before any later implementation readiness

These are exit criteria for a separately authorized next phase, not actions
executed here. Keep real admission disabled until all are satisfied.

1. Name the concrete identity issuer/client access and trusted enrollment route.
   Prove actual Owner identity, protected current session, exact Nexus mapping,
   logout/account/workspace switch and relevant role-removal invalidation.
2. Qualify N02's existing Host surface and callback transport against forged,
   automated, hidden, cleared, timed-out, substituted and stale approvals.
   Prove the Owner saw the complete exact effect bound to the same bytes.
3. Select an existing transactional store and independent recovery fence; document
   IAM/restore domains and prove durable ordering, corruption, disk-full, checkpoint
   mismatch, database rollback and whole-domain restoration behavior.
4. Approve distinct future receipt/intent/production-decision contracts while
   preserving every v1 body and fixture limitation. Define bounded formats,
   domain separation, limits, all join checks and evidence provenance explicitly.
5. Prove the executor cannot write or impersonate any authoritative surface,
   inject into Owner/Host processes, read application credentials, replace service
   dependencies, alter backups/fence, or invoke equivalent provider/target effects
   outside the gate. Include effective permissions, not configuration claims alone.
6. Qualify deterministic revoke/admit/claim race outcomes, concurrent duplicate
   confirmation, clock regression, crash at each ledger/fence/handoff interval,
   one-time dispatch, uncertain outcomes and denial on every unavailable dependency.
7. Reconfirm unchanged G1/G2/task/Host restrictions, disabled v1 public admission,
   no fixture-to-production path and minimum two-component scope. Any failed or
   unavailable mandatory proof leaves `U1_MINIMAL_IMPLEMENTATION_READY = NO`.

## 9. Documentary validation and phase disposition

This document is the only new distributable subject for this phase. The static
manifest is extended from 335 to 336 entries through an isolated source snapshot;
the prior 335 entries remain unchanged. The two preceding U1 documents and three
historical untracked Route D drafts are preserved byte-for-byte. No executable
source, contract, test, script, plugin or configuration changes are made.

Static validation covers component classifications, all seven existing contracts,
nine trust boundaries with all nine requested attributes, required decision fields,
local links, source preservation and deterministic manifest generation. This
validates documentary completeness only; it does not qualify any production trust
boundary. Ignored local validation evidence is under
`state/g3-u1-minimal-authority-20261008/`.

```text
MINIMAL_AUTHORITY_ARCHITECTURE = DEFINED
PREFERRED_AUTHORITY_OPTION = C
OWNER_BINDING_DESIGN = VERIFIED_EXTERNAL_PRINCIPAL_PLUS_AUTHORITY_OWNED_EXACT_WORKSPACE_PROJECT_BINDING
PROTECTED_STATE_DESIGN = SINGLE_REMOTE_TRANSACTIONAL_LEDGER_WITH_INDEPENDENT_RECOVERY_FENCE
ANTI_REPLAY_DESIGN = AUTHORITY_NONCE_DURABLE_CONSUMPTION_EPOCH_AND_NONROLLBACKABLE_RECOVERY_CHECKPOINT
ATOMIC_ADMISSION_DESIGN = ONE_SERIALIZED_REVOKE_ADMIT_DISPATCH_CLAIM_DOMAIN
EXECUTOR_EXCLUSION_DESIGN = DISTINCT_OWNER_AUTHORITY_AND_EXECUTOR_SECURITY_CONTEXTS_PLUS_GATE_COMPLETE_MEDIATION
NEW_TRUSTED_COMPONENT_COUNT = 2
U1_MINIMAL_IMPLEMENTATION_READY = NO
REAL_ADMISSION_IMPLEMENTED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
CREDENTIAL_ACCESS = NONE
ACCOUNT_POLICY_CHANGES = NONE
FAIL_CLOSED_BOUNDARY = PRESERVED
```
