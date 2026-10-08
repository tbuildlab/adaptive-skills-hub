# Nexus G3 D01 diagnostic RP offline implementation and review v1

Date: 2026-10-08. Scope: OFFLINE IMPLEMENTATION AND REVIEW ONLY.
Repository: `D:\chatgpt\安装skills\adaptive-skills-hub`.
Branch: `nexus-v2-g3-live-qualification`.
Starting/ending HEAD for this uncommitted slice:
`6100cb298f58a52ab1f55d0df22b3c2ae34b7535`.

Authoritative inputs: [setup plan](nexus-g3-live-qualification-setup-plan-v1.md),
[Principal closure](nexus-g3-u1-stytch-principal-closure-v1.md),
[bounded context](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md),
[N02 architecture](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md)
and unchanged G3 contracts/fail-closed implementation. This application is neither
N01 nor N02 and cannot produce production authority.

## Scope and manually reported environment

Owner reports Stytch workspace `Nexus G3 Qualification`, Consumer Test projects
`Nexus-G3-P-OWNER` / `Nexus-G3-P-OTHER`, U_OWNER and U_NONOWNER in P_OWNER,
U_FOREIGN in P_OTHER, and Vercel project `nexus-g3-qual`. Reported P_OWNER settings:
only origin `https://nexus-g3-qual.vercel.app`; email OTP and TOTP enabled; maximum
provider session duration 15 minutes; magic link, SMS/WhatsApp OTP, OAuth, passwords,
Web3, WebAuthn and impersonation disabled; localhost removed.

These are OWNER_REPORTED, DEPLOYMENT_UNVERIFIED. No account/resource/UI was read,
no native provider IDs were discovered, and factor enrollment/issuer/audience,
effective custody and deployment configuration have not been qualified. Emails,
display names, project labels and this repository are never enrollment authority.

The implemented web route is permanently FAKE_DISABLED. Factor controls are
prepared and visibly disabled; no email/code/seed is collected. Model tests exercise
typed synthetic observations offline. They are not an operational login flow.
Live enablement requires a later reviewed code change, not merely setting a flag.

## Exact changed files and framework

New isolated application; no files under `ash/` are edited or imported:

| File | Responsibility |
|---|---|
| `diagnostics/g3-d01-rp/package.json` | Private ESM package, Node 24.x, zero third-party dependencies, native test command |
| `diagnostics/g3-d01-rp/vercel.json` | Framework-free Vercel Node Functions/static configuration; output public; security headers |
| `diagnostics/g3-d01-rp/api/diagnostic.js` | Sole deployable API entrypoint; imports disabled HTTP facade only |
| `diagnostics/g3-d01-rp/lib/policy.js` | Closed enums, exact origin, hard false live gate, sanitized result projection |
| `diagnostics/g3-d01-rp/lib/adapter.js` | Disabled adapter and names-only future server input interface; no SDK/network/env access |
| `diagnostics/g3-d01-rp/lib/http.js` | Exact-host/origin checks, anti-CSRF page cookie, bounded volatile page store, fixed error output |
| `diagnostics/g3-d01-rp/lib/model.js` | Test-only semantic state machine, factor/identity joins, bounded lineage and retirement |
| `diagnostics/g3-d01-rp/public/index.html` | Explicitly labelled disabled email/TOTP workflow and observation interface |
| `diagnostics/g3-d01-rp/public/app.js` | Same-origin API transport, fixed evidence projection, no storage/analytics |
| `diagnostics/g3-d01-rp/public/app.css` | Local responsive styles and visible focus state |
| `diagnostics/g3-d01-rp/tests/model.test.js` | Synthetic equality, freshness, lifecycle, lineage and redaction adversaries |
| `diagnostics/g3-d01-rp/tests/http.test.js` | Route/CSRF/cookie/origin/expiry/worker/gate adversaries, actual entrypoint smoke test |
| `diagnostics/g3-d01-rp/tests/boundary.test.js` | Import/config/UI boundary checks and in-process client DOM/transport checks |
| `docs/nexus-g3-d01-diagnostic-rp-implementation-review-v1.md` | This implementation review and remaining gates |
| `MANIFEST.json` | Existing mechanism adds eligible static files; previous entries unchanged |

