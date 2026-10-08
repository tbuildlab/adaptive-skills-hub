# Nexus G3 D01 pre-secret readiness closure v1

2026-10-08. OFFLINE implementation and review only.
Branch: nexus-v2-g3-live-qualification. Starting checkpoint:
`f66da1364f43d20d3cb0c702cc2e0a64441c7d10`.

Inputs: [accepted adapter review](nexus-g3-d01-live-stytch-adapter-offline-review-v1.md),
[diagnostic shell review](nexus-g3-d01-diagnostic-rp-implementation-review-v1.md),
[Principal closure](nexus-g3-u1-stytch-principal-closure-v1.md),
[bounded context](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md),
[D04](nexus-g3-u1-d04-executor-exclusion-and-mediated-dispatch-v1.md).
Historical records and canonical v1/D05 bodies are unchanged. No network request,
provider credential/config read, login, session mutation, deployment or admission
occurred. Existing disabled deployment was not visited.

## Outcome and classification limits

Transport, credential-interface, closed registration and transient UI preparation
are defined and covered by offline adversaries. **Secret-custody readiness remains
NO.** Current executor exclusion has not been established. The request's local
Vercel CLI/OIDC artifact is reported evidence of a custody concern, not proof of
its permissions or isolation. No independent Owner device or effective dashboard,
deployment, environment, logging or Stytch admin separation has been demonstrated.

DEFINED below means closed source/design preparation, not native network operation,
deployed isolation or successful real factor authentication. There is no live
server assembly. Current factories always return FAKE_DISABLED; even a future
gate change would not silently assemble a live path. The native HTTPS primitive,
protected registration loader/current-context source, keys and Owner handoff must
be separately reviewed and connected before any credential use. No fake is that
assembly. The server registration predicate validates syntax only; a string
OWNER_REVIEWED is not an Owner ceremony or trust proof.

## Phase 1: fixed protected transport

The new server module has six named operations only: EMAIL_OTP_SEND,
EMAIL_OTP_AUTHENTICATE, TOTP_CREATE, TOTP_AUTHENTICATE, SESSION_AUTHENTICATE and
SESSION_REVOKE_EXACT. Private body construction pins the previously reviewed Test
POST paths; caller URL/endpoint/method/project/duration/custom claims reject.
HTTPS hostname/servername=test.stytch.com, port=443, certificate verification=true,
no proxy agent, no redirect follow and no retry. Credential is only in a privately
constructed Basic header, never URL/query or output. Explicit request bound=4096
bytes; response bound=65536 actual bytes including streaming, UTF-8 JSON only,
no compression, verified declared length if present. Unsupported material denies.

A private native Node HTTPS implementation installs an absolute 4000 ms timer
covering DNS/TLS/upload/body, aborts on failure, bounds streaming before parsing,
and closes 3xx/unknown/auth/429/5xx/network/TLS/timeout errors. It is not invoked by
any factory or route in this build. Offline IO is a WeakMap-branded literal queue,
not an injectable callback/network client; synthetic failures exercise parsing and
classification. Socket cancellation, TLS/DNS behavior and real enforcement are
**UNVERIFIED**; static preparation is not a native-IO test. No SDK/dependency was added.

The synthetic protocol reuses accepted Session/factor and RS256 verifiers, checks
same project/user/session/token, current registration generations on each operation,
and an absolute non-refreshable 300000 ms context. Initial OTP/TOTP duration=15
minutes; direct rechecks omit duration/custom claims. TOTP create is guarded by
pre/post session checks, not an invented provider atomic lease. After TOTP auth,
another fresh remote-session exchange is mandatory in the offline protocol. The
accepted check-to-use race remains. Broad user revoke is absent. Unknown failures
retire, wipe best-effort local custody, and never trigger automatic issuer cleanup.

## Phases 2–4: credential custody and registered identity

The server-only loader has exactly two named prospective environment reads:
STYTCH_PROJECT_ID and STYTCH_SECRET. Both occur only after closed code/config gates;
no environment value is read here. No enumeration, profile/CLI/home search, disk
reader, dotenv, Vercel OIDC/bypass use, logging, fallback or secret hashing exists.
Handles serialize a fixed denial and provide no getter. Basic-header application
only accepts pinned HTTPS request options. Fixture custody accepts only an explicit
OFFLINE_CREDENTIAL_PLACEHOLDER, never provider-shaped values. Missing/malformed
inputs deny; getters are not invoked. Lifetime is one volatile context, disposed
at retirement; no cross-worker/persistent cache. Immutable JS strings cannot be
guaranteed zeroized. Actual Vercel runtime memory/log custody remains unverified.

