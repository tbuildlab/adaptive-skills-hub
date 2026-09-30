# Nexus GovernanceAssessment Advisory Compatibility Review v1

**Status: synthetic/offline compatibility evidence checkpoint; no production integration acceptance.**

## 1. Subjects and exact binding

This is the bounded follow-up justified by the [advisory integration design](nexus-governance-advisory-integration-design-v1.md) and [offline prototype review](nexus-governance-offline-prototype-review-v1.md). The complete assessment and zero-authority report remain the advisory pair; no alternate governing representation or aggregate result is introduced.

| Reviewed artifact | Exact SHA-256 |
|---|---|
| [Corrected advisory design](nexus-governance-advisory-integration-design-v1.md) | `E85EA44B70FF752E054332E04A80CF0BA9C7489E2138A9C81E326CA7DB8BFF51` |
| [Test-only compatibility implementation](../tests/test_governance_advisory_compatibility.py) | `92713C6483FD0797EFA5DE2846776B5EE6610B8151C64D3505058BC20A3C6296` |
| [Unchanged standalone consumer](../prototypes/governance_assessment_offline_v1.py) | `388DD5752EB85595036A0399F4BF3C6FD9D56F8E03DB24E7D55ABCB6F24BD80E` |
| [Unchanged synthetic corpus](fixtures/nexus-governance-assessment-static-v1.json) | `8070279464078209CBBFA7E0CA8AD834FBC252078471890C7B635F5E3F652908` |

One routine design clarification was necessary: a schema validator cannot perform the digest operator. The tests therefore use two separate existing receipts: one digest-integrity check and two schema equality checks. The corrected design names both explicitly. This changes no assessment semantics, approved registry definition, receipt schema or authority boundary.

## 2. Falsifiable compatibility results

| Attack / question | Observed result |
|---|---|
| F: structural receipt PASS while final effect remains UNKNOWN | Both limited receipts PASS; offline handling remains PRESERVE_UNKNOWN; input bytes unchanged. |
| G: structural receipt PASS while EXECUTED/APPLIED remain unproved | Limited PASS coexists with mandatory unknowns; no capability promotion. |
| All 19 corpus records | Digest receipt can PASS even for a rejected record; schema facts FAIL for structural invalidity. Neither result proves truth or acceptance. |
| Whitespace/byte replacement after receipt creation | Revalidation against the new exact subject digest rejects the old receipts. |
| Fabricated caller report with matching input digest | Limited fact checks can PASS without proving report derivation. This is an explicit trust limitation, not a positive production binding. |
| Record/report submitted as evaluation request/receipt | Closed schema rejection; no implicit adapter. |
| Prototype validator ID supplied by name | Unregistered validator rejected; no manifest/name-based promotion. |
| Null/UNKNOWN/DEFERRED/N/A/integer `required` | Rejected as unsupported boolean mapping; original applicability cannot be losslessly coerced. |
| Static lifecycle with artifact-metadata validator | INVALID_REQUEST: executed-subject evidence required. No receipt invented to overcome this. |
| 17 declared checks | Rejected; no truncation, splitting or aggregate PASS. |
| Digest operator sent to schema validator | INVALID_REQUEST; validators keep their closed purposes. |
| Forged result/authority substitution | Receipt revalidation rejects the tampering. |

Every tested receipt retains `declared_checks_for_exact_subject_digest_only`, zero authority, unapplied transition and synthetic `not_executed` lifecycle. These lifecycle values describe unasserted synthetic test state, not observations of a real workload or claims that physical source files do not exist. The hermetic-test loader does not authorize a production context.

## 3. Final static/adversarial review and tests

A separate final pass by the same assistant reviewed the complete candidate and compatibility design, not only the passing tests. It challenged digest-versus-truth confusion, self-attested derivation, unsupported automatic selection, lost UNKNOWN, false execution lifecycle, registry/bridge promotion, receipt-transition laundering and input-position reuse. No independent agent was used and no independent real-world observation is claimed.

**ACCEPTABLE AS WRITTEN FOR THIS OFFLINE ADVISORY/COMPATIBILITY CHECKPOINT ONLY.** The fabricated-report case deliberately preserves an unresolved production trust boundary. Limited receipt PASS must never be exposed as GovernanceAssessment acceptance, required-property closure or permission to execute.

Isolated snapshot command: `py -3.12 -B -m unittest tests.test_governance_assessment_offline tests.test_governance_advisory_compatibility tests.test_evaluation_contract tests.test_quality_loop_evaluation -v`.

Result: **99 tests PASS**: 28 offline tests, 12 compatibility tests, 43 unchanged evaluation-contract regressions, 16 unchanged quality/evaluation regressions. Corpus subcases additionally cover all 19 complete records. Fixed test/source imports require no network, provider, secret, installation or runtime task. Compilation, UTF-8/LF/reference/secret-pattern/scope checks and canonical isolated manifest rebuild are checkpoint prerequisites. Verification logs and helper scripts are repository-external.

The earlier 57-test governance run remains **52 PASS / 3 SKIP / 1 FAIL / 1 ERROR**, attributable to the known Scout state mismatch and unavailable `mcp_types`. This is not a full-green/full-regression claim. No unrelated baseline behavior was repaired.

## 4. Exact continuation boundary

The authorized static representation, minimal offline design/prototype, adversarial tests, advisory integration design and justified compatibility follow-up are complete. Repeating them or adding a report UI, convenience CLI, duplicate receipt engine, persistence or textual policy interpreter would not resolve the demonstrated trust limitation and is not justified by the anti-bloat rule.

The next meaningful integration step is a governance decision about accepted structural-only advisory use and who establishes source/check-selection/provenance/freshness. The current autonomous authorization explicitly stops before owner policy decisions, architecture acceptance or introducing a trusted consumer/profile. No production routing/registry/state integration is permitted from these checkpoints alone. Stop at that boundary with the prototype usable only as the tested offline candidate.

Recommended next task: owner review of the advisory integration design and this demonstrated limitation; accept/reject the documentary use boundary and determine the separately reviewed evidence-provenance requirements before any production integration proposal. Acceptance of the artifacts alone must not certify assessment claims, grant execution or cross G2 HOLD.

No bounded implementation defect remains unfinished. Semantic authority/exclusion/diagnosis, evidence authenticity/freshness, selection completeness and real effects remain outside the prototype's proof scope. A0-A6/P1-P12/D01/D02 and original accepted files remain unchanged; no sealed qualification package is read, modified or executed.

Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI escalation PENDING. No provider contact/resource, credential/secret access, paid action, HostAdapter, G2 runtime, merge, push, tag or freeze.
