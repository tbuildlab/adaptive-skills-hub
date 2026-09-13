# Nexus Ecosystem Gap Scan — Extreme Comprehensive Research Pass

> **Roadmap authority notice — 2026-09-13:** This report's research observations,
> dispositions and old Slice 4/5/6/7/R6 proposals are retained as historical
> evidence. [Owner-accepted Roadmap V2](nexus-roadmap-v2.md) governs remaining
> future work and supersedes the old roadmap, including Section 32. Its G5 is
> optional/conditional; a generic Nexus Agent Runtime is not a default product
> responsibility. Historical `INTEGRATE` recommendations confer no trust,
> approval, routability or execution authority. G1 has not started.

**Status:** Research complete; architecture review required before any implementation.
**Research date:** 2026-08-27
**Repository:** `TDY0225/adaptive-skills-hub` (Private)
**Research branch:** `nexus-ecosystem-gap-scan`
**Starting baseline:** `32d01941acca95a9067329f0493508d151893b42`

> This report is research and architecture evidence only. No discovered project was installed, executed, vendored, granted routing authority, or made a Nexus dependency. `INTEGRATE` means a narrowly scoped future integration is recommended after a separate approval gate; it does not mean integration occurred.

## 1. Baseline verification

The research branch was created from the accepted Slice 1 baseline:

| Item | Verified value |
|---|---|
| `main` / `origin/main` at research start | `32d01941acca95a9067329f0493508d151893b42` |
| `post-r5-runtime-integration-slice1-final^{}` | `32d01941acca95a9067329f0493508d151893b42` |
| `runtime-r5-final^{}` | `627484495a6578b13532e7560918c137394379af` |
| Research branch | `nexus-ecosystem-gap-scan` |
| Repository visibility | Private |
| Runtime changes | None |
| Frozen-tag movement | None |
| Candidate execution/installation | None |

The accepted upstream-source registry was treated as authoritative evidence for its pinned seed commits. Those sources were not re-audited wholesale.

