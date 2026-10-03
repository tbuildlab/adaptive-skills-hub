# Nexus G2 Route B Fresh Provider Adjudication v1

Date: 2026-10-03. Status: **FACTUAL CHECKPOINT ONLY; NO QUALIFICATION OR TASK AUTHORITY.**

Authority and historical per-row bindings: [delta matrix](nexus-g2-route-b-fresh-evidence-delta-v1.md). All D/M/E/O citations below resolve in the [source register](nexus-g2-route-b-fresh-source-register-v1.md), retrieved 2026-10-03. Public evidence is not runtime observation. No account, credentials, runtime or billing settlement was inspected. The three modes retain their historical exclusions; features discussed outside a mode are risk analysis, not permission to enable them.

## 1. P5: fourteen required questions

TTL reset authority is not by itself architectural impossibility: a qualified Nexus controller may enforce no extension, no retry and credential/actor exclusion. No such current composition is qualified. Sandbox lifetimes do not govern an external model harness.

| Question | Daytona | Modal | E2B |
| --- | --- | --- | --- |
| 1. Hard maximum lifetime? | Wall TTL when explicitly nonzero; no unconditional default bound (D01) | Sandbox timeout; default 300s, maximum 24h (M01/M02) | Destructive timeout; continuous-run plan cap 1h/24h, not cumulative resume cap (E01) |
| 2. Enforcing layer? | Provider lifecycle service; cgroup resource layer (D01/D06) | Provider Sandbox lifecycle; CPU throttle/memory OOM (M02/M04) | Provider lifecycle/plan; allocation returned by Platform (E01/E11) |
| 3. Workload can reset? | API credentials could enable reset; guest non-reachability not qualified (D07/D08) | Guest must lack reachable workspace authority; actor graph unqualified (M09) | Project key must remain unavailable to guest; envd/control separation documentary only (E05/E07) |
| 4. Controller can reset? | Yes, setTtl resets; no-extension must be enforced (D08) | Creates/recreates a new lifetime; no recreation permitted by hypothetical fixed mode (M02) | Yes, setTimeout resets; resume starts another continuous interval (E14/E01) |
| 5. Survives controller loss? | Documented hard existence ceiling is client-independent; effective compliance/failure observation remains unqualified (D01) | Lifetime not a client wait; infrastructure failure/tail bound UNKNOWN (M02) | Timeout independent of ordinary client; fault-path cessation bound UNKNOWN (E01/E12) |
| 6. Setup/main/descendants/background/paused/model/cleanup? | TTL covers started/stopped/paused/archived unit; setup/cleanup failure timing and external loops UNKNOWN (D01) | Unit lifetime includes running work; timer origin/setup, entire tree, persistence and cleanup scope UNKNOWN (M01) | Running unit expires; paused retained state/auto-resume is separate; setup/cleanup/external loop coverage incomplete (E01/E13) |
| 7. Expiry outcome? | Destroy (D01) | Timeout terminates Sandbox; complete tree/terminal reconciliation not observed (M01/M02) | Kill releases unit by default; pause preserves it in other mode (E01) |
| 8. Sync or async? | Delete defaults fire-and-forget; waited delete is separate (D08) | terminate wait flag controls waiting; timeout execution is service-side (M02) | Delete 204 means killed; lost response remains UNKNOWN (E12) |
| 9. Maximum termination delay? | D01 promises existence bounded by declared TTL; D08 does not give a separate delete-operation latency maximum | UNKNOWN; waiting/polling is not finite fault guarantee (M02) | UNKNOWN under failed/lost kill or infrastructure fault; normal kill described promptly (E10/E12) |
| 10. CPU ceiling? | cgroup hard cap; exact quota/config observation still Q (D06) | Explicit hard limit, not request alone; physical-core units (M03/M04) | Template CPU allocation and plan ceiling documented; hard workload enforcement evidence still Q (E02/E11) |
| 11. Memory ceiling? | cgroup cap; actual binding Q (D06) | Explicit limit/OOM; actual binding Q (M04) | Allocated memory; hard enforcement/failure behavior not independently qualified (E02/E11) |
| 12. Disk/persistence? | Disk allocated/billed; detached snapshots/volumes outside unit need exclusion or own finite bounds (D02) | Ephemeral container disk bounded by quota/worker availability; persistent services outside unit (M04) | Plan disk included; paused/persistent modes outside fixed kill scope (E03) |
| 13. Can descendant survive? | Isolation claim does not provide tested zero-live whole-tree/fault evidence (D06) | Same-container scope is not complete tree/alternate-creation cleanup proof (M01/M02) | Sandbox termination semantics do not prove every reachable external process/effect ceased (E10/E12) |
| 14. Resources outside envelope? | Organization APIs, detached storage, previews/integration/model calls (D02/D07) | Workspace services/storage/network/model harness (M05/M07/O01) | Project APIs/builds/snapshots/volumes and external model harness (E07/E13/O01) |

