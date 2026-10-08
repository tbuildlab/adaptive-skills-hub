# Nexus G3 U1 N02 minimal confirmation architecture amendment v1

Date: 2026-10-08. Phase: architecture/specification only.
Reviewed source checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`
on `nexus-v2-g3-development`.

```text
D02_EXISTING_HOST_CONFIRMATION = BLOCKED
N02_CUSTOM_MINIMAL_SURFACE_ALLOWED = YES
D02_MINIMAL_NEXUS_CONFIRMATION_DESIGN = DEFINED
N02_MINIMAL_CONFIRMATION_DESIGN = DEFINED
N02_IDENTITY_SOURCE = D01_QUALIFIED_EXTERNAL_OIDC_ISSUER_COGNITO_CANDIDATE
N02_PRESENTATION_SOURCE = N01_FROZEN_AUTHORITY_MATERIAL
N02_DECISION_TYPES = CONFIRM_DENY_ONLY
N02_CALLBACK_DESTINATION = N01_ONLY
N02_EFFECT_RELEASE_AUTHORITY = NONE
PREFERRED_N02_DEPLOYMENT = A
NEW_TRUSTED_COMPONENT_COUNT_DELTA = 0
N02_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
```

Define N02 as one dedicated, server-rendered Owner confirmation page colocated
with N01 in the protected authority deployment. N02 displays one authority-frozen
challenge and conveys exactly one explicit CONFIRM or DENY to N01. It cannot
issue identity, grant authority or release an effect. This removes dependence on
an unqualified Codex native approval integration from the proposed D02 design.
It does not qualify a deployed confirmation surface or close other U1 blockers.

The new Owner decision permits this narrow custom surface. N01 and N02 remain
the two planned Nexus trusted components; N02's responsibility changes from Host
approval adapter to dedicated confirmation surface. The component-count delta
is zero, although the new presentation/session code is an additional trusted
responsibility within N02. No component, page, endpoint or resource is built here.

## 1. Amendment authority, exact supersession and preserved inputs

Authoritative inputs are the accepted
[minimal authority architecture](nexus-g3-u1-minimal-authority-architecture-v1.md),
[Option C deployment qualification](nexus-g3-u1-option-c-deployment-qualification-v1.md),
[D02 Host qualification](nexus-g3-u1-d02-host-confirmation-qualification-v1.md),
[authorization contracts](nexus-g3-authorization-contracts-v1.md) and
[bridge contract](nexus-g3-host-approval-bridge-contract-v1.md).
Their bytes and historical dispositions remain unchanged. This additive amendment
applies only the expressly authorized changes below.

| Prior requirement / decision | Amended requirement | Limit preserved |
|---|---|---|
| Minimal architecture R02/N02 and O04 relied on an existing protected Host surface and excluded a new UI | Permit one dedicated Nexus N02 confirmation page; replace the protected native-approval adapter role | No generic approval service, queue, delegation, workflow engine or extra broker. |
| Architecture section 5.2 and T03 required trusted Host request/gesture origin | For the new N02 path, use authenticated current Owner context, protected page/view identity, exact authority challenge and explicit decision origin | Native request IDs remain correlation data when present; they are not required human-origin proof for this new path. All binding, material, freshness and durability requirements remain. |
| Option C stack layer 2 required Codex native UI interception before release | Propose N02 colocated with N01, using existing managed external login solely for identity | The other eight stack layers and their qualification gaps remain unchanged. |
| D02 stop report found no existing qualified Host surface | Keep `D02_EXISTING_HOST_CONFIRMATION=BLOCKED`; define a separate Nexus-owned design | Do not change the original `D02_HOST_CONFIRMATION=BLOCKED` or mark D02 VERIFIED. |
| Native accept had to be held pending N01 release | The dedicated page has no native/provider execution continuation; CONFIRM only submits confirmation input | All actual effects must still be mediated by N01, including every alternative/direct route under D04. |
| Host candidate/event shapes carried offline observations only | Preserve them unchanged as optional offline correlation evidence | This page does not emit a fictitious native accept or relabel `HostDecisionEvidenceCandidate` as trusted authority. |

The new page is an alternative **authority ingress**, not another accepted v1
bridge method. A challenge/view/decision envelope and production receipt/intent
seam need separately named and versioned contracts before implementation. The
semantic requirements in this document do not amend any closed canonical body
or introduce a production-positive basis into `EligibilityDecision`.

Where an actual supported native command proposal exists, its unchanged
`HostApprovalProposal` may be referenced as frozen source evidence. A direct
Nexus proposal without that native request cannot be forced into its required
`native_request` field. The future separately versioned non-native challenge
envelope must bind the unchanged Subject/scope and exact effect evidence directly;
it may reference a genuine v1 Host proposal when applicable. Do not fabricate a
dummy command, remove native fields or emit a synthetic HostApprovalEvent for the
page decision. The future envelope encoding is a D05 review gap.

OpenAI/Codex can continue to support untrusted proposal preparation, interaction,
execution and sanitized status where already authorized. Chat text, native accept,
automatic review, thread IDs and account display metadata have no authority in
the N02 path. No new OpenAI integration or account access is performed.

## 2. Scope and smallest deployment

The preferred target remains Option C: protected remote N01, one transactional
store and an independently administered recovery fence. N02 adds a small module
and fixed template to that application, not another authority process or service.
Use the existing proposed Fargate/ALB/ACM deployment, subject to its outstanding
qualification. The executor must not execute code inside that task or share its
role, filesystem, process, sidecar or administration.

The Owner uses a separately protected browser/device context. “Separate browser
profile” on a host where the executor can read browser data, automate the page or
inject processes is insufficient. The present broad local executor has no proven
exclusion from the Owner context; it is not automatically qualified by this design.

N02 has no provider SDK usage, command executor, grant issuer, revocation API,
policy interpreter, generic form builder, account-registration UI or own database.
Use an existing maintained OIDC relying-party library and ordinary HTTP/template
framework; no particular package/version is selected or installed in this phase.
There is one code/dependency review boundary shared with N01; a renderer defect
can affect the combined service, so colocation is an explicit security tradeoff.

## 3. Minimal N02 trust contract

### P01. Owner identity

N02 consumes D01's independently verified identity. The concrete external issuer
candidate remains Amazon Cognito managed login from the Option C proposal. It is
CONDITIONAL, not an existing verified pool/client/Owner. A qualified OpenAI or
existing managed enterprise issuer may replace it only through explicit D01 review;
N02 issues no users, identities, federation assertions or OAuth grants.

N01 verifies issuer, approved client/audience, signature and algorithm, token
type, validity, OIDC transaction nonce and stable subject through the selected
issuer's documented rules. An access token and ID token have different validation
and use rules; neither becomes Nexus consent. The principal tuple is the accepted
`(issuer, client/audience, stable subject)`, not email or display name. N01 resolves
it against its current exact `(authority, workspace, project, binding generation)`
registration. No executor-provided identity header, cookie or project marker
enrolls an Owner. Unknown issuer/client, absent binding or wrong Owner denies.
The page identifies the verified current principal and exact bound project so
the Owner can detect the wrong account; display labels are explanatory only.

Candidate login is authorization code with S256 PKCE, one-time server-held state
and OIDC nonce, exact pre-registered HTTPS callback and fresh authentication per
challenge. Cognito managed login documents `prompt=login`; it is not supported
identically by classic hosted UI or all federated issuers. These are relying-party
requirements, not a custom OAuth provider.
[Cognito authorization endpoint](https://docs.aws.amazon.com/cognito/latest/developerguide/authorization-endpoint.html).

For a minimum-secret candidate, evaluate a no-client-secret registered client with
PKCE, server-held exchange state and tokens. Its exact supported mode must be
qualified in D01; do not invent a client-secret value or assume registration exists.
If the qualified client requires a secret, custody is protected authority-runtime
configuration using existing managed storage, never the browser/executor/repo.

No implicit grant, silent approval, refresh-driven long-lived Nexus session or
credential entered into Nexus is needed. External login may create its own managed
session; N02 neither controls nor treats that cookie as consent. A successful login
must return to the exact frozen page for a separate explicit decision.

Lifecycle remains a real blocker. Cognito revocation does not make an old token
fail ordinary offline signature/expiry checks; managed logout does not end every
upstream federated session.
[Token revocation](https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html),
[managed logout](https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html).
The previously proposed online `GetUser` check is a candidate current-token check,
not proof of every account switch/role removal and not atomic with dispatch.
[GetUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetUser.html).
N01 must qualify current-context loss/invalidation ordering at decision and claim;
missing lifecycle evidence blocks use. Short expiry is not a substitute for that
requirement. No identity token or credential is accessed in this phase.

### P02. Exact presentation

N01 validates/freezes the proposal, canonical Subject, exact scope and complete
target/effect evidence using the accepted rules and qualified technical sources.
It derives IDs/digests itself. Freezing an executor assertion does not prove its
effects; unresolved source/config/target-to-dispatch mappings remain inadmissible.
N02 reads a protected N01 snapshot, never executor-authored HTML/Markdown or text
used as a trusted explanation. External sources are not fetched by the page.

| Required display element | Authoritative source and presentation obligation |
|---|---|
| Authority instance | Protected authority registration, epoch and current incarnation; show the actual instance identity. |
| Workspace/project | Current registered IDs and protected human-readable context; show exact binding, not only cwd or a title. |
| Subject | Full unchanged canonical Subject material and subject ID, including source/revision/config/tool/account fields applicable to its kind. Cosmetic title is clearly secondary. |
| Requested action | Exact Subject/proposal action; show its qualified execution mapping. |
| Exact scope | Full canonical scope with every task class, operation, task ID and account constraint; no inferred future coverage. |
| Operations | Complete effect operation set, equal to scope operations under v1 rules. |
| Full target material | Complete frozen target evidence, checked against the existing `targets_sha256`; a digest or ellipsis is insufficient. |
| Effect summary | Frozen operation/target summary plus bounded reviewed human-readable explanation of the exact effect; retain original v1 `effect_summary` fields unchanged. |
| Challenge nonce | Authority-generated single-use nonce, displayed as data; not an approval credential. |
| Challenge expiry | Exact authority expiry/time basis and maximum remaining interval; browser clock never extends it. |
| Current binding generation | Protected current generation plus binding identity; a generation change retires this page's challenge. |

Also display the proposal ID and the protected presentation digest. The digest
binds all required material, full target evidence and required contextual values
in a separately reviewed presentation-envelope domain. It is not silently
substituted for the existing proposal ID/hash or Subject's domain-separated ID.
Target bytes/explanation remain outer evidence; do not add them to v1 bodies.

The protected renderer must render every material value deterministically from
that one snapshot, with strict HTML escaping and bounded lists/strings. No raw HTML,
executable markup, remote images, third-party scripts, iframes, automatic links
that fetch targets, progressive hidden fields or material edited in the browser.
Ordinary scrolling/wrapping is permitted; material truncation or unsupported
encoding/layout denies presentation instead of hiding effects. The minimum uses
no client JavaScript and no SPA. Fixed local styling is part of protected code.

A server-issued view identity binds session/context, challenge, proposal digest,
presentation digest and template/deployment revision. This supports later
render-to-decision matching; it does not cryptographically prove a human read
every pixel. Qualification must demonstrate complete correct rendering and a
protected actual Owner interaction path. Hashes alone do not provide that proof.
Changing any material value requires retiring the old challenge and a new display
and decision; no in-place rescoping or reuse of an old view is permitted.

### P03. Explicit decision and minimum UI behavior

The decision alphabet is exactly **CONFIRM** and **DENY**, case-sensitive. Other
values are rejected; missing decision, default option or merely visiting the page
never confirms. The two controls are “Confirm this exact proposal” and “Deny”.
Neither is preselected or automatically submitted. An informational sentence
states that confirmation authorizes N01 to evaluate this one challenge and starts
no execution. Enter/focus behavior must not accidentally activate confirmation.

No session consent, automatic review, remember-choice setting, policy amendment,
broad future consent, delegation, background approval or provider continuation.
N02 cannot interpret a login result, chat reply, native accept, submitter claim
or prior screenshot as CONFIRM. It must not report “execution approved” on submit.

The trusted human-origin claim is conditional on D01 authentication and the
protected Owner-controlled browser interaction, including exclusion of executor
automation/injection and session theft. A POST with a genuine session authenticates
that context; it is not a hardware-attested proof of a physical click. The design
does not claim nonrepudiation or infer human origin from HTTP shape alone.

### P04. Protected callback and proposed interface semantics

The minimum has one protected HTTPS origin, one challenge-page route, one decision
POST route, external-login start/callback handling and session termination. These
are conceptual endpoints, not implemented APIs or approved production schemas.
Infrastructure liveness routes, if necessary, contain no authority or material.
There is no public decision API accepting an executor's identity assertion.

| Exchange | Required semantic content / authority |
|---|---|
| Untrusted executor to N01 | Submit an untrusted proposal; obtain at most a locator and permitted status. The locator is not an approval capability or token. |
| N01 to N02 presentation | Authority-frozen bytes, current challenge/Owner-binding context, nonce/expiry, presentation digest and protected view identity. No executor rendering input. |
| Owner browser to N02 decision | Closed future request containing challenge locator, view identity, nonce, proposal/presentation digests, CONFIRM or DENY and per-view CSRF proof. Treat all submitted fields as untrusted until compared with server state. |
| N02 to N01 | In-process typed call in preferred A, carrying the verified session/context reference and decision plus all frozen joins. N01 derives Owner/project from protected state; caller text cannot override them. |
| N01 to browser | Same-page accepted/pending/denied/expired/unknown status, according to actual durable state. No bearer grant, reusable receipt token, provider dispatch token or direct callback to executor. |
| N01 to executor status | Sanitized non-authoritative outcome/reference only under existing permitted readback; no Owner cookie, CSRF proof, identity token or confirmation credential. |

Decision binds the exact authority instance/epoch/incarnation, nonce/challenge,
verified Owner and context generation, workspace/project/binding generation,
unchanged proposal/Subject/scope identities, full effect/presentation digest and
protected view identity. N01 verifies all joins on delivery. The browser may send
IDs for comparison but is never their authoritative writer.

For A there is no separate N02-to-N01 network service credential or external
decision callback. The Owner POST handler and typed handoff reside in the protected
application; executor handlers cannot construct an authenticated Owner-context
object from request fields or invoke the decision path with executor credentials.
Network reachability of a public endpoint is allowed; authenticated decision
acceptance must be excluded. A rejected unauthenticated request creates no authority.

Use HTTPS, exact fixed Host/origin/redirect configuration, trusted ingress only,
server-side session lookup and a per-view synchronizer CSRF proof. Require exact
Origin on decision POST, rejecting absent/null/mismatched Origin; this deliberately
rejects unsupported clients. Origin can be forged by a non-browser client and is
not identity proof. Cookie authentication and CSRF/view/nonce checks remain mandatory.
No wildcard CORS, JSONP, method override or state-changing GET. Proxy identity and
forwarded headers are trusted only after the ingress strips/replaces client values.
[OWASP CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

Use an opaque unpredictable `__Host-` Owner session cookie with Secure, HttpOnly,
Path=/, no Domain and explicit SameSite=Strict. Keep identity tokens and session
meaning server-side; no localStorage, browser JWT grant or signed client-side
authority session. OIDC's top-level GET return may need a separate short-lived
SameSite=Lax pre-authentication cookie, bound to one state/PKCE transaction. That
cookie confers no Owner/decision authority, is consumed on return and replaced
with a new Owner session ID; do not weaken the decision cookie for login convenience.
[OWASP session guidance](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).

Response policy includes no-store, no referrer propagation, no MIME sniffing,
fixed restricted CSP with scripts disabled and form submission confined to the
authority origin, `frame-ancestors 'none'` and X-Frame-Options DENY as applicable.
External login is top-level navigation, not an embedded frame. Frame protections
do not prove human intent or prevent every deceptive top-level interaction.
[OWASP clickjacking guidance](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html).
No decision/nonce/CSRF/token material in URLs, analytics or logs. A public locator
has no bearer power and must not bypass authenticated material-access checks.
Enforce bounded request bodies and session/view cardinality; malformed, oversized
or quota-exhausted input denies without echoing identity or secret values.

### P05. Gate separation and ordering

CONFIRM creates only a **candidate trusted confirmation input** at N01 ingress.
It is not an `ApprovalGrant`, positive `EligibilityDecision`, native approval reply
or dispatch. “Trusted” is conditional on the entire identity/session/presentation/
exclusion boundary; N01 still validates it independently. The unchanged offline
Host candidate is a different non-authoritative record.

Required later authority ordering, preserving the accepted architecture:

1. N01 validates/freezes exact material, resolves Owner binding and creates the
   challenge. N02 authenticates and presents it, without effects.
2. On decision, N01 serializes the current identity/context/binding check with
   challenge expiry, view/material joins and one-use transition. Receipt/evidence,
   challenge consumption and any later separately authorized grant provenance are
   recorded together under the accepted transaction rules.
3. Complete the independent fence/durability protocol before acknowledging positive
   authority. Prepared or ambiguous writes do not confer authority; quarantine
   uncertainty. N02 never supplies a fence-completed boolean.
4. Separately evaluate current technical/task/Host/G1/G2 facts, binding, context,
   expiry and revocation through the future reviewed production decision seam.
   Serialize revoke/admit and intent creation inside N01; the page cannot request
   broader scope or bypass these checks.
5. Recheck and atomically claim one exact dispatch intent. Complete durable claim
   and recovery fence before the protected N01 adapter starts the effect. A revoke
   ordered before claim prevents it; a receipt alone does not defeat revocation.

N02 has no “run now” route, provider authentication or native request to unblock.
The architecture can therefore separate gesture capture from effects without a
native pre-response interception hook. This is a proposed separation, not proven
enforcement. D04 must exclude all executor/direct execution equivalents; an
unmediated provider route keeps real admission closed.

DENY atomically retires the challenge and records exact denial evidence, never a
new v1 `Revocation` or wildcard policy. It cannot cancel an already-claimed unrelated
attempt or revoke a previous grant. Browser cancellation/closure is no decision;
authority expiry and trusted context loss independently retire pending work.
Acknowledgment loss yields unknown status, not new confirmation or a replacement
execution. Retain the accepted `NO_AUTOMATIC_REDISPATCH` behavior for ambiguous
effect handoffs; external exactly-once execution is not claimed.

### P06. Replay, expiry, session and recovery semantics

N01 generates at least 256 random nonce bits through the existing platform CSPRNG;
enforce uniqueness in protected challenge state. Challenge lifetime is at most
five minutes, never longer than verified context/binding validity. Owner session
and view are scoped to this one challenge and expire no later; no refresh or
silent extension. Login must finish within the original challenge deadline or
the challenge is retired. Authority time/monotonic elapsed time govern expiry;
clock regression/uncertainty closes use.

| State/event | Required result |
|---|---|
| Pending, current view, valid CONFIRM | N01 may validate one candidate, then follow its protected transaction/fence/gate rules. No effect starts from POST. |
| Pending, current view, valid DENY | Record denial/consumption through N01; no grant, revocation or future choice. |
| Missing/wrong session, CSRF, view, nonce, digest, Owner or binding | Reject; do not consume another person's pending challenge or fabricate authenticated denial. |
| Repeated identical POST/callback | Return bounded already-recorded/pending/unknown status only to the current authorized Owner; no new receipt, nonce use or intent. |
| Conflicting CONFIRM/DENY or concurrent tabs | First valid serialized terminal transition wins; no reversal/merge. Replacement views retire former view IDs; one active view/challenge per Owner/project in the minimum. |
| Expiry, logout, account/profile/project switch, Owner/binding change | Retire affected pending challenge/context before any later confirmation or claim; no silent rebinding. |
| Browser back/refresh/cached page or copied request | Revalidate protected live state; stale views cannot acquire authority or extend expiry. |
| N01/N02 restart, recovery or unqualified transport/session loss | Retire pending contexts/views and unclaimed intents; preserve durable consumption/denial/revocation history. Apply accepted retirement of pre-restart grants. |
| Unknown transaction/fence acknowledgment | Quarantine; no success acknowledgment or release; replay does not repair authority by resubmission. |

Use a bounded ephemeral server session/view map in the one protected process, not
Redis or another session database. It stores only short-lived login state, PKCE,
tokens and context references needed for this one interaction; discard after
termination/expiry/restart. Durable challenge/decision/consumption/generation and
evidence belong to N01's existing planned store/fence, not N02 storage.
No restored session map or browser cookie recreates authority. Memory loss is
safe denial; backup contains no reusable N02 identity/session material.
After a terminal decision, close further browser decision use. Any identity/context
material needed for N01's later claim validation may remain only in protected
memory until the original context deadline, with no refresh or extension. Losing
that material or reaching the deadline blocks the claim; receipt durability does
not preserve a live identity session.

The context validity check must also occur before later dispatch claim, not merely
at POST. An accepted decision can outlive its page without granting a reusable
session; current identity/context loss must still block the intent. Browser closure
and external logout are not automatically observable. A shorter deadline, fresh
login or `GetUser` cannot alone prove all invalidation semantics; D01/D04 must
qualify those semantics before implementation readiness.

### P07. Executor exclusion

The executor can prepare untrusted proposals, read allowed sanitized status and
report faults. It has no privilege to create the authenticated decision context,
alter authoritative material or release effects. Requirements apply to direct
and indirect access, including restore/backup and deployment tooling.

| Surface executor must not control | Exact exclusion requirement |
|---|---|
| Owner browser/session | Separate protected Owner context outside executor OS/admin/profile/process/UI-automation access; no cookie storage, input injection, extension/debug endpoint, screen overlay or remote-control capability. A same-host profile is insufficient without equivalent proven isolation. |
| N02 deployment/config | No image/template/dependency/origin/OIDC-client modification, deploy role, `iam:PassRole`, task execution, shell/debug attach, DNS/TLS changes, policy override or rollback to retired deployment. |
| Callback endpoint | Cannot authenticate as Owner, forge trusted context objects, replace the handler/route/proxy, bypass checks through internal/admin routes or inject a decision into N01. Public HTTPS reachability alone provides no rights. |
| Identity tokens | No ID/access/refresh token, PKCE verifier, login-state cookie, Owner session ID or auth secret read/injection; no issuer/client administration or token minting. |
| N02 application credentials | No task-role/conditional OIDC secret, memory, environment, secret mount, logs, dump, backup or recovery access. A separate executor must not share a Fargate task/sidecar role. |
| Rendered authoritative material | No authoritative snapshot/template/CSS replacement, active external content, effect text override, cache substitution or same-origin script injection. Untrusted input is escaped and independently mapped to frozen qualified material. |
| Challenge state | No nonce/expiry/consumption/context/generation store writes, maintenance access, restore/reset, replay-set omission or activation of retired challenge/view state. |

The Owner can authenticate, inspect and decide on one bound challenge; this does
not confer deployment/issuer/store administrator powers. Separate trusted admins
enroll/rebind, deploy protected code and recover into quarantine under the accepted
design; these operations do not impersonate an Owner confirmation. No new general
role hierarchy or administrative UI is proposed.

Fargate task isolation/roles are candidate managed primitives, not proof of Owner
browser isolation or of the deployed permissions. Code inside a task can access
that task's credentials, so N01/N02 must never share the task with executor code.
[ECS task roles](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html).
Actual identities, policies, endpoint paths, devices and effective denials remain
UNKNOWN. If any exclusion cannot be established, the confirmation input remains
untrusted and implementation/admission remain blocked.

### P08. Minimum UI and trusted code inventory

One fixed confirmation page displays one exact challenge and two decision actions.
Same-page status is sufficient; no history dashboard, approval queue, team workflow,
delegation, generic policy, multi-application service or decision editor. External
managed login and necessary session termination are authentication plumbing, not
extra Nexus approval screens. No new visual mockup or runnable web page is created.

| Component | Classification | Amendment |
|---|---|---|
| Existing G3 canonical records/parsers | REUSE | Unchanged exact bodies, IDs and denial behavior. |
| Managed D01 issuer/login + maintained OIDC library | REUSE | Candidate relying-party consumption only; no identity issuance or custom OAuth. |
| N01 authority core, store/fence and dispatch | NEW_MINIMAL, already planned | Retain responsibility for every authoritative state transition and effect. |
| N02 fixed page, ephemeral session/view handling and decision ingress | NEW_MINIMAL, replaces planned N02 adapter | Exactly one authority function; no separate store, broker, provider execution or general form schema engine. |
| Existing TLS/runtime/deployment/backup primitives | REUSE | Conditional previously proposed stack; protect new routes/template/session too. |
| Custom PKI, receipt signer, generic vault/IAM/workflow/approval platform | NOT_NEEDED | No transferable signed receipt or new cryptographic identity system. |
| Qualified identity/lifecycle, effective exclusion, recovery fence and production seam | BLOCKED or CONDITIONAL as previously recorded | Required qualification and versioned contract review remain; no deployment proof from this document. |

Planned new Nexus trusted components remain **2**. `DELTA=0` counts logical new
components relative to the accepted architecture, not lines of code or the total
managed infrastructure/browser/issuer trusted computing base. N02 gains trusted
web/session handling code; the count must not conceal its review burden.

### P09. Deployment comparison

| Option | Small concrete candidate | Code/secrets/session burden | Exclusion, audit and recovery | Disposition |
|---|---|---|---|---|
| A | Fixed server-rendered N02 module in the proposed N01 Fargate task; one authority HTTPS origin through existing ALB/ACM | One image/relying-party library/template; no separate N02 service credential, SPA tokens, state replication or session store. Opaque bounded ephemeral sessions. | Executor excluded from combined task; one audited N01 decision transition. Restart retires views/sessions. Web-code compromise can affect N01; protect and review the shared boundary. Owner browser exclusion remains independent. | Preferred CONDITIONAL design. Minimum added deployment trust for the already selected N01 stack. |
| B | Protected S3/CloudFront static assets plus N01 backend | Additional origin/bucket/CDN policy and cache invalidation; client rendering/version binding. SPA token handling or another backend session facade increases custody/code burden. | Static content can be protected administratively but must be joined to the exact N01 snapshot; stale caches, frontend rollback, cross-origin auth and direct origin routes need qualification. | Not selected. No strict scope/exclusion advantage for one fixed page; do not introduce an extra backend facade. |
| C | Lambda-rendered page through a managed HTTPS ingress plus existing N01 backend | Existing managed runtime, but separate role/deployment/callback authentication and session continuity; a cold start must not silently lose/recreate usable context. | Qualify every ingress and the serverless-to-N01 handoff. Public HTTPS alone is not Owner auth. Direct function URL/alternate routes cannot bypass checks. Ephemeral loss closes the challenge. | Conditional alternative, not smaller than A with N01 already on Fargate. |
| D | Same-process page with different packaging or local executor-host browser/service | Same-process remote packaging is A; shared local executor context exposes session/deployment and may add OS isolation/recovery work. | No strictly simpler independent custody/complete mediation demonstrated. | NONE selected; shared executor-context shortcut NOT_SUITABLE. |

Managed primitives do not supply Nexus semantics automatically. CloudFront origin
access control can restrict access to S3 origins, but does not bind a rendered page
to an Owner challenge.
[CloudFront origin protection](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html).
Lambda function URL auth has AWS_IAM/NONE modes; neither by itself is this browser
Owner confirmation contract.
[Lambda function URL authentication](https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html).

A is preferred because it uses the existing candidate runtime/transport/store and
avoids a second session/callback/deployment domain. It is not chosen merely for
coding ease or claimed to have the strongest possible compartmentalization.
If qualified protection of the combined application cannot be demonstrated,
revisit B/C explicitly; do not add runtime services as an unreviewed fallback.
The prior ALB-to-task trusted private-hop assumption remains conditional; this
amendment does not claim end-to-end TLS, create custom PKI or weaken ingress trust.

### P10. D02 reclassification and readiness

| Property/blocker | Status after this amendment | Required closure |
|---|---|---|
| Existing Host D02 | BLOCKED | Historical native UI/callback/release gaps remain; no new Host qualification. |
| Minimal Nexus D02 design | DEFINED | Specification covers identity, display, decisions, callback, separation, replay, exclusion and deployment; not VERIFIED. |
| D01 identity/access/lifecycle | CONDITIONAL candidate, actual capability UNKNOWN | Concrete available issuer/client/principal/binding and current invalidation semantics must be qualified. |
| D03 independent fence | CONDITIONAL candidate, actual capability UNKNOWN | Actual independent durable checkpoint/recovery permissions and ordering must be qualified. |
| D04 exclusion/mediation | BLOCKED | Protected Owner browser plus combined N01/N02 code/session/ingress and every direct effect route must be evidenced. |
| D05 production decision seam | BLOCKED | Review separate challenge/view/decision/receipt/intent/production-decision contracts without changing v1 bodies. |
| N02 implementation readiness | NO | The above trust/contract dependencies remain unqualified; this phase authorizes no implementation. |
| U1 implementation candidate readiness | NO | A defined N02 resolves a design dependency but does not qualify the complete authority chain. |

The architecture's ban on custom confirmation UI is explicitly narrowed by this
Owner instruction. Its mandatory identity/exclusion/freshness/serialization gates
are retained. No source or runtime feature flag is changed, and no readiness
field from an earlier accepted artifact is retroactively edited.

## 4. Trust-boundary register

All locations and roles below are requirements for a future qualified deployment,
not resources created here. Each boundary preserves the accepted nine attributes.

| Attribute | B01: issuer/Owner context to N01/N02 | B02: frozen material to page/view | B03: explicit decision to N01 |
|---|---|---|---|
| Authoritative writer | External issuer authenticates; N01 verifies and binds current context | N01 freezes qualified material; protected N02 template renders it | Current bound Owner through protected N02; N01 validates/records |
| Authoritative reader | N01 validators; N02 via protected references | N02 and authenticated exact Owner | N01 only; scoped status readback |
| Executor permissions | No session/token/browser/auth/admin access | Untrusted proposals only; no render or snapshot override | No authenticated decision submission or context construction |
| Persistence location | Issuer plus N01 binding/context evidence; short-lived tokens in protected memory | N01 store/fence; ephemeral view map and uncached Owner page | N01 transaction domain/fence, no N02 database |
| Recovery semantics | Fresh current authentication; no restored session activation | Retire pending views/challenges after restart/recovery | Preserve terminal consumption; ambiguous commit quarantines |
| Replay semantics | One-time login state/PKCE/nonce; current context generation | Exact challenge/nonce/epoch/digest/view match | Atomic one-use outcome; duplicate never creates second receipt |
| Revocation semantics | Logout/switch/removal closes current context before later claim | Binding/context change retires display | Challenge DENY retires it; grant revocation remains separate N01 ordering |
| Failure mode | Wrong/stale identity or incomplete loss detection | Missing/changed/truncated/active content or template mismatch | Forgery, stale view, CSRF, duplicate conflict, store/fence ambiguity |
| Fail-closed behavior | No display authority/confirmation/claim | No confirmation control for invalid material | Reject or quarantine; no grant/effect from callback |

| Attribute | B04: protected deployment/administration | B05: durable authority to dispatch gate |
|---|---|---|
| Authoritative writer | Separate trusted deployment/recovery administrators | N01 alone, serialized with revoke/admit and claim |
| Authoritative reader | N01 verifies fixed deployment registration; independent qualification audit | N01 protected adapter and permitted scoped audit |
| Executor permissions | No image/config/role/debug/session-store/DNS/TLS/backup/restore write or read of secrets | No credentials, store/fence mutation, cached positive decision or equivalent privileged route |
| Persistence location | Existing protected runtime/config; authority registration and independent recovery custody | N01 store plus independent fence, retained intent/attempt history |
| Recovery semantics | Retired code/context cannot reopen old authority; restore into quarantine | Retire pending/unclaimed authority; reconcile ambiguous existing attempt only |
| Replay semantics | Protected revision/epoch/incarnation; no executor-controlled rollback | Exactly one durable claim; NO_AUTOMATIC_REDISPATCH |
| Revocation semantics | Deployment/context changes close affected authority and require requalification | Revoke before claim blocks it; later revoke prevents subsequent claims, not undoing completed effects |
| Failure mode | Shared executor task/browser, policy bypass, leaked credentials or unsafe restored deployment | Fence/state mismatch, missing scope enforcement, direct route or uncertain handoff |
| Fail-closed behavior | Keep N02 input untrusted and admission denied | No release until every gate completes; ambiguous attempt remains consumed |

N02 adds no recovery or enrollment administration page. It records no own grant,
revocation or policy state. These belong to N01 and its separately protected
administration under the accepted architecture.

## 5. Required later evidence, not actions authorized now

Before implementation readiness, separately review the future bounded envelope
schemas and acceptance semantics for this non-native authority path. In particular,
decide the presentation/target evidence encoding and digest domain, protected
context/view interfaces, DENY/duplicate acknowledgments and ledger/fence transitions.
Do not issue synthetic grants or attach new bases to the old evaluator to test it.

Later qualification must demonstrate: wrong issuer/Owner/project denial; correct
full rendering of all eleven elements; tamper/CSRF/cross-origin/framing rejection;
executor denial of all seven excluded surfaces; actual explicit Owner operation
with no automatic/session consent; double-submit/conflicting-tab/late/cached-view
rejection; restart, context switch, binding/role removal and recovery retirement;
durable receipt/consumption/fence failure closure; and no effect at CONFIRM before
serialized current intent claim. Existing public v1 denial must remain intact.

These are future evidence obligations only. This phase runs no browser page,
login, diagnostic, account call, provider, container, AWS operation or implementation
test. The present document and hashes cannot prove human intent, lifecycle coverage,
protected rendering or actual executor exclusion. Missing proof keeps readiness NO.

## 6. Documentary validation and final fields

This phase adds this document and its distributable manifest entry. Local ignored
evidence is under `state/g3-u1-n02-amendment-20261008/`. Static checks cover the ten
properties, eleven display elements, seven exclusion surfaces, four deployment
options, boundary attributes, required final fields and local links. All eight
prior accepted/historical untracked documents, every prior manifest subject,
tracked source/code/contracts and 21 pinned schema files remain byte-preserved.

The unchanged manifest builder runs twice over a clean isolated snapshot of the
prior 338 subjects plus this document: 339 deterministic entries, with all prior
338 entries unchanged. Existing source/package guards are preserved. This checks
documentary consistency and source equality, not deployed security. No full runtime
test suite or production authority test is claimed.

The seven existing G3 authorization/bridge record types remain unchanged. Public
valid-input evaluation still rejects with `G3_APPROVAL_ORIGIN_UNVERIFIED`; the
offline candidate remains `OFFLINE_CONTRACT_ONLY`, `owner_authenticated=false`
with no approval/dispatch authority. No grants, revocations, sessions, challenges,
receipts, intents or authority credentials are instantiated by this phase.

```text
D02_EXISTING_HOST_CONFIRMATION = BLOCKED
N02_CUSTOM_MINIMAL_SURFACE_ALLOWED = YES
D02_MINIMAL_NEXUS_CONFIRMATION_DESIGN = DEFINED
N02_MINIMAL_CONFIRMATION_DESIGN = DEFINED
N02_IDENTITY_SOURCE = D01_QUALIFIED_EXTERNAL_OIDC_ISSUER_COGNITO_CANDIDATE
N02_PRESENTATION_SOURCE = N01_FROZEN_AUTHORITY_MATERIAL
N02_DECISION_TYPES = CONFIRM_DENY_ONLY
N02_CALLBACK_DESTINATION = N01_ONLY
N02_EFFECT_RELEASE_AUTHORITY = NONE
PREFERRED_N02_DEPLOYMENT = A
NEW_TRUSTED_COMPONENT_COUNT_DELTA = 0
N02_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
N01_N02_IMPLEMENTED = NO
LIVE_DIAGNOSTICS_PERFORMED = 0
CREDENTIAL_ACCESS = NONE
ACCOUNT_POLICY_CHANGES = NONE
```
