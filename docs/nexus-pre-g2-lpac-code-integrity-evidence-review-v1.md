# Nexus Pre-G2 Local LPAC Code Integrity Evidence Amendment — Adversarial Review v1

Review ID: `nexus.pre-g2.lpac-code-integrity-evidence-review.v1`

Version: `1.0.0`

Date: 28 September 2026

Result: **ACCEPTABLE AS WRITTEN FOR OWNER ACCEPTANCE**

Architectural conclusion reviewed: **B. EXACT CI POLICY IDENTITY IS REPLACEABLE EVIDENCE**, exclusively within the specified local LPAC scope.

## 1. Exact subject, method and authority

Subject: [Code Integrity Evidence Necessity and Amendment v1](nexus-pre-g2-lpac-code-integrity-evidence-amendment-v1.md).

Reviewed SHA-256: `c9e53a54610b0818b3efebfe07ef408fc35985dac12fe4721433a6439b6349f9`.

Baseline: `nexus-v2-g2-development`, HEAD `725ca39bbdb1a82902f02da0a26b5a614da96b35`. Preserved V3 manifest: `C359EE0BCA2480A25454D7C0AD5A7544D47BE57428C9008C17FC383519884F4B`.

Method: a separate adversarial document pass by the root assistant after drafting and bounded corrections. This is not a separately staffed agent/human review, runtime experiment, owner acceptance or qualification receipt. No subagent was used. Accepted sources were interpreted through their acceptance records, including historical headings that still say PROPOSED.

Reviewed against Pre-G2 A0–A6, Roadmap G2, G1 policy/conformance, accepted Scope & Exit §§3–9, Evidence Successor §§2.2/2.5, System-Module Provenance amendment/acceptance, Responsibility amendment/acceptance, sealed V3 Protocol v5 §1 and preserved owner-path denial analysis. Microsoft CI-option and policy-rule documentation supports security semantics only. No new Windows-internals discovery was performed to force feasibility.

## 2. Attempt to falsify conclusion B

The strongest objection is that a permissive policy can remain enforced: neither DeviceGuard status nor actual successful launch measures admission strictness. Unknown policy metadata can also hide rule-only drift. If the accepted local boundary relied on a particular WDAC allow/deny rule or guaranteed detection of every semantic policy change, B would be invalid and the subject expressly requires rejection under §7.

The accepted HQ1–HQ5 boundary instead admits fixed, reviewed, protected code through independently bound actual-load observations and verifies token/DACL/input/Job/evidence consequences. CI contributes effective unchanged-security Windows enforcement inside the bounded loader/kernel/owner TCB; it does not replace those independent controls. No approved complete CI content baseline is named as the local admission rule. Enumerating GUIDs/versions without such a baseline would not prove rule strictness either. Changing that administrative-inventory gate is therefore defensible only with the subject's complete replacement contract, scope limitation and explicit residual assurance loss.

The conclusion is not inferred from the inability to run CiTool. It is derived from the accepted threat/property boundary; CiTool denial explains why the current evidence mechanism remains unresolved. Removing that gate alone would not be acceptable.

## 3. Ten requested adversarial challenges

| Challenge | Review finding / subject coverage |
| --- | --- |
| 1. Hidden attack when IDs are unknown | §4 admits lost rule-only replacement/drift assurance. It does not claim a complete inventory or that attack detection is equivalent. Fixed protected admission and actual loaded identity remain mandatory. |
| 2. Weaker policy while enforcement is reported | Explicitly acknowledged. CI2 requires effective native flags as well as WMI; CI1/CI5/CI6 independently close relevant code/resource paths. The combination does not claim the policy is restrictive for arbitrary code. Untrusted policy writers invalidate the TCB/binding rather than receiving an exception. |
| 3. Exact-byte launch value | CI4 proves actual admission on the accepted path, not policy strictness. Refusal STOPs; no bypass/rebuild/sign/elevate rescue is approved. No current launch is assumed successful. |
| 4. Provenance compensation | CI5 preserves strong actual Nexus bytes and actual Windows physical-image/trust basis. It compensates for substitution, not missing kernel integrity, unknown code closure or general arbitrary runtime safety. |
| 5. System TCB dependence on an ID | Same-process physical mapping/build/hash/trust and effective-state evidence are retained. Any newly discovered reliance on specific rules requires abandoning this amendment or a separate decision. |
| 6. Security vs reproducibility | Obtainable metadata remains recorded. Full machine-policy reproduction is explicitly not claimed; task/governance policy bindings remain unchanged. |
| 7. Accepted invariant weakening | §6 changes exactly a CI evidence interpretation/inventory STOP. A0–A6, all mandatory HQ controls and effective CI UNKNOWN/STOP remain. Less inventory/detailed drift assurance is disclosed, not falsely represented as identical metadata. |
| 8. Ordinary-owner dependency | The evidence deficit is specific to this host/current retention; no universal claim that Windows requires elevation is made. No administrator action is requested. |
| 9. Bounded successor | CI1–CI7 are conjunctive, source/time/process bound and falsifiable. Stale WMI, unknown required native state, path exclusion, code ambiguity or incomplete tests STOP. No helper/service/observer expansion is implied. |
| 10. Scope transfer | Only the exact empty-capability four-case local configuration and separately reviewed successor bytes. No network LPAC, E2B, HQ6, production, generic Host or G2 acceptance transfers. |