**P5 conclusion for EACH provider: PROVIDER_CLARIFICATION_REQUIRED.** Resource/lifecycle controls are meaningful; no complete presently admissible whole-unit/failure envelope has been established. Process-count/output channels can be bounded by a qualified application/Host combination when applicable; universal provider-native PID limits are not newly required. Remaining questions concern the exact reachable unit, not every provider feature.

## 2. P6: exhaustive reachable-driver review

Review scope is one proposed deterministic CPU Sandbox on an existing fixed image/template, no models or new builds, snapshots, mounts/volumes, GPU, sidecars, MCP, arbitrary browsing, resume or automatic recreation. These are intended exclusions only: an actual preflight must prove that the control/workload operation graph cannot reach them before treating a term as zero. Published rates below are inspection-time figures, not reserved price ceilings. USD terms are not a current owner authorization or foreign-exchange ceiling.

| Material dimension | Daytona | Modal | E2B |
| --- | --- | --- | --- |
| CPU | D03: $0.0504/vCPU/hour; hard cap binding Q | M08: $0.00003942/physical core/second; request vs actual M03 | E03/E04: $0.000014/vCPU/second; fixed allocation |
| Memory | D03: $0.0162/GiB/hour | M08: $0.00000667/GiB/second; explicit hard limit needed | E03/E04: $0.0000045/GiB/second |
| Duration | D02: reserved resources charged during creation/start/stop/pause transitions and active state | M01/M02 maximum lifetime; metered setup/failure tail still needs bound | E02 running-time allocation billing; normal kill/timeout stops charging |
| Disk/storage | D03: $0.000108/GiB/hour above free allowance; reserve full disk conservatively | M04 ephemeral quota; price/applicability to exact Sandbox needs binding | E03 included plan disk; RAM default conflict must not select resources |
| Stopped/paused storage | D02 stopped/paused storage still billed | Persistent/snapshot resources need exclusion; no automatic zero inference | E01/E02 pause compute free, indefinite retained unit; auto-resume excluded |
| Images/builds | Fixed existing image intended; creation/build side effects not implicitly excluded by timeout | No package/image build authorized; readiness/setup charges unresolved | No template build authorized; existing fixed build identity required |
| Snapshots | D02 survive unit deletion; separately billed/retained if reachable | Separate persistence must be unreachable or bounded | Pause/snapshot/clone paths excluded and must be denied |
| Volumes/mounts | Separate retained resources: excluded only after graph closure | Separate storage and IO: excluded only after graph closure | Separate persistence: excluded only after graph closure |
| GPU | Excluded; CPU-mode binding required | Excluded; GPU parameter must not be reachable | Excluded; no new GPU profile admitted |
| Network/egress | Exhaustive rate/byte ceiling UNKNOWN; no price mention is not free egress | M06 charges effective Oct 1; Starter allowance 1 TiB, excess $0.04/GiB; allowance not execution cap | Exhaustive rate/byte or non-billable inclusion binding UNKNOWN; network denial alone not zero-price proof |
| API operations | No exhaustive charge/inclusion boundary established | No exhaustive charge/inclusion boundary established | No exhaustive charge/inclusion boundary established |
| Cleanup tail | D02 provider-fault failed-deletion no-charge clause narrows exposure but attribution/scope remain | No numeric all-in termination/cost tail | E02 immediate stop-billing statement supports normal path; fault attribution/settlement remains |
| Delayed destruction | TTL/await request do not quantify failed destruction billing tail | wait=True does not cap maximum billed failure tail | Delete errors/lost acknowledgement retain ambiguity; no retry extension authorized |
| Retained resources | D02 snapshots and stopped disk are separate from compute termination | Detached/persistent objects must be positively excluded or independently bounded | Retained pause/auto-resume explicitly excluded from historical formula |
| Bundled model usage | None in fixed deterministic mode; Agents SDK external calls separate | None in fixed deterministic mode; external model loop not under Sandbox timer | None in fixed deterministic mode; external model loop not under Sandbox timer |
| Other fees/minimums/taxes/FX | Current tier/top-up, rounding, price period and applicable invoice terms require binding | Workspace shared usage, gross budget vs net spend, minima and invoice terms require binding | Plan/subscription/minima/current rates and exact ledger settlement require binding |

