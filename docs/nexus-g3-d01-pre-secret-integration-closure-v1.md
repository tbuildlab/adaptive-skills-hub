# Nexus G3 D01 pre-secret integration closure v1

2026-10-08. Offline implementation and review at source checkpoint
`1ae954e2cf913013d28ca4c889002de1a99521e0`, branch
`nexus-v2-g3-live-qualification`. This additive closure preserves the historical
[pre-secret readiness result](nexus-g3-d01-pre-secret-readiness-closure-v1.md),
[Stytch adapter review](nexus-g3-d01-live-stytch-adapter-offline-review-v1.md), and
[live setup plan](nexus-g3-live-qualification-setup-plan-v1.md).

The diagnostic source assembly is LIVE_CAPABLE_BUT_HARD_DISABLED. Its code,
registration interface, native HTTPS parser, private Owner channel and deterministic
deployment source composition are complete for future qualification. The code
does not implement Nexus production authority. Identity provenance, actual provider
behavior, Vercel build/runtime enforcement and D04 effective exclusion remain
unqualified. No account, environment variable, credential or network service was
used. The supplied report about existing Vercel CLI/OIDC artifacts is
USER_REPORTED; those paths and values were not inspected.

## 1. Assembly and activation

The unchanged current deployment route remains
`api/diagnostic.js -> lib/http.js -> policy.js/adapter.js -> FAKE_DISABLED -> DENY`.
The original public assets, configuration, seven earlier diagnostic/test modules,
G3 authority source/contracts and historical documents retain their baseline bytes.

The future standalone source route is
`future-deployment/diagnostic-entry.js -> server/diagnostic-service.js`
with a fixed protected composition:

1. `deployment-input.js`: immutable server configuration; no discovery.
2. `pre-secret-policy.js`: two literal false compile gates, exact mode and generation.
3. `provider-registration.js`: closed reviewed registration, cloned/frozen records
   and per-deployment control. A `source: OWNER_REVIEWED` string is syntax, not
   proof of an Owner ceremony. Protected deployment custody must supply provenance.
4. `pinned-identity.js`: project/generation-bound reviewed public-key input.
5. `credential-custody.js`: exactly two prospective named server environment reads,
   only after the activation gates. No disk lookup, enumeration or fallback.
6. `stytch-transport.js`: typed six-operation protocol, fixed native HTTPS, signed
   identity check, direct session observation and sanitized projection.
7. `owner-channel.js`: one-use transient material envelope, separate HTML output.

Current configuration is `mode: FAKE_DISABLED`, `provider: null`, `keyset: null`,
`registration_generation: 0`, `deployment_revision: UNREGISTERED`. Both
`CODE_REVIEWED_LIVE_ENABLED` and `DEPLOYMENT_REGISTRATION_ENABLED` are false.
The factory returns the old disabled handler before credentials are read or
native IO is constructed. Missing/malformed credentials yield disabled operations;
failed identity or current-session checks retire the diagnostic context and deny.

Future activation requires a separately reviewed source revision changing both
gates, protected static `mode: D01_DIAGNOSTIC_LIVE_STYTCH`, `deployment_tier:
PRODUCTION`, exact stable HTTPS origin, matching deployment revision and
registration/application generation, reviewed registration/keyset and valid
protected Test credential custody. All of these are conjunctive. Credentials alone,
browser body/query/cookie/header, public JS, Preview/unknown environment, fake IO
and fixture objects cannot activate it. Changing the gates is not authorized here.
The runtime tier input needs independent deployment-policy evidence; it does not
authenticate itself. Owner must prohibit live Preview builds and validate that
policy before any later activation. Host checks also reject Preview domains.

Only the protected factory constructs the native protocol. The offline factory
requires WeakMap-branded synthetic registration, credential and IO handles. Its
IO script can only create in-memory events; external callbacks/network clients
cannot be substituted. Native construction ignores fixture input; there is no
HTTP promotion route. Fixture PASS always remains unqualified, authority NONE.

## 2. Native transport boundary