The closed non-secret model registers provider/environment, exact native project
and Owner user, project/application/Owner/binding generations, fixed origin, factor
set, 15-minute provider bound, 300000 ms context, issuer/audience, deployment revision,
independent review reference/source and separately registered email delivery address.
Delivery email is never principal authority. No first-login enrollment, display-label
ID, metadata or external_id is accepted. Protected review/current-control provenance
must later come from the independent Owner context; browser input cannot register it.
P_OTHER/U_FOREIGN remain negative fixtures. Synthetic controls can invalidate a
generation while a context exists; the next operation denies before IO.

Principal compatibility remains **CONDITIONAL**: native issuer
stytch.com/&lt;exact registered project_id&gt;, the exact project audience conditional on
its dedicated Nexus application semantics, native user_id matched to signed sub
and remote Session/User. This uses the accepted documentary provider-source evidence;
no new network research or OIDC capability is invented. Session ID is protected
context evidence, not subject/client; token is private volatile bearer. Reuse of
RS256 public-key validation requires pinned project/key provenance, freshness and
rotation qualified later. No JWKS URL/discovery is guessed or fetched. JWT-positive
and remote-negative denies. Local signature verification is not lifecycle proof.

## Phase 5: transient Owner UI preparation

The future-owner-ui directory is outside current public output and import graph.
It contains an explicitly disabled HTML surface and a DOM controller, no third-party
scripts, QR service, analytics, clipboard, storage or network request. The default
constructor cannot display material. The offline constructor admits only synthetic
primary-factor context with exact project/user/session/generations/worker and a
bounded absolute deadline. It displays OFFLINE_ manual seed/recovery placeholders
using textContent, never HTML injection or URL data, and accepts a six-digit
transient confirmation input. A local QR renderer is NOT_NEEDED for manual entry.

Success/deny/timeout/logout/switch/reload/pagehide/visibility change/worker loss and
mismatch clear retained nodes/input/placeholder references and listeners. Enrollment
does not extend the deadline. Confirmation returns DENY/PROTECTED_REMOTE_RECHECK_REQUIRED,
never proof of real TOTP authentication. Restored/mismatched worker context denies.
The real protected server-to-Owner handoff, cookies/CSRF/context provenance and
factor display are absent and BLOCKED pending assembly and independent custody.
Current deployed controls remain disabled; no real secret can enter the staged UI.

## Phases 6–7: redaction and deployment boundary

Closed errors include AUTH_REJECTED, SESSION_INVALID, RATE_LIMITED,
PROVIDER_UNAVAILABLE, TIMEOUT, MALFORMED_RESPONSE and UNKNOWN. Only internally
tagged failures retain a class; provider free text, raw errors/stacks, headers,
bodies, cookie/query/env, OTP, token/JWT, seed/QR/recovery and Basic header never
enter result JSON. Fixture request introspection exposes keys, operation, pinned
route, retry count and synthetic session alias only, not body/Authorization values.
Source has no console/logger/telemetry. This proves local explicit output behavior,
not Vercel platform logging settings or external tracing.

Server modules reject browser globals and are absent from every current client,
API, HTTP/default-adapter and production ash import graph. Current config/package/
HTML/JS/CSS and accepted tests are byte-identical. Future activation requires both
a separately reviewed source gate and deployment-registration gate, followed by
reviewed mode/revision/native registration. Credential presence, browser flags or
fake mode words satisfy neither. Both gates remain false. Diagnostics contain no
real authority factory or positive admission path.

The current Vercel function maxDuration=5 seconds is unchanged. A future multi-call
OTP/TOTP lifecycle needs a separately reviewed end-to-end budget and deployment
configuration; several 4000 ms exchanges cannot be presumed to fit that worker
budget. Timeout never justifies retry or context refresh.

## Phases 8–9: Owner custody and explicit stop disposition

[Names-only runbook](nexus-g3-d01-vercel-secret-custody-runbook-v1.md) defines the exact
conditional dashboard procedure, Production scope, non-public variable names,
deployment/change gates, value-free evidence and independent cleanup/rotation.
It explicitly forbids injecting credentials now.

| Surface | Present evidence / required exclusion | Disposition |
|---|---|---|
| Current Windows/Codex executor | Executor has workspace access; no isolated Owner context proved | Exclude from all credentials/admin/browser custody |
| Reported deploy .env.local / VERCEL_OIDC_TOKEN | User-reported only; no file/value/permissions read | Owner must independently invalidate any effective executor grant; local deletion is insufficient |
| Vercel project/admin/environment | No effective role or environment-read denial evidence | Independent Owner administration and effective denial required |
| Deployment controls | No exclusion proof; current source gates disabled | No executor deployment tokens/alternate control route |
| Vercel function logs/debug/telemetry | Application source closed; platform settings unverified | Owner audits platform and access from excluded context |
| Stytch workspace/project administration | No credential or dashboard inspection | Independent Owner-only Test admin, no executor role/secret read |
| Owner browser/device | Ordinary-browser report only | Separate device/security context without executor automation/session access |
| Server bearer custody | Private synthetic handles/model only | Effective runtime/shell/dumps/backups/access exclusion still required |