For declared caps C (CPU), M (GiB), D (disk GiB), T (seconds), the supported **compute components** are:

- Daytona: `T * (0.0504*C + 0.0162*M + 0.000108*D) / 3600`, using full disk rather than assuming a shared free allowance. Billable states may outlast requested active time (D02/D03).
- Modal: `T * (0.00003942*C + 0.00000667*M)`, C in physical cores with hard ceilings and metered max(request, actual) (M03/M08).
- E2B: `T * (0.000014*C + 0.0000045*M)`, fixed kill-only allocation with included disk (E02/E03). This retains historical documentary support; pause/resume/SDK automatic wake-up cannot inherit it.

For EVERY provider the required pre-dispatch expression is instead:

`MAX_EXPOSURE = compute_under_all_billable_states + separately_retained_storage + bounded_egress_bytes*rate_ceiling + build/snapshot/volume/GPU/API/model_terms_if_reachable + minimums/rounding/applicable_invoice_terms + cleanup_and_fault_tail + approved_conversion_buffer`.

Every term must be bounded by an authoritative ceiling or justified unreachable/non-billable in the exact protected composition. Requested T cannot substitute for maximum billable T, unknown prices cannot be zero, and any reset/recreation path needs exclusion. No numeric all-in maximum can currently be evaluated. P6: Daytona/Modal PROVIDER_CLARIFICATION_REQUIRED; E2B whole-property PARTIAL, with its previously SUPPORTED narrow provider compute half preserved.

Daytona's cancellation clauses describe up to 48h reporting, a 30-day claim window and a final summary within five business days; they concern billing cancellation, not a numeric maximum charge or per-unit deletion SLA (D02). Modal gross usage budgets, net spend limits and Environment compute budgets have different scopes (M05). E2B credits/spend limits and all providers' resource quotas are not substitutes for per-dispatch conservative exposure. Reporting delay is not necessarily extra accrual; final settlement and stopped accrual remain separate.

## 3. P7: ten distinct states

Each cell describes documented observation interfaces/meaning, **not a state observed this run**. D08, M02 and E12 are the main lifecycle API bindings; billing rows additionally use D02, M05/M06 and E02. No generic cancellation method is assumed equivalent across providers.

| State | Daytona | Modal | E2B |
| --- | --- | --- | --- |
| CANCEL_REQUESTED | stop/force-stop/delete submitted; controller receipt needed | terminate submitted; controller receipt needed | kill/delete submitted; controller receipt needed |
| CANCEL_ACKNOWLEDGED | API success/request acceptance; wait flag matters | terminate return depends on wait option | 204 documents successful kill, stronger than mere acceptance; loss is UNKNOWN |
| EXECUTION_STOPPING | Lifecycle stopping state may be observable | poll/wait distinguishes pending from exit, not every descendant | Pending request/query/lifecycle observations; no invented universal stopping event |
| EXECUTION_CEASED | Stopped/terminal control state is component evidence; task effects still need binding | wait/poll/exit evidence is component evidence | Successful kill/runtime query is component evidence |
| DESCENDANTS_CEASED | Whole-unit negatives and externally bound zero-live evidence unqualified | Complete tree and alternate creation observations unqualified | Whole-unit tree/failure evidence unqualified |
| SANDBOX_TERMINATED | Deletion/destroy state; waited completion separate | Terminated unit versus pending request must be distinguished | Killed/timeout destruction mode; pause not termination |
| RESOURCE_RELEASED | Stopped != deleted; storage/snapshots can remain | Process exit != all persistent object deletion | Destroyed mode releases unit; detached resources excluded only with evidence |
| BILLING_CEASED | D02 maps states; stopped storage remains chargeable | No account-specific settled cessation or bounded tail established | E02 normal kill/timeout/pause billing cessation stated, not a final invoice |
| RESULT_OBSERVED | Original command/session/status/log observations, gaps retained | Entrypoint logs/exit, exec coverage gaps retained | Lifecycle IDs/events not complete command result evidence |
| EFFECTS_RECONCILED | Nexus original IDs/artifacts/exposure protected; unresolved means no retry | Same rule; reusable names are not effect identity | Same rule; 404 missing/inaccessible does not prove never started |

