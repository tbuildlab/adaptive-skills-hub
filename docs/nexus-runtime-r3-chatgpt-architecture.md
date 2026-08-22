# Nexus Runtime R3 — ChatGPT Integration Architecture and Feasibility

**Status:** design-only; this document implements nothing.

**Design branch:** `nexus-runtime-r3-design`
**Frozen baseline:** Nexus V1.2 + Runtime R2, `5825eb5f241e7276a5894c0af860953e38636b6e`.

## Executive summary

R3 should begin with **R3-E: reuse the existing local, read/plan-only Nexus R2
stdio server from ChatGPT Desktop on the same Codex host**. This is the smallest
documented architecture and adds no service, tunnel, OAuth deployment, copy of the
planner, or Windows remote-control path. The user enables/selects the configured
`Nexus` server in Desktop and uses `/mcp`; the host may call bounded capability or
planning tools and performs only work it independently supports.

This does not claim that ChatGPT Web can access
`D:\chatgpt\安装skills\adaptive-skills-hub`, that localhost is reachable from the
cloud, or that `@Nexus` is a supported literal invocation. Official documentation
states that ChatGPT Desktop, Codex CLI, and the IDE share local MCP configuration,
while ChatGPT Web does not read local Codex configuration and uses remote
plugin-backed tools. [Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp)

For later Web/cross-device use, defer **R3-B**: a custom plugin with a bounded
remote MCP backend. It needs a stable HTTPS endpoint and, when protected data is
exposed, OAuth-based authorization. It must never bridge cloud callers to this
machine's filesystem, shell, Skills, or credentials. This document does not
authorize R3-B implementation.

The exact `@Nexus` syntax is **UNKNOWN / NOT DOCUMENTED**. The closest documented
Desktop UX is `/mcp`; the closest Web UX is adding the enabled connection from the
tools menu. Tool metadata can influence selection but cannot guarantee automatic
invocation. [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)

## Scope and non-goals

### In scope

- Feasibility, UX, security, privacy, deployment, and test design.
- Local-Desktop-first reuse of R2's three read-only tools.
- A constrained future remote design and a future-only Skill Scout design.

### Explicit non-goals

- Any V1.1/V1.2/R1/R2 planner, ranking, selection, code, tag, or AI Coordinator change.
- A listener, HTTP service, tunnel, relay, OAuth flow/server, plugin/App package,
  web UI, deployment, payment, or dependency installation.
- Cloud access to D:, project files, raw `SKILL.md`, environment variables,
  credentials, shell, package installation, Agent spawning, or arbitrary execution.
- Automatic Skill discovery installation/update/execution.

## Evidence and terminology

### Current local facts

R2 is a local stdio adapter exposing exactly `nexus.health`,
`nexus.discover_capabilities`, and `nexus.plan_task`. It returns redacted planning
or capability data only. It uses opaque allowlisted workspace IDs, guarded context
and selected-Skill reads, bounded budgets, and read-only/non-destructive tool
annotations. It has no HTTP listener, network client, executor, or Agent runtime.
The enabled local registration is `nexus-r2-local`, with stdio and
`default_tools_approval_mode = "writes"`.

### Official terminology

