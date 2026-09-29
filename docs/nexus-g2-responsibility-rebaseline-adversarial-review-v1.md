# Nexus G2 Responsibility Re-baseline Adversarial Review v1

Document ID: `nexus.g2.responsibility-rebaseline-adversarial-review.v1`

Version: `1.0.0`

Date: 30 September 2026

Status: **DRAFT BOUNDED REVIEW — NOT OWNER ACCEPTANCE OR QUALIFICATION**

## 1. Subject and result

Subject: [Responsibility Re-baseline Review v1](nexus-g2-responsibility-rebaseline-review-v1.md), 19,171 raw UTF-8/LF bytes, SHA-256 `8220287EDDC1DFE653394E29D53A53B7413168598336907F61493DD65E751B93`. This is a separate threat-focused review of its proposed conclusion A, not a claim that the draft or any execution binding has been accepted. A second Codex agent performed a read-only adversarial pass on the draft; its wording findings were corrected and rechecked by the author, without representing independent owner acceptance. The review uses the accepted [Pre-G2 A0–A6](nexus-pre-g2-architecture-addendum-v1.md), [HQ Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) and [acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md), [Next Host Route Decision](nexus-g2-next-host-route-decision-v1.md), and Route B [P1–P12 contract](nexus-g2-route-b-provider-neutral-host-contract-v1.md) and [acceptance](nexus-g2-route-b-provider-interface-acceptance-v1.md) as controlling sources. No provider research or runtime test was performed.

**Bounded review result: acceptable as a non-authorizing interpretation, provided every exact current route gate retains its STOP effect.** The strongest risk is an overly generous reading of “equivalent”: a platform promise, plan entitlement, unbound hash or guest report cannot substitute for evidence of an applicable enforced property. The draft does not authorize such substitution. A future concrete claim that accepted wording itself prevents an otherwise safe mode would require a named versioned successor, not this review.

## 2. Attempted falsification

| Attack on proposed re-baseline | Failure if mishandled | Adjudication and preserved minimum |
| --- | --- | --- |
| Call a security property “legacy” because its local proof uses Windows APIs. | Secret/control access or substitute code crosses a new Host boundary. | Only the API/fixture is D; HQ1–HQ5 equivalent properties and subject-external evidence remain mandatory. The current local protocol is not relaxed. |
| Treat a provider contract as proof of every applied restriction. | A mutable or ineffective policy is accepted despite drift. | The exact mode, actor set, relevant effective state, freshness, observed negatives and release timing must bind. P3 permits controlled immutability or equivalent drift-safe observation, not configuration-only PASS. |
| Omit a P5 dimension merely because the synthetic task did not visibly use it. | Background work, retention, output/log overflow or another billable path exceeds authority. | Close the reachable operation graph first; each applicable safety/charge dimension gets a hard bound or demonstrated hard composition. Unknown applicability is STOP. |
| Use a monthly/provider plan limit as the Nexus task ceiling. | Shared use, delayed cutoff or residual storage exceeds owner budget. | P6 still requires enforced money or conservative all-in finite maximum plus current account/headroom; Nexus reservations do not enforce provider spend. |
| Treat a cancellation request or process exit as final zero-live state. | Descendants, remote effects or late cost survive. | P7/HQ4 distinguish request, acknowledgement, terminal/zero-live evidence, and effect/cost reconciliation. Query the original unit; keep exposure unresolved while ambiguous. |
| Demand Windows loaded-module inspection inside opaque provider internals. | Endless qualification with no corresponding Nexus property improvement. | Bind Nexus-controlled admitted bytes and the exact supported provider unit/configuration within an explicit provider TCB. Do not require proof against a malicious provider/kernel; do not accept a bare tag, path or guest report as the binding. |
| Downgrade P10 because the control plane runs under the owner. | Guest-modifiable or stale receipts create false admission. | Protect the Nexus writer/record path and bind issuer, unit, operation, config, time and observation gaps. Qualify route-specific custody for the exact supported configuration and revalidate affected proof after material change; do not recursively verify each verifier. |
| Make provider-native session recovery stand in for Nexus checkpoint/recovery. | Revoked authority, stale input or duplicate external effect is silently resumed. | Nexus retains ordered domain state, fresh authority, accepted artifacts, reservations and UNKNOWN effects; native session state is only an observation/input. |
| Interpret “equivalent” as allowing weaker convenience controls. | Prompt instructions, client timeout, soft alerts or post-hoc logs replace hard pre-effect boundaries. | A1–A2/P3–P9 require actual enforcing layer, applicable hard limit and safe release before effects. Any unsupported equivalent remains UNKNOWN/STOP. |
| Add an intriguing new attestation requirement after finite qualification. | A recursive assurance project prevents the accepted useful G2 workflow. | Require a named uncovered threat, affected G2 property, failure of existing controls and smallest extra measure; otherwise classify E. Scope & Exit §9 already supplies this finite exit. |

## 3. Decision test and residuals

The proposed conclusion **A — CURRENT G2 RESPONSIBILITY MODEL IS APPROPRIATELY SCOPED** survives only because the accepted texts already separate portable outcomes from exact-route mechanisms. In particular, Scope & Exit §§2/4/9 permit equivalent cross-Host proof and explicitly keep exact local B gates active until successor acceptance; Route B §§3–5 permit equivalent mechanisms and task-relevant hard compositions. P1/P5/P7/P10 contain wording that could be misread, but this review identifies no concrete accepted universal mechanism that must be deleted to preserve an otherwise qualifying Host. A speculative ambiguity alone does not justify an architecture amendment or provider experiment.

Remaining UNKNOWNs are unchanged: no selected provider, current deployed restrictions/actors/account/billing, full hard exposure, exact-unit cancellation/effects, supported reconciliation, or qualified control-plane custody for a new route. If a concrete candidate later demonstrates that an exact accepted obligation is overstrong while its product property can be preserved, propose a **bounded versioned change naming that clause, threat, replacement evidence and negative tests** for separate owner acceptance. No silent fallback, blanket waiver or automatic qualification follows.

No MANIFEST update, commit, architecture acceptance, provider resource, HQ6 start or G2 implementation is made by this review. Scenario 01–04 NOT RUN; HQ1–HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD.