P7 remains **EXPERIMENT_RESOLVABLE / NOT PASS** for all three, but **no experiment is safe to authorize now**. An eventual lost-response/controller-loss test may compare original-unit provider observations, zero-live evidence, effects and settled cost only after P5/P6/controller prerequisites already bound its exposure. A client timeout, lost stream, no PID, HTTP 404, kill/delete method name or an exit code cannot establish the full sequence. No unbounded retry/poll loop is proposed.

## 4. Official OpenAI Agents SDK compatibility only

O01-O03 document `DaytonaSandboxClient`, `ModalSandboxClient`, `E2BSandboxClient`; Python extras are `openai-agents[daytona/modal/e2b]`, JS import paths `@openai/agents-extensions/sandbox/{provider}`. Fixed source snapshots O04-O11 are the actual basis below, not assumed package installations. Python source version **0.23.1**, commit `81f0ccf20c6e24063b9da36fa37f2bdb6a43d8d3`; JS extensions source version **0.18.0**, commit `96aa754b69282fef3bf8be2f15897985400ee0a6`. Publication date/installed version UNKNOWN.

| Provider | Python declared dependencies | JS peer / dev dependencies | Lifecycle/settings exposed | Safety-critical limitation | Credentials/custody |
| --- | --- | --- | --- | --- | --- |
| Daytona | daytona>=0.155.0 | @daytonaio/sdk ^0.201.0; dev 0.201.0 | create/start/resume/delete/session close; resource and caller-wait/idle controls | Reviewed create options do not expose explicit wall TTL; snapshot path can bypass resource overrides | Organization API key in trusted controller; source serialization/custody must not leak it |
| Modal | modal==1.4.3 | modal ^0.7.6; dev 0.7.6 | create/resume/delete/terminate/session close; lifetime + CPU/memory hard settings | Lifetime differs from create/command wait timeout; older Python pin is not current 1.6 backend evidence | Modal owner/service credentials in controller; GPU/mount/port helpers excluded |
| E2B | e2b==2.31.0; e2b-code-interpreter==2.8.1 | e2b ^2.14.1; dev 2.51.0; code-interpreter ^2.3.3 dev 2.8.0 | create/connect/resume/delete/session close; timeout/lifecycle/network options | Python defaults on_timeout=pause, auto_resume=True; JS seconds vs underlying milliseconds; API generation must be pinned | Project key in controller; envd token separate; no token exported to a restricted subject |

The SDK adds an external model/tool-routing harness, optional filesystem/mount/credential helpers and persistence/recreation paths. Those are new reachable channels to assess, not a qualified Nexus adapter. Model authorization/cost/deadline is outside the Sandbox resource timer; an optional OpenAI model key is separate from compute credentials. No model call or SDK installation occurred. A generic SDK client being official does not satisfy G2. Any future use requires separately qualified exact-stack custody, explicit disabled extras, fixed mode and full operation-graph bounds. Provider client availability does not close P5/P6 or grant execution authority.

## 5. HQ1-HQ6 responsibility mapping

| Gate | Supporting-property classification | Fresh evidence / unresolved binding | Current status |
| --- | --- | --- | --- |
| HQ1 | PROVIDER-MANDATORY + COMPOSITE + QUALIFICATION-EXPERIMENT | Provider instance/build/runtime APIs; actual Nexus admitted loaded bytes/dependencies and operation binding still unqualified | NOT PASS |
| HQ2 | PROVIDER-MANDATORY + COMPOSITE + QUALIFICATION-EXPERIMENT | Isolation/network/token semantics plus exact actor/secret/escape negatives; custody not qualified | NOT PASS |
| HQ3 | PROVIDER-MANDATORY + COMPOSITE + QUALIFICATION-EXPERIMENT | Closed command/file/env/mount/network/service inputs; effective observations and denied indirect channels missing | NOT PASS |
| HQ4 | PROVIDER-MANDATORY + COMPOSITE + QUALIFICATION-EXPERIMENT | Hard resources/lifetime, whole-unit termination, controller-loss/fault fallback and zero-live observations incomplete | NOT PASS |
| HQ5 | NEXUS-OWNED + COMPOSITE + QUALIFICATION-EXPERIMENT | Protected source/config/time/unit/operation evidence, no-replay, gaps and original UNKNOWN; provider telemetry corroborates | NOT PASS |
| HQ6 | NEXUS-OWNED + COMPOSITE + QUALIFICATION-EXPERIMENT | One accepted capability pre-effect authority/budget, checkpoint/recovery/reconciliation primitives need complete Host binding first | NOT STARTED |

