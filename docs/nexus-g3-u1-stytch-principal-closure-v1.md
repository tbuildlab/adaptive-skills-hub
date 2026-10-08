# G3 U1 Stytch Principal closure v1

2026-10-08. Additive qualification; no sign-in, token inspection or API invocation.
Inputs: [D05](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[previous compatibility finding](nexus-g3-u1-stytch-d05-compatibility-review-v1.md),
[bounded context](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md).
Historical findings and every canonical body remain unchanged.

## Evidence and exact candidate mapping

The provider-maintained [JWT helper](https://github.com/stytchauth/stytch-python/blob/main/stytch/shared/jwt_helpers.py)
checks RS256 signatures, project audience and a default project-qualified issuer.
This is documented SDK behavior, not evidence from a deployed Nexus application.
The [Consumer Sessions implementation](https://github.com/stytchauth/stytch-python/blob/main/stytch/consumer/api/sessions.py)
calls that helper and resolves the verified subject into the native user identifier.
It separately resolves the session identifier from session claims. This establishes
Consumer semantics; it does not borrow Connected Apps or machine-to-machine identity.

| D05 field | Exact selected candidate meaning | Qualification |
|---|---|---|
| issuer | Exact native default issuer `stytch.com/<registered-project-id>`, with the actual provider-issued project ID. No added HTTPS prefix, discovery endpoint or invented OIDC issuer. | DEFINED candidate from provider code. The SDK also allows a base-URL issuer; Nexus must reject that alternative for this profile unless separately qualified. |
| client_id | Exact provider project ID used as the verified JWT audience, **only for a dedicated, administratively registered Nexus Consumer application project/environment**. | CONDITIONAL. This is an audience/application identity, not an OAuth client assertion. No arbitrary project label, shared unrelated application project or executor-selected audience is allowed. |
| subject | Exact native `user_id`, equal to verified Consumer JWT `sub` and the remote authenticated Session/User identity. | DEFINED candidate; enrollment and continuity remain unverified. No email, phone, display name, external_id, federation alias or session ID substitution. |

D05 specifies an exact verified issuer/client/stable subject without requiring an
OAuth protocol or an issuer URI. Its existing audience/application interpretation
can represent the actual provider audience; this review does not redefine client_id
as a caller label. A shared Stytch project cannot distinguish relying parties and
is NOT_SUITABLE for this selected mapping. The dedicated project, exact test/live
partition, authorized Nexus application ownership and audience must later be
proved through independent administrator enrollment and isolated live evidence.
No project is registered or selected in this run.

The [User object](https://stytch.com/docs/api-reference/consumer/api/users/user-object)
identifies a native user account. Native ID equality is the continuity rule; a
merge/delete/recreation cannot migrate Owner authority through mutable aliases.
Changed or missing native ID requires local invalidation and new independent
Owner enrollment with increasing owner/binding generations. No permanent
cross-merge ID guarantee is inferred from uniqueness documentation.

## Protected evidence adapter, without a new body

Select compatibility option A: a narrow provider identity-evidence adapter joins
the configured dedicated project and environment, verified exact issuer/audience/
subject, remote Session/User equality and qualified authentication factors.
Principal remains `{issuer, client_id, subject}`. Protected registration pins the
project, native issuer, audience, provider endpoint and application environment.
No provider ID is supplied by an executor or resolved from an approval document.

At page creation, decision POST, receipt creation, AdmissionIntent creation and
DispatchAttempt claim, future N01 must directly authenticate the protected opaque
session with Stytch. Returned JWT claims may substantiate identity only when
signature and exact pinned claims validate and match that remote response.
JWT-only success never supplies positive current-context proof. Direct remote
session authentication provides point-time validity, as described by
[Stytch backend validation](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session).
Do not request duration extension or refresh the Nexus context. The accepted
300000 ms absolute, single-challenge, non-refreshable, cross-restart-forbidden
context remains; enforce the earlier provider/factor/grant/challenge deadline.

Session ID is protected OwnerContext evidence only. Opaque token, JWT, project
secret and cookie are protected runtime material only, not canonical records,
snapshot rows, EvidenceRef strings or logs. EvidenceRef identifies a retained
sanitized assertion; it never embeds bearer bytes or a bearer-derived public ID.
Future persistence must permit proving assertion provenance without preserving
the bearer. A restarted runtime loses token custody and retires the context.

Remote validation at t0 cannot exclude revoke/logout at t1 before local claim t2.
The accepted bounded risk remains ACCEPTED, rather than a continuous-lifecycle
claim. Current local Owner/binding/context/epoch/registration invalidation is
mandatory at every stage and serialized with claim. No lifecycle broker is added.

## Remaining gates and alternatives

Mapping changes from the previous BLOCKED *documentary evidence gap* to
CONDITIONAL on newly reviewed provider code, not to VERIFIED deployment.
The future relying-party adapter can be prepared offline; D01 positive use is
not implementation-ready. Live tests must prove the dedicated application's
registered audience, issuer selection, user/session equality, factor freshness,
wrong project/environment rejection, logout/revoke/account-switch behavior,
Owner enrollment and D04 custody exclusion. Do not run them here.

Option B, an additive D05 compatibility body amendment, is NOT_NEEDED for this
candidate because the native claims fit the existing fields. It would require a
separate version if a qualified application identity cannot fit; never silently
relabel the fields. Option C, reject Stytch while preserving provider abstraction,
remains the fallback if dedicated application or exact claims fail qualification.
OpenAI identity is still BLOCKED and no new capability is assumed.

```text
STYTCH_IDENTITY_PROVIDER = STYTCH_CONSUMER_SESSIONS_CANDIDATE
STYTCH_ISSUER_MAPPING = EXACT_NATIVE_PROJECT_QUALIFIED_ISSUER_CANDIDATE
STYTCH_CLIENT_ID_MAPPING = EXACT_VERIFIED_PROJECT_AUDIENCE_CONDITIONAL_ON_DEDICATED_NEXUS_APPLICATION
STYTCH_SUBJECT_MAPPING = EXACT_NATIVE_USER_ID_MATCHING_VERIFIED_SUB_AND_REMOTE_SESSION
STYTCH_SESSION_ID_LOCATION = PROTECTED_OWNER_CONTEXT_EVIDENCE_ONLY
STYTCH_SESSION_TOKEN_LOCATION = PROTECTED_RUNTIME_ONLY
D05_PRINCIPAL_BODY_CHANGED = NO
STYTCH_TO_D05_PRINCIPAL_MAPPING = CONDITIONAL
D01_IDENTITY = CONDITIONAL
D01_IMPLEMENTATION_READY = NO
REAL_ADMISSION_ENABLED = NO
```
