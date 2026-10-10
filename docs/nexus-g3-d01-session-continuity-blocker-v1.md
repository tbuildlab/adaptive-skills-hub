# D01 TOTP reply continuity blocker and compatibility review

Date: 2026-10-10. Source checkpoint: `33cba4ebaa62c60bcfc8046843a56924d08450a3`.
Disposition: observed qualification blocker; compatibility proposal only, not an accepted amendment or runtime change.

## Exact observed boundary

The Owner completed the fresh current-factor ceremony on the reviewed stable diagnostic deployment. The visible sanitized result is `DENY / IDENTITY_SESSION_TOTP_REPLY`, context expiry null, authority NONE, admission DISABLED and qualified_live=false. Controls are disabled. The context has been retired, its private token/session custody cleared, and no replacement ceremony is initiated in this closure. Sanitized JSON and a screenshot cropped to the evidence panel are retained only in ignored validation state. No OTP, TOTP, raw token/JWT, cookie, private identifier, QR, setup key, recovery material or provider response was inspected or retained by the executor.

The deployed source is the independently verified 20-file artifact SHA256 `58ac4a85ee81093f77fb5f4c023a695ba1b08030a3fee8a5ee0f48f225cc3a47`, deployment `dpl_CMjDbhhZddL3qnnHWbPqKZ5vib1m`, revision `g3-d01-session-continuity-stage-v7`, application generation 3. The last independent source UID/public asset verification is retained at the source checkpoint. This turn does not repeat deployment, provider authentication, enrollment or mutation.

| Predicate / operation | Evidence and exact limit |
|---|---|
| Primary OTP bootstrap | Source control flow requires a successful fixed Owner OTP proof before this TOTP operation can run. This is inferred from the verified source plus the phase label, not a separately retained OTP response. |
| Direct pre-TOTP session check | Passed the same User/session/token, primary time, expiry and factor checks; otherwise the operation cannot reach TOTP_REPLY. This is control-flow evidence, not a raw packet trace. |
| Fixed TOTP request | Source supplies retained native User and session_token, transient human code and duration 15 minutes to the fixed Test endpoint; no browser session selection, redirect or retry. Actual bearer values are not inspected. |
| Returned native Owner, active/unlocked state, factors, expiry, signed identity and token shape | These checks precede the failing continuity guard and therefore passed for this response. Two fresh factors were present according to the unchanged projection. This does not establish every factor lineage requirement. |
| Returned session continuity | Failed at TOTP_REPLY. Both projected User identities must already equal the fixed registered native Owner; therefore the differing session_id is a source-level conclusion. Exact IDs were not observed. |
| Returned token equality and unchanged primary factor time | UNKNOWN: checked after the failed guard, so neither may be asserted. |
| Direct two-factor postcheck and five lifecycle observation points | NOT_REACHED; no positive current-context qualification exists. |
| Provider cause | UNKNOWN. The observation does not prove intentional rotation, unsupported attachment, ignored fields, or a universal Stytch limitation. |

Do not retry the same retired context, recreate an enrollment, delete the verified factor, or ask for another code merely to reproduce this refusal. No real Nexus OwnerContext, receipt, grant, revocation, intent or dispatch is issued.

## Documented capability versus deployed behavior