HQ1-HQ4 may be supplied by equivalent qualified platform properties, with Nexus verifying/binding them. HQ5/HQ6 remain Nexus responsibilities. This is the accepted Responsibility Re-baseline, not six documentation PASS verdicts. No LPAC-specific mechanism is made universal; the exited LPAC route is not reopened.

## 6. Decisions and minimum material clarification

| Provider | Exactly one verdict | Why evidence improved but does not cross the safe-experiment gate |
| --- | --- | --- |
| Daytona | **B. PUBLIC EVIDENCE IMPROVED BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | Previously uncaptured provider-fault charging/settlement clauses and clearer enforcement evidence narrow questions; per-dispatch fault tail/all-in charge/channel/actor closure still missing. TTL was already known. |
| Modal | **B. PUBLIC EVIDENCE IMPROVED BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | Announced egress charging is now effective and metering/budget scopes clarified; hard tuples/lifetime do not close counted traffic, shared-cap overshoot and cessation tail. |
| E2B | **B. PUBLIC EVIDENCE IMPROVED BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | API kill success, continuous-versus-resumed lifecycle and exact SDK defaults make scope clearer; no complete current all-in/fault/actor binding. Historical kill-only compute support remains. |

No A exists, so Phase 15 is **NOT APPLICABLE**: no speculative experiment design, resources, numeric owner exposure or executable package. B does not mean better safety, new capability, provider selection or formal acceptance.

Only the following compact provider questions could materially change readiness; this is not a new generic questionnaire or permission to send it:

| Route | Minimum authoritative clarification needed | What it would change |
| --- | --- | --- |
| Daytona | For fixed hosted container/Tier 3-4/no extras/no reset: confirm all-in accrual ceiling and charge inclusions for the already documented hard existence TTL, including billed setup/failed teardown/egress/persistence; clarify actor-exclusion and denial scope for reachable channels. | Close P5/P6 prerequisite versus prove mode cannot meet it; fault no-charge clause alone is insufficient. |
| Modal | For fixed CPU/gVisor/block-all/hard tuples/no extras: maximum setup/termination/fault billing tail, all counted egress/storage/minimums, and quantitative gross-budget cutoff if used; clarify immutable/actor-excluded policy and reachable exceptions. | Decide finite all-in unit ceiling; shared workspace budget is not itself dispatch reservation. |
| E2B | For exact secured POST-v2 template/kill/no resume/no extras: complete failure-path deadline and all-in charge inclusion/rate ceiling; resolve schema/default generation and full denial/actor boundaries. | Preserve narrow compute formula while deciding whether a safe complete binding is possible. |
| OpenAI human route | Existing pending targeted hard-envelope escalation remains useful only if a human/platform authority supplies binding bounded semantics beyond the AI-assisted public-doc reply. | May change prerequisite evidence, not qualify a Host. No repeat broad research or outreach is performed here. |

All three deserve **conditional later clarification**, without preference/ranking; no current Route B candidate has sufficient evidence. Answers do not replace Nexus controller qualification. Once authoritative prerequisites close, a separately authorized preflight must verify account/actor/custody, price/headroom, fixed controls and complete graph before proposing a bounded experiment. No future cleanup/upload/create is implicit authority.

## 7. Factual checkpoint and finite stop

These four additive documents plus canonical MANIFEST are the only justified repository checkpoint. No architecture acceptance record, HostAdapter, runtime, phase advance or support dispatch is created. Deterministic hygiene, 36-row coverage, source/hash bindings, manifest isolation and relevant offline tests are required. Known governance baseline is 52 PASS / 3 SKIP / 1 FAIL / 1 ERROR; unexpected drift must not be silently reattributed.

Exact STOP: **No complete conservative pre-effect provider/controller P5/P6 envelope exists for any candidate; incomplete documentation cannot be repaired by running the experiment.** Next recommended task: owner review of this factual delta, then separately authorize only the minimum targeted authoritative clarification. OWNER ACTION REQUIRED for execution: **NO** (no experiment proposed); later outreach requires separate authority. SAFE RESUME POINT ESTABLISHED.

Scenario 01-04 = NOT RUN; HQ1-HQ5 = NOT PASS; HQ6 = NOT STARTED; Positive Host Binding = ABSENT; G2 = HOLD; OpenAI human escalation = PENDING. No provider execution/accounts/login/keys/resources/paid activity; no secret access. Only public page/source retrieval occurred. A0-A6 and P1-P12 semantics remain unchanged.
