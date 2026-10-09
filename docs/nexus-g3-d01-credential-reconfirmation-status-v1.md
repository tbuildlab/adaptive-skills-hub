# Nexus G3 D01 credential reconfirmation status v1

Date: 2026-10-10. Starting checkpoint: `6e26c7324bd1a360141f2ff75cb10abfdda2c14b`. Additive observation after the Owner confirmed private Production configuration. Earlier credential failures and immutable review records are preserved.

## Exact resumed deployment

The existing `LIVE_DIAGNOSTIC_CREDENTIAL_FORMAT` artifact was force rebuilt without source changes to ingest the Owner's updated Production variables. SHA256 remains `8de2147e6edb1489c4089524f3159159c552d60de8dedba17ed478b49c58ce29`, with exactly 19 runtime files. Deployment `dpl_4LW97NBsehyMcEAa1L295UMM4jpq` was verified before promotion, then checked at `https://nexus-g3-qual.vercel.app`. All source UIDs, three public assets, Production project identity, Node 24.x, Other framework, fixed function configuration, application generation 2 and implementation-checkpoint metadata matched. Metadata binds `523a572118892e3ffd414552c4e03a6e6ccdb53e`; subsequent documentary commits do not change the artifact.

The reviewed public keyset and absolute window remain unchanged and were revalidated before staging. No credential variable was read by the executor, pulled to disk, printed, hashed or inspected. Only the protected reviewed runtime uses the two named server variables opaquely. Hosted GET verification makes zero Stytch calls and retains no cookie/CSRF values.

## Single live observation

After stable verification, the existing diagnostic browser page was reloaded to create a fresh bounded context. Exactly one registered email-send action was performed. The sanitized result was DENY / SESSION_INVALID, authority NONE, real admission DISABLED, qualified_live false, with a null context. The backend retired the failed page and its custody. No resend, OTP authentication, TOTP operation, session authentication or revocation was attempted.

In the unchanged transport parser, `failureForStatus(404)` returns SESSION_INVALID for every operation. This attempt was EMAIL_OTP_SEND before any session existed. Therefore the observed enum proves an HTTP 404 from the single fixed native exchange; it is not evidence of an expired, revoked or otherwise invalid provider session. The actual provider error type/message was not retained and the exact 404 cause remains UNKNOWN. The prior 401/403 did not recur in this attempt, but a 404 alone is not sufficient evidence of fully qualified credential permissions or principal authentication.

