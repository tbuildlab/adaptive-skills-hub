# Nexus G2 Route B OpenAI-Hosted Agents API Adversarial Review v1

Status: **ACCEPTABLE AS WRITTEN FOR OWNER REVIEW — CLARIFICATION REQUIRED; NO EXPERIMENT**

Review date: 30 September 2026

## 1. Subject and byte binding

This review challenges the exact UTF-8 bytes of [OpenAI-Hosted Agents API Authoritative Candidate Evaluation v1](nexus-g2-route-b-openai-hosted-authoritative-evaluation-v1.md):

- SHA-256: `B6F6AB0933CFFF3E88B84788374FFF22442AD565A430E81F79E9D1A330BA8284`
- Subject disposition: **B. OPENAI CLARIFICATION IS REQUIRED BEFORE A BOUNDED EXPERIMENT**

Any byte change invalidates this review binding and requires re-review. The companion [support question pack](nexus-g2-route-b-openai-hosted-support-question-pack-v1.md) is a proposed unsent clarification plan, not an accepted provider claim.

## 2. Review method and invariants

The review rechecked the subject against the accepted Route B P1–P12 definitions and Responsibility Re-baseline. It attempted to upgrade, downgrade or reject every classification using only the subject’s official OpenAI evidence set. It preserved the distinction between documented requested configuration, provider observation and later effective qualification evidence.

Required invariants remain: default deny; Nexus-owned admission, budget decision, receipt custody, reconciliation decision and qualification state; provider properties require exact Nexus verification/binding; guest/model self-report cannot establish PASS; P7 remains experimental; no C-class prerequisite may be repaired by an unauthorized experiment.

## 3. Adversarial challenges

| Challenge | Attack | Finding |
| --- | --- | --- |
| Hosted means sufficiently isolated | OpenAI provisions a separate Linux workspace and recommends isolated compute. | Hosting and separate workspaces are useful, but no actual image/enforcement identity or complete applied restriction receipt is documented. P1/P3 remain PARTIAL. |
| Requested policy means applied policy | `network.access: "disabled"` explicitly says outbound is blocked. | This establishes request semantics, not same-instance applied-state, freshness, hidden exceptions or mutation exclusion. P3 cannot be SUPPORTED. |
| Disabled network closes all inputs/effects | Optional external channels are excluded in the proposed profile. | Files, model/harness commands, live file mutation, processes/IPC/services and provider-internal channels remain relevant. Disabled network alone cannot close P4. |
| Container size is a hard resource envelope | `small` reports 1 vCPU/1 GB and output/file limits are numeric. | Docs do not state whole-tree hard enforcement/failure semantics or storage/PID/output/wall-clock bounds. P5 remains PARTIAL. |
| One-hour expiry is a hard lifetime | A connected sandbox can be deleted after activity and keep-alives stop for one hour. | “Can be deleted” after inactivity is not a maximum active lifetime and does not cover descendants/controller loss. No upgrade. |
| Client timeout or cancel bounds execution | Cancel input and cancelled terminal events exist. | Stream close does not cancel; no hard cancel/descendant/physical-cleanup deadline is documented. P7 is testable but NOT PASS; P5/P9 remain open. |
| Deletion reconciles effects | Delete returns `deleted: true`. | Official reference limits this to public API removal and permits asynchronous physical cleanup/unpublished output loss. It cannot prove no prior or continuing effect. P9 remains PARTIAL. |
| Artifacts reconcile the operation | Artifacts are immutable, turn-bound and survive environment expiry. | They cover only published outputs; missing artifacts cannot prove no execution/effect, and deletion/retention gaps remain. P8/P9 remain PARTIAL. |
| Signed webhooks/traces are security receipts | Webhooks are signed/retried and traces expose detailed steps. | Webhook events can duplicate and stop retrying after a finite window; trace data appears later and export captures currently available records. Neither binds applied restrictions/deployed revision/cleanup. P10 remains PARTIAL. |
| Stable API resources establish deployment identity | Sessions, environments, turns, items and artifacts have stable IDs. | Resource IDs do not identify the actual image/runtime/policy implementation or loaded byte basis. P1/P12 remain PARTIAL. |
| Key separation closes actor authority | The application key stays outside the hosted sandbox and can be narrowly permissioned. | Project/concurrent/provider actors and active-session revocation propagation are not fully specified. The harness itself legitimately issues commands. P2/P11 remain PARTIAL. |
| Published prices yield a finite maximum | Container rate and model/tool rates are public; optional channels can be disabled. | Rate is not a cap. No hard active lifetime or bounded model-loop/token/retry count exists in the cited contract; usage is best effort and not the bill. P6 remains PARTIAL. |
| Managed recovery resolves ambiguity | OpenAI manages session recovery and saved items survive stream disconnect. | Streams do not replay; idempotency for lost create/input and post-delete/expiry distinction are incomplete. P9 remains PARTIAL. |
| Beta version identifies requalification boundary | Requests use `agents=v1`; agent settings and environment type are visible. | API generation and requested config do not reveal hosted enforcement revision or material-change identity. P12 remains PARTIAL. |
| Codex Cloud can fill missing guarantees | Codex Cloud also runs tasks in managed containers with network controls. | Its user-facing environment docs do not provide a stronger customer Host contract for the missing P1–P12 semantics. Cross-product import would be invalid. |

