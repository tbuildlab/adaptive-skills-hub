# Nexus G3 Delegated Executor Authority Policy v1

Status: Owner-authorized additive policy amendment; documentary only. Source checkpoint: `f9bfdfdad552734ad94d84e8352ec8b55fe177af`, branch `nexus-v2-g3-live-qualification`. This amendment records the Owner's explicit policy override supplied on 2026-10-09. It does not implement an authority service or modify an accepted canonical body.

## Effective policy

```text
G3_AUTHORITY_MODE = DELEGATED_EXECUTOR
OWNER_EXCLUSIVE_AUTHORITY = WAIVED
D04_EXECUTOR_EXCLUSION = NOT_REQUIRED_AS_A RELEASE GATE
ROUTINE_OWNER_CHECKPOINTS = DISABLED
OWNER_PREAUTHORIZED_AUTONOMOUS_EXECUTION = YES
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE
REAL_ADMISSION_ENABLED = NO
```

The executor may carry out the currently authorized Git/Vercel investigation and the minimum safe deployment correction without routine Owner approval. It must first inspect existing state, preserve the exact reviewed source, prefer an existing legitimate deployment mechanism, and verify the resulting Production commit/source and disabled diagnostic behavior. No meaningless source edit is permitted. An empty trigger commit requires evidence that safer deployment mechanisms are unavailable and that it is necessary; absence of a check run alone is insufficient.

Delegation changes the trust assumption: the executor is trusted to act within the Owner's stated scope. Executor exclusion is no longer a release gate in this mode. It has not been demonstrated, and D04 is not PASS or VERIFIED. Historical D04 BLOCKED findings and Owner-exclusive architecture remain intact as evidence of the earlier model. The amendment applies only to delegated mode; it does not waive unrelated isolation controls, provider authentication, or fail-closed validation.

## Retained mandatory controls

Every eventual authority operation must enforce exact scope, least privilege, expiry, revocation, anti-replay, generation/version binding, exact provider/account/target binding, deterministic authorization contracts, audit/evidence, secret redaction, fail-closed unknown/error behavior, no silent privilege expansion, and bounded cost/resource use. Short TTL, copied records, fixtures, source hashes, provider credentials, and this policy document are not bearer authority.

Delegation does not establish a numeric spending limit. Paid resources, subscription upgrades, unbounded retries, and irreversible retention must not be inferred from it. Existing resource limits and test-environment restrictions continue to apply. Missing cost or resource bounds deny the affected action.

## Credential custody

Existing credentials may be used only through legitimate protected runtime/provider interfaces for the exact authorized service and account. Raw secrets, auth headers, cookies, session tokens/JWTs, OTP/TOTP material, private keys, and credential values must never be printed, copied into evidence, committed, or bundled into public assets. No credential-file inspection or browser-storage extraction is authorized by this amendment. Sanitized evidence contains identities, revisions, timestamps, hashes, and status labels only.

A browser connection error does not justify bypassing its access policy. Missing usable authenticated access remains an operational blocker. The executor must stop the affected action at interactive MFA/OTP/CAPTCHA, unavailable account/credential, payment/legal acceptance, hardware confirmation, an architecture contradiction, an irreversible out-of-scope action, or a platform limitation no available tool can cross. Independent authorized offline work may continue. These are real execution boundaries, not routine Owner checkpoints.

## Migration impact

| Dependency | Effect in delegated mode | Remaining prerequisite |
| --- | --- | --- |
| D01 | Diagnostic investigation and protected credential-interface use may proceed within scope; Owner-exclusive browser custody is no longer a release gate. | Actual identity/session/factor semantics and exact registration must still be qualified. Stytch runtime Principal mapping remains CONDITIONAL; provider session validation is not replaced by delegation. |
| D02 / N02 | The minimal fixed confirmation design remains accepted; existing Host confirmation remains historically BLOCKED. | N02 is NOT_IMPLEMENTED. A delegated action cannot be relabeled as an observed human CONFIRM or accepted Owner receipt. |
| D03 | Offline protocol remains DEFINED; deployed fence enforcement remains UNVERIFIED and CONDITIONAL. | Sequence, immutable checkpoint lineage, rollback/fork/gap detection, quarantine, crash recovery, epoch/incarnation retirement, and revocation/claim ordering remain required. No AWS enforcement is proved by this policy. |
| D04 | NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE; never PASS. | Least privilege and credential redaction remain mandatory. Claims of resistance to a malicious executor would be unsupported under the revised trust assumption. |
| D05 / N01 | Seven accepted production outer contracts and existing v1 bodies remain unchanged. N01 remains NOT_IMPLEMENTED. | Production-positive transitions require qualified current context, closed protected state, exact target/dispatch contracts, transactional uniqueness, checkpoint protocol, and a separately reviewed production decision seam. |