`node:https.request` is wired privately into the future native factory. It uses
HTTPS, `test.stytch.com:443`, matching TLS server name, certificate verification,
POST, `agent: false`, JSON request/Accept headers, and server-created Basic
authentication. No URL/query credentials, environment proxy interpretation,
redirects, generic fetch, retries, arbitrary URL/path/headers or SDK are used.
Only these fixed paths exist:

| Operation | Fixed POST path |
|---|---|
| EMAIL_OTP_SEND | /v1/otps/email/send |
| EMAIL_OTP_AUTHENTICATE | /v1/otps/authenticate |
| TOTP_CREATE | /v1/totps |
| TOTP_AUTHENTICATE | /v1/totps/authenticate |
| SESSION_AUTHENTICATE | /v1/sessions/authenticate |
| SESSION_REVOKE_EXACT | /v1/sessions/revoke |

Request maximum: 4,096 bytes. Response maximum: 65,536 bytes. Absolute call
timeout: 4,000 ms including streaming. Exact JSON content type, identity encoding,
bounded consistent Content-Length, fatal UTF-8 decoding, non-array object and
status_code 200 are required. JSON grammar rejects duplicate members, escaped
duplicate aliases and depth/node overflow before normal parsing; the same
precheck applies to signed JWT header/claims. Historical JWT verifier bytes remain
unchanged. Unsupported status, redirect, abort, error, malformed JSON and unknown
outcome deny and retire. Provider free-text, raw bodies, headers and exceptions
never become output. No automatic retry or broad-user revoke exists.

Offline tests replace the private request boundary with EventEmitter scripts,
exercise the same native event/response/parser path and install native HTTPS/fetch
traps. They open no sockets. Timeout fixture events test the failure path without
pretending to measure real DNS/TLS/provider latency. Real interoperability and
Node/Vercel network behavior require later separately authorized qualification.

## 3. Protected non-secret registration and identity seam

No actual provider ID is supplied or accepted during this run. The future Owner
input below is a **format template**, not a valid registration or authorization:

```json
{
  "provider": "STYTCH_CONSUMER",
  "environment": "TEST",
  "project_id": "<registered_project_id>",
  "owner_user_id": "<registered_owner_user_id>",
  "project_generation": 1,
  "application_generation": 1,
  "owner_generation": 1,
  "binding_generation": 1,
  "origin": "https://nexus-g3-qual.vercel.app",
  "factors": ["EMAIL_OTP", "TOTP"],
  "session_max_minutes": 15,
  "context_max_ms": 300000,
  "issuer": "stytch.com/<registered_project_id>",
  "audience": "<registered_project_id>",
  "deployment_revision": "<independently_reviewed_revision>",
  "source": "OWNER_REVIEWED",
  "review_id": "<protected_registration_review_reference>",
  "delivery_email": "<disposable_delivery_address>"
}
```

The existing field `project_id` represents registered_project_id; `owner_user_id`
represents registered_owner_user_id. `session_max_minutes=15` is 900,000 ms;
`context_max_ms=300000` is the non-refreshable diagnostic bound. This is the
existing closed registration format, not a silent body rename. Delivery email
is routing only, never identity. Source and review references require protected
Owner/admin custody; they cannot establish trust by textual assertion alone.
One registration is immutable within one worker/deployment. Owner/binding/project/
application/config change requires retiring the previous deployment and provider
sessions under separate authorization. No hot mutable admin API is added.

Candidate Principal semantics remain: issuer `stytch.com/<project_id>`, client_id
equal to the dedicated registered project/application candidate, subject equal
to native stable user_id. Provider session_id stays private contextual evidence;
opaque session_token stays server memory only. Existing D05 Principal and v1
canonical bodies are unchanged. Dedicated project-to-relying-party semantics,
actual signed issuer/audience/subject values, provider response/token behavior,
and key provenance require live evidence. Mapping is CONDITIONAL, not established
merely because a synthetic signed token passes.

The exact keyset registration schema is:

```text
source = OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET
project_id = exact registered Test project
application_generation = exact reviewed deployment generation
review_id = protected public-key provenance review reference
valid_from / valid_until = integer Unix milliseconds, valid now, <=24-hour window
keys = 1..8 public RSA JWKs with exactly kty/kid/alg/use/n/e
```