## 4. Additional red-team cases

| Proposed failure / misleading claim | Required result |
| --- | --- |
| WMI says 2 but native kernel/UMCI enable is missing | CI2 UNKNOWN/STOP or positive enforcement failure; no PASS. |
| Native test-signing/audit/debug/exclusion bit is set | The exact forbidden mask `0x08FA` rejects it. HVCI/VBS baseline is retained. Documentation defines a candidate check, not proof of the current bitmask. |
| Native query result is inaccessible or malformed | Required state UNKNOWN/STOP. No fallback to the old WMI values, signatures or readable policy files. |
| Owner action history alone says no bypass | Corroboration only. OS effective-state, source review, normal actual launch and all provenance/isolation observations are independently mandatory. |
| Query surfaces agree before/after but arbitrary rule changes are invisible | Complete rule-only drift detection is not claimed. Known/observed changes invalidate affected evidence; malicious owner/SYSTEM/kernel is outside the unchanged accepted TCB. A concrete in-scope claim needing those semantics would invalidate B. |
| An unknown DLL is admitted by a weak CI policy | Actual-load closure cannot rely on CI admission; unresolved/unapproved code STOPs before the relevant execution/effect. Bootstrap custody/Windows trust remains the explicit finite TCB, not self-attestation. |
| Verifier or controller fails before a required CI receipt | Preserve UNKNOWN; reconcile original objects through unchanged A–I cleanup rules. Clean process exits cannot fabricate the missing fact. |
| Denied CiTool is relabeled CI PASS after document acceptance | Prohibited. Policy identity stays UNKNOWN; the new bounded observation remains unearned until every required gate is actually satisfied. Current V3 remains STOP and unchanged. |
| Existing V3 is launched immediately after accepting this amendment | Prohibited. Exclusion-path rejection and bracketed/fresh evidence are not established in V3. Separate bounded preparation, exact successor review and explicit execution authorization remain required. |
| A new service or collector is proposed to satisfy timing | Outside this document. STOP for a separate decision; the proposed combination must fit the existing finite roles. |

## 5. Bounded corrections and final re-review

The initial draft was checked for concrete internal defects before this final exact-subject review. Three bounded clarifications were applied:

1. Corrected the Responsibility Amendment Windows TCB cross-reference to §4.
2. Narrowed the machine-policy mutation prohibition so it does not accidentally forbid the already accepted constrained LPAC/profile/Job/synthetic-object setup; alternative controller accounts remain prohibited.
3. Made native enforcement rejection falsifiable with exact enable bits and forbidden mask, including the documented UMCI exclusion-path condition and retained HVCI/VBS state. No existing implementation was changed.

Final re-review found no unresolved blocking documentary defect in the exact subject hash above. It retains the current gate until governed successor adoption, conditional implementation/preparation gates, no inherited release, preserved V3 history and the original failure/cleanup contracts. It clearly separates architecture acceptance, preparation, local runtime qualification, complete Host binding and G2 acceptance. This result accepts a proposal for owner consideration, not its implementation or observed correctness.

## 6. Remaining experimental UNKNOWNs and authority

Full active policy metadata; fresh exact native enforcement/exclusion state; bounded owner-query availability and before/during/after timing; final exact-byte admission outside Codex; actual load graph; effective LPAC token/capabilities/environment/TEMP/handles/resource denials; complete descendants/Job/deadlines/controller/watchdog/verifier-loss evidence; recovery/cleanup and every HQ runtime result remain UNKNOWN or NOT PASS. Historical diagnostic failures and blocked attempts are not resolved by this review.

No accepted/frozen artifact or MANIFEST is changed. V3 is unchanged. No qualification binary, policy-changing negative, AppContainer profile, E2B resource or G2 runtime is executed/created. No privilege, ACL or Windows security-policy change occurs.

**Scenario 01–04 NOT RUN; HQ1–HQ5 NOT PASS; Positive Host Binding ABSENT; G2 HOLD; Option D current; Option A HOLD; A0–A6 unchanged.**

The only next action is owner acceptance or rejection of the exact amendment/review pair. Acceptance would permit planning a separately authorized bounded successor preparation under the proposed evidence design; it is neither implicit implementation permission nor an execution release.

**Final document-review result: ACCEPTABLE AS WRITTEN FOR OWNER ACCEPTANCE.**