Thus D04_PRE_SECRET_CUSTODY=CONDITIONAL_OWNER_DEVICE_REQUIRED, while full D04 remains
BLOCKED. Policy text does not prove the executor is currently excluded. Owner-only
device/account/permission preparation is a STOP for this run; no weaker test replaces it.

## Phases 10–11: validation, packaging and checkpoint

Exact new source files:

- diagnostics/g3-d01-rp/lib/server/pre-secret-policy.js
- diagnostics/g3-d01-rp/lib/server/provider-registration.js
- diagnostics/g3-d01-rp/lib/server/credential-custody.js
- diagnostics/g3-d01-rp/lib/server/stytch-transport.js
- diagnostics/g3-d01-rp/future-owner-ui/totp-transient.js
- diagnostics/g3-d01-rp/future-owner-ui/index.html
- diagnostics/g3-d01-rp/tests/pre-secret.test.js
- docs/nexus-g3-d01-vercel-secret-custody-runbook-v1.md
- docs/nexus-g3-d01-pre-secret-readiness-closure-v1.md
- MANIFEST.json (regenerated)

The accepted manifest rule matches `credential` in the loader path and excludes
that file. **Rule unchanged, file not renamed to evade it.** Manifest regeneration
therefore includes 388 entries: 380 previous + eight eligible new files. The loader
is committed source, not a manifest-packaged artifact. The current disabled package
does not import it; a future distributable live assembly must resolve this protected
packaging/dependency issue through separately accepted rules or an independently
reviewed source deployment. Package PASS does not qualify that future assembly.

| Exact command | Offline result |
|---|---|
| node --test tests/pre-secret.test.js (diagnostics/g3-d01-rp) | PASS, 50 new tests, all 44 requested cases covered |
| node --test tests/model.test.js tests/http.test.js tests/boundary.test.js tests/stytch-adapter.test.js tests/stytch-boundary.test.js | PASS, 107 accepted tests |
| node --test tests/*.test.js | PASS, 157 total diagnostic tests |
| python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge | PASS, 134 G3 tests |
| python -B -m unittest tests.test_ecosystem_isolation_package (isolated manifest-source snapshot) | PASS, 11 package tests |
| python -B state/g3-d01-pre-secret-20261008/verify_pre_secret.py | PASS, secret/syntax/import/preservation/manifest gates |
| git diff --check; staged diff check | PASS |

Python: D:\DevTools\NexusR2Python\Scripts\python.exe, bytecode disabled. Static secret
scan is bounded to this slice and manifest, not credential discovery on the machine.
Baseline preservation covers 384 non-manifest pre-existing paths, including accepted
shell/adapter/tests/G3 contracts and three unrelated Route D files. Main/development
are unchanged. Ignored validation state is excluded. The final direct Owner policy
supersedes the attachment's no-auto-commit sentence: exactly one local checkpoint
is permitted only after every listed gate passes. This document describes the
offline source result at the starting checkpoint; the final commit hash is reported
after commit, without rewriting historical accepted reviews.

## Remaining Owner-only actions and readiness

1. Establish the independent Owner device/security context and effective Vercel/
   Stytch administration, deployment, environment, browser and log exclusions.
   Independently reconcile/invalidate reported executor CLI/OIDC authority.
2. Review exact native Test project/Owner/application registration, protected
   current-control provenance and project public-key provenance/rotation.
3. Separately review a bounded real server assembly, deployment timing, packaged
   dependencies and protected transient Owner handoff. No fake is promotable.
4. Release secret-custody readiness only with evidence of actual pre-secret
   exclusion and all assembly prerequisites; then separately authorize dashboard
   entry/deployment. Never provide values to Codex.
5. Separately authorize exact live OTP/TOTP/session/revoke qualification. Preserve
   CONDITIONAL identity and BLOCKED effective D04 until their live gates pass.

No remaining safe task can establish those external identity/custody facts here.
All prepared components remain disabled and qualification is not advanced.

```text
D01_PROTECTED_TRANSPORT = DEFINED
D01_CREDENTIAL_LOADER = DEFINED
D01_NATIVE_REGISTRATION_MODEL = DEFINED
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL
D01_TOTP_TRANSIENT_OWNER_UI = DEFINED
D01_LOG_REDACTION_BOUNDARY = DEFINED
D01_DEPLOYMENT_BOUNDARY = DEFINED
D01_SECRET_CUSTODY_RUNBOOK = DEFINED
D04_PRE_SECRET_CUSTODY = CONDITIONAL_OWNER_DEVICE_REQUIRED
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
READY_FOR_SECRET_CUSTODY_SETUP = NO
READY_FOR_D01_LIVE_AUTHORIZATION = NO
```
