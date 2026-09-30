# Nexus G2 Route B Provider Authoritative Evidence Acquisition v1

Document ID: `nexus.g2.route-b.authoritative-evidence-acquisition.v1`

Version: `1.0.0`

Date: 30 September 2026

Status: **PROPOSED AUTHORITATIVE-EVIDENCE CLOSURE — NO PROVIDER SELECTION OR EXPERIMENT AUTHORITY**

## 1. Result and authority boundary

This document performs the official-evidence closure phase authorized by the owner for the three already assessed Route B modes. It applies the accepted [provider-neutral Host contract](nexus-g2-route-b-provider-neutral-host-contract-v1.md), [provider documentation fact matrix](nexus-g2-route-b-provider-documentation-fact-matrix-v1.md), [G2 Responsibility Re-baseline](nexus-g2-responsibility-rebaseline-review-v1.md), and [UNKNOWN Resolution Matrix](nexus-g2-route-b-unknown-resolution-matrix-v1.md), together with their acceptance records. It does not reopen those conclusions or add a provider.

Starting repository state was branch `nexus-v2-g2-development`, HEAD `71feff89b899164efcf06112267b558f6168b82c`, clean, with source `MANIFEST.json` at 179/179 matched. Its SHA-256 was `0601B82E604BE58EBE9400E608D1A789999E5DC5F70EA0663398A1554193AC42`.

The result is:

| Provider | Authoritative prerequisites | SUPPORTED | PARTIAL | NOT DOCUMENTED | CONTRADICTED |
| --- | --- | ---: | ---: | ---: | ---: |
| E2B | **INCOMPLETE** | 2 | 9 | 0 | 0 |
| Modal | **INCOMPLETE** | 0 | 11 | 0 | 0 |
| Daytona | **INCOMPLETE** | 0 | 11 | 0 | 0 |
| **Total** | No provider crosses the advance gate | **2** | **31** | **0** | **0** |

`SUPPORTED` means only that the authoritative provider-side semantic for the row is sufficient to make its later Q evidence meaningful. It is not P-property PASS, Host qualification, account verification, experiment authority or evidence of effective runtime enforcement. P7 remains the accepted A-class experiment-resolvable property and is outside these counts. No D-class blocker is established by this review.

## 2. Method and exact assessed modes

The bounded search used official API references, security/architecture guides, billing/resource documentation, provider SDK source and changelogs. Living sources were retrieved on 30 September 2026. Unversioned documentation and repository `main` are time-bound facts, not hosted-deployment revision pins. No account login, credential, authenticated API, provider resource, execution or payment was used.

| Provider | Exact assessed mode | Excluded features |
| --- | --- | --- |
| E2B | E2B Cloud Sandbox; Platform API `POST /v2/sandboxes`; native secured envd; SDK behavior documented for JavaScript/Python `2.51.0`; OpenAPI document `0.1.0`; fixed existing build; destructive timeout/kill. | Template build during qualification, volumes, snapshots, pause/resume as an exposure mechanism, MCP, model calls and custom infrastructure. |
| Modal | Ordinary CPU container Sandbox through Python SDK `1.6.0`; standard create/exec/terminate interfaces; explicit `runtime="gvisor"`; `block_network=True`; explicit CPU/memory hard limits and short timeout. | Experimental Sandbox V2 surface, VM/GPU, sidecars, volumes/NFS/cloud mounts, secrets/OIDC, tunnels/connect tokens/ports, custom HTTP endpoints and models. |
| Daytona | Hosted container Sandbox through organization API and toolbox interfaces. A strict block-all candidate would require current Tier 3/4 semantics; the account tier remains Q evidence and is not assumed here. | Self-host/BYOC, VM/GPU, volumes, snapshots, MCP, SSH/VNC/VPN/preview services, model calls and new organization creation. |

## 3. E2B official evidence register