Limit: 16 KiB keyset, unique kid, RSA >=2048 bits, RS256 only, use sig. Public
keys are independently obtained/reviewed by the Owner outside the executor;
there is no guessed OIDC issuer URL, fetched endpoint, browser key URL, arbitrary
key source, TOFU, discovery or private-key input. Project/generation/time mismatch,
expired pin or missing/ambiguous kid denies. The runtime wires this interface to
the existing signature/issuer/audience/subject verifier. Actual provider-origin
public-key provenance and rotation remain CONDITIONAL. No JWKS network call ran.
A local valid JWT is never sufficient: every positive session observation requires
direct SESSION_AUTHENTICATE in the future native mode.

## 4. Factor lifecycle and five-point diagnostic flow

The server obtains OTP destination/method and primary native user/session from
its registered deployment and typed response only. Initial OTP authenticate requests
15 minutes. TOTP enrollment performs direct session checks before and after,
creates a private one-use envelope, and does not extend the Nexus deadline. TOTP
authentication carries the retained session token and checks exact user/session/
token/primary-factor lineage; contradictory or stale factors retire. Its 15-minute
provider ceremony parameter does not extend the existing diagnostic deadline.
Later SESSION_AUTHENTICATE requests contain only retained session_token, no
duration/extension. Provider refresh/rotation incompatible with exact retained
lineage denies, rather than weakening that rule to obtain success.

The handler permits PAGE, DECISION_POST_SIMULATION, RECEIPT_SIMULATION,
INTENT_SIMULATION and CLAIM_SIMULATION in exact order. Each label calls a fresh
direct session check; these labels create no receipt/grant/intent/claim or authority
record. A complete label flow is terminal except exact test-session revocation.
Provider error/negative/revoked/unknown evidence never becomes positive output.

One private page cookie and CSRF bind each operation; Host, origin, same-origin
mutation, exact path/content type/closed body and bounded input checks are enforced.
OwnerContext expiry is the minimum of page-creation+300,000 ms, primary-factor
authentication+300,000 ms, provider expiry and any later shorter factor bound.
Reload/enrollment never extends it. Timer retirement clears idle server custody;
request checks also enforce expiry and monotonic time. Clock rollback clears all
local pages. Local logout/switch/cancel retires server custody; exact revoke is a
separate future provider mutation. Restart/worker loss/missing cookie state denies;
there is no rehydration or storage. Worker affinity is not assumed. Vercel worker
changes may reduce availability, never restore a missing page or authorize it.

## 5. Owner-only transient channel

The Owner display is a protected same-origin POST form to the **same diagnostic
function**, with exact action OWNER_TOTP_DISPLAY and transient CSRF. It requires
the server's already authenticated primary Owner session, page cookie, current
registration and another direct remote check. It returns separate one-use HTML,
not diagnostic evidence JSON. Raw seed/QR/recovery provider fields are cleared
even when response validation/post-check fails. Server envelope is consumed once.

Manual seed enrollment makes QR NOT_NEEDED; no QR service, clipboard, analytics,
storage or third-party script is used. Seed/recovery text is escaped. HTTP uses
no-store, no-referrer, nosniff, frame denial and CSP self-only script/connect/form.
No secret enters a URL/query. Diagnostic JSON can carry CSRF/expiry transport
metadata, but its evidence projection omits bearer material and native identifiers.
Cookie is Secure/HttpOnly/SameSite Strict and never projected as evidence.

Owner browser JS removes transient DOM/input/meta material **before** enrollment
submit/cancel, and on deadline, pagehide/unload/visibility change. Failed requests
retain no displayed seed; server retirement handles failure/unknown outcome. Success,
failed enrollment, local logout/switch/cancel, timeout and context retirement clear
server material; worker loss destroys in-memory custody. Browser destruction on
its local deadline does not depend on a surviving worker. There is no guarantee
of JavaScript heap zeroization or revocation of an Owner's manual copy. This is
ephemeral operational handling, not proof against a compromised Owner device.
No actual TOTP secret was generated, displayed or enrolled in this run.

## 6. Deployment source artifact and MANIFEST

[verify_deployment.py](../diagnostics/g3-d01-rp/scripts/verify_deployment.py) builds
only a fixed 19-file standalone diagnostic source closure under ignored validation
state. Destination/source mapping is:

