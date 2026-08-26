# Nexus Runtime R5 — Host Capability Inventory

**Status:** human accepted as the bounded inventory component of
`runtime-r5-final`. This additive protocol does not modify the frozen Core,
R1–R3 baselines, RC1–RC6, or any earlier final tag. The R4 Host handoff is
accepted as a component of the same R5 baseline rather than through a separate
R4 tag.

## Finding and pilot.3 defect

The successful Desktop presentation run used only `Presentations` because two
different inventories had been conflated:

1. Nexus builds a local metadata catalog from project Skills, user Skills, and
   plugin source/cache directories. That catalog can prove that a `SKILL.md`
   exists and can be loaded by Nexus/Codex, but it does not prove that the
   current ChatGPT Desktop conversation has enabled or can execute it.
2. The R4 execution path intentionally restricts the handoff to the reviewed
   `chatgpt.presentations` mapping and independently verifies the selected
   `Presentations` Skill. R5 retains that mapping for bounded refinement.

Therefore the prior run did not compare all installed Host capabilities. It
followed the only reviewed Host execution mapping. This was safe, but it did
not provide a truthful current-Host inventory.

The pilot.3 Desktop trace then exposed a separate implementation defect. The
assessment succeeded, but Nexus required a fictional same-name callable
`Presentations` tool before it would map the Host capability. The Host instead
created and validated a `.pptx` through an independent native fallback. That
artifact was valid, but it was not adaptive execution and does not pass R5.

## Official platform boundary

OpenAI documents that a Plugin may provide Skills, MCP servers, or both; a
Skill supplies instructions and resources, while an MCP server exposes its own
declared tools. A Skill can work without an MCP server when its instructions
and tools already available to the model are sufficient. ChatGPT may choose
among installed Plugins/Skills or the user may select one explicitly. The
documented MCP connection flow discovers tools from the connected server.

Consequently, a Host Skill workflow does not need a callable tool with the same
name. The reviewed Presentations path is `load/follow Presentations Skill
instructions -> use the Host artifact/runtime tools required by that workflow`,
not `call a tool named Presentations`.

The current official documentation does not expose an API by which one local
Plugin/MCP server can enumerate every installed/enabled ChatGPT Desktop Skill
or Plugin, inspect host enablement state, or programmatically invoke an
arbitrary second Host Skill. Nexus therefore must not scrape Desktop caches,
configuration, or private application state and must not represent a local
filesystem catalog as a Host inventory.

References:

