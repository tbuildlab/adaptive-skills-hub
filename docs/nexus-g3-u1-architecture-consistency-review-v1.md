# G3 U1 architecture consistency review v1

Date: 2026-10-08. Additive precedence and implementation-scope clarification.
Historical accepted files and v1/D05 bodies remain unchanged.

## Precedence and contradictions resolved

| Topic / original input | Current interpretation | Remaining gate |
|---|---|---|
| [Minimal architecture](nexus-g3-u1-minimal-authority-architecture-v1.md) Option C | Still preferred; two new trusted application components N01 and N02. Colocation is a deployment choice, not removal of either responsibility. Libraries/parsers and managed primitives do not become new authority services. | Independent custody and deployment exclusion not proved. |
| [Host qualification](nexus-g3-u1-host-authority-qualification-v1.md), [D02](nexus-g3-u1-d02-host-confirmation-qualification-v1.md) | Existing OpenAI/Codex Host approval integration remains BLOCKED. | No native accept event is upgraded to Owner consent. |
| [N02 amendment](nexus-g3-u1-n02-minimal-confirmation-architecture-amendment-v1.md) | Minimal fixed server-rendered confirmation colocated with N01 is DEFINED; N02 never releases effects. | Browser/session/origin/render exclusion and D01 still unqualified. |
| [Option C qualification](nexus-g3-u1-option-c-deployment-qualification-v1.md) Cognito reference | Historical concrete candidate, superseded for preferred session reuse by Stytch; it is not edited or claimed qualified. | Exact Stytch Principal mapping/factor policy blocked. |
| [D01 lifecycle](nexus-g3-u1-d01-identity-lifecycle-qualification-v1.md) continuous requirement | Cognito continuous ordering stays BLOCKED for the former model. [Bounded amendment](nexus-g3-u1-d01-bounded-owner-context-amendment-v1.md) explicitly removes continuous/instant external invalidation requirements. | Point-time rechecks and mandatory local invalidation remain; residual remote race accepted only as architecture risk. |
| [Managed-session survey](nexus-g3-u1-d01-managed-identity-session-reuse-survey-v1.md) | Complete documentary survey; Stytch preferred candidate, not identity readiness. | [Compatibility review](nexus-g3-u1-stytch-d05-compatibility-review-v1.md) leaves semantic mapping BLOCKED. |
| D03 snapshot hash previously unspecified | [D03 qualification](nexus-g3-u1-d03-recovery-fence-qualification-v1.md) fixes root/page encoding additively. | Closed semantic row schemas, inventory completeness, leader fencing, retention/size rollover and deployment evidence remain open. |
| D04 exclusion/mediation | [Exclusion matrix](nexus-g3-u1-d04-executor-exclusion-and-mediated-dispatch-v1.md) defines 15 surfaces. | BLOCKED without real exclusion proof, including all equivalent provider routes. |
| D05 specification count | Seven immutable outer schemas; eligibility merged into AdmissionIntent. Two DispatchAttempt variants do not create an eighth schema. | Hashes/parsed metadata do not confer protected membership. |
| D05 historical "no implementation" phase | The current overnight authorization permits isolated pure metadata preparation and adversarial tests. It does not authorize N01/N02, receipt acceptance, persistence or positive admission. | Full production schemas/joins and effect-specific payload contracts still need qualification. |

This review cross-checks every accepted G3 document present at the source checkpoint:
Phase 1 survey (`nexus-g3-reuse-survey-v1.md`),
Phase 2A (`nexus-g3-authorization-contracts-v1.md`), Phase 2B
(`nexus-g3-host-approval-bridge-contract-v1.md`), U1 OpenAI/Host reuse probe,
trusted-admission architecture,
Host authority qualification, minimal authority architecture, Option C qualification,
D02 Host qualification, N02 amendment, D05 contracts, D01 lifecycle qualification
and managed-session survey. File existence/names are validated against the actual
repository inventory.
Route D documents are separate custody work, preserved but do not qualify G3.