- Eight `lib/server/` modules listed in section 1, including credential-custody.js.
- Five `lib/` modules: policy.js, http.js, adapter.js, stytch-identity.js,
  stytch-projection.js.
- `api/diagnostic.js` from future-deployment/diagnostic-entry.js.
- `public/index.html`, `public/app.js`, `public/owner-transient.js` from their
  future-deployment counterparts.
- package.json and vercel.json from future-deployment.

The private ESM package uses the existing Node 24 profile, no dependency install,
build script or downloaded SDK. Future config names one function, maxDuration 30,
public output and security headers; the original current maxDuration 5 config is
unchanged. Actual account plan/runtime support for that duration is unverified
and must be checked by the Owner later. An unsupported host configuration blocks
activation; it is never worked around by weakening time/identity checks.

The verifier checks bounded files, no symlink/reparse/escape, deterministic LF bytes
and fixed-time sorted ZIP, exact static dependency closure and zero authority
imports. It rejects extra artifact members (including synthetic .env) without
reading their contents, scans selected source values and metadata, and runs the
composed entrypoint with a native network trap. It reads only this explicit source
inventory, never the local deployment directory, environment files, .vercel or
account/OIDC artifacts. Repeated source ZIP hashes match. No real env/token/secret,
state, Route D, tests, raw evidence or Nexus authority code is packaged.

Repository MANIFEST is authoritative for the **existing repository package**;
it is not used by this new standalone diagnostic source artifact. The accepted
SENSITIVE_TOKENS path rule and packager are byte-preserved. Credential-named
source remains excluded from the repository package; this exclusion is intentional
and non-blocking only for the separately reviewed diagnostic deployment source.
No file was renamed or broadly allowlisted. A repository package alone must not
be represented as this complete deployment source.

D01_DEPLOYMENT_ARTIFACT=VERIFIED_OFFLINE means deterministic reviewed **source
composition and disabled entrypoint**, not a Vercel-built function artifact,
deployed client/function trace, effective permissions or provider qualification.
Provider build/deploy are NOT_RUN. The future Owner-controlled build must retain
function/client trace evidence proving the fixed source closure and absence of
bundled runtime secrets/server code in public assets before separately authorized
live use. These are external qualification gates, not presumed passed here.

## 7. Custody readiness and remaining gates

The [additive custody integration runbook](nexus-g3-d01-secret-custody-integration-runbook-addendum-v1.md)
defines the future Owner sequence. Current Windows/Codex execution, reported
Vercel CLI authentication and generated local OIDC artifact do not establish an
independent custody domain. This machine and its browsers/CLI/filesystem are
explicitly forbidden for Owner secrets. No credential-bearing path was opened.
D04 remains BLOCKED; pre-secret custody is CONDITIONAL_OWNER_DEVICE_REQUIRED.

The in-memory dry-run models Owner set -> redeploy -> server-only runtime ->
rotation -> cleanup, using only OFFLINE_SENTINEL values. Sentinel tests check
client JS/HTML, JSON, headers, logs, evidence, exceptions and artifact metadata.
This proves fixture/source non-export behavior, not Vercel secret lifecycle or
deployed isolation. Old deployments may retain old values; future cleanup needs
issuer rotation/revocation plus independently verified deployment retirement.

READY_FOR_SECRET_CUSTODY_SETUP=YES has the exact requested **pre-secret technical
preparation** meaning: no remaining local CODE/source DEPLOYMENT composition gap
requires reading a secret to resolve. It permits no credential access, account
mutation, deployment or live test. It does not approve the current machine or
claim Owner/device/provenance/effective-permission qualification. Actual secret
entry stays HOLD until the Owner supplies a separate authorization and verifies
independent device/account/deployment exclusion. Stop if that cannot be proved.

Remaining Owner-only gates are: independently controlled device/account roles,
invalidation of executor-accessible deployment/OIDC rights; disposable Test
project/native-user registration and public-key provenance; actual Vercel build/
duration/security trace review; private Production-only credential entry and old
deployment retirement under separate authorization; then separately reviewed
activation/live-test authorization. Stytch issuer/audience/session/factor behavior
needs disposable live observation. Full D04 effective denial tests, D03/AWS and
production N01/N02/admission remain outside this slice. No weaker test substitutes
for those gates.

