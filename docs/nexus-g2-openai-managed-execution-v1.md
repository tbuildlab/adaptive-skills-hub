# G2-OPENAI — Managed Execution architecture v1

Architecture decision: owner-directed on 2026-10-07. Implementation baseline:
`c283e6471daacaa076cf501180d195f82494cfc7`, `nexus-v2-g2-development`.
Core Alpha 2 remains the accepted practical local execution engine. This sprint
adds an opt-in expansion layer; it does not reinterpret the Alpha 2 checkpoint.

## Current roadmap and responsibility

Core Alpha 2 → G2-OPENAI → G3 → G4 → G6; G5 remains optional.
This decision supersedes the active-path recommendations in the historical
[Roadmap V2](nexus-roadmap-v2.md), without changing its frozen record or tags.

Nexus owns task intake, planning, capability/Skill selection, policy, task-bound
Owner approval, state/checkpoint/resume, bounded retry/replan, verification and
final completion. OpenAI provides a selected managed execution substrate.
Host adapters own transport, authentication, downloads and mechanism-specific
controls. Provider availability supplies no task authority.

G3 remains **Separate Capability Authorization**: exact subject/version, scope,
expiry, revocation and task eligibility remain Nexus responsibilities. OAuth,
connections and installation may be Host/provider mechanisms. This slice binds
one reviewed artifact-handoff capability; it does not implement general G3 grants.

## Trust statement

The owner-directed architecture assumes the selected OpenAI-managed executor
enforces its documented environment properties. This is **MANAGED EXECUTION
TRUST**, not independently proven Host security. A direct adapter must identify
the actual provider environment and supported controls before dispatch.

`SELF_HOSTED_G2 = DEFERRED`; `PRODUCTION_POSITIVE_HOST_BINDING = ABSENT`.
Route D, Root R, SD01/SD05 production Host proof, G01–G06, Trusted UTC/N07,
U02-C/D2-C, PHB, historical UNKNOWN, accounting and violation records are preserved
as an optional future self-hosted high-assurance backend. None passed because of
this decision. No VM or legacy qualification action is part of this sprint.

No claim of offline operation, provider independence, hostile-cloud resistance,
infallible infrastructure/workers, or complete production security is made.

## Actual surface discovery, 2026-10-07

