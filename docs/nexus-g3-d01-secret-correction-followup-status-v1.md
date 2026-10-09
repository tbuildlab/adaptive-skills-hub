# Nexus G3 D01 secret-correction follow-up status v1

Date: 2026-10-10. Starting checkpoint: `6523136fe6c68c6e44daff3e7de6bdd75d1b4295`. This is an additive status capture following the Owner's private configuration correction. Prior failures, public-key review, immutable canonical contracts and original runtime source remain historical evidence.

## Completed work and evidence

The unchanged readiness artifact was force rebuilt to ingest Production variables, verified by all 19 source UIDs and three exact public assets, promoted and checked at the stable origin. One send returned DENY / RETIRED, revealing a proven diagnostic observability gap: mandatory retirement discarded the underlying fixed error enum. No retry occurred. Its provider-exchange count remains UNKNOWN 0..1.

The separately reviewed protocol-status profile preserved the enum while retaining irreversible retirement, DENY, null context/CSRF and no authority. All 521 then-current offline tests passed. Local checkpoint `79042b2b4e03907e4244bc9e866a37dad838a686` records that coherent change. Its exact hosted artifact was verified before and after promotion. Exactly one new-profile send returned AUTH_REJECTED, which the fixed parser assigns only to HTTP 401/403. That attempt proves one native provider exchange, not successful identity qualification or email delivery. The actual provider error type/message, exact status and secret value were not inspected or retained. No second action was submitted to that retired context.

Public official documentation confirmed the Basic/project-secret request shape and exposed a separate local grammar incompatibility: official Test-key examples can include trailing padding. A minimal versioned compatibility profile accepts bounded optional trailing padding and rejects all whitespace, embedded/excess padding, wrong environment, short and oversized input. It never transforms, repairs or guesses a credential. This does not establish the actual Owner key's representation or the cause of AUTH_REJECTED. See [credential format review](nexus-g3-d01-credential-format-compatibility-review-v1.md) and its linked primary sources.

All 536 relevant offline tests passed. Local checkpoint `523a572118892e3ffd414552c4e03a6e6ccdb53e` records the compatibility slice. The final artifact is `LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT`, revision `g3-d01-owner-live-credential-format-v2`, SHA256 `8de2147e6edb1489c4089524f3159159c552d60de8dedba17ed478b49c58ce29`. Hosted deployment `dpl_FVQxLjDjQw5vtTyi67VjcNnurXjK` is Production, Node 24.x, Other framework, exact 19-file source, with unchanged three public assets. Metadata binds the implementation checkpoint and application generation 2. The stable domain is `https://nexus-g3-qual.vercel.app`. Hosted source/routing verification uses only whitelisted metadata/file UIDs and public byte comparisons; it makes zero Stytch calls and does not inspect environment values. No send is performed on this corrected profile until the necessary private credential preparation is confirmed.

The original generation 1 pin and all earlier artifact profiles are unchanged. Generation 2 key fields and review window are unchanged: the review expires at 2026-10-10 23:35:37 Asia/Kuala_Lumpur, with no automatic renewal. The original repository default stays FAKE_DISABLED with false compile/registration gates. Only explicitly reviewed generated diagnostic profiles select Test live IO; none contains Nexus authority or real admission.

## Validation and exact changes

Commands use `D:\DevTools\NexusR2Python\Scripts\python.exe` for `python` below:

```text
node --test tests/*.test.js                         # diagnostic cwd: 305 PASS
python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge  # 134 PASS
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py  # 56 PASS
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py  # 30 PASS
python -B -m unittest tests.test_ecosystem_isolation_package  # fresh explicit-path snapshot: 11 PASS
git diff --check
```

Total unique relevant tests: 536 PASS. The 56 artifact tests include 31 previous tests, 10 protocol failure/retirement tests and 15 credential grammar/custody tests. Source and artifacts pass bounded secret/private-key scans, exact import-closure/client-boundary validation and all preceding profile composition checks. No credential source is scanned or read. Existing runtime files/contracts are compared byte-for-byte after repository newline normalization. MANIFEST is deterministically regenerated and checked from an explicit tracked-plus-accepted static snapshot, with 426 entries expected at this documentary closure. Sensitive path rules are unchanged; ignored validation evidence and unrelated Route D files are excluded.

Exact changed paths relative to the starting checkpoint:

```text
MANIFEST.json
diagnostics/g3-d01-rp/scripts/verify_generation2.py
diagnostics/g3-d01-rp/tests/test_protocol_status_artifact.py
diagnostics/g3-d01-rp/tests/test_credential_format_artifact.py
docs/nexus-g3-d01-protocol-failure-status-review-v1.md
docs/nexus-g3-d01-credential-format-compatibility-review-v1.md
docs/nexus-g3-d01-secret-correction-followup-status-v1.md
```

Branch remains `nexus-v2-g3-live-qualification`. No main modification, push, merge, tag, freeze or release occurs in this follow-up. The prior Git authentication transport remains unavailable; remote branch HEAD is unverified, not silently assumed synchronized. Completed local checkpoints are retained. Final closure commit identity is recorded separately in ignored sanitized completion evidence because this document is itself part of that commit.

