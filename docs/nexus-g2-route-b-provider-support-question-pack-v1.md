# Nexus G2 Route B Provider Support Question Pack v1

Document ID: `nexus.g2.route-b.provider-support-question-pack.v1`

Version: `1.0.0`

Date: 30 September 2026

Status: **PROPOSED SUPPORT QUESTIONS — NOT SENT; NO PROVIDER CONTACT OR EXPERIMENT AUTHORITY**

## 1. Purpose and submission rule

These questions are the minimum provider-specific clarification path arising from the [authoritative evidence acquisition](nexus-g2-route-b-authoritative-evidence-acquisition-v1.md). They disclose no credential, private repository content or account secret. They have not been sent.

For every answer, ask the provider to state whether the semantic is part of the supported service/API contract for the exact named mode and to cite an official API, schema or documentation reference. A support assurance without supported-contract status or a reproducible reference remains `PARTIAL`. Each numbered question targets one principal unresolved semantic; explanatory clauses define its scope rather than authorize a broader survey.

## 2. E2B Cloud Sandbox questions

Exact mode: `POST /v2/sandboxes`, native secured envd, fixed existing build, no volume/snapshot/pause-resume/MCP/model/custom infrastructure.

1. **P1 — loaded identity:** What provider-issued record binds a Sandbox execution to the immutable image/build and executable/dependency byte basis actually loaded?
2. **P1/P8 — durable command identity:** Does native envd expose a durable command-operation ID and completed result query after process exit or Sandbox kill, and what is its retention?
3. **P3 — applied state:** Does `GET /sandboxes/{sandboxID}` return actively enforced network state or stored desired configuration, and what revision/freshness marker identifies that state?
4. **P3 — update ordering:** When network replacement returns success, is the new policy fully enforced before the response, with no command or guest traffic able to run under an intermediate policy?
5. **P2/P3 — guest mutation:** Can a guest process possessing no project API key, but possibly the native envd token, relax Platform network, lifecycle, resource or public-traffic restrictions?
6. **P4 — full network scope:** What is the supported behavior of `denyOut: ["0.0.0.0/0"]` for IPv6, DNS, link-local/metadata, loopback, E2B internal services, QUIC and non-80/443 protocols?
7. **P5 — hard resource scope:** Are configured CPU, RAM and disk values hard, non-guest-relaxable whole-VM bounds for all descendants, and which hard process/output limits also apply?
8. **P5/P7 — timeout bound:** What provider-guaranteed worst-case interval applies from timeout expiry to complete Sandbox and descendant termination after controller loss?
9. **P8/P10 — lifecycle completeness:** Which lifecycle actions are guaranteed to produce retrievable control-side events, and what completeness/retention guarantee applies when webhook delivery fails?
10. **P9 — no-effect distinction:** Is there a supported query that distinguishes an original create/command that never took effect from one that took effect but is no longer visible?
11. **P11 — revocation propagation:** When a project API key is revoked, what happens to in-flight Platform requests, existing SDK clients, issued envd tokens and running Sandboxes?
12. **P12 — hosted drift:** Which supported deployed Platform/runtime-policy revision or material-change identifier can be recorded during qualification and checked before later dispatch?

An answer to P6 is not presently requested: the official fixed-resource/no-extra-feature formula is sufficient for the provider half, while current rates/account/headroom remain later Q evidence. Any added billing dimension reopens P6.

## 3. Modal ordinary CPU gVisor Sandbox questions

Exact mode: Python SDK `1.6.0`, ordinary CPU Sandbox, `runtime="gvisor"`, `block_network=True`, fixed CPU/memory limits, short timeout, with excluded advanced features.

1. **P1/P12 — backend identity:** What supported provider API returns the actual hosted Sandbox backend generation/revision for a specific Sandbox ID?
2. **P1 — loaded image identity:** What supported external API returns the immutable root Image ID/digest and runtime identity actually loaded by that Sandbox?
3. **P1/P8 — exec identity:** Does `Sandbox.exec` expose a stable operation ID that a fresh client can query after the original client disconnects or crashes?
4. **P2 — attenuated authority:** Is there a service-user/RBAC role that permits create, exec, read and terminate for one Environment while denying network-policy, mount, image, Secret and other control mutations?
5. **P3 — release ordering:** For `block_network=True`, is the block enforced before the entrypoint can first execute?
6. **P3 — lifetime mutation:** Is `block_network=True` immutable for that Sandbox lifetime to every Workspace/Environment actor and API?
7. **P4 — block scope:** Does `block_network=True` contractually cover IPv4, IPv6, DNS, link-local/metadata, private Modal networking and every other outbound route?
8. **P3/P10 — applied receipt:** Is there a provider-side record keyed by Sandbox ID for applied network policy, runtime, image, CPU/memory limits, timeout, mounts and secret/OIDC presence, with a stated freshness guarantee?
9. **P5/P7 — descendants:** Do timeout and `terminate(wait=True)` end every descendant process in the main container, and can any work survive a terminal Sandbox state?
10. **P5 — remaining limits:** Which hard process-count, output/log and storage limits apply to this exact CPU gVisor Sandbox after controller loss?
11. **P6 — budget overshoot:** Can a Workspace budget be exceeded because of metering/cutoff delay or already-running workloads, and what is the maximum overshoot?
12. **P6 — exhaustive charges:** For the exact no-GPU/no-volume/no-region/block-network configuration, what billable dimensions can accrue after Sandbox creation and after terminal state?
13. **P8 — retained exec result:** Are exec stdout, stderr and exit status retained and queryable after client loss and Sandbox termination, by what stable ID and for how long?
14. **P9 — create ambiguity:** Does Sandbox creation accept a client idempotency key or expose a request ID that unambiguously reconciles a lost create response?
15. **P9 — not-found meaning:** What does `NotFound` from `Sandbox.from_id` mean for never-created, expired, deleted and previously-finished IDs, and how long is metadata retained?
16. **P10 — provider receipt:** Is there an integrity-protected provider record binding actor, Sandbox ID, actual image/runtime/applied restrictions, exec ID, timestamps and terminal result, and what is its retention?
17. **P11 — token revocation:** When a service-user token is deleted, when do existing SDK clients, direct Sandbox connections and already-issued handles lose control authority?
18. **P12 — material-change notice:** What supported notification or identity tells clients that hosted backend, enforcement semantics or another qualification-material behavior changed?

