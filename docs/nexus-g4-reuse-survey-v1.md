# Nexus G4 Reuse Survey and Implementation Scope v1

Status: implementation entry survey, 2026-10-10. Source HEAD: `792a3fd`.
G4_MODE = PREPARATION_FAIL_CLOSED. D01 = CLOSED (bounded live profile),
D03 = DEFERRED, G3 = INCOMPLETE, REAL_ADMISSION_ENABLED = NO.
The current Owner directive permits independent offline G4 implementation; it
supersedes the historical pre-G4 NOT ENTERED scope without rewriting that history.
Historical D04 evidence is unchanged; executor exclusion is not a delegated-mode
release gate. This preparation does not qualify G2 or G3.

## Reconstructed accepted architecture

`docs/nexus-roadmap-v2.md` G4 and the three pre-G3/pre-G4 readiness documents
require Website and Source-backed Report packs, ProjectDecisionRecord,
ContextManifest, CapabilityRelation, ChangeImpactRecord and WorkflowPack.
The existing planner remains advisory. Domain logic stays outside planner core.
The declared managed G2 v3 configuration is historically verified in nexus-g2-openai-structured-v3.md; production Positive Host Binding remains ABSENT. Applicable durable recovery remains an external prerequisite for live authority acceptance. The
Owner's new instruction adds a preparation execution/result seam, not a new
planner, ledger, runtime, decision memory service or authority category.

## Capability matrix

| Capability | Current implementation | OpenAI/Host reuse available | Nexus responsibility | Action / reuse classification |
| --- | --- | --- | --- | --- |
| Reasoning, planning, decomposition, tool choice, coding, replanning | Existing Codex session; Nexus advisory planner | Current agent and tool loop | No replacement | REUSE / REUSE_DIRECT |
| File/repository work, tests, tool outputs, command failures | Current exec_command/apply_patch; existing Git/Python | Callable and exercised this session | Validate bounded evidence only | REUSE / REUSE_DIRECT |
| Structured tool invocation | Current tools and functions orchestration | Callable current session | Closed input/result contract | ADAPT / REUSE_WITH_THIN_ADAPTER |
| Context and session continuation | Host conversation/context; existing SafeContextReader | Host owns compaction and continuation | Scope, provenance, omissions and obligation checks | ADAPT / REUSE_WITH_THIN_ADAPTER |
| Execution status, cancellation and retries | managed_execution ExecutionStatus and ExecutionBackend | Host exec sessions/write_stdin, cancellation facilities | Preserve failed/cancelled/unknown; no automatic retry | ADAPT / REUSE_WITH_THIN_ADAPTER |
| Browser interaction | Current browser tool surface | Metadata visible; not exercised for G4 | Keep browser evidence separate from qualification | REUSE / REUSE_DIRECT; runtime availability UNVERIFIED |
| Computer interaction | Native computer APIs disabled in current CUA surface | Browser surfaces only | Do not infer native desktop access | NOT_REQUIRED |
| App connectors, skills, persistent chats | Current Host metadata/tools | Available subset; not globally inventoried or exercised | No connector platform or session store | REUSE / REUSE_DIRECT; execution UNVERIFIED |
| G1 profiles and conformance | ash/g1_profiles.py, g1_selection.py | Host facts remain distinct from permission | Reuse bounded/exact/token/hash validators | REUSE / REUSE_DIRECT |
| G3 authority | ash/g3_authorization.py and g3_host_approval_bridge.py | Host self-report cannot authenticate admission | Typed decision input; unconditional real deny | ADAPT / REUSE_WITH_THIN_ADAPTER |
| Parsing, canonical encoding, digest, quarantine evidence | ecosystem_models.py, ecosystem_evidence.py | Host outputs are untrusted evidence | Reuse parser/encoding; add isolated G4 schema domain | EXTEND / REUSE_WITH_THIN_ADAPTER |
| G2 execution, result classes and durability | managed_execution.py, core_host.py, openai_hosted.py | Existing interfaces; no fresh provider execution needed | Reference status vocabulary; no replacement ledger | REUSE / REUSE_WITH_THIN_ADAPTER |
| Five accepted domain records and two packs | Logical roadmap contracts only | Host can propose evidence; cannot certify scope/coverage | Closed deterministic validators | EXTEND / REUSE_WITH_THIN_ADAPTER |
| Recovery fence | D03 offline protocol defined; live fence unqualified | No qualified current fence | Fail-closed port; no service infrastructure | ADAPT / REUSE_WITH_THIN_ADAPTER |
| Replay protection for structural contract checks | Existing G3/G2 production protocols | Host retry is not an authority replay guarantee | Bounded one-use process-local structural checks only | EXTEND / REUSE_WITH_THIN_ADAPTER |
| AI memory, graph engine, scheduler, agents/frameworks, model router | Host owns generic functions | No demonstrated deterministic gap | None | NOT_REQUIRED |

No NEW Nexus subsystem is proposed. OPENAI_REUSE_INSUFFICIENT is established only
for deterministic contract checking: an executor's assertion cannot independently
establish authority, exact scope/generation, evidence binding or acceptance coverage.
Two small modules extend existing validation foundations. They perform no I/O,
transport, command execution, persistence, model calls or workflow scheduling.
No additional dependencies, provider execution or paid infrastructure is required.

## Evidence and limits of the survey

Repository evidence takes priority over installed metadata. The Nexus local skill
was inspected: its workflow is advisory/presentation-specific, not a general G4
execution runtime, so it is NOT_REQUIRED for this coding task. OpenAI Docs was
inspected for official-source research. Current tools establish only callable
surfaces and the local operations observed here; installed metadata does not prove
execution or production qualification.

Official OpenAI [Using tools](https://developers.openai.com/api/docs/guides/tools)
and [Shell](https://developers.openai.com/api/docs/guides/tools-shell) were opened
on 2026-10-10. They document external tools/local execution and observable tool
outputs. They do not certify this Nexus Host, G3 admission or D03 recovery. No
Agents API/SDK migration or extra provider dispatch is necessary.

## Finite implementation and acceptance boundary

Implement closed domain records, two offline pack coverage checks and a Host
request/result adapter with explicit structural-only fixtures, typed G3 deny,
exact input binding, replay refusal and unqualified recovery seam. Run adversarial
checks and full existing regression, update deterministic MANIFEST, commit and
push a development checkpoint. Do not use the final release tag: the Roadmap's
real bounded pack workflows and qualified G2/live acceptance remain unproved.
Implementation and offline qualification may complete independently; live
integration and real recovery remain blocked. A structural PASS never grants
execution, confirms an Owner decision or proves semantic source truth.