| Surface | Current evidence | Integration disposition |
|---|---|---|
| Responses hosted shell | [Official shell guide](https://developers.openai.com/api/docs/guides/tools-shell) documents managed containers and downloadable artifacts | Documented candidate; no authorized paid API call or repository transport adapter |
| Codex SDK | [Official SDK guide](https://learn.chatgpt.com/docs/codex-sdk) controls local threads | Local/Host candidate; SDK presence or local shell execution is not managed-cloud evidence |
| Agents API hosted browser | [Official computer-use guide](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use) documents hosted browser sessions and origin approval | Documented candidate; account eligibility and callable repository adapter unverified |
| Background/cancellation | [Responses cancellation](https://developers.openai.com/api/reference/resources/responses/methods/cancel) applies to background Responses | Future adapter-specific mapping; cancellation is not proof of external-effect reconciliation |
| Current Codex Host | Current-turn shell, browser and app tool metadata | Host-only tools; no supported arbitrary invocation from the Nexus Python CLI |
| Current connected apps | Current-turn connector metadata | Host handoff candidates; each requires its own task scope and authority |

The current Python runtime has no importable `openai` SDK. No credentials,
private app state, account entitlements or hidden configuration were inspected.
Official documentation establishes interfaces, not current account access.
Current Host thread tools are not a generic remote executor API; creating another
chat requires an explicit user request. No new thread or autonomous delegation
is used by this slice. These observations cover only the current visible subset.

## Provider-neutral contract and routing

`ExecutionBackend`, `ExecutionCapability`, `ExecutionRequest`, `ExecutionBoundary`,
`ExecutionBudget`, `ExecutionArtifact`, `ExecutionReceipt`, `ExecutionFailure` and
`ExecutionStatus` are versioned, closed, bounded data contracts. `ExecutionBackend`
is a transport protocol, not a fabricated provider API.

Local supported deterministic task → `LOCAL_CORE` using existing reviewed hooks.
Explicit coding candidate with a reviewed callable managed adapter →
`OPENAI_MANAGED`. Current coding/browser/app artifact requests → `HOST_HANDOFF`.
Unsupported category/surface → `UNSUPPORTED`. Credentials, payments, destructive
actions, account creation, deployment, elevation, irreversible effects, high cost
or unsupported authority → `OWNER_BOUNDARY`, never local fallback.

Routing accepts structured task profile facts; natural-language keywords cannot
authorize a command, select an installed provider or supply a tool handle.
The minimal CLI exposes `managed-plan`; the single-command `nexus "<task>"`
experience remains a future intake composition over existing Core and this layer.

Each request binds task/attempt identity, task text, capability subject/version,
backend, project label, exact Git baseline if present, explicit input byte hashes,
artifact expectations, output-only effect scope, provider budget declaration,
attempt/replan ceilings, expiry, approval and verification requirements. Local
paths stay in the checksum-bound local ledger. Export includes only explicitly
approved non-secret input bytes and the request. Nothing uploads automatically.

This slice supports **artifact-only exchange**. Source patch transfer can use a
returned patch artifact, but applying/reviewing/testing that patch is a separate
Core/Owner workflow. No patch is applied, repository archived, Git branch created,
or filesystem grant expanded. Before every new handoff, baseline/input drift is
checked. Hashes establish byte equality, not secret detection or provider identity.

## Lifecycle, verification and recovery

Prepare → review exact digest → export one bounded handoff → Host separately
checks authority/availability → import structured receipt and selected artifacts
→ Nexus checks bindings, declared effects, exact artifact membership/byte budget
and independently computes artifact hashes → checkpoint → completion decision.

`EXECUTION_COMPLETED` is distinct from `TASK_VERIFIED_COMPLETE`. Provider checks
are descriptive evidence and never run as commands. For the minimum slice,
completion requires **preapproved expected SHA-256 for every artifact**, plus
successful receipt binding and no warnings/ambiguity. `owner_review` expectations
remain `VERIFICATION_REQUIRED`. This verifies the specified artifact contract,
not broad code correctness or Host security. General structured-output validators
and local rerun integration are deferred; Alpha 2 already supplies local checks.

Imported artifacts are copied only into fresh task-owned output storage. Changed
files outside artifact output, missing outputs, extra effects, mismatched IDs,
unknown fields, duplicate keys, linked paths, oversized bytes and stale attempts
are refused. A checksum protects local accidental corruption, not same-user
tampering. Host reports remain unauthenticated until a future reviewed transport
binds provider provenance. Local verification cannot prove every remote effect.
Expiry uses the ordinary local clock, not trusted UTC/N07 evidence. Clock rollback
and concurrent same-user tampering are outside this source slice's trust model.

OBSERVE → CLASSIFY → RETRY/REPLAN → VERIFY retains Alpha 2's policy: at most two
attempts, a modeled one-replan ceiling, no renewed expiry, no automatic loops.
In-task replan is not implemented in this minimal slice. Only a confirmed
pre-execution provider-unavailable/transient failure is retryable in this slice.
Implementation, wrong/missing capability and verification failures require a new
reviewed plan; ambiguity never replays. Retry creates a new request/attempt digest
and requires new explicit review. Completed artifacts are not redispatched.

Export is conservatively treated as possibly in flight even though it does not
execute. Export intent is persisted before writing the handoff; a crash requires
reconciliation, never blind re-export. Resume inspects the same ledger/reference;
it does not submit a task. Late/replayed receipts cannot reopen a terminal task.

Cancellation distinguishes `CANCEL_REQUESTED`, `PROVIDER_ACKNOWLEDGED`,
`EXECUTION_STOPPED`, `RESULT_RECONCILED`. The current CLI records a request only;
it has no provider stop API. Only bound evidence may advance those later states.
Reconciled cancellation still cannot become verified completion or retry.

Provider budgeting is separate from `CoreBudget`: declared cost class, optional
declared monetary ceiling, attempt limit, and exposed usage evidence. No current
hard financial cap or live price telemetry exists. This handoff-only slice refuses
paid/high-cost dispatch; adding paid execution needs explicit Owner authority and
an adapter-specific review of whether its budget can actually be enforced.

## Architecture review and minimum implementation decision

Review before implementation: preserve Core and its MCP contracts; do not encode
SDK-local execution as cloud execution; do not equate provider success with
completion; avoid replay after uncertain export/cancel; keep all transport and
external-effect mechanisms absent until a real reviewed interface is authorized.
Implement the offline handoff contract and deterministic tests now. Demonstrate
preparation/export/status with real non-secret fixture bytes; fixture provider
receipts are tests only, never a live provider demonstration or qualification.

The provider-neutral interface allows future OpenAI managed coding/browser,
connected app, other-provider and self-hosted adapters. Direct submission,
polling, actual cancellation, in-task replan, authenticated provider references, broad local
verification, usage accounting and installed-CLI release remain integration gaps.
The sprint report records the actual checks and one final classification.
