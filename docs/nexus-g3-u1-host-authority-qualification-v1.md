# Nexus G3 U1 OpenAI Host authority qualification v1

Date: 2026-10-08. Scope: existing-facility investigation only.
Repository checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`,
branch `nexus-v2-g3-development`.
Preserved input: [U1 architecture and feasibility](nexus-g3-u1-trusted-admission-architecture-v1.md).

```text
U1_I_TRUSTED_IDENTITY = UNKNOWN
U1_X_EXECUTOR_EXCLUSION = UNKNOWN
OPENAI_HOST_AUTHORITY_REUSE = NO
U1_PHASE_2_IMPLEMENTATION_READY = NO
STOP_STATE = BLOCKED
```

No reviewed existing OpenAI/Codex/ChatGPT facility proves both the complete
Nexus Owner identity chain and executor exclusion. The requested stop condition
has been reached. Investigation ends with this report; no implementation,
custom authority design, integration prototype or live qualification follows.

`NO` means no qualified existing Host authority is established for this Nexus
use case and evidence scope. It does not assert that every private, partner-only
or future OpenAI facility is incapable of supplying one. Useful existing identity,
approval, policy and audit components remain distinct from a qualified authority.

## 1. Status interpretation and acceptance rule

Only the requested statuses are used for qualification:

- `VERIFIED`: evidence establishes the stated property at its explicitly stated
  scope. A verified documented primitive is not a verified deployed Nexus chain.
- `UNKNOWN`: the exact property is not established; absence of evidence is not
  proof of impossibility or a successful attack.
- `BLOCKED`: a required prerequisite or separately authorized access is missing.
- `NOT_SUITABLE`: the reviewed contract serves a different purpose or cannot
  supply the requirement as the authority under consideration. This does not
  reject unrelated legitimate uses of that product.

The seven numbered rows under each candidate correspond to:

| # | Required qualification question |
|---|---|
| 1 | Can the facility authenticate the actual human approval principal? |
| 2 | Can it expose a stable authenticated profile/account identity? |
| 3 | Can that identity be authoritatively bound to the exact Nexus workspace/project? |
| 4 | Can explicit approval be cryptographically or Host-authoritatively bound to the exact Nexus proposal/Subject/scope? |
| 5 | Can executor forgery, overwrite, replay, restore and bypass of that authority be excluded? |
| 6 | Is the required authoritative state outside executor-controlled writable state? |
| 7 | Can logout, account switch, workspace switch and role removal invalidate the relevant authority? |

For row 5, `VERIFIED` would mean interference is excluded, not that an attack
succeeded. Every attack class must be covered; partial filesystem isolation is
insufficient. Row 7 requires the Nexus authority consequence of all four
transitions, not merely a product's ability to log out.

U1-I requires the joint human/profile/workspace/proposal chain. U1-X requires
effective exclusion across state, ingress, writer identity, recovery and the
enforcement path. These cannot be assembled from unrelated guarantees without
evidence of a supported existing Host connection between them. A complete
authority must also expose a usable trusted decision to the Nexus boundary;
an internal feature with no established consumption/verifier contract is not
qualified by inference.

`YES` would require a qualified existing facility. `CONDITIONAL` would require
an identified supported existing authority contract with specifically bounded
qualification conditions still outstanding. Here no such complete contract is
established, so the result is `NO`, despite reusable partial facilities.

## 2. Evidence boundary and current baseline

Official OpenAI documentation was searched and opened. The investigation also
rechecked the existing 21-file CLI 0.160.1 schema snapshot and read existing G3
source. No live identity, account, connector, compliance, attestation or policy
endpoint was called. No authentication artifacts, environment credentials or
stored tokens were read. Tenant eligibility, effective deployed policies,
protected Host storage and executor impersonation resistance remain untested.

The pinned schema metadata inventory SHA-256 remains
`65a9c9c78866f00e9ada94607751fde9a482c659ee3801a3fc00f86bd82f13f8`.
This verifies the prior static export, not the active desktop protocol/version.
Existing input manifest: 334 entries, SHA-256
`019774e93df57c746c1362da2997c97347308cceb6f8d829932ed66a12f44e32`.
The uncommitted architecture input is preserved with SHA-256
`7b859255dee665b64376302e2910023fe8f45bb464335c426c61ccb69e31ed29`.

**VERIFIED local facts:** [public G3 evaluation](../ash/g3_authorization.py)
still refuses real approval origin. [The offline bridge](../ash/g3_host_approval_bridge.py)
labels all candidates `owner_authenticated=false`, `approval_authority=none`,
`dispatch_authority=none`; replay state is caller-owned. No candidate is a grant.
[Workspace allowlisting](../ash/mcp/authorization.py) establishes permitted paths,
not an authenticated human. [Existing G2 local state](../ash/managed_execution.py)
explicitly uses same-user trust and unauthenticated checksums.

The session declares `approval_policy=never` and `danger-full-access`. This is
current session configuration, not a protected Host storage audit. It supplies
no evidence of a mandatory native human approval or effective executor exclusion
for U1. No configuration change is attempted.

## 3. Candidate dispositions

The following twelve candidate families cover the relevant documented identity,
approval, custody, policy, isolation and evidence surfaces found in this bounded
survey. They are not a claim to enumerate undisclosed OpenAI internals.

| Candidate | Existing facility | U1-I | U1-X | Disposition as a complete Nexus authority |
|---|---|---|---|---|
| C01 | ChatGPT/Codex sign-in and App Server account context | UNKNOWN | UNKNOWN | UNKNOWN |
| C02 | Native human approvals, user input and MCP elicitation | UNKNOWN | UNKNOWN | UNKNOWN |
| C03 | Desktop upstream attestation | UNKNOWN | UNKNOWN | UNKNOWN |
| C04 | Sign in with ChatGPT OIDC | UNKNOWN | UNKNOWN | BLOCKED |
| C05 | Authenticated plugin profile and selected OAuth connection | UNKNOWN | UNKNOWN | NOT_SUITABLE |
| C06 | Enterprise workspace membership, roles and provisioning | UNKNOWN | UNKNOWN | UNKNOWN |
| C07 | Workspace/shared connections | NOT_SUITABLE | UNKNOWN | NOT_SUITABLE |
| C08 | Agent Security, managed requirements, sandbox rules and hooks | NOT_SUITABLE | UNKNOWN | NOT_SUITABLE |
| C09 | Work cloud coordinator and hosted executor separation | UNKNOWN | UNKNOWN | UNKNOWN |
| C10 | Platform RBAC and Responses MCP approvals | NOT_SUITABLE | UNKNOWN | NOT_SUITABLE |
| C11 | Compliance API and immutable audit stream | UNKNOWN | UNKNOWN | NOT_SUITABLE |
| C12 | Signed MCP Events delivery | NOT_SUITABLE | UNKNOWN | NOT_SUITABLE |

`NOT_SUITABLE` applies to using the named partial facility as the complete
authority. `UNKNOWN` candidates are not accepted alternatives. C04 access
verification is blocked; its published identity capability does not establish
the other missing properties even if access were available.

## 4. Seven-condition assessment of each candidate

### C01. ChatGPT/Codex sign-in and App Server account context

**VERIFIED documented facts:** ChatGPT sign-in and API-key sign-in are different
authentication paths. Managed local configuration can require a login method and
ChatGPT workspace; a mismatch logs out and exits. This constrains an OpenAI
workspace, not a Nexus project. Logout is available, but does not establish
invalidation of separate Nexus decisions. [Authentication](https://learn.chatgpt.com/docs/auth).

**VERIFIED static facts:** The inspected `GetAccountResponse` account variants
expose type or email/plan, without a returned stable human Owner/project chain.
An unused `WorkspaceRouting` definition is not that returned chain.
`previousAccountId` is a refresh-routing hint. Neither schema was invoked.
[App Server reference](https://learn.chatgpt.com/docs/app-server).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | Account authentication exists; the actual human approving this Nexus proposal is not attested by the inspected account response. API-key possession cannot establish that person. |
| 2 | UNKNOWN | The existing account metadata surface does not establish an exposed stable authenticated Owner ID for this deployment. C04 is a separate OIDC contract. |
| 3 | UNKNOWN | Forced ChatGPT workspace selection is documented; no trusted mapping to the exact Nexus workspace/project and its Owner entitlement is established. |
| 4 | NOT_SUITABLE | Sign-in or account metadata alone carries no explicit human Nexus proposal/Subject/scope approval. |
| 5 | UNKNOWN | Login/account state, transport custody, alternative clients and effective gate protection were not inspected or tested. |
| 6 | UNKNOWN | Credential persistence is not evidence of an independently protected Nexus decision authority; no required authoritative record is identified. |
| 7 | UNKNOWN | Logout and workspace restrictions exist; account/workspace switches and role removal are not proved to invalidate any previously accepted Nexus authority. |

### C02. Native human approvals, user input and MCP elicitation

**VERIFIED documented facts:** App Server requests a client decision; a resolved
notification can mean answered or cleared. Permission acceptance has native
turn/session scope. [App Server](https://learn.chatgpt.com/docs/app-server).
Human and automatic reviewers are distinct; permitted actions may require no
approval. Automatic review is not an authenticated human decision.
[Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security).

**VERIFIED static facts:** Command responses carry a decision, not an authenticated
principal. Resolution carries request/thread IDs. The reviewed guardian-denial
override accepts a serialized assessment event and thread ID, with an empty
response shape; that shape proves no Owner receipt. Phase 2B's added Nexus
proposal/Subject/scope binding is offline data supplied to the adapter.

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | A native human interaction exists; the reviewed transport does not authenticate the actual approving human to Nexus. |
| 2 | UNKNOWN | Native approval replies expose no stable authenticated human/profile identity in the inspected contract. |
| 3 | UNKNOWN | Thread/turn/item, cwd and environment IDs correlate native context; they do not establish Nexus Owner entitlement. |
| 4 | UNKNOWN | Native request correlation is established; trusted binding of the human decision to the exact Nexus material tuple is not. Adding hashes to ordinary JSON cannot supply provenance. |
| 5 | UNKNOWN | Executor access to the trusted decision channel, replay/recovery state and bypass routes is unproven. Ordinary bridge input can be fabricated; this does not prove a Host handler was compromised. |
| 6 | UNKNOWN | No protected authoritative Nexus approval state or Host-owned read/verifier interface is evidenced. Conversation or session state alone is insufficient. |
| 7 | UNKNOWN | Pending-request cleanup is known; logout/account/workspace switch and role removal effects on a Nexus authority are not established. |

### C03. Desktop upstream attestation

**VERIFIED documented fact:** `requestAttestation` opts into a desktop-supplied
opaque token for upstream attestation. [App Server](https://learn.chatgpt.com/docs/app-server).
**VERIFIED static fact:** The pinned parameters declare no proposal fields;
the response requires only an opaque token. No token was requested or read.

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | No inspected claim/verifier contract authenticates the human approval principal. |
| 2 | UNKNOWN | Stable authenticated account/profile claims are not exposed by the reviewed opaque interface. |
| 3 | UNKNOWN | No verified claim binds its identity to the exact Nexus workspace/project. |
| 4 | UNKNOWN | The upstream attestation purpose is documented; no exact Nexus human-decision/proposal/Subject/scope verifier is established. |
| 5 | UNKNOWN | Signer custody, recipient verification, replay rejection, restore resistance and effective enforcement exclusion are unproven. |
| 6 | UNKNOWN | An opaque token does not prove the location or protection of the required authoritative decision state. |
| 7 | UNKNOWN | Logout, both switches and role-removal invalidation semantics for Nexus are unspecified in the reviewed contract. |

### C04. Sign in with ChatGPT OIDC

**VERIFIED documented facts:** The website flow verifies an OpenAI ID token's
signature, issuer, audience, expiry and nonce, and uses verified `sub` with
issuer/client context as a stable external identity. Account linking and the
application session belong to the integrating application.
[Website identity flow](https://developers.openai.com/siwc/website).
The plugin variant is currently a limited trial for selected commercial partners
and separates OpenAI sign-in from connector authorization. Its identity scopes
are identity-only authorization. [Plugin sign-in flow](https://developers.openai.com/siwc/chatgpt-plugin).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | Authenticated account sign-in is documented; no available current integration or actual human principal was verified here. |
| 2 | VERIFIED | The published contract exposes a cryptographically verifiable stable external identity using `sub` plus issuer/client context. This verifies the documented capability, not a current identity or tenant entitlement. |
| 3 | UNKNOWN | No existing qualified mapping from that external identity to this Nexus Owner/workspace/project is evidenced. |
| 4 | NOT_SUITABLE | An identity-only ID token is not an explicit Nexus capability approval. Binding a login nonce does not attest acceptance of the Nexus Subject/scope. |
| 5 | UNKNOWN | The mandatory integrating application's session/mapping/verifier custody and executor exclusion are unproven. A valid token signature alone cannot exclude gate bypass or restored application state. |
| 6 | UNKNOWN | OpenAI identity issuance is external; the required Nexus authority and integrating application state are not identified as protected existing Host state. |
| 7 | UNKNOWN | Expiry/nonce validation exists; logout, both switches and role-removal invalidation of the integrating application's Nexus authority are not established. |

Availability qualification is `BLOCKED`: partner eligibility and an existing
deployed consumer were not established, and no login/token access is authorized.
Building the application's identity mapping/session would cross the user's
custom-system prohibition, so this investigation does not do so.

### C05. Authenticated plugin profile and selected OAuth connection

**VERIFIED documented facts:** A profile tool returns a stable opaque ID resolved
from the selected connection's validated credentials. The service must guarantee
its stability and scoping; schema conformance alone is insufficient. Multiple
connections may be available and the model can select one. This is connected
profile identity, not automatically the approval person's identity.
[Plugin authentication/profile contract](https://developers.openai.com/plugins/build/auth).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | NOT_SUITABLE | The profile contract identifies credentials' profile; it does not guarantee the actual human Owner who approves the Nexus proposal. |
| 2 | UNKNOWN | The stable profile interface is documented, but no existing selected service's behavioral identity guarantees were qualified or invoked. |
| 3 | UNKNOWN | No authoritative Nexus workspace/project/Owner relationship is exposed by the reviewed profile contract. |
| 4 | NOT_SUITABLE | Profile retrieval and OAuth consent are not an exact explicit Nexus capability approval receipt. |
| 5 | UNKNOWN | Service identity resolution, connection selection, authority writer/verifier custody and replay/bypass protection are untested. |
| 6 | UNKNOWN | Host credential routing does not establish the required protected Nexus approval store or enforcement state. |
| 7 | UNKNOWN | Reconnect stability is documented; logout/account/workspace switches and role removal do not have established Nexus authority invalidation semantics. |

### C06. Enterprise workspace membership, roles and provisioning

**VERIFIED documented facts:** Workspace roles control covered product features;
local permission profiles are a separate layer. Effective access requires checking
all assignments. [Roles and workspace permissions](https://learn.chatgpt.com/docs/enterprise/roles-and-workspace-permissions).
Provisioning and removal operate through workspace administration or the owning
identity provider; synchronization can restore membership if assignments remain.
Automation credentials require separate review.
[User lifecycle management](https://learn.chatgpt.com/docs/enterprise/user-lifecycle).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | Enterprise identity and membership controls exist; the actual current approver and Nexus Owner entitlement are unverified. |
| 2 | UNKNOWN | No permitted inspected interface supplies a stable authenticated human/profile context with the required Nexus decision in this deployment. |
| 3 | UNKNOWN | A ChatGPT workspace role is not an evidenced Owner mapping to the exact Nexus workspace/project. Native project sharing is also a distinct permission scope. |
| 4 | UNKNOWN | No reviewed existing role/provisioning interface produces the required material proposal approval. |
| 5 | UNKNOWN | No concrete tenant's effective management permissions, executor-accessible APIs, recovery rights or gate exclusion are qualified. |
| 6 | UNKNOWN | Workspace administration is a service facility, but no required protected Nexus authority state/consumer contract is identified. |
| 7 | UNKNOWN | Native membership removal is supported; propagation, concurrent admissions and all four Nexus invalidation transitions are unproven. Effective role semantics also need resolution below. |

**Source inconsistency:** The roles page describes ordinary permissions as
additive, with Off not removing another role's grant. The lifecycle page describes
Off overriding On. These statements do not justify choosing an effective tenant
rule without verification. This report records the discrepancy and makes no
automatic invalidation claim. No role or provisioning state was changed.
[Roles](https://learn.chatgpt.com/docs/enterprise/roles-and-workspace-permissions),
[lifecycle](https://learn.chatgpt.com/docs/enterprise/user-lifecycle).

### C07. Workspace/shared connections

**VERIFIED documented facts:** Workspace connections can use a designated account
whose permissions differ from the requesting person's. Use and management rights
are separate. Disabling a ChatGPT connection does not replace revoking provider
authorization. [Workspace connections](https://learn.chatgpt.com/docs/enterprise/shared-connections).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | NOT_SUITABLE | A shared or service-account connection cannot itself authenticate the actual human approval principal. |
| 2 | UNKNOWN | Account routing exists; no qualified stable human/profile receipt for this exact Nexus decision is exposed here. |
| 3 | UNKNOWN | Workspace availability and connection audience do not establish the Nexus Owner/project mapping. |
| 4 | NOT_SUITABLE | Designated-account access approval is not acceptance of an exact Nexus proposal/Subject/scope. |
| 5 | UNKNOWN | Actual executor use/manage rights, service APIs, connection substitution and enforcement/recovery exclusion are unproven. |
| 6 | UNKNOWN | Managed connection custody is not evidence of the required protected Nexus authority state. |
| 7 | UNKNOWN | Connection removal has its own lifecycle; logout/account/workspace switches and role removal are not proved to invalidate Nexus authority or provider access together. |

### C08. Agent Security, managed requirements, sandbox rules and hooks

**VERIFIED documented facts:** Enforced requirements differ from overridable
defaults and can constrain supported approval and permission settings. Managed
hooks can be enforced, but some callback errors/timeouts/malformed responses fail
the hook without blocking the tool.
[Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration).
Local file, native-app and browser access follow different controls; one path's
restriction does not establish all-path exclusion.
[Work local security](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-local-security).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | NOT_SUITABLE | A runtime permission policy is not an authentication facility for the actual approval person. |
| 2 | NOT_SUITABLE | A Codex permission/configuration profile is not a stable authenticated account/profile identity. |
| 3 | UNKNOWN | Filesystem/path restrictions can exist; no authenticated human-to-Nexus-Owner/project binding is established by them. |
| 4 | UNKNOWN | Rules may trigger native prompts, but exact trusted Nexus proposal/Subject/scope acceptance is not proved. Generic hook callbacks cannot be assumed fail closed. |
| 5 | UNKNOWN | No instance-specific effective policy proves exclusion across every write, replay, restore, native-app, alternate-client and gate-bypass route. Current full-access configuration supplies no such proof. |
| 6 | UNKNOWN | Managed policy distribution exists; the required authority state and protected gate/writer are not identified or audited. |
| 7 | UNKNOWN | No evidence establishes how all four identity transitions invalidate Nexus authority through this facility. |

### C09. Work cloud coordinator and hosted executor separation

**VERIFIED documented facts:** Work Cloud uses OpenAI-managed execution with
authenticated account/workspace context. A connected computer remains a separate
trust boundary; local and cloud requirements differ. Audit coverage is not
complete for every action or approval.
[Work cloud security](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security).
Agents API documents an environment key that permits environment connection
without other API actions. This is a useful documented executor separation
primitive, not a Nexus authority qualification.
[Sandbox security](https://developers.openai.com/api/docs/guides/agents-api/environments/security).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | Hosted account association is documented; the actual human approver of a Nexus decision is unverified. |
| 2 | UNKNOWN | No qualified exposed stable human/profile decision interface for this local Nexus workspace is established. |
| 3 | UNKNOWN | Hosted project/account context and connected local paths lack an evidenced exact Nexus Owner mapping. |
| 4 | UNKNOWN | No reviewed existing coordinator receipt binds explicit human approval to the Nexus material tuple. |
| 5 | UNKNOWN | Product separation is documented, but this Nexus executor's complete accessible APIs/tools, control-plane rights and bypass/restore routes are unqualified. An environment-key restriction alone is insufficient. |
| 6 | UNKNOWN | Hosted infrastructure exists outside local files; no required authoritative Nexus approval state in that protected service is identified. Sandboxed workload files remain a different state class. |
| 7 | UNKNOWN | Product access controls exist; logout, both switches and role removal are not proved to invalidate Nexus authority atomically. |

No cloud task, provider execution, environment, key or new connection was created.
Accepted G2 evidence does not qualify this new U1 property.

### C10. Platform RBAC and Responses MCP approval items

**VERIFIED documented facts:** Platform authorization combines applicable roles
and API-key permissions for API resources.
[Platform RBAC](https://developers.openai.com/api/docs/guides/rbac).
Responses MCP approval accepts a caller-submitted `mcp_approval_response` linked
to a tool-call approval request. That is an API client's decision submission,
not independently authenticated human approval.
[MCP approvals](https://developers.openai.com/api/docs/guides/tools-connectors-mcp).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | NOT_SUITABLE | API credentials/roles authenticate API access; the approval item's boolean does not identify the actual human Owner. |
| 2 | UNKNOWN | No stable authenticated approving-human/profile claim accompanies the reviewed approval item. |
| 3 | NOT_SUITABLE | Platform project authorization is a different resource domain; no native Nexus workspace/project Owner binding is established. |
| 4 | NOT_SUITABLE | Native tool-call linkage is useful, but caller approval is not a Host-attested Nexus Subject/scope human decision. |
| 5 | UNKNOWN | Where the executor is the authorized API caller it can submit a decision; an independently excluded approval caller is not evidenced. Actual credential/API rights were not accessed. |
| 6 | UNKNOWN | API-side state exists, but no required independently protected Nexus authority/writer contract is identified. |
| 7 | UNKNOWN | Native API role/key changes do not establish invalidation on ChatGPT logout/account/workspace switches or a Nexus Owner role change. |

No API request or approval item was created. An external approval intermediary
would be custom authority work and is prohibited here.

### C11. Compliance API and immutable audit stream

**VERIFIED documented facts:** The Compliance API supports an append-only audit
stream and investigative collection. Exact event schemas and coverage belong to
its Admin API reference. Supported Work events do not establish a complete record
of all approvals/actions.
[Compliance API and audit events](https://learn.chatgpt.com/docs/enterprise/compliance-api).
The linked Admin reference is outside the OpenAI Docs skill's allowed source
domains; exact protected event schemas were not fetched. No API/log access occurs.

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | UNKNOWN | No exact inspected event contract authenticates the actual Nexus approval person. Audit attribution cannot be assumed to prove explicit approval. |
| 2 | UNKNOWN | Stable authenticated principal/profile fields for the required decision were not established from the reviewed guide. |
| 3 | UNKNOWN | No exact Nexus workspace/project mapping in a supported authority event is evidenced. |
| 4 | UNKNOWN | Native event coverage and material Nexus decision binding are unverified; an audit stream is not demonstrated as a synchronous admission gate. |
| 5 | UNKNOWN | Source immutability is documented; executor access, event injection, replay/restore and gate bypass for the required decision are not qualified. Writable local exports cannot substitute for source authority. |
| 6 | UNKNOWN | Source service logging is distinct from executor files, but the required authoritative Nexus approval state has not been identified. |
| 7 | UNKNOWN | Recording an identity change does not establish timely invalidation of a Nexus authority on all four transitions. |

Disposition: `NOT_SUITABLE` as a standalone admission authority. A supported
immutable audit record could be evidence for a separately established authority;
no such authority is qualified here.

### C12. Signed MCP Events delivery

**VERIFIED documented facts:** MCP Events uses signed delivery and callback
challenge verification, with subscription lifecycle and access checks. Signatures
cover service event delivery, not a human Owner's acceptance of a Nexus proposal.
[MCP Events](https://developers.openai.com/plugins/build/mcp-events).

| # | Status | Finding for the required Nexus authority |
|---|---|---|
| 1 | NOT_SUITABLE | A service-signed event does not authenticate the actual human approval principal. |
| 2 | NOT_SUITABLE | Subscription identity is not a qualified stable authenticated Nexus Owner/profile identity. |
| 3 | UNKNOWN | Subscription arguments and audience are not an evidenced authoritative Nexus Owner/workspace/project binding. |
| 4 | NOT_SUITABLE | Cryptographic delivery integrity is a different property from explicit human approval of the exact Nexus proposal/Subject/scope. |
| 5 | UNKNOWN | The actual emitter's credential custody, executor rights, replay/restore paths and effective gate exclusion are unqualified. |
| 6 | UNKNOWN | No existing protected Nexus decision state is identified in the event service or its subscription store. |
| 7 | UNKNOWN | Subscription access/lifetime checks do not establish invalidation of Nexus authority on logout, both switches and role removal. |

No emitter, receiver, subscription, signing secret or transport adapter was made.
Repurposing this into an approval service would violate the custom-system ban.

## 5. U1-X attack coverage and composition result

The required exclusion is conjunctive. This investigation establishes no existing
facility with complete positive evidence for the following attack classes:

| Executor action | Current evidence and qualification result |
|---|---|
| Forge | VERIFIED: ordinary offline bridge observation fields are caller data, not authenticated provenance. UNKNOWN: an existing protected human-decision ingress/receipt usable by Nexus. |
| Overwrite | Executor-writable project/state files are NOT_SUITABLE as authority. UNKNOWN: effective independent Host protection for the required authority and gate. |
| Replay | VERIFIED: offline consumption depends on supplied state. UNKNOWN: existing Host consumption/freshness continuity for Nexus across sessions/restarts. |
| Restore | UNKNOWN: independent high-water mark, source recovery rights and rollback exclusion for the required Host authority. |
| Bypass | UNKNOWN: mandatory existing Host enforcement for every applicable execution path. Login, logging and policy descriptions do not demonstrate this gate. |

No live attack test was performed. These findings do not assert a Host breach,
credential leak or successful impersonation. They establish insufficient
qualification evidence and unsuitability of ordinary local copies as authority.

Combining C04 identity, C02 prompts, C06 roles, C08 policy and C11 logs does not
establish a supported existing authority. No inspected contract connects the
same authenticated human, stable profile, exact Nexus workspace/project,
material proposal and protected enforcement in one authoritative decision path.
Supplying those missing connections ourselves would create custom identity or
approval authority work, which the user expressly prohibited. Therefore no
composition prototype, new storage, signature scheme, broker or UI is proposed.

## 6. Stop checkpoint and limits of the conclusion

The best partial identity finding is C04's documented stable cryptographic
external identity. The strongest documented separation candidates are C08/C09's
managed policy and hosted execution facilities. Neither supplies a demonstrated
complete Nexus authority. C02/C03 remain unqualified possible Host seams, without
the missing human/context/verifier/custody contracts.

All candidates fail to establish the conjunction U1-I AND U1-X. The stop gate is
active immediately upon completion of this bounded survey. No real admission,
grant/revocation creation, custom-system design or implementation follows.
This report requests no credential access, login, role/policy change or new
provider run, and does not initiate another phase.

The unresolved facts could change only with evidence for an already existing
supported Host authority: its exact identity and Nexus decision contract,
independent state/enforcement custody, allowed executor interfaces and complete
invalidation semantics. None is supplied or accepted here. Public documentation
cannot prove an undisclosed facility absent, and untested account eligibility
must remain UNKNOWN rather than being invented.

## 7. Documentary verification and preservation

The only new source artifact is this report, plus its manifest entry. Isolated
source-only regeneration with the existing builder preserves all 334 input
entries and adds one entry, yielding 335. The prior architecture, all application
and test code, package guards, offline contract/evaluator and three historical
untracked Route D successor drafts remain unchanged. No commit or publication
is made.

Static validation checks all twelve candidates and their 84 criterion rows,
status vocabulary, explicit output fields, local links, whitespace, bounded
secret-pattern checks, schema inventory and prior source hashes. These are
documentary checks, not tests of real Host identity or executor exclusion.
Ignored verification receipts reside under
`state/g3-u1-host-qualification-20261008/`.

```text
U1_I_TRUSTED_IDENTITY = UNKNOWN
U1_X_EXECUTOR_EXCLUSION = UNKNOWN
OPENAI_HOST_AUTHORITY_REUSE = NO
U1_PHASE_2_IMPLEMENTATION_READY = NO
STOP_STATE = BLOCKED
REAL_ADMISSION_IMPLEMENTED = NO
GRANTS_REVOCATIONS_CREATED = 0
NEW_PROVIDER_EXECUTIONS = 0
CREDENTIAL_OPERATIONS = NONE
ACCOUNT_POLICY_CHANGES = NONE
EXISTING_FAIL_CLOSED_BOUNDARY = UNCHANGED
```
