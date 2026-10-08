# Nexus G3 U1 OpenAI/Host reuse probe v1

Inspected: 2026-10-08. Documentary and local static interface inspection only.
Architecture: [Phase 1](nexus-g3-reuse-survey-v1.md).
Foundation: [Phase 2A contracts](nexus-g3-authorization-contracts-v1.md).

## U1 requirement and evidence boundary

U1 requires an authenticated Owner decision bound to an exact immutable G3
subject, proposal and scope; protected immutable grant/revocation records;
executor write exclusion; replay/freshness controls; and serialized revocation
versus final admission. A Host prompt alone cannot satisfy all of these.

Classification concerns reuse candidates for that exact requirement. `BUILD_GAP`
means the checked mechanism does not expose the necessary Nexus contract; it
does not prove every OpenAI service lacks the feature. `UNKNOWN` means the
required guarantee cannot be established from the checked evidence. An adapter
recommendation is a proposal, not admission authority.

## Official evidence checked

| Source | Relevant evidence and limits |
|---|---|
| [Codex App Server](https://learn.chatgpt.com/docs/app-server#approvals) | JSON-RPC command/file confirmations, permission requests, MCP elicitation, connector confirmation, request resolution, turn/session scoping and status APIs. Correlation is reusable; durable Nexus authority is unestablished. |
| [App Server initialization](https://learn.chatgpt.com/docs/app-server#initialization) | Host attestation is an opaque upstream token. No documented G3 decision verification contract. |
| [Agent approvals/security](https://learn.chatgpt.com/docs/agent-approvals-security#automatic-approval-reviews) | Review may be human or automatic; an accepted event alone does not identify a human Owner. |
| [MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) | Existing OAuth, server/tool policies and connection mechanics are reusable. They do not substitute for separate subject grants. |
| [Plugin authentication/profile identity](https://developers.openai.com/plugins/build/auth#support-multiple-accounts) | Credential-resolved stable opaque profile IDs are a documented option. Available Nexus-consumer exposure and Owner/workspace binding are unverified. |
| [MCP server annotations](https://developers.openai.com/plugins/build/mcp-server#tool-annotations-and-elicitation) | Tool hints guide confirmation behavior; server authorization remains required. |
| [Plugin packaging/policy](https://developers.openai.com/plugins/build/plugins) | Installation, enablement, per-tool policy and hook review are existing Host mechanisms, separate from G3. |

All pages were opened during this phase. Sources establish interface contracts,
not observed account permissions or a tested Host decision bridge. No account,
connector, provider or OAuth operation was invoked.

## Installed interface evidence

Installed npm metadata and `codex --version`: `codex-cli 0.160.1`.
Inspected wrapper: `C:/Users/De Yong/AppData/Roaming/npm/codex.ps1`.
Inspected package: `C:/Users/De Yong/AppData/Roaming/npm/node_modules/@openai/codex/package.json`.
Native binary used for schema export:
`C:/Users/De Yong/AppData/Roaming/npm/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe`.

No-effect metadata commands: version; schema-export help; then
`app-server generate-json-schema --out state/g3-phase2a-20261008/app-server-schema`.
Export exit: 0. This generated protocol definitions; it did not start a server,
thread or turn. No account status, credential availability, login, MCP startup,
tool invocation or configuration write was performed.

Disposable definitions and `u1-static-evidence.json` are under ignored
`state/g3-phase2a-20261008/`; they are not authoritative or packaged evidence.
Inventory SHA-256 for the 21 selected schema metadata records:
`65a9c9c78866f00e9ada94607751fde9a482c659ee3801a3fc00f86bd82f13f8`.
Hashes establish the inspected schema bytes only.

| Definition checked | Observed interface |
|---|---|
| `CommandExecutionRequestApprovalParams/Response` | Thread/turn/item and start time; optional callback `approvalId`, command/cwd/actions and context; response `decision` |
| `FileChangeRequestApprovalParams/Response` | Thread/turn/item/start time, optional grant root/reason; response `decision` |
| `PermissionsRequestApprovalParams/Response` | Requested permissions with thread/turn/item/cwd and optional environment; response subset and `scope=turn/session` |
| `ToolRequestUserInputParams/Response` | Question/answer payloads, IDs, blocking flag and optional auto-resolution timeout |
| `McpServerElicitationRequestParams/Response` | Server/thread context and structured elicitation; response action/content |
| `v2/ServerRequestResolvedNotification` | `threadId`, `requestId`; resolution is not proof of acceptance or human action |
| `v2/ListMcpServerStatusResponse` | Tools, schemas, connection/auth status and presentation serverInfo; no G3 authority contract |
| `v2/GetAccountResponse` | Account union includes API-key mode, ChatGPT email/plan and Bedrock mode; no stable Owner/workspace ID in its inspected account variants |
| `ChatgptAuthTokensRefreshParams` | Nullable prior account/workspace hint for token-refresh routing, not a human decision receipt; only schema inspected |
| `v1/InitializeResponse` | User-agent, platform and Codex-home metadata; does not authenticate the Owner or canonical workspace |
| `AttestationGenerateParams/Response` | Empty input; opaque token output; no visible subject/scope/decision verifier |
| `v2/ThreadApproveGuardianDeniedActionParams/Response` | Serialized Guardian event and thread input, empty response; real human authentication and durable grant semantics unknown |
| `ClientRequest` / `ServerRequest` unions | Machine-readable method inventory; no selected G3 subject/grant/revocation/generation-store API |

The callback `approvalId` is nullable for ordinary execution and distinguishes
some subcommand/stdin callbacks. It is not a demonstrated durable grant ID.
`serverRequest/resolved` may also describe cleared requests. User-input timeout
and automatic review prevent inferring a human decision from resolution alone.
The JSON-RPC client sends the response; the schema does not constrain that sender
to a protected human UI or exclude executor access to transport/storage.

Current web documentation and the installed CLI are not identical surfaces.
The CLI lacks some currently documented account-mode fields and adds locally
defined callback fields. No assumption is made that this app uses that CLI build.
Whole provider schemas can include floats and larger graphs; their digest can be
pinned after appropriate validation, but the frozen G3 integer parser is not
weakened to import arbitrary schemas.

## Property-by-property decisions

| Property | Classification | Evidence or precise remaining condition |
|---|---|---|
| A. Human/Owner interaction | REUSE_WITH_SMALL_ADAPTER | Reuse existing confirmation UI; adapter must distinguish explicit human choice from auto-review, timeout and cleared requests. Protected origin is still conditional. |
| B. Exact proposal binding | REUSE_WITH_SMALL_ADAPTER | Reuse request/thread/turn/item correlation; normalize and present a canonical proposal digest, preserving the exact decision payload. No live binding verified. |
| C. Exact subject binding | REUSE_WITH_SMALL_ADAPTER | Bind the G3 digest to that proposal; native command/tool metadata is not an immutable implementation identity. U2/U3 prerequisites remain. |
| D. Exact scope binding | REUSE_WITH_SMALL_ADAPTER | Map the normalized G3 scope into the proposal; Host turn/session/network/filesystem scope does not directly encode G3 task/project/account scope. |
| E. Trusted Owner/profile/workspace identity | UNKNOWN | Profile identity is documented; no available nonsecret identity chain linking the human, selected Host profile and Nexus workspace was proven. Email/client name/cwd is insufficient. |
| F. Anti-replay/event identity | BUILD_GAP | Request IDs support correlation, but durable one-use consumption, session namespace and protected replay state are absent from the inspected G3 boundary. |
| G. Immutable decision evidence | BUILD_GAP | JSON events are inspectable evidence; protected immutable exact decision records/exportable G3 receipt are not established. Opaque upstream attestation is insufficient. |
| H. Durable approval storage | BUILD_GAP | Turn/session/action decisions and config policies have no demonstrated exact-subject persistent G3 grant-store contract. |
| I. Durable revocation storage | BUILD_GAP | No exact-grant revocation/order API established; disconnect or policy edit cannot stand in for immutable G3 revocation. |
| J. Executor write exclusion | UNKNOWN | Neither schemas nor docs prove that this executor cannot forge client responses or mutate authoritative evidence/store. No OS/ACL changes or hostile probe performed. |
| K. Freshness/generation/rollback | BUILD_GAP | No accepted G3 generation, rollback protection or atomic revoke/admit serialization contract is exposed by the inspected mechanisms. |
| L. Machine-readable admission interface | REUSE_WITH_SMALL_ADAPTER | JSON-RPC is reusable as input/event transport; a thin normalization interface is possible. Final protected atomic admission is conditional on E/F/G/H/I/J/K and remains disabled. |

These are property-level reuse assessments, not PASS labels for an implemented
trusted bridge. A-D and L are conditional adapter proposals. Protected admission
cannot proceed while E/J and the store/freshness boundary remain unresolved.

## Reuse and exact gap

Reuse Host authentication, credential custody, OAuth, connection lifecycle,
native UI, event transport and status/schema discovery. Retain Nexus canonical
subject comparison and pure evaluator. Do not manufacture Owner identity from
a catalog row, local writable file, `issuer=owner`, ordinary JSON response,
scanner PASS or a schema hash.

The minimum missing accepted contract is an independently trusted decision
source, binding the exact proposal/subject/scope and stable nonsecret context,
plus a durable grant/revocation authority store with executor write exclusion,
one-use event consumption, fresh generation and serialized revoke/admit ordering.
The store may be an existing protected Host/operator facility with a thin adapter;
none was demonstrated here. Same-user atomic files/locks supply mechanics only.
No new store, approval bridge or admission service was implemented in Phase 2A.

Remaining UNKNOWN: actual desktop protocol/version; human-origin evidence
available to a Nexus consumer; stable Owner/profile/workspace exposure; executor
transport and store access; attestation verification/purpose; usable protected
Host store; trusted time; live source/revision guarantees; end-to-end gate coverage.

MUST NOT build: IAM/RBAC/ABAC, OAuth/IdP, vault, CA/PKI/TPM, privileged broker,
Windows service, ACL/account redesign, VM, Root R, Route D, hardware trust root or
universal signed infrastructure. Session grants and broad remote adoption remain
deferred. U1 absence must not trigger a larger security program.

## Smallest next experiment

PROPOSAL, not started: an offline thin bridge contract test using these installed
schemas and a synthetic Host transcript, one local-adapter subject and one narrow
task scope. Display a canonical proposal digest, associate one explicit decision
with the complete request identity, and reject mismatched/duplicate/cleared/
auto-resolved events. Keep output non-authoritative. This can establish adapter
normalization behavior without credentials, effects or live App Server startup.

Before any real admission, independently obtain the existing Host/operator
boundary's identity/store/exclusion/serialization guarantees and review them
against E/F/G/H/I/J/K. If no such existing facility is exposed, present that
concrete unresolved boundary for a future Owner decision. There is no current
permission request and no dependent runtime path is started by this document.

```text
U1_OPENAI_HOST_REUSE_PROBE = COMPLETE
U1_OWNER_INTERACTION = REUSE_WITH_SMALL_ADAPTER
U1_DURABLE_AUTHORITY_STORE = BUILD_GAP
U1_EXECUTOR_EXCLUSION = UNKNOWN
U1_REAL_ADMISSION_READY = NO
REAL_OWNER_APPROVAL_ADMISSION = DISABLED_UNTIL_U1
```
