# Nexus Governance Advisory Integration Contract Design v1

**Status: PROPOSED DESIGN CHECKPOINT — not production integration authorization.**

## 1. Accepted basis and exact candidate surface

The [advisory acceptance](nexus-governance-advisory-integration-acceptance-v1.md) permits useful offline/advisory follow-through and preserves separate production prerequisites. The [traceability review](nexus-governance-advisory-traceability-review-v1.md) proves bounded computational pairing, not original evidence truth or complete coverage. The original [integration design](nexus-governance-advisory-integration-design-v1.md) and [representation](nexus-minimal-executable-representation-design-v1.md) keep their declared scopes; no historical record is rewritten.

Exact proposed call boundary: a separately authorized **read-only artifact-advisory caller** supplies two non-secret byte strings to `prototypes.governance_advisory_traceability_v1.review_pair`; it retains the supplied source and derived report and returns/displays the comparison plus unchanged recomputed report to a reviewer. It does not modify an artifact, persist state or perform an action. This design does not choose or create an actual Nexus production entry point. No production caller currently exists for that helper.

Excluded wiring points: [evaluation](../ash/evaluation.py) `evaluate_contract` / `validate_evaluation_receipt`, [ecosystem bridge](../ash/ecosystem_bridge.py) `adapt_evaluation_receipt`, [quality loop](../ash/quality_loop.py) `validate_quality_receipt`, and R2/R4/R5, provider/Host admission or dispatch paths. Those have existing closed schemas/trust/transition purposes, not permission to accept arbitrary advisory reports. Their registry, integrity pins, sealed profiles, receipts and behavior remain unchanged. Do not add a trusted GovernanceAssessment validator/profile as an implementation shortcut.

## 2. Input and evidence responsibilities

| Responsibility | Contract requirement | Remaining limitation / owner decision |
|---|---|---|
| Exact integration point | Only the named pure function candidate, with no automatic downstream decisions | Actual production caller/call site must be separately selected and authorized; no speculative entry point added |
| Input provenance | Authorized supplier identifies original evidence source, actor/method, exact subject/configuration and reported/observed/derived basis under the criterion | Matching bytes prove no issuer or source authenticity; the caller's evidence acquisition/trust policy is not supplied by this helper |
| Check selection and coverage | Governing task/reviewer selects accepted criteria, applicability and necessary evidence; keep full source record, omissions and required dependencies | Check count describes selected structure only; no automatic completeness or OPTIONAL/N/A classification |
| Freshness/version | Preserve binding required by the actual governing property; changed source/configuration/criteria invalidate affected current conclusions | Matching unchanged bytes cannot refresh an old underlying observation; no universal timestamp/hash requirement |
| Semantic adjudication | Authorized reviewer applies accepted meanings; claims need their own source evidence and actual relevant scope | No free-text rule engine, unsupported authority/exclusion/diagnosis oracle or evidence-grade upgrade |
| Authority source | Independently issued, then-valid governing grant where an action actually requires it | Report production, MATCH, source PASS, capability or credential cannot create consent; no actions are taken here |
| Effects | Keep original operation/final state/cost/reconciliation observations separately bound where applicable | Unknown/pending effects remain unresolved; do not query/retry/cancel/settle through this caller |

The same person may legitimately supply and review evidence, but those responsibilities remain distinct and must be attributed. An actor declaration is not independent attestation. Unsupported mandatory conclusions stay unresolved. The production caller's acquisition and trust policy needs explicit review; the current design cannot certify one that has not been selected.

## 3. Advisory failure and uncertainty behavior

| Observation | Required advisory behavior | Prohibited action |
|---|---|---|
| Input envelope invalid | INVALID_INPUT, no inspection/hash/echo, count/report null | Convert refusal to empty coverage or an accepted record |
| Source structurally invalid | Retain REJECT_RECORD; a matching rejection report does not rescue it | Treat MATCH as validity, task PASS or a retry grant |
| Supplied derived bytes differ | MISMATCH with current recomputed report, require review of the pair | Silently replace the historical report, erase its difference or accept stale numeric positions |
| Source-required evidence/dependency UNKNOWN/null/FAIL | Preserve exact source/recomputed gaps; independent governing rules retain their blocked claims | Local metadata PASS resolves a mandatory premise or automatically waives it |
| Applicability unknown or contradictory evidence | Retain original uncertainty/dispute and request scoped review | Default to OPTIONAL/N/A or invent a favorable fact |
| Limited deterministic PASS or MATCH | State exact checked property/proof scope and trace it to source bytes; preserve source claims as unverified | Claim complete governance, execution, authority, Host/HQ/P qualification or universal correctness |
| Helper unavailable/internal failure | No derived result; retain source evidence and required unknowns; bounded content-free diagnostic only | Fabricate a report, echo source/error values or silently fall back to another engine |
| Pending external effect | Report unresolved original operation, observation/reconciliation/cost gaps | Retry unknown effects or infer remote termination/settlement |