The [official Consumer email-send reference](https://stytch.com/docs/api-reference/consumer/api/otp/via-email/send) confirms the exact Test POST route and existing-user send behavior. Unlike login-or-create, this endpoint does not enroll a new user. The [official 404 reference](https://stytch.com/docs/api-reference/consumer/api/errors/404#email_not_found) identifies an absent project email association as one possible cause for OTP send. This is a documented hypothesis, not the observed error type. Do not substitute login-or-create, adopt a returned native ID, change the registered Owner, or infer a new binding from email equality.

This attempt contributes exactly one provider exchange. Together with the previous confirmed rejected exchange and the earlier ambiguous readiness action, cumulative calls are bounded to 2..3; the exact total remains UNKNOWN. Claims of zero calls or a fabricated exact cumulative count would be false.

## Closure and exact private boundary

No runtime/source change is needed to preserve this observation. The previous 536-test offline checkpoint remains accepted: 305 diagnostic, 134 G3, 56 artifact, 30 deployment and 11 package tests. These unchanged-code suites are retained, not represented as rerun here. Current closure reruns the 11 package/isolation tests in a fresh explicit-path snapshot, all profile/source scanners and baseline comparison, current public review validation, deterministic MANIFEST validation, and `git diff --check`. Actual MANIFEST count is 426, with byte-identical regenerated output: the unchanged sensitive path rule excludes this document because its filename contains credential. The document remains explicitly tracked and scanned; the rule is not bypassed through renaming. Only this document is added; no ignored evidence, unrelated Route D file, secret or archive is staged. Historical runtime, canonical v1/D05 bodies and all artifact bytes remain unchanged. The initial documentary count expectation of 427 was corrected to the observed 426 before commit.

The next necessary private action is a read-only Owner inspection in the existing P_OWNER Consumer Test dashboard: open the already registered native Owner user and verify whether its email records include the exact reviewed delivery address. Report only SAME_REGISTERED_USER_EMAIL_PRESENT or EMAIL_ABSENT_OR_DIFFERENT_USER. Do not paste credentials, screenshots containing secrets, OTP or session material. Do not create a user, change native ID, alter email records or modify settings during this check. The executor has no established authenticated Stytch dashboard session, and the accepted six-route diagnostic cannot read the provider user registry. Adding a new provider route, guessing identity or retrying the same failed request is not a substitute for this evidence. Any later correction must retain exact reviewed principal semantics and follow the actual finding.

The failed context cannot be reused. After that non-secret finding, continue bounded diagnosis/correction from the reviewed deployment. A fresh send requires a justified corrected prerequisite and a new context, never automatic redispatch. D01 remains unqualified; downstream D03/N01/N02 entrances and real admission remain closed.

```text
G3_OVERALL_STATUS = BLOCKED_PROVIDER_EMAIL_REGISTRATION_EVIDENCE
G3_COMPLETION_PERCENT_ESTIMATE = 0_PERCENT_FULLY_QUALIFIED_RELEASE_GATES_0_OF_13
D01_STATUS = BLOCKED_EMAIL_SEND_HTTP_404_CAUSE_UNKNOWN
D01_GENERATION2_ARTIFACT = VERIFIED_OFFLINE_19_FILES_UNCHANGED
D01_DEPLOYMENT_STATUS = EXACT_SOURCE_AND_STABLE_ROUTING_VERIFIED
D01_LIVE_PROVIDER_STATUS = ONE_NEW_CONFIRMED_HTTP_404_EXCHANGE
EMAIL_OTP_STATUS = SEND_DENIED_DELIVERY_NOT_CONFIRMED
TOTP_STATUS = NOT_RUN
SESSION_AUTH_STATUS = NOT_RUN
SESSION_REVOKE_STATUS = NOT_RUN
ISSUER_STATUS = EXPECTED_MODEL_ONLY_LIVE_NOT_OBSERVED
AUDIENCE_STATUS = CONDITIONAL_LIVE_NOT_OBSERVED
SUBJECT_STATUS = OWNER_REVIEWED_NATIVE_REGISTRATION_NOT_LIVE_AUTHENTICATED
RUNTIME_MAPPING_STATUS = CONDITIONAL
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
COMPLETE_MEDIATION_STATUS = DEFINED_NOT_LIVE_QUALIFIED
EXPIRY_STATUS = OFFLINE_NEGATIVES_PASS_LIVE_NOT_RUN
REVOCATION_STATUS = OFFLINE_NEGATIVES_PASS_LIVE_NOT_RUN
ANTI_REPLAY_STATUS = OFFLINE_NEGATIVES_PASS_LIVE_NOT_RUN
GENERATION_BINDING_STATUS = OFFLINE_AND_DEPLOYMENT_VERIFIED_LIVE_IDENTITY_NOT_RUN
LATEST_SEND_ERROR_CLASS = SESSION_INVALID
LATEST_SEND_HTTP_STATUS = 404
LATEST_404_REASON = UNKNOWN
LATEST_PROVIDER_EXCHANGES = 1
LIVE_STYTCH_CALLS_PERFORMED = UNKNOWN_EXACT_TOTAL_BOUNDED_2_TO_3
RAW_CREDENTIAL_VALUES_ACCESSED_BY_EXECUTOR = NO
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
RETAINED_OFFLINE_TEST_CHECKPOINT = 536_PASS
CURRENT_DOCUMENTARY_PACKAGE_TESTS = 11_PASS
MANIFEST_STATUS = PASS_DETERMINISTIC_426_ENTRIES_BYTE_IDENTICAL
SECRET_SCAN_STATUS = PASS_REVIEWED_SOURCE_AND_ARTIFACTS_ONLY
PRIVATE_KEY_SCAN_STATUS = PASS
CURRENT_BRANCH = nexus-v2-g3-live-qualification
SOURCE_CHECKPOINT = 6e26c7324bd1a360141f2ff75cb10abfdda2c14b
DEPLOYED_IMPLEMENTATION_CHECKPOINT = 523a572118892e3ffd414552c4e03a6e6ccdb53e
REMOTE_STATUS = PRIOR_PUSH_FAILED_GIT_AUTH_UNAVAILABLE_REMOTE_HEAD_UNVERIFIED
G3_REQUIRED_GATES_REMAINING = D01,D03,N01,N02,COMPLETE_MEDIATION,REVOCATION,EXPIRY,ANTI_REPLAY,GENERATION_BINDING,LIVE_PROVIDER_BINDING,SECRET_BOUNDARY,FAIL_CLOSED,FULL_REGRESSION
HUMAN_ACTION_REQUIRED = YES
D04_STATUS = NOT_REQUIRED_UNDER_DELEGATED_EXECUTOR_MODE_NEVER_PASS
```

The final local closure commit is recorded in ignored sanitized completion evidence because this document is itself committed there. No push, main change, merge, tag, freeze or release occurs. The same three unrelated Route D custody-domain documents remain untracked and untouched.
