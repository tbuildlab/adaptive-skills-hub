# Nexus GovernanceAssessment Bounded Advisory Integration Design v1

**Status: design/review checkpoint only; no production integration or promotion authorized.**

## 1. Justification and unchanged authority

The [offline prototype review](nexus-governance-offline-prototype-review-v1.md) validates structural/uncertainty diagnostics, with semantic/source adjudication deferred. The [representation design](nexus-minimal-executable-representation-design-v1.md), [Northstar acceptance](nexus-northstar-knowledge-promotion-acceptance-v1.md) CP1/CP4/ES1-ES6, and [D01/D02 acceptance](nexus-cross-project-refinement-d01-d02-acceptance-v1.md) continue to govern meaning. The owner authorizes bounded integration DESIGN and justified offline follow-up, not production governance promotion or new trust/semantic decisions.

Inspected existing boundaries: [Slice 3B](nexus-post-r5-runtime-integration-slice3b.md), [deterministic evaluation implementation](../ash/evaluation.py), [approved registry](../config/validator-registry.json), and [ecosystem bridge](../ash/ecosystem_bridge.py). Registry definitions are integrity-bound and closed; a parser-only object is not a trusted registry, and the production loader binds an approved semantic digest. The ecosystem bridge separately restricts exact supported profiles/subjects and sealed provenance. No GovernanceAssessment structural consumer is registered there.

## 2. Smallest defensible integration shape

Keep the complete assessment bytes as a non-secret advisory source, accompanied by its exact-input-bound offline diagnostic report. Preserve every declared applicability/outcome, reference, required dependency, uncertainty and unverified PASS. A reviewer can inspect the pair under existing manual governance; there is no new API, profile, resolver, state store, record envelope or authoritative result field.

The report's numerical positions refer to the exact input hash only. The caller must not reuse a report with changed/reordered input, substitute a canonical-object digest for an exact-byte digest, or claim hash equality proves source truth. Manifest inclusion proves repository byte integrity only; it does not register the consumer, establish source acceptance or authorize an action.

| Existing surface | Defensible advisory use | Prohibited inference / change |
|---|---|---|
| Standalone offline consumer | Inspect explicitly supplied non-secret bytes; return structural diagnostics | Production parser/validator registration, criterion execution, automatic gate selection |
| `nexus.validator.schema` | Existing bounded equality/presence checks over selected, explicitly scoped report facts in a synthetic compatibility test | A full GovernanceAssessment schema implementation, evidence authenticity or gate PASS |
| `nexus.validator.digest-integrity` | Existing exact subject-digest comparison | Provenance of the computation or source acceptance merely from a digest |
| `nexus.evaluation-contract.v1` | Retain existing literal proof scope and zero authority for limited declared checks | Map an assessment's PASS/UNKNOWN/N/A/DEFERRED onto aggregate task readiness |
| `nexus.validator.artifact-metadata` | Only with independently established executed-subject evidence as already required | Invent an execution/creator receipt to make a static record eligible |
| Quality/evidence bridge and transition store | Leave unchanged | Apply a validation/state transition, restore execution authority or use prototype results as trusted ecosystem evidence |

## 3. No lossless direct conversion to an existing receipt

The assessment can contain 512 items per prototype list; an evaluation request permits 16 checks. Assessment applicability has REQUIRED/OPTIONAL/NOT_APPLICABLE/DEFERRED/null, whereas the existing check request has a boolean `required`. Assessment diagnostic handling has REJECT_RECORD/PRESERVE_UNKNOWN/REQUIRE_REVIEW, whereas evaluation has PASS/FAIL/NOT_APPLICABLE/INSUFFICIENT_EVIDENCE/INVALID_REQUEST/VALIDATOR_UNAVAILABLE. Their result meanings differ.

