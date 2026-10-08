# G3 U1 D01 bounded OwnerContext amendment v1

Date: 2026-10-08. Status: architecture amendment, not deployed identity qualification.
Source: overnight-run authorization and the accepted [managed-session survey](nexus-g3-u1-d01-managed-identity-session-reuse-survey-v1.md), [D05](nexus-g3-u1-d05-production-authority-contracts-v1.md), and [N02 amendment](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md).

## Decision and exact limitation

The authorized model replaces continuous external lifecycle ordering with a
short-lived, non-refreshable, single-challenge Nexus OwnerContext. Stytch Consumer
Sessions is the preferred managed candidate. This changes the lifecycle requirement;
it does not establish a verified Owner enrollment, protected browser or deployed
executor exclusion. Historical Cognito/continuous-lifecycle BLOCKED conclusions
remain true for their original requirements.

RESIDUAL_CHECK_TO_CLAIM_RISK is ACCEPTED for this bounded architecture under the
user's explicit bounded-context authorization. It is not a claim that the race is
eliminated or permission to activate admission: remote success at t0, external
revoke/logout at t1, then local claim at t2 can still occur. There is no shared
Stytch/Nexus transaction or guaranteed provider lease. The maximum five-minute
context lifetime bounds exposure but does not replace a required remote recheck.
No custom lifecycle broker is proposed.

The documented direct `authenticate()` path contacts Stytch; locally validated
JWTs do not supply the required current remote evidence. This is a documented
capability, not a tested project configuration.
[Provider validation semantics](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session).
The candidate uses opaque session authentication and omits duration-extension and
custom-claim parameters. Its response carries session/user identifiers and expiry.
[Authenticate Session](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session).

## Protected context policy

N01 creates the context only from authenticated protected N02 ingress after fresh
human authentication meeting a separately qualified factor policy. Remote session
validation alone does not prove a fresh human interaction. Authentication-factor
freshness, login callback/CSRF/origin checks and token custody remain prerequisites.
No executor TOFU enrollment: a separate authenticated Owner/admin ceremony binds
one registered principal to exact authority_instance/workspace_id/project_id,
owner_generation, binding_id and binding_generation. No email/name authority.

One protected context_id maps internally to exactly one challenge ID, Principal,
managed session_id, binding and authority epoch/incarnation. This internal relation
is protected evidence, not a new field in the D05 OwnerContext or Principal body.
Context lifetime is min(authentication time + 300000, challenge expiry, managed
session expiry, qualified factor freshness deadline). Exclusive deadlines apply;
missing expiry/factor evidence denies. No sliding refresh, JWT renewal extension,
cross-challenge reuse or cross-restart use is allowed.

"Single use" means one consent lineage, not destruction before its own dispatch:
one terminal CONFIRM/DENY consumes the challenge's decision opportunity; at most
one linked receipt/grant/intent/claim lineage can use that context. The accepted
CONFIRM context may support its same lineage's rechecks until expiry, but cannot
authorize another challenge or a second claim. DENY retires the lineage. Atomic
consumption, durable tombstones and provenance are future N01/D03 requirements.

## Required current-context checks

All rows require exact protected Principal/session/challenge/binding membership,
unchanged owner/binding generations, current epoch/incarnation and local context
not retired/expired. D03/D04 and technical/task/Host/G1/G2 prerequisites still deny
positive use when missing. Remote evidence is not accepted from executor JSON.

| Stage | Required additional evidence and failure |
|---|---|
| page creation | Fresh qualified human login; direct remote session authentication; register the fixed server-rendered view from immutable challenge material. Failure produces no confirming view. |
| decision POST | Protected browser origin, CSRF and registered view checks; direct remote authentication of the same retained session; frozen material and deadline joins. Failure creates no trusted receipt. |
| receipt creation | Recheck local context under the serialized authority transition; require direct remote validation for this transition (a decision check may be reused only inside the same uninterrupted protected operation with a fixed evidence deadline); checkpoint before authority acknowledgment. |
| AdmissionIntent creation | Direct remote validation plus all eight current GateFacts, exact receipt/grant/scope and complete revocation state. No TTL-only positive result. |
| DispatchAttempt claim | New direct remote check for this claim; bind response evidence to exact operation/session/context; recheck protected generations, revocation and deadlines under serialization; complete independent witness before bounded handoff. No cached/local-JWT fallback. |

