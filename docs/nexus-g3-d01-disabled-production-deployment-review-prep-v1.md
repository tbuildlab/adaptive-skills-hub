# Nexus G3 D01 disabled Production deployment review preparation v1

2026-10-09, Asia/Kuala_Lumpur. Offline review and future Owner handoff only.
The source, config and secret-free handoff are complete locally. No hosted
deployment, account access or provider operation was performed or authorized.
An unknown Owner deployment mechanism remains an explicit future gate.

## Checkpoint and preserved boundary

Repository: `D:\chatgpt\安装skills\adaptive-skills-hub`.
Branch: `nexus-v2-g3-live-qualification`.
Exact source checkpoint/required commit parent:
`3ccdb3d414ac75895361aa1274d560996c6ccd1b`.
Checkpoint message: `g3: pin D01 Owner registration and public JWKS`.
Tracked worktree and index were clean at the start. The three unrelated Route D
documents remain unchanged, untracked and excluded from staging and packaging.
All 410 captured baseline paths other than MANIFEST.json retain their raw bytes.
The original 405 manifest entries retain their normalized hashes and sizes.
Existing source, tests, G3 v1/D05 contracts, pin generation/window and both false
compile gates are unchanged. No runtime/deployment source file is edited.
Neither main nor nexus-v2-g3-development is modified.

Windows Vercel CLI and Dashboard authorization revocation, Windows Stytch logout,
continued independent Owner phone custody and no STYTCH_SECRET injection are
**OWNER_REPORTED**. They are not effective-permission or logout proof. No local
credential artifacts, environment values, provider Dashboard/API, remote Git
state or browser data were inspected. Windows authentication must not be restored.

## Frozen deployment inventory

The unchanged accepted `diagnostics/g3-d01-rp/scripts/verify_deployment.py`
generates precisely the following **19 runtime files**, with LF-normalized source
bytes, sorted ZIP_STORED entries, fixed timestamps and file modes. These artifact
paths are not the entire repository. No tests, docs, state, Route D, .git, .vercel,
.env, shell/browser data, account artifacts or production authority modules belong
to the deployment root. Its private dependency-free package requires no install.

Deterministic deployment-source ZIP SHA-256:
`84796f260303ad64e9982134075a4fadae968c70919d3ffaf17a62be51c78fc3`.
This is the accepted checkpoint's source hash, unchanged in this run.

| Frozen artifact path | SHA-256 |
| --- | --- |
| api/diagnostic.js | cae0802c8bd2e1e62a73ad3c9ddc2ce23ab7bc28420abb2f209171a65e4466d4 |
| lib/adapter.js | 5aece3c908071e7088c8a63ce86de3ba8a387cf3fb3c867283a90a3a5eb47782 |
| lib/http.js | befe3d2574ca0b4ba1e1c615771c27021f14d57b9b7744d35fcc13960393d5bc |
| lib/policy.js | d8175e9b8674a84db1c4d54e98ec0028799b4cead09b8614f56bd7ef7e1811c2 |
| lib/server/credential-custody.js | c135a353cf89ac28bbfdb41c9a230c830ed213a81ae91515065c6c997cc78e21 |
| lib/server/deployment-input.js | 67cedb5d52c4f5523252c864c08d48f752f522036e40719eaf6fc8d5addaabeb |
| lib/server/diagnostic-service.js | c156c25d4eb0b489b3ea432f383704d2f48e0f1ef710f6c99a4d654a9e6affa7 |
| lib/server/owner-channel.js | 1a0653105efc39cf799bffce176e557349db911037aa6c2305d5402a7ba27542 |
| lib/server/pinned-identity.js | 2ca7402f71c1c54aba84bb1a60e15c5ffce332f4857e40d35e913f6da2d88d50 |
| lib/server/pre-secret-policy.js | b39432303e0b9079b3bb188107466afacbce7bdffc00bf8318cf6275c13297e7 |
| lib/server/provider-registration.js | 22d3197240beee0e8a42f09559c88f348ceda04c075655c165cea04eeb9cda9a |
| lib/server/stytch-transport.js | 3508ef7aea6618018dc08f0712f2bb4ff6f95b9ab8211e7ee51f1566ae80e94b |
| lib/stytch-identity.js | 6b711b0232b3890c7ad56a4db8265a55a752b191545fcdd8cbb00c784c7c0047 |
| lib/stytch-projection.js | 637e48f727706bc498f4ceb8abafc4103a3a79ee8efb609fe1901e0d2bea0d42 |
| package.json | e4e6a7e8176f0138e2b31954b29ea77026b7629ba359af110fcfab0807fcc4ce |
| public/app.js | 340bbe76f15af98a9a07903a4a2e4aa3b22d71c6e2c1604170568f09334f99df |
| public/index.html | 899839c32d1fca98997f4a890846de35189e472ef06994c7ffbb99a26095c9d9 |
| public/owner-transient.js | 21968c6a5eb1a55cb784dc23526039a9379202c63fd78bc02a2a32f9fa1ff7c6 |
| vercel.json | cbd5fb25d6a43d674d243ddd45e4eb890aca136f0f5405d43be244be3963a272 |

