# Nexus Governance Advisory Source-to-Derived Consistency Design v1

**Status: bounded offline design/review checkpoint under the accepted advisory-only boundary; no production integration.**

## 1. Demonstrated gap and governing scope

The [accepted advisory boundary](nexus-governance-advisory-integration-acceptance-v1.md) permits continued offline consistency/coverage work. The [compatibility review](nexus-governance-advisory-compatibility-review-v1.md) demonstrates that caller-supplied metadata can produce limited receipt PASS without proving report derivation. Its F/G sources still have mandatory UNKNOWN. The original [representation](nexus-minimal-executable-representation-design-v1.md), [offline design](nexus-governance-offline-evaluator-design-v1.md) and accepted CP1/CP4/ES1-ES6/D01/D02 meanings remain unchanged.

Smallest justified improvement: compare a supplied derived report's exact canonical bytes with a fresh invocation of the already-reviewed offline consumer on the exact supplied source bytes. Preserve that recomputed report and its unknowns. Report the count of source-selected checks when structure is consistent, while explicitly leaving selection completeness and original evidence validity UNVERIFIED. No new assessment fields, source resolver or semantic rules.

## 2. Pure function boundary and byte comparison

Add one standalone prototype module with one public `review_pair(source_bytes, derived_bytes)` function. It imports the unchanged local offline consumer and standard JSON only. There is no production caller, CLI, registry registration, policy DSL, file/environment/network access, evidence retrieval or state write. Inputs must be caller-supplied non-secret immutable bytes; use the same 1 MiB implementation envelope for each input. Wrong type/oversize returns a fixed INVALID_INPUT comparison with no inspection/hash/echo of the supplied values.

Canonical derived bytes mean standard JSON serialization of `review_bytes(source_bytes)`, sorted keys, compact separators, ASCII escaping, no nonfinite values, and one LF terminator. This exact representation is a local prototype comparison convention, not a replacement for GovernanceAssessment canonicalization or the existing evaluation-receipt schema. The supplied derived bytes are not parsed or executed. Noncanonical whitespace, unsupported members, duplicate keys or a different report cannot compare equal. No second parser, exception text, user callback or custom object equality is needed.

MATCH means only exact agreement with the current offline computation on the supplied bytes. It does not establish who generated the earlier report, its historical invocation, the authenticity of either input, a trusted process, original source truth, accepted evidence, completeness, freshness or permission. A hand-constructed identical report can MATCH; that must not be described as independent attestation. A MISMATCH diagnoses inconsistent/stale/modified derived bytes, not malicious intent or a confirmed source defect.

## 3. Fixed advisory output and coverage limits

Output contains only:

- comparison MATCH / MISMATCH / INVALID_INPUT, scoped to byte consistency;
- literal authority none and dispatch_requested false;
- fixed proof scope `recomputed_offline_report_matches_supplied_bytes_only`;
- literal source evidence status UNVERIFIED and selection completeness UNVERIFIED;
- declared check count for structurally consistent input, otherwise null;
- the unchanged recomputed offline report, or null when the input envelope prevents inspection.

No aggregate assessment PASS, CONTINUE recommendation, current authority, trusted-source claim or accepted-evidence flag. Comparison values are local diagnostics, not governance dispositions or security-gate states. The nested report keeps its input-byte hash, positions, unverified PASS claims, required unknowns, failed claims and unknown applicability/profile facts unchanged. Numeric positions remain scoped to those exact bytes; no raw IDs, locators, claims or reference values are echoed.

Coverage count refers only to selected checks whose structure was inspected. It does not mean those human-readable criteria were factually evaluated or that unselected required checks are absent. An empty selected list can have count zero and MATCH while still requiring review with completeness UNVERIFIED. Invalid source structure has unknown count, never zero by inference. An exact matching rejection report stays REJECT_RECORD; MATCH cannot override rejection, UNKNOWN or a source-required dependency.

## 4. Required adversarial tests

Test the complete 19-case corpus, repeat determinism/input immutability, exact serialization, stale/reordered/modified source pairing, altered UNKNOWN/authority/dispatch/count/dependency projections, missing/extra fields, duplicate/noncanonical derived bytes, malformed source, unsupported versions, wrong types and bounds. Explicitly reproduce the compatibility limitation: the fake F report must MISMATCH while a freshly derived F report retains PRESERVE_UNKNOWN. G must retain unproven execution/application. A manually identical report may MATCH without obtaining source trust or historical provenance.

Test no input-controlled object callback/equality, source/derived text echo, locator access or filesystem/environment access by the new function. Shared existing consumer regressions remain required. No network, credentials, real workload, Host qualification or security policy experiment.

## 5. Design challenge and acceptance for implementation

A separate pass by the same assistant challenged hash laundering, invented producer identity, source substitution, falsely complete coverage, cosmetic normalization hiding duplicates, exact rejected-report promotion, source UNKNOWN erasure and automatic gate decisions. Exact recomputation, unparsed candidate bytes, the nested original report, null invalid coverage and fixed UNVERIFIED/zero-authority fields contain those claims. This is deterministic consistency of two supplied inputs, not closing a real-world provenance boundary.

**ACCEPTABLE AS WRITTEN FOR THIS BOUNDED OFFLINE IMPLEMENTATION UNDER THE CURRENT OWNER AUTHORIZATION.** No independent agent/attestation is claimed. Do not modify the accepted consumer or any historical review hash binding; one isolated module and focused tests suffice. No crypto stack or universal receipt framework is introduced; existing JSON and exact-input hashing remain enough for this narrow comparison.

## 6. Continuation and hard boundary

Implement/test/review this exact helper, checkpoint verified results, then use that evidence to specify the remaining production integration responsibilities and rollback/disable behavior as DESIGN only. Do not create a production entry point, register a trusted validator, mutate a lifecycle or fetch source evidence to complete unknowns. A new trust/policy decision or materially ambiguous mandatory conclusion remains STOP for owner review.

A0-A6/P1-P12 unchanged. Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI escalation PENDING. No provider, credentials/secrets, paid action, G2 runtime, amend, merge, push, tag or freeze.
