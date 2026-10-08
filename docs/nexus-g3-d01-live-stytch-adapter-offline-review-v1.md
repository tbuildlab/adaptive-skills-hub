# Nexus G3 D01 live Stytch adapter offline implementation review v1

Date: 2026-10-08. OFFLINE IMPLEMENTATION AND REVIEW ONLY.
Repository: `D:\chatgpt\安装skills\adaptive-skills-hub`.
Branch: `nexus-v2-g3-live-qualification`.
Starting/ending HEAD: `844f8d095b5786e3575df0c93d3f225a666b5012` (no commit).

Inputs: [accepted diagnostic shell](nexus-g3-d01-diagnostic-rp-implementation-review-v1.md),
[setup plan](nexus-g3-live-qualification-setup-plan-v1.md),
[Stytch Principal closure](nexus-g3-u1-stytch-principal-closure-v1.md),
[bounded context](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md),
[D04 exclusion](nexus-g3-u1-d04-executor-exclusion-and-mediated-dispatch-v1.md).
The [deployment observation](nexus-g3-d01-owner-reported-disabled-deployment-v1.md)
records Owner-reported disabled labels only; no visit or provider action occurred.

## Outcome and exact scope

Six narrow operation protocols, private synthetic session custody, same-lineage
checks, response projection and RS256 identity verification are implemented and
tested offline. IMPLEMENTED_OFFLINE covers this protocol seam, not an operational
live HTTP client. The future live constructor always returns disabled denials;
there is no network transport or credential loader. Current deployed import graph,
HTML/JS/CSS, default adapter, config, package/dependencies and 51 existing tests are
unchanged. No native Owner registration was accepted and no D05/v1 body changed.

The guarded protocol implementation is exercised only by an in-memory fixture
transport. Its output is OFFLINE_ADAPTER_FIXTURE / qualified_live=false, despite
signed synthetic identity or PASS results. No live evidence is manufactured.

## Exact changed files

| File | Responsibility |
|---|---|
| `diagnostics/g3-d01-rp/lib/stytch-live-adapter.js` | Six-operation protocol/state machine, disabled prospective live constructor, closed fixture transport and private custody |
| `diagnostics/g3-d01-rp/lib/stytch-identity.js` | Bounded native Node RS256 verification against protected public keys; no discovery or signing service |
| `diagnostics/g3-d01-rp/lib/stytch-projection.js` | Typed Session/User/factor projection, UTC timestamp normalization, closed evidence/error output |
| `diagnostics/g3-d01-rp/tests/stytch-adapter.test.js` | 34 requested contract cases plus lineage, enrollment, lifecycle and signed-identity adversaries |
| `diagnostics/g3-d01-rp/tests/stytch-boundary.test.js` | Import, hard-gate, credential-getter, fake-promotion, deployed-entrypoint and no-network checks |
| `docs/nexus-g3-d01-owner-reported-disabled-deployment-v1.md` | Secret-free report; no independent deployed qualification |
| `docs/nexus-g3-d01-live-stytch-adapter-offline-review-v1.md` | This review and readiness blockers |
| `MANIFEST.json` | Existing accepted regeneration mechanism adds seven new eligible files |

No framework/library/package changes, .env files, dependency install, live SDK,
authority engine, credential manager, database, custom IAM/OAuth/PKI or telemetry
are introduced. Node crypto verifies only the pinned Stytch RS256 profile. Test
signing keys are newly generated in process memory and never exported as private
key material, written to a file or installed as a trust authority.

## Documented provider contracts and deliberate restrictions

All URLs are fixed to **https://test.stytch.com**; all operations are POST with
JSON, fixed server-only authentication seam, timeout 5000 ms, redirect=error and
retry=NEVER. The fixture sends only a synthetic Basic header built from an invalid
test placeholder, never a credential from the environment. No browser-selected
URL, method, route, project, user, credential, duration, custom claim or redirect
is accepted by any operation.

