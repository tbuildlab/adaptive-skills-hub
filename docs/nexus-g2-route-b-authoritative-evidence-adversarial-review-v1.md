# Nexus G2 Route B Authoritative Evidence Adversarial Review v1

Review ID: `nexus.g2.route-b.authoritative-evidence.adversarial-review.v1`

Version: `1.0.0`

Date: 30 September 2026

Status: **PROPOSED INDEPENDENT DOCUMENTARY REVIEW — NO PROVIDER SELECTION OR EXPERIMENT AUTHORITY**

## 1. Exact subjects and review boundary

This review challenges these exact UTF-8 draft bytes:

| Subject | SHA-256 before this review | Bytes |
| --- | --- | ---: |
| [Provider Authoritative Evidence Acquisition v1](nexus-g2-route-b-authoritative-evidence-acquisition-v1.md) | `C7A9C60F1BDFDD3AD5E13DBCD347A51F82C4B0BEE1BD8C18EC6D4308F28528AE` | 27,836 |
| [Provider Support Question Pack v1](nexus-g2-route-b-provider-support-question-pack-v1.md) | `D7FC17B5EC014C604F8BA6DF0653B853951ECCAC9A77F9C6E2F98F9D1FE338F9` | 11,387 |

The governing requirements are the accepted Route B P1–P12 contract, provider fact matrix, Responsibility Re-baseline and UNKNOWN Resolution Matrix. The review tests provider-side authoritative closure only. It does not treat official documentation as effective-instance proof and does not add a new Host requirement.

## 2. Review questions and findings

| Challenge | Finding |
| --- | --- |
| Exact provider mode is mixed with another product/backend | **PASS.** E2B is fixed to secured create-v2/native envd; Modal to ordinary CPU gVisor Sandbox and standard interfaces; Daytona to hosted container Sandbox and organization toolbox. Excluded modes are explicit. |
| Marketing or generic feature text is treated as a guarantee | **PASS.** Classifications rely on official API, security, lifecycle, billing, SDK or provider-maintained sources. Marketing/pricing material is used only for its published rate surface and never alone to close a mandatory control. |
| Requested/stored configuration is treated as applied state | **PASS.** P3 remains PARTIAL for every provider. Successful create/update and GET fields are not called effective-policy receipts. |
| Guest output is treated as independent evidence | **PASS.** P10 remains PARTIAL; route-controller custody and provider cross-checks remain future prerequisites. |
| A timeout or cancellation acknowledgement is treated as complete effect termination | **PASS.** P5 remains PARTIAL, P7 remains unrun, and descendants/controller-loss/unknown effects remain separate. |
| Deletion or not-found is treated as positive no-effect evidence | **PASS.** P9 remains PARTIAL for all providers. E2B's ambiguous 404 and each provider's lost-create/result gaps are explicit. |
| Published rates, credits or an alert are treated as a hard money ceiling | **PASS, with one narrow supported composition.** Modal and Daytona P6 remain PARTIAL. E2B P6 relies only on fixed CPU/RAM allocation, official per-running-second formula, included disk and destructive fixed timeout in the no-extra-feature mode. It does not rely on the dashboard spending limit. |
| API-token scope is treated as the complete actor set | **PASS.** E2B P2's supported provider half still requires current actor/key custody as Q. Modal P2 remains PARTIAL. Daytona P2 explicitly records organization-wide toolbox authority and the unproven personal-organization composition. |
| One API/SDK identifier is treated as a hosted deployment revision | **PASS.** P12 remains PARTIAL for all three providers. Build, image, envd, SDK and daemon labels are not promoted to complete backend-policy identity. |
| Provider telemetry is treated as complete or infallible | **PASS.** Webhook retries, event retention, dropped/best-effort telemetry, missing exec audit coverage and unknown retention remain limitations. |
| P7 is silently converted to PASS | **PASS.** P7 stays A-class experiment-resolvable, outside the closure counts, and unrun. |
| An experiment is justified when one or two rows are supported | **PASS.** Eligibility requires all eleven mandatory C rows. Every provider remains INCOMPLETE. |

## 3. Challenge to each SUPPORTED result

