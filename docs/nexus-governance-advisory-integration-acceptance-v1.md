# Nexus Governance Advisory Integration Acceptance Record v1

Decision ID: `nexus.governance.advisory-integration-acceptance.v1`

Decision version: `1.0.0`

Owner acceptance date: 1 October 2026

Status: **ACCEPTED ADVISORY-ONLY BOUNDARY — NO PRODUCTION INTEGRATION OR EXECUTION AUTHORITY; G2 HOLD**

## 1. Conditional owner authority and exact subjects

The owner explicitly authorizes controlled acceptance of the existing boundary if review confirms the stated invariants. Starting branch: `nexus-v2-g2-development`; HEAD: `27b587e1e779ca06dff26cf1a88503e64e5b73cd`; working tree CLEAN. Starting MANIFEST: 229/229 PASS, SHA-256 `56FD20F5291B6A88473CAB6F649581C312113DD3490AC8DBDA148C308E9B1A73`.

| Accepted subject / bound implementation evidence | Exact LF-normalized SHA-256 |
|---|---|
| [Advisory integration design](nexus-governance-advisory-integration-design-v1.md) | `E85EA44B70FF752E054332E04A80CF0BA9C7489E2138A9C81E326CA7DB8BFF51` |
| [Advisory compatibility review](nexus-governance-advisory-compatibility-review-v1.md) | `E73C39A482003570CCD5FFEDBCF3A07A27C9482D1414F69272DDB90828B58802` |
| [Offline structural consumer](../prototypes/governance_assessment_offline_v1.py) | `388DD5752EB85595036A0399F4BF3C6FD9D56F8E03DB24E7D55ABCB6F24BD80E` |
| [Compatibility tests](../tests/test_governance_advisory_compatibility.py) | `92713C6483FD0797EFA5DE2846776B5EE6610B8151C64D3505058BC20A3C6296` |

The [representation design](nexus-minimal-executable-representation-design-v1.md), [static review](nexus-governance-static-prototype-review-v1.md), [offline design](nexus-governance-offline-evaluator-design-v1.md), [offline tests](../tests/test_governance_assessment_offline.py) and [offline review](nexus-governance-offline-prototype-review-v1.md) were inspected and matched the starting manifest. Seven subject-hash rows in the two prototype/compatibility reviews matched their actual subjects. Historical status/headings remain unchanged; this acceptance supplies the later, narrowly scoped advisory-use overlay, not retrospective production acceptance.

## 2. Acceptance decision and purpose

**A. ACCEPT ADVISORY-ONLY INTEGRATION BOUNDARY.**

Accept the complete source-record / derived-report pair for local, deterministic, offline advisory review within the inspected implementation's structural/uncertainty scope. It can report declared outcomes, missing associations, explicit dependency conflicts and UNKNOWN, and the existing separately scoped receipt tests can report PASS/FAIL for their declared deterministic facts. A new result vocabulary, aggregate assessment PASS, CONTINUE recommendation or semantic rule is not required or implemented by this acceptance.

Accepting the advisory purpose does not promote all possible evaluator features: the current consumer is not an evidence authenticator or semantic oracle. Source-reported PASS remains unverified; a narrow receipt PASS concerns only its actual checks. Omitted coverage, unsupported exclusions, credential-to-authority inference and unreproduced-to-FALSE_POSITIVE claims cannot gain approval. Recommendations, if separately justified within accepted semantics, remain advice, not instructions automatically acted upon.

Superior authority remains [Northstar CP1/CP4/CP5 and ES1-ES6](nexus-northstar-knowledge-promotion-acceptance-v1.md), [D01/D02 acceptance](nexus-cross-project-refinement-d01-d02-acceptance-v1.md), [Pre-G2 A0-A6](nexus-pre-g2-architecture-addendum-v1.md), and unchanged existing [Slice 3B](nexus-post-r5-runtime-integration-slice3b.md) contracts. This acceptance narrows use; it creates no new governance semantics, trust issuer, accepted validator registration or automatic transition.

## 3. Explicit evidence responsibility

| Responsibility | Governing actor / obligation | Evaluator limit |
|---|---|---|
| Source provenance | Authorized source supplier identifies original observation/actor/method/subject and supplied versus observed basis; reviewer checks adequacy under the actual criterion | Input labels, locators or hashes do not authenticate facts; generated output is DERIVED |
| Check selection / coverage | Governing task/reviewer selects applicable accepted criteria and documents omissions; mandatory coverage cannot be waived by record selection | PASS concerns evaluated checks only; absent checks never become PASS |
| Freshness / version / configuration | Source supplier and reviewer preserve/reference bindings required by the actual property and revalidate affected conclusions after change | No automatic freshness or universal timestamp/hash requirement for every task |
| Semantic adjudication | Governing reviewer applies already accepted semantics with bound evidence; disputes/unsupported cases retain UNKNOWN or REQUIRE_REVIEW | Opaque text is inert; parser/structure success does not establish validity or invent policy |
| Authority | Separately valid accepted issuer/owner grant supplies action/actor/subject/scope authority where required | Advice, credentials, capability, receipt, session and checkpoint cannot issue or renew grants |
| Effects and reconciliation | Authorized effect owner supplies accepted observation tied to the original operation and resolves relevant remaining exposure | Attempt/cancel/transport loss/report cannot settle effects/cost or justify unsafe retry |

