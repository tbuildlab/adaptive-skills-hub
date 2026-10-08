# G3 U1 Stytch / D05 compatibility review v1

Date: 2026-10-08. Bounded static review, no project/login/token inspection.
Inputs: [D05](nexus-g3-u1-d05-production-authority-contracts-v1.md),
[survey](nexus-g3-u1-d01-managed-identity-session-reuse-survey-v1.md),
[bounded model](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md).

## Result

The existing D05 shape can carry protected identity/session EvidenceRefs and bounded
OwnerContext without bearer material or new fields. The exact selected issuer and
client identity semantics are not yet proved. Structural representability is not
semantic qualification. Mapping remains BLOCKED; no Principal amendment is justified
solely to relabel an API project as an authenticated OAuth client.

| Required mapping | Documented / repository evidence | Disposition |
|---|---|---|
| Provider project/application | Protected SDK configuration selects project_id and secret. Remote response is associated with this configured trust channel, not an executor-selected project. | CONDITIONAL: exact project/environment registration and successful credential-to-project binding must be qualified. |
| Stable user | Remote session/user objects expose user_id. | VERIFIED_CANDIDATE for point-time identifier; continuity under merge/delete/recovery and actual Owner enrollment remain CONDITIONAL. |
| Managed session | Exact session_id/user_id/expiry joins from direct remote authenticate. | VERIFIED_CANDIDATE capability; protected response origin/custody is unverified. |
| D05 Principal.subject | Candidate native user_id, never email/name/external_id. | CONDITIONAL on project partition, continuity and qualified login ceremony. |
| D05 Principal.issuer | Must be exact verified issuer; selected opaque-token response does not expose a reviewed issuer assertion. | BLOCKED. API base hostname or a caller-defined label is insufficient. |
| D05 Principal.client_id | Must be exact verified client/application identity; project_id is not automatically a qualified client_id. | BLOCKED. Do not manufacture an OIDC aud/azp assertion from a project string. |
| OwnerContext evidence | Fixed protected evidence source retains exact provider project/user/session, authentication-factor policy and remote response timing; body carries only EvidenceRefs. | Structurally COMPATIBLE, trust qualification CONDITIONAL. |
| Canonical records | No session_token/session_jwt/project secret/cookie in Principal, OwnerContext, receipt, grant, snapshot or evidence-ref identifier. | COMPATIBLE exclusion requirement; deployment proof depends on D04. |
| Token custody | Retained opaque token only in protected relying-party runtime/session custody, never executor-supplied authority or local JWT fallback. | BLOCKED_BY_D04 until actual isolation is qualified. |

Provider documentation distinguishes direct remote session authentication from local
JWT validation and shows project/secret configuration. This establishes a candidate
transport, not a qualified D05 identity assertion.
[Backend session validation](https://stytch.com/docs/consumer-auth/manage-sessions/validate-session).
The session authentication response exposes user and session identifiers.
[Authenticate Session response](https://stytch.com/docs/api-reference/consumer/api/sessions/authenticate-session).

The review used accepted survey evidence and a bounded read of current official
session validation, authenticate-session and authenticate-jwt pages. Those reads
do not prove that Stytch lacks an issuer/audience mechanism elsewhere; they provide
insufficient evidence for the selected opaque-token path. Absence of a reviewed
mapping is a stop condition, not a claim of product impossibility. OpenAI Host
identity remains the previously BLOCKED reuse alternative; no investigation is
reopened or undocumented Sign in with ChatGPT integration invented.

## Closure path

Before relying-party implementation, identify a documented project-bound issuer/
client assertion or propose a separately reviewed *semantic* mapping profile with
protected issuer/application registration. Prove native user continuity and factor
freshness, then enroll Owner through an independent ceremony. If that profile
changes D05's meaning, a separately authorized explicit additive contract amendment
is required. This run does not silently change the accepted definition. No custom
IAM/OAuth provider/lifecycle broker or PKI is needed to record the gap.

Live qualification must later test wrong project/environment, wrong user/session,
revocation, account switch, factor freshness, token custody and callback origin.
Never store acquired bearer data in the documentary evidence. Until qualified,
all five context stages deny real use even though bounded lifecycle is DEFINED.

```text
STYTCH_D05_STRUCTURAL_COMPATIBILITY = COMPATIBLE_WITH_PROTECTED_EVIDENCE
STYTCH_TO_D05_PRINCIPAL_MAPPING = BLOCKED
STYTCH_SEMANTIC_MAPPING_AMENDMENT_CREATED = NO
EXISTING_D05_BODIES_CHANGED = NO
BEARER_TOKENS_IN_CANONICAL_RECORDS = FORBIDDEN
LIVE_QUALIFICATION_REQUIRED = YES
D01_IMPLEMENTATION_READY = NO
U1_IMPLEMENTATION_CANDIDATE_READY = NO
```