Only two rows are marked `SUPPORTED`; both are E2B-specific.

### 3.1 E2B P2 authority separation

**Challenge:** `envdAccessToken` is broad filesystem/command/controller authority, not an exec-only capability. Workspace/project members and project keys can also control the Sandbox. Could the classification hide concurrent authority or leak control into the workload?

**Resolution:** The provider-side semantic is sufficiently explicit to define two planes and the complete documented credential classes: project API key for Platform control and Sandbox-specific envd token for the data plane. The row does not claim fine-grained project roles or actual actor exclusion. It makes current member/key inventory, owner-controller custody, guest non-reachability and the envd token's inability to call Platform mutation Q gates. The restricted subject must not receive the project key. This is a meaningful, falsifiable future composition, so `SUPPORTED` survives. Any undisclosed runtime-capable actor or guest-reachable project key is STOP.

### 3.2 E2B P6 hard exposure

**Challenge:** A spending limit is not documented as a hard cutoff; timeout can be reset; pause/resume can extend lifetime; rates can change; extra services may add charges. Could the claimed finite maximum be exceeded?

**Resolution:** The classification excludes spending-limit reliance, pause/resume, volumes, snapshots, MCP, models, custom infrastructure and template building. For this exact mode, official documentation describes only allocated CPU and RAM per running second, includes disk, stops compute billing on destructive timeout/kill and exposes fixed build allocation. Nexus must bind the current official rate, set a fixed destructive timeout, exclude all actors able to extend it, reserve the computed maximum and reconcile later usage. Any additional billable dimension or unclosed extension actor invalidates the classification. The provider half therefore remains `SUPPORTED`, subject to explicit Q gates; it is not account-cost PASS.

## 4. Challenge to PARTIAL and zero-count classes

The 31 `PARTIAL` rows each have at least one affirmative official fact and at least one named material semantic gap. None was downgraded to `NOT DOCUMENTED`, because the provider exposes a relevant supported surface in every row; the missing part is completeness, scope, freshness, retention, actor closure, revocation or drift meaning. None was upgraded merely because a bounded test could observe one instance.

No row is `CONTRADICTED`. Daytona's organization-wide toolbox authority conflicts with single-key attenuation in collaborative organizations, but the official personal-organization single-user model leaves a narrowly possible controller-only actor composition. That composition is not assumed and P2 remains PARTIAL. Modal's SNI allowlist is unsuitable for exact-host authorization, but the assessed zero-egress candidate uses `block_network=True`; P4/P3 remain PARTIAL rather than contradicted. E2B's incomplete network semantics likewise do not prove the complete input boundary impossible.

No row is `NOT APPLICABLE`. Each P1–P6/P8–P12 property remains mandatory for the exact assessed operation even when an optional feature is excluded.

## 5. Cross-provider and question-pack review

The common blockers correctly separate provider contract facts from later observations:

- P3 needs an applied-state/freshness/safe-release or equivalent immutability contract;
- P5 needs complete hard bounds and controller-loss scope;
- P8/P9 need durable operation/effect observation and safe ambiguity handling;
- P10 needs provider record scope plus a separately qualified Nexus receipt path;
- P12 needs hosted material-change identity and invalidation semantics.

The support pack asks about the exact fixed mode, one principal semantic per numbered item, supported-contract status and an official reference. It does not request account access, credentials, private information, resources or demonstrations. Questions that public documentation already answers negatively are not used to manufacture a different answer: Modal SNI/domain-fronting behavior and Daytona organization-wide toolbox authority remain recorded facts. A response can close only the row it actually supports.

## 6. Governance and disposition

The evidence document does not modify A0–A6, P1–P12 or HQ1–HQ6. It selects no Host and authorizes no support contact, account operation, experiment, provider resource, HQ6 start or G2 Runtime work. No previous G0/G1 authority transfers.

**REVIEW RESULT: ACCEPTABLE AS WRITTEN FOR OWNER REVIEW.**

The bounded evidence supports final disposition **B. PROVIDER CLARIFICATION IS REQUIRED BEFORE ANY BOUNDED EXPERIMENT**. Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**.