The N02 amendment's Cognito/OIDC-specific factor/callback statements are historical
candidate mechanics, not a claim that Stytch opaque sessions implement OIDC code
flow. The new preferred managed-session path still owes an exact issuer/client
mapping compatible with D05; that gap is BLOCKED. No API project identifier is
silently substituted for an OIDC client assertion. The earlier OpenAI reuse probe's
"small adapter" possibility was superseded by the later Host qualification's
BLOCKED identity/exclusion finding and the explicit custom-minimal-N02 decision.

## Deadline and restart clarification

Challenge: exclusive deadline <= issued_at + 300000. Context: <= authenticated_at
+ 300000 and <= challenge/session/factor deadlines, one challenge/consent lineage,
no refresh or cross-restart use. Receipt: <= accepted_at + 600000 *and* current
context expiry; the longer upper cap cannot extend the five-minute context.
Future linked grant: finite expiry <= receipt/context and acceptance + 600000;
historical v1 integers are not silently reinterpreted. Intent: <= evaluation +
60000 and every receipt/grant/context/task/Host/GateFact deadline. Claim/handoff:
<= all current bounds; no post-fence deadline extension. Equality at expiry denies.

OwnerContext single-use consumption is terminal consent plus at most one claim
lineage. It does not erase context evidence before its own linked claim recheck.
View replacement retires the previous view/challenge; no extra confirmable tab.
Local logout/generation change retires before later serialized claims. External
logout/account switch cannot be promised instant knowledge under the accepted
bounded model. A newly remote-authenticated still-valid session is not fresh human
authentication; factor freshness and Owner enrollment remain separate.

Restart or epoch/incarnation change retires pre-restart contexts/views/grants and
unclaimed intents. Persistent revocation, nonce/receipt and claim tombstones survive;
UNKNOWN attempts never redispatch. D03 does not reopen a restored matching prefix.
Independent full latest history and exact control state are required before an
independently authorized recovery transition. No old fixture or Host candidate can
be promoted to production by wrapping, copying or restoring it.

## Implementation preparation boundaries

Only isolated untrusted metadata parsing/canonicalization may be implemented now.
Seven exact outer field sets/closed variants, typed refs and selected self-contained
nested validations can be checked without any authority state. Successful parsing
must remain explicitly UNTRUSTED with semantic/provenance joins unresolved. No
production consumer, public API, CLI or dispatcher imports this preparation module.

Protected semantic validation is a separate future step: current issuer, enrollment,
source authenticity, qualified target/payload contracts, exact scope/account effects,
registered view digest, record membership, grant provenance, complete revocation
index, current eight gates and full checkpoint/control readback. It cannot be
implemented as a positive fallback using a synthetic resolver or fixture flag.

For R05 DENIED metadata, the Section 3 vocabulary's success codes are explicitly
`CONFIRMED, INTENT_PENDING, CLAIMED, COMPLETED`; remaining listed failure/retirement
codes are eligible, sorted/unique, subject to protected semantic justification.
This clarifies the existing vocabulary without adding codes or fields. `FAILED`
and `RETIRED` are non-positive statuses; parser acceptance never issues a DENIED
authority record. No production-positive state-machine or adapters are prepared
while the storage row schemas, issuer mapping and D04 exclusion remain blocked.

```text
CONSISTENCY_REVIEW = COMPLETE_WITH_EXPLICIT_GAPS
NEW_TRUSTED_COMPONENT_COUNT = 2
PRODUCTION_CONTRACT_COUNT = 7
EXISTING_V1_D05_BODIES_CHANGED = NO
D01 = BLOCKED_IDENTITY_WITH_DEFINED_BOUNDED_CONTEXT
D02 = HOST_BLOCKED_NEXUS_N02_DESIGN_DEFINED
D03 = CONDITIONAL
D04 = BLOCKED
D05 = DEFINED_SPECIFICATION_ONLY
FIXTURE_TO_PRODUCTION_PATH = NONE
COPIED_RECORD_BEARER_AUTHORITY = NO
REAL_ADMISSION_ENABLED = NO
```
