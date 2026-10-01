# Nexus Read-Only Governance Advisory Caller Integration Review v1

**Status: owner-authorized bounded integration checkpoint; advisory only, with explicit limitations.**

## 1. Exact subject binding and implementation

| Reviewed subject | Exact LF-normalized SHA-256 |
|---|---|
| [Caller selection/design](nexus-governance-advisory-caller-selection-v1.md) | `4F2A09CEAE76A69A8A21E0B8DE0A110443D73D1FC2D707E7172E1E0EEC2ECD04` |
| [Existing CLI caller](../scripts/hub.py) | `6A00981A435410809FDBACE69C93C4F02201560182CCAED6B6960814E6851E8C` |
| [Focused caller tests](../tests/test_governance_advisory_caller.py) | `B8198DF5555A79441D69F39D76011A25B8CDDC7ADDFC30B499EDBD379D3BFBAB` |

The unchanged [consumer](../prototypes/governance_assessment_offline_v1.py), [pair helper](../prototypes/governance_advisory_traceability_v1.py), accepted [advisory record](nexus-governance-advisory-integration-acceptance-v1.md), prior designs/reviews and existing registry/closed runtime contracts remain protected by the starting manifest. The caller's sole existing-source modification is `scripts/hub.py`; no `ash`, transport, validator registry, profile, packager, prototype or previous test is changed. Starting HEAD `84b40bdbe8472130039d52e14bfd0de45e8973a7` was verified CLEAN with 235/235 entries. Frozen tag identities are preserved; all 234 other original entries remain unchanged.

Actual path: existing `main` plan/handoff branch performs ordinary planning/context acquisition/load/validation, then invokes the existing `_plan_handoff`. Its optional `_governance_advisory` display helper selects one already captured explicit project evidence item and calls the original `review_bytes`. The option is rejected outside stateless handoff before acquisition. It cannot fetch the selected path or any reference. No new standalone caller, assessment producer, report store, runtime or trust issuer is created.

## 2. Separate adversarial static pass

This is a separate source/diff/static review pass by the same assistant after implementation, not an independent agent, human acceptance or Host attestation. Syntax compilation emits no bytecode. AST/call inspection confirms that the advisory helper has no file read/write/resolve, environment, subprocess, network, `eval`, `exec`, dispatch or state operation. The final conditional attachment occurs after original plan validation and never feeds planning, fallback, execution or exit status.

| Attack / invariant | Evidence / outcome |
|---|---|
| Invent a caller or duplicate planner | Existing CLI plan/handoff chain and `ContextItem` acquisition traced; one existing display function gains an optional attachment. Core planner untouched. |
| Infer a record/check set from catalog metadata or filename | Explicit selector required; exact unique captured `explicit_task_file` / `project_evidence` only. Existing but unnamed file is not automatically read. No assessment/check factory. |
| Add an arbitrary read / traversal / governing-rule source | Selector rejects noncanonical, absolute, traversal and control-character forms; no selector resolution/open. Non-evidence kind, absence, skipped capture or ambiguity returns null report/PRESERVE_UNKNOWN. |
| Source hash becomes evidence truth or fresh policy | Captured content/length/hash match checked; digest binds captured bytes only. Source evidence/coverage UNVERIFIED; freshness UNKNOWN and subject scope UNVERIFIED in every result. An old capture matching its own hash is never current-source proof. |
| PASS becomes authority or overall validation | Source PASS remains unverified; all returned advice has authority none, dispatch false, outer PRESERVE_UNKNOWN. Existing plan fields/validation unchanged. Existing CLI `Status` concerns plan checks only, never governance acceptance. |
| UNKNOWN/null/dependency failure becomes N/A/PASS | Full corpus matches unchanged original report including required gaps/rejections. Missing dependency/reference/version/malformed data remain non-PASS; no defaults or outcome rewriting. |
| Callable implies executed; execution implies applied; checkpoint settles effect | G and modified G retain unproved execution/application; F retains unresolved effects. No external observer/retry/reconciler or effect claim. Original source remains the supplier's record. |
| Import/failure/version drift produces approval or disclosures | Unavailable import, import exception, evaluator exception, invalid authority/hash/dispatch/handling and changed output envelope return bounded diagnostics with null report. No error/source text forwarded. New top-level report fields or missing fixed fields are refused. |
| Reviewer text/locators are executed, fetched or echoed | Original byte consumer keeps text inert and outputs positions/codes only. Caller selects context without following locators and does not echo selector/source/exception text. Non-secret input is the supplier's explicit prerequisite, not something hashes certify. |
| Circular evidence / self-pairing / self-attestation | No generated report is fed to `review_pair` as its own independent historical evidence. No loaded-code/source identity attestation is claimed; review hashes are checkpoint byte bindings only. |
| Disable bypasses mandatory checks | Omit selector: no attachment/evaluator invocation; all original `validate_plan`, Skill integrity, fallback and handoff fields unchanged. Disabled advice means not requested, never approved. |
| Frozen runtime / provider / privileged coupling | No R2/R4/R5/HQ/provider/G2 path edited or called by the addition. No credentials/network/installation, generic broker or new policy mechanism. |