The Owner-provided native IDs and exact public pin stay in the protected server
input source; this report uses aliases P_OWNER_PROJECT_ID_REVIEWED and
U_OWNER_NATIVE_ID_REVIEWED. The one RSA-2048/RS256 public verification key, normalized
public fields, Owner-reviewed provenance, generation 1 and null delivery_email
remain unchanged. Public mathematical key fields are non-secret; no private JWK
field, certificate response-envelope metadata, bearer or factor value is pinned.
This run does not observe a signed provider token or prove runtime Principal
semantics. STYTCH_PRINCIPAL_RUNTIME_MAPPING remains CONDITIONAL; D04 remains
unqualified/BLOCKED. Server-side placement is not production executor exclusion.

## Production input review and hosted evidence boundary

| Input | Offline verdict | Actual hosted evidence |
| --- | --- | --- |
| Private ESM package, Node 24.x, zero dependencies | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| One function api/diagnostic.js, maxDuration 30 seconds | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| One application API route /api/diagnostic | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| Three public source assets: index.html, app.js, owner-transient.js | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| No framework/build command; public output directory | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| No rewrites, redirects, env configuration or extra endpoint | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| Exact Host/origin https://nexus-g3-qual.vercel.app | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| Both compile gates false; Preview/Development/unknown tier cannot activate | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| Static headers and function JSON overrides | PASS | OWNER_LIVE_REVIEW_REQUIRED |
| Actual plan limits, function trace, platform routes/settings/permissions | NOT_INSPECTED | OWNER_LIVE_REVIEW_REQUIRED |

Header input is no-store, no-referrer, nosniff, frame denial, CSP default-src none
and self-only public script/style/connect/form sources. Function JSON responses
have the stricter default-src none CSP. Global `/(.*)` header matching does not
accept wildcard request Host/origin. Exact origin checks remain unchanged. Actual
merged headers, output trace, runtime/version and account duration support cannot
be established from vercel.json/package.json; no workaround or broader origin is
authorized. Unsupported hosted requirements retain HOLD.

## Hard-disabled local startup proof

The new offline proof loads the composed artifact entrypoint in an isolated Node
child. Network traps cover HTTP/HTTPS request/get, net connect/createConnection,
TLS connect and fetch. A synthetic environment Proxy replaces process.env without
reading/saving/enumerating the original environment. In-memory load hooks install
counted rejecting traps at credential loading, native transport construction,
provider exchange, runtime pin selection, signature verification and Owner
transient envelope creation. Any trap invocation fails the proof, even if caught
by the handler. Files, gates and canonical records are not rewritten by the hooks.

Fixture GET/POST/factor/simulation/Owner-form and browser-override requests reach
only FAKE_DISABLED -> DENY, AUTHORITY NONE and REAL_ADMISSION DISABLED. Wrong Host,
Origin, Preview/Development Host and extra route have explicit denial assertions.
Compile gates reject attempted live configurations for unknown tiers as well.
Registration/public key presence and a synthetic throwing credential getter cannot
activate live mode. All network, credential environment/loader, native factory,
provider exchange, runtime pin/signature, Owner-material and environment-enumeration
counters equal zero. There is no real session/factor authentication or authority.

This proves the reviewed local composed source under the specified fixtures. It
does not prove hosted traces, provider behavior, Owner account custody or effective
D04 permissions. The unchanged verifier also validates public pins structurally
using only Owner-supplied public material; that offline operation is distinct from
the disabled entrypoint's zero runtime signature-path counter.

## Client/server separation

Static browser assets have no server import, environment-value access, native
Owner/project ID, public keyset/provenance, raw JWT/token, factor secret, storage
API, analytics, debug fetch or authority module. Import closure resolves only
reviewed relative source and Node builtins server-side; no third-party dependency.
The server assembly/HTTPS/custody source is included, without invoking it.

The closed diagnostic projection contains: diagnostic/classification/evidence_source;
authority/real_admission/qualified_live; result/state/case_id; project/user/session
aliases; factor_types/factor_freshness_status/factor_last_authenticated_at;
context_generation/owner_generation/binding_generation; observation_start/end,
context_expires_at/observation_point/error_class. Transport adds
live_diagnostic_enabled=false, adapter_mode=FAKE_DISABLED and a nullable CSRF field.
Current disabled observations have no verified identity/factor/session values.
Exact native identifiers and server pin/provenance are unnecessary and withheld.