Only the same three unrelated Route D documents remain untracked and untouched:

```text
docs/nexus-route-d-successor-custody-domain-adversarial-review-v1.md
docs/nexus-route-d-successor-custody-domain-architecture-v1.md
docs/nexus-route-d-successor-custody-domain-setup-authorization-spec-v1.md
```

## Required status at this capture

```text
G3_OVERALL_STATUS = BLOCKED_PRIVATE_PROVIDER_CREDENTIAL_PREPARATION
G3_COMPLETION_PERCENT_ESTIMATE = 0_PERCENT_FULLY_QUALIFIED_RELEASE_GATES_0_OF_13
D01_STATUS = BLOCKED_AUTH_REJECTED_HTTP_401_OR_403
D01_GENERATION2_ARTIFACT = VERIFIED_OFFLINE_19_FILES
D01_DEPLOYMENT_STATUS = REVIEWED_CREDENTIAL_FORMAT_PROFILE_EXACT_SOURCE_VERIFIED
D01_LIVE_PROVIDER_STATUS = ONE_CONFIRMED_REJECTED_NATIVE_EXCHANGE
EMAIL_OTP_STATUS = SEND_REJECTED_DELIVERY_NOT_CONFIRMED
TOTP_STATUS = NOT_RUN
SESSION_AUTH_STATUS = NOT_RUN
SESSION_REVOKE_STATUS = NOT_RUN
ISSUER_STATUS = EXPECTED_MODEL_ONLY_LIVE_NOT_OBSERVED
AUDIENCE_STATUS = CONDITIONAL_LIVE_NOT_OBSERVED
SUBJECT_STATUS = OWNER_REVIEWED_NATIVE_REGISTRATION_NOT_LIVE_AUTHENTICATED
RUNTIME_MAPPING_STATUS = CONDITIONAL
D03_STATUS = CONDITIONAL_DEPLOYED_ENFORCEMENT_UNVERIFIED_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
COMPLETE_MEDIATION_STATUS = DEFINED_NOT_LIVE_QUALIFIED
EXPIRY_STATUS = OFFLINE_NEGATIVES_PASS_LIVE_NOT_RUN
REVOCATION_STATUS = OFFLINE_NEGATIVES_PASS_LIVE_NOT_RUN
ANTI_REPLAY_STATUS = OFFLINE_NEGATIVES_PASS_LIVE_NOT_RUN
GENERATION_BINDING_STATUS = OFFLINE_AND_DEPLOYMENT_BINDING_VERIFIED_LIVE_IDENTITY_NOT_RUN
LIVE_STYTCH_CALLS_PERFORMED = UNKNOWN_EXACT_TOTAL_BOUNDED_1_TO_2
LATEST_CONFIRMED_STYTCH_CALL_COUNT = 1
RAW_CREDENTIAL_VALUES_ACCESSED_BY_EXECUTOR = NO
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
TOTAL_TEST_COUNT = 536_PASS_RELEVANT_OFFLINE
MANIFEST_STATUS = PASS_DETERMINISTIC_426_ENTRIES_AT_CLOSURE
SECRET_SCAN_STATUS = PASS_REVIEWED_SOURCE_AND_ARTIFACTS_ONLY
PRIVATE_KEY_SCAN_STATUS = PASS
CURRENT_BRANCH = nexus-v2-g3-live-qualification
CURRENT_HEAD = 523a572118892e3ffd414552c4e03a6e6ccdb53e
LATEST_IMPLEMENTATION_CHECKPOINT = 523a572118892e3ffd414552c4e03a6e6ccdb53e
REMOTE_STATUS = PRIOR_PUSH_FAILED_GIT_AUTH_UNAVAILABLE_REMOTE_HEAD_UNVERIFIED
G3_REQUIRED_GATES_REMAINING = D01,D03,N01,N02,COMPLETE_MEDIATION,REVOCATION,EXPIRY,ANTI_REPLAY,GENERATION_BINDING,LIVE_PROVIDER_BINDING,SECRET_BOUNDARY,FAIL_CLOSED,FULL_REGRESSION
HUMAN_ACTION_REQUIRED = YES
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE_NEVER_PASS
```

## Exact next private action

In the Owner's existing private Stytch/Vercel UI, copy/verify the complete current Consumer P_OWNER Test API secret verbatim into the existing nexus-g3-qual Production STYTCH_SECRET variable. Retain any original trailing padding; do not add, remove or guess characters. Do not issue a new key, change project/Owner registration or broaden permissions. Never paste the value, OTP or token into chat. Confirm completion only. AUTH_REJECTED's exact cause remains UNKNOWN until subsequent bounded verification; the public grammar correction is not a substitute for valid provider credentials. After confirmation, resume from the same corrected reviewed artifact: rebuild to ingest the variable, verify exact source/stable routing, then attempt one new diagnostic send and stop at any unavoidable private OTP boundary.