An executor/session identity must never silently replace the authenticated Owner Principal in existing D05 records. Where a production transition needs a human OwnerDecision, this delegation alone is not a fabricated decision. If delegated operation requires different actor/provenance semantics, define an explicit additive versioned compatibility amendment and qualify it before accepting a positive transition; deny the incompatible transition in the meantime. The policy does not require inventing such an amendment for the disabled diagnostic shell.

OwnerContext stays short-lived, non-refreshable, single-challenge, single-use, and unable to cross restart; its maximum lifetime remains 300000 ms. Claim-time remote session recheck remains required. The accepted residual check-to-claim race remains visible. No continuous external-lifecycle guarantee is newly asserted. Local invalidation, binding/Owner generations, expiry, epoch/incarnation, and irreversible claim consumption remain enforced requirements. Results, including UNKNOWN, cannot authorize automatic redispatch.

## Real admission activation gate

REAL_ADMISSION remains disabled until delegated-mode qualification passes. That requires evidence for the actual provider/account registration and runtime identity mapping; current-context and local invalidation semantics; exact frozen display-to-target-to-payload binding; nonce, receipt/grant provenance, revocation and intent/claim serialization; durable rollback-safe recovery; protected dispatch semantics; revision/epoch checks; redaction; and bounded effects. Fake/offline models cannot promote themselves to production authority. Policy mode and actor provenance must be explicitly bound in the reviewed production configuration before any positive path is enabled. Unknown, stale, mismatched, or missing evidence denies or quarantines according to the accepted contracts.

The current entrypoint stays FAKE_DISABLED. CODE_REVIEWED_LIVE_ENABLED and DEPLOYMENT_REGISTRATION_ENABLED remain false. No code activation, secret injection, real Owner receipt, grant/revocation, N01/N02 authority, or provider execution is performed by this amendment.

## Current bounded provenance and operational evidence

Protected GitHub read-only integration independently resolved `TDY0225/nexus-g3-qual` main to `5ccf94c769b7d9a88c0689d8e17b47a9ff506120`, merge of PR #1. Its tree is `4435b88bd03e76698bcfc222b8887655b8d1598d`, containing exactly 19 regular files. Each path, size, and Git blob identity matches the accepted deployment-source ZIP; the retrieved remote bytes are also compared directly and scanned before this checkpoint. The reviewed deterministic ZIP SHA256 is `84796f260303ad64e9982134075a4fadae968c70919d3ffaf17a62be51c78fc3`.

The merge has no returned commit statuses and zero check runs. This does not prove whether Vercel received, skipped, ignored, or failed an event. The accepted repository-side vercel.json has no ignore command, disabled-Git setting, build filter, rewrite, or redirect; it specifies Other/no build command, public output, one function, and security headers. The dependency-free ESM package requests Node 24.x. Project/dashboard settings and Git-provider installation scope are separate evidence and remain unverified.

The Vercel dashboard attempt redirects to login in the available in-app browser. Chrome and Edge inventory attempts fail while loading browser access policy; no credentials are extracted to bypass that failure. No Vercel connector is exposed and no existing vercel executable is found in PATH or the standard user npm command directory. The page's Open Vercel Plugin entrypoint produced no usable connected MCP App. Root cause remains UNKNOWN; no trigger commit, provider-setting change, push, deployment, or live Stytch action is justified from these observations.

Unauthenticated bounded GETs of the public Production domain return a diagnostic response labelled FAKE_DISABLED, DENY, authority NONE, real_admission DISABLED, and live_diagnostic_enabled false. The served homepage and app.js bytes differ from the reviewed source; owner-transient.js returns an HTTP error. This supports the Owner's stale-deployment report and establishes that the current public asset set does not match reviewed main. It does not identify a deployment ID, prove backend source provenance, measure internal credential accesses, or establish the Git-event root cause. Local disabled-startup traps independently establish zero credential-loader, native-transport, provider-operation, and network calls for the reviewed artifact. Public HTTP/GitHub inspection traffic is distinct from those zero offline-provider counters.

The reviewed public pin window is not extended: its existing upper bound is `1791564125000` (2026-10-10 00:42:05 Asia/Kuala_Lumpur). Delivery email remains unregistered; future OTP delivery continues to deny. Neither the time window nor that deliberate absent registration is silently repaired by delegation.

## Checkpoint validation

Only this amendment and deterministic MANIFEST.json addition are eligible for the local policy commit. All historical tracked source, contracts, tests, and documents must match the source checkpoint byte-for-byte under Git's line-ending rules. The deployment source must retain the accepted 19-file digest and disabled startup behavior. The 285 diagnostic, 30 deployment preparation, 134 G3, and 11 isolated package tests must pass (460 total). The existing deployment verifier, secret/private-JWK scan, public/server import checks, documentary policy checks, deterministic manifest validation, and git diff --check must pass. Ignored evidence and unrelated Route D files must not be staged.

No existing qualification status is promoted by documentary completion. Detailed command results, remote inventory, baseline comparisons, and final execution status belong in ignored validation evidence. The local checkpoint message is `g3: adopt delegated executor authority mode`.