The disabled page's random Secure/HttpOnly/SameSite Strict cookie and CSRF protect
fixture page transport, without Owner authentication or provider bearer authority.
They stay in test memory; no raw response/cookie/header is retained. Browser-visible
labels/aliases, enums, booleans, bounded timestamps and nullable generations are
the permitted evidence. No OTP, TOTP seed/recovery code, session bearer or future
private enrollment HTML is produced. Public-key mathematics alone is not secret,
but the static client does not require or receive it.

## Owner-only deployment mechanism assessment

| Candidate | Available offline evidence | Disposition |
| --- | --- | --- |
| A. Existing Git-connected Production source | No remote/project read; checkpoint is local only | OWNER_CONFIRMATION_REQUIRED |
| B. Owner Dashboard deploy/redeploy | No dashboard read; ZIP import/current revision support unknown | OWNER_CONFIRMATION_REQUIRED |
| C. CLI on independent Owner device | Phone reported; CLI/device capability not proved | OWNER_CONFIRMATION_REQUIRED |
| D. Owner-controlled Git integration | No integration/ref evidence; no push authorized | OWNER_CONFIRMATION_REQUIRED |
| E. No currently proven Owner-only path | Secret-free handoff is available locally | SOURCE_PREPARATION_READY; deployment remains gated |

No class is selected as an established mechanism. An Owner must confirm one exact,
independent, separately authorized transfer/deploy path. A remote integration may
contain older bytes; Redeploy is insufficient without source proof. Windows login,
executor upload or push is not a fallback. Per task scope this uncertainty does not
block preparing a safe handoff; it blocks claiming any actual deployment.

## Deterministic Owner handoff and review window

Ignored local package:
`state/g3-d01-deployment-prep-20261009/owner-handoff.zip`.
Expanded handoff: `state/g3-d01-deployment-prep-20261009/handoff/`.
Deterministic handoff ZIP SHA-256:
`b6cedd51150326ce7e393bf2c3e682ec5d478ce680edd6addf84dcfb3b6d238f`.

Exactly 27 members: source/<19 files>, deployment-source.zip, source-manifest.json,
SHA256SUMS.txt, source-bundle.sha256.txt, deployment-config-summary.json,
OWNER-CHECKLIST.md, POST-DEPLOYMENT-EVIDENCE.json and DISABLED-LABELS.json.
Only the 19-file source directory is a future deployment root. The package includes
no repository MANIFEST dependency, real account credentials, .env/.vercel, OIDC,
browser/session data, ignored evidence, tests, unrelated files or authority modules.
Public registration/key values occur only in server source copies. Both source and
handoff ZIPs reproduce byte-for-byte; readback verifies closed names, hashes, labels
and all 18 exact post-deployment checks. No check may be omitted, duplicated or
promoted to verified by an offline artifact. No upload/deployment is performed.

The [Owner runbook](nexus-g3-d01-disabled-production-deployment-owner-runbook-v1.md)
defines Production source verification, independently confirmed mechanism, runtime/
duration/header/function trace, public/server separation and sanitized evidence.
All 18 hosted checks remain OWNER_LIVE_REVIEW_REQUIRED, including revision/domain,
source trace, function/route/assets, runtime/duration, headers, tiers, alternate
endpoint/telemetry checks, native-ID/secret output, credential reads, disabled labels
and provider calls. Page load or DENY alone is insufficient evidence.

The fixed review window ends **2026-10-10 00:42:05 Malaysia time**
(`1791564125000`). No generation/window is extended. Complete Owner disabled
deployment/review before this deadline if current pin provenance is intended.
After expiry, STOP before secrets/live activation; the independent Owner must
re-review current public JWKS, compare exact keyset/generation and establish a new
reviewed provenance checkpoint if required. Expiry does not invalidate historical
offline source hashes or test results; it prevents later stale positive use.

## Validation and exact checkpoint slice

Commands below run locally with no provider/cloud request:

On a fresh checkout, run prepare_owner_handoff.py first to generate the bounded
ignored artifact/handoff fixtures used by the new JS and Python tests. Tests do
not accept a missing/unreviewed fixture or fetch a replacement from a provider.