A validation failure, timeout, malformed response, mismatched user/session,
unqualified provider project, rate limit or missing protected response evidence
denies. Uncertain durable state quarantines. Evidence valid_until cannot exceed
any applicable deadline. If fencing consumes the deadline, retain consumption
and suppress handoff; do not extend the context or reissue a replacement attempt.
The local-to-provider claim race remains explicitly accepted, even when all these
checks succeed. Post-claim revoke cannot guarantee rollback of an external effect.

## Invalidation, custody and recovery

Nexus logout, observed account/session switch, Owner replacement, workspace/project
rebind, local revocation, generation change and epoch/incarnation change retire
affected contexts and unclaimed authority through the protected serialized ledger
and D03 witness. Local logout invalidation must win against later claims when it
linearizes first; browser cookie clearing alone is insufficient. During witness
uncertainty close the entire release gate. Restart retires all pre-restart contexts,
views and pending positive lineages; consumed nonces/claims remain consumed.

External logout is detected only when remote validation rejects the retained
session. Upstream federated logout and unobserved account/profile changes do not
promise instant invalidation. An externally switched browser may leave the old
session valid; protected N02 must visibly identify the enrolled Owner and require
the exact challenge confirmation. Account disable/deletion/merge semantics and
fresh factor policy still require isolated live qualification. External roles or
workspace membership are excluded from Nexus Owner authority.

Executor has proposal/status permissions only, never tokens, browser session,
provider admin/project secret, context/evidence writes, Owner enrollment, N02
origin or runtime/deployment/restore permissions. Stytch bearer values stay only
in protected runtime custody; canonical records contain protected evidence refs,
never tokens. D04 has no deployed exclusion proof and remains BLOCKED.

## D05 compatibility stop

The unchanged Principal requires exact verified issuer/client_id/subject semantics.
The selected remote response proves user/session within a configured project but
does not itself establish a qualified D05 issuer/client_id mapping. Do not infer
that project_id is an OAuth client_id or invent an issuer from an API hostname.
STYTCH_TO_D05_PRINCIPAL_MAPPING remains BLOCKED until the bounded Phase 4 review
and later qualification can prove it. No D05 body or public admission changes.

## Exact status

```text
D01_SELECTED_SESSION_PROVIDER = STYTCH_CONSUMER_SESSIONS_CANDIDATE
D01_EXTERNAL_IDENTITY_ROLE = MANAGED_IDENTITY_AND_POINT_TIME_SESSION_VALIDATION
NEXUS_OWNER_CONTEXT_MODEL = SHORT_LIVED_NON_REFRESHABLE_SINGLE_CHALLENGE
OWNER_CONTEXT_MAX_LIFETIME_MS = 300000
OWNER_CONTEXT_REFRESH_ALLOWED = NO
OWNER_CONTEXT_CROSS_RESTART_ALLOWED = NO
OWNER_CONTEXT_SINGLE_USE = YES
CLAIM_TIME_REMOTE_SESSION_RECHECK = REQUIRED
CONTINUOUS_EXTERNAL_LIFECYCLE_REQUIRED = NO
EXTERNAL_LOGOUT_INSTANT_INVALIDATION_REQUIRED = NO
LOCAL_NEXUS_INVALIDATION_REQUIRED = YES
CUSTOM_LIFECYCLE_BROKER_REQUIRED = NO
RESIDUAL_CHECK_TO_CLAIM_RISK = ACCEPTED
STYTCH_TO_D05_PRINCIPAL_MAPPING = BLOCKED
D01_BOUNDED_CONTEXT_DESIGN = DEFINED
D01_IDENTITY = BLOCKED
D01_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
REAL_ADMISSION_ENABLED = NO
GRANTS_REVOCATIONS_ISSUED = 0
PROVIDER_EXECUTIONS_ADDED = 0
FAIL_CLOSED_BOUNDARY = PRESERVED
```