A concrete static compatibility concern was corrected before this review: checking only zero authority and the digest could allow a future evaluator to add raw top-level fields. The caller now requires the exact current v1 top-level output envelope and refuses schema drift. This is a bounded redaction/compatibility guard, not a second assessment parser or semantic engine. Additional tests cover that correction.

## 3. Tests and limitations

Focused command: `py -3.12 -B -m unittest tests.test_governance_advisory_caller tests.test_governance_assessment_offline tests.test_governance_advisory_compatibility tests.test_governance_advisory_traceability tests.test_evaluation_contract tests.test_quality_loop_evaluation tests.test_v2 -v`.

**178 tests PASS:** 22 new caller tests; 111 prior offline/pair/evaluation/quality regressions; 45 existing planner/CLI tests. All 19 corpus subcases retain their exact mechanical handling; conceptual/manual semantic rejections are not overturned. New tests exercise actual CLI context acquisition/output in a temporary synthetic project, stateless enable/disable, before-acquisition option rejection, captured-file changes, no automatic input discovery, ambiguity, malformed/dependency/version/ref failures, schema drift, import/evaluator errors, privacy, no additional helper I/O, repeated determinism and unchanged plan fields. Temporary test fixtures/mocks are not positive Host or real source evidence.

Bounded governance suite: ecosystem isolation/package, GitHub distribution, quality/evaluation and R5 inventory modules. Current result **57 tests: 52 PASS, 3 SKIP, 1 FAIL, 1 ERROR**. Known baseline/environment attribution remains Scout `evidence_only` versus `recommendation_ready`, unavailable `mcp_types`, and embedded-runtime skips. No installation/fix, full-green regression claim or new attribution research. The release tests use temporary local fixtures; they do not install a provider or modify the actual owner's security environment.

A reused-snapshot rerun additionally produced a package-boundary ERROR (51 PASS, 3 SKIP, 1 FAIL, 2 ERROR). Inspection found an empty `state` directory left by the existing `test_cli_normal_plan_retains_stateful_compatibility`: it deletes/restores its state file but retains the directory. The unchanged packager correctly refuses such a directory. A fresh canonical export rerun restored the 52/3/1/1 result and the package test passed. Both failed and fresh rerun logs remain external evidence. No test, packager, isolation rule or actual repository state was relaxed/deleted to get that result; test groups must use separate clean snapshots.

Canonical manifest rebuild, exact scoped diff, UTF-8/LF/newline/control/trailing-whitespace/reference checks, bounded high-confidence secret-pattern scan, old/new subject bindings and full working/index/committed-manifest verification are checkpoint gates. Final count/hash/commit/test receipts are recorded externally to avoid circular document self-hashing. No scanner/manifest result establishes source truth or runtime qualification.

Remaining limitations: the source supplier/reviewer still owns authentication, mandatory coverage, required freshness/configuration and semantic/effect evidence. No real task record was adjudicated. The portable source archive excludes `prototypes`, so its optional evaluator can be unavailable; refusal is tested and no packaging expansion is claimed. Captured bytes do not attest current filesystem contents, historical invocation or actual loaded evaluator identity. These cannot support mandatory governance acceptance or execution.

## 4. Verdict, follow-through and safe usage

**B. READ-ONLY ADVISORY INTEGRATION VALIDATED WITH DOCUMENTED LIMITATIONS.** The mechanical caller integration is acceptable within this authorization; no general production execution/qualification authority is granted. The selected caller remains selection A after bounded design refinement. No accepted governance meaning, A0-A6/P1-P12 or frozen runtime contract changes.

Directly justified follow-through completed: unique source selection and captured-byte binding, original outcome/coverage visibility, UNKNOWN propagation, unavailable/error handling, default-disable verification, stateless real CLI tests, output-envelope hardening, capture-envelope/no-auto-discovery negatives, prior regression coverage and additive design/review documentation. No further wrapper/feature flag/store/parser/receipt framework is warranted.

For a separately supplied **non-secret** project assessment, the optional local syntax is `python scripts/hub.py plan "Review assessment.json" --project <project-root> --handoff --governance-advisory-context assessment.json`. This is usage documentation, not execution during this checkpoint or a grant to inspect arbitrary confidential content. Use the project-relative forward-slash path already captured because the task explicitly named it. Source supplier preserves the original assessment and its references. Observe the attached report as DERIVED/non-authoritative; review its source independently. To disable, omit the last option and value. Existing manual/mandatory checks still apply.

Rollback only through a later bounded reviewed revert of this caller change and matching manifest; preserve source and historical evidence. No state migration, process, network resource or security setting to undo. Never roll back by dropping a mandatory UNKNOWN or treating a missing attachment as PASS.

## 5. Exact continuation boundary

Mechanical integration/hardening is complete. The next meaningful step is a scoped application to an owner-identified non-secret GovernanceAssessment with actual source/coverage/freshness/semantic responsibility and evidence. Those real facts were not supplied or established here. Do not manufacture a source record from planning metadata, authenticate sources with their own reports, adjudicate missing mandatory facts, or convert advice into a release mechanism. Any such required conclusion needs the responsible source/reviewer and separate governing scope; this integration does not supply it.

Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI human escalation = PENDING. No provider activity/resource/cost, credentials/secrets, LPAC/security changes, HostAdapter/OpenAIHostAdapter, G2 runtime, amend, merge, push, tag or freeze. Tests/static advice are not qualification or authority.