Current official developer documentation calls the custom integration surface
**Plugins**: a package can contain skills, an optional MCP server, and optional
UI. This document uses “custom plugin/App” only as product language. It does not
assume a separate legacy “Apps SDK” is required. [Plugin architecture](https://developers.openai.com/plugins/concepts/plugins)

The official sources inspected did not establish a separate, mandatory standalone
Apps SDK path for Nexus. Its project status is **UNKNOWN / NOT DOCUMENTED AS
REQUIRED**; the documented plugin/MCP path is the reference.

## Official capability findings

| Capability | Status | Evidence and design consequence |
| --- | --- | --- |
| Desktop local MCP | **SUPPORTED** | Desktop, CLI, and IDE share MCP configuration on the same Codex host; Settings can add STDIO or HTTP servers and `/mcp` shows connections. Reuse R2 locally. [MCP](https://learn.chatgpt.com/docs/extend/mcp) |
| Local stdio | **SUPPORTED for local Codex-host clients** | A command starts the server; it is not a Web transport. [MCP](https://learn.chatgpt.com/docs/extend/mcp) |
| Web access to local config/localhost | **UNSUPPORTED** | Web does not read local configuration or expose the local command menu. Do not assume D: or localhost access. [MCP](https://learn.chatgpt.com/docs/extend/mcp) |
| Web custom remote MCP | **CONDITIONALLY SUPPORTED** | Hosted Work supports remote plugin tools. Developer-mode availability depends on account/workspace policy. [Connect and test](https://developers.openai.com/plugins/deploy/connect-chatgpt) |
| Production remote transport | **SUPPORTED with conditions** | Production MCP guidance specifies stable public HTTPS using streamable HTTP. Deferred. [MCP server](https://developers.openai.com/plugins/concepts/mcp-server) |
| Developer mode/private connection | **CONDITIONALLY SUPPORTED** | Settings → Security and login → Developer mode; account/workspace policy can block it. [Connect and test](https://developers.openai.com/plugins/deploy/connect-chatgpt) |
| App/plugin selection | **CONDITIONALLY SUPPORTED** | Developer mode can add a connection; a new chat adds it from the tools menu. Public distribution needs review/permissions. [Connect and test](https://developers.openai.com/plugins/deploy/connect-chatgpt) |
| Read tools | **SUPPORTED** | `readOnlyHint: true` is documented; R2 already has the equivalent intent. [Optimize metadata](https://developers.openai.com/plugins/guides/optimize-metadata) |
| Write tools | **CONDITIONALLY SUPPORTED** | Server validation and human confirmation are required for irreversible actions. R3 exposes no writes. [Security and privacy](https://developers.openai.com/plugins/guides/security-privacy) |
| OAuth for protected remote MCP | **EXPECTED** | Official authentication guidance expects OAuth 2.1/MCP authorization for an authenticated MCP server. [Authentication](https://developers.openai.com/plugins/build/auth) |
| Workspace/admin controls | **CONDITIONALLY SUPPORTED** | Web tool availability and developer mode can be policy controlled. [MCP](https://learn.chatgpt.com/docs/extend/mcp) |
| Plus/Pro/Business/Enterprise/Edu matrix | **UNKNOWN / NOT VERIFIED** | Inspected sources establish account/workspace policy dependence, not a stable exhaustive entitlement matrix for this account. |
| Literal `@Nexus` | **UNKNOWN / NOT DOCUMENTED** | No source reviewed documents this for a custom MCP connection/plugin. |
| Automatic invocation | **CONDITIONALLY SUPPORTED, NOT GUARANTEED** | Names, descriptions, schemas, and annotations influence tool choice; positive and negative prompts must be evaluated. [Optimize metadata](https://developers.openai.com/plugins/guides/optimize-metadata) |

## Target UX

| Model | Current possibility | Friction | Security/reliability | Maintenance | Decision |
| --- | --- | --- | --- | --- | --- |
| A. Explicitly select Nexus tool | Supported Desktop; conditional remote | Medium | Strong intent signal | Low local / medium remote | **Primary** |
| B. Supported app reference UX | `/mcp` Desktop or tools menu remote | Medium | Explicit boundary | Low / medium | **Use** |
| C. Automatic tool call | Conditional, not deterministic | Low | Needs continuous negative tests | Ongoing | Secondary only |
| D. Literal `@Nexus` | Unknown/not documented | Low if available | No contract | Unknown | Do not design around it |
| E. Dedicated plugin/App | Conditional | Higher | Needs remote auth/HTTPS | High | Future |
| F. Separate Web UI | Technically possible | Highest | Another auth/data surface | High | Reject |

### Recommended experience

1. In Desktop, enable `nexus-r2-local` in **Settings → MCP servers**.
2. In the composer, type `/mcp`, select Nexus, and request a task plan.
3. ChatGPT makes an applicable read-only R2 call; Nexus returns a bounded plan.
4. ChatGPT states whether Nexus was used and performs only separately supported,
   user-authorized follow-on work.

This is the closest safe present-day equivalent to “我在 ChatGPT 里面叫 Nexus，它就自动帮我选 Skills 来做。” It is deliberately explicit rather than making an unsupported literal-mention or auto-routing promise.

## Recommended architecture

### Primary: R3-E, local-only capability/planning projection

R3-E keeps Nexus local and exposes only the existing R2 safe projection to
ChatGPT Desktop through shared local MCP configuration. No remote projection is
created in this phase.

```text
User in ChatGPT Desktop
  -> explicit /mcp selection or validated tool choice
  -> local stdio JSON-RPC (no listener)
  -> Nexus R2: opaque workspace ID, guards, budgets, redaction
  -> frozen Nexus V1.2/R1 planner
  -> versioned safe plan/error
  -> ChatGPT host independently decides follow-on work
```

### Request flow and trust boundaries

1. The user enables/selects the local server; Desktop starts the configured child process.
2. The host calls health, metadata discovery, or bounded planning.
3. Planning accepts a small task, constraints, context mode, and opaque workspace ID; never a path.
4. R2 resolves only an allowlisted ID, reads fixed governance context, selects and validates bounded Skills.
5. It emits selected identity/load evidence, validation intent, and explicit fallback state; it omits instructions, paths, rules, candidates, scores, and secrets.
6. A plan is not execution authority. The host retains all file, command, artifact, test, and user-communication authority.

User task text and project/Skill content are untrusted. Local policy and the private workspace allowlist are trusted control inputs. Raw Skills, files, environment values, and credentials do not cross the local boundary.

### Architecture options

| Option | Attack surface / operating cost | Decision |
| --- | --- | --- |
| R3-A: thin remote MCP gateway → local planner | New forwarding channel, replay/liveness coupling, and Windows-adjacent privilege risk | Reject as primary |
| R3-B: custom plugin/App → bounded remote MCP | HTTPS, OAuth when protected, abuse controls, observability, review, and a remote projection required; initial scope is MCP-only with no component UI | **Deferred Web successor** |
| R3-C: remote gateway ↔ local bridge | Highest local compromise risk and credential/channel complexity | Reject |
| R3-D: restricted planner remotely | Avoids local reachability but needs signed projection and drift controls | Only a component of R3-B |
| R3-E: local R2 projection to Desktop | No new network surface; same-host only | **Select** |

### Fallback and deferred designs

- **Fallback:** accepted R1 `scripts/nexus.py plan … --handoff`, or labelled native host reasoning. Never imply Nexus succeeded when it did not.
- **Deferred:** R3-B with a newly approved remote read/plan-only service. It has no Windows-local reachability and begins only after explicit approval of data, hosting, identity, domain, OAuth, cost, and tests.

## Local versus remote boundary

Desktop can launch the configured stdio server on the same host; no public endpoint
or OAuth is introduced. Web cannot use `config.toml`, localhost, or this project
path. A Web plugin needs remote HTTPS or, for developer testing only, a Secure MCP
Tunnel. A tunnel does not replace the public HTTPS endpoint required for a
submitted plugin. [Connect and test](https://developers.openai.com/plugins/deploy/connect-chatgpt)

No tunnel, reverse proxy, relay, or bridge is created. Any future remote component
must be a new constrained service with no Windows credentials and no capability to
request arbitrary local files or commands.

The initial future R3-B surface is MCP-only and has no component UI. Any future UI is separately scoped and must cover origin isolation, strict CSP, iframe/message validation, safe rendering of untrusted text, and user consent for tool calls; it inherits no approval from this document.

## Authentication and authorization

### Primary R3-E local Desktop model

- **Caller identity:** the same local OS-user/ChatGPT Desktop process that the user explicitly configured. This is a same-OS-user trust boundary, not cryptographic caller attestation or malware/local-user isolation.
- **Workspace identity:** opaque R2 `workspace_id`, resolved only from the private local allowlist. Tool input never contains a filesystem path.
- **Authority:** read/plan-only; no write, execution, installation, spawning, or resource enumeration beyond the three bounded tools.
- **Tokens:** no R3 token, OAuth secret, browser token, or service account is introduced or persisted.
- **Revocation:** disable/remove the server in Desktop/Codex configuration or remove the workspace from the private allowlist, then restart the local client.
- **Audit:** safe local events retain only request ID, tool, outcome, duration, and safe selected IDs.

R3-E therefore requires configuration and executable integrity: absolute approved command paths, user-ACL protection of the private configuration/allowlist, and release hash/provenance checks. It must be acceptance-tested against direct same-user process invocation and configuration/command substitution. It is not suitable as a defense against code already executing under the same Windows identity.

### Future R3-B remote model

An anonymous metadata-only service may be possible in general, but Nexus must not make a remote endpoint anonymous if it accepts task text, user settings, or workspace-specific data. Protected remote MCP needs OAuth 2.1/MCP authorization: protected-resource metadata, authorization-server metadata, PKCE, and access-token verification are the documented design. [Authentication](https://developers.openai.com/plugins/build/auth)

Required controls are short-lived audience-bound access tokens; tenant/workspace authorization on every call; scopes such as `plan:read` only (never filesystem or shell scopes); static client registration; an exact pre-registered redirect-URI allowlist; PKCE `S256` only; no dynamic redirect URI; state/nonce, rotation, revocation, rate limits, and a bounded replay-detection window. The server rejects scope, audience, client, and redirect mismatch and never forwards user tokens downstream. Tokens never appear in source, prompts, tool output, URLs, or logs. Service credentials are vault-backed, least-privileged, independently rotated, and never the user's ChatGPT session token.

## Privacy model

| Data class | Local R3-E | Future R3-B default | Tool result allowed? |
| --- | --- | --- | --- |
| Safe capability metadata | Bounded local metadata | Signed/curated projection only | Yes, bounded |
| Skill identity/hash | Selected ID/name/hash/load status | Same only when necessary | Yes, bounded |
| Task text | Local bounded processing | Send only when remote plan is explicitly invoked | Summary only |
| Project context | Fixed local governance context | Do not send initially | No raw content |
| Raw `SKILL.md` | Guarded local read after selection | Never mirror/send by default | No |
| Secrets/credentials | Never read/output | Never accept/store/output | No |
| Local filesystem metadata | Opaque workspace ID only | Never send path/structure | No |

The plan must not contain raw instructions, rules, candidate scores, hidden reasoning, paths, environment values, or tracebacks. Nexus-controlled telemetry/storage retention is zero by default. ChatGPT conversation handling remains governed by the applicable ChatGPT account/workspace policy, not Nexus. A future R3-B flow must visibly disclose before invocation that necessary task text will cross to the remote planner. If operational telemetry is enabled later, store only redacted fields under an explicit retention/deletion policy. This matches official least-privilege, minimization, consent, and redacted-logging guidance. [Security and privacy](https://developers.openai.com/plugins/guides/security-privacy)

Any future signed/curated remote projection needs a complete trust contract: a signed manifest binds canonical source identity, immutable content digest, schema version, signing-key ID, and expiry. Verification checks the trusted key set plus key rotation/revocation status and fails closed on altered content, expiry, revoked key, or schema downgrade.

## Skill execution model

| Stage | Local R3-E Desktop | Future Web plugin | Boundary |
| --- | --- | --- | --- |
| Nexus knows a Skill exists | Yes, bounded discovery | Safe, intentionally published metadata only | No raw content |
| Nexus selects a Skill | Yes, frozen V1.2 logic | Only an approved versioned equivalent/projection | No semantic drift |
| Nexus loads `SKILL.md` | Yes, locally and guarded after selection | Never from this Windows machine | Raw instructions stay local |
| Nexus returns safe guidance | Yes | Yes, bounded schema | Redaction required |
| ChatGPT follows guidance | Conditional on host capabilities | Conditional on host capabilities | Not local execution |
| Local Codex executes work | Separate local authority only | Never through Web plugin | No remote control channel |

Thus a remote plugin can truthfully help with bounded planning and published capability metadata, but cannot claim direct execution of arbitrary local Codex Skills. R1/R2 remain local authority and native fallback remains available.

## Threat model and testable invariants

| Threat | Mitigation | Testable invariant |
| --- | --- | --- |
| Remote caller impersonation | No remote caller in R3-E; OAuth issuer/audience/token checks in R3-B | Invalid, expired, or wrong-audience token never reaches planner |
| Prompt injection/task text | Treat all task text as data; fixed schemas and policy precedence | Injection cannot widen tools, workspace, context, or output fields |
| Malicious project content | Fixed context allowlist and redaction | Caller-named files, README/source comments, and unapproved paths are not read |
| Malicious/poisoned Skill | Provenance/hash/load guards; Skill never grants authority | Skill text cannot enable commands, network, installs, Agents, or export |
| Skill changes after index | Guarded read and changed-file check | Changed selected file fails closed |
| Data exfiltration | Output allowlists, redaction, no raw logs | Secret sentinels never occur in output/telemetry |
| Filesystem escape | Opaque IDs, canonical roots, no reparse points | Traversal, UNC/device, symlink/junction, drive/home root fail closed |
| SSRF | R3-E has no HTTP client; future service egress allowlist | Input cannot fetch arbitrary URLs/metadata |
| Command injection | No execution tool or subprocess interface | Command-like task input cannot launch a process |
| OAuth/token theft | HTTPS, OAuth 2.1/PKCE, redacted logs | No token in URL, error, tool result, or log |
| Replay | Future request IDs, expiry, nonce/state, idempotent reads | Replay is rejected or safely deduplicated |
| DoS/excessive tools | Input/context/catalog/output/time caps and per-identity rate limits | Oversize/burst traffic yields bounded safe errors |
| Cross-workspace access | Server-side authorization every call | Tenant A cannot enumerate or plan tenant B |
| Remote-to-local escalation | Reject R3-C; no listener/bridge | No network peer can instruct the Windows host |
| Compromised gateway | Future projection has no local path, credentials, or remote control | Gateway compromise cannot read D: or run shell |
| Dependency compromise | Pin/review/lock/SBOM before a later install | Unreviewed artifact change cannot enter release |

Host-facing fields derived from task text, project context, or Skill content are never authority. Results use a strict allowlisted schema; any explanatory free text is labelled untrusted content and cannot trigger a follow-on tool. Sentinel-injection tests must prove it neither appears as an imperative host instruction nor causes action.

Security policy outranks task text, ChatGPT instructions, project content, Skill instructions, and metadata. Tool metadata aids routing but never authorizes action. Official guidance explicitly assumes prompt injection and malicious inputs reach servers and requires server-side validation and defense in depth. [Security and privacy](https://developers.openai.com/plugins/guides/security-privacy)

## Deployment options

| Target | Cost/complexity | Security/maintenance | Windows-local implication | Decision |
| --- | --- | --- | --- | --- |
| Local Desktop stdio | Existing cost; lowest complexity | No network listener; local config hygiene | Same-host only | **Recommended now** |
| Local companion + tunnel/bridge | Low infrastructure, high security complexity | Durable remote-to-local channel is high risk | Windows-adjacent attack surface | Reject |
| Small VPS/container | Low-medium cost, medium operations | TLS, patching, OAuth, secrets, monitoring needed | Host projection, never local state | Possible R3-B |
| Managed container/serverless | Variable cost, medium complexity | Still needs identity, abuse, egress, observability | No local access | Possible R3-B |
| Private cloud | Higher cost/governance | Strong tenancy, higher operations | No local access | Defer |
| Tunnel/worker architecture | Low initial cost, high boundary complexity | Developer test only if separately approved | Does not authorize local access | Not R3 |

## Failure and fallback contract

| Condition | Required response | Host behavior |
| --- | --- | --- |
| Nexus unavailable/offline | `NEXUS_UNAVAILABLE`, no partial plan | State Nexus was not used; explicit native/R1 fallback only |
| Authorization failure | `UNAUTHORIZED_WORKSPACE` without data | Do not reveal IDs or retry with guesses |
| Skill unavailable/ambiguous | `SKILL_LOAD_FAILED` or invalid evidence | Exclude it; report fallback status |
| Planner timeout/failure | Bounded safe error | Do not present stale data as current |
| App unavailable by policy | UI unavailable | Desktop `/mcp` where supported, else R1/native fallback |
| Future remote/local version mismatch | `UNSUPPORTED_VERSION` | Refuse semantic execution; show safe supported versions |

## Version and compatibility contract

R3 must not couple any future remote client to Nexus internal Python classes. Preserve R2 as an adapter over V1.2 and expose only a versioned envelope, for example:

```json
{
  "schema_version": "nexus.chatgpt.plan.v1",
  "protocol_min": "1.0",
  "protocol_max": "1.x",
  "server_capabilities": ["health", "discover_capabilities", "plan_task"],
  "status": "passed|fallback_needed|error",
  "request_id": "opaque-id"
}
```

Future rules: only additive optional fields within a major schema version; negotiate compatibility before calls; incompatible versions fail closed; tool schemas, annotations, redaction, and selected-Skill evidence are regression-tested contract artifacts; no remote release silently changes local V1.2 ranking, selection, or loading semantics.

## Privacy-preserving observability

Allowed fields are request ID, schema version, tool, policy result, safe selected capability/resource IDs, status/error code, duration, and coarse rate-limit outcome. Do not persist raw task text, project context, Skills, absolute paths, tokens, environment values, hidden reasoning, or full arguments/results by default. Redaction runs before persistence; telemetry is off or local-only until a retention/deletion policy exists.

## Exact `@Nexus` finding

**Classification: UNKNOWN / NOT DOCUMENTED.** The official evidence documents `/mcp`, a tools menu, developer-mode connection creation, and metadata-driven selection. It does not document literal `@Nexus` for a custom Nexus MCP connection/plugin. R3 must not market or test it as a requirement. The closest supported UX is explicit selection followed by “Use Nexus to plan this task.”

## Automatic invocation finding

**Classification: CONDITIONALLY SUPPORTED, NOT GUARANTEED.** Metadata drives when ChatGPT/Codex considers a tool relevant, and official guidance requires direct, indirect, negative, and boundary prompt testing whenever metadata changes. [Optimize metadata](https://developers.openai.com/plugins/guides/optimize-metadata), [Connect and test](https://developers.openai.com/plugins/deploy/connect-chatgpt)

This differs from R1's local `AGENTS.md` activation policy: R1 is project-local policy, while ChatGPT selection is host/model behavior plus workspace policy. R3 can improve metadata and evaluate it, but explicit selection is the dependable path.

## Nexus Skill Scout — future extension only

Skill Scout is not an R3 tool, runtime, installer, or permission grant. It is a future recommendation workflow:

```text
Capability gap
  -> approved-source search
  -> real SKILL.md/package validation
  -> relevance and workflow-quality review
  -> Codex/Nexus compatibility and dependency analysis
  -> security, maintenance, license, duplication review
  -> ranked candidates with evidence
  -> human recommendation/approval
  -> separately authorized controlled installation
  -> re-index and routing validation
```

Ranking priority is: (1) task relevance, (2) Skill/workflow quality, (3) Nexus/Codex compatibility, (4) security, (5) maintenance activity, (6) license, (7) dependency burden, (8) community adoption, and (9) stars/forks only as a secondary signal. Popularity never overrides an unsafe dependency, missing/poisoned Skill structure, incompatible license, or failed compatibility review.

Defenses require allowlisted sources/owners; canonical repository/release identity; tagged-release preference and commit pinning; typo-squatting/name-confusable checks; activity/ownership-change assessment; dependency-lock/install-script inspection; sandboxed compatibility tests; duplicate detection; license verification; and prompt-injection review of instructions. Repo takeover, star manipulation, abandonment, dependency confusion, unbounded installer, or unexpected command/network request is reject-or-escalate. Skill Scout never installs, updates, executes commands, or changes routes automatically.

## Future implementation phases

### R3-0 — Desktop local validation

- No code change until the intended account/workspace confirms the documented Desktop MCP UI and `/mcp` behavior.
- Validate health, capability discovery, and one authorized plan; verify redaction and native fallback.
- Maintain direct, indirect, negative, malformed, injection, and unavailable-server golden prompts.

### R3-1 — Remote feasibility gate

- Decide whether cross-device/Web value justifies a service, privacy policy, domain, hosting cost, authorization ownership, and support/incident responsibilities.
- Approve one data classification, schema, tenant model, rate limit, OAuth issuer, retention policy, and deletion path.
- Reject Windows bridge/tunnel designs unless an independent high-assurance review approves a materially different trust model.

### R3-2 — Bounded remote plugin implementation

- Build a new remote read/plan-only MCP backend from a minimal versioned projection; it must not import a Windows path or invoke the local R2 process.
- Implement OAuth 2.1 only when protected identities/data exist; otherwise keep the least-privileged documented model.
- Test in developer mode; do not submit/publish without a public endpoint, review artifacts, organization verification, and permissions.

### R3-3 — Controlled release

- Run security, privacy, red-team, compatibility, load, and negative-routing acceptance tests.
- Create a separately named integration release only after approval; never change V1.2 or R2 frozen tags.

## Future test plan

| Area | Required acceptance evidence |
| --- | --- |
| Connectivity | Desktop stdio lifecycle, direct same-user invocation, command/config substitution; future plugin HTTPS discovery/connect; no localhost/Web assumption |
| Authentication | OAuth success, wrong issuer/audience/client/scope, expiry, revocation, PKCE/state/nonce, redirect substitution, authorization-code replay, and token query/error/log leakage |
| Authorization | User/tenant/workspace allow/deny and no cross-workspace enumeration |
| Tool invocation | Direct, indirect, negative, and near-miss prompts with selected tool/arguments recorded |
| Planning | Schema-valid plan, selected Skill load evidence, explicit fallback, no execution authority |
| Redaction | Secret sentinels in task/context/Skill/logs absent from output and telemetry |
| Injection | Prompt/project/Skill injection cannot alter policy, tools, context, schema, host-facing authority, or follow-on tool choice |
| Failure | Offline server, App absence, timeout, bridge absence, mismatch all fail closed |
| Versioning | Older/newer client/schema negotiation and incompatible feature refusal |
| Abuse | Rate limits, concurrency, oversized inputs, replay, DoS resource bounds |
| Compromise | Altered/expired/revoked-key/downgraded signed projection, poisoned Skill, dependency change, and gateway compromise cannot reach local host |
| Review | Metadata annotations match behavior; privacy, retention, and review artifacts complete |

## Review record

### Architecture review

The design reuses R2 instead of duplicating the V1.2 planner or parsing R1 stdout. Web/cross-device support is identified as a separate product/service rather than a configuration toggle.

### Security and privacy review

The core weakness of a remote-gateway-to-local design is transforming an advisory planner into a Windows-adjacent remote service. R3-E removes that category. R3-B remains a constrained remote projection with no local reachability or command/filesystem capability.

### Official-capability accuracy review

Claims are limited to current official evidence: shared Desktop local MCP configuration, Web remote plugin tools, account/workspace policy conditions, stable HTTPS remote production requirements, metadata-driven selection, and OAuth expectations for protected MCP. No entitlement, literal-mention, or guaranteed auto-invocation claim is made where documentation is absent.

### Scope and overengineering review

R3-E adds no software, service, tunnel, credential, deployment, package, database, vector store, multi-agent runtime, or execution capability. It is less magical than literal `@Nexus`, but is the smallest documented and defensible experience.

## Open questions requiring later human/account evidence

1. Does the intended ChatGPT Desktop account/workspace expose the documented MCP settings and `/mcp` UI at adoption time?
2. Is explicit-select local UX sufficient, or is remote cross-device access a separately approved product requirement?
3. If remote, who owns the domain, hosting budget, privacy policy, OAuth issuer, verification, support, incident response, and deletion path?
4. What safe capability metadata can be published without exposing private Skill/project information?
5. Is public directory publication desired, or only private/workspace developer-mode use?

## Official sources

- [Model Context Protocol — ChatGPT Learn](https://learn.chatgpt.com/docs/extend/mcp) — local/Desktop, Web separation, setup, transport, auth, and approval controls.
- [Plugin architecture — OpenAI Developers](https://developers.openai.com/plugins/concepts/plugins) — skills/MCP/UI and smallest-shape principle.
- [MCP server concept — OpenAI Developers](https://developers.openai.com/plugins/concepts/mcp-server) — tool lifecycle, streamable HTTPS, and authorization boundary.
- [Build an MCP server — OpenAI Developers](https://developers.openai.com/plugins/build/mcp-server) — controlled tools and server instructions.
- [Authentication — OpenAI Developers](https://developers.openai.com/plugins/build/auth) — anonymous read-only distinction and OAuth 2.1/MCP authorization.
- [Connect and test your plugin — OpenAI Developers](https://developers.openai.com/plugins/deploy/connect-chatgpt) — developer mode, endpoint/tunnel conditions, and evaluation.
- [Security and privacy — OpenAI Developers](https://developers.openai.com/plugins/guides/security-privacy) — least privilege, consent, validation, logging, and injection.
- [Optimize metadata — OpenAI Developers](https://developers.openai.com/plugins/guides/optimize-metadata) — selection metadata, negative prompts, and read-only annotations.
- [MCP server review requirements — OpenAI Developers](https://developers.openai.com/plugins/deploy/app-review) — production endpoints, private/developer mode, verification, and review metadata.