- [Plugin architecture](https://developers.openai.com/plugins/concepts/plugins)
- [Skills](https://developers.openai.com/plugins/concepts/skills)
- [MCP servers](https://developers.openai.com/plugins/concepts/mcp-server)
- [Connect a Plugin to ChatGPT](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [ChatGPT Skills and Plugins](https://learn.chatgpt.com/docs/skills-and-plugins)

## Supported inventory architecture

```text
Current ChatGPT Desktop conversation
  -> nexus.begin_host_capability_assessment
  -> server-issued, 120-second, single-use runtime ticket
  -> Host-visible Skill/Plugin/tool metadata subset
  -> Host loads relevant Skill instructions and verifies required Host runtime/tools
  -> closed, content-free ticket-bound snapshot
  -> nexus.assess_host_capabilities (read-only advisory assessment)
  -> minimum mapped Host capability set
  -> existing R4 plan/load/hash verification and Host handoff
  -> Host independently re-verifies and executes
  -> artifact validation and truthful receipt
```

The Host first requests a ticket whose purpose fixes the surface, scope,
completeness, task category, and required interfaces. Nexus stamps that ticket
with server time and stores only bounded replay state in the current stdio
runtime process. The Host then supplies only metadata that the platform already
surfaced in the current conversation. Nexus cannot request or claim a global
list. The snapshot contains no caller-generated timestamp and cannot repeat or
alter the ticket purpose:

```json
{
  "schema_version": "nexus.host-capability-snapshot.v3",
  "ticket_id": "server-issued UUID",
  "snapshot_id": "new UUID",
  "capabilities": []
}
```

Descriptors contain only bounded identities, an untrusted display name,
resource kind, availability/evidence enums, closed interface tags, a closed
logical capability, and exactly one execution binding kind:
`direct_host_tool`, `host_skill_workflow`, or `none`. They cannot contain
descriptions, raw instructions, paths, URLs,
commands, tool handles, permissions, environment values, secrets, project
content, or arbitrary execution mappings. Nexus includes the label in the
snapshot digest but does not echo it in the MCP result. The Host correlates the
returned opaque provider/capability IDs with its own current-turn trace. This
prevents a hostile label from becoming reflected tool-output instructions.

## Classification and selection

The assessment reports all relevant observed capabilities with two distinct
facts:

- `functional_role`: `primary_creator`, `enhancer`, `reviewer`, `alternative`,
  or `incompatible` based on closed interfaces;
- `classification` and `decision_state`: including `redundant`, `unavailable`,
  `considered`, `selected`, or `rejected` based on current evidence and mapping
  eligibility.

Installed, enabled, metadata-visible, loadable, workflow-ready, tool-callable,
selected, loaded, executed, and validated are separate states. The minimum-selection
algorithm covers only required interfaces and rejects redundant candidates.
For editable PowerPoint creation, the first pilot requires
`editable_pptx_create` plus `pptx_open_render_validate`.

The assessment is name-independent. A display name never grants a mapping.
Only a current-turn executable binding with an independently reviewed logical
Host mapping can be selected for handoff. A direct binding requires a real
current-turn tool plus tool-catalog evidence. A Host Skill-workflow binding
requires current Skill metadata, loaded instructions, the current tool catalog,
and the complete current execution substrate required by those instructions.
The first reviewed mapping remains `chatgpt.presentations`, pinned to the
canonical `openai-primary-runtime/presentations/skill` provenance identity;
labels cannot grant it. Adding another identity or mapping requires separate
code review, security tests, and real Host execution evidence.

## Expected PPT classification

The exact result depends on what the Host actually surfaces in that new chat:

| Observed capability | Safe classification rule |
| --- | --- |
| Host-native Presentations with canonical provenance, loaded instructions, and complete current execution substrate | mapped `host_skill_workflow` primary creator; selected if it provides all required interfaces |
| DashAI PPT or Ppt Master visible/loadable but without a reviewed current-turn Host execution binding | functional creator, but unavailable for Nexus execution |
| A callable non-PPTX presentation creator without a reviewed mapping | alternative, rejected |
| emil-design-eng with an explicit presentation review interface | reviewer; otherwise incompatible |
| Unmapped callable creator already covered by the selected mapping | redundant but not execution-eligible |
| Two descriptors claiming the same reviewed logical execution mapping | ambiguous snapshot; fail closed |
| Disabled, installed-only, or stale candidate | unavailable |
| Capability not surfaced in the current conversation | not observed; Nexus makes no claim |

These names are examples for acceptance reporting, not branches in the
implementation.

## Security properties

- The snapshot is a Host assertion, not authenticated Host state.
- Its SHA-256 is an integrity binding, not an authorization credential.
- The ticket uses Nexus server time, a monotonic 120-second deadline, atomic
  single-use consumption, and a bounded in-process tombstone. It removes the
  unreliable caller-clock dependency without extending the freshness window.
- Ticket binding proves only freshness and one use in the same Nexus stdio
  runtime process. The `current_turn` scope remains a Host assertion, not a
  cryptographic ChatGPT turn identity; the Host must retain the actual current
  tool result and a per-chat replay set.
- The MCP tool is read-only and has no persistent state, filesystem, artifact,
  subprocess, network, installation, Agent, or Host execution authority.
- Unknown or unmapped capabilities can be classified but cannot be executed.
- A caller cannot grant a mapping by supplying a label or logical ID; Nexus
  derives eligibility from a reviewed provider/capability/kind identity and a
  matching binding profile.
- The Host must independently verify current availability immediately before
  execution and must use the existing R4 handoff/receipt checks.
- The assessment only reports `considered` and `selected`; it can never report
  a Skill as loaded, executed, or validated.

## Host-local receipt binding

The MCP retains only bounded, short-lived security state for tickets; it writes
nothing to disk. Immediately before execution, the Host claims the still-fresh
assessment/handoff pair into a one-use Host-local execution-start binding. The
claim includes a canonical SHA-256 of the complete allowlisted R4 handoff after
strict schema, selected Skill/hash/load, profile, validation, fallback, and
security checks, plus the selected provider/capability identity, execution
binding kind, and R4 selected Skill resource/hash from the bound assessment.
It is not an MCP payload or authorization token. It prevents stale work from
starting, while allowing a real artifact build and validation to complete after
the original ticket/handoff TTL without extending either TTL. After a successful
R4 execution, the Host keeps a local
`nexus.host-capability-receipt.v3` wrapper containing the ticket ID, assessment
ID, snapshot digest, exact selected identity/mapping, inventory states
`considered` and `selected`, and the existing R4 execution receipt. The local
validator requires that the inventory mapping equals the R4 handoff mapping,
rejects stale starts, identity/binding/hash mismatch, or replay, and consumes a
one-use start claim even when the later receipt fails. It accepts protocol success only when the
nested R4 receipt asserts an opaque `.pptx` artifact reference and passed
validation states. It cannot open or render the Host-owned artifact; real
artifact evidence and validation remain a Host/Desktop human-acceptance
boundary. The receipt is never sent to Nexus MCP and grants no execution
authority.

If ticket issuance or assessment fails, or the reviewed Skill is present but
its current-turn execution substrate cannot be proved, the adaptive path stops
before Nexus planning or handoff with
`HOST_EXECUTION_BINDING_UNAVAILABLE`. A separately safe native Host fallback is allowed only as
an explicitly separate result: `adaptive_path.status: failed`, the exact
assessment-stage reason code, `fallback.kind: native_host_fallback`, and no
Nexus selected/loaded/executed/enhanced capability states. A native artifact
may be valid, but it is not R5 adaptive success.

## Human acceptance boundary

Automated tests can verify schema validation, classification, minimal
selection, mapping restrictions, redaction, and MCP behavior. Only ChatGPT
Desktop can prove which capability metadata is surfaced in a real conversation
and whether the Host actually executes the mapped capability. Human acceptance
must inspect the inventory trace, then require the existing real editable
`.pptx`, open/render validation, and execution receipt.

## Pilot.4 accepted inventory evidence

The successful Desktop trace used inventory scope
`current_turn_host_visible_subset` and completeness
`not_globally_enumerated`. The restricted assessment considered and selected
only the relevant `presentations` capability. Its execution
binding was the reviewed `host_skill_workflow -> chatgpt.presentations ->
nexus.host-map.presentations.v1` mapping. The subsequent Host receipt proved
actual execution and validation; the inventory assessment itself did not claim
those states.

Ppt Master was visible in the Host skill directory but was not included in the
restricted snapshot. It was therefore not considered, selected, rejected, or
executed by Nexus. DashAI PPT (`dashiai-ppt`) was visible but disabled and was
also absent from the snapshot; it likewise was not considered, selected,
rejected, or executed. Neither name is an authorization rule, and the accepted
freeze does not expand Nexus into unsupported global Host enumeration.

Known limitation: the protocol truthfully reasons only over current-turn
Host-surfaced metadata. Capabilities outside that subset are `not observed`,
not implicitly unavailable, redundant, or rejected.