| Key | Official source | Provider semantic used |
| --- | --- | --- |
| E1 | [Changelog](https://docs.e2b.dev/changelog) | On 21 September 2026 SDK `2.51.0` moved create/connect to v2 and made every Sandbox secured. |
| E2 | [Projects](https://docs.e2b.dev/projects) and [Workspaces](https://docs.e2b.dev/workspaces) | An API key is scoped to one project; project/workspace membership and equal project-member permissions are documented. |
| E3 | [Create Sandbox v2](https://docs.e2b.dev/api-reference/sandboxes/create-sandbox-v2) | Creation inputs and returned Sandbox, template, envd and access-token fields. |
| E4 | [Secured access](https://docs.e2b.dev/sandbox/secured-access) | Sandbox-specific `envdAccessToken` authenticates command, filesystem and general envd APIs. |
| E5 | [Get Sandbox](https://docs.e2b.dev/api-reference/sandboxes/get-sandbox) | Reports unit/configuration fields; 404 means nonexistent or inaccessible. |
| E6 | [Update Sandbox network](https://docs.e2b.dev/api-reference/sandboxes/update-sandbox-network) and [official SDK source](https://github.com/e2b-dev/E2B/blob/main/packages/js-sdk/src/sandbox/sandboxApi.ts) | Runtime network replacement; SDK source describes replacement as atomic. |
| E7 | [Internet access](https://docs.e2b.dev/network/internet-access) | Default access, IPv4 deny form, allow precedence, automatic DNS and domain-filter limits. |
| E8 | [Template tags](https://docs.e2b.dev/template/tags) and [Get Template](https://docs.e2b.dev/api-reference/templates/get-template) | Build ID pins a build artifact; tags are mutable; build resources and envd version are queryable. |
| E9 | [Lifecycle events API](https://docs.e2b.dev/sandbox/lifecycle-events-api) and [webhooks](https://docs.e2b.dev/sandbox/lifecycle-events-webhooks) | Seven-day lifecycle retention, provider IDs/timestamps, signed webhooks and limited retries. |
| E10 | [Price calculation](https://docs.e2b.dev/faq/calculate-sandbox-price), [billing](https://docs.e2b.dev/billing) and [Sandbox lifetime](https://docs.e2b.dev/faq/sandbox-lifetime) | Allocated CPU/RAM per running second, included disk, immediate billing stop on pause/kill/timeout, destructive default timeout action. |
| E11 | [OTel export](https://docs.e2b.dev/sandbox/otel-telemetry-export) | Identifier-bearing telemetry is expressly best effort and may be delayed or dropped. |
| E12 | [Process start](https://docs.e2b.dev/api-reference/process/start) and [connect](https://docs.e2b.dev/api-reference/process/connect) | Process creation and reconnection to a running PID; no documented durable completed-command result. |
| E13 | [API key](https://docs.e2b.dev/api-key) and [access-token deprecation](https://docs.e2b.dev/migration/access-token-deprecation) | SDK/CLI use the project API key; legacy access token is disabled. |

## 4. E2B P-property closure

| Property | Result | Authoritative semantic established | Remaining authoritative gap | Later experimental/Q half | Ready? |
| --- | --- | --- | --- | --- | --- |
| P1 identity | **PARTIAL** | E3/E8/E9 expose build, execution, Sandbox, project, template and envd identities. | No durable provider command/effect ID, loaded Nexus byte/dependency identity or hosted enforcement revision. | Bind the exact build, events, envd version, admitted bytes, process and artifacts; test substitution and ID mismatch. | NO |
| P2 authority | **SUPPORTED** | E2–E4 distinguish project control authority from a Sandbox-specific envd data-plane token and enumerate project/workspace permission semantics. | Current members/keys, credential custody and the intentionally broad envd scope are Q facts; there is no fine-grained project-key role. | Enumerate current actors and keys; keep project key from the restricted subject; prove envd token cannot invoke Platform mutation. | YES, subject to Q |
| P3 applied restrictions | **PARTIAL** | E3/E5/E6 define requested/stored policy and a runtime replacement interface. | GET is not documented as live applied state; there is no policy revision, conditional update, exec-policy linearization or safe-release record. | Same-ID readback, negative traffic and mutation-denial checks remain insufficient until the provider semantic closes. | NO |
| P4 inputs | **PARTIAL** | E3/E4/E7/E12 identify command, filesystem, environment, mount, network, public-traffic and envd channels. | IPv6, metadata/internal services, loopback and the complete indirect graph are not closed; domain filtering is protocol-limited and DNS may be opened automatically. | Exercise every declared channel with no secrets and bind allowed/denied observations externally. | NO |
| P5 resources | **PARTIAL** | E8/E10 expose fixed CPU/RAM/disk allocation, plan runtime ceilings and destructive timeout kill. | Allocation is not a complete hard-limit contract; process count, descendants, output/logs and controller-loss timing remain incomplete. | Stress each bound and descendants; observe timeout/controller-loss cleanup; bind mutation actors. | NO |
| P6 cost | **SUPPORTED** | For the exact excluded-feature mode, E10 gives a finite formula: fixed allocated CPU plus RAM per running second, disk included, with billing stopping on kill/timeout. A destructive fixed timeout supplies finite duration. | Current rates/account/headroom/actors and later settlement are Q evidence. Any pause/resume, volume, snapshot, MCP, model/tool or other billable feature reopens this row. | Bind rates, build allocation, timeout, account headroom and sole-control state before creation; reconcile event duration and delayed usage. | YES, subject to Q |
| P8 observation | **PARTIAL** | E9 supplies provider lifecycle identities/timestamps and seven-day retention. | E12 reconnects only to a running PID; durable completed command results and task-effect coverage are absent. | Interrupt/reconnect, cross-bind lifecycle records, streams and immutable effects; retain uncovered effects as UNKNOWN. | NO |
| P9 unknown effects | **PARTIAL** | Original unit/execution references and lifecycle events can be queried. | E5 conflates nonexistent and inaccessible; process not-found cannot distinguish never started, completed, expired or deleted. | Inject lost create/dispatch/result/kill responses; query only original identities and never blind retry. | NO |
| P10 evidence | **PARTIAL** | E9 provides control-side records and signed webhook origin evidence. | Limited delivery and E11's lossy telemetry do not bind full applied configuration, command result/effects or protected Nexus custody. | Verify signatures/deduplication, cross-check polling and protect route-controller receipts; missing/contradictory records STOP. | NO |
| P11 credentials | **PARTIAL** | E2/E4/E13 distinguish project control and Sandbox data-plane credentials; no model key is required. | Revocation/rotation effects on in-flight calls, existing envd tokens and running Sandboxes are undocumented. | Bind custody and guest non-reachability; test changed-authority invalidation only under separate authority. | NO |
| P12 drift | **PARTIAL** | E1/E3/E5/E8 expose API generation, SDK, build, envd and configuration identities. | They do not identify the hosted Platform enforcement revision or provide a material-change contract. | Bind every observable identity/expiry and prove pre-dispatch invalidation on mismatch. | NO |

**E2B: AUTHORITATIVE PREREQUISITES = INCOMPLETE.** P2 and P6 do not compensate for the blocking P3/P5/P8/P9/P10/P12 provider semantics; P1/P4/P11 also remain partial.

## 5. Modal official evidence register

| Key | Official source | Provider semantic used |
| --- | --- | --- |
| M1 | [Python SDK releases](https://modal.com/docs/sdk/py/releases) and [Sandbox API](https://modal.com/docs/sdk/py/latest/Sandbox) | SDK `1.6.0`, ordinary Sandbox arguments, IDs, lifecycle and next-generation backend transition. |
| M2 | [Sandbox guide](https://modal.com/docs/guide/sandboxes) and [runtime identifiers](https://modal.com/docs/guide/environment_variables) | Sandbox/task/image identifiers and standard create/exec/terminate behavior. |
| M3 | [Sandbox networking](https://modal.com/docs/guide/sandbox-networking) | Full outbound block, SNI-domain behavior, domain-fronting limitation and runtime mutation semantics. |
| M4 | [RBAC](https://modal.com/docs/guide/rbac) and [service users](https://modal.com/docs/guide/service-users) | Workspace/Environment roles, service-user scoping and default access. |
| M5 | [Sandbox resources](https://modal.com/docs/guide/sandbox-resources) and [resources](https://modal.com/docs/guide/resources) | CPU/memory request and hard-limit semantics, disk quota and billing basis. |
| M6 | [Budgets](https://modal.com/docs/guide/budgets), [billing](https://modal.com/docs/guide/billing), [egress billing](https://modal.com/docs/guide/network-egress-billing), [Workspace API](https://modal.com/docs/sdk/py/latest/Workspace) and [pricing](https://modal.com/pricing) | Workspace hard cap, Environment-budget exclusions, rate/usage sources and delayed billing data. |
| M7 | [Security](https://modal.com/docs/guide/security) and [audit logs](https://modal.com/docs/guide/audit-logs) | Retention and audit coverage; Sandbox exec is not covered as a durable audit/result record. |
| M8 | [Feature maturity](https://modal.com/docs/guide/feature-maturity) | Stability labels and compatibility expectations. |
| M9 | Modal staff reply dated 23 September 2026, already preserved in accepted Nexus evidence | No supported effective-runtime-restrictions getter, revision, digest or change notification before exec. This is Tier 3 and supplementary to public docs. |

## 6. Modal P-property closure

| Property | Result | Authoritative semantic established | Remaining authoritative gap | Later experimental/Q half | Ready? |
| --- | --- | --- | --- | --- | --- |
| P1 identity | **PARTIAL** | M1/M2 expose Sandbox/task/image identifiers and SDK/runtime class. | No immutable provider tuple binds hosted backend, actually loaded image/dependencies, exec identity and result. | Bind one Sandbox, reviewed bytes, actual runtime/image IDs and artifacts; test substitution. | NO |
| P2 authority | **PARTIAL** | M4 scopes service users to Environments and documents Contributor/Viewer/No Access; a default Sandbox lacks Modal-resource access. | Contributor is full read/write, Owners/Managers remain Contributors, and no create/exec/terminate-only role or closed concurrent-actor inventory is documented. | Bind actors/roles/custody and prove denied mutation/secret/control paths. | NO |
| P3 applied restrictions | **PARTIAL** | M3 documents `block_network=True`; it is incompatible with dynamic policy and dynamic updates are immediate for their separate mode. | M9 confirms no effective-state getter/revision/digest/change notification; pre-entrypoint ordering and lifetime immutability of block-all are not stated. | Same-unit observations and negatives cannot substitute for the missing provider contract. | NO |
| P4 inputs | **PARTIAL** | M1–M3 enumerate command, env, workdir, secret, mount, filesystem and network inputs. | Full IPv4/IPv6/DNS/link-local/metadata/internal-service and indirect graph is not contractually exhaustive; SNI allowlisting permits domain fronting. | Use zero-egress synthetic fixtures and test every declared channel after authoritative closure. | NO |
| P5 resources | **PARTIAL** | M1/M5 document CPU throttling, memory OOM enforcement, fixed disk quota and maximum lifetime. | Complete descendant/process-count/output/controller-loss scope is absent. | Stress and externally observe every bound, whole tree and zero-live terminal state. | NO |
| P6 cost | **PARTIAL** | M6 documents a hard Workspace gross-usage cap, per-second resource billing, rates, multipliers and egress terms. | No maximum cutoff overshoot/propagation statement; cap is shared; Environment budget omits dimensions; reports may lag and egress charging changes on 1 October 2026. | Bind current Workspace/plan/cap/payment/actors/rates/headroom and reconcile delayed/residual usage. | NO |
| P8 observation | **PARTIAL** | M7 documents retention; `Sandbox.logs` survives termination for entrypoint logs. | It excludes exec logs; audit logs exclude exec; no stable durable exec result/reconnect ID is documented. | Interrupt original operation and validate retained provider records/effects without relying on guest-only streams. | NO |
| P9 unknown effects | **PARTIAL** | Sandbox ID/from-id and metadata exist. | Names are reusable; no create idempotency key, lost-create request ID or complete not-found/expiry distinction exists. | Fault-inject loss and reconcile only immutable original IDs; blind recreation is forbidden. | NO |
| P10 evidence | **PARTIAL** | M7 supplies metadata/logs and Enterprise actor/target/time records for covered workspace changes. | Runtime exec is omitted and no record binds applied configuration, image, exec and terminal result. | A qualified route controller must protect and cross-check receipts; stale/forged/partial evidence STOP. | NO |
| P11 credentials | **PARTIAL** | M4/M6 document service tokens, Environment roles, proxy-token TTL/revocation and owner Workspace billing. | Service-token deletion/revocation effects on existing clients, direct connections and issued handles are not stated. | Bind current identity/custody and prove no token enters guest or evidence. | NO |
| P12 drift | **PARTIAL** | M1/M8 document SDK semver/deprecation and explicit gVisor runtime class. | SDK `1.6.0` changed Sandbox backend automatically; no hosted-backend revision/digest or material-change notification is exposed. | Bind all observable versions and stop before dispatch on any missing/mismatched material identity. | NO |

**Modal: AUTHORITATIVE PREREQUISITES = INCOMPLETE.** Documented hard resources, block-all and Workspace budget are positive facts, but they do not close applied-state, actor, operation/result, cost-overshoot or hosted-drift semantics.

## 7. Daytona official evidence register

| Key | Official source | Provider semantic used |
| --- | --- | --- |
| D1 | [Sandboxes](https://www.daytona.io/docs/en/sandboxes/) and [Sandbox SDK](https://www.daytona.io/docs/en/typescript-sdk/sandbox/) | Hosted container identity, resources, lifecycle, TTL and configuration fields. |
| D2 | [Snapshots](https://www.daytona.io/docs/en/snapshots/) | Snapshot/image references and persistence behavior. |
| D3 | [API keys](https://www.daytona.io/docs/api-keys) and [organizations](https://www.daytona.io/docs/en/organizations/) | Organization authority and the documented non-scopeability of toolbox runtime access. |
| D4 | [Network limits](https://www.daytona.io/docs/en/network-limits/) and [limits](https://www.daytona.io/docs/limits) | Tier-specific block/allow rules, live updates, shared quotas and Tier 3/4 prerequisites. |
| D5 | [Billing](https://www.daytona.io/docs/billing), [pricing](https://www.daytona.io/pricing) and [persistence](https://www.daytona.io/docs/en/persistence/) | State-dependent billing, retained disk/snapshot behavior and published rates. |
| D6 | [Process execution](https://www.daytona.io/docs/en/process-code-execution/), [Process SDK](https://www.daytona.io/docs/en/typescript-sdk/process/) and [log streaming](https://www.daytona.io/docs/en/log-streaming/) | Session/command identifiers, state, exit and log interfaces. |
| D7 | [Troubleshooting](https://www.daytona.io/docs/en/troubleshooting/) | Typed error states including 404/410 cases. |
| D8 | [Audit logs](https://www.daytona.io/docs/audit-logs/), [webhooks](https://www.daytona.io/docs/en/webhooks/) and [OTel](https://www.daytona.io/docs/en/observability/otel-collection/) | Actor/target/time records, lifecycle deliveries and observability sources. |
| D9 | [Preview](https://www.daytona.io/docs/en/preview/) | Sandbox-wide preview token scope and revocation limitation. |
| D10 | [Changelog](https://www.daytona.io/changelog) | Public platform change history; latest observed entry was `v0.220.0` dated 29 September 2026. |

## 8. Daytona P-property closure

| Property | Result | Authoritative semantic established | Remaining authoritative gap | Later experimental/Q half | Ready? |
| --- | --- | --- | --- | --- | --- |
| P1 identity | **PARTIAL** | D1/D2 expose Sandbox ID, snapshot/image reference, daemon/build fields, time and resources. | No record binds the same process to loaded immutable bytes/dependencies or identifies hosted control-plane revision. | Bind exact Sandbox/session/command, reviewed bytes and artifacts; test substitution. | NO |
| P2 authority | **PARTIAL** | D3 explicitly states toolbox runtime access is not grantable/scopable: every organization-valid key and collaborative member can use it. A personal organization has one user. | No single-Sandbox attenuation exists; a personal-organization composition still needs an exhaustive runtime-capable actor/credential inventory. | Bind a personal organization if separately authorized; enumerate members, keys, preview/SSH/session tokens and prove controller-only custody. | NO |
| P3 applied restrictions | **PARTIAL** | D4 documents Tier 3/4 strict per-Sandbox rules, persistence and live updates; GET exposes stored fields. | No atomic safe-release receipt, desired/effective distinction, enforcement freshness or complete mutation-actor exclusion is documented. | Bind same-unit configuration and perform negative/mutation tests only after provider semantics close. | NO |
| P4 inputs | **PARTIAL** | D1/D4/D6 identify toolbox, command/file and network channels; Tier 3/4 omit the lower-tier essential-service bypass. | IPv6, DNS, link-local/metadata, linked-Sandbox and provider-side graph remain incomplete; outbound proxy is expressly not a security boundary. | Test the complete exact-tier graph with synthetic no-secret fixtures. | NO |
| P5 resources | **PARTIAL** | D1 documents CPU/RAM/disk, cgroup observation, wall TTL, force-stop and waited deletion. | Hard PID/process and output limits, descendant scope, mutation exclusion and controller-loss cleanup guarantee are incomplete. | Stress limits/descendants/TTL and verify zero-live cleanup externally. | NO |
| P6 cost | **PARTIAL** | D5 documents per-second resource/state billing, stopped-disk charging, ephemeral deletion and snapshot persistence. | Exhaustive dimensions, rounding/minimums, price-binding period, reporting/final-settlement lag and hard wallet cutoff are not established. Tier 3 currently documents a $500 top-up. | Bind exact account/tier/payment/rates/headroom and reconcile delayed/residual charges only after a finite ceiling is authoritative. | NO |
| P8 observation | **PARTIAL** | D6 exposes session/command IDs, status, exit and logs. | Retention after completion/stop/delete and truncation/output limits are not sufficiently documented. | Interrupt/reconnect to original IDs and validate retained provider records/artifacts. | NO |
| P9 unknown effects | **PARTIAL** | D7 provides typed errors and existing-reference queries. | No documented create idempotency/client request key or async-command idempotency closes a lost response. | Inject lost responses and query only original IDs; retain UNKNOWN rather than recreate. | NO |
| P10 evidence | **PARTIAL** | D8 documents actor/org/action/target/result/source/time records and Sandbox lifecycle deliveries. | Toolbox command coverage, effective-policy fields, retention, signed authenticity/replay protection and a complete execution receipt are absent. | Protect a route-controller receipt and cross-check exact provider records; forged/stale/partial evidence STOP. | NO |
| P11 credentials | **PARTIAL** | D3 documents immediate unrecoverable API-key deletion; D9 describes Sandbox-wide preview authority. | Existing connection/session invalidation and propagation bounds are not defined; preview tokens cannot be revoked while the Sandbox runs. | Bind every runtime credential and guest non-reachability; changed authority invalidates Nexus grants/evidence. | NO |
| P12 drift | **PARTIAL** | D1/D10 supply daemon/build, SDK and changelog versions. | They do not identify hosted backend/policy revision or provide a qualification-material change contract. | Bind all available identities/expiry and prove pre-dispatch invalidation on mismatch. | NO |

**Daytona: AUTHORITATIVE PREREQUISITES = INCOMPLETE.** Organization-wide toolbox authority remains especially material. A personal organization may be a compositional candidate, but public evidence still does not close the full actor set or the other mandatory rows.

## 9. P6 cost-boundary adversarial result

| Provider | Hard-bound path assessed | Result |
| --- | --- | --- |
| E2B | Exact no-extra-feature build allocation × documented CPU/RAM rate × fixed destructive timeout; included disk; no pause/resume or persistent resource. | **SUPPORTED provider half**, narrowly. Any additional billable feature, mutable extension path or unbound current rate/account state invalidates this conclusion. |
| Modal | Hard Workspace gross-usage cap plus finite Sandbox limits/rates. | **PARTIAL.** Shared use, maximum cutoff overshoot/propagation, changing egress charges, excluded Environment-budget dimensions and delayed reporting prevent a conservative all-in operation ceiling today. |
| Daytona | Fixed resources/TTL plus published state-dependent rates. | **PARTIAL.** Hard wallet cutoff, exhaustive charges, rounding, price binding and settlement/residual bounds are missing; Tier 3's documented top-up is not an operation cap. |

A cost alert, credit balance, plan quota, post-hoc estimate or nominal resource allocation was not treated as a hard bound. Late or revised provider usage remains unresolved until reconciled.

## 10. Common authoritative blockers and finite next boundary

The mandatory blockers common to all three providers are:

1. **P3 applied-state and release semantics:** stored/requested policy is not an instance-bound, fresh, subject-external applied-state record with safe release or equivalent immutability/mutation exclusion.
2. **P5 complete resource scope:** provider documentation does not close all applicable descendants/process/output/controller-loss dimensions.
3. **P8/P9 durable operation and unknown-effect semantics:** none documents a complete durable command/result identity and a positive distinction for every lost-response/not-found state needed to avoid blind retry.
4. **P10 receipt coverage:** provider telemetry does not bind the complete applied configuration, admitted operation, result/effects and protected Nexus custody.
5. **P12 hosted drift identity:** SDK/API/build labels do not identify the complete hosted enforcement revision or a material-change/requalification contract.

P1 loaded-byte/result binding, P4 full input-channel closure and P11 revocation effects are also partial for all three. P2 is provider-specific: E2B's provider half is supported; Modal remains under-bounded; Daytona documents organization-wide toolbox authority and needs a proven personal-organization actor composition. P6 is provider-specific: only E2B's narrowly fixed, no-extra-feature formula reaches `SUPPORTED`.

Resolution now requires official provider or supported service-contract clarification. P3/P8/P9/P10/P12 may require API/schema or service-contract additions if support confirms no supported interface exists. Modal and Daytona P6 may require a billing-control guarantee or a closed finite-charge composition. No architecture change is selected here; a later architecture decision would be necessary only if provider clarification proves the accepted property cannot be supplied by the route-specific provider/controller composition.

The [support-question pack](nexus-g2-route-b-provider-support-question-pack-v1.md) is the finite next documentary action. Silence or an unsupported assurance remains unresolved. No provider experiment is justified.

## 11. Preserved governance state

No accepted file or `MANIFEST.json` is modified by this draft. No provider has been selected or ranked. Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**. P7 is not PASS. A0–A6 and all accepted/frozen architecture remain unchanged.
