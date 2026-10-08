# Nexus G3 U1 D01 identity and lifecycle qualification v1

Date: 2026-10-08. Scope: documentary qualification only.
Source checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`,
branch `nexus-v2-g3-development`.

```text
D01_IDENTITY = BLOCKED
SELECTED_IDENTITY_ISSUER = AMAZON_COGNITO_MANAGED_LOGIN_OIDC_CANDIDATE_ONLY
OWNER_PRINCIPAL_MODEL = EXACT_ISSUER_CLIENT_ID_SUB
OWNER_ENROLLMENT_MODEL = PREAUTHORIZED_ADMIN_NOMINATION_PLUS_FRESH_OWNER_CONFIRMATION_CONDITIONAL
CURRENT_CONTEXT_VALIDATION = BLOCKED_MISSING_ORDERED_LIFECYCLE_PROOF
LOGOUT_INVALIDATION = LOCAL_RETIRE_DEFINED_EXTERNAL_LIFECYCLE_BLOCKED
TOKEN_REVOCATION_HANDLING = ONLINE_GETUSER_PLUS_ADMIN_STATUS_CONDITIONAL
OWNER_BINDING_INVALIDATION = PROTECTED_GENERATIONS_AND_FENCED_RETIREMENT_DEFINED
ACCOUNT_SWITCH_HANDLING = LOCAL_SWITCH_RETIRE_DEFINED_EXTERNAL_SWITCH_BLOCKED
ROLE_LIFECYCLE_DEPENDENCY = NONE_FOR_OWNER_AUTHORITY_ADMIN_EXCLUSION_REQUIRES_D04
EXECUTOR_IDENTITY_EXCLUSION_DEPENDENCY = BLOCKED_PENDING_D04_BROWSER_TOKEN_CALLBACK_ISSUER_ADMIN_EXCLUSION
LIVE_QUALIFICATION_REQUIRED = YES
LIVE_QUALIFICATION_DEFINED = YES
D01_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
```

Amazon Cognito is a documented identity/login candidate. It is **not a qualified
complete current-context authority** for this Nexus design. Required issuer
logout/account-switch observation and its ordering with the protected claim have
not been established. Token checks, a recent authentication and short deadlines
cannot fill that gap. Overall D01 is BLOCKED; the primitive remains reusable.
This refines the earlier Option C CONDITIONAL assessment without changing that
historical document or any accepted contract.

## 1. Authoritative inputs, evidence rules and scope

The design inputs are the accepted
[minimal authority architecture](nexus-g3-u1-minimal-authority-architecture-v1.md),
[Option C deployment qualification](nexus-g3-u1-option-c-deployment-qualification-v1.md),
[N02 amendment](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md),
[D05 contracts](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[G3 v1 contracts](nexus-g3-authorization-contracts-v1.md),
[bridge contract](nexus-g3-host-approval-bridge-contract-v1.md) and
[fail-closed source](../ash/g3_authorization.py). They remain unchanged.

Qualification uses public official AWS/OpenAI documentation, relevant standards
and local static inspection. No issuer discovery request to a customer resource,
cloud console, account API, login UI, token endpoint, credential store, app-server
or provider has been used. Documentation URLs are sources, not tested deployments.
Resource names below are symbolic requirements, not existing registrations.

| Classification | Meaning in this phase |
|---|---|
| VERIFIED_CANDIDATE | A documented primitive fits its stated limited role; no actual deployment or human/session has been verified. |
| CONDITIONAL | A concrete composition is specified but access, configuration, enrollment, integration or operational behavior still needs qualification. |
| UNKNOWN | Evidence does not establish the property; no claim that the feature is impossible or absent. |
| BLOCKED | A mandatory qualification dependency is missing; dependent positive authority cannot proceed. |
| NOT_SUITABLE | The exact reviewed mode fails the required role. |

Actual pool/client IDs, issuer mode, HTTPS hostname/callback, Owner principal,
administrator identities, permissions, MFA configuration and deployed lifecycle
integration are **UNKNOWN**. No principal is enrolled by this document.

The minimum candidate uses **Cognito local users only**, one separately registered
public/no-client-secret app client, managed login branding, code plus S256 PKCE,
protected server-held transactions/tokens and an exact N01/N02 HTTPS callback.
Federation, identity pools, silent authentication, implicit flow, M2M identity,
refresh-driven Nexus sessions and external group/workspace role authorization are
outside this candidate. Excluding federation does not solve Cognito-only logout
or browser/profile-switch observation.

## 2. Qualification register: all twelve requirements

Statuses assess each complete requirement, not just whether a named API exists.

| ID | Requirement | Classification | Documented/design basis | Verified deployment and remaining gap |
|---|---|---|---|---|
| R01 | VERIFIED PRINCIPAL | VERIFIED_CANDIDATE | Exact issuer/client/sub is supported by signed ID/access tokens; email/name excluded. | UNKNOWN actual Owner, pool and client; authentication identifies an account, not physical human presence or control of a protected browser. |
| R02 | LOGIN TRANSACTION | CONDITIONAL | Code, S256, returned state/nonce, HTTPS registration and managed-login fresh-authentication mode; server relying-party design below. | UNKNOWN configuration, callback, state consumption, authentication/MFA behavior and token custody. |
| R03 | OWNER ENROLLMENT | CONDITIONAL | Existing protected administrator nomination plus fresh verified Owner binding confirmation; no executor TOFU. | No qualified bootstrap administrator/root, named resources or actual ceremony; enrollment cannot run. |
| R04 | CURRENT CONTEXT | BLOCKED | Local generations plus online token/user/config checks proposed at all five stages. | No complete external session/logout/switch proof or ordered validity through claim/handoff. |
| R05 | LOGOUT | BLOCKED | Local retirement is defined; issuer cookie logout and token revocation have distinct effects. | No qualified issuer-only logout notification or current issuer-browser session proof. |
| R06 | TOKEN REVOCATION / ACCOUNT DISABLE | CONDITIONAL | Online GetUser plus protected user-status/config reads; revoked-token rejection documented. | No live rejection/propagation/race evidence; no atomicity with external issuer administration. |
| R07 | OWNER / BINDING CHANGE | CONDITIONAL | N01 serialized generation change, tombstones and D03 fencing already required by D05. | Protected enrollment writer, D03 persistence and D04 administration exclusion not deployed/qualified. |
| R08 | ACCOUNT / PROFILE SWITCH | BLOCKED | Nexus-observed switch retires first; new tuple must match current enrollment. | Switch solely in issuer, native Host or another browser profile is not proven observable or prevented. |
| R09 | ROLE / ENTITLEMENT CHANGE | VERIFIED_CANDIDATE | External groups/roles/workspace memberships excluded from Owner authority; exact Nexus mapping is the sole authorization binding. | This exclusion is a design choice, not role-removal detection. D04 still governs administrator privilege lifecycle. |
| R10 | FAIL-CLOSED LIFECYCLE | BLOCKED | Missing/stale/unordered proof always denies; TTL is only an upper bound. | Accepted complete lifecycle premise is unsatisfied, so no D01 PASS can be released. |
| R11 | EXECUTOR EXCLUSION DEPENDENCY | BLOCKED | Issuer assertion validation is separable from browser/runtime/callback/admin protection. | No qualified D04 boundary for the current executor; a separate browser profile alone is insufficient. |
| R12 | LIVE QUALIFICATION PLAN | CONDITIONAL | Small isolated no-admission diagnostic defined in Section 10. | Future execution requires separate authorization and a protected prepared environment; no tests run. |

### 2.1 Existing OpenAI identity reuse alternative

Current official documentation describes a website OIDC code/PKCE integration,
server verification and the issuer/client/sub account mapping. Website identity
access is a limited trial for selected commercial partners; Nexus entitlement
and an issued identity client are UNKNOWN. Identity sign-in supplies an external
account; the application owns its session and authorization.
[OpenAI website identity](https://developers.openai.com/siwc/website).

The quickstart distinguishes identity-only integration from optional plan usage.
Broad open-source plan availability does not establish entitlement for this remote
identity-only N02 integration. No inference scopes or execution are needed here.
[OpenAI quickstart](https://developers.openai.com/siwc/quickstart).

Open-source account/session documentation defines application account selection,
separate client/token registrations and renewable-session revocation. It does not
establish an ordered Nexus callback for every ChatGPT logout or Host profile
change. Reusing stored executor-side credentials would violate the proposed D04
boundary. A ChatGPT workspace is not an exact Nexus project binding.
[OpenAI accounts and sessions](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions).

| Alternative | Status | Disposition |
|---|---|---|
| OpenAI website identity primitive | CONDITIONAL; deployment/access UNKNOWN | Supported integration is documented; reconsider only with an approved identity client and qualified lifecycle/exclusion. |
| OpenAI as complete D01 current-context source | BLOCKED | Required ordered lifecycle evidence not established. No undocumented introspection, logout webhook, role signal or signed Nexus approval assumed. |
| Open-source inference registration/token sharing as this remote N02 authority | NOT_SUITABLE in the reviewed mode | Different deployment/purpose; no automatic identity-only remote eligibility, Owner binding or executor exclusion. |
| Codex account labels, thread/workspace metadata, native accept or chat | NOT_SUITABLE | Auxiliary interaction/context; cannot replace verified principal or current protected session. |

These observations do not reopen D02 native approval qualification or modify its
BLOCKED conclusion. No OpenAI client is requested or account inspected.

## 3. Verified principal and supported login transaction

### 3.1 Exact principal model

Use unchanged D05 `Principal={issuer,client_id,subject}`. For this candidate,
`subject` is the exact verified ID-token `sub`; `client_id` is the fixed enrolled
app client, compared with ID-token `aud`. Issuer is the exact registered pool
issuer URI, not the login domain or an executor-supplied discovery URL.
Cognito documents `sub` as its preferred identifier, ID-token audience/token use
and authentication time; `sub` must not be constrained to an assumed UUID format.
[Cognito ID token](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html).

Access-token validation is separate: require `token_use=access`, the enrolled
`client_id`, same issuer/sub and required scope. Its resource `aud`, if present,
does not replace the client identity. Tokens with M2M meaning cannot establish a
human Owner. [Cognito access token](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html).

Discovery/JWKS and issuer mode are protected registration inputs. AWS documents
both original and updated issuer URI forms; do not accept both by prefix, or
silently migrate a tuple when issuer mode changes. Keep the exact approved issuer
and endpoint allowlist. [Cognito issuer endpoints](https://docs.aws.amazon.com/cognito/latest/developerguide/federation-endpoints.html).

Proposed N01 acceptance: verify signature with pinned issuer JWKS and approved
algorithm, token use, issuer, exact single client audience, nonempty bounded sub,
nonce, issue/expiry/authentication time and callback transaction. Reject wrong
token type, multi-audience ambiguity, unknown key after bounded authorized JWKS
refresh, malformed claims and any tuple mismatch. Signature verification is a
documented primitive; current lifecycle is a separate check.
[AWS JWT verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html).

Account identity does not prove that the physical Owner is presently operating
the browser. That assertion also requires the qualified N02 interaction and D04
isolation. No `email`, `email_verified`, display name, username, login hint,
Cognito group or AWS role claim enrolls or replaces an Owner. Treat exact strings
as identifiers; no case folding, email alias linking or name-based recovery.
[OIDC claim stability](https://openid.net/specs/openid-connect-core-1_0.html#ClaimStability).

### 3.2 Login capability evidence

AWS documents authorization code, pre-registered HTTPS callbacks, returned state,
nonce in the ID token and only S256 for PKCE. `prompt=login` requests reauthentication
in **managed login**, not classic hosted UI; it does not invalidate an older session.
`prompt=select_account` has no effect for local sign-in. These are candidate
capabilities, not verified behavior for a resource.
[Authorization endpoint](https://docs.aws.amazon.com/cognito/latest/developerguide/authorization-endpoint.html).

PKCE compares the original challenge to the verifier at code redemption.
[Cognito PKCE](https://docs.aws.amazon.com/cognito/latest/developerguide/using-pkce-in-authorization-code.html).
The token endpoint supports server HTTPS POST and a public client without a secret,
using its client ID; code exchange returns identity/access/refresh tokens.
[Token endpoint](https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html).

The following are proposed relying-party constraints, not a new OAuth provider
or changes to D05. They must be verified in a later diagnostic:

1. N01 begins a transaction tied to the exact pending challenge, protected browser
   transaction, authority instance/epoch/incarnation and current binding generation.
   Generate independent login state, OIDC nonce and PKCE verifier with at least
   256 bits of entropy. They are distinct from the authority approval nonce.
2. S256 uses unpadded base64url SHA-256 of a standard-conforming verifier. Retain
   verifier only server-side. Require code flow, `prompt=login`, exact configured
   redirect and explicit minimum `openid aws.cognito.signin.user.admin` scopes.
   Use local sign-in only; no implicit, silent or refreshed login substitute.
   [PKCE standard](https://www.rfc-editor.org/info/rfc7636/).
3. Register one exact production HTTPS callback origin/path for this client and
   environment. Reject arbitrary return URLs, wildcard/loopback/custom-scheme
   callbacks, untrusted forwarded-host changes and executor-selected issuers.
   Actual callback value remains UNKNOWN; no sample URL is a registration.
4. Store the transaction in protected ephemeral N01 memory, single-use and no
   later than the five-minute challenge deadline. A short `Secure`, `HttpOnly`,
   host-only, `SameSite=Lax` transaction cookie permits the top-level external
   callback. It conveys a random transaction locator, never a token/verifier.
   Consume state atomically before exchange; loss/restart/duplicate callback denies.
5. N01 exchanges the code directly over authenticated HTTPS. Browser/executor
   receives neither ID/access/refresh tokens nor token endpoint credentials.
   Verify returned ID and access tokens separately and their issuer/sub/client join.
6. Proposed fresh-authentication check: required integer NumericDate `auth_time`
   must match this transaction's time window, with at most five seconds clock
   tolerance and at most sixty seconds age at callback acceptance. `iat` or a
   freshly refreshed token is insufficient. Missing/stale authentication time
   denies. This bound is a diagnostic target, not a demonstrated issuer SLA.
   MFA settings alone do not prove MFA was performed in this authentication.
7. Convert validated integer issuer seconds to D05 Unix milliseconds using checked
   arithmetic. Do not copy seconds into `_ms`, normalize principal strings or
   alter D05's canonical bounds/time representation. Unrepresentable values deny.
8. After successful validation, rotate the protected Nexus context/session,
   consume the login transaction and remove its cookie. The confirmation session
   uses the N02 protected cookie/CSRF requirements; no OAuth state substitutes for
   decision POST CSRF. Return to full frozen display for separate CONFIRM/DENY.
9. Retain necessary tokens only in protected ephemeral runtime custody for the
   bounded context. No token cache in repo, browser storage, executor, evidence,
   logs, URL parameters or restored backup. No refresh-based positive renewal;
   retain a refresh token only if needed for separately authorized end-session
   revocation, then destroy it. Restart requires fresh authentication.

OAuth state/nonce checks prevent transaction confusion; they do not continuously
observe issuer cookies, prove human presence or close the claim-time lifecycle
gap. The selected no-client-secret mode minimizes secrets without weakening D04
token/verifier/callback protection. A deployment needing a confidential client
must be separately requalified; no secret is invented or retrieved here.

## 4. Owner enrollment and exact Nexus binding

No executor TOFU enrollment. The first successful login, matching email, AWS
account administrator status or copied workspace marker cannot create ownership.
Use the architecture's **existing independently authenticated administrator plus
Owner ceremony** route; the concrete administrative primitive candidate is an
existing AWS IAM Identity Center human administrator session, not Cognito Owner
groups. Identity Center supplies managed workforce access; actual tenant,
administrator and privileges remain UNKNOWN.
[IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html).

Proposed ceremony, only after separate authorization and root qualification:

1. Separately trusted deployment and recovery administrators establish the exact
   authority instance, fixed issuer/client, registration resource and independent
   recovery root using their existing protected administration. Executor nominates
   none of these. The initial administrator identity must have been authenticated
   independently of this enrollment request; a new browser claiming admin is not
   the bootstrap root.
2. Administrator preauthorizes one candidate principal using identity obtained
   from a verified protected issuer transaction. Nomination by name/email is not
   final principal verification. No Cognito account creation is part of Nexus.
3. The same principal freshly authenticates through the selected relying-party
   path and explicitly confirms the exact authority/workspace/project binding
   through a protected ceremony. Administrative approval and Owner participation
   remain separate from capability consent; this creates no approval grant.
4. N01 compares the approved nomination, actual tuple and independent root,
   and records the existing D05 Binding/control state: Owner principal,
   owner_generation, workspace_id, project_id, binding_id and binding_generation,
   under the current Stamp. First generations start at one under the qualified
   genesis; replacements strictly advance. Registry resolves a protected project
   and execution environment, not labels or a filesystem marker alone.
5. Publication requires the existing N01 ledger/D03 checkpoint protocol. Recovery
   administrator verifies custody/readback. No binding becomes current from a
   partially committed nomination or historical table copy.

This specifies an enrollment route, not a new account-registration UI, generic
approval service, enrollment schema or implementation. An actual named existing
administrator/root and Owner-confirmation channel must be qualified; until then,
there is no usable enrollment. Reuse D05's seven records and protected control
state; do not append fields to Principal, Binding or receipts.

Owner may authenticate/inspect/confirm the exact binding and later qualified
proposal. Owner login confers no direct table, fence, issuer-admin or deployment
write privileges. Administrators may perform only separately authorized
configuration/enrollment/recovery; administrator login is not Owner consent.
Executor can submit untrusted proposals and read permitted sanitized status only.

## 5. Current context at every required stage

Candidate evidence has three distinct layers:

- **Identity**: verified original transaction and exact issuer/client/sub.
- **Nexus state**: live protected session, context/binding generations, pending
  current view, epoch/incarnation and independently witnessed state.
- **External lifecycle**: current token/user/config observation plus qualified
  issuer/browser/Host logout/switch/loss evidence, with supported ordering to use.

The third layer is incomplete. None of the checks below may currently produce
D05 `D01_IDENTITY_CONTEXT=PASS`.

`GetUser` uses the user's access token and the `aws.cognito.signin.user.admin`
scope; IAM credentials do not authorize it. It returns user attributes, not a
browser-session or human-presence attestation.
[GetUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetUser.html).
`AdminGetUser` is IAM-authorized and exposes Enabled/status/user attributes.
Compare returned sub with the enrolled Owner; a returned username is a lookup
key, not replacement identity. [AdminGetUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminGetUser.html).

Proposed current token/user/config bundle: revalidate the held tokens, query
GetUser with the exact access token, require its exact sub, obtain protected
AdminGetUser Enabled/acceptable local-user status and registered-client configuration
readback. No cached positive bundle authorizes a later stage. These online reads
must use fixed resources and protected custody. The client-description API and
client-type schema expose supported configuration; they do not attest a browser
session or create a linearizable Nexus transaction.
[DescribeUserPoolClient](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeUserPoolClient.html),
[UserPoolClientType](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_UserPoolClientType.html).

| Required stage | Protected checks and exact joins | Current qualification |
|---|---|---|
| page creation | Fresh callback accepted; exact Owner binding, active context, pending unexpired challenge, current epoch/fence; candidate online bundle; full protected display and view registration. | BLOCKED: external current-session/loss proof and D04 absent. |
| decision POST | Same active context/cookie and generation, exact current view/nonce/presentation, explicit CONFIRM/DENY, Origin/CSRF and protected ingress; repeat lifecycle/token/user checks. | BLOCKED: a legitimate cookie/POST is insufficient without full lifecycle proof. |
| receipt creation | Under N01 serialization recheck current Owner/binding/context and challenge/view expiry; atomically consume nonce and retain evidence; wait for D03 durability. | BLOCKED: no authoritative lifecycle observation ordered through acceptance. |
| AdmissionIntent creation | Fresh D01 observation plus current binding/context and all D05 eight gates; exact trusted receipt/grant lineage, current revocation and fence; combined evaluation/intent transaction. | BLOCKED: old receipt and recorded PASS cannot supply missing D01 evidence. |
| DispatchAttempt claim | Fresh complete D01 observation, exact current context/material and all other gates under claim serialization; recheck after fence delay and before bounded adapter handoff. | BLOCKED: external reads are not atomic with Cognito logout/switch/disable; no supported ordering premise. |

Hold N01's local generation/revoke/admit serialization through the accepted
bounded handoff, giving priority to locally pending invalidations. This prevents
known Nexus changes from racing a claim. It **does not lock Cognito, its browser
cookie, an upstream issuer or an administrator**. Successful GetUser/AdminGetUser
followed by logout/disable and then claim is an unresolved external race.

An issuer-supplied documented current-session mechanism with complete relevant
event coverage and a qualified ordering/validity model would be required to close
that race. No such Cognito-to-Nexus mechanism is established by this review.
An event arriving later, issuer expiry or a timestamped snapshot is not a lease.
Without evidence that remains valid for the required use, refuse positive authority.

D05 identity_evidence/session_evidence and GateFact.source_evidence remain exact
references to retained protected observations. This document does not define an
eighth record, add token/jti fields to D05 bodies or turn parsed issuer booleans
into authority. Details live in qualified source evidence/protected state only.

## 6. Logout, token revocation and account state

### 6.1 Logout effects and proposed Nexus disposition

AWS describes `/logout` as interactive managed-session sign-out/redirection and
documents its failure to log out external OIDC/social providers; SAML SLO is a
separate configured mechanism. [Cognito logout](https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html).
GlobalSignOut invalidates user token use in Cognito but does not clear the managed
login cookie; clearing that cookie requires the browser logout route.
[GlobalSignOut](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GlobalSignOut.html).

| Event / route | What Nexus may establish | Required disposition / gap |
|---|---|---|
| Local Nexus session termination | A valid protected request reaches N01 and serializes retirement of the exact context. | RETIRE before acknowledging local termination; retire dependent view/challenge/grant/intent, preserve consumed attempts. Cookie deletion alone is insufficient. |
| N01-led Cognito sign-out | N01 first retires its context, then may use separately authorized issuer revocation/logout operations. | Local closure does not wait for issuer availability. Record remote failure as UNKNOWN; never report universal issuer logout success from local cookie removal. |
| Cognito `/logout` without N01 involvement | Browser managed-login session ends; no validated Nexus invalidation is implied. | BLOCKED: no established authoritative ordered notification to N01. A logout redirect or unauthenticated callback is not complete session-loss proof. |
| Cognito GlobalSignOut / AdminUserGlobalSignOut | Revokes the targeted user's issuer token families; candidate online rejection can detect their invalid use. | CONDITIONAL detection; no automatic browser-cookie clearance or atomic Nexus ordering. |
| Issuer logout in another tab/device/client | May affect an issuer session/token family different from the held N01 context. | Scope/correlation UNKNOWN; deny if required loss coverage cannot be proven. |
| Upstream federated logout | Not used in the selected local-only candidate. | NOT_SUITABLE as an assumed propagated mechanism. Adding federation requires separate upstream freshness/logout/switch qualification. |
| Browser close, crash, offline, profile replacement | No authenticated logout receipt follows merely from silence. | No positive continuation on a missing heartbeat, browser request or expired timeout. Required loss observation remains BLOCKED; close authority use. |

Do not assume JWT expiry equals logout. Managed-session cookie, JWT family and
Nexus context are separate state. Browser redirects/JavaScript notifications are
not authenticated completeness guarantees. Refusing silent reauthentication
helps new transactions but cannot retroactively observe an older context's loss.

### 6.2 Revoked token and account checks

AWS documents that revoked JWTs can still pass ordinary offline signature/expiry
checks. Revocation-aware Cognito APIs reject revoked token use. Refresh-family
revocation does not necessarily cover the user's other token families; global
sign-out has a broader scope. `origin_jti`/jti identifies records, not proof of
current validity. [Cognito revocation](https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html).

AdminDisableUser deactivates the profile and revokes access tokens; AdminDeleteUser
deletes the profile. Candidate live checks must confirm the exact resulting
token/user lookup behavior rather than infer it from an offline claim.
[AdminDisableUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminDisableUser.html),
[AdminDeleteUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminDeleteUser.html).

| Condition | Candidate detection | Failure/recovery semantics |
|---|---|---|
| Revoked held access-token family | Online issuer token-authenticated GetUser rejection, not AdminGetUser Enabled alone. | RETIRE authentic affected context; no refresh rescue, another family's token or old successful response. |
| Disabled/deleted user | Online token check plus protected exact user-status lookup. | Disabled/missing/nonacceptable user denies; reenable or same email on a new account does not revive old context/binding. |
| Client deleted/changed or policy relaxed | Fixed client metadata readback against approved protected revision; unknown/different client/audience rejects. | Retire dependent context; reconfiguration/requalification required. Returned token fields alone do not prove current client policy. |
| Issuer/pool/domain migration | Exact registered issuer/endpoints and protected configuration match; no arbitrary discovery. | Different issuer changes the principal tuple; retire first, explicit reenrollment; no matching-sub migration. |
| Password/MFA change, reported compromise or stale session | Qualified issuer observation or protected local invalidation; fresh login is only one check. | Unknown effect/event coverage denies. MFA settings or recent auth_time alone cannot establish absence of compromise. |
| API outage/throttling/permission loss/unexpected response | Missing current authoritative observation. | DENY, not last-known-good. Local retirement persists; uncertain durable state QUARANTINE. |

Each query observes a service response at one time. Propagation, deletion/recreation
and cross-operation consistency for this exact composition remain UNKNOWN. Tests
may identify counterexamples; repeated success cannot establish a stronger vendor
ordering guarantee than documented. No token introspection endpoint is assumed.

### 6.3 Audit/event alternatives do not close the lifecycle gap

Cognito documents CloudTrail API and managed-login events, including a Logout
entry in the hosted-UI event list. This does not establish complete managed-login
browser/session correlation or guaranteed delivery before Nexus claim.
[Cognito CloudTrail](https://docs.aws.amazon.com/cognito/latest/developerguide/logging-using-cloudtrail.html).
CloudTrail delivery is asynchronous and its typical delivery time is not a
guarantee. [CloudTrail delivery](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html).
CloudTrail/EventBridge/polling is NOT_SUITABLE as the sole current-context fence;
no new audit pipeline is proposed. Logs may assist later investigation only.

OIDC defines explicit session-management and back-channel logout mechanisms;
being an OIDC issuer does not imply these optional integration capabilities or
an atomic validity lease with Nexus. They are a qualification checklist, not a
Cognito feature claim. [OIDC session management](https://openid.net/specs/openid-connect-session-1_0.html),
[OIDC back-channel logout](https://openid.net/specs/openid-connect-backchannel-1_0.html).

## 7. Owner/binding change, account switch and roles

N01's existing protected registration is the authoritative writer of Nexus
Owner/binding/context generations; qualified issuer evidence is the identity
input. The executor has no writer permission. Owner replacement, unbind/rebind,
project/environment switch, issuer/client change or new authority epoch/incarnation
must retire dependent authority before the replacement becomes current.

Proposed transition: close the old context/binding under N01 serialization,
retain retirement/consumption/revocation history, strictly advance applicable
owner/binding/context generations and independently checkpoint it. Require new
qualified enrollment/authentication, challenge, display and explicit decision.
No old receipt/grant/intent is rebound. Unknown fence completion closes use;
recovery compares the latest independent history, never an older matching table.
Authority restart retires all pre-restart positive use, as D05 requires.

Before claim, invalidation denies/retire-checks the intent. After a durable claim,
retain the consumed attempt and block new claims; do not promise to undo an effect
already handed off. NO_AUTOMATIC_REDISPATCH. Claim/fence uncertainty is QUARANTINE,
external outcome uncertainty UNKNOWN with no replacement dispatch.

| Switch boundary | Handling | Qualification |
|---|---|---|
| Nexus-observed sign-in as another principal | Retire the old context before accepting the new transaction; exact tuple mismatch denies; no auto-enrollment. | CONDITIONAL on protected callback/state/generations. |
| Nexus workspace/project switch | Close current view/challenge/context; resolve new exact protected binding and freshly authenticate. | CONDITIONAL on N01/D03/D04. |
| Cognito sign-in/account switch outside Nexus | Held old token may still identify the enrolled Owner; token checks do not attest the active browser account. | BLOCKED absent qualified observation/prevention. |
| Browser profile switch, copied session cookie or device switch | No cross-profile adoption; restored/copied sessions cannot prove current protected context. | BLOCKED pending D04 isolation and a lifecycle source; no claim that profiles are intrinsically isolated from the executor. |
| Codex/ChatGPT account or workspace switch | Does not replace the Cognito principal. If that Host context participates in proposal/execution restrictions, its loss is a separate current HOST/G2 fact. | UNKNOWN source, BLOCKED dependent use; exclude identity inference from Host labels. |

External Cognito groups, SAML/OIDC roles, AWS identity-pool roles and OpenAI
workspace memberships are **not relied on for Nexus Owner authority**. No group
claim grants or revokes ownership. Removal from an unrelated external group is
not asserted to be an Owner invalidation event; exact Nexus unbinding/replacement
is the authoritative authorization change. This explicitly excludes a dependency,
not a claim that external role-removal lifecycle has been solved.

Existing administrator/deployment/recovery privileges remain D04 dependencies:
loss/replacement of trusted administrators must close affected configuration
authority and require requalification. Issuer-admin control can reset/link/change
accounts or clients; allowing an executor that control defeats the identity chain.
AWS group/role authority is never silently promoted to Nexus consent.

## 8. Trust boundaries, permissions, persistence and failure

| Boundary | Authoritative writer / reader | Executor permissions | Owner/admin permissions and location |
|---|---|---|---|
| Cognito issuer to N01 relying party | Cognito signs identity; protected N01 validates it. | Public metadata and untrusted locator only; no token/verifier/callback/admin access. | Owner authenticates with issuer UI; separately trusted issuer administrator controls fixed pool/client; issuer state in managed service. |
| Owner browser to N02 | Authenticated protected ingress contributes interaction; N01 records current context and qualified receipt evidence. | No browser data/process injection, UI automation, cookie read, protected POST impersonation or callback routing. | Owner sees frozen page and explicit decision; runtime session/transaction/tokens ephemeral outside executor; raw secrets never ledger evidence. |
| Enrollment/configuration to N01 registry | Qualified existing admin/Owner ceremony, enforced by N01 and D03. | No nomination-as-authority, root/mapping/code/config update or role assumption. | Admin uses existing managed human administration; Owner participates; exact registration/control generations in protected authority store. |
| N01 to token/user/config APIs | Trusted issuer service response observed by protected N01. | No held user token or N01 role; no arbitrary subject/resource proxy. | N01 candidate role has fixed-resource read-only AdminGetUser/client-description permissions; user-token GetUser separately authorizes itself. No runtime create/update/disable/delete/sign-out admin permissions implied. |
| N01 state to recovery and claim | N01 serializer/checkpoints; separately administered D03 custody; protected adapter reads current claim. | Sanitized status only; no store/fence/restore/deployment/dispatch bypass. | Owner receives no direct writes; recovery administrator independently authenticates and restores only to quarantine. |

Recovery: do not restore raw token/session/transaction memory. Fresh login and
current independently fenced binding are required; incomplete history QUARANTINE.
Replay: single-use login transaction plus separate one-use challenge nonce,
current view/generations and D05 durable consumption; matching bytes are references.
Revocation: local retirement precedes acknowledgment, current token/status evidence
is required at each use, and known invalidations precede claim. External ordering
and coverage remain BLOCKED. Failure: untrusted/missing/stale joins DENY; authentic
lost context RETIRE; uncertain durable history QUARANTINE; unknown API/effect outcome
UNKNOWN and no positive fallback. No TTL becomes a substitute lifecycle source.

D01 can independently specify and documentary-verify issuer protocol, exact
principal comparison, login freshness/replay checks and external token-state
query candidates. It cannot independently prove secure human operation, exclusive
token custody, callback/network integrity, protected dependencies/registration,
issuer-admin exclusion or inability to bypass N01. Those require D04 with D03
and N02 qualification. The current broad local executor is not a qualified
Owner context and must not be used for a real sign-in diagnostic.

### 8.1 Required credentials/secrets, identified but not accessed

| Material | Candidate custody / necessity |
|---|---|
| Owner password/passkey/MFA/recovery factors | Existing Cognito/Owner interaction only; never Nexus/executor custody. Concrete factor policy UNKNOWN. |
| Client ID, pool/issuer/endpoints, callback and public JWKS | Configuration/public metadata, not credentials; protected exact registration required. No actual values obtained. |
| PKCE verifier, login/CSRF/session values, authorization code | Protected transient N01/browser transaction as appropriate; code only to fixed callback and backend exchange; never logs/evidence. |
| ID/access/refresh tokens | Protected ephemeral N01 only; no refresh to extend positive context; no backup restore or token forwarding. |
| App client secret | NOT_REQUIRED for selected public PKCE candidate. A later confidential mode adds protected managed custody and must be requalified. |
| N01 IAM workload identity | Existing managed role mechanism for restricted reads/state; no static AWS key or executor role reuse. Effective permissions UNKNOWN. |
| Existing administrator/recovery login | Protected existing managed human session, separately authorized operations; not an implicit runtime or Owner privilege. |
| TLS keys | Existing ACM/ALB candidate custody; no custom PKI or local key access proposed. |

No resources, permissions, accounts, credentials or secrets are created/read/changed
by this phase. No generic credential proxy, vault, IAM or approval platform is added.

## 9. Fail-closed stop findings

Short TTL only limits exposure; it is not proof of logout, role/context loss or
account switch. Fresh authentication per challenge is necessary but cannot prove
the same context remains live at later decision/claim. An online token check is
stronger than offline verification for token revocation but not a complete session
or ordering guarantee.

The stop follows these concrete gaps:

1. **External loss coverage:** no qualified Cognito-only logout/account/profile/Host
   switch signal establishes current context and retires it before a later claim.
2. **External ordering:** no issuer validity lease or supported synchronization
   joins those changes to N01 acceptance/claim/bounded handoff.
3. **Bootstrap authority:** existing concrete administrator/root, exact pool/client,
   resource registration and Owner enrollment are unverified.
4. **Protected observation:** D04 browser/session/token/callback/issuer-admin
   exclusion and D03 recovery custody remain unqualified.

Do not solve these by assuming polling completeness, implementing a custom
identity/lifecycle broker, narrowing accepted invalidation semantics, redefining
OwnerContext or enabling the seam with UNKNOWN evidence. Requalification or a
separately authorized architecture amendment would be needed for a different
lifecycle model. No such amendment is made here.

## 10. Smallest safe future live qualification plan

LIVE_QUALIFICATION_REQUIRED = YES means the documented candidate's configuration,
fresh-authentication behavior, token rejection and isolation will need actual
testing **if a suitable lifecycle path and protected environment are identified**.
LIVE_QUALIFICATION_DEFINED = YES describes this bounded plan, not permission to
run it. Static evidence already suffices to withhold readiness. Live tests alone
cannot repair missing supported lifecycle/ordering semantics.

Use one already prepared isolated test pool/client with two synthetic local users
(candidate Owner A and non-Owner B), one registered HTTPS callback and an existing
protected test browser/device. No production users, resources or data. This phase
does not prepare the environment. If no such environment exists, stop; provisioning
requires a separate task and authorization, not fallback to real accounts.

Future diagnostic must be an isolated relying-party probe with **no N01/N02
production implementation**, authority store, real binding activation, grant,
revocation record, intent, dispatch adapter, provider credential or execution path.
It can verify a proposed principal/binding in test memory and return non-authorizing
PASS/FAIL/UNKNOWN observations. No D05 production records are created. Issuer token
revocation/user disable/delete are account-state mutations and require explicit
future authorization; distinguish them from forbidden G3 grant/revocation issuance.

Run protocol/control inspection first; then bounded login tests; then separately
authorized lifecycle mutation tests with an independent protected test administrator.
Stop on the first mandatory failure and retain sanitized evidence. Never attempt
to simulate a real dispatch to qualify D01. A model of ordering is only documentary
evidence; integrated D03/D04/N01 race qualification remains a later phase.

| Case | Future bounded observation | Expected acceptance/stop criterion |
|---|---|---|
| L01 | Inspect approved issuer/client/callback/managed-login mode/local-only configuration through protected test administration. | Exact configuration and effective exclusion match; unknown/mismatch stops before login. |
| L02 | A signs in with code/S256/state/nonce and fresh authentication. | Correct tuple, actual fresh auth_time, no secret/token leakage; login alone never approves. |
| L03 | B signs in; use same display labels/email if permitted by prepared test configuration without modifying it. | Exact sub comparison rejects non-Owner; display metadata irrelevant. |
| L04 | Wrong/missing/replayed state, wrong nonce or verifier in a controlled test callback. | Reject with no context; consume transaction at most once; no retry that reopens it. |
| L05 | Unregistered callback, wrong issuer/client/audience/type or altered token. | Reject, no discovery/token request to attacker-chosen endpoints. |
| L06 | Existing managed-login cookie with fresh-auth request; attempt classic or silent mode. | Fresh evidence must be present; unsupported mode rejected, not assumed fresh. |
| L07 | Token/code/session leakage review of browser, transport, logs and diagnostic outputs. | No exposed token/verifier; failure stops qualification. |
| L08 | Local test-session termination at each of the five modeled use stages. | Old context/view becomes unconditionally unusable before local acknowledgment; no production receipt/claim made. |
| L09 | Direct issuer `/logout`, bypassing local test-session termination. | Demonstrate supported correlated loss observation before later modeled use; absence confirms BLOCKED, not TTL success. |
| L10 | Separately authorized test refresh-family revocation; compare offline validation and GetUser. | Old family rejected online; offline signature alone never accepted. |
| L11 | Separately authorized GlobalSignOut; inspect remaining managed-login session behavior. | Do not equate token invalidation with cookie clearance; close local use regardless. |
| L12 | Separately authorized disable of A; later reenable, if explicitly allowed. | Online/status checks deny disabled user; old context cannot return merely on reenable. |
| L13 | Separately authorized deletion of disposable B, with no recreated production identity. | Missing-user handling denies; no email/username identity adoption. |
| L14 | Account switch within test relying party and separately at issuer. | Local switch retires; external switch must be supported/observed or remains BLOCKED. |
| L15 | Protected browser/profile switch, copied cookie and restart. | No session adoption; absence of qualified loss/isolation proof stops. |
| L16 | Use preconfigured mismatching client/config/issuer snapshots; no live reconfiguration needed. | Wrong registrations deny; snapshots do not prove live config-change ordering. |
| L17 | Simulate Owner replacement/rebinding/generation/epoch/incarnation changes only in non-authorizing test memory. | Old context always rejects; does not qualify D03 production rollback protection. |
| L18 | Issuer outage/throttling/unknown response and loss of test read permission. | Deny, no cached-positive fallback; preserve local closure. |
| L19 | Documented-source and bounded trace review of revocation/disable/logout immediately after online read. | Require supported ordering guarantee; observed test success cannot manufacture it. Unknown keeps D01 BLOCKED. |
| L20 | D04 dependency review: browser/runtime tokens/callback/deployment/issuer admin cannot be controlled by test executor. | Independent effective-permission evidence required; no escalation, real credential extraction or attack on production. |

Evidence: immutable sanitized configuration revision, public issuer/client labels
or redacted stable comparison identifiers, transaction/observation timestamps,
claim-validation dispositions and issuer error classes. Keep raw tokens, codes,
cookies, MFA values and PKCE verifier out of retained evidence. Test administrator
handles any authorized mutations directly; no executor privilege promotion.

Stop if any required prerequisite is absent, human consent is unavailable,
mutation scope would touch a production user, exclusion cannot be proven or
supported lifecycle coverage/ordering remains missing. Cleanup/restore of test
account state must also be explicitly covered by future mutation authorization;
do not silently reenable, recreate users or edit clients. Record residual state
honestly. No live stage has been run in this phase.

## 11. Contract preservation and documentary validation

This document qualifies a relying-party candidate; it changes no schema, canonical
body, flag, evaluator or source. D05 still contains seven separately versioned
outer records, merged production evaluation/AdmissionIntent, reference-only copied
metadata and protected current-gate/one-claim authority. No old record or fixture
is promoted.

Current public valid-input eligibility remains `G3_APPROVAL_ORIGIN_UNVERIFIED`.
Fixture-only positive decisions have no dispatch authority; Host evidence remains
`OFFLINE_CONTRACT_ONLY`, with owner_authenticated=false and approval/dispatch
authority none. Subject, ApprovalGrant, Revocation, EligibilityDecision,
HostApprovalProposal, HostApprovalEvent and HostDecisionEvidenceCandidate are
unchanged. No fixture or authority factory is invoked for this review.

Local documentary verification checks all required final fields, twelve classified
requirements, five stage definitions, twenty future diagnostic cases, links and
historical byte preservation. The original manifest builder is reused twice on
an isolated static snapshot: 341 deterministic entries, all previous 340 unchanged.
Ten prior untracked documents, including D05, and 21 pinned schemas remain
byte-identical. No source/package guard is weakened. Ignored evidence is under
`state/g3-u1-d01-qualification-20261008/`. This is static documentary consistency,
not executable identity validation, live qualification or full runtime regression.

No N01/N02, Cognito resource, login, credential access, AWS deployment, admission,
grant/revocation, provider execution, account/policy change, commit, push, merge,
tag, freeze or release is performed. Public documentation reads are not provider
execution or authenticated cloud calls.

```text
D01_IDENTITY = BLOCKED
SELECTED_IDENTITY_ISSUER = AMAZON_COGNITO_MANAGED_LOGIN_OIDC_CANDIDATE_ONLY
OWNER_PRINCIPAL_MODEL = EXACT_ISSUER_CLIENT_ID_SUB
OWNER_ENROLLMENT_MODEL = PREAUTHORIZED_ADMIN_NOMINATION_PLUS_FRESH_OWNER_CONFIRMATION_CONDITIONAL
CURRENT_CONTEXT_VALIDATION = BLOCKED_MISSING_ORDERED_LIFECYCLE_PROOF
LOGOUT_INVALIDATION = LOCAL_RETIRE_DEFINED_EXTERNAL_LIFECYCLE_BLOCKED
TOKEN_REVOCATION_HANDLING = ONLINE_GETUSER_PLUS_ADMIN_STATUS_CONDITIONAL
OWNER_BINDING_INVALIDATION = PROTECTED_GENERATIONS_AND_FENCED_RETIREMENT_DEFINED
ACCOUNT_SWITCH_HANDLING = LOCAL_SWITCH_RETIRE_DEFINED_EXTERNAL_SWITCH_BLOCKED
ROLE_LIFECYCLE_DEPENDENCY = NONE_FOR_OWNER_AUTHORITY_ADMIN_EXCLUSION_REQUIRES_D04
EXECUTOR_IDENTITY_EXCLUSION_DEPENDENCY = BLOCKED_PENDING_D04_BROWSER_TOKEN_CALLBACK_ISSUER_ADMIN_EXCLUSION
LIVE_QUALIFICATION_REQUIRED = YES
LIVE_QUALIFICATION_DEFINED = YES
D01_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
LIVE_DIAGNOSTICS_PERFORMED = 0
SIGNINS_PERFORMED = 0
N01_N02_IMPLEMENTED = NO
CREDENTIAL_ACCESS = NONE
ACCOUNT_POLICY_CHANGES = NONE
EXISTING_V1_AND_D05_CONTRACTS_CHANGED = NO
```