The [official Consumer TOTP reference](https://stytch.com/docs/api-reference/consumer/api/totp/authenticate) documents an existing session_token input and duration-based session extension. Its response schema includes native User/session identifiers, factor timestamps and nested email/TOTP factor references. Those fields are documented candidates; their exact deployed relationships are not established by the sanitized refusal.

The [official session management article](https://stytch.com/blog/session-management-best-practices/) describes the opaque session_token as static during a session. That statement does not prove equal tokens in this failed response or authorize treating different native session IDs as one session. No reviewed official source explains the observed change sufficiently to waive the accepted guard. Consumer and B2B intermediate-session semantics must not be conflated. No provider support message is sent and no account setting is changed.

## Accepted contract that prevents automatic continuation

The [accepted adapter review](nexus-g3-d01-live-stytch-adapter-offline-review-v1.md), operation table, requires the “same native user/session/token and unchanged email-factor time.” The [live setup plan](nexus-g3-live-qualification-setup-plan-v1.md) explicitly blocks the factor-policy case when same-session continuity is missing. The [phase attribution review](nexus-g3-d01-session-continuity-stage-review-v1.md) permits labels only, with no different session/token adoption. These requirements are preserved. D01 is BLOCKED for the current factor-policy composition; this is narrower than rejecting Stytch as an identity provider in every architecture.

The [bounded OwnerContext architecture](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md) requires fresh qualified human factors before an authoritative context is created, then one fixed managed session per context with no refresh/restart reuse. That ordering suggests a possible compatibility design, but it does not silently override the stricter accepted diagnostic bootstrap contract.

## Concrete options

| Option | Scope and disposition |
|---|---|
| A: retain the current contract | Keep refusing; seek an official explanation of Consumer TOTP session attachment and ID behavior, using sanitized facts only. Do not claim provider support access exists. If a bounded wire/configuration defect is proved, fix it under the unchanged contract. There is currently no proved local omission to fix. |
| B: separately versioned pre-context MFA final-session establishment | Candidate for Owner architecture review. Permit one explicit final session binding during the human MFA bootstrap, before any authoritative OwnerContext exists. Require the complete guard set below and new offline/live qualification. It is not implemented, accepted, or a present positive path. |
| C: retain provider abstraction and reject this Stytch composition | Available if A cannot establish equal-session behavior and B cannot prove sufficiently bound fresh-factor evidence. Do not invent another identity provider, PKI, broker or generic IAM platform to force progress. |

Recommended review target: B, because it can keep the authoritative OwnerContext fixed after qualified MFA and preserve the existing D05 Principal and context bodies. Selecting it requires a separately accepted compatibility amendment to the diagnostic factor-policy contract. Owner approval alone cannot prove the provider evidence or D04 exclusion; missing required evidence still denies. A remains available without any contract change. This document does not choose a weaker acceptance predicate merely to mark the gate passed.

## Guard set for option B, if separately accepted

1. Keep a server-owned, single-use MFA bootstrap with exact registered Principal, Owner/binding/application generations, origin, review/deployment revision, one pending ceremony and absolute original page deadline. Primary-only state has no Owner confirmation or effect authority. Browser/caller cannot provide an issuer, User, session, token, factor, generation or replacement context.
2. Authenticate OTP to the fixed native Owner. Freeze the exact email method/factor reference, primary authentication time and original deadline. Require an unambiguous currently verified Owner TOTP reference from protected provider evidence; absent, ambiguous, mismatched or undocumented factor references deny. Email address, external_id and display name remain non-authoritative.
3. Directly recheck the retained primary session immediately before the one TOTP request. Recheck local generations and deadline. Send only the existing fixed native User/retained opaque token plus human code and allowed initial duration. No fallback endpoint, duration trick, JWT-only bootstrap, automatic retry or second enrollment.
4. Treat the direct authenticated TOTP response as a pending candidate, not current context authority. Validate exact project/environment and native Owner, pinned signature/issuer/audience/subject, active/unlocked status, exact two-factor set, both factor IDs, unchanged primary factor time, fresh TOTP time and exclusive bounds. Require the candidate itself to contain both factors; never aggregate independent one-factor sessions. Compare factor time losslessly at provider precision while flooring deadlines conservatively; millisecond truncation must not manufacture equality. Missing evidence denies.
5. Only this one in-flight server-originated response may propose the final session/token. Perform a new direct remote authentication of that candidate, with no duration/custom claims. Demand exact candidate User/session/token, factor IDs/times/expiry and all fixed identity checks in the postcheck. Recheck local generations, retirement, original deadline and clock high-water before finalization. Postcheck failure or uncertainty retires the entire bootstrap; no candidate is adopted, reused, retried or restored.
6. Finalize once under protected serialization, only before authoritative OwnerContext creation. Preserve the earliest original primary/page/factor/provider deadline, maximum 300000 ms, no refresh and no restart continuation. The final qualified session is then fixed for all page/decision/receipt/intent/claim rechecks. Any later session/token/factor change denies. No active OwnerContext rebinding is allowed, and no pre-MFA bootstrap can be promoted to a trusted receipt or grant.
7. Private old/candidate bearer custody exists only in the protected runtime; no bearer bytes or public bearer-derived hashes enter canonical records, logs, evidence or backups. Both failure and restart clear custody. Primary bootstrap has no Nexus authority even if its external provider session temporarily remains active. Any provider cleanup would target exact privately retained bootstrap identity, be separately specified, never broad-user revoke, and never turn an UNKNOWN cleanup into a retry or qualification pass.
8. Preserve D05 Principal issuer/client_id/subject, all seven production bodies, the closed control schema and its fixed final provider_session relation. Any new bootstrap assertions belong to separately versioned protected pre-context evidence, never copied bearer authority. Real positive N01/N02 paths remain blocked by D01/D03/D04 and all other mandatory gates.

Unresolved B prerequisites: exact primary factor/time continuity, nested native factor-reference availability and equality, candidate token behavior, direct final-session stability, race/crash/retirement tests, complete managed lifecycle tests, and D04 custody. The observed TOTP_REPLY failure does not satisfy these prerequisites. No implementation or new live attempt follows this draft automatically.

## Closure and remaining boundary

No runtime, accepted canonical body, registration, generation, public key, review interval, provider factor, deployment setting or policy is modified in this documentary closure. The original public review interval must not be extended or restarted while awaiting a decision. D03 deployed fence enforcement and D04 effective exclusion remain unqualified; dependent positive N01/N02/E2E work cannot bypass the failed D01 factor gate. Independent offline architecture/schema/fake preparation is already covered by the accepted offline closure checkpoint and is not repeated.

The next necessary decision is whether to authorize a separately versioned option-B compatibility amendment and its bounded diagnostic qualification preparation. This is an accepted-contract boundary, not routine phase-transition approval. Until then the current equal-session refusal remains active. No further OTP/TOTP entry is needed now.

Documentary closure validation passed: required status fields matched the saved sanitized response; the exact reviewed artifact hash was reproduced; every previously tracked source/contract/document byte remained unchanged after newline normalization. The 134 G3 regressions, 13 phase-attribution tests and 11 isolated package tests were rerun and passed (158 subset tests, not new additions to the 902-test complete offline baseline from the source checkpoint). Commands: `python -B -m unittest discover -s tests -p test_g3*.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_session_stage_artifact.py`; and `python -B -m unittest tests.test_ecosystem_isolation_package` in a fresh accepted-file snapshot. Bounded secret/private-field scanning, client/server boundary, deterministic MANIFEST and `git diff --check` passed. MANIFEST remains byte-identical at 485 entries; its unchanged sensitive-path rule excludes this session-named document. Only this additive document belongs to the checkpoint. Ignored evidence and the three unrelated Route D documents remain excluded. No runtime code changes, new tests, live calls, enrollment, deployment or provider mutation were performed in this closure.

```text
OBSERVED_DIAGNOSTIC_RESULT = DENY_IDENTITY_SESSION_TOTP_REPLY
PRE_TOTP_REMOTE_RECHECK = PASSED_BY_VERIFIED_CONTROL_FLOW
TOTP_REPLY_SESSION_CONTINUITY = FAILED
TOKEN_CONTINUITY = UNKNOWN_NOT_REACHED
PRIMARY_FACTOR_TIME_CONTINUITY = UNKNOWN_NOT_REACHED
PROVIDER_ROTATION_CAUSE = UNKNOWN
POST_TOTP_REMOTE_RECHECK = NOT_REACHED
D01 = BLOCKED_CURRENT_SAME_SESSION_FACTOR_POLICY
COMPATIBILITY_PROPOSAL = PRE_CONTEXT_MFA_FINAL_SESSION_ESTABLISHMENT
COMPATIBILITY_AMENDMENT_ACCEPTED = NO
POST_CONTEXT_SESSION_REBINDING = FORBIDDEN
D05_BODIES_CHANGED = NO
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
NEW_PROVIDER_CALLS_THIS_CLOSURE = 0
RAW_CREDENTIAL_ACCESS = NONE
HUMAN_ACTION_REQUIRED = ACCEPTED_CONTRACT_COMPATIBILITY_DECISION
```