These describe advice and preservation of existing governing semantics, not implementation of an automatic allow/block policy. The helper currently returns computational diagnostics only. No CONTINUE recommendation or additional result mapping is necessary; adding one would require its own accepted scope rather than deriving permission from structural success.

## 4. Compatibility and version policy

Supported assessment version remains exact `1.0`; unknown versions/members retain the original consumer's REJECT_RECORD behavior. Source and derived-report serialization are distinct: pair comparison requires the design's exact compact canonical report bytes. No coercion, permissive version fallback, truncation or reuse of an old positional report with changed bytes.

The helper is the named versioned prototype artifact, with implementation bytes bound by its checkpoint manifest/review. Its fixed proof scope does not attest the loaded code/process. A future algorithm/output change needs reviewed version compatibility and new matching expectations; record old inputs/results under their old binding and do not relabel a mismatch as an old PASS. A deployment/caller must separately verify the actual implementation version/bytes if its governing requirement needs that assurance; the helper does not read/hash its own code or mint a trust seal.

Do not map the complete assessment into a `nexus.evaluation-request.v1`: its boolean required field, 16-check bound and outcome semantics cannot losslessly represent the assessment. The earlier two-receipt synthetic compatibility path remains limited metadata evidence, with no aggregate task result or state-transition application.

## 5. Tests, rollback and disable design

Current offline evidence: 111 focused tests PASS; original 19-case corpus, fake/stale/modified/invalid pairs, required UNKNOWN, capability/effect distinctions, null/empty coverage, type/bounds, duplicate/noncanonical report bytes, no I/O/text echo, determinism and existing evaluation/quality compatibility. This is not production integration evidence. Any separately authorized caller would need tests for its exact no-action call path, input attribution, original-byte preservation, unsupported/failure behavior, unchanged UNKNOWN/authority/effects, version drift, disclosure and disable behavior before release.

Current disable action is simply **do not invoke the standalone helper**. It has no production hooks, background process, state, credentials or external effects to undo. Preserve source/report/history and continue existing authorized manual review; manual review does not waive missing required evidence. No removal of accepted history, reset of grades or weakening of gates is needed. This is a design argument, not an executed production rollback experiment.

A future caller must offer an explicit stop-invoking path before it is accepted. Disabling advisory output must leave upstream/downstream authority, required criteria, unknown effects and accepted evidence unchanged. Unexpected authority/state mutation, raw source disclosure, report/source mix-up or result-based gate release requires stop-use, preserve evidence and scoped review. Do not downgrade to a weaker engine or source trust merely to recover availability.

## 6. Separate design review and exact stop boundary

A separate pass by the same assistant challenged automatic decisions from advisory STOP/PASS, source-trust laundering after recomputation, count-as-completeness, hidden production registration, receipt/quality transition reuse, freshness from unchanged bytes and rollback by erasing failed/unknown evidence. The excluded hooks, explicit responsibilities, invariant failure table and no-state disable design preserve the accepted boundary. No independent agent/Host attestation is claimed.

**ACCEPTABLE AS WRITTEN AS A PROPOSED PRODUCTION-PREREQUISITE DESIGN CHECKPOINT ONLY.** It does not accept a production caller or acquisition policy. The computational consistency work is complete; source provenance, actual selected governing coverage/freshness and semantic evidence remain responsibilities of the future authorized context, not UNKNOWNs solved by this report.

The next meaningful step would select/authorize an actual caller and its input/evidence responsibility, then review a bounded production integration proposal. The current owner authorization explicitly states that advisory acceptance does not automatically authorize production integration. Choosing that call site or promoting the prototype into trusted evidence is therefore an owner decision boundary. Stop before implementation there. Further wrappers, fixtures, registries, persistence or UI would not resolve the missing authorization/trust assignment and are not justified by anti-bloat.

Recommended next owner action: approve or reject this proposed read-only artifact-advisory call boundary, including the actual intended caller and its source/coverage/freshness responsibility; no production implementation or execution authority follows merely from acceptance of this design checkpoint.

A0-A6/P1-P12 unchanged. Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI escalation PENDING. No provider/network/resource/cost, credential/secret, LPAC/security change, production authority, G2 runtime, amend, merge, push, tag or freeze.
