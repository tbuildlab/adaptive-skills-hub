# Nexus Runtime R5 — Host Capability Inventory

**Status:** development pilot only. This additive protocol does not modify the
frozen Core, R1–R4 baselines, RC1–RC6, or any final tag.

## Finding

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

## Official platform boundary

OpenAI documents that a Plugin may provide Skills, MCP servers, or both; a
Skill supplies instructions and resources, while an MCP server exposes its own
declared tools. ChatGPT may choose among installed Plugins/Skills or the user
may select one explicitly. The documented MCP connection flow discovers tools
from the connected server.

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
  -> Host-visible Skill/Plugin/tool metadata subset
  -> closed, content-free snapshot
  -> nexus.assess_host_capabilities (read-only advisory assessment)
  -> minimum mapped Host capability set
  -> existing R4 plan/load/hash verification and Host handoff
  -> Host independently re-verifies and executes
  -> artifact validation and truthful receipt
```

The Host supplies only metadata that the platform already surfaced in the
current conversation. Nexus cannot request or claim a global list. Every
snapshot states:

```json
{
  "schema_version": "nexus.host-capability-snapshot.v1",
  "host_surface": "chatgpt_desktop",
  "inventory_scope": "current_turn_host_visible_subset",
  "inventory_completeness": "not_globally_enumerated",
  "task_category": "presentation"
}
```

Descriptors contain only bounded identities, an untrusted display name,
resource kind,
availability/evidence enums, closed interface tags, and a closed logical
capability. They cannot contain descriptions, raw instructions, paths, URLs,
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

Installed, enabled, metadata-visible, loadable, tool-callable, selected,
loaded, executed, and validated are separate states. The minimum-selection
algorithm covers only required interfaces and rejects redundant candidates.
For editable PowerPoint creation, the first pilot requires
`editable_pptx_create` plus `pptx_open_render_validate`.

The assessment is name-independent. A display name never grants a mapping.
Only a current-turn callable capability with an independently reviewed logical
Host mapping can be selected for handoff. The first reviewed mapping remains
`chatgpt.presentations`; adding another mapping requires separate code review,
security tests, and real Host execution evidence.

## Expected PPT classification

The exact result depends on what the Host actually surfaces in that new chat:

| Observed capability | Safe classification rule |
| --- | --- |
| Host-native Presentations with current callable-tool evidence | mapped primary creator; selected if it provides all required interfaces |
| DashAI PPT or Ppt Master visible/loadable but without a reviewed callable Host mapping | functional creator, but unavailable for Nexus execution |
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
- Snapshot timestamps and assessments are short-lived. The `current_turn`
  scope is a caller assertion, not a cryptographic chat binding; the Host must
  retain the actual current tool result and a per-chat replay set.
- The MCP tool is read-only, stateless, and has no filesystem, artifact,
  subprocess, network, installation, Agent, or Host execution authority.
- Unknown or unmapped capabilities can be classified but cannot be executed.
- The Host must independently verify current availability immediately before
  execution and must use the existing R4 handoff/receipt checks.
- The assessment only reports `considered` and `selected`; it can never report
  a Skill as loaded, executed, or validated.

## Host-local receipt binding

The MCP remains stateless. After a successful R4 execution, the Host keeps a
local `nexus.host-capability-receipt.v1` wrapper containing the assessment ID,
snapshot digest, exact selected identity/mapping, inventory states
`considered` and `selected`, and the existing R4 execution receipt. The local
validator requires that the inventory mapping equals the R4 handoff mapping,
rejects expiry/mismatch/replay, and accepts protocol success only when the
nested R4 receipt asserts an opaque `.pptx` artifact reference and passed
validation states. It cannot open or render the Host-owned artifact; real
artifact evidence and validation remain a Host/Desktop human-acceptance
boundary. The receipt is never sent to Nexus MCP and grants no execution
authority.

## Human acceptance boundary

Automated tests can verify schema validation, classification, minimal
selection, mapping restrictions, redaction, and MCP behavior. Only ChatGPT
Desktop can prove which capability metadata is surfaced in a real conversation
and whether the Host actually executes the mapped capability. Human acceptance
must inspect the inventory trace, then require the existing real editable
`.pptx`, open/render validation, and execution receipt.