Therefore do not flatten, truncate, split into a purported aggregate PASS, coerce null/DEFERRED to false, or replace original applicability/UNKNOWN with receipt result state. Keep the original record and offline report intact. A limited equality/presence receipt can describe only its declared facts; it is not an equivalent full-record validation result. An unlisted obligation still remains unproved.

Existing evaluation may permit an artifact validation-state transition when its selected checks pass; that transition is not applied by the evaluator and cannot be applied to the governed task here. Do not modify the receipt to hide the field or reinterpret its scope. No quality stage, ecosystem proposal, store append or lifecycle promotion is part of this design.

## 4. Justified compatibility experiment, not a production adapter

The next bounded task is a test-only synthetic compatibility check using the unchanged integrity-loaded **hermetic-test registry seam**. This tests existing receipt shape/scope, not production registry eligibility. No new wrapper/adapter/function outside the test file is required.

For a complete fixture record, bind the evaluation subject to the exact record bytes. Use two separate existing receipts: `nexus.validator.digest-integrity` performs one exact digest comparison; `nexus.validator.schema` performs two equality checks for report `structure` equals CONSISTENT and report `authority` equals none. Do not send the digest operator to the schema validator or combine these receipts into an aggregate task result. Explicitly label summaries structural-only. Do not supply expected task PASS, scope grants, effect settlement or required-gap closure. Lifecycle fixtures assert no task execution and carry no fabricated creator/execution/reviewer evidence.

The important falsifiable case is F: structural checks can pass while the original final effect and authority-dependent obligations remain UNKNOWN. Receipt PASS must coexist with PRESERVE_UNKNOWN without modifying source bytes, proving that the receipt's limited result cannot be treated as task acceptance. G similarly must not advance EXECUTED/APPLIED. Additional attacks must cover a changed subject digest, direct-record submission, unsupported validator, prototype-report submission as an evaluation receipt, result substitution, requiredness coercion and the executed-subject metadata requirement.

A caller-supplied report can be fabricated or rebound along with a digest. Existing equality/presence evidence does not independently prove that the report was computed from those bytes. These tests establish API compatibility of bounded facts only, not a trusted observation chain. That remaining provenance boundary must not be silently accepted for production use.

## 5. Adversarial design review

A separate pass by the same assistant challenged report-PASS laundering, loss of UNKNOWN through boolean mapping, omitted mandatory checks, stale input/reordered positions, fake receipt provenance, arbitrary validator names, registry promotion from manifest membership, fabricated execution lifecycle and automatic bridge/state transitions.

Responses are narrow: no direct conversion; retain the pair; keep trusted registry and fixed proof scope unchanged; use only synthetic hermetic tests; never infer task acceptance from metadata equality; no new authority, production route, receipt field or state mutation. Source truth, accepted applicability selection, freshness and semantic rejection still require governing evidence review.

**ACCEPTABLE AS WRITTEN FOR BOUNDED ADVISORY INTEGRATION DESIGN AND THE NAMED SYNTHETIC COMPATIBILITY TESTS.** This internal review is not owner acceptance of a production governance path or independent Host qualification.

## 6. Decision and exact exit boundary

**ADVISORY PAIR IS SUFFICIENT FOR MANUAL REVIEW; LIMITED EXISTING RECEIPT COMPATIBILITY CAN BE TESTED WITHOUT CHANGING ARCHITECTURE.** Continue only to the named test-only compatibility task and factual results checkpoint. Do not add a duplicate evaluation engine, field mapping DSL, production registration or persistent integration.

After that bounded evidence is recorded, a meaningful production continuation would require explicit governance acceptance of how structural-only reports are used, who establishes source/check-selection/provenance/freshness, and whether a separately reviewed trusted consumer/profile is appropriate. Those are not established by this design or current autonomous authorization. Stop before making that policy/trust decision; do not invent unrelated work to extend the run.

A0-A6/P1-P12/D01/D02 and all frozen behavior remain unchanged. Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI escalation PENDING. No provider, secret, credential, paid action or Host qualification.