| Command / cwd | Result |
| --- | --- |
| node --test tests/deployment-prep.test.js / diagnostics/g3-d01-rp | 18 PASS |
| python -B diagnostics/g3-d01-rp/tests/test_deployment_prep.py / repo | 30 PASS |
| node --test tests/*.test.js / diagnostics/g3-d01-rp | 285 PASS, including the 18 new cases |
| node --test tests/owner-pinning.test.js / diagnostics/g3-d01-rp | 53 PASS, also included above |
| python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge / repo | 134 PASS |
| python -B -m unittest tests.test_ecosystem_isolation_package / fresh approved source snapshot | 11 PASS |
| python -B diagnostics/g3-d01-rp/scripts/prepare_owner_handoff.py --output state/g3-d01-deployment-prep-20261009 / repo | PASS; unchanged verifier + startup proof + handoff scan/roundtrip |
| python -B state/g3-d01-deployment-prep-20261009/verify_prep.py / repo | PASS; baseline, scans, import/config closure, deterministic MANIFEST/source/handoff |
| git diff --check; git diff --cached --check / repo | PASS |

Python is `D:\DevTools\NexusR2Python\Scripts\python.exe`.
New tests cover all requested 01..37 cases (18 JS + 19 numbered Python) and 11
additional Python attacks: added function/redirect/rewrite, private JWK, handoff
environment/path escape, false hosted claims, modified source/self-attestation,
authority-label promotion and omitted/duplicated checklist evidence. All reject
unsafe source/evidence changes. Existing guards/tests are unchanged. Unique tests:
285 diagnostic + 30 Python + 134 G3 + 11 package = **460 PASS**; separate subset
runs are not added again. Package tests use a fresh explicit static snapshot, not
the checkout containing ignored state/.git objects. Packaging exclusions remain
unchanged, including sensitive filename rules and credential-custody source
exclusion from MANIFEST; the accepted standalone runtime verifier includes that
reviewed source module independently. MANIFEST adds only six new approved paths:
**411 entries**, all 405 prior entries preserved.

Exact changed/staged slice (six new files and MANIFEST only):

1. diagnostics/g3-d01-rp/scripts/prepare_owner_handoff.py
2. diagnostics/g3-d01-rp/scripts/prove_disabled_startup.mjs
3. diagnostics/g3-d01-rp/tests/deployment-prep.test.js
4. diagnostics/g3-d01-rp/tests/test_deployment_prep.py
5. docs/nexus-g3-d01-disabled-production-deployment-owner-runbook-v1.md
6. docs/nexus-g3-d01-disabled-production-deployment-review-prep-v1.md
7. MANIFEST.json

Ignored validation logs/snapshot/artifacts/handoff and all three unrelated Route D
documents are excluded from the local commit. The final hash is recorded in the
local checkpoint receipt under ignored state and the completion response, avoiding
a self-referential commit hash in this file. No push/merge/tag/release/deploy.

## Remaining Owner-only actions

Confirm independent device/account custody and effective remote permissions; select
and separately authorize an exact transfer/Production deployment mechanism; verify
source bytes and all 18 actual hosted checks on that device. Retain sanitized
non-secret evidence only. Review public-pin currency before the fixed deadline;
after expiry re-review it before any later secret/live step. Do not restore Windows
authorization, inject STYTCH_SECRET or perform OTP/TOTP/session calls in this scope.
Future secret custody and D01/D04 live qualification remain separately gated.

```text
D01_REVIEWED_DEPLOYMENT_SOURCE = FROZEN
D01_REVIEWED_SOURCE_FILE_COUNT = 19
D01_REVIEWED_SOURCE_HASH = 84796f260303ad64e9982134075a4fadae968c70919d3ffaf17a62be51c78fc3
D01_PRODUCTION_CONFIG_REVIEW = PASS
D01_DISABLED_STARTUP_PROOF = PASS
D01_CLIENT_SERVER_BOUNDARY = PASS
D01_OWNER_HANDOFF_PACKAGE = READY
OWNER_DEPLOYMENT_MECHANISM = OWNER_CONFIRMATION_REQUIRED
VERCEL_ACTUAL_BUILD_VERIFIED = NO
VERCEL_ACTUAL_RUNTIME_VERIFIED = NO
VERCEL_ACTUAL_PERMISSION_REVIEW = OWNER_REQUIRED
DISABLED_PRODUCTION_DEPLOYMENT_VERIFIED = NO
LIVE_ADAPTER_DEFAULT = FAKE_DISABLED
CODE_REVIEWED_LIVE_ENABLED = false
DEPLOYMENT_REGISTRATION_ENABLED = false
NETWORK_CALLS_PERFORMED = 0
CREDENTIAL_READ_ATTEMPTS = 0
LIVE_STYTCH_CALLS_PERFORMED = 0
STYTCH_CREDENTIAL_ACCESS = NONE
VERCEL_SECRET_ACCESS = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
READY_FOR_OWNER_DISABLED_DEPLOYMENT = YES
READY_FOR_SECRET_INJECTION = NO
READY_FOR_D01_LIVE_AUTHORIZATION = NO
```