Modal's public documentation already states that domain allowlisting is SNI based and permits domain fronting; no question asks Modal to reclassify it as exact-host authorization. The dated staff reply already states that the general effective-policy getter/revision mechanism is absent. Questions 5–8 seek only a distinct supported immutable contract for `block_network=True`.

## 4. Daytona hosted container Sandbox questions

Exact mode: hosted container Sandbox through organization API/toolbox. A future strict block-all composition would require current Tier 3/4 behavior; personal-organization feasibility is not assumed.

1. **P1 — loaded identity:** Which API field binds a hosted container Sandbox to the immutable image/snapshot and executable/dependency bytes actually loaded?
2. **P1/P12 — backend identity:** Which field identifies the deployed hosted control-plane and network-policy revision for the same Sandbox?
3. **P2 — workload-scoped authority:** Can toolbox runtime authority be restricted to one key and one Sandbox, or is organization-wide toolbox authority unavoidable?
4. **P2 — personal-organization actors:** For a personal organization, what is the exhaustive set of runtime-capable human, API-key, dashboard-session, preview-token and SSH-token actors?
5. **P3 — create ordering:** Does Tier 3/4 creation return only after `networkBlockAll` is enforced on the runner?
6. **P3 — applied readback:** Does Sandbox GET expose actively enforced network state or only stored intent, and what freshness/revision marker applies?
7. **P4 — block scope:** Does Tier 3/4 block-all cover IPv4, IPv6, DNS, link-local/metadata, essential services, linked Sandboxes, VPN/proxy routes and provider-side egress paths?
8. **P4/P6 — tier prerequisite:** Can strict per-Sandbox block-all be enabled without the currently documented Tier 3/4 top-up?
9. **P5 — descendant limits:** Are CPU, RAM and disk hard limits shared by every descendant, and which hard PID/process limit applies?
10. **P5/P7 — TTL cleanup:** Does wall TTL terminate every descendant and every billable Sandbox state by `autoDestroyAt` after controller loss?
11. **P5 — output bound:** Which hard output and retained-log limits apply to the exact container mode?
12. **P6 — complete billing:** For the exact minimal configuration, what are all billable dimensions, rounding/minimum rules, price-binding period and final settlement lag?
13. **P6 — hard cutoff:** Is account balance or any supported usage limit a hard execution cutoff, and what maximum overshoot can occur?
14. **P8 — result retention:** How long are session state, command exit status and logs retained after completion, stop and deletion?
15. **P9 — lost create:** Does create support a caller idempotency key, and how is exactly the original Sandbox recovered after a lost create response?
16. **P9 — command ambiguity:** Is asynchronous command dispatch idempotent by a caller-supplied command ID, and how are never-accepted and accepted-but-expired results distinguished?
17. **P10 — audit coverage:** Which toolbox/session/command operations appear in provider audit logs, with which configuration/result fields and retention?
18. **P10 — authenticity:** What authenticity and replay protections apply to webhook and audit evidence?
19. **P11 — revocation propagation:** Does API-key deletion invalidate existing API, WebSocket and toolbox connections and running sessions, with what propagation bound?
20. **P12 — material-change notice:** Which backend/runtime/policy/identity/billing changes trigger a supported notification or mandatory revalidation signal?

## 5. Bounded disposition

These questions are not a request to create resources, inspect an account or run a demonstration. A provider answer can close only the authoritative half it directly supports. Current account/configuration, actual effective behavior, protected Nexus receipt composition and adversarial qualification remain separate. If a provider confirms that a mandatory semantic is unavailable, the affected route must be reassessed under the accepted contract; silence remains unresolved.

No question pack has been submitted. No provider support contact, authenticated operation, credential, cost or experiment is authorized by this document.