| Seed source | Pinned commit | License | Existing category | Existing trust tier | Treatment |
|---|---:|---|---|---|---|
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | `9572c66428bb` | MIT | agent-definition-catalog | trusted_seed_canonical | Preserved from accepted audit; not re-audited wholesale |
| [jnMetaCode/agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) | `972452cdedef` | MIT | localized-agent-definition-overlay | trusted_seed_localized_overlay | Preserved from accepted audit; not re-audited wholesale |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | `11a4bc330e4b` | Apache-2.0 | llm-application-and-skill-example-collection | trusted_seed_component_review_required | Preserved from accepted audit; not re-audited wholesale |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | `d23d7f88a2e2` | MIT | skill-catalog-and-design-resource | trusted_seed_pinned_component | Preserved from accepted audit; not re-audited wholesale |
| [rdev/liquid-glass-react](https://github.com/rdev/liquid-glass-react) | `ac48eab18d1f` | MIT | react-ui-library | trusted_seed_reference | Preserved from accepted audit; not re-audited wholesale |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | `788a890bd022` | MIT | multi-agent-harness-framework-and-skill-corpus | trusted_vendor_reference | Preserved from accepted audit; not re-audited wholesale |
| [greensock/GSAP](https://github.com/greensock/GSAP) | `13e2b7905464` | GreenSock Standard License; non-OSI SPDX classification | javascript-animation-library | trusted_seed_license_gate | Preserved from accepted audit; not re-audited wholesale |
| [openai/codex](https://github.com/openai/codex) | `10d5a603aecb` | Apache-2.0 | official-agent-runtime-and-protocol-reference | official_vendor | Preserved from accepted audit; not re-audited wholesale |
| [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | `b150a551b8d4` | MIT | agent-runtime-harness-framework | official_vendor_preview | Preserved from accepted audit; not re-audited wholesale |
| [revfactory/harness](https://github.com/revfactory/harness) | `cceac68ea1d0` | Apache-2.0 | claude-skill-factory | reviewed_community | Preserved from accepted audit; not re-audited wholesale |
| [cft0808/edict](https://github.com/cft0808/edict) | `14a207557719` | MIT | multi-agent-runtime-and-governance-harness | reviewed_community | Preserved from accepted audit; not re-audited wholesale |
| [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | `fe0374687037` | MIT | skill-and-persona-factory | reviewed_community | Preserved from accepted audit; not re-audited wholesale |

The unresolved `github.com/green` organization entry remains unresolved because an organization URL is not an auditable repository.

## 2. Search methodology

The scan used 55 bounded GitHub search queries plus canonical repository, README, LICENSE, SECURITY, source-tree, release, and official-protocol checks. It did not recursively crawl GitHub.

The strategy deliberately combined:

1. 24 systematic domain queries across A-R.
2. 24 alternative-terminology queries.
3. 7 exact-name checks for the specifically named candidates.
4. Official/vendor repositories and official specifications.
5. Direct references and adjacent projects found from the accepted seed set.
6. Canonical repository renames and alias resolution.
7. A bounded serious-candidate promotion step.

| Query domain | Queries | Raw results | Terms |
|---|---:|---:|---|
| A-memory | 4 | 40 | `"agent memory" framework`<br>`"long term memory" multi agent`<br>`agentic memory framework`<br>`persistent memory agents` |
| B-context | 3 | 12 | `"context engineering" agent`<br>`context management LLM agents`<br>`context compression LLM` |
| C-registry | 4 | 11 | `"agent skill registry"`<br>`"capability registry" MCP`<br>`capability catalog agents`<br>`trusted skills registry` |
| D-discovery | 4 | 20 | `"skill marketplace" agent`<br>`"dynamic tool discovery" MCP`<br>`agent tool discovery`<br>`skill discovery RFC` |
| E-runtime | 3 | 10 | `"agent runtime" lifecycle checkpoint`<br>`durable agent runtime`<br>`agent lifecycle state machine` |
| F-multi-agent | 3 | 10 | `"multi agent orchestration" supervisor`<br>`multi agent DAG orchestration`<br>`planner reviewer agents` |
| G-evaluation | 3 | 0 | `"agent evaluation" framework`<br>`agent eval quality gates`<br>`hallucination groundedness eval` |
| H-self-healing | 2 | 0 | `"self healing agent" repair`<br>`agent recovery rollback` |
| I-security | 4 | 20 | `"MCP security" scanner`<br>`"agent sandbox" tool isolation`<br>`sandbox AI agents`<br>`prompt injection MCP` |
| J-observability | 2 | 1 | `"agent observability" tracing`<br>`agent trace OpenTelemetry` |
| K-workflow | 2 | 0 | `"durable execution" agent`<br>`agent DAG scheduler` |
| L-code-intelligence | 2 | 0 | `"code graph" LLM agent`<br>`code intelligence graph agents` |
| M-skill-factory | 2 | 0 | `"skill generation" agent`<br>`skill synthesis evaluation` |
| N-mcp | 3 | 10 | `"MCP registry"`<br>`"MCP gateway" security`<br>`MCP gateway proxy` |
| O-harness | 2 | 0 | `"coding agent harness"`<br>`coding agent environment sandbox` |
| P-interoperability | 1 | 0 | `"agent protocol" MCP A2A` |
| Q-planning | 1 | 0 | `"hierarchical planning" agent` |
| R-checkpoint | 3 | 0 | `"agent checkpoint" resume`<br>`"LLM workflow" idempotency replay`<br>`agent checkpoint idempotency` |
| exact:TencentDB-Agent-Memory | 1 | 10 | `TencentDB-Agent-Memory` |
| exact:Agent Registry | 1 | 10 | `"Agent Registry"` |
| exact:Open SSR | 1 | 0 | `"Open SSR" agent` |
| exact:skills-registry | 1 | 10 | `skills-registry` |
| exact:skills-mcp | 1 | 10 | `skills-mcp` |
| exact:agent-discover | 1 | 10 | `agent-discover` |
| exact:Open Multi-Agent | 1 | 0 | `"Open Multi-Agent"` |

Several quoted GitHub searches returned zero results even when canonical projects were known under different terminology. That is search-engine evidence, not proof that the capability does not exist. Alternate terminology and explicit canonical checks were therefore required.

Diminishing returns were reached when additional results were predominantly forks, small demos, vertical applications, unmaintained repositories, SEO/awesome lists, or duplicates of already promoted architectures.

Primary standards/product sources included the [OpenAI plugin model](https://developers.openai.com/plugins), [OpenAI MCP guidance](https://learn.chatgpt.com/docs/extend/mcp), [official MCP Registry](https://modelcontextprotocol.io/registry/about), [Agent Skills specification](https://agentskills.io/specification), [A2A specification](https://a2a-protocol.org/dev/specification/), and canonical project repositories.

### Nexus-guided workflow evidence

The accepted Nexus production handoff was consulted exactly once for this substantial research task. It selected and loaded:

| Field | Evidence |
|---|---|
| Skill | `research` |
| Resource ID | `skill:636f8dc6b3d41df7` |
| Source scope | `external-local` |
| Loaded content SHA-256 | `bf824e72dd93941c8d591e4af13bb7e3a09380cd6ed7dd8c1f61a295648fa023` |
| Load state | `loaded_verified` |
| Agents recommended/consulted | None |

The selected Skill is a Product Design UX research workflow, so it is not a complete semantic match for ecosystem architecture/security research. Its source-grounding, evidence/inference separation, source-map and anti-overclaiming rules were materially applied. Its interview, Figma and visual UX workflow was not forced. Native Codex research covered the uncovered GitHub, architecture, license, security, deduplication and Git work. This routing mismatch is recorded as a Nexus gap; no runtime change was made during this research phase.

## 3. Capability-domain coverage

All required domains A-R received meaningful coverage. The current-state labels are evidence-based:

- **STRONG:** proven accepted controls already exist.
- **PARTIAL:** useful production capability exists, but important generic behavior is absent.
- **FOUNDATION ONLY:** contracts or data models exist without the full runtime/control plane.
- **MISSING:** no implemented Nexus capability.
- **DEFERRED:** explicitly outside the accepted runtime.

| ID | Domain | Current Nexus state | Principal gap | Strong candidates | Recommended direction | Priority |
|---|---|---|---|---|---|---|
| A | Memory / Long-term Memory | **MISSING** | No persistent cross-session/team memory, consolidation, forgetting, conflict or permission model. | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)<br>[getzep/graphiti](https://github.com/getzep/graphiti)<br>[mem0ai/mem0](https://github.com/mem0ai/mem0)<br>[langchain-ai/langmem](https://github.com/langchain-ai/langmem) | Design a Nexus-owned, opt-in, provenance-first memory ledger after checkpoint/evaluation foundations. | P3 |
| B | Context Engineering | **PARTIAL** | Progressive Skill loading and bounded evidence exist; no general compaction, token budgeting, caching or task context assembler. | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)<br>[pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)<br>[TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)<br>[langchain-ai/langmem](https://github.com/langchain-ai/langmem) | Adapt explicit budgets, typed context slots and snapshot hashes; no opaque prompt proxy. | P2 |
| C | Skill / Capability Registry | **FOUNDATION ONLY** | Static pinned local registry exists; no publication/promotion/deprecation service. | [agentskills/agentskills](https://github.com/agentskills/agentskills)<br>[iflytek/skillhub](https://github.com/iflytek/skillhub)<br>[Observal/Observal](https://github.com/Observal/Observal) | Extend current data model with review states and immutable versions before any external installation. | P1 |
| D | Skill Discovery / Marketplace / Scout | **FOUNDATION ONLY** | Local sources can be discovered; no bounded external discovery/evaluation source adapters. | [cloudflare/agent-skills-discovery-rfc](https://github.com/cloudflare/agent-skills-discovery-rfc)<br>[modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry)<br>[NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | Make Slice 2 a read-only candidate admission and recommendation pipeline; no auto-install/execute. | P1 |
| E | Agent Runtime | **FOUNDATION ONLY** | Agents are advisory-only; no executable lifecycle, cancellation, budget, pause/resume or receipts. | [openai/openai-agents-python](https://github.com/openai/openai-agents-python)<br>[google/adk-python](https://github.com/google/adk-python)<br>[pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | Defer execution until registry, evaluation and checkpoints are proven; adapt contracts, not a full framework. | P4 |
| F | Multi-Agent Orchestration | **DEFERRED** | No supervisor/DAG/debate runtime by design. | [google/adk-python](https://github.com/google/adk-python)<br>[openai/openai-agents-python](https://github.com/openai/openai-agents-python)<br>[crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | Only bounded creator-reviewer/enhancer roles after single-agent lifecycle; no swarm. | P5 |
| G | Reviewer / Evaluation / Validation | **PARTIAL** | Deterministic artifact validation exists for supported host paths; no generic reviewer/eval registry or calibrated suites. | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo)<br>[confident-ai/deepeval](https://github.com/confident-ai/deepeval)<br>[NVIDIA/garak](https://github.com/NVIDIA/garak) | Build deterministic validator and evidence-receipt contracts, with promptfoo as dev-only regression support. | P2 |
| H | Self-Healing / Self-Correction | **MISSING** | No bounded diagnosis/repair/replan state machine beyond manual engineering loops. | [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)<br>[microsoft/RD-Agent](https://github.com/microsoft/RD-Agent)<br>[sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) | Add bounded retry/error taxonomy only after validation/checkpoint primitives; prohibit recursive self-improvement. | P4 |
| I | Sandbox / Security / Trust | **STRONG** | Strong fail-closed routing, hashes, allowlists and redaction; no external candidate static scan or isolated third-party runtime. | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector)<br>[stacklok/toolhive](https://github.com/stacklok/toolhive)<br>[snyk/agent-scan](https://github.com/snyk/agent-scan) | Add no-LLM static admission scanning and keep runtime execution out of Scout. | P1 |
| J | Observability / Governance | **PARTIAL** | Receipts/provenance exist; no standardized redacted traces, costs, health or replay UI. | [traceloop/openllmetry](https://github.com/traceloop/openllmetry)<br>[Observal/Observal](https://github.com/Observal/Observal)<br>[langfuse/langfuse](https://github.com/langfuse/langfuse) | Define opt-in redacted event envelopes and correlation IDs; avoid automatic prompt capture. | P2 |
| K | Workflow / DAG / Scheduling | **FOUNDATION ONLY** | Decision bridge exists, but no durable scheduler, dependency runtime or crash recovery. | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)<br>[dbos-inc/dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py)<br>[temporalio/temporal](https://github.com/temporalio/temporal) | Build a minimal internal state ledger rather than import an orchestration service. | P2 |
| L | Knowledge / Code Intelligence | **MISSING** | No language-aware repository graph, symbol/dependency index or impact analysis. | [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter)<br>[scip-code/scip](https://github.com/scip-code/scip)<br>[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)<br>[getzep/graphiti](https://github.com/getzep/graphiti) | Start with pinned local syntax/index protocols; benchmark turnkey CodeGraph in isolation later. | P3 |
| M | Skill Factory / Capability Generation | **DEFERRED** | Generation sources are audited but no generated capability can be promoted. | [sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill)<br>[alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)<br>[revfactory/harness](https://github.com/revfactory/harness) | Require quarantine, held-out evaluation, signed provenance and explicit human promotion before any generator. | P5 |
| N | MCP / Tool Discovery | **PARTIAL** | Local R2 MCP is stable; no external registry, gateway, dynamic lifecycle or compatibility evaluation. | [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry)<br>[modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector)<br>[stacklok/toolhive](https://github.com/stacklok/toolhive) | Read metadata only in Slice 2; do not start remote servers, OAuth or dynamic execution. | P1 |
| O | Harness / Operating Environment | **PARTIAL** | Codex/ChatGPT integration is proven; no cross-harness execution contract or portable checkpoint layer. | [openai/codex](https://github.com/openai/codex)<br>[google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)<br>[cline/cline](https://github.com/cline/cline)<br>[pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | Preserve host ownership; adapt capability negotiation/checkpoint patterns without bundling another harness. | P3 |
| P | Cross-Runtime Interoperability | **PARTIAL** | MCP and Agent Skills are used; A2A/ACP task/session protocols are not mapped. | [a2aproject/A2A](https://github.com/a2aproject/A2A)<br>[agentclientprotocol/agent-client-protocol](https://github.com/agentclientprotocol/agent-client-protocol)<br>[agentskills/agentskills](https://github.com/agentskills/agentskills) | Keep standards mapping data-only until an executable Agent Runtime exists. | P3 |
| Q | Planning / Reasoning Architecture | **STRONG** | V1.2 planner is bounded and proven; generic plan repair/reviewer contracts are partial. | [openai/openai-agents-python](https://github.com/openai/openai-agents-python)<br>[google/adk-python](https://github.com/google/adk-python)<br>[langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Preserve planner semantics; add validation and repair around it rather than replace it. | P2 |
| R | State / Checkpoint / Resume | **MISSING** | No durable resume across usage limits/process restarts and no replay/idempotency ledger. | [dbos-inc/dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py)<br>[langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)<br>[temporalio/temporal](https://github.com/temporalio/temporal)<br>[cline/cline](https://github.com/cline/cline) | Implement a versioned, append-only, local state/receipt ledger with idempotency and explicit resume tokens. | P2 |

## 4. Total repositories/projects discovered

The bounded search produced:

| Measure | Count |
|---|---:|
| Search queries | 55 |
| Unique repository candidates after case-insensitive deduplication | 265 |
| Serious candidates deeply evaluated | 69 |
| Serious candidates present in the 265-item query inventory | 68 |
| Manually verified adjacent promotion after an exact-name zero result | 1 (`open-multi-agent/oma-forge`) |
| Preserved accepted seed-source records | 13 |
| `INTEGRATE` dispositions | 6 |
| `ADAPT PATTERNS` dispositions | 17 |
| `REFERENCE ONLY` dispositions | 28 |
| `WATCH` dispositions | 8 |
| `REJECT` dispositions | 10 |

The full 265-project query inventory, search terms and domain signals, plus all 69 serious-candidate exact commits, releases, licenses, 20-dimension assessments, dispositions and decisions, are in [the machine-readable research registry](../research/nexus-ecosystem-gap-scan.json). Sixty-eight serious candidates are present in the query inventory. `open-multi-agent/oma-forge` was added through manual adjacent verification after the exact phrase `"Open Multi-Agent"` returned no repository result; it is not misrepresented as a query hit.

Exact-name verification prevented ambiguous labels from being promoted as sources:

| Search label | Result | Verified related candidates | Finding |
|---|---|---|---|
| Agent Registry | **AMBIGUOUS** | [awslabs/a2a-agent-registry-on-aws](https://github.com/awslabs/a2a-agent-registry-on-aws) | A generic label, not a canonical repository identity. |
| Open SSR | **NOT VERIFIED** | None | No trustworthy exact canonical Agent/Skill repository was found in the bounded search. |
| skills-registry | **AMBIGUOUS** | [opendatahub-io/skills-registry](https://github.com/opendatahub-io/skills-registry)<br>[iflytek/skillhub](https://github.com/iflytek/skillhub)<br>[Observal/Observal](https://github.com/Observal/Observal) | Multiple unrelated implementations; exact repository identity is mandatory. |
| skills-mcp | **AMBIGUOUS** | [snyk/agent-scan](https://github.com/snyk/agent-scan)<br>[NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | Search phrase mostly surfaced adjacent components, not a canonical project. |
| agent-discover | **AMBIGUOUS** | [cloudflare/agent-skills-discovery-rfc](https://github.com/cloudflare/agent-skills-discovery-rfc)<br>[sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) | No single authoritative repository with this exact identity. |
| Open Multi-Agent | **NOT VERIFIED AS EXACT NAME** | [open-multi-agent/oma-forge](https://github.com/open-multi-agent/oma-forge)<br>[THU-MAIC/OpenMAIC](https://github.com/THU-MAIC/OpenMAIC) | OMA Forge is an early project; OpenMAIC is a classroom app, not a general runtime. |

## 5. Serious candidates deeply evaluated

Every serious candidate was evaluated across the same 20 positively oriented dimensions:

1. gap fit;
2. architectural quality;
3. security model;
4. provenance quality;
5. license compatibility;
6. maintenance/activity;
7. runtime simplicity;
8. dependency lightness;
9. Windows compatibility;
10. offline/local compatibility;
11. MCP compatibility;
12. cross-runtime usefulness;
13. integration ease;
14. low duplication;
15. unique capability gain;
16. testability;
17. auditability;
18. failure isolation;
19. rollback feasibility;
20. long-term strategic value.

A score of 1 is unfavorable and 5 is strong. The score is a compact comparison aid, not an automatic disposition rule; security, licensing, fit and authority boundaries can override popularity or total score.

| Serious candidate | Exact commit | License | Domains | Disposition | Score | Nexus decision |
|---|---:|---|---|---|---:|---|
| [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | `5299c00aaf65` | MIT | A, B, L, M | **ADAPT PATTERNS** | 75/100 | Do not import the runtime or proxy. Adapt typed memory assets, ACL-scoped loadouts, bounded retrieval budgets, explicit provenance, human promotion, and versioned lifecycle states into a smaller Nexus-owned design. |
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | `0070e08e01d7` | Apache-2.0 | A, B | **ADAPT PATTERNS** | 82/100 | Adapt namespace, temporal ranking, and bounded single-pass retrieval patterns; do not depend on managed-only behavior or benchmark claims. |
| [getzep/graphiti](https://github.com/getzep/graphiti) | `683a8539c892` | Apache-2.0 | A, B | **ADAPT PATTERNS** | 81/100 | Adapt temporal validity intervals, source-edge provenance, contradiction-as-invalidation, and historical queries; avoid importing a graph database before scale evidence. |
| [letta-ai/letta](https://github.com/letta-ai/letta) | `4511fa0bc91f` | Apache-2.0 landing; active source letta-code Apache-2.0 | A, B, E, O | **REFERENCE ONLY** | 59/100 | Reference memory-block ergonomics and append-only history only. Do not permit agent self-modification or cloud-coupled identity. |
| [langchain-ai/langmem](https://github.com/langchain-ai/langmem) | `29cbe41e5852` | MIT | A, B | **ADAPT PATTERNS** | 83/100 | Adapt hot-path/background separation, explicit memory namespaces, and write receipts; keep Nexus storage and policy independent. |
| [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | `9119efe5554e` | Apache-2.0 | A, B, M | **WATCH** | 61/100 | Watch until architecture and local-only security contracts stabilize; consider cube isolation and correction receipts after a dedicated memory threat model. |
| [microsoft/graphrag](https://github.com/microsoft/graphrag) | `f40e9a26ce62` | MIT | B, L | **REFERENCE ONLY** | 57/100 | Reference the methodology only; the project explicitly reports maintenance mode and is too expensive for default Nexus context. |
| [run-llama/llama_index](https://github.com/run-llama/llama_index) | `246a9b7712eb` | MIT | A, B, L | **REFERENCE ONLY** | 56/100 | Do not introduce the framework; adapt narrow connector contracts only when a concrete Nexus source requires them. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | `bdb8a9c7a4aa` | MIT | B, E, K, Q, R | **ADAPT PATTERNS** | 83/100 | Adapt versioned state snapshots, transition guards, interrupt tokens, and resume idempotency into Nexus; do not adopt the runtime before an execution authority phase. |
| [continuedev/continue](https://github.com/continuedev/continue) | `5522c6f44ca0` | Apache-2.0 | B, O, Q, R | **REFERENCE ONLY** | 59/100 | Keep reference-only; Nexus already has a narrower Host/MCP contract and should not embed an editor harness. |
| [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry) | `6036804f1c62` | Apache-2.0/MIT transition; documentation CC-BY-4.0 | C, D, N | **INTEGRATE** | 90/100 | Add only a bounded read-only candidate-source adapter in a future Scout slice; pin returned package/version metadata, enrich with security evidence, never auto-install or execute. |
| [docker/mcp-registry](https://github.com/docker/mcp-registry) | `8c773729f13f` | MIT | C, D, I, N | **REFERENCE ONLY** | 58/100 | Do not make Docker a Nexus prerequisite; consume only provenance concepts or optional metadata later. |
| [iflytek/skillhub](https://github.com/iflytek/skillhub) | `2e78f79e836c` | Apache-2.0 | C, D, J | **ADAPT PATTERNS** | 77/100 | Adapt lifecycle/status, version-diff, review, and audit schemas. Do not import the enterprise stack or installer. |
| [Observal/Observal](https://github.com/Observal/Observal) | `c26b29529121` | Apache-2.0 | C, D, J, O | **ADAPT PATTERNS** | 76/100 | Adapt evidence-led promotion, component version diffs and opt-in trace receipts; do not adopt automatic telemetry or installers. |
| [cloudflare/agent-skills-discovery-rfc](https://github.com/cloudflare/agent-skills-discovery-rfc) | `1bd1167983fa` | Apache-2.0 | C, D, M | **INTEGRATE** | 88/100 | Implement a bounded read-only discovery adapter after architecture approval; require allowlisted origins, exact digest, safe extraction, no scripts, no automatic installation/execution. |
| [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | `16cf2c354ef3` | Apache-2.0 | D, I, M | **INTEGRATE** | 89/100 | Pilot as a pinned, isolated, no-network/no-LLM, non-authoritative admission signal after license/SBOM verification; Nexus policy remains the final gate. |
| [snyk/agent-scan](https://github.com/snyk/agent-scan) | `68eea852fb7f` | Apache-2.0 | D, I, N | **WATCH** | 63/100 | Watch and adapt issue taxonomy only. Do not run on private Nexus content until a no-execution/no-egress mode is independently proven. |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | `69ef37e9424c` | Apache-2.0 | C, D, M, P | **INTEGRATE** | 92/100 | Validate and normalize supported fields directly, preserving Nexus provenance, hash, trust, and host eligibility as independent controls. |
| [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) | `db3357aef880` | Apache-2.0 | C, E, I, J, N, P | **REFERENCE ONLY** | 57/100 | Do not integrate; Nexus R2 intentionally remains local/read-plan-only and remote/federated gateway work is deferred. |
| [stacklok/toolhive](https://github.com/stacklok/toolhive) | `8fa9220de1ca` | Apache-2.0 | C, I, J, N | **ADAPT PATTERNS** | 77/100 | Adapt permission manifests, provenance signatures, per-request policy and audit receipts. Do not import runtime or start servers from discovery. |
| [docker/mcp-gateway](https://github.com/docker/mcp-gateway) | `a21c0ac1c1e7` | MIT | C, D, I, N | **REFERENCE ONLY** | 58/100 | Keep reference-only; no Docker, OAuth or dynamic server execution prerequisite for Nexus. |
| [archestra-ai/archestra](https://github.com/archestra-ai/archestra) | `5676c73127f3` | AGPL-3.0-only default; enterprise-marked regions proprietary | C, E, I, J, N | **REJECT** | 42/100 | Reject direct use and code adaptation; use permissively licensed primary sources for equivalent patterns. |
| [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | `edf54f5dec5f` | UNRESOLVED (no root license file found) | G, I, N | **REFERENCE ONLY** | 61/100 | Reference its conformance matrix; do not vendor or require it until license and sandboxed invocation are resolved. |
| [awslabs/a2a-agent-registry-on-aws](https://github.com/awslabs/a2a-agent-registry-on-aws) | `77405f7d77f3` | Apache-2.0 | C, D, P | **REFERENCE ONLY** | 56/100 | Do not integrate; A2A is deferred and a local metadata registry should not depend on AWS. |
| [opendatahub-io/skills-registry](https://github.com/opendatahub-io/skills-registry) | `948ef7bb32ef` | Apache-2.0 | C, D, P | **WATCH** | 66/100 | Watch only; no direct installer or symlink behavior. Re-evaluate if it adopts pinned, reviewed, fail-closed admission. |
| [open-multi-agent/oma-forge](https://github.com/open-multi-agent/oma-forge) | `96ab97ceb1a6` | Apache-2.0 | E, F, P | **WATCH** | 57/100 | Watch only; do not run or import. Require protocol stability, sandboxing, and execution receipts before reconsideration. |
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | `10cdae4a3c30` | MIT | E, F, G, J, P, Q | **ADAPT PATTERNS** | 84/100 | Adapt typed handoff/guardrail/receipt boundaries after Nexus authorizes Agent Runtime; do not add SDK runtime in Slice 2. |
| [microsoft/autogen](https://github.com/microsoft/autogen) | `027ecf0a379b` | CC-BY-4.0 at reviewed root | E, F, N, P | **REJECT** | 37/100 | Reject direct dependency; use successor/standards documentation if a future review is approved. |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | `fcdeb3d98d85` | MIT | E, F, J, Q | **REFERENCE ONLY** | 58/100 | Do not import; it duplicates future Nexus runtime responsibilities and offers less precise authority separation than needed. |
| [google/adk-python](https://github.com/google/adk-python) | `0dbc37d67e92` | Apache-2.0 | E, F, G, K, P, Q, R | **ADAPT PATTERNS** | 85/100 | Adapt workflow/agent separation, confirmation tokens and bounded graph transition schemas; no runtime dependency yet. |
| [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | `2dbcf1dff61b` | MIT | B, E, G, O, P, Q, R | **ADAPT PATTERNS** | 84/100 | Adapt schema-first tool/result validation, dependency injection and explicit capability composition. Do not import shell/subagent authority. |
| [agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope) | `9983e76d1ee7` | Apache-2.0 | B, C, D, E, F, I, J, N, O, R | **ADAPT PATTERNS** | 78/100 | Adapt event envelopes, permission decisions and capability-limited workspace contracts only; do not import the full rapidly expanding runtime. |
| [camel-ai/camel](https://github.com/camel-ai/camel) | `e88b5eebe9f8` | Apache-2.0 | E, F, A, Q | **REFERENCE ONLY** | 58/100 | Keep reference-only; do not use swarm scale as a Nexus design goal. |
| [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT) | `11cdf466d042` | MIT | E, F, Q | **REFERENCE ONLY** | 57/100 | Do not integrate; adapt only the idea that role outputs are typed artifacts subject to review. |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | `1a7130ce9633` | MIT | E, F, I, O, Q, R | **REFERENCE ONLY** | 56/100 | Do not integrate; Nexus must remain a capability router rather than another coding-agent platform. |
| [THU-MAIC/OpenMAIC](https://github.com/THU-MAIC/OpenMAIC) | `97ceb11a145b` | MIT | F | **REJECT** | 40/100 | Reject for Nexus architecture; it is a vertical application, not a reusable bounded runtime. |
| [confident-ai/deepeval](https://github.com/confident-ai/deepeval) | `eb61968725bb` | Apache-2.0 | G, J, Q | **REFERENCE ONLY** | 63/100 | Use deterministic Nexus validators first; consider a separately approved optional judge adapter only after calibration. |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | `e3b36451f4a2` | MIT | G, I, J | **INTEGRATE** | 88/100 | Pilot as a pinned dev/test tool using synthetic fixtures and no live billable providers by default; never put it in Nexus runtime. |
| [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | `5e7136cf3538` | Elastic License 2.0 | G, J | **REFERENCE ONLY** | 56/100 | Do not integrate or redistribute; adapt redacted trace schemas and dataset versioning from permissive standards. |
| [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | `298b68274234` | Apache-2.0 | G | **REFERENCE ONLY** | 58/100 | Keep reference-only until Nexus has a retrieval runtime and calibrated datasets. |
| [microsoft/AgentAsJudge](https://github.com/microsoft/AgentAsJudge) | `6ff9c5ad7cc4` | MIT | G, F | **REJECT** | 39/100 | Reject; low adoption, narrow text scoring and nondeterministic multi-agent judging do not justify risk. |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | `105154b20a57` | MIT core; enterprise directories separately licensed | G, J | **REFERENCE ONLY** | 58/100 | Do not import the platform; adapt minimal redacted event/receipt schema and opt-in dataset promotion. |
| [traceloop/openllmetry](https://github.com/traceloop/openllmetry) | `62e24c2ffde6` | Apache-2.0 | J, P | **ADAPT PATTERNS** | 85/100 | Adapt stable event/span naming and trace correlation IDs; keep collection opt-in, local, redacted and independent from execution authority. |
| [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | `3ea751c087f3` | MIT | H, O, Q | **REFERENCE ONLY** | 56/100 | Do not integrate the superseded harness; adapt bounded reproduce-fix-regression states. |
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | `6762f84f9bc0` | MIT | H, K, Q | **REFERENCE ONLY** | 55/100 | Adapt bounded diagnosis/repair/validation state transitions only. |
| [NVIDIA/garak](https://github.com/NVIDIA/garak) | `8ed1543b985a` | Apache-2.0 | G, I | **REFERENCE ONLY** | 68/100 | Keep optional reference until Nexus has an approved model endpoint and synthetic red-team budget; do not add live calls by default. |
| [protectai/llm-guard](https://github.com/protectai/llm-guard) | `168c1034ffdb` | MIT | I | **REJECT** | 37/100 | Reject direct use due archived status. |
| [temporalio/temporal](https://github.com/temporalio/temporal) | `38948f8a271e` | MIT | E, K, R | **REFERENCE ONLY** | 63/100 | Reference event history, deterministic workflow/activity separation and idempotency tokens; do not add the server. |
| [dbos-inc/dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py) | `9c219ad5fdd3` | MIT | K, R | **ADAPT PATTERNS** | 83/100 | Adapt step receipts, idempotency keys and resume-from-last-validated-step; avoid mandatory Postgres until scale requires it. |
| [restatedev/restate](https://github.com/restatedev/restate) | `e812a2907f10` | Business Source License 1.1 | E, K, R | **REJECT** | 46/100 | Reject direct dependency; use permissive sources for equivalent state-machine patterns. |
| [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | `38041e65c47f` | Apache-2.0 | K, J, R | **REFERENCE ONLY** | 59/100 | Do not integrate; Nexus needs a smaller state ledger rather than a data orchestrator. |
| [dagster-io/dagster](https://github.com/dagster-io/dagster) | `37e82c69b441` | Apache-2.0 | K, J | **REJECT** | 44/100 | Reject for Nexus; use smaller workflow patterns from DBOS/LangGraph. |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet) | `ad0bd039453b` | MIT | E, K, J, R | **REFERENCE ONLY** | 59/100 | Keep reference-only; too large for local Nexus checkpointing. |
| [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter) | `664e9a678667` | MIT | L, I | **INTEGRATE** | 92/100 | Pilot a narrow pinned parser layer for allowlisted languages after architecture approval; no semantic execution or automatic code indexing. |
| [github/stack-graphs](https://github.com/github/stack-graphs) | `fcb7705d5b38` | Apache-2.0 | L | **REJECT** | 45/100 | Reject direct use due archived status; cite as historical reference only. |
| [scip-code/scip](https://github.com/scip-code/scip) | `a7b9c65a8aa1` | Apache-2.0 | L, P | **ADAPT PATTERNS** | 84/100 | Adapt stable symbol identity, index version/hash and producer provenance; avoid requiring all external indexers initially. |
| [codefuse-ai/CodeFuse-Query](https://github.com/codefuse-ai/CodeFuse-Query) | `bccce36f3b8b` | Apache-2.0 | L | **WATCH** | 59/100 | Watch until maintenance, Windows packaging and index provenance are clearer. |
| [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | `6a056ec5db35` | MIT | B, L, O | **WATCH** | 72/100 | Watch and benchmark in an isolated repository later; require pinned binaries, SBOM, no auto-update, bounded index and deterministic provenance before integration. |
| [sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) | `36f6f0495229` | Apache-2.0 | M, G, H, O | **WATCH** | 69/100 | Watch until Nexus has quarantine, deterministic validators, isolated execution and explicit human promotion. Never auto-install generated output. |
| [a2aproject/A2A](https://github.com/a2aproject/A2A) | `5e233e57fd37` | Apache-2.0 | C, E, F, P, R | **REFERENCE ONLY** | 69/100 | Keep reference-only until Nexus has a bounded Agent Runtime; later map Nexus task/receipt states to A2A without exposing hidden context. |
| [ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) | `90c0528532f0` | MIT | J, P, R | **REFERENCE ONLY** | 61/100 | Do not integrate in the local Desktop phase; adapt only redacted event semantics if Nexus gains a separate UI. |
| [agentclientprotocol/agent-client-protocol](https://github.com/agentclientprotocol/agent-client-protocol) | `e54cfc5bbebf` | Apache-2.0 | E, O, P, R | **ADAPT PATTERNS** | 87/100 | Adapt version/capability negotiation and schema artifact pinning; do not treat negotiated capability as authorization. |
| [agi-inc/agent-protocol](https://github.com/agi-inc/agent-protocol) | `5047199152dc` | MIT | E, P | **REJECT** | 36/100 | Reject due lower activity and protocol redundancy. |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | `cad6304e85e2` | All rights reserved; Anthropic Commercial Terms | B, E, I, O, Q, R | **REFERENCE ONLY** | 57/100 | Do not vendor, redistribute or depend on source; rely on public specifications and approved compatibility tests. |
| [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | `3c311beac2e7` | Apache-2.0 | B, E, I, N, O, Q, R | **REFERENCE ONLY** | 66/100 | Keep reference-only; adapt checkpoint and context precedence tests, not the runtime. |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | `6568a8245532` | MIT | E, F, I, O, Q | **REFERENCE ONLY** | 63/100 | Do not import; Nexus already separates read-only planning from Host execution. |
| [cline/cline](https://github.com/cline/cline) | `1d5d3b005575` | Apache-2.0 | B, E, F, I, J, O, Q, R | **ADAPT PATTERNS** | 83/100 | Adapt approval receipts, reversible action boundaries and plan/act mode invariants only. Do not import runtime, schedules or auto-approve. |
| [RooCodeInc/Roo-Code](https://github.com/RooCodeInc/Roo-Code) | `b867ec914575` | Apache-2.0 | E, F, O | **REJECT** | 37/100 | Reject direct use due archived status. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | `d8409a4b0813` | MIT | B, C, D, E, F, G, H, I, J, M, O, Q, R | **WATCH** | 64/100 | Keep CANDIDATE_SOURCE/WATCH. Review components individually; never install the whole bundle or grant agents/hooks automatic authority. |

## 6. TencentDB-Agent-Memory deep evaluation

**Candidate:** [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)
**Pinned commit:** `5299c00aaf65481703c180fd69df066d11254eb7`
**Reviewed release:** `v2.0.1`
**License:** MIT, verified from the root `LICENSE`; GitHub metadata reported `NOASSERTION`.
**Disposition:** **ADAPT PATTERNS**; reject the runtime/proxy as a Nexus dependency.

### Architecture

The repository combines four governed asset types:

- **Chat Memory** with L0-L3 representations;
- **Skill** assets extracted from successful experience;
- **LLM-Wiki** document knowledge;
- **CodeGraph** repository knowledge.

Its strongest design is not merely retrieval. It is a team memory hub with:

- owner/team/restricted/agent ACLs;
- explicit loadouts that bind assets to agents;
- human review and management;
- hybrid BM25, vector and graph retrieval;
- reciprocal-rank fusion;
- character/count/timeout budgets;
- incremental and asynchronous extraction;
- framework-portable asset identities;
- migration/version tooling.

### Runtime and dependency assumptions

The reviewed deployment expects Node.js 22.16 or newer, Docker Compose, several local services/ports, two sets of model parameters, and optional SQLite, Tencent Cloud VectorDB, MongoDB or related backends. Its proxy uses PTY/protocol interception and injects selected memory into agent traffic. OpenTelemetry and a management/control plane are also present.

### Security and governance

Positive evidence:

- typed memory assets rather than one undifferentiated vector store;
- explicit ACLs and team roles;
- user-visible management/review;
- retrieval budgets;
- asset/source separation;
- migration tooling.

Blocking evidence:

- no dedicated repository `SECURITY.md` was found at the reviewed commit;
- the prompt/protocol proxy becomes an injection and credential boundary;
- automatic asset/Skill extraction needs a promotion policy Nexus does not yet have;
- fast v2 beta evolution and a feature branch as default increase change risk;
- the deployment is substantially larger than the current local Nexus boundary.

### Nexus decision

Nexus should implement a smaller internal memory design inspired by:

1. typed memory assets;
2. temporal/source provenance;
3. namespace/ACL-scoped loadouts;
4. explicit user promotion;
5. bounded retrieval budgets;
6. versioned lifecycle states;
7. inspect/delete/forget controls.

Nexus should **not** import the proxy, multi-service runtime, automatic Skill promotion, credentials, or databases as a default dependency.

## 7. Memory-system comparison

| Best of class | TencentCloud/TencentDB-Agent-Memory (governed team assets)<br>getzep/graphiti (temporal provenance)<br>mem0ai/mem0 (compact retrieval) |
| Complementary | langchain-ai/langmem (hot/background memory) |
| Redundant | run-llama/llama_index (broad retrieval framework) |
| Unsuitable | letta-ai/letta runtime self-modification<br>MemOS automatic skill evolution |
| Nexus decision | Nexus-owned hybrid: typed assets + temporal provenance + bounded retrieval; no imported proxy/runtime. |

| System | Best capability | Principal weakness for Nexus | Disposition |
|---|---|---|---|
| TencentDB-Agent-Memory | Governed team assets and loadouts | Proxy/multi-service authority and high operational weight | ADAPT PATTERNS |
| Graphiti | Temporal truth, contradiction history and provenance | Graph database and provider dependency | ADAPT PATTERNS |
| Mem0 | Compact multi-signal retrieval | Managed/OSS behavior gap and provider dependence | ADAPT PATTERNS |
| LangMem | Hot-path vs background consolidation | Agent-authorized writes and LangGraph/store dependencies | ADAPT PATTERNS |
| MemOS | Memory cubes, correction and local modes | Self-evolving Skills and broad cloud/local stack | WATCH |
| Letta Code | Editable memory blocks and Git history | Agent self-modification and cloud identity | REFERENCE ONLY |
| GraphRAG | Graph context for large corpora | Maintenance mode and expensive indexing | REFERENCE ONLY |

**Recommended memory model:** a Nexus-owned local ledger, not a generic vector database. Begin with explicit scoped facts/events and source hashes; add temporal edges and retrieval only after deletion, conflict, retention and permission semantics are testable.

## 8. Registry/discovery comparison

| Best of class | agentskills/agentskills (format)<br>cloudflare/agent-skills-discovery-rfc (Skill discovery)<br>modelcontextprotocol/registry (MCP metadata) |
| Complementary | NVIDIA/SkillSpector (security signal)<br>iflytek/skillhub (lifecycle patterns)<br>Observal/Observal (usage evidence) |
| Redundant | docker/mcp-registry for mandatory local use<br>multiple ambiguous skills-registry projects |
| Unsuitable | opendatahub installer/symlink behavior<br>Open SSR exact name unverified |
| Nexus decision | Build a small Nexus aggregator/admission layer; official/standard sources feed candidates, never authority. |

The official MCP Registry is a metadata source, not a trust verdict. Its documentation explicitly states that downstream aggregators should add curation and security scanning. The Cloudflare Skill discovery RFC adds artifact digests and safe-archive guidance, but origin integrity is not equivalent to code safety. Agent Skills defines the package format, not authority.

The recommended Nexus control plane separates:

`source discovery → canonical identity → immutable pin → license → static scan → duplicate analysis → human/policy review → candidate recommendation`

from:

`installation → Host mapping → current-turn eligibility → execution`

The first path is a suitable Slice 2 target. The second remains forbidden.

## 9. Agent Runtime comparison

| Best of class | openai/openai-agents-python (handoffs/guardrails)<br>google/adk-python (workflow/confirmation)<br>pydantic/pydantic-ai (typed contracts) |
| Complementary | agentscope-ai/agentscope permission/event patterns |
| Redundant | crewAIInc/crewAI<br>camel-ai/camel<br>MetaGPT |
| Unsuitable | microsoft/autogen superseded<br>OpenMAIC vertical app |
| Nexus decision | Adapt small contracts only; no runtime import before admission/evaluation/checkpoint prerequisites. |

OpenAI Agents provides the strongest official handoff/guardrail/session vocabulary. Google ADK provides useful Agent-versus-Workflow separation and tool confirmation. Pydantic AI provides the strongest type-driven tool/result validation. AgentScope offers broad permission, event and workspace abstractions but is too expansive to adopt wholesale.

Nexus should not replace its frozen planner with any of these frameworks. A future runtime should implement only the minimal lifecycle contract needed by Nexus:

`created → eligible → approved → started → paused/cancelled → succeeded/failed → validated → reported`

Each transition must be versioned, receipt-backed and incapable of manufacturing Host authority.

## 10. Multi-Agent comparison

| Best of class | google/adk-python bounded graphs<br>openai/openai-agents-python handoffs |
| Complementary | Edict governance evidence from frozen seed audit |
| Redundant | CrewAI role crews<br>MetaGPT software-company roles |
| Unsuitable | unbounded CAMEL scale<br>early OMA Forge subprocess model |
| Nexus decision | Future bounded creator-reviewer/enhancer DAG, not swarm/debate by default. |

The scan found no evidence that an open-ended swarm would improve Nexus. Role counts, debate and voting do not substitute for validation. The first justified multi-Agent shape is a fixed, bounded graph:

`Creator → deterministic validator → optional Reviewer → optional Enhancer → validator`

with explicit maximum fan-out, time/token budget, no recursive delegation, no shared hidden reasoning and no automatic consensus.

## 11. Reviewer/Evaluation comparison

| Best of class | promptfoo/promptfoo development regression<br>traceloop/openllmetry event semantics |
| Complementary | deepeval metric ideas<br>garak red-team taxonomy<br>Observal evidence loops |
| Redundant | Langfuse and Phoenix full platforms |
| Unsuitable | AgentAsJudge low-evidence multi-judge<br>llm-guard archived |
| Nexus decision | Deterministic validators first; calibrated judge tests optional; redacted local traces only. |

Deterministic validation remains primary. Promptfoo is the only direct integration recommendation in this group, and only as a pinned development/test tool with synthetic fixtures and no default live provider calls. DeepEval/Ragas contribute metric ideas. Garak contributes adversarial taxonomies. LLM judges must be versioned, calibrated and supplemental; they must never alone assert artifact success, security or execution.

## 12. Self-Healing comparison

No reviewed project justifies autonomous recursive self-improvement.

| Candidate | Useful pattern | Unsafe/unsuitable behavior | Decision |
|---|---|---|---|
| SWE-agent | Reproduce → change → test trajectory | Full repository/shell authority; superseded by mini-SWE-agent | REFERENCE ONLY |
| RD-Agent | Hypothesis → experiment → feedback | Linux/data-model R&D runtime and broad execution | REFERENCE ONLY |
| EvoSkill | Held-out evaluation of generated Skill variants | Generated instructions/scripts and harness installers | WATCH |
| Letta Code | Git-backed self-edit history | Rewrites memory, Skills, prompts and harness | REFERENCE ONLY |

Nexus should first implement a bounded failure taxonomy:

`diagnose → propose one repair → policy check → apply under existing authority → regression → rollback or accept`

Retry counts, changed files, tool calls and budgets must be bounded. Failure must never grant broader authority.

## 13. Security/Sandbox comparison

| Best of class | stacklok/toolhive security model<br>official MCP registry metadata |
| Complementary | MCP Inspector conformance tests |
| Redundant | IBM ContextForge, Docker Gateway and Archestra for current local-only scope |
| Unsuitable | Remote MCP/OAuth in current phase |
| Nexus decision | Preserve R2 read/plan-only boundary; adopt metadata and policy patterns, not gateways. |

| Candidate | Security strength | Limitation | Decision |
|---|---|---|---|
| NVIDIA SkillSpector | Dedicated Skill static analysis, no-LLM mode, injection/exfiltration/taint/YARA categories | Scanner is evidence, not proof | INTEGRATE as future isolated admission signal |
| Snyk Agent Scan | Cross-harness discovery and issue taxonomy | Can start MCP servers and send data to an API | WATCH |
| ToolHive | Container isolation, permission files, identity, signing and audit | Docker/Podman/Kubernetes and third-party execution | ADAPT PATTERNS |
| Docker MCP Gateway | Containers, secrets and catalog separation | Docker Desktop, OAuth and dynamic servers | REFERENCE ONLY |
| Archestra | Broad enterprise guardrails | AGPL/enterprise mixed license and central authority | REJECT |
| LLM Guard | Input/output scanners | Archived | REJECT |

The fail-closed rule is unchanged: a clean scanner result can add evidence, but cannot promote, install, map or execute a capability.

## 14. Observability/Governance comparison

A minimal Nexus observability layer should use:

- opaque correlation IDs;
- versioned state-transition events;
- candidate/Skill/Agent identity and content hash;
- permission/eligibility decision codes;
- bounded timing/token/cost counters;
- artifact/validation receipts;
- redaction applied before persistence;
- opt-in trace retention.

It must exclude raw Skill bodies, hidden reasoning, project rules, credentials, absolute private paths and arbitrary prompt/output capture.

Edict's existing frozen audit remains the governance reference for authority separation. OpenLLMetry contributes cross-runtime event semantics. Observal contributes evidence-to-registry feedback and replay concepts. Langfuse/Phoenix are reference-only because of platform weight, trace privacy and licensing.

## 15. Workflow/DAG comparison

| Best of class | langchain-ai/langgraph state/interrupt model<br>dbos-inc/dbos-transact-py step/idempotency model |
| Complementary | Temporal deterministic history as reference<br>Cline revert/checkpoint UX |
| Redundant | Prefect/Hatchet generic orchestration services |
| Unsuitable | Dagster data-asset focus<br>Restate BSL service |
| Nexus decision | Nexus-owned append-only local ledger; no orchestration server. |

General workflow engines solve reliability at a much larger operational scale than Nexus currently needs. The recommended design is an internal append-only event ledger with idempotent activities, not Temporal, Prefect, Hatchet, Dagster or Restate as a dependency.

LangGraph and DBOS supply the most transferable patterns:

- snapshot before interrupt;
- immutable step identity;
- versioned state schema;
- idempotency key for each side effect;
- resume only from a validated transition;
- activity outputs stored by hash/reference;
- explicit expiry/replay protection;
- compensating rollback record.

## 16. Knowledge/CodeGraph comparison

| Best of class | tree-sitter/tree-sitter syntax foundation<br>scip-code/scip semantic index protocol |
| Complementary | colbymchenry/codegraph isolated benchmark<br>Graphiti temporal graph model |
| Redundant | Tencent bundled CodeGraph as a reason to reuse its whole runtime |
| Unsuitable | stack-graphs archived<br>CodeFuse-Query uncertain activity/Windows |
| Nexus decision | Layer syntax -> versioned semantic index -> optional graph, each with producer hash/provenance. |

TencentDB-Agent-Memory's Wiki/CodeGraph integration is valuable as a combined user experience, but specialized sources are stronger foundations:

- Tree-sitter for local syntax;
- SCIP for language-neutral symbol/index interchange;
- Graphiti for temporal provenance;
- CodeGraph as a future isolated turnkey benchmark.

Nexus should not begin with embeddings or a vector database. A staged code-intelligence layer should be:

`pinned parser → file/content hash → symbol index → dependency edges → impact query → optional semantic/graph enrichment`

Every derived index must identify its producer version, grammar/indexer hash, input tree hash and freshness state.

## 17. Skill Factory comparison

| Best of class | sentient-agi/EvoSkill held-out evolution |
| Complementary | Nuwa and RevFactory patterns from frozen seed audit |
| Redundant | multiple persona/skill generators without evaluation |
| Unsuitable | automatic promotion or agent self-modification |
| Nexus decision | Quarantine + held-out tests + security scan + explicit human promotion; generation never grants trust. |

Nuwa and RevFactory remain authoritative from the existing seed audit. EvoSkill adds a stronger held-out evaluation model, but it still generates untrusted code/instructions. A future Skill Factory needs:

1. isolated generation;
2. provenance to source trajectories;
3. license analysis;
4. static security scan;
5. deterministic schema tests;
6. held-out task evaluation;
7. duplicate/conflict analysis;
8. quarantine;
9. independent review;
10. explicit human promotion.

A generated capability never inherits the trust of the generator, benchmark or model.

## 18. MCP/tool-discovery comparison

The official MCP Registry should be integrated only as a read-only candidate metadata source. It authenticates namespace ownership but does not attest server code safety. ToolHive/Docker/IBM/Archestra provide gateway or lifecycle runtimes that conflict with the accepted local, read/plan-only R2 boundary.

MCP discovery in Nexus must never:

- start a candidate server;
- execute an installation command;
- resolve `latest`;
- read credentials;
- enable OAuth;
- expose Host-private state;
- turn catalog metadata into a Host mapping.

A separately approved compatibility probe may later validate an already quarantined package in an isolated environment.

## 19. Harness comparison

| Best of class | OpenAI Codex frozen official audit<br>Cline approval/checkpoint patterns<br>Gemini CLI checkpoint/context patterns |
| Complementary | Pydantic AI harness typed capabilities |
| Redundant | OpenCode full agent<br>OpenHands platform |
| Unsuitable | Claude Code source redistribution<br>Roo Code archived<br>ECC whole-bundle install |
| Nexus decision | Host remains executor; Nexus stays router/handoff. Cross-harness support is protocol mapping, not bundling. |

The existing OpenAI Codex, DeepSeek Harness and RevFactory audits remain authoritative. New useful evidence:

- Gemini CLI demonstrates explicit context files and checkpoint/resume UX.
- Cline demonstrates visible Plan/Act separation, approval and reversible checkpoints.
- Pydantic AI Harness demonstrates typed capability composition.
- OpenCode demonstrates read-only and execution-capable agents.
- OpenHands demonstrates workspace/event API separation.

Nexus should not bundle or imitate another harness. It should remain host-mediated and adapt portable contracts only.

## 20. Cross-runtime interoperability findings

| Best of class | Agent Skills format<br>MCP for tools<br>A2A for agent-to-agent<br>ACP for editor-agent |
| Complementary | AG-UI for future UI events |
| Redundant | generic Agent Protocol |
| Unsuitable | Treating any advertised capability as authorization |
| Nexus decision | Map protocols through versioned adapters; keep trust, permissions and Host eligibility Nexus-owned. |

Official/open standards solve different layers:

| Layer | Standard/source | Meaning for Nexus |
|---|---|---|
| Skill package | Agent Skills | Portable instructions/resources; not trust or execution authority |
| Tool/resource connection | MCP | Host-to-tool protocol; not Agent delegation |
| Public MCP metadata | MCP Registry | Discovery metadata; not code safety |
| Agent-to-agent | A2A | Opaque Agent Cards/tasks/artifacts; deferred until Agent Runtime |
| Editor-to-coding-agent | ACP | Version/capability negotiation; capability is not authorization |
| Agent-to-UI | AG-UI | Event streaming; future UI-only reference |
| OpenAI plugin | OpenAI Plugins | Reusable Skills plus MCP capabilities under host ownership |

Adapters must preserve separate version, trust, permission, current-turn Host evidence and execution states.

## 21. Checkpoint/resume findings

Usage-limit and process interruptions are a proven Nexus development/runtime concern. The highest-value transferable patterns are:

- LangGraph: explicit state snapshots and interrupts;
- DBOS: durable step records and resume from the last completed step;
- Temporal: deterministic event history and workflow/activity separation;
- Cline/Gemini CLI: user-facing checkpoint and resume UX;
- ACP: protocol version/capability negotiation.

A minimal Nexus checkpoint record should contain:

- task and plan versions;
- previous/new state;
- input/output hashes;
- side-effect idempotency key;
- capability and Skill identity/hash;
- approval/eligibility result;
- artifact reference/hash;
- validator result;
- expiry and replay status;
- redacted failure code.

It must not persist hidden reasoning, raw Skill instructions, project rules, secrets or unredacted paths.

## 22. Nexus capability gap map

The most important architectural finding is that Nexus is strongest at bounded planning, provenance and Host-mediated presentation execution, but weakest at external candidate admission, generic evaluation, durable state and scoped memory.

The dependency order is therefore:

`candidate admission/security → generic validation/receipts → durable checkpoint/resume → context/memory → executable Agent lifecycle → bounded multi-Agent`

This order prevents a future Agent Runtime or Skill Factory from operating on untrusted, unvalidated or non-resumable state.

## 23. INTEGRATE candidates

These are recommendations for future narrow integrations, not current changes.

| Candidate | Domains | Unique value | Narrow approved shape |
|---|---|---|---|
| [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry) | C, D, N | Authoritative public MCP metadata source and interoperable subregistry schema. | Add only a bounded read-only candidate-source adapter in a future Scout slice; pin returned package/version metadata, enrich with security evidence, never auto-install or execute. |
| [cloudflare/agent-skills-discovery-rfc](https://github.com/cloudflare/agent-skills-discovery-rfc) | C, D, M | Smallest standards-oriented Skill discovery surface with content integrity. | Implement a bounded read-only discovery adapter after architecture approval; require allowlisted origins, exact digest, safe extraction, no scripts, no automatic installation/execution. |
| [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | D, I, M | Most directly relevant dedicated Skill security scanner reviewed. | Pilot as a pinned, isolated, no-network/no-LLM, non-authoritative admission signal after license/SBOM verification; Nexus policy remains the final gate. |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | C, D, M, P | Canonical cross-harness Skill format vocabulary. | Validate and normalize supported fields directly, preserving Nexus provenance, hash, trust, and host eligibility as independent controls. |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | G, I, J | High-value development-only regression and red-team harness without production execution authority. | Pilot as a pinned dev/test tool using synthetic fixtures and no live billable providers by default; never put it in Nexus runtime. |
| [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter) | L, I | Best low-level local syntax foundation without an agent runtime or vector database. | Pilot a narrow pinned parser layer for allowlisted languages after architecture approval; no semantic execution or automatic code indexing. |

No full runtime framework is in this category.

## 24. ADAPT PATTERNS candidates

| Candidate | Domains | Unique value | Pattern to adapt |
|---|---|---|---|
| [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | A, B, L, M | Strongest integrated blueprint for typed team memory assets, bounded layered retrieval, portable loadouts, and human-governed promotion. | Do not import the runtime or proxy. Adapt typed memory assets, ACL-scoped loadouts, bounded retrieval budgets, explicit provenance, human promotion, and versioned lifecycle states into a smaller Nexus-owned design. |
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | A, B | Practical compact memory API and multi-signal retrieval baseline. | Adapt namespace, temporal ranking, and bounded single-pass retrieval patterns; do not depend on managed-only behavior or benchmark claims. |
| [getzep/graphiti](https://github.com/getzep/graphiti) | A, B | Best temporal/provenance model among reviewed memory candidates. | Adapt temporal validity intervals, source-edge provenance, contradiction-as-invalidation, and historical queries; avoid importing a graph database before scale evidence. |
| [langchain-ai/langmem](https://github.com/langchain-ai/langmem) | A, B | Clean separation between immediate user-controlled memory writes and asynchronous consolidation. | Adapt hot-path/background separation, explicit memory namespaces, and write receipts; keep Nexus storage and policy independent. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | B, E, K, Q, R | Best reviewed conceptual source for state snapshots, interrupts, and deterministic transition boundaries. | Adapt versioned state snapshots, transition guards, interrupt tokens, and resume idempotency into Nexus; do not adopt the runtime before an execution authority phase. |
| [iflytek/skillhub](https://github.com/iflytek/skillhub) | C, D, J | Strong registry lifecycle model for draft/beta/stable, review, quarantine and deprecation. | Adapt lifecycle/status, version-diff, review, and audit schemas. Do not import the enterprise stack or installer. |
| [Observal/Observal](https://github.com/Observal/Observal) | C, D, J, O | Best combined model for registry evidence, version diffs, usage reports and replayable traces. | Adapt evidence-led promotion, component version diffs and opt-in trace receipts; do not adopt automatic telemetry or installers. |
| [stacklok/toolhive](https://github.com/stacklok/toolhive) | C, I, J, N | Strongest reviewed MCP isolation/provenance operating model. | Adapt permission manifests, provenance signatures, per-request policy and audit receipts. Do not import runtime or start servers from discovery. |
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | E, F, G, J, P, Q | Best official reference for explicit handoff, guardrail, session and trace contracts. | Adapt typed handoff/guardrail/receipt boundaries after Nexus authorizes Agent Runtime; do not add SDK runtime in Slice 2. |
| [google/adk-python](https://github.com/google/adk-python) | E, F, G, K, P, Q, R | Strong explicit distinction between Agent behavior and Workflow orchestration. | Adapt workflow/agent separation, confirmation tokens and bounded graph transition schemas; no runtime dependency yet. |
| [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | B, E, G, O, P, Q, R | Best type-driven contract and result-validation patterns. | Adapt schema-first tool/result validation, dependency injection and explicit capability composition. Do not import shell/subagent authority. |
| [agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope) | B, C, D, E, F, I, J, N, O, R | Comprehensive permission-event-workspace architecture. | Adapt event envelopes, permission decisions and capability-limited workspace contracts only; do not import the full rapidly expanding runtime. |
| [traceloop/openllmetry](https://github.com/traceloop/openllmetry) | J, P | Cross-runtime standard trace propagation without owning a full observability platform. | Adapt stable event/span naming and trace correlation IDs; keep collection opt-in, local, redacted and independent from execution authority. |
| [dbos-inc/dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py) | K, R | Clear mapping from ordinary functions to versioned durable steps. | Adapt step receipts, idempotency keys and resume-from-last-validated-step; avoid mandatory Postgres until scale requires it. |
| [scip-code/scip](https://github.com/scip-code/scip) | L, P | Best reviewed neutral code-index interchange model. | Adapt stable symbol identity, index version/hash and producer provenance; avoid requiring all external indexers initially. |
| [agentclientprotocol/agent-client-protocol](https://github.com/agentclientprotocol/agent-client-protocol) | E, O, P, R | Strong model for separating wire protocol version from artifact/package version and optional capability negotiation. | Adapt version/capability negotiation and schema artifact pinning; do not treat negotiated capability as authorization. |
| [cline/cline](https://github.com/cline/cline) | B, E, F, I, J, O, Q, R | Useful concrete design for action approvals, reversible checkpoints and visible diffs. | Adapt approval receipts, reversible action boundaries and plan/act mode invariants only. Do not import runtime, schedules or auto-approve. |

These sources influence architecture only; they are not dependencies.

## 25. REFERENCE ONLY candidates

| Candidate | Domains | Unique value | Reference boundary |
|---|---|---|---|
| [letta-ai/letta](https://github.com/letta-ai/letta) | A, B, E, O | Useful study of explicit editable memory blocks and Git-backed context history. | Reference memory-block ergonomics and append-only history only. Do not permit agent self-modification or cloud-coupled identity. |
| [microsoft/graphrag](https://github.com/microsoft/graphrag) | B, L | Well-documented graph context methodology for large narrative corpora. | Reference the methodology only; the project explicitly reports maintenance mode and is too expensive for default Nexus context. |
| [run-llama/llama_index](https://github.com/run-llama/llama_index) | A, B, L | Reference connector abstractions and provenance-aware node metadata. | Do not introduce the framework; adapt narrow connector contracts only when a concrete Nexus source requires them. |
| [continuedev/continue](https://github.com/continuedev/continue) | B, O, Q, R | Reference cross-harness context-file and provider UX. | Keep reference-only; Nexus already has a narrower Host/MCP contract and should not embed an editor harness. |
| [docker/mcp-registry](https://github.com/docker/mcp-registry) | C, D, I, N | Reference container provenance, SBOM and minimal-permission catalog metadata. | Do not make Docker a Nexus prerequisite; consume only provenance concepts or optional metadata later. |
| [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) | C, E, I, J, N, P | Reference federation, policy placement and protocol-translation boundaries. | Do not integrate; Nexus R2 intentionally remains local/read-plan-only and remote/federated gateway work is deferred. |
| [docker/mcp-gateway](https://github.com/docker/mcp-gateway) | C, D, I, N | Reference separation of catalog, gateway, secrets and server lifecycle. | Keep reference-only; no Docker, OAuth or dynamic server execution prerequisite for Nexus. |
| [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | G, I, N | Canonical MCP debugging behavior and test cases. | Reference its conformance matrix; do not vendor or require it until license and sandboxed invocation are resolved. |
| [awslabs/a2a-agent-registry-on-aws](https://github.com/awslabs/a2a-agent-registry-on-aws) | C, D, P | Reference Agent Card normalization and explicit registration/discovery separation. | Do not integrate; A2A is deferred and a local metadata registry should not depend on AWS. |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | E, F, J, Q | Reference flow/crew separation and declarative task dependencies. | Do not import; it duplicates future Nexus runtime responsibilities and offers less precise authority separation than needed. |
| [camel-ai/camel](https://github.com/camel-ai/camel) | E, F, A, Q | Reference research on coordination and failure modes, not a production control plane. | Keep reference-only; do not use swarm scale as a Nexus design goal. |
| [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT) | E, F, Q | Reference explicit SOP artifacts and producer/reviewer role separation. | Do not integrate; adapt only the idea that role outputs are typed artifacts subject to review. |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | E, F, I, O, Q, R | Reference event/workspace/conversation separation and sandbox UX. | Do not integrate; Nexus must remain a capability router rather than another coding-agent platform. |
| [confident-ai/deepeval](https://github.com/confident-ai/deepeval) | G, J, Q | Reference metric contracts, datasets and regression organization. | Use deterministic Nexus validators first; consider a separately approved optional judge adapter only after calibration. |
| [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | G, J | Reference experiment/dataset lineage and trace exploration UX. | Do not integrate or redistribute; adapt redacted trace schemas and dataset versioning from permissive standards. |
| [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | G | Reference groundedness/retrieval metric decomposition. | Keep reference-only until Nexus has a retrieval runtime and calibrated datasets. |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | G, J | Reference trace-to-dataset feedback loops and evaluator lineage. | Do not import the platform; adapt minimal redacted event/receipt schema and opt-in dataset promotion. |
| [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | H, O, Q | Reference minimal action interfaces, trajectory evidence and repair evaluation. | Do not integrate the superseded harness; adapt bounded reproduce-fix-regression states. |
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | H, K, Q | Reference evidence-gated hypothesis-experiment-feedback loops. | Adapt bounded diagnosis/repair/validation state transitions only. |
| [NVIDIA/garak](https://github.com/NVIDIA/garak) | G, I | Reference red-team taxonomy and pass/fail probe reporting. | Keep optional reference until Nexus has an approved model endpoint and synthetic red-team budget; do not add live calls by default. |
| [temporalio/temporal](https://github.com/temporalio/temporal) | E, K, R | Gold-standard conceptual source for deterministic replay and activity separation. | Reference event history, deterministic workflow/activity separation and idempotency tokens; do not add the server. |
| [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | K, J, R | Reference simple task/flow decoration and observable retry states. | Do not integrate; Nexus needs a smaller state ledger rather than a data orchestrator. |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet) | E, K, J, R | Reference pause/resume event contracts and worker slot/rate controls. | Keep reference-only; too large for local Nexus checkpointing. |
| [a2aproject/A2A](https://github.com/a2aproject/A2A) | C, E, F, P, R | Best reviewed agent-to-agent interoperability standard. | Keep reference-only until Nexus has a bounded Agent Runtime; later map Nexus task/receipt states to A2A without exposing hidden context. |
| [ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) | J, P, R | Reference event taxonomy for future user-visible state transitions. | Do not integrate in the local Desktop phase; adapt only redacted event semantics if Nexus gains a separate UI. |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | B, E, I, O, Q, R | Reference cross-harness Skill/plugin conventions only. | Do not vendor, redistribute or depend on source; rely on public specifications and approved compatibility tests. |
| [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | B, E, I, N, O, Q, R | Reference checkpoint UX and context-file layering in an open harness. | Keep reference-only; adapt checkpoint and context precedence tests, not the runtime. |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | E, F, I, O, Q | Reference explicit plan-only vs execution-capable modes. | Do not import; Nexus already separates read-only planning from Host execution. |

## 26. WATCH candidates

| Candidate | Domains | Unique value | Re-evaluation condition |
|---|---|---|---|
| [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | A, B, M | Broad memory-cube isolation and feedback correction across agents. | Watch until architecture and local-only security contracts stabilize; consider cube isolation and correction receipts after a dedicated memory threat model. |
| [snyk/agent-scan](https://github.com/snyk/agent-scan) | D, I, N | Useful risk taxonomy and cross-harness discovery coverage. | Watch and adapt issue taxonomy only. Do not run on private Nexus content until a no-execution/no-egress mode is independently proven. |
| [opendatahub-io/skills-registry](https://github.com/opendatahub-io/skills-registry) | C, D, P | May provide useful cross-harness packaging examples. | Watch only; no direct installer or symlink behavior. Re-evaluate if it adopts pinned, reviewed, fail-closed admission. |
| [open-multi-agent/oma-forge](https://github.com/open-multi-agent/oma-forge) | E, F, P | Potentially useful packaging ideas if a real protocol and governance model emerges. | Watch only; do not run or import. Require protocol stability, sandboxing, and execution receipts before reconsideration. |
| [codefuse-ai/CodeFuse-Query](https://github.com/codefuse-ai/CodeFuse-Query) | L | Potential reusable query model for architecture/impact analysis. | Watch until maintenance, Windows packaging and index provenance are clearer. |
| [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | B, L, O | Most directly relevant turnkey local CodeGraph candidate, also used by TencentDB-Agent-Memory. | Watch and benchmark in an isolated repository later; require pinned binaries, SBOM, no auto-update, bounded index and deterministic provenance before integration. |
| [sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) | M, G, H, O | Best reviewed evidence-driven Skill evolution candidate beyond Nuwa/RevFactory. | Watch until Nexus has quarantine, deterministic validators, isolated execution and explicit human promotion. Never auto-install generated output. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | B, C, D, E, F, G, H, I, J, M, O, Q, R | High-density source of patterns and test ideas across harnesses. | Keep CANDIDATE_SOURCE/WATCH. Review components individually; never install the whole bundle or grant agents/hooks automatic authority. |

## 27. REJECT candidates

| Candidate | Domains | Unique value | Rejection |
|---|---|---|---|
| [archestra-ai/archestra](https://github.com/archestra-ai/archestra) | C, E, I, J, N | Some policy/gateway ideas overlap IBM/ToolHive but add no unique low-risk fit. | Reject direct use and code adaptation; use permissively licensed primary sources for equivalent patterns. |
| [microsoft/autogen](https://github.com/microsoft/autogen) | E, F, N, P | Historical design reference is superseded by better maintained permissive candidates. | Reject direct dependency; use successor/standards documentation if a future review is approved. |
| [THU-MAIC/OpenMAIC](https://github.com/THU-MAIC/OpenMAIC) | F | No unique infrastructure value beyond generic multi-agent coordination. | Reject for Nexus architecture; it is a vertical application, not a reusable bounded runtime. |
| [microsoft/AgentAsJudge](https://github.com/microsoft/AgentAsJudge) | G, F | Little unique value over stronger eval frameworks and deterministic validators. | Reject; low adoption, narrow text scoring and nondeterministic multi-agent judging do not justify risk. |
| [protectai/llm-guard](https://github.com/protectai/llm-guard) | I | No unique maintained value over active scanners and explicit Nexus policy. | Reject direct use due archived status. |
| [restatedev/restate](https://github.com/restatedev/restate) | E, K, R | Patterns overlap Temporal/DBOS without a licensing or complexity advantage. | Reject direct dependency; use permissive sources for equivalent state-machine patterns. |
| [dagster-io/dagster](https://github.com/dagster-io/dagster) | K, J | No unique Nexus value beyond generic orchestration. | Reject for Nexus; use smaller workflow patterns from DBOS/LangGraph. |
| [github/stack-graphs](https://github.com/github/stack-graphs) | L | Valuable paper/design, but maintained alternatives are required. | Reject direct use due archived status; cite as historical reference only. |
| [agi-inc/agent-protocol](https://github.com/agi-inc/agent-protocol) | E, P | No unique value over active standards. | Reject due lower activity and protocol redundancy. |
| [RooCodeInc/Roo-Code](https://github.com/RooCodeInc/Roo-Code) | E, F, O | No unique maintained value over Cline/OpenCode/Codex. | Reject direct use due archived status. |

## 28. Duplicate/redundancy findings

### Memory

| Best of class | TencentCloud/TencentDB-Agent-Memory (governed team assets)<br>getzep/graphiti (temporal provenance)<br>mem0ai/mem0 (compact retrieval) |
| Complementary | langchain-ai/langmem (hot/background memory) |
| Redundant | run-llama/llama_index (broad retrieval framework) |
| Unsuitable | letta-ai/letta runtime self-modification<br>MemOS automatic skill evolution |
| Nexus decision | Nexus-owned hybrid: typed assets + temporal provenance + bounded retrieval; no imported proxy/runtime. |

### Registry and discovery

| Best of class | agentskills/agentskills (format)<br>cloudflare/agent-skills-discovery-rfc (Skill discovery)<br>modelcontextprotocol/registry (MCP metadata) |
| Complementary | NVIDIA/SkillSpector (security signal)<br>iflytek/skillhub (lifecycle patterns)<br>Observal/Observal (usage evidence) |
| Redundant | docker/mcp-registry for mandatory local use<br>multiple ambiguous skills-registry projects |
| Unsuitable | opendatahub installer/symlink behavior<br>Open SSR exact name unverified |
| Nexus decision | Build a small Nexus aggregator/admission layer; official/standard sources feed candidates, never authority. |

### Agent Runtime

| Best of class | openai/openai-agents-python (handoffs/guardrails)<br>google/adk-python (workflow/confirmation)<br>pydantic/pydantic-ai (typed contracts) |
| Complementary | agentscope-ai/agentscope permission/event patterns |
| Redundant | crewAIInc/crewAI<br>camel-ai/camel<br>MetaGPT |
| Unsuitable | microsoft/autogen superseded<br>OpenMAIC vertical app |
| Nexus decision | Adapt small contracts only; no runtime import before admission/evaluation/checkpoint prerequisites. |

### Multi-Agent

| Best of class | google/adk-python bounded graphs<br>openai/openai-agents-python handoffs |
| Complementary | Edict governance evidence from frozen seed audit |
| Redundant | CrewAI role crews<br>MetaGPT software-company roles |
| Unsuitable | unbounded CAMEL scale<br>early OMA Forge subprocess model |
| Nexus decision | Future bounded creator-reviewer/enhancer DAG, not swarm/debate by default. |

### Evaluation and observability

| Best of class | promptfoo/promptfoo development regression<br>traceloop/openllmetry event semantics |
| Complementary | deepeval metric ideas<br>garak red-team taxonomy<br>Observal evidence loops |
| Redundant | Langfuse and Phoenix full platforms |
| Unsuitable | AgentAsJudge low-evidence multi-judge<br>llm-guard archived |
| Nexus decision | Deterministic validators first; calibrated judge tests optional; redacted local traces only. |

### Durable workflow and checkpoint

| Best of class | langchain-ai/langgraph state/interrupt model<br>dbos-inc/dbos-transact-py step/idempotency model |
| Complementary | Temporal deterministic history as reference<br>Cline revert/checkpoint UX |
| Redundant | Prefect/Hatchet generic orchestration services |
| Unsuitable | Dagster data-asset focus<br>Restate BSL service |
| Nexus decision | Nexus-owned append-only local ledger; no orchestration server. |

### Code intelligence

| Best of class | tree-sitter/tree-sitter syntax foundation<br>scip-code/scip semantic index protocol |
| Complementary | colbymchenry/codegraph isolated benchmark<br>Graphiti temporal graph model |
| Redundant | Tencent bundled CodeGraph as a reason to reuse its whole runtime |
| Unsuitable | stack-graphs archived<br>CodeFuse-Query uncertain activity/Windows |
| Nexus decision | Layer syntax -> versioned semantic index -> optional graph, each with producer hash/provenance. |

### Skill factory

| Best of class | sentient-agi/EvoSkill held-out evolution |
| Complementary | Nuwa and RevFactory patterns from frozen seed audit |
| Redundant | multiple persona/skill generators without evaluation |
| Unsuitable | automatic promotion or agent self-modification |
| Nexus decision | Quarantine + held-out tests + security scan + explicit human promotion; generation never grants trust. |

### MCP gateway

| Best of class | stacklok/toolhive security model<br>official MCP registry metadata |
| Complementary | MCP Inspector conformance tests |
| Redundant | IBM ContextForge, Docker Gateway and Archestra for current local-only scope |
| Unsuitable | Remote MCP/OAuth in current phase |
| Nexus decision | Preserve R2 read/plan-only boundary; adopt metadata and policy patterns, not gateways. |

### Harness

| Best of class | OpenAI Codex frozen official audit<br>Cline approval/checkpoint patterns<br>Gemini CLI checkpoint/context patterns |
| Complementary | Pydantic AI harness typed capabilities |
| Redundant | OpenCode full agent<br>OpenHands platform |
| Unsuitable | Claude Code source redistribution<br>Roo Code archived<br>ECC whole-bundle install |
| Nexus decision | Host remains executor; Nexus stays router/handoff. Cross-harness support is protocol mapping, not bundling. |

### Interoperability

| Best of class | Agent Skills format<br>MCP for tools<br>A2A for agent-to-agent<br>ACP for editor-agent |
| Complementary | AG-UI for future UI events |
| Redundant | generic Agent Protocol |
| Unsuitable | Treating any advertised capability as authorization |
| Nexus decision | Map protocols through versioned adapters; keep trust, permissions and Host eligibility Nexus-owned. |

Canonical alias findings:

- `invariantlabs-ai/mcp-scan` resolves to the current Snyk Agent Scan lineage.
- `All-Hands-AI/OpenHands` resolves to `OpenHands/OpenHands`.
- `sourcegraph/scip` resolves to `scip-code/scip`.
- `explodinggradients/ragas` resolves to `vibrantlabsai/ragas`.
- `AI-Engineer-Foundation/agent-protocol` resolves to `agi-inc/agent-protocol`.
- The active Letta source moved from `letta-ai/letta` to `letta-ai/letta-code`.
- Generic labels such as Agent Registry, skills-registry and agent-discover cannot be used as source identity.

## 29. License/security blockers

| Candidate | Reviewed license | Disposition | Blocking concern |
|---|---|---|---|
| [archestra-ai/archestra](https://github.com/archestra-ai/archestra) | AGPL-3.0-only default; enterprise-marked regions proprietary | REJECT | AGPL-3.0 default; enterprise mixed licensing; broad execution/credential boundary; duplication |
| [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | UNRESOLVED (no root license file found) | REFERENCE ONLY | No root license file found at reviewed commit; server launch/connect side effects; Node dependency |
| [microsoft/autogen](https://github.com/microsoft/autogen) | CC-BY-4.0 at reviewed root | REJECT | Superseded architecture; CC-BY root license ambiguity for code; MCP command execution; framework overlap |
| [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | Elastic License 2.0 | REFERENCE ONLY | ELv2 restriction; trace privacy; large service footprint; remote MCP excluded |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | MIT core; enterprise directories separately licensed | REFERENCE ONLY | Mixed licensing; large database stack; trace data sensitivity; platform overlap |
| [restatedev/restate](https://github.com/restatedev/restate) | Business Source License 1.1 | REJECT | BSL-1.1; server dependency; runtime authority; duplication |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | All rights reserved; Anthropic Commercial Terms | REFERENCE ONLY | Proprietary license; host-private state; service dependency; cannot assume feature parity |

Additional security blockers:

- discovery metadata cannot prove code safety;
- stars/forks cannot prove trust;
- scanner output cannot grant authority;
- auto-update and `latest` are incompatible with reproducible admission;
- a prompt/proxy layer can become an injection boundary;
- automatic Skill generation cannot bypass quarantine;
- trace capture can leak confidential context;
- remote MCP/A2A introduces credentials, network and replay boundaries;
- host-installed or advertised capability is not necessarily callable;
- no candidate may scan ChatGPT private state.

## 30. Recommended architecture changes

1. Keep Nexus Core planner/selector deterministic and data-driven; external catalogs remain untrusted candidate sources.
2. Introduce a separate Candidate Admission Control Plane with immutable source identity, commit/package hash, license, scanner evidence, duplicate disposition, compatibility and reviewer decision.
3. Use an explicit state ladder: DISCOVERED -> VERIFIED -> DEEPLY_EVALUATED -> QUARANTINED/APPROVED_REFERENCE -> ELIGIBLE_FOR_ROUTING; execution requires an independent Host mapping and current-turn evidence.
4. Build a minimal append-only local task/event ledger before Agent Runtime or self-healing. Every side effect needs an idempotency key and validation receipt.
5. Use deterministic validators as the primary quality gate. LLM judges are supplemental, calibrated, versioned and never sole authority.
6. Adopt protocol-specific adapters: Agent Skills for instruction packages, MCP Registry/MCP for tools, ACP for editor-agent capability negotiation, and A2A only after Agent Runtime exists.
7. For memory, build a Nexus-owned narrow model combining typed assets, temporal provenance, bounded retrieval, namespace permissions, retention/forgetting and human promotion. Do not import Tencent's proxy.
8. For code intelligence, layer pinned Tree-sitter parsing and SCIP-like indexes before considering a turnkey graph runtime.
9. Keep telemetry opt-in, local-first and redacted. Never auto-capture prompts, Skill bodies, project rules, absolute paths, secrets or hidden reasoning.
10. No candidate may install, update, start a process, mutate host configuration or become executable because of discovery metadata or popularity.

The recommended new component boundary is:

```text
External source adapters (read-only)
  -> Candidate normalizer
  -> Canonical identity + immutable pin
  -> License/provenance/security evidence
  -> Duplicate/conflict analysis
  -> Quarantine/review decision
  -> Recommendation only

Existing Nexus planner/selector
  -> Installed local catalog only
  -> Current-turn Host evidence
  -> Existing Host handoff
  -> Host-owned execution
  -> Validation receipt
```

No arrow crosses from external discovery directly to routing or execution.

## 31. Evidence-based Slice 2 recommendation

**Recommended Slice 2:** **Provenance-aware Candidate Admission and Read-only Skill/MCP Scout**.

Why this precedes Agent Runtime:

1. External capability discovery is currently a real gap.
2. The Slice 1 data-only decision bridge already provides a suitable boundary.
3. Agent Runtime would amplify supply-chain and recovery risk before admission, evaluation and checkpoint controls exist.
4. Agent Skills, the Cloudflare discovery RFC and official MCP Registry provide interoperable metadata inputs.
5. SkillSpector provides a candidate security signal without granting execution.
6. Recommendation-only behavior preserves the frozen Host/MCP boundary.

Slice 2 must stop at a candidate recommendation. It must not install, update, load into live context, start MCP, invoke Host tools or create execution eligibility.

## 32. Longer-term Slice roadmap

| Order | Phase | Name | Scope | Exit gate |
|---:|---|---|---|---|
| 1 | Slice 2 | Provenance-aware Candidate Admission and Read-only Skill/MCP Scout | Agent Skills normalization; allowlisted .well-known discovery; official MCP Registry read-only metadata; exact commit/package pinning; license/provenance/dedup/security evidence; NVIDIA SkillSpector no-LLM static signal; recommendation only | A candidate can move DISCOVERED -> VERIFIED -> REVIEWED/QUARANTINED with immutable evidence, but cannot become executable. |
| 2 | Slice 3 | Generic Reviewer / Evaluation Contracts | deterministic validator registry; creator-reviewer-enhancer evidence states; promptfoo dev-only synthetic regression; redacted evaluation receipts | Selected, executed, validated and reported remain distinct across more than Presentations. |
| 3 | Slice 4 | Durable Local Checkpoint and Resume Ledger | append-only state events; idempotency keys; resume tokens; snapshot hashes; replay/expiry protection; crash recovery | A long task resumes after process/usage interruption without replaying validated side effects. |
| 4 | Slice 5 | Context Budgeting and Scoped Memory Foundation | typed context slots; token budgets; provenance; temporal validity; opt-in namespaces; retention/forgetting; conflict states | Memory is inspectable, deletable, permission-scoped and never silently injected. |
| 5 | Slice 6 | Bounded Single-Agent Runtime Contract | lifecycle; budget; cancel/pause/resume; explicit tools; approval; receipts; failure isolation | One allowlisted Agent can execute under a typed contract with complete receipts and rollback. |
| 6 | Slice 7 | Bounded Multi-Agent Creator-Reviewer-Enhancer DAG | fixed role graph; fan-out limits; independent review; deterministic merge; budget and timeout | Multiple Agents add measurable value over one Agent under fixed budgets and audit traces. |
| 7 | R6 candidate milestone | External capability admission + generic validation + durable resume | Freeze only after clean Host and security acceptance | Research-to-runtime foundations are accepted without weakening R5 or Slice 1. |

The proposed **R6 candidate milestone** should cover external candidate admission, generic validation receipts and durable local resume—not a full Agent Runtime.

## 33. Projects explicitly deferred

- Slice 2 implementation
- Automatic Skill or MCP installation/update/execution
- Agent Runtime and multi-Agent runtime
- Generated Skill promotion
- Remote MCP, OAuth and credential flows
- Vector database or embeddings as a default Nexus dependency
- TencentDB-Agent-Memory runtime/proxy
- Large workflow/observability/gateway platforms
- ChatGPT private Host-state inspection or modification
- V1.3 or any frozen-tag movement

Also deferred:

- direct TencentDB-Agent-Memory runtime/proxy use;
- MemOS/Letta self-evolution;
- ECC whole-bundle installation;
- Docker/IBM/Archestra gateways;
- A2A remote agents;
- code graph runtime benchmarking;
- generic Documents/Spreadsheets Host execution expansion;
- V1.3.

## 34. Git/research branch status

| Item | Status |
|---|---|
| Branch | `nexus-ecosystem-gap-scan` |
| Started from | `32d01941acca95a9067329f0493508d151893b42` |
| Files added | `docs/nexus-ecosystem-gap-scan.md`, `research/nexus-ecosystem-gap-scan.json` |
| Production/runtime files changed | None |
| Main modified/merged | No |
| Frozen tags moved | No |
| New final tag | No |
| Candidate code installed/executed | No |
| Remote verification | Performed after the research commit; final SHA is reported in the completion response |
| Intended final worktree state | Clean |

## 35. Known uncertainties

- GitHub metadata is a time-stamped snapshot and can change after the pinned commits.
- Stars/forks are secondary context only and were not used as execution or trust evidence.
- Several repositories use mixed, source-available or unresolved licenses; owner/legal review is required before code reuse.
- No candidate code was installed or executed, so runtime behavior and benchmark claims were not independently reproduced.
- Some official specifications and preview registries can change before general availability.
- Windows compatibility was based on canonical documentation and repository evidence, not a clean-machine execution test for every candidate.
- Exact names Open SSR, skills-mcp, agent-discover and Open Multi-Agent did not resolve to single authoritative repositories.
- Nexus routing selected a Product Design research Skill whose UX workflow did not match this ecosystem architecture task; only its evidence-grounding discipline was applicable, and native Codex research completed the uncovered work.

The research remains a dated evidence snapshot. A future implementation review must re-verify exact commits, licenses, security policies and protocol versions before using any `INTEGRATE` recommendation.

---

## Decision

The ecosystem does not justify importing a broad Agent platform into Nexus. The evidence supports a smaller sequence: provenance-aware external candidate admission, generic validation receipts, durable checkpoint/resume, scoped context/memory, and only then a bounded Agent Runtime.

**NEXUS ECOSYSTEM GAP SCAN COMPLETE — READY FOR ARCHITECTURE REVIEW**