| Narrow operation | Fixed path/body and protected evidence |
|---|---|
| sendEmailOtp | `/v1/otps/email/send`; registered disposable email, expiration_minutes=5, locale=en; returned native user must match registration; retain email_id as method ID privately |
| authenticateEmailOtp | `/v1/otps/authenticate`; retained method_id, transient six-digit code, session_duration_minutes=15; same user and method, signed identity and one fresh email factor; retain exact opaque token/session privately |
| startTotpEnrollment | Direct session recheck, then `/v1/totps` with retained native user_id and expiration_minutes=5, then another direct session recheck; expose no seed/QR through evidence |
| authenticateTotp | Direct primary-session recheck then `/v1/totps/authenticate`; retained user_id/token, transient totp_code, fixed session_duration_minutes=15 during initial ceremony only; require same native user/session/token and unchanged email-factor time |
| authenticateSession | `/v1/sessions/authenticate`; **only retained session_token**; no duration, JWT-only argument, custom claims or telemetry; new exchange at each ordered observation point |
| revokeSession | `/v1/sessions/revoke`; **only retained session_id**; no caller argument, broad-user revoke or alternate session; clear custody and terminally retire after acknowledgment |

Request shapes derive from official [email send](https://stytch.com/docs/api-reference/consumer/api/otp/via-email/send),
[OTP authenticate](https://stytch.com/docs/api-reference/consumer/api/otp/authenticate),
[TOTP API source](https://github.com/stytchauth/stytch-python/blob/main/stytch/consumer/api/totps.py),
[session authenticate](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session)
and [session API source](https://github.com/stytchauth/stytch-python/blob/main/stytch/consumer/api/sessions.py).
No example credential/code/user from documentation is copied into implementation.

Email uses send rather than login-or-create; user/session arguments that can attach
a new email are omitted. Email is a registered delivery destination, not Owner
authority. Test fixtures use example.invalid and synthetic IDs only. Project labels
P_OWNER/P_OTHER, email/name/external_id/metadata cannot substitute for native-ID
equality. U_NONOWNER and foreign-project identity deny even if authenticated.

**TOTP create has no session-token parameter.** Provider source supports user_id
and expiration_minutes only. The adapter does not invent an unsupported parameter
or claim that create is atomically bound to the retained session. Exact user and
pre/post remote-session checks provide the proposed point-time composition;
revocation/switch between checks remains possible. This is CONDITIONAL for actual
deployment semantics and must be qualified, not promoted by fixture success.

The initial TOTP ceremony may set the same provider session to 15 minutes from
that operation, as documented; it never extends the local context deadline.
Repeated ceremony requests are rejected. After two-factor verification, a changed
session expiry, token, factor identity or authentication time denies rather than
silently refreshing or adopting a different session. Actual static-token continuity
and Session return behavior require live qualification; mismatches remain blocked.

## State, context and error behavior

Closed protocol states: SIGNED_OUT -> EMAIL_PENDING -> PRIMARY_VERIFIED -> optional
ENROLLMENT_PENDING -> TWO_FACTOR_VERIFIED -> OBSERVATIONS_COMPLETE, or terminal
RETIRED/REVOKED. Unrecognized state jumps, duplicate authentication, broad revoke,
missing registration or invalid operation input deny. Only one async operation is
in flight; overlapping requests receive BUSY and cannot create a second lineage.

Context expiry is initialized from the email factor's timestamp + 300000 ms or
provider expiry, whichever is earlier. TOTP may only shorten it. Deadline checks
occur before and after each operation; exactly at expiry denies and clears custody.
Rechecks occur in PAGE -> DECISION_POST_SIMULATION -> RECEIPT_SIMULATION ->
INTENT_SIMULATION -> CLAIM_SIMULATION order, each consuming its own new exchange.
No cached result/JWT can satisfy the next label, and no real corresponding authority
record is created. Restart destroys the private object; no persistence/restore API
exists. Clock regression retires. The five-minute bound is not a substitute for
remote recheck, and it does not eliminate the accepted external lifecycle race.

Provider 429, 5xx, negative status, timeout, unknown envelope, malformed body,
expired session, missing/stale/duplicate/unexpected factors or identity mismatch
deny and retire. No retry, fallback, exception object/message/stack serialization
or automatic revoke is performed. A failed or unknown revoke drops local custody
without asserting issuer revocation; later Owner-controlled cleanup is separate.
Elapsed fake exchange >=5000 ms denies. Real transport cancellation/deadline/body
bounds are still a future transport requirement, not tested network enforcement.

## Principal, signature and factor validation

Preserve existing CONDITIONAL Principal `{issuer, client_id, subject}`: exact native
`stytch.com/<registered_project_id>`, exact dedicated project audience/application
candidate, native user_id matching signed sub and remote Session/User. The provider
[JWT helper](https://github.com/stytchauth/stytch-python/blob/main/stytch/shared/jwt_helpers.py)
uses RS256 and those native project semantics; this profile rejects its alternate
base-URL issuer. Project/application registration remains a live qualification gate.

Identity verifier accepts only RS256, a single registered kid, RSA public signing
key >=2048 bits, exact issuer/audience/subject, required exp/iat/nbf, unexpired time
and JWT age <300 seconds. Multi-audience, unknown/duplicate kid, algorithm/key URL
injection, future time or missing signature fails. Singleton audience arrays are
accepted without broadening audience. No jti-to-session assumption or invented
OIDC discovery URI is made. Keys are protected input, never downloaded here;
exact JWKS endpoint/project registration, provenance, rotation and freshness remain
future qualification/transport requirements. Signed identity never overrides a
negative direct remote-session observation.

Typed remote projection joins User.user_id and Session.user_id/session_id; optional
top-level user_id must agree, and OTP/TOTP responses require it. Native User must
be active and explicitly not locked. Optional raw project_id, if present anywhere
in the identity join, must agree. Missing/changed fields fail closed. No external
role/workspace entitlement is read. Only email OTP (`otp`/`email_otp` with email
delivery) and TOTP with authenticator_app delivery are accepted, based on provider
[factor definitions](https://github.com/stytchauth/stytch-python/blob/main/stytch/consumer/models/sessions.py).
Each required factor appears exactly once, has a valid UTC timestamp and is fresh;
factor order is normalized. UTC fractional precision is floored to milliseconds,
never rounded to extend a deadline; invalid dates/offsets are denied.

## Secret custody and output boundaries

No STYTCH_SECRET/Vercel secret/environment/file is read. Prospective live factory
does not inspect its config/secret-interface arguments, even poisoned getters;
every narrow method returns FAKE_DISABLED denial. The separate offline constructor
requires an authentic in-memory fixture transport, TEST registration and
example.invalid delivery destination. A lookalike SDK/client or injected fake with
mode text cannot be promoted. It accepts only explicit OFFLINE_ token/seed placeholders
and synthetic signed JWT/key fixtures, never an operational credential path.

The future secret interface remains the accepted server-only STYTCH_PROJECT_ID /
STYTCH_SECRET names; no frontend SDK/public token is added. An eventual real loader,
transport and registration source require separately reviewed code and protected
custody. Token/JWT live values would stay in excluded volatile server runtime;
the adapter stores no raw JWT, and the current fixture token is a private field.
Object JSON serialization reveals only diagnostic labels/denial. Opaque tokens,
JWT bytes, Basic headers, codes and raw responses never enter diagnostic evidence.

TOTP create raw secret/QR/recovery placeholders are validated then delivered only
to a protected-consumer analogue after successful pre/post checks. They are never
returned in result JSON. Shared transient/raw fields are cleared in finally; the
consumer is dropped after authentication/retirement. JavaScript immutable strings
cannot be guaranteed securely zeroized, and an actual trusted consumer must not
copy/persist/log them. There is no real Owner enrollment display, browser storage,
seed generation or QR rendering in this version. Real transient display needs an
Owner-controlled same-origin surface and an independent custody review.

Evidence allows only fixed labels, OFFLINE_ADAPTER_FIXTURE, result/error enum,
bounded UUID request_id, fixed project/user/session aliases, normalized factor
types/timestamps/freshness, observation start/end, context expiry, observation point
and positive Owner/binding generations. Unknown fields and malformed request IDs
are dropped; raw response input is not an operation, and token strings cannot replace
typed input. No OTP/seed/cookie/header/env/stack/raw object is exposed. This projector
does not add fields to canonical G3/D05 bodies. Transport-shape introspection is
fixture-only, never reachable from a page/evidence/export endpoint.

## Live selection and deployment preservation

Both current policy gate and new LIVE_ADAPTER_BUILD_ENABLED remain false. Current
api/diagnostic -> http -> policy/default adapter graph never imports these new
modules. Browser flags, environment secret presence, adapter mode strings and fake
fixture results cannot activate live operations. No generic request method, provider
route input, OAuth/auth product, credential loader, HTTP fetch/SDK fallback,
runtime debug endpoint or effect/authority path is introduced.

Future activation requires an explicit Owner-reviewed source/config revision,
protected server transport/credentials/registration/public-key provenance, complete
factor/continuity tests, exclusion evidence and separately authorized action IDs.
No flag is set true, no Vercel redeploy occurs and no active deployment is visited.
The Owner's existing shell report is recorded only as OWNER_REPORTED_DEPLOYMENT_OBSERVATION.

## Offline verification and review findings

| Exact command / location | Result |
|---|---|
| `node --test tests/stytch-adapter.test.js tests/stytch-boundary.test.js` in diagnostics/g3-d01-rp | PASS, 56 adapter/boundary tests; 34 requested numbered cases included |
| `node --test tests/model.test.js tests/http.test.js tests/boundary.test.js` there | PASS, all 51 existing diagnostic tests, unchanged |
| `node --test tests/*.test.js` there | PASS, 107 total Node tests |
| `python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge` at repo root | PASS, 134 existing G3 tests |
| `python -B -m unittest tests.test_ecosystem_isolation_package` in isolated manifest-source snapshot | PASS, 11 package/isolation tests |
| `python -B state/g3-d01-stytch-adapter-offline-20261008/verify_adapter.py` at repo root | PASS, final fields, source preservation, syntax/import boundary, bounded secret scan and deterministic manifest |
| `git diff --check` plus new-file whitespace scan | PASS |

Python executable: D:\DevTools\NexusR2Python\Scripts\python.exe; bytecode disabled.
Node: v24.18.0. Original tests/guards are not edited. New tests never create a socket
or HTTP client and use synthetic request/response/key data only; injected global
fetch/credential getters prove the inactive path performs zero calls/reads.
No real Stytch, OTP, factor, session or revoke operation is executed.

Review corrected response-shape assumptions (session authenticate need not have
top-level user_id), missing lock evidence, revoke terminal acknowledgment handling,
typed factor redaction, independent verifier registration checks and UTC fractional precision. TOTP create session binding
is explicitly restricted to pre/post point-time checks, with its remaining race
reported. These are new-module corrections; no accepted canonical body or guard
is weakened. Review PASS is bounded to the offline protocol implementation.

Baseline preservation covers 377 pre-existing non-manifest paths, including all
13 accepted shell files, prior 51 tests, G3 contracts/production fail-closed code,
accepted documentation and three unrelated untracked Route D documents. Main,
development and HEAD remain unchanged. The sole tracked edit is MANIFEST.json;
seven new files are listed above. Existing builder/policy regenerates 380 entries
from 373 accepted entries plus these seven, deterministic and old entries unchanged.
Sensitive-path exclusions are not relaxed. Ignored audit/fixture snapshot artifacts
stay outside the commit/package scope; nothing is staged or committed.

## Remaining blockers and Owner next action

Owner may review the code and a **names-only secret-custody plan**. Do not yet inject
real secrets or enable/authorize live diagnostics. READY_FOR_SECRET_CUSTODY_SETUP=NO
because actual Owner/device/deployment/token/log custody and effective exclusion
have not been established. The disabled shell's ordinary-browser report is
insufficient for that permission boundary.

Exact remaining gates:

1. Independently register native project/user/application/environment IDs and
   qualified Owner binding. Fixture IDs/mailboxes are not real registration.
2. Establish excluded Owner browser/device and Stytch/Vercel admin/secret/volatile
   token/telemetry custody; qualify D04 surfaces and alternate routes. No effective
   Vercel/Stytch permissions or external lifecycle proof exists here.
3. Review a real server-only credential loader, bounded pinned-Test transport with
   redirect/retry/body/cancellation rules, provenance/freshness-controlled JWKS,
   and Owner-controlled ephemeral factor surface. They are not implemented by
   fixture transport and must never adopt test fixtures as live evidence.
4. Separately authorize deployment/config selection and exact disposable login,
   OTP/TOTP/session/revoke tests, mutations and limits from the setup plan. No
   existing report, code PASS or stored secret supplies this authorization.
5. Live tests must resolve dedicated project/application Principal semantics,
   actual same-session/token/factor/expiry behavior, TOTP-create race composition,
   Test-mode genuine human authentication and lifecycle invalidation. Preserve
   CONDITIONAL/BLOCKED if any cannot be established; no D05 relabeling.

No real receipt/grant/revocation authority, AdmissionIntent, DispatchAttempt,
provider dispatch/effect release or positive real admission path exists. Public
fail-closed behavior remains unchanged. No commit/push/merge/tag/freeze/release,
cloud/account/policy mutation, credential access or redeployment was performed.

```text
D01_LIVE_STYTCH_ADAPTER_CODE = IMPLEMENTED_OFFLINE
D01_LIVE_STYTCH_ADAPTER_REVIEW = PASS
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
OWNER_REPORTED_DISABLED_DEPLOYMENT = VERIFIED_AS_REPORTED
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
READY_FOR_SECRET_CUSTODY_SETUP = NO
READY_FOR_D01_LIVE_AUTHORIZATION = NO
```
