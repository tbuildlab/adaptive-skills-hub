# Nexus G2 Route B OpenAI-Hosted Agents API Authoritative Candidate Evaluation v1

Status: **PROPOSED DOCUMENTATION/EVIDENCE CHECKPOINT — AUTHORITATIVE PREREQUISITES INCOMPLETE; NO EXPERIMENT; G2 HOLD**

Evaluation date: 30 September 2026

## 1. Authority, fixed scope and preserved state

This bounded evaluation applies the accepted [Route B Provider-Neutral Host Contract v1](nexus-g2-route-b-provider-neutral-host-contract-v1.md), [G2 Responsibility Re-baseline v1](nexus-g2-responsibility-rebaseline-review-v1.md), [Route B UNKNOWN Resolution Matrix v1](nexus-g2-route-b-unknown-resolution-matrix-v1.md), and their acceptance records to one new candidate. It does not reopen or change the accepted E2B, Modal or Daytona results.

Starting repository state was branch `nexus-v2-g2-development`, HEAD `97dfe170310f699c906e93bb4c683507cfa6ece6`, clean, with source `MANIFEST.json` at 183/183 matched. Its SHA-256 was `5BCF2929178A82D594C5AA8650CAA7E9D084C23B867509585C6B34941FA60C46`.

This is documentation research only. No account, credential, authenticated API, environment, session, sandbox, model call, artifact, provider support contact, experiment or cost was used. P7 is not PASS. Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**.

## 2. Exact candidate mode

The evaluated product is the **OpenAI Agents API with an OpenAI-hosted sandbox**, using the OpenAI-managed Codex harness and `environment.type: "openai_hosted"`. The current documented beta HTTP contract uses `/v1/agents/sessions` with `OpenAI-Beta: agents=v1`. OpenAI creates and manages one Linux sandbox for the session; the application sends input and receives events. The application controls compute only for self-hosted environments, so self-hosted Agents API semantics are excluded.

The bounded candidate configuration, if a later experiment were separately authorized, would use:

- one newly created session and its separate `/workspace`;
- `container_size: "small"` (documented as 1 vCPU and 1 GB memory);
- `network.access: "disabled"`;
- no environment template, setup commands, packages, skills, plugins, capability directories, vaults, MCP servers or function tools;
- multi-agent disabled (the documented default), one fixed model/configuration, fixed inline or Files API inputs and published outputs only under `/workspace/outputs`;
- no environment variable containing a secret and no application API key in the sandbox.

This exact profile is a proposed evaluation boundary, not a provider guarantee, accepted protocol, experiment authority or Host selection. The managed harness still chooses and issues shell commands within the configured agent loop. A deterministic payload is not equivalent to a direct one-command execution API.

Terminology is fixed as follows: **harness** is the OpenAI-hosted Codex model/tool loop; **environment/sandbox** is the hosted Linux execution unit; **session** is the durable agent instance; **turn** is one work cycle; **events/items** are live and saved observations; **artifact** is an immutable published copy of an output file; **cancel input** requests cancellation of the active turn; **session deletion** removes the public API resource while physical cleanup may continue asynchronously. Billing combines model API rates, OpenAI tool rates when used, and standard container rates.

This mode is a legitimate Route B Host candidate because it supplies a provider-managed execution unit, control API, externally held application authority, lifecycle operations, provider-side events and retrievable artifacts. Candidate status does not establish P1–P12, HQ1–HQ6 or effective isolation.

## 3. Evidence policy and official source register

Only current official OpenAI documentation and API reference were used for closure. Pages are descriptive API documentation unless an explicit API field or response schema is identified; none is treated as a negotiated service guarantee.