These are responsibility assignments for interpreting advisory evidence, not new services, mandatory forms, automated evidence fetchers or execution grants. Required missing/stale/contradictory/inaccessible evidence remains unresolved. ASSUMED/PROVIDED declarations alone do not prove independently enforced authority/security/effect properties.

## 4. Derived result rule and unknown preservation

`SOURCE RECORD -> evaluator -> DERIVED ADVISORY RESULT`.

A result can establish what this exact computation concluded about the supplied bytes; it does not independently prove source authenticity/completeness/freshness/truth, execution, application/effect, owner/provider authority, reconciliation or universal correctness. Source scope, applicable dependencies and evaluated coverage must remain traceable. An exact digest proves bytes, not trusted issuance or factual truth.

Keep the entire source and its independent applicability/outcome/reference relationships. Source UNKNOWN/null/FAIL/DEFERRED, missing coverage, cause uncertainty and unresolved mandatory premises are never erased or upgraded by structural PASS or acceptance of this record. Capability remains distinct from authority; EXECUTED from APPLIED; attempted effect from reconciled effect; remediation from validation. An unresolved mandatory dependency blocks its dependent supported PASS; advice cannot release a security gate.

The documented forged-report experiment remains a limitation: existing metadata equality/digest receipts cannot prove report derivation. Acceptance does not close that provenance gap or convert the synthetic corpus to real observations. N02/N05/N07's manual semantic rejection remains unchanged despite their non-accepting offline handling. Bounded offline recomputation/traceability work may investigate consistency, never substitute for independent source evidence.

## 5. Separate adversarial acceptance verification

A separate pass by the same assistant challenged report-authority escalation, derived-as-source evidence, parsing-as-truth, limited-PASS laundering, omitted checks, required-UNKNOWN coercion, capability/authority and execution/effect conflation, fake remediation, unsupported conclusions, stale reports and security-gate release. No separate agent or independent real-world attestation is claimed.

The inspected implementation fixes authority to none and dispatch to false, never follows evidence locators, never executes criteria/text, keeps unverified claims explicit and mechanically refuses its closed structural contradictions. The compatibility tests demonstrate that limited PASS coexists with F/G UNKNOWN and cannot qualify the Host/task. These limits satisfy this exact advisory-only acceptance; they do not satisfy production evidence responsibility by themselves.

**ACCEPTABLE AS WRITTEN FOR OWNER-AUTHORIZED ADVISORY-ONLY ACCEPTANCE.** Current focused verification: 99 tests PASS across offline, compatibility, existing evaluation-contract and quality/evaluation suites. Existing Scout state mismatch, missing `mcp_types` and environment skips remain known baseline limitations; no full-regression/full-green claim or unrelated repair.

## 6. Production prerequisites, deferred work and non-goals

Before any production integration, separately establish exact integration point, source-provenance and check-selection responsibility, required freshness/version bindings, independent authority source, failure/UNKNOWN behavior, effect-reconciliation responsibility, compatibility/version policy, bounded tests and rollback/disable path. A materially ambiguous mandatory evidence conclusion, new trust boundary, policy decision or architecture change requires STOP and owner review. No authoritative or execution-affecting production integration follows automatically.

Deferred: source authentication/freshness and semantic evidence adjudication, completeness of selected criteria, accepted validator/profile promotion, production routing/state transitions, execution/effect verification and automatic reconciliation. Non-goals: generic policy DSL, database, event bus, universal receipt framework, workflow/runtime, new credential facility, UI, provider coupling or G2 runtime.

The owner separately authorizes continued useful offline/advisory preparation that preserves this boundary. Next justified work: design and test exact source-to-derived consistency and bounded coverage traceability in the standalone prototype lane, then define remaining integration prerequisites without connecting production. Each implementation requires reviewed bounded design; no previous qualification authorization transfers.

## 7. Canonical integration and preserved state

Follow the existing additive acceptance pattern: preserve all 229 original entries, add this one record canonically, inspect exact scope, verify UTF-8/LF/references/secret patterns, focused tests, isolated double rebuild and full working/index/HEAD manifest before the acceptance checkpoint. Final hashes and commit identity are recorded externally, not circularly inside this record. No historical artifact, registry or production source is rewritten.

No task/execution/provider/owner authority, external-effect authorization, privileged action, Host qualification, HQ/P PASS or security-gate release is granted. No provider contact/resource/cost, credential/secret access, installation, LPAC execution or security modification. A0-A6/P1-P12 and frozen behavior remain unchanged.

Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI human support escalation = PENDING. No HostAdapter/OpenAIHostAdapter, G2 runtime, amend, merge, push, tag or freeze.
