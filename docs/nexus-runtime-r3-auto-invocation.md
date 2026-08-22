# Nexus Runtime R3 Automatic Invocation Optimization

**Scope:** metadata-only optimization of the existing local R2 MCP tool
contract. It does not introduce a classifier service, embeddings, a vector
database, network calls, automatic Skill installation, an Agent runtime, or
execution authority.

## Status and evidence boundary

ChatGPT Desktop has already shown `nexus-r2-local` as enabled and successfully
completed explicit `nexus.health`, `nexus.discover_capabilities`, and
`nexus.plan_task` requests. An explicit editable PowerPoint planning request
selected `ppt-master`; the native editable PPTX routing correction is retained.

Four fresh Desktop conversations completed the automatic-selection evaluation.
Neither eligible positive prompt (editable PowerPoint planning or backend
debugging/regression testing) showed an observable Nexus tool call. Both
ineligible prompts (`What is 2 + 2?` and a one-sentence inflation explanation)
correctly bypassed Nexus. This proves only that automatic selection was **not
observed for those positive conversations**. It does not prove a Desktop defect
or a deterministic cause. Tool choice is host/model policy; R2 metadata can
clarify semantics but cannot force ChatGPT Desktop to call a local tool.

## Tool responsibility and activation policy

| Tool | Use when | Do not use when |
| --- | --- | --- |
| `nexus.health` | Diagnosing availability or the connection. | Planning, execution, or ordinary chat. |
| `nexus.discover_capabilities` | The user explicitly asks which Nexus Skills/capabilities are available. | Ordinary task planning or casual conversation. |
| `nexus.plan_task` | A substantive multi-step task benefits from selecting the smallest suitable Skill set before the host executes. | A greeting, simple arithmetic/fact, simple translation, short rewrite, or task execution itself. |

`nexus.plan_task` is eligible (not required) for professional artifact work,
technical implementation/debugging/testing/security, evidence-based research,
coursework planning, and comparable multi-step work. It remains advisory:
Nexus selects and validates a plan; the host decides whether and how to
execute it.

The exposed title and concise description make this boundary explicit. The
existing read-only, non-destructive, idempotent, and closed-world annotations
remain unchanged. Input schemas, opaque workspace authorization, redaction,
and response limits are unchanged.

`workspace_id` remains a required opaque authorization value. This is a
deliberate security boundary: the host cannot supply an arbitrary path, and R3
does not add a default workspace or reveal workspace roots merely to increase
automatic invocation. Consequently, hosts without a known configured ID may
decline to call `nexus.plan_task` automatically. This is an accepted limitation
for precision and least privilege, not a reason to weaken R2 authorization.

## Activation corpus

### Eligible positive cases

1. `I need to create an editable PowerPoint presentation. Plan the work first.`
2. `Create a professional Excel forecasting workbook from my data.`
3. `Help me diagnose this backend API bug and add regression tests.`
4. `Review this application for cross-user authorization vulnerabilities.`
5. `Prepare an evidence-based Word report from these sources.`
6. `Help me plan my business assignment using the rubric and lecturer materials.`
7. `Create and verify a PDF report.`
8. `Build a responsive frontend page from this design.`

### Normally ineligible negative cases

1. `Hello.`
2. `What is 2 + 2?`
3. `Explain inflation in one sentence.`
4. `Translate 'thank you' into Chinese.`
5. `Rewrite this sentence to sound friendlier.`
6. `What does GDP stand for?`

### Boundary cases

| Prompt | Eligibility |
| --- | --- |
| `Explain what PowerPoint is.` | No |
| `Help me create a PowerPoint.` | Yes |
| `What is an Excel workbook?` | No |
| `Build an Excel workbook with formulas and charts.` | Yes |
| `What is SQL injection?` | Normally no |
| `Audit this API for SQL injection and propose regression tests.` | Yes |
| `Summarize this short paragraph.` | Normally no |
| `Analyze these sources and prepare a cited report.` | Yes |

These are evaluation prompts, not hard-coded trigger phrases. The Nexus core
still assesses the task only after a host elects to call it.

## Platform behavior classification

- **Supported:** MCP tools expose name, title, description, JSON input schema,
  and annotations; R2 supplies all of these.
- **Recommended:** concise, explicit descriptions state what a tool does, when
  to use it, side effects, and key exclusions.
- **Heuristic:** a host/model may use this semantic metadata when deciding
  whether a tool is relevant.
- **Not guaranteed:** ChatGPT Desktop automatic invocation for any individual
  eligible prompt. No R2 description can require a call.
- **Observed here:** automatic tool selection did not occur for the two tested
  eligible Desktop prompts, while both tested ineligible prompts bypassed it.
- **Variable:** account-, model-, and product-surface-specific automatic-tool
  selection behavior may differ elsewhere and is not a product contract.

Local Codex-host observation is a separate Level C signal. A natural positive
prompt did not show an MCP call within the observable command window, so it is
recorded as inconclusive rather than a pass or a Desktop result.

Official references: [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.2)
and [Extending Codex with MCP](https://learn.chatgpt.com/docs/extend/mcp).

## Completed Desktop acceptance packet

Each prompt was run in a **fresh ChatGPT Desktop conversation** with no mention
of Nexus, MCP, or Skills:

1. `I need to create an editable PowerPoint presentation. Plan the work first.`
2. `Help me diagnose this backend API bug and add regression tests.`
3. `What is 2 + 2?`
4. `Explain inflation in one sentence.`

The first two prompts had no observable Nexus call. The final two bypassed
Nexus, as intended. If a substantive task needs Nexus, the reliable R3 contract
is an explicit request such as `Use Nexus to plan this task: ...`, or a visible
MCP/tool selection where available. Do not infer literal `@Nexus` support
unless that product surface is visible.

## Security and performance

The metadata contains no paths, workspace roots, instructions, credentials, or
execution claim. It adds no preflight catalog call to ordinary chat: selection
remains the host's decision and `plan_task` remains bounded after invocation.
