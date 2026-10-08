# Nexus G3 U1 D01 managed identity and session reuse survey v1

Date: 2026-10-08. Phase: documentary reuse qualification only.
Source checkpoint: `571bfc872873cb361361ab2c66ed59e591067ac1`,
branch `nexus-v2-g3-development`.

**Stytch Consumer Sessions is the preferred primitive for further qualification:**
direct remote authentication of an opaque session token, with an exact returned
session/user identity and no requested lifetime extension. Clerk is the closest
alternative through an exact session GET. This selection identifies a narrower
reuse opportunity; it does not qualify a production Owner login or admission.
The primitive is documented in the
[Stytch validation guide](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session)
and [Authenticate Session API](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session).

No reviewed provider documents a guarantee that external session validity stays
current through a later Nexus dispatch claim. The accepted D01 continuous
lifecycle requirement remains unsatisfied. **D01 and U1 implementation readiness
remain NO.** A managed session service can replace custom external session
management; constructing a custom lifecycle broker is not a demonstrated remedy
for the remaining ordering gap.

## 1. Inputs, scope and evidence meanings

Authoritative inputs remain the accepted
[minimal authority architecture](nexus-g3-u1-minimal-authority-architecture-v1.md),
[Option C qualification](nexus-g3-u1-option-c-deployment-qualification-v1.md),
[N02 amendment](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md),
[D05 contracts](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[D01 Cognito qualification](nexus-g3-u1-d01-identity-lifecycle-qualification-v1.md),
[G3 v1 contracts](nexus-g3-authorization-contracts-v1.md), and
[offline bridge](nexus-g3-host-approval-bridge-contract-v1.md).
This survey is **not an amendment** to any of them. In particular, the accepted
`CURRENT_CONTEXT_VALIDATION = BLOCKED_MISSING_ORDERED_LIFECYCLE_PROOF` stands.

Only public technical documentation and local static files were inspected.
No accounts, applications, tenants, pools or projects were registered; no sign-in,
credential access, authenticated API request, live diagnostic, deployment,
provider execution, enrollment, grant or revocation occurred. No N01/N02 code was
implemented. Source and canonical contract bodies remain unchanged.

| Label | Meaning |
|---|---|
| VERIFIED_CANDIDATE | Official technical documentation establishes the specified primitive. No deployment, entitlement, principal, secret custody or measured behavior is verified. |
| CONDITIONAL | A useful documented primitive needs additional configuration, identity mapping, integration or lifecycle qualification. Explicit UNKNOWN subproperties remain unresolved. |
| BLOCKED | A required property cannot be established from the reviewed evidence; dependent positive authority is unavailable. This does not prove universal impossibility. |

All actual deployment capabilities are **UNKNOWN**. Provider summaries use the
requested three classifications. A primitive may be VERIFIED_CANDIDATE while
its full use in N01 is CONDITIONAL or BLOCKED. No marketing, pricing feature count,
forum claim or uninspected dashboard constitutes qualification.

“Current” below means provider-observed validity during the remote operation,
not the browser's currently selected account, continuous human presence, or
validity at some later local transaction. An exact session identifier is a
reference; an opaque session token is a bearer secret. They are not interchangeable.

## 2. Capability comparison and selection

| Candidate | Smallest relevant documented capability | Principal/application qualification | Main limitation relative to Nexus | Disposition |
|---|---|---|---|---|
| WorkOS AuthKit | List active sessions for exact user, locate exact `sid`; revoke that session | Stable provider user plus fixed AuthKit application/environment; full D05 tuple mapping CONDITIONAL | Paginated membership lookup; no snapshot/claim fence established | Useful reuse alternative |
| Stytch Consumer | Remote Authenticate Session with opaque token; returned exact session/user; omit duration extension | Provider user plus fixed project/environment; exact D05 issuer/client mapping CONDITIONAL | Token custody, complete account lifecycle and login mapping still unqualified; no claim fence | Preferred session primitive |
| Clerk | Backend `GET /sessions/{session_id}`; remote state/user/expiry; revoke | Signed instance issuer/sub/sid; fixed application binding CONDITIONAL | Browser client ID is not an OIDC app ID; active provider session is not active browser account; no claim fence | Closest alternative |
| Auth0 | Enterprise Management API exact session GET; single/all deletion; back-channel logout | OIDC issuer/client/sub primitive VERIFIED_CANDIDATE | Required Enterprise access UNKNOWN; deletion and back-channel delivery expressly asynchronous | Strong OIDC alternative with additional entitlement/custody requirements |
| Cognito | Online token/user checks and token-family/global revocation | Existing OIDC issuer/client/sub primitive VERIFIED_CANDIDATE | No qualifying exact managed-login session-status endpoint established in the reviewed baseline | Keep historical baseline; not preferred for this gap |

The API bases are the
[WorkOS session reference](https://workos.com/docs/reference/authkit/session),
[Stytch session authentication](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session),
[Clerk session GET](https://clerk.com/docs/reference/backend/sessions/get-session),
[Auth0 session management](https://auth0.com/docs/manage-users/sessions/manage-user-sessions-with-auth0-management-api),
and [Cognito GetUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetUser.html).

Selection is an engineering inference from those bounded capabilities. Stytch
directly authenticates possession and session validity in one provider operation
without needing a list search or a session-management Enterprise entitlement
identified in the reviewed docs. This is not a claim of free access, contractual
SLA, strongest account lifecycle, or lowest total implementation cost. Actual
access and commercial terms remain UNKNOWN. Clerk's exact GET would be preferable
if avoiding persistent opaque-token custody outweighs Stytch's explicit remote
authentication semantics in a later qualified deployment.

If unchanged D05 principal semantics require a separately registered OIDC client
that cannot be mapped to the Stytch project-bound identity evidence, this Stytch
path must stop; Auth0 is the documented OIDC alternative, not permission to
reinterpret `client_id` or add a custom identity issuer. No complete provider is
qualified for the existing continuous contract.

## 3. WorkOS AuthKit

<!-- PROVIDER WORKOS START -->

| ID | Requirement | Classification | Evidence and remaining limitation |
|---|---|---|---|
| R01 | Stable principal | CONDITIONAL | JWT `sub` is WorkOS user ID; pin exact `iss`, application/environment and application-specific validation keys. Email/name are excluded. Full client-bound D05 identity evidence still needs qualification; no assumed `aud` claim. |
| R02 | Server session | VERIFIED_CANDIDATE | AuthKit creates a provider session with user, ID, status and expiry. This is distinct from the access JWT. |
| R03 | Exact remote validation | CONDITIONAL | List all active sessions for the enrolled user, match exact `sid`/user and expiry. Finish necessary pagination; incomplete/ambiguous lookup denies. No direct exact GET or consistent list snapshot is assumed. |
| R04 | Revocation/account lifecycle | CONDITIONAL | Single session revoke documented; listing then revoking covers observed sessions, not atomic all-session retirement against concurrent login. User deletion documented; automatic session/token invalidation and account-disable propagation remain UNKNOWN. |
| R05 | Logout | CONDITIONAL | WorkOS prescribes deleting app session then redirecting to provider logout using `sid`. Clearing a cookie alone is insufficient. JWT/refresh/backend/upstream distinctions appear in Section 8. |
| R06 | Claim-time check | CONDITIONAL | Protected N01 could perform a fresh remote list/membership check immediately before claim, subject to deadlines and D04. Local JWT/sealed-session validation alone does not provide this check. |
| R07 | Account/profile isolation | CONDITIONAL | Bind exact session/user; organization refresh can change organization without changing user. Never use organization role as Nexus ownership. Unobserved browser/profile switching is not remotely proven. |
| R08 | Freshness | CONDITIONAL | Maximum session length, access-token duration and inactivity timeout are configurable. Inactivity depends on refresh. Nexus must not renew its bounded context through automatic refresh. Actual settings/access UNKNOWN. |
| R09 | Lifecycle ordering | BLOCKED | No reviewed validation-through-Nexus-claim lease, shared transaction or mandatory external revocation barrier. Pagination and a recent token do not create one. |
| R10 | Events | CONDITIONAL | `session.revoked` and `user.deleted` documented. Full disable/logout coverage and delivery-to-claim ordering are unqualified; events only trigger retirement/recheck. |
| R11 | OwnerContext | CONDITIONAL | Exact managed session plus protected project binding can simplify session tracking. Complete identity/freshness/current-browser proof and continuous ordering remain unresolved. |
| R12 | Executor exclusion | BLOCKED | D04 must protect Owner browser, provider administration, API key, callback, runtime and evidence. Provider storage outside repo does not establish these permissions. |

Sources: [AuthKit sessions and claims](https://workos.com/docs/authkit/sessions),
[session list/revoke](https://workos.com/docs/reference/authkit/session),
[user read/delete](https://workos.com/docs/reference/authkit/user),
[events](https://workos.com/docs/events), and
[webhook infrastructure](https://workos.com/docs/reference/webhooks).

Automatic token refresh rotates refresh tokens; the SDK resilience guidance can
retain application sessions on transient failure. Nexus must independently deny
protected authority transitions whenever required remote evidence is missing,
including timeout, rate limit or server error. Keeping a UX session is not a
positive admission decision.
[Session resilience](https://workos.com/docs/authkit/session-resilience).

```text
IDENTITY = CONDITIONAL
SERVER_SESSION = VERIFIED_CANDIDATE
REMOTE_SESSION_VALIDATION = CONDITIONAL
SESSION_REVOCATION = CONDITIONAL
LOGOUT_SEMANTICS = CONDITIONAL
CLAIM_TIME_VALIDATION = CONDITIONAL
ACCOUNT_SWITCH_ISOLATION = CONDITIONAL
LIFECYCLE_ORDERING = BLOCKED
D04_DEPENDENCY = BLOCKED
```

<!-- PROVIDER WORKOS END -->

## 4. Stytch Consumer Sessions

<!-- PROVIDER STYTCH START -->

| ID | Requirement | Classification | Evidence and remaining limitation |
|---|---|---|---|
| R01 | Stable principal | CONDITIONAL | Native `user_id` is provider user identity; fixed project credentials select the provider application partition. Exact D05 issuer/client assertion mapping and identifier continuity under merge/recovery are not yet qualified. Never use email/external_id/name to enroll. |
| R02 | Server session | VERIFIED_CANDIDATE | Provider Session object identifies one user/session, authentication factors, start/access/expiry times; JWT and opaque token represent that underlying session. |
| R03 | Exact remote validation | VERIFIED_CANDIDATE | Direct Authenticate Session always contacts Stytch; opaque-token validity is established at that point. Match returned `session_id` and `user_id` to protected enrollment/session reference. SDK local JWT fallback is excluded. |
| R04 | Revocation/account lifecycle | CONDITIONAL | Revoke by exact session ID/token/JWT documents immediate opaque-token invalidation. List active user sessions then revoke each is possible, but not a race-free global disable. Complete delete/disable effects and propagation remain UNKNOWN in reviewed evidence. |
| R05 | Logout | CONDITIONAL | Revoke provider session plus retire Nexus context and clear browser locator. Offline JWT may remain signature/expiry-valid; no upstream-provider logout or remote browser-selection proof is assumed. |
| R06 | Claim-time check | CONDITIONAL | Protected N01 can directly authenticate the retained opaque token immediately before claim without requesting duration extension. This is a point check, not atomic ordering with Nexus. |
| R07 | Account/profile isolation | CONDITIONAL | Exact session/user join separates A's context from B's session. A session can remain valid when the visible browser switches elsewhere. Retire observed switches locally; unknown external switches remain a gap. |
| R08 | Freshness | CONDITIONAL | Session expiry exposed; authenticate can extend lifetime if duration supplied. Omit it on rechecks. SDK docs distinguish extension from JWT renewal. Native idle policy and guaranteed nonrenewable provider mode remain UNKNOWN; enforce Nexus's independent absolute deadline. |
| R09 | Lifecycle ordering | BLOCKED | Explicit point-time validity does not grant a lease through subsequent claim. Immediate token invalidation after revoke does not exclude revoke between validation and local commit. |
| R10 | Events | CONDITIONAL | Consumer user-change webhooks supported; reviewed linked catalog does not establish session/logout/disable coverage. Stytch documents no inherent event ordering guarantee. Do not substitute events for current validation. |
| R11 | OwnerContext | CONDITIONAL | Managed user/session + direct remote authentication + exact Nexus Owner binding + bounded confirmation is a concrete reuse path. Identity/login/account-lifecycle gaps and unchanged continuous requirement still block use. |
| R12 | Executor exclusion | BLOCKED | D04 must exclude executor from Owner browser, project secret, bearer tokens, admin console/API, login ingress, callback and protected session evidence. |

Sources: [session layer](https://stytch.com/docs/consumer-auth/manage-sessions/overview),
[session object](https://stytch.com/docs/api-reference/consumer/api/sessions/session-object),
[user object](https://stytch.com/docs/api-reference/consumer/api/users/user-object),
[remote validation](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session),
[Authenticate Session](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session),
[Get Sessions](https://stytch.com/docs/api-reference/consumer/api/sessions/get-sessions),
[Revoke Session](https://stytch.com/docs/api-reference/consumer/api/sessions/revoke-session),
[Authenticate JWT](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-jwt),
[webhooks](https://stytch.com/docs/resources/workspace-management/webhooks), and
the [provider-linked Consumer event catalog](https://www.svix.com/event-types/us/org_2olWIePjxAFYube1xW8DoQUEnyY/).

The SDK `authenticateJwt` can validate locally until its age/expiry threshold;
its name alone does not prove a remote call. Select direct remote authentication,
omit `session_duration_minutes` and custom-claim writes, and never replace the
original Nexus deadline with a newly minted JWT expiry. An expired JWT can be
renewed against a still-valid underlying session; that is not fresh human login.
[Consumer Authenticate JWT semantics](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-jwt).

The user model's `is_locked` describes a temporary failed-authentication lock,
not a qualified administrative disable fence. Do not infer existing sessions are
invalidated by that flag. The future candidate must separately establish the
account-status checks required by D01; missing evidence denies.
[User object](https://stytch.com/docs/api-reference/consumer/api/users/user-object)
and [user locks](https://stytch.com/docs/resources/policies/platform/user-locks).

```text
IDENTITY = CONDITIONAL
SERVER_SESSION = VERIFIED_CANDIDATE
REMOTE_SESSION_VALIDATION = VERIFIED_CANDIDATE
SESSION_REVOCATION = CONDITIONAL
LOGOUT_SEMANTICS = CONDITIONAL
CLAIM_TIME_VALIDATION = CONDITIONAL
ACCOUNT_SWITCH_ISOLATION = CONDITIONAL
LIFECYCLE_ORDERING = BLOCKED
D04_DEPENDENCY = BLOCKED
```

<!-- PROVIDER STYTCH END -->

## 5. Clerk

<!-- PROVIDER CLERK START -->

| ID | Requirement | Classification | Evidence and remaining limitation |
|---|---|---|---|
| R01 | Stable principal | CONDITIONAL | Session JWT contains instance `iss`, user `sub`, exact `sid`. Bind a protected fixed application/instance; `azp` is request origin, not OIDC client ID. Backend Session `clientId` identifies a browser client, not fixed Nexus app registration. D05 mapping remains unqualified. |
| R02 | Server session | VERIFIED_CANDIDATE | Backend Session resource exposes ID, user, status, expiry/abandonment and activity. It is separate from the short-lived session JWT. |
| R03 | Exact remote validation | VERIFIED_CANDIDATE | Backend `getSession(sessionId)` wraps exact session GET. Join ID/user, require active status and unexpired resource plus independently authenticated session origin. ID lookup alone does not authenticate a caller. |
| R04 | Revocation/account lifecycle | CONDITIONAL | Exact revoke documented. Global user-session retirement requires complete list/revoke or ban; `banUser` revokes all sessions and prevents login. Delete supported, but exact delete-to-session propagation is not established here. No Nexus atomicity/SLA inferred. |
| R05 | Logout | CONDITIONAL | `signOut` ends selected/current-client sessions, not every other device. Exact session selection matters. Browser cleanup and provider termination do not automatically retire a separate Nexus backend context or already-issued offline token. |
| R06 | Claim-time check | CONDITIONAL | Protected fresh Backend API GET can precede claim. JWT authentication alone, even with a short token lifetime, does not establish that this status read occurred. |
| R07 | Account/profile isolation | CONDITIONAL | Multi-session accounts are independent; switching active session is supported. Binding exact `sid`/user prevents cross-account substitution but does not prove old sessions were revoked or observe another browser profile. |
| R08 | Freshness | CONDITIONAL | Maximum lifetime and inactivity timeout supported; custom production lifetime/idle settings require paid access. Activity includes token refresh. Stop refresh-based Nexus renewal and impose existing context deadline. Native absolute nonrefreshable mode not qualified. |
| R09 | Lifecycle ordering | BLOCKED | No reviewed session GET validity lease/shared Nexus transaction. An active response followed by ban/revoke can precede claim; remote session active is not a current-browser assertion. |
| R10 | Events | CONDITIONAL | Webhooks supported; public guide points full event catalog to dashboard. Exact logout/revoke/disable subscriptions not deployment-qualified. Guide explicitly disclaims ordering and synchronous delivery. |
| R11 | OwnerContext | CONDITIONAL | Exact managed session GET provides a small reuse seam. Qualified application mapping, fresh authentication, callback/token custody and continuous lifecycle remain dependencies. Reject impersonated Owner sessions. |
| R12 | Executor exclusion | BLOCKED | D04 must protect Owner browser, secret key, provider admin/actor-token surfaces, ingress/callback and evidence. Publishable client access is not exclusive authority. |

Sources: [session claims](https://clerk.com/docs/guides/sessions/session-tokens),
[Backend Session](https://clerk.com/docs/reference/backend/types/backend-session),
[session GET](https://clerk.com/docs/reference/backend/sessions/get-session),
[session revoke](https://clerk.com/docs/reference/backend/sessions/revoke-session),
[user ban](https://clerk.com/docs/reference/backend/user/ban-user),
[user delete](https://clerk.com/docs/reference/backend/user/delete-user),
[session options](https://clerk.com/docs/guides/secure/session-options),
[multi-session switching](https://clerk.com/docs/guides/development/custom-flows/authentication/multi-session-applications),
[sign-out](https://clerk.com/docs/guides/development/custom-flows/authentication/sign-out), and
[webhook delivery semantics](https://clerk.com/docs/guides/development/webhooks/overview).

The minimal candidate would avoid multi-account Owner confirmation flows; a
Nexus-observed new session must retire the old context before creating a new one.
That is a proposed relying-party restriction, not proof that Clerk or the Host
prevents all external profile switches. Clerk's actor/impersonation evidence must
be rejected for actual Owner authority, rather than interpreting impersonation
as the human principal's confirmation.
[Backend Session actor](https://clerk.com/docs/reference/backend/types/backend-session).

```text
IDENTITY = CONDITIONAL
SERVER_SESSION = VERIFIED_CANDIDATE
REMOTE_SESSION_VALIDATION = VERIFIED_CANDIDATE
SESSION_REVOCATION = CONDITIONAL
LOGOUT_SEMANTICS = CONDITIONAL
CLAIM_TIME_VALIDATION = CONDITIONAL
ACCOUNT_SWITCH_ISOLATION = CONDITIONAL
LIFECYCLE_ORDERING = BLOCKED
D04_DEPENDENCY = BLOCKED
```

<!-- PROVIDER CLERK END -->

## 6. Auth0

<!-- PROVIDER AUTH0 START -->

| ID | Requirement | Classification | Evidence and remaining limitation |
|---|---|---|---|
| R01 | Stable principal | VERIFIED_CANDIDATE | OIDC ID token issuer/client audience/sub matches D05's tuple primitive. Require exact registered strings, signature and transaction checks; no email/name authority or silent account-link migration. No actual Owner/app verified. |
| R02 | Server session | VERIFIED_CANDIDATE | Auth0 SSO Session resource has persistent `sid` distinct from application session and access/refresh tokens. |
| R03 | Exact remote validation | CONDITIONAL | `GET /api/v2/sessions/{sessionId}` with `read:sessions`; join ID-token sid/user/application evidence and expiry. Session API requires Enterprise entitlement, presently UNKNOWN. |
| R04 | Revocation/account lifecycle | CONDITIONAL | Single/all session DELETE documented. Revoke endpoint also targets associated refresh tokens; deletion is asynchronous/eventually consistent. Blocking prevents login; immediate removal of every active authority after block/delete remains unqualified. |
| R05 | Logout | CONDITIONAL | OIDC logout terminates Auth0 session layer. Separate local application and upstream IdP layers exist; refresh tokens can survive session expiry/delete/logout. Access JWT must not be treated as revocation-aware proof. |
| R06 | Claim-time check | CONDITIONAL | Fresh protected exact session GET before claim is possible with qualified entitlement/custody. It does not make preceding deletion request completion or later validity atomic. |
| R07 | Account/profile isolation | CONDITIONAL | Sid refers to user-agent/device SSO session; bind it with verified principal/app. Other sessions can remain. Exact session identity does not observe every Host/browser account switch. |
| R08 | Freshness | CONDITIONAL | Idle and maximum lifetime for persistent/nonpersistent sessions configurable. Enforce fresh `auth_time` through supported reauthentication, not JWT issue time. No Nexus renewal from silent login/refresh; actual configuration unverified. |
| R09 | Lifecycle ordering | BLOCKED | DELETE is expressly eventually consistent; revoke response 202 is accepted, not completed. No validation-through-claim fence. Even a completed remote revocation implementation would leave the later local claim race. |
| R10 | Events | CONDITIONAL | Enterprise OIDC Back-Channel Logout carries signed sub/sid to retire local sessions; requests queued asynchronously. Complete block/delete initiation coverage is not qualified. It cannot be an atomic claim-time fence. |
| R11 | OwnerContext | CONDITIONAL | OIDC principal + exact remote session + Nexus binding is a useful alternative. Enterprise access, external lifecycle ordering and exclusion remain dependencies. |
| R12 | Executor exclusion | BLOCKED | D04 must isolate Owner browser, tenant administration, application/client settings, Management API token/credentials, callback and protected state. No executor management scopes. |

Sources: [ID-token validation](https://auth0.com/docs/secure/tokens/id-tokens/validate-id-tokens),
[session Management API](https://auth0.com/docs/manage-users/sessions/manage-user-sessions-with-auth0-management-api),
[session and refresh-token revoke](https://auth0.com/docs/api/management/v2/sessions/revoke-session),
[account block](https://auth0.com/docs/manage-users/user-accounts/block-and-unblock-users),
[logout layers](https://auth0.com/docs/authenticate/login/logout),
[OIDC logout](https://auth0.com/docs/authenticate/login/logout/log-users-out-of-auth0),
[upstream logout](https://auth0.com/docs/authenticate/login/logout/log-users-out-of-idps),
[session lifetime](https://auth0.com/docs/manage-users/sessions/configure-session-lifetime),
[fresh authentication](https://auth0.com/docs/authenticate/login/max-age-reauthentication), and
[back-channel logout](https://auth0.com/docs/authenticate/login/logout/back-channel-logout).

Access to the session API is a mandatory prerequisite, not a feature inferred
from an ordinary Auth0 account. N01's future read path would need protected
Management API authentication with `read:sessions` and any independently
qualified user-status read scope; provider administration/revocation scopes
belong to separately protected administration. No Management API token or client
secret has been read or created.

```text
IDENTITY = VERIFIED_CANDIDATE
SERVER_SESSION = VERIFIED_CANDIDATE
REMOTE_SESSION_VALIDATION = CONDITIONAL
SESSION_REVOCATION = CONDITIONAL
LOGOUT_SEMANTICS = CONDITIONAL
CLAIM_TIME_VALIDATION = CONDITIONAL
ACCOUNT_SWITCH_ISOLATION = CONDITIONAL
LIFECYCLE_ORDERING = BLOCKED
D04_DEPENDENCY = BLOCKED
```

<!-- PROVIDER AUTH0 END -->

## 7. Amazon Cognito baseline

<!-- PROVIDER COGNITO START -->

| ID | Requirement | Classification | Evidence and remaining limitation |
|---|---|---|---|
| R01 | Stable principal | VERIFIED_CANDIDATE | Existing D01 exact registered issuer/client/sub; ID audience and access-token client are separately validated. Email/name never authority. |
| R02 | Server session | CONDITIONAL | Managed-login browser session and token revocation state exist. A qualifying backend-readable exact managed-login session object/join is not established; do not equate origin_jti with that object. |
| R03 | Exact remote validation | BLOCKED | GetUser can validate token/user, not attest that a specific managed-login browser session is current or that the selected browser/profile still matches. |
| R04 | Revocation/account lifecycle | CONDITIONAL | RevokeToken targets refresh-token family; GlobalSignOut/AdminUserGlobalSignOut target all user tokens; disable revokes access/refresh. Account deletion checks and propagation require qualification; offline JWT verification still accepts revoked signed tokens. |
| R05 | Logout | BLOCKED | Managed-login /logout and token sign-out are different operations. /logout does not log out OIDC/social IdPs; external browser-only logout is not a qualified Nexus retirement signal. |
| R06 | Claim-time check | BLOCKED | Online token/user/config checks can precede claim, but do not supply required exact active browser-session evidence or ordered lifecycle proof. |
| R07 | Account/profile isolation | BLOCKED | Exact token principal prevents identity substitution; a retained token does not detect all issuer/Host/profile switches. Prior D01 blocking conclusion retained. |
| R08 | Freshness | CONDITIONAL | Prior D01 qualified documented token expiry/login primitives, separate managed-login cookie and refresh behavior. Proposed short nonrenewed Nexus context remains insufficient for current session proof. |
| R09 | Lifecycle ordering | BLOCKED | No remote-to-Nexus ordered validation lease/fence established. Token revocation state and short TTL do not supply continuous validity. |
| R10 | Events | BLOCKED | Prior baseline has no qualified complete issuer logout/switch/disable event stream ordered before Nexus claim. Audit/event observations cannot substitute. |
| R11 | OwnerContext | BLOCKED | Can reuse identity primitive, but exact current managed session and continuous lifecycle evidence are still missing under accepted model. |
| R12 | Executor exclusion | BLOCKED | D04 browser/token/callback/issuer-admin exclusion remains unqualified. IAM availability does not verify executor permissions. |

Sources: [accepted D01 baseline](nexus-g3-u1-d01-identity-lifecycle-qualification-v1.md),
[GetUser](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetUser.html),
[token revocation](https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html),
[disable user](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminDisableUser.html), and
[managed-login logout](https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html).
The accepted baseline retains the full identity/login/expiry analysis; no new
Cognito deployment or changed lifecycle premise is inferred by this comparison.

```text
IDENTITY = VERIFIED_CANDIDATE
SERVER_SESSION = CONDITIONAL
REMOTE_SESSION_VALIDATION = BLOCKED
SESSION_REVOCATION = CONDITIONAL
LOGOUT_SEMANTICS = BLOCKED
CLAIM_TIME_VALIDATION = BLOCKED
ACCOUNT_SWITCH_ISOLATION = BLOCKED
LIFECYCLE_ORDERING = BLOCKED
D04_DEPENDENCY = BLOCKED
```

<!-- PROVIDER COGNITO END -->

## 8. Logout and token boundaries

The following distinguishes documented provider effects from **proposed Nexus
retirement**. No provider action was executed. Unqualified or missing coverage
denies current-context qualification; it is not converted to success by a TTL.

| Candidate | Browser/session locator | Provider session | Access/session JWT | Refresh or equivalent bearer | Nexus backend context |
|---|---|---|---|---|---|
| WorkOS | App removes its cookie; logout uses exact sid | Provider logout/revoke ends selected session; global coverage not assumed | Local signature/expiry remains insufficient after lifecycle change | Refresh succeeds only for active session; no future Nexus refresh renewal | N01 must retire separately before further decisions/claims; provider redirect is not proof of that retirement |
| Stytch | Clear protected Nexus locator; do not rely on browser cookie deletion | Exact revoke invalidates underlying session token | Locally checked JWT has documented stale window; direct remote authentication required | Opaque session token is the bearer; new JWT does not renew Nexus context | N01 retires and destroys token custody; external revoke still needs remote observation/order qualification |
| Clerk | Sign-out selected/current-client sessions; other devices can remain | End/revoke exact session | A JWT's existing signature/expiry does not establish live status | Browser-managed session/token renewal is distinct from Nexus context; no refresh token assumed | Separate protected retirement; browser active-session switch cannot silently rebind context |
| Auth0 | OIDC logout acts on Auth0 cookie; application locator separate | Auth0 layer terminated; Management deletion may be pending | No offline JWT-to-current-session equivalence | Refresh can outlive session/logout; explicit associated revoke is separate | Verified back-channel message can trigger retirement, but asynchronous arrival is not a fence |
| Cognito | /logout clears managed-login state; separate Nexus cookie | Exact backend managed-login session proof unqualified | Revoked JWT can still pass offline validation | RevokeToken family and global sign-out are distinct from cookie logout | N01 local retirement defined; issuer-only logout notification remains blocked |

These effects are supported by the provider session/logout sources above,
especially [Stytch JWT versus opaque validation](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session),
[Clerk sign-out scope](https://clerk.com/docs/guides/development/custom-flows/authentication/sign-out),
[Auth0 logout layers](https://auth0.com/docs/authenticate/login/logout), and
[Cognito token revocation](https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html).
Upstream social/OIDC/SAML logout is not generically guaranteed. Prefer no
federation in the minimum candidate; adding it requires separate qualification.
Deleting cookies, closing a browser or losing the Owner UI may remove local
access without producing a remote session-revocation event. Session “active”
therefore cannot alone prove current physical Owner interaction.

## 9. Ordering result: point checks do not close continuous lifecycle

Consider three ordered moments, even for a strongly consistent remote check:

```text
t0: provider authenticates exact session S as valid
t1: provider/admin retires S, or Owner switches away from the protected context
t2: Nexus transaction claims the dispatch attempt using the t0 observation
```

Moving t0 immediately before t2 reduces elapsed time but cannot rule out t1.
Repeating the query after claim can discover invalidation after an irreversible
handoff; it cannot retroactively authorize the effect. Polling, cached status,
webhook timestamps, signed JWT expiry, MFA and short OwnerContext deadlines do
not establish a shared serialization boundary. Holding a Nexus lock during a
remote read does not lock the provider's independent administrator/session state.

**Evidence conclusion:** no reviewed technical source promises a provider-issued
nonrevocable validity lease through a Nexus claim, participates in the Nexus
transaction, or mandates every relevant external retirement/switch through N01.
This is insufficient evidence for this contract, not proof that such a facility
can never exist. Auth0 expressly documents eventual consistency; Stytch and
Clerk expressly disclaim webhook ordering.
[Auth0 deletion limitations](https://auth0.com/docs/manage-users/sessions/manage-user-sessions-with-auth0-management-api),
[Auth0 asynchronous logout queue](https://auth0.com/docs/authenticate/login/logout/back-channel-logout),
[Stytch webhook disclaimers](https://stytch.com/docs/resources/workspace-management/webhooks),
[Clerk webhook guarantees](https://clerk.com/docs/guides/development/webhooks/overview).

Nexus-owned Owner/binding/epoch/revocation transitions still use the unchanged
D05 serialization and D03 recovery fence. They protect Nexus authority state;
they cannot serialize provider-only events. A signed event authenticates an
observation, not the absence of an as-yet-undelivered event. Event loss, delayed
delivery, duplicate replay or restart cannot authorize a positive transition.

## 10. Reuse path and residual OwnerContext responsibilities

Proposed composition only: **managed identity + exact managed session ID +
protected direct remote validation + exact Nexus project Owner binding + bounded
N02 confirmation**. The provider owns external identity/session lifecycle. N01
remains the relying party and owns only the already-authorized Nexus binding,
context retirement and authority evidence. No generic lifecycle broker, identity
issuer, OAuth provider, approval platform, vault or new session database is proposed.

No executor TOFU: independently protected administration preauthorizes the Owner
principal, followed by the existing fresh Owner-binding confirmation ceremony.
Bind exact authority_instance/workspace_id/project_id and protected generations.
Provider roles, organization membership, email, display names and browser labels
do not establish or transfer Nexus ownership. Provider administrator privileges
are D04 dependencies, not Owner entitlements.

D05 `Principal={issuer,client_id,subject}` and `OwnerContext` remain byte-for-byte
unchanged. The managed session ID is retained in qualified protected evidence and
its protected association to existing `session_evidence`; do not add a field,
place a bearer token in an EvidenceRef, or reinterpret `context_id` as a provider
credential. Exact issuer/app/client mapping must be established before production
identity evidence can satisfy the existing tuple. For Stytch this is CONDITIONAL;
no issuer URI or OIDC client claim has been invented. Provider merge/link/recovery
must not silently change the enrolled principal; retirement and a separately
authorized Owner replacement are required if exact identity changes.

The candidate leaves the existing authentication/confirmation requirements in
place: a protected fresh login transaction, authenticated Owner, exact callback,
transaction anti-replay, qualified fresh factor evidence, protected server token
handling, exact frozen proposal/Subject/scope/effect summary and explicit bounded
CONFIRM/DENY. A session check or refreshed JWT is not fresh authentication or
consent. Stytch's initial login mechanism and its compatibility with the accepted
code/PKCE/nonce relying-party requirements are not qualified by this session
survey. Do not silently replace that transaction with an email link or SDK flow.

| Existing stage | Proposed protected checks | Qualification consequence |
|---|---|---|
| page creation | Fresh identity/session join; direct remote validity; current binding/stamp/generations; protected browser and challenge | No page with authoritative confirmation provenance until all prerequisites are qualified |
| decision POST | Same exact session/principal; remote validity; current view/context; CSRF and explicit decision; matching proposal digest | Wrong/stale/missing context denies; no cookie or client boolean can supply evidence |
| receipt creation | Recheck exact session plus local retirement/generation serialization and qualified provenance | Remote observation must not be presented as continuous proof; accepted requirement still blocks positive receipt |
| AdmissionIntent creation | Revalidate context/session/binding, technical/task/Host prerequisites, grant/revocation and fence | Receipt alone never admits; missing ordered lifecycle proof denies |
| DispatchAttempt claim | New uncached protected remote check immediately before claim; compare exact session/user and local generations/deadlines inside existing claim protocol | CONDITIONAL point-check primitive; positive claim remains blocked by continuous lifecycle and D04 |

Short TTL remains an upper bound, not substitute proof. Retain the N02 challenge
maximum of **five minutes**, and bound context by the earliest challenge, verified
session, authentication and protected binding deadlines. These existing design
bounds are not provider SLAs or a new claim-validity allowance. Remote checks,
activity updates, refresh, browser reload and retry never extend the original
Nexus context. Idle/absolute provider settings supplement this bound; any
unqualified idle behavior stays UNKNOWN.

Nexus-observed logout/account/project switch, Owner replacement, binding-generation
change, epoch/incarnation change and context loss retire affected pending
contexts/views/unclaimed intents under existing serialization. Destroy ephemeral
tokens on retirement/restart. Recovery must not restore bearer custody or revive
pre-restart contexts. Unknown outcome/fence acknowledgment quarantines; preserve
`NO_AUTOMATIC_REDISPATCH`. Remote absence/error/timeout/429/5xx, malformed result,
user/session mismatch, stale evidence or missing lifecycle coverage denies.

Under a **separately accepted bounded-observation lifecycle model**, these controls
would plausibly reduce retained-token/cached-session exposure compared with
Cognito-only token checks. This is a qualitative engineering inference, with no
measured reduction or maximum external revocation latency asserted. Such a model
would still accept residual external check-to-claim/switch risk and would be an
explicit architecture/contract acceptance question, not a hidden relaxation in
this document. Under today's accepted continuous model, those controls do not
release positive authority.

## 11. D04 and credential dependency register

| Surface | Authoritative controller/reader | Executor permissions required | Unqualified dependency/failure behavior |
|---|---|---|---|
| Provider user/session state | Managed provider; independently authenticated provider administrators | No administration, impersonation, secret retrieval or session minting/revocation authority | Actual roles/IAM/provider settings UNKNOWN; exclude executor or deny |
| Exact Owner browser/session | Actual enrolled Owner; qualified N02 ingress | No browser automation, cookies, storage, interaction injection, profile selection or user impersonation | Separate profile alone is insufficient; missing D04 exclusion blocks |
| Runtime token/API credential custody | Protected N01 runtime under separate deployment principal | No read/write/debug/shell/process-memory/log/backup access | WorkOS API key; Stytch project secret + opaque bearer; Clerk secret key; Auth0 Management API authentication; Cognito token custody/admin reads where required. Names only, no values accessed |
| Login/callback/session ingress | Protected N01/N02; provider authenticates its response | No callback config edits, origin/code/state/session substitution or positive evidence injection | Exact HTTPS callback, protected transaction, session establishment and fresh authentication remain to qualify |
| Nexus binding/context/evidence/gate | Existing proposed N01, protected ledger plus independent D03 fence | Submit untrusted proposal and read allowed sanitized status only | No authoritative writes, generation reset, restore, direct dispatch or bypass; missing D03/D04 denies |
| Recovery/deployment administration | Separate qualified human/runtime administration | No secret/state snapshot restore, app registration mutation or deployment replacement | No recovered active OwnerContext; restore uncertainty retires/quarantines and keeps admission closed |

A provider-hosted authoritative session is outside writable repository state,
but executor possession of its secret, Owner cookie, administrator login or
deployment access could still forge, alter or bypass the relying-party authority.
No provider capabilities independently close D04. Existing OpenAI/Codex interaction
and execution reuse neither establishes these permissions nor exposes a trusted
Owner browser by itself.

## 12. Answers A-D and closure conditions

| Question | Answer | Consequence |
|---|---|---|
| A. Material improvement over Cognito? | YES for WorkOS/Stytch/Clerk/Auth0 managed-session observation, subject to their conditions. Stytch is preferred for its direct remote opaque-session check. | Provides evidence of one managed session, rather than merely a retained token/user. Does not prove continuous browser context. |
| B. Eliminate custom lifecycle broker? | YES for owning external sessions and point-time checks: reuse provider authority. NO candidate closes the unchanged continuous contract. Building a broker is not a justified solution to undocumented provider ordering. | `CUSTOM_LIFECYCLE_BROKER_REQUIRED = NO` is the recommendation to reuse and retain the stop gate; it does not assert complete lifecycle qualification or removal of N01's existing context responsibilities. |
| C. Fully satisfy continuous lifecycle? | NO established candidate. | Existing D01 BLOCKED remains; no positive receipt/admission/dispatch. Unknown stronger guarantees require evidence, not custom composition assumptions. |
| D. Managed session plus bounded OwnerContext reduces residual risk? | YES as a conditional qualitative inference for an explicitly accepted bounded model. NO as proof under the current continuous contract. | Retain bounded context; do not change the accepted model or readiness. |

Remaining closure gaps are: exact issuer/application/client identity mapping and
fresh login integration for the preferred primitive; complete account disable,
delete, recovery/link and provider-only logout/switch coverage; documented
external lifecycle ordering through protected claim; actual D04 browser/admin/
credential/callback/runtime exclusion; qualified D03 recovery and production D05
seam. Deployment entitlements and actual runtime behavior are UNKNOWN.

A later separately authorized isolated diagnostic could check the chosen
provider's fresh login, exact session/user/application join, unchanged expiry on
remote recheck, single/all session retirement, account disable/delete, cookie-only
logout, account/profile switching, timeout/rate-limit denial, event delay/replay
and restart retirement. It must use a prepared isolated protected environment,
synthetic proposals, no real grants/intents/providers and no production credentials.
Testing cannot establish a universal ordering guarantee absent a documented
protocol. Do not run it until the design and exclusion prerequisites are qualified;
no live diagnostic ran in this survey.

## 13. Documentary validation and repository preservation

The local verifier checks all five providers' twelve requirements (60 rows),
45 provider status fields and 17 final fields, link targets, secret-shaped content,
unchanged baseline raw bytes, unchanged source/contracts and 21 pinned Host schema
records. It parses existing fail-closed source without executing an authority
factory. Existing `OFFLINE_CONTRACT_ONLY` evidence and
`G3_APPROVAL_ORIGIN_UNVERIFIED` refusal remain preserved.

The original manifest builder runs twice on a fresh isolated source snapshot,
without changing its source-boundary rules. Its existing `SENSITIVE_TOKENS`
path rule excludes this required filename because it contains `session`.
Consequently the new document is **not included in MANIFEST**; all 341 existing
entries and the existing MANIFEST bytes remain unchanged. The new document's raw
SHA256 is recorded separately in ignored documentary evidence. This exclusion is
a repository packaging/manifest limitation, not an identity qualification result.
No filename workaround, manual manifest insertion or rule relaxation was made.

Evidence paths: `state/g3-u1-d01-managed-session-survey-20261008/baseline.json`,
`baseline-manifest.json`, `verify_documentary.py`, `validation.json` and
`static-source/`. Static PASS only means documentary consistency and preservation;
it is not deployed identity/session/exclusion/admission verification.

This phase adds only the requested survey document to Git-visible files; eleven
pre-existing untracked documents and the pre-existing MANIFEST modification are
preserved. No commit, push, merge, tag, freeze or release occurs.

## 14. Exact final status

YES capability values below mean documented Stytch candidate primitives, not
verified deployment. SESSION_REVOCATION_AVAILABLE covers exact-session revocation;
all-session/account-lifecycle coverage remains CONDITIONAL. The claim-time value
includes unqualified protected N01/D04 integration. REUSE_PATH_DEFINED describes
this conditional documentary composition only.

```text
D01_MANAGED_SESSION_REUSE_SURVEY = COMPLETE
BEST_CANDIDATE = STYTCH
BEST_CANDIDATE_REASON = DIRECT_REMOTE_OPAQUE_SESSION_AUTHENTICATION_WITHOUT_LIFETIME_EXTENSION_CANDIDATE_ONLY
SERVER_SIDE_SESSION_AVAILABLE = YES
REMOTE_CURRENT_SESSION_VALIDATION = YES
SESSION_REVOCATION_AVAILABLE = YES
CLAIM_TIME_SESSION_RECHECK = CONDITIONAL
CONTINUOUS_EXTERNAL_LIFECYCLE_REQUIREMENT_SATISFIED = NO
CUSTOM_LIFECYCLE_BROKER_REQUIRED = NO
BOUNDED_OWNER_CONTEXT_STILL_REQUIRED = YES
D01_REUSE_PATH_DEFINED = YES
D01_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
```