| ID | Official source | Material contract evidence |
| --- | --- | --- |
| O1 | [Agents API overview](https://developers.openai.com/api/docs/guides/agents-api/overview) | Managed Codex harness; Agent/Environment/Session/Events; hosted-session responsibility; pricing categories; US-only residency and no ZDR. |
| O2 | [Agents API architecture](https://developers.openai.com/api/docs/guides/agents-api/architecture) | OpenAI runs harness; OpenAI creates/manages hosted sandbox; application submits work, receives results and handles function tools; application controls compute only for self-hosted mode. |
| O3 | [OpenAI-hosted sandboxes](https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted) | `openai_hosted`, `/workspace`, setup channels, sizes, network modes, environment status, separate workspace, artifacts, expiry, cleanup request, `409`, stream-close behavior and separate billing. |
| O4 | [Retrieve an agent environment](https://developers.openai.com/api/reference/python/resources/beta/subresources/agents/subresources/environments/methods/retrieve) | Environment ID/type/status and safe installed metadata; returned schema does not expose applied network, image/runtime revision or hard-limit receipt. |
| O5 | [Run and continue sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions) | Durable session ID, terminal turn events, saved items after disconnect, stream non-replay, steer/update behavior and active-turn cancel input. |
| O6 | [Manage sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage) | List/retrieve/delete sessions and retain application-side session identity for recovery. |
| O7 | [Delete an agent session](https://developers.openai.com/api/reference/python/resources/beta/subresources/agents/subresources/sessions/methods/delete) | Running execution must first be cancelled; deletion may abandon unpublished outputs; physical cleanup may continue asynchronously; `deleted` confirms public-API removal only. |
| O8 | [Files and artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files) | Input/live-file channels, immutable artifacts bound to session/turn/path, survival after environment expiry and size/count limits. |
| O9 | [Observability and usage](https://developers.openai.com/api/docs/guides/agents-api/observability) | Event/history/turn/subagent observations; usage is best effort, may be null/change and is not the final bill. |
| O10 | [Tracing](https://developers.openai.com/api/docs/guides/agents-api/tracing) | Recorded model/tool/subagent spans and public OTLP export; traces arrive after a turn and exports contain only traces available at request time. |
| O11 | [Session webhooks](https://developers.openai.com/api/docs/guides/agents-api/sessions/webhooks) and [Webhooks](https://developers.openai.com/api/docs/guides/webhooks) | Signed provider POSTs, event IDs, up to 72-hour retry and possible duplicates; consumers must verify and deduplicate. |
| O12 | [Sandbox security](https://developers.openai.com/api/docs/guides/agents-api/environments/security) | Application-key permissions and separation; agent code can access available files/credentials/network; keep application key outside environment. |
| O13 | [Vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults) | Optional proxy substitution for approved exact hosts; real secret stays outside sandbox. The bounded profile excludes vaults. |
| O14 | [Configuring Agents](https://developers.openai.com/api/docs/guides/agents-api/configuration) and [Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) | Active turns retain settings; only specified later-turn settings are mutable; tools/instructions/multi-agent require a new session; subagents are disabled by default. |
| O15 | [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) | Current container charges are per 20-minute session by memory size; model/tool/storage categories have separate prices. |
| O16 | [Agents API reference](https://developers.openai.com/api/reference/python/resources/beta/subresources/agents) | Beta resources for sessions, environments, artifacts, events, items, turns and subagents; environment templates provision a fresh hosted environment per session. |

All sources were read on 30 September 2026. Absence claims below mean that bounded review of this source set did not find the mandatory semantic; they are not claims about undocumented OpenAI internals.

## 4. Nexus/OpenAI responsibility composition

| Layer | Retained responsibility |
| --- | --- |
| Nexus trusted controller/governance | Owner admission and permission decision; conservative budget decision; exact candidate/config admission; protected receipt custody; retry refusal while effects are UNKNOWN; qualification and requalification state. |
| OpenAI control plane / managed Codex harness | Session and turn orchestration, model/tool loop, context compaction/recovery, command issuance, provider events/items/traces and hosted-environment coordination. |
| OpenAI-hosted sandbox | Linux command/file execution within provider-enforced compute and configured network surface; live workspace and output publication. |
| Bounded workload | Uses only admitted files and `/workspace/outputs`; receives no controller/API credential and no external side-effect channel in the proposed network-disabled profile. |

O2 and O12 support keeping the application API key, authentication, approval, billing decision, audit custody and recovery state outside the sandbox. This composition is architecture-compatible in principle: HQ1–HQ4 may be provider-supplied only after Nexus verifies and binds the exact property, while HQ5–HQ6 remain Nexus-owned. The current documentation does not complete that verification.

## 5. Authoritative prerequisite matrix

P7 is handled separately because the accepted contract classifies it as experimentally resolvable. Every other row below is a mandatory provider-side prerequisite for a meaningful experiment.

| Property | Classification | Authoritative positives | Material unresolved semantic | Advance gate |
| --- | --- | --- | --- | --- |
| P1 deployment / instance identity | **PARTIAL** | O4–O8 expose environment, session, turn, item, artifact and path identities; artifacts bind session/turn/path. | No supported identity binds the actual hosted image/runtime/enforcement revision or loaded executable/dependency byte basis to the same execution. No direct command-operation lookup contract closes that substitution gap. | CLOSED |
| P2 authority / actor exclusion | **PARTIAL** | O2/O12 separate application, harness and sandbox; restricted application-key permissions exist; reserved `OPENAI_API_KEY` is rejected from hosted env config; multi-agent can be disabled. | Complete create/mutate/connect/cancel/delete actor classes, concurrent project authority, hosted-harness authority, environment mutation scope and revocation propagation are not documented as one closed actor graph. | CLOSED |
| P3 applied restrictions | **PARTIAL** | O3 explicitly defines enabled/disabled/restricted network requests, exact-host restricted entries and template non-broadening; O4 exposes environment status. | Retrieve does not return applied network/configuration or an enforcement revision. No instance-bound, fresh, provider-issued applied-policy receipt or safe-release/mutation-exclusion guarantee is documented. Requested `disabled` is not proof of effective policy. | CLOSED |
| P4 closed input / effect graph | **PARTIAL** | O3/O8/O12–O14 enumerate files, env, packages, setup commands, tools, skills/plugins, vaults, MCP, network, model input, steering and function tools. The proposed profile excludes optional channels. | Documentation does not close provider/harness internal channels, DNS/internal/metadata behavior under disabled mode, environment file mutation actors, process/IPC/service/descendant surfaces or all indirect model/harness inputs/effects. | CLOSED |
| P5 hard resource / lifetime boundary | **PARTIAL** | O3 documents selected vCPU/memory and fixed file/artifact request limits; inactivity may lead to sandbox deletion after one hour; delete requests cleanup. | No complete nonrelaxable CPU scheduling, memory enforcement/failure, storage, PID/process tree, output, wall-clock/active lifetime, background-process or controller-loss bound. “Can be deleted” is not a hard deadline; O7 says cleanup may remain asynchronous. | CLOSED |
| P6 finite financial exposure | **PARTIAL** | O1/O3/O15 publish model, tool and container billing categories and current container rates; the proposed profile removes networked tools/vault/MCP and selects `small`. | No enforceable maximum agent steps/model calls/retries/output tokens/active hosted duration is documented for one session/turn; usage is best effort, can change and is not a final bill (O9). No hard per-operation spend cutoff, maximum accounting lag/overshoot or complete retained-charge bound is established. | CLOSED |
| P8 result / effect observation | **PARTIAL** | O5/O8 provide terminal turn events, saved items and immutable artifacts tied to session/turn/path, surviving environment expiry. File/artifact size limits are explicit. | Completion does not prove every tool succeeded; stream events are not replayed; retention/expiry/not-found/truncation coverage for items, turns, traces and artifacts is not fully stated; unpublished/background effects and deletion blind spots remain. | CLOSED |
| P9 unknown-effect reconciliation | **PARTIAL** | O5/O6 provide durable session retrieval and saved items after disconnect; original IDs can be retained; O7 defines deletion response semantics. | No create/input idempotency key or durable direct-command identity/lookup semantics are documented. Public deletion and expired/missing records cannot distinguish never happened from happened then became unobservable; physical cleanup is asynchronous. | CLOSED |
| P10 evidence integrity | **PARTIAL** | O9–O11 provide provider-side events/history/traces and signed, deduplicable webhook envelopes; Nexus could protect downloaded receipts externally. | No security-grade receipt binds requested and applied environment config, deployment revision, exact command/loaded bytes, actor, result/effects and cleanup to one operation. Trace availability is delayed/partial-at-export; completeness and retention guarantees are unresolved. | CLOSED |
| P11 credential lifecycle | **PARTIAL** | O12 documents project-key permission scopes and keeping the application key outside the environment; O13 can keep optional third-party secret values outside a hosted sandbox. The proposed profile uses no vault. | Rotation/revocation propagation and effects on existing sessions, active turns, event streams, vault grants and concurrent clients are not documented with a bound. Current actor/key custody would also require account-specific evidence later. | CLOSED |
| P12 version / drift / requalification | **PARTIAL** | O14/O16 identify beta/GA configuration surfaces, requested model and session configuration; O3/O4 identify environment type/status/size. | No hosted image/runtime/platform-policy revision, deployed change identity, material-change notice or compatibility/requalification contract binds the qualified execution. API/config identity does not identify enforcement implementation. | CLOSED |

Counts across P1–P6 and P8–P12: **SUPPORTED 0; PARTIAL 11; NOT DOCUMENTED 0; CONTRADICTED 0; NOT APPLICABLE 0.** The uniform PARTIAL result is deliberate: each property has relevant official semantics, but every row retains at least one mandatory provider-side gap.

## 6. P7 lifecycle experiment status

P7 remains **EXPERIMENT-RESOLVABLE / NOT PASS**. O5 defines `agent.session.input.cancel` and the terminal `agent.session.turn.cancelled` event. O3 says closing the stream does not cancel work and describes a bounded client retry strategy for cleanup-request `409`. O7 requires running execution to be cancelled before session deletion and explicitly states that physical cleanup may continue after public deletion.

These interfaces could support a future fault-injected experiment measuring active-turn cancellation, stream disconnect, lost acknowledgement, deletion ordering, descendants/background work, terminal status and post-cancel observations. Documentation does not guarantee a hard cancellation deadline, complete descendant cessation, physical-cleanup completion signal or reconciled external effects. P7 cannot compensate for any closed C-row advance gate.

## 7. Cost and lifetime boundary

The proposed `small` sandbox currently maps to 1 GB and the standard container pricing table lists 1 GB at USD 0.03 per 20-minute session. This is a rate, not a hard maximum. Model usage is separately billed, the managed harness may make multiple model/tool-loop steps, and the official usage resource is best effort and not the final bill. The one-hour inactivity wording is permissive (“can be deleted”), applies after activity and keep-alives stop, and is not configurable; it does not bound active work. Session deletion can leave physical cleanup in progress.

Consequently Nexus cannot yet calculate a conservative finite all-in maximum exposure before dispatch from authoritative enforceable semantics. A cheap example, account usage limit, post hoc usage object or client timeout would not close P6.

## 8. Observation, reconciliation and evidence custody

The strongest documented observation chain is `session.id → turn/item IDs → command/tool items → artifact.id + turn_id + path`, supplemented by environment ID/status, signed webhook event IDs and exported traces. This is materially stronger than guest self-report and makes the mode a genuine candidate.

It remains incomplete because live streams do not replay, traces are built later and export only currently available records, a completed turn does not guarantee tool success, and deletion can abandon unpublished output while physical cleanup continues. No complete provider receipt binds actual applied restrictions and deployed revision to admitted bytes, command/effects, final cleanup and the exact observation set. Nexus must therefore retain protected controller-side receipts and preserve UNKNOWN on any gap; it cannot infer no effect from deletion, expiry, missing artifact or missing usage.

## 9. Codex Cloud secondary check

The bounded secondary check covered the official [Codex Cloud overview](https://developers.openai.com/codex/cloud), [cloud environments](https://developers.openai.com/codex/cloud/environments), and [legacy agent internet access](https://developers.openai.com/codex/cloud/internet-access) pages. They describe user-facing cloud tasks/environments, repository checkout, setup/maintenance scripts and agent-phase internet controls. The bounded search found no Codex Cloud customer Host API exposing the same first-class session/environment/turn/item/artifact lifecycle plus stronger deployed-runtime, applied-policy, hard-budget or reconciliation receipts.

Codex Cloud is therefore **INSUFFICIENT AS A STRONGER ROUTE B DOCUMENTATION SOURCE** for this decision. No Codex Cloud guarantee is imported into the Agents API matrix, and no second provider evaluation is opened.

## 10. Experiment-readiness decision and finite next boundary

**OPENAI-HOSTED AUTHORITATIVE PREREQUISITES = INCOMPLETE.**

The exact OpenAI-hosted Agents API environment is a legitimate Route B Host candidate. It does not yet cross the accepted advance gate. P1–P6 and P8–P12 are all PARTIAL; P7 remains experiment-resolvable and NOT PASS. The blocking common core is:

1. P1/P12: no actual hosted deployment/runtime/enforcement identity or material-change contract;
2. P3/P10: no fresh instance-bound applied-policy and complete execution/cleanup receipt;
3. P5: no complete hard whole-unit lifetime/resource/descendant bound;
4. P6: no enforceable finite maximum for every billable dimension before dispatch;
5. P8/P9: incomplete retention/not-found/idempotency and post-delete effect-reconciliation semantics;
6. P2/P4/P11: incomplete closed actor/input graph and active-authority revocation behavior.

The minimum next action is the separate [OpenAI-hosted support question pack](nexus-g2-route-b-openai-hosted-support-question-pack-v1.md). It requests one coherent authoritative response/API-contract bundle for only these gaps. Silence, marketing assurances, account settings, requested configuration or a cheap run remain UNKNOWN. No experiment is justified until every mandatory row has enough authoritative provider-side semantics for its later experimental half to be meaningful.

The separate [bounded adversarial review](nexus-g2-route-b-openai-hosted-adversarial-review-v1.md) challenges this result and binds the exact bytes of this evaluation. No MANIFEST change, acceptance record or commit is authorized in this phase.

**Disposition: B. OPENAI CLARIFICATION IS REQUIRED BEFORE A BOUNDED EXPERIMENT.**