Framework choice: native Vercel Node.js Functions plus static HTML/CSS/JavaScript,
without React/Next/auth middleware or installation. Node `node:crypto` supplies
random page/lineage IDs and timing-safe comparison; `node:test`/`node:assert` and
test-only filesystem/VM modules supply offline verification. No dependency lockfile
is necessary because there are no package dependencies or install/build steps.
Vercel documents [Node.js functions](https://vercel.com/docs/functions/runtimes/node-js),
[ESM configuration](https://vercel.com/docs/functions/configuring-functions/runtime)
and [Node 24.x support](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions).
These establish documented runtime compatibility, not a successful deployed build.

## Architecture and trust boundaries

```text
public labelled static page
  -> same-origin /api/diagnostic
  -> Host/Origin + volatile anti-CSRF page context
  -> fixed FAKE_DISABLED denial (local retirement only)

offline test process
  -> exact fixture registration + injected synthetic clock/observations
  -> OfflineDiagnosticModel
  -> sanitized fake results; qualified_live=false, authority=NONE
```

The deployed import graph does not reference model.js. There is no fake-success
endpoint, browser registration endpoint, dynamic adapter import or environment
selector. Test-only source is outside public/. A deployment bundler accidentally
including a model file cannot activate it through the sole API route.

| Boundary | Writer/readers and permitted state | Failure/recovery behavior |
|---|---|---|
| Public page | Browser reads labels and projected output; sends only closed action enum and CSRF transport header | Wrong origin never requests API; unknown transport result displays denial; no localStorage/sessionStorage/evidence download |
| Page anti-CSRF store | Sole handler instance owns max 128 entries: random page key, random CSRF, absolute five-minute deadline | Capacity denies; reload preserves deadline/cookie; expiry deletes entry; old cookie on another worker/restart denies; clock regression clears store |
| Offline Owner simulation | Test process supplies protected-input analogue; registration/observations copied into private model fields | No browser access; malformed registration denies; changed IDs/generations retire; no real Owner or durable authority |
| Future adapter custody | NOT_IMPLEMENTED; requires excluded server runtime and independently registered non-secret provider inputs | No env reads, SDK, token constructor, persistence or fallback in this version; unavailable adapter denies |
| Authority/effect boundary | No writer, reader, endpoint, record factory or credential exists in this app | All authority paths absent; existing public real admission code unchanged |

Volatile per-instance state is intentionally an availability limitation: load
balancing/cold starts can require a new diagnostic page, but cannot restore its
previous OwnerContext. No database, shared store, signed bearer context, epoch
service or custom lifecycle broker is introduced. A new page is not a refreshed
Owner context and has no authentication authority.

## Closed state machine and bounded context

| Current state | Permitted offline event | Next state / guard |
|---|---|---|
| SIGNED_OUT | EMAIL_START | EMAIL_OTP_PENDING; valid protected-input fixture registration |
| EMAIL_OTP_PENDING | PRIMARY_OBSERVATION | PRIMARY_FACTOR_VERIFIED; exact typed project/environment/native identity; fresh email factor |
| PRIMARY_FACTOR_VERIFIED | TOTP_ENROLLMENT_START (optional) | TOTP_ENROLLMENT_REQUIRED; no seed/QR generation |
| PRIMARY_FACTOR_VERIFIED / TOTP_ENROLLMENT_REQUIRED | TOTP_START | TOTP_PENDING |
| TOTP_PENDING | TOTP_OBSERVATION | TWO_FACTOR_VERIFIED; same native user/session and unchanged primary factor timestamp; exact fresh email + TOTP factors |
| TWO_FACTOR_VERIFIED | OWNER_EQUALITY | OWNER_EQUALITY_SIMULATED; native ID equals registered Owner; create one private synthetic challenge/context |
| OWNER_EQUALITY_SIMULATED | PAGE recheck | SESSION_RECHECK_RESULT; exact fresh typed observation join |
| SESSION_RECHECK_RESULT after PAGE | One CONFIRM_SIMULATION or DENY_SIMULATION | Confirm consumes terminal opportunity and checks DECISION_POST_SIMULATION; deny retires |
| SESSION_RECHECK_RESULT | Next ordered RECEIPT_SIMULATION, INTENT_SIMULATION, CLAIM_SIMULATION | Same bounded lineage, unchanged IDs/generations/factors; final label yields DIAGNOSTIC_COMPLETE |
| Active model | Local logout, observed revoke or observed switch | LOCAL_CONTEXT_RETIRED, cleared identity/context; no provider mutation |
| Any invalid/expired/replayed transition | Invalid event | DIAGNOSTIC_DENIED; context cleared, no recovery to positive state |
| Complete/retired/denied | Any further action | DENY; no second terminal lineage or challenge |

All PASS values above mean OFFLINE_FAKE_FIXTURE only, with qualified_live=false.
No real corresponding record is created at any observation label. Rechecks must
carry a new synthetic point-time observation; cached/unknown/JWT-only input denies.

Context expiry is the earliest provider expiry or either required factor timestamp
plus 300000 ms. The deadline is exclusive; exactly 300000 ms denies. Context has
one random private challenge, incarnation, context generation, copied registration,
owner_generation/binding_generation and absolute expiry. Reload/recheck never
extends it, and unexpected renewed factor/session deadlines deny. Restart changes
incarnation and retires old context. Clock regression denies. IDs/generations
are checked before each label; no fixture persists or crosses process restart.
One terminal simulation consumes the opportunity; the same lineage's remaining
observation labels are allowed until expiry, but a second decision/claim denies.

The model retains only closed, non-bearer registration and typed native identity,
session, factor/time fields required to compare observations. Output maps session
to a fixed lineage alias and user to a registered diagnostic alias; native values
are never copied into browser evidence. No email/name equality is used.

## Future Stytch seam and secret custody

Current selectAdapter always returns FAKE_DISABLED regardless of missing, malformed
or true flags and injected fake adapters. The hard constant
G3_D01_LIVE_DIAGNOSTIC_ENABLED=false is never read from process.env. No Stytch SDK,
HTTP client or API call exists. The API has no provider selection/configuration input.
Passing a flag does not make a fixture eligible for live evidence.

Names-only future interface: STYTCH_PROJECT_ID and STYTCH_SECRET, exclusively in
protected server injection. STYTCH_PUBLIC_TOKEN is not required because this
version uses no frontend SDK; adding one requires review rather than silently
introducing a browser auth path. No value, .env file, sample credential, project
secret, session token/JWT, factor code, seed, QR, recovery code, raw response,
credential path, authorization header, error object, stack or environment dump is
created/read/logged/persisted. A page cookie is transport-only, Secure/HttpOnly/
SameSite=Strict/__Host; it is not a provider session and never enters evidence.
The CSRF token travels to the same-origin page only and is excluded from its
evidence projection; cookie/CSRF values are never logged.

Future reviewed adapter must implement email OTP then TOTP on the *same* retained
opaque provider session/user, validate both exact factor timestamps, and directly
authenticate that retained session separately at PAGE, DECISION_POST_SIMULATION,
RECEIPT_SIMULATION, INTENT_SIMULATION and CLAIM_SIMULATION. Those labels remain
diagnostic. Rechecks omit duration-extension/custom-claim parameters. It must not
use local JWT validation as positive current-context proof. Provider revoke/login/
OTP/enrollment code is absent here and needs later specific authorization.

Only the accepted CONDITIONAL Principal mapping is represented: native
`stytch.com/<registered_project_id>` issuer, exact project audience as client_id
conditional on dedicated Nexus application registration, native user_id matching
verified signed sub and remote Session/User. The model does not verify a JWT or
invent a new issuer/client identity. Its synthetic equality is not proof of issuer
signature or project/application suitability. Exact real IDs are later supplied
through protected non-secret registration, never browser email or TOFU.

External logout/revoke/switch cannot be asserted by a browser message. The current
UI account-switch button retires local page state only; the offline model can mark
observed invalidation for adversarial tests. Provider/session results and the
accepted t0-check/t1-revoke/t2-local-use race remain unqualified; no instant external
logout or continuous lifecycle guarantee is claimed.

## Sanitized observations and ingress

The result model contains fixed diagnostic/classification/authority/admission
labels, fake source, PASS/DENY/UNKNOWN, closed state/case/project/user/session
aliases, factor types/freshness/timestamps, context/owner/binding generations,
start/end/expiry timestamps, observation point and closed error class. Future
request_id is deliberately absent until a reviewed bounded sanitizer/provenance
rule exists. Unknown fields are dropped on output; extra/raw provider fields are
rejected at observation intake. No arbitrary exception message is serialized.

Exact origin and Host: https://nexus-g3-qual.vercel.app only. Preview/custom/localhost
hosts and ports, hostile/missing POST Origin, cross-site metadata and forwarded-host
substitution deny. GET bootstrap may omit Origin; it establishes only a random
non-authoritative page cookie, with no CORS permission and no provider action.
POST requires exact Origin, JSON content type, valid existing page cookie and a
timing-safe matching CSRF header. Body must contain only one closed action. No
redirect, callback, query, user/session/project/provider/flag argument is accepted.
There is no callback endpoint or OAuth code flow. Future callback requirements must
be explicitly reviewed; user-controlled destinations cannot be introduced.

No-store, CSP self-only static assets/connects, frame denial, base-uri none,
nosniff and no-referrer protect the prepared surface. Client fetch uses fixed
relative /api/diagnostic with redirect=error. No analytics, external fonts, vendor
telemetry, third-party auth or external API is bundled. Platform access/error logs,
headers and future OTP/token traces must be separately reviewed before live use;
this app cannot establish Vercel administrator/executor exclusion.

## Offline review findings and test evidence

Review found and corrected issues before final acceptance: model registration
replacement now invalidates on *all* identity fields as well as generations; status
reads at expiry/clock regression retire rather than expose stale simulated PASS;
and disabled-gate responses retain page CSRF transport so a subsequent local logout
still works. Missing registration cannot display an Owner alias; stale observation
replay is separately rejected. These repairs only
affect new diagnostic code; no existing test guard or authority body was relaxed.

Mandatory adversarial requirements 01-26 are individually named in model.test.js
and http.test.js (22/23 are HTTP tests). Additional tests cover exact five-point
ordering, DENY lineage, raw/duplicate/future factors, protected registration,
cache replay, immutable input copies, bounded page capacity, Host/proxy confusion,
multi-worker invalidation, client evidence projection and the deployed import graph.
Native request/response objects and a minimal in-process DOM/VM are injected: no
browser login, listener, provider request, credential or cloud operation occurs.

| Exact command / location | Result |
|---|---|
| `node --test tests/*.test.js` in diagnostics/g3-d01-rp | PASS, 51 tests; no network or provider calls |
| `python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge` at repository root | PASS, 134 unchanged G3 regression tests |
| `python -B -m unittest tests.test_ecosystem_isolation_package` in isolated manifest-source snapshot | PASS, 11 package/isolation tests |
| `python -B state/g3-d01-rp-offline-20261008/verify_offline.py` at repository root | PASS, documentary fields, baseline byte preservation, static-file syntax and manifest boundary |
| `git diff --check` plus new-file trailing-whitespace scan | PASS |

Python commands use D:\DevTools\NexusR2Python\Scripts\python.exe and bytecode is
disabled. Node runtime observed locally: v24.18.0. The manifest is regenerated by
unchanged scripts/build_manifest.py over the accepted 359-entry baseline plus the
14 explicitly authorized new files: 373 entries, deterministic, previous entries
unchanged. Sensitive-path exclusion is preserved; no survey renaming, allowlist
change, ZIP release, installation or fixture promotion occurs. Validation evidence
and source snapshot remain ignored under state/g3-d01-rp-offline-20261008.

Baseline preservation covers 363 pre-existing non-manifest paths, including
accepted code/contracts, all accepted documents and three unrelated untracked
Route D documents. The only tracked change is MANIFEST.json; this slice adds the
13 application files and this review. Main/development refs and HEAD remain
unchanged; nothing is staged or committed. Tests establish offline behavior and
configuration consistency only, not Vercel build, browser E2E or effective exclusion.

## Deployment/live gates and exact blockers

Owner can review this **disabled** deployment artifact now. Later Owner-only
deployment review must select root directory diagnostics/g3-d01-rp, Node 24.x,
framework Other/native Functions, no build/install dependencies, public output,
sole API and exact stable domain. Review actual Vercel project overrides, source
digest, routing/security headers, dashboard/preview/access control, request/error
logging and cost/window before separately authorizing deployment. Do not set any
Stytch secret merely to view this disabled version. No build/deployment was run.

Remaining blockers before D01 live authorization:

1. No live Stytch adapter/factor flow exists. Implement it under a new reviewed
   bounded scope, with excluded server-only token custody, same-session factor join,
   signed pinned issuer/audience/sub checks, direct remote rechecks and sanitized
   exceptions. Retain no real authority path. Do not promote the offline model.
2. Complete independent native registration and Owner binding ceremony, exact
   application/project/SDK/factor semantics, genuine Test-mode human authentication
   and session-lifecycle matrix from the setup plan. Owner-reported settings alone
   do not prove these facts. No real registration was accepted here.
3. Resolve protected Owner browser/device, deployment/issuer administration,
   function-token custody, log/telemetry exposure and every equivalent executor
   route. Complete D04 effective exclusion remains BLOCKED.
4. Qualify volatile worker/restart/session custody for any eventual live RP;
   unknown instance/lost bearer must retire and require fresh authentication.
   Never add persistence/refresh to hide failed context recovery.
5. Complete Owner preparation checklist and separately authorize exact live action
   IDs, credential-*use* boundary, account mutations, counters, evidence custody
   and stops. This code review supplies none of those permissions.

Safe for Owner review: YES. Suitable to deploy as an explicitly disabled diagnostic
shell only after Owner deployment approval/configuration review: YES. Ready for
real login/session diagnostics or actual N02 Owner confirmation: NO. D01 remains
CONDITIONAL, D04 BLOCKED, N01/N02 NOT_IMPLEMENTED, public real admission disabled.
No push/merge/tag/freeze/release/main change or automatic commit is performed.

```text
D01_DIAGNOSTIC_RP = IMPLEMENTED_OFFLINE
D01_DIAGNOSTIC_RP_REVIEW = PASS
LIVE_STYTCH_CALLS_IMPLEMENTED = NO
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
VERCEL_DEPLOYMENT_PERFORMED = NO
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
READY_FOR_OWNER_DEPLOYMENT_REVIEW = YES
READY_FOR_D01_LIVE_AUTHORIZATION = NO
```
