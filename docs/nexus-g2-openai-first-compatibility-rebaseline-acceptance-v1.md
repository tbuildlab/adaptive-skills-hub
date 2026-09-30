# Nexus G2 OpenAI-First Compatibility Re-baseline Acceptance Record v1

Decision ID: `nexus.g2.openai-first.compatibility-rebaseline-acceptance.v1`

Decision version: `1.0.0`

Owner acceptance date: 30 September 2026

Baseline commit: `11f1e8cff470001fdce8dc057cf59ce3a421da2d`

Status: **ACCEPTED ARCHITECTURE-REVIEW CHECKPOINT — LIMITED CLARIFYING AMENDMENTS ONLY; NO IMPLEMENTATION; G2 HOLD**

## Accepted subjects and exact bytes

The owner accepts the following exact review package and its conclusion as the basis for a future bounded clarifying-amendment phase. The proposed/review headings remain historical; this record supplies repository acceptance. This checkpoint does not itself amend an accepted contract or authorize execution.

| Accepted subject | SHA-256 | Bytes |
| --- | --- | ---: |
| [OpenAI-First Compatibility Re-baseline Review v1](nexus-g2-openai-first-compatibility-rebaseline-review-v1.md) | `CCA9C25D833A1423B026F72C7EE459218D79151A9F23DDA86E078BDF192D6471` | 15,867 |
| [OpenAI-First Contract Minimization Matrix v1](nexus-g2-openai-first-contract-minimization-matrix-v1.md) | `8A291A4A8AFB1644F473368813C13F443AF1650680E1F6C5DFADA014956D2A5E` | 13,785 |
| [OpenAI-First Compatibility Re-baseline Adversarial Review v1](nexus-g2-openai-first-compatibility-adversarial-review-v1.md) | `06BB4F52F56D71D3B3C1C1AEFE17C3D400686D4F04F0192D79E901BD6819BDEA` | 7,917 |
| [OpenAI-First Proposed Minimized Clarification Pack v1](nexus-g2-openai-first-proposed-clarification-pack-v1.md) | `82DA60966F590448CE887519A6819D9577730B13BC7114FDC87E27762B3A5190` | 3,858 |

The adversarial review is bound to the exact main-review and matrix hashes above. Its verdict is **ACCEPTABLE AS WRITTEN FOR OWNER REVIEW — LIMITED CLARIFICATIONS ONLY; G2 HOLD**.

## Accepted conclusion and scope

**C. ONLY LIMITED CLARIFYING AMENDMENTS ARE JUSTIFIED.**

The existing G2 safety model remains fundamentally valid. No broad G2 redesign or security-property removal is accepted. Provider guarantees, Nexus controller enforcement, composite guarantees, bounded qualification evidence and fail-closed behavior may contribute to end-to-end safety where the accepted architecture permits them. Provider-mandatory remote enforcement, resource/lifetime and financial-exposure facts cannot be fabricated or substituted by Nexus.

This acceptance authorizes only the review conclusion as the basis for a future separately authorized, versioned and independently reviewed clarifying-amendment phase. It does **not** itself modify or supersede the accepted G2 Host Contract, P1–P12, A0–A6, Responsibility Re-baseline, OpenAI evidence evaluation or any Host Qualification result.

OpenAI-hosted remains a legitimate candidate, not a qualified Host. Its accepted evidence classifications remain **SUPPORTED 0 / PARTIAL 11**, and P7 remains **EXPERIMENT-RESOLVABLE / NOT PASS**.

## Accepted non-negotiable safety core

The review preserves:

1. Authority, admission and reservation precede side effects.
2. The workload cannot expand its own authority.
3. Controller/API credentials do not enter the workload.
4. Resource and cost exposure is finitely bounded and enforceable.
5. Cancellation request, acknowledgement, terminal cessation, effect reconciliation and settlement remain distinct.
6. UNKNOWN cannot become success or safe retry without reconciliation.
7. Qualification cannot rely solely on guest/model self-report.
8. Qualification binds sufficiently stable public configuration, execution identity and observation scope.
9. Security-relevant drift, expiry, authority/configuration change or missing required evidence invalidates the affected binding.
10. Default deny remains default deny.
11. Qualification does not grant task execution authority.

No acceptance wording strengthens or weakens these invariants.

## Accepted responsibility and adapter direction

The accepted review direction for a future phase is:

```text
G2 Safety Contract
        ↓
HostAdapter
        ↓
OpenAIHostAdapter
        ↓
OpenAI Agents API / managed harness / openai_hosted
```

G2 core remains provider-neutral. OpenAI session, environment, turn, item and artifact semantics remain adapter-specific unless separately justified. This direction does not authorize implementation of `HostAdapter`, `OpenAIHostAdapter`, G2 Runtime or any provider operation.

## Accepted question classification and proposed clarification core

The accepted review classification of the historical 24-question pack is:

- **KEEP:** 5, 7, 9, 11, 13, 14
- **REFRAME:** 1, 2, 3, 4, 6, 8, 10, 15, 16, 19, 20, 21, 23
- **MOVE-TO-NEXUS:** 18
- **MOVE-TO-EXPERIMENT:** 12, 17
- **DEFER:** 22, 24

The proposed six-question provider-side clarification core is:

1. security-relevant configuration mutation boundary;
2. complete enforcement scope and exceptions of `network.access: disabled`;
3. whole-unit hard resource, active-lifetime and controller-loss bounds;
4. managed agent/model-loop, retry, token and tool-step bounds;
5. complete billing dimensions, cutoff/overshoot and finite worst-case financial exposure;
6. post-cancellation physical cleanup, continued work and billing tail.

These questions remain **PROPOSED and UNSENT**. This acceptance grants no OpenAI outreach, support submission, account access, credential use, authenticated API call, environment/sandbox creation, experiment or cost authority.

## Preserved governance state

No accepted P1–P12, A0–A6, G2 architecture, Responsibility Re-baseline, OpenAI evidence or Host Qualification result changes. No Host is selected. Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**.

No amendment implementation, HostAdapter implementation, provider outreach, qualification experiment, G2 Runtime, Windows LPAC reopening, E2B/Modal/Daytona reopening, merge, push, tag or freeze is authorized.

## Repository integration

The source `MANIFEST.json` records the four exact accepted subjects and this minimum acceptance record using LF-normalized source bytes. Portable runtime allowlists and implementation files remain unchanged. One focused acceptance commit records only these five documents and the required manifest additions. This record is an architecture-review checkpoint, not a contract amendment, provider qualification, Host binding or G2 acceptance.