## 4. Classification re-test

No row survives an attempted upgrade to SUPPORTED. Each row has official positive evidence, so `NOT DOCUMENTED` would discard material facts; none has an authoritative conflict proving the property impossible, so `CONTRADICTED` would overstate the record.

| Property | Reviewed classification | Result |
| --- | --- | --- |
| P1 identity/provenance | PARTIAL | Confirmed |
| P2 authority/actors | PARTIAL | Confirmed |
| P3 applied restrictions | PARTIAL | Confirmed |
| P4 input/effect graph | PARTIAL | Confirmed |
| P5 resource/lifetime | PARTIAL | Confirmed |
| P6 cost exposure | PARTIAL | Confirmed |
| P8 result/effect observation | PARTIAL | Confirmed |
| P9 unknown-effect reconciliation | PARTIAL | Confirmed |
| P10 evidence integrity | PARTIAL | Confirmed |
| P11 credential lifecycle | PARTIAL | Confirmed |
| P12 drift/requalification | PARTIAL | Confirmed |

Final counts remain **SUPPORTED 0; PARTIAL 11; NOT DOCUMENTED 0; CONTRADICTED 0; NOT APPLICABLE 0**. P7 remains **EXPERIMENT-RESOLVABLE / NOT PASS**.

## 5. Question-pack review

The 24 questions are bounded to the exact OpenAI-hosted Agents API mode, each asks one principal semantic, requests official contract/API documentation, separates hard guarantees from best effort and carries no Nexus secret. They cover every open row without asking support to perform qualification. Overlapping identity, lifecycle and receipt questions are intentionally distinct because deployed identity, command identity, cleanup completion and evidence completeness are separate semantics.

No question has been submitted. A support answer would remain evidence to adjudicate; it would not itself authorize or pass an experiment.

## 6. Review verdict and preserved boundary

The subject correctly recognizes a genuine new candidate without treating OpenAI management as qualification. Its proposed exact profile narrows optional channels but does not claim that narrowing is applied or sufficient. The conclusion follows from multiple independent blockers, especially P3/P5/P6/P9/P10/P12; P7 alone cannot advance the candidate.

**Review verdict: ACCEPTABLE AS WRITTEN FOR OWNER REVIEW.**

The candidate result remains **AUTHORITATIVE PREREQUISITES INCOMPLETE** and the disposition remains **B. OPENAI CLARIFICATION IS REQUIRED BEFORE A BOUNDED EXPERIMENT**.

No account, key, authenticated API, sandbox, model call, provider support contact, cost or experiment was used. No accepted file or `MANIFEST.json` was modified. No Host/provider is selected. Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**. No commit, merge, push, tag or freeze is authorized.