## 8. Exact change scope and validation

Modified: MANIFEST.json and four server modules: credential-custody.js,
pre-secret-policy.js, provider-registration.js, stytch-transport.js.

Added: five server modules (custody-dry-run.js, deployment-input.js,
diagnostic-service.js, owner-channel.js, pinned-identity.js); six future-deployment
files (app.js, diagnostic-entry.js, index.html, owner-transient.js, package.json,
vercel.json); scripts/verify_deployment.py; tests/integration.test.js; this document
and the custody integration runbook addendum. All diagnostic paths above are
under diagnostics/g3-d01-rp/. Twenty exact files comprise the checkpoint slice.
Three preexisting unrelated Route D documents remain untracked and unstaged.
Ignored state evidence and generated ZIP/source are excluded from the commit.

Final command evidence is retained only under ignored
`state/g3-d01-integration-20261008/`. Validation commands (repository root unless
noted) and results:

| Command | Result |
|---|---|
| `node --test tests/integration.test.js` (diagnostic directory) | 57 PASS |
| `node --test tests/model.test.js tests/http.test.js tests/boundary.test.js tests/stytch-adapter.test.js tests/stytch-boundary.test.js tests/pre-secret.test.js` (diagnostic directory) | 157 PASS |
| All seven diagnostic test files together | 214 PASS |
| `D:\DevTools\NexusR2Python\Scripts\python.exe -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge` | 134 PASS |
| Same Python, `-B -m unittest tests.test_ecosystem_isolation_package`, accepted isolated source snapshot with PYTHONDONTWRITEBYTECODE=1 | 11 PASS |
| Same Python, `-B diagnostics/g3-d01-rp/scripts/verify_deployment.py --output state/g3-d01-integration-20261008/artifact` | 19-file source closure PASS; composed entrypoint disabled; network 0 |
| Same Python, `-B state/g3-d01-integration-20261008/verify_integration.py` | Scope, baseline, secret scan, JS syntax, import graph, deterministic MANIFEST PASS |
| `git diff --check` and staged equivalent | PASS |

The 48 requested adversarial cases plus nine integration/duplicate-member/
destruction/construction cases are covered. One new browser-mock assertion initially
ran before its async callback settled; awaiting the callback fixed the test harness,
without changing product checks or weakening prior tests. Artifact import checking
was corrected to examine actual anchored static declarations rather than prose.
No guard, old test or sensitive-path rule was relaxed. Baseline audit preserves
389 preexisting non-slice paths, including all prior tests and unrelated files;
403 deterministic MANIFEST entries retain all old entries except three explicitly
modified source hashes. Main/development refs remain unchanged. Static scanning
is a bounded source/staged-value check, not a credential discovery exercise or
proof about uninspected external files.

## Final fields

```text
D01_SERVER_ASSEMBLY = DEFINED
D01_NATIVE_HTTPS_TRANSPORT = IMPLEMENTED_DISABLED
D01_CREDENTIAL_SOURCE_PACKAGING = DEFINED
DEPLOYMENT_REQUIRES_MANIFEST = NO
MANIFEST_SENSITIVE_RULE = UNCHANGED
D01_PROVIDER_REGISTRATION_RUNTIME = DEFINED
D01_JWKS_RUNTIME_SEAM = CONDITIONAL
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL
D01_FACTOR_FLOW_ASSEMBLY = DEFINED
D01_TOTP_OWNER_CHANNEL = DEFINED
D01_LIVE_ACTIVATION_CONTRACT = DEFINED
D01_DEPLOYMENT_ARTIFACT = VERIFIED_OFFLINE
D04_PRE_SECRET_CUSTODY = CONDITIONAL_OWNER_DEVICE_REQUIRED
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
NETWORK_CALLS_PERFORMED = 0
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
VERCEL_SECRET_ACCESS = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
READY_FOR_SECRET_CUSTODY_SETUP = YES
READY_FOR_D01_LIVE_AUTHORIZATION = NO
```
