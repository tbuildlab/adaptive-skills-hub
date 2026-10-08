# Nexus G3 Phase 1 — Reuse-First Survey and Minimum Architecture v1

Date: 2026-10-08 (Asia/Kuala_Lumpur). Status: **G3_REUSE_SURVEY_COMPLETE**.
Architecture proposals below are **INFERRED / PROPOSED**, not implemented or
Owner acceptance of a new approval issuer, storage security boundary, or executor.

## 1. Objective and controlling direction

G3 answers: **Is this exact capability approved for use in this exact Nexus
context?** Host/provider connection and Nexus capability authorization are
independent. OAuth, installation, discovery, account access, a visible tool,
scanner PASS, registration, and executor suitability cannot create Nexus approval.

**REUSE FIRST. BUILD ONLY THE GAP. NO ROUTINE OWNER INTERRUPTIONS.
AUTONOMY DOES NOT CREATE AUTHORITY.** This authorization covers Phase 1 survey,
architecture, documentation and local documentation validation only. Phase 2,
provider access, installation, push, merge, tag, freeze and release are excluded.

Survey order followed: A existing Nexus; B OpenAI/Host; C plugins/connectors;
D MCP; E existing SDK/runtime/provider; then minimum Nexus gap. Repository facts
were inspected before external research. No ecosystem candidate was adopted.

## 2. Accepted G2 starting state and repository checkpoint

| Item | Starting evidence / meaning |
|---|---|
| G2 status | `G2_OPENAI_MANAGED_E2E_VERIFIED`; `G2_OPENAI_MAINLINE = COMPLETE_FOR_DECLARED_MANAGED_CONFIGURATION` |
| Self-hosted / production binding | `SELF_HOSTED_G2 = DEFERRED`; `PRODUCTION_POSITIVE_HOST_BINDING = ABSENT` |
| Exact baseline | `5f2803f3581a5795232240490bb433a14ed3d0c5` |
| Baseline agreement | Initial local HEAD and cached `origin/nexus-v2-g2-development` both resolve to that commit. No fetch or remote-server verification was performed. |
| Working branch | New local `nexus-v2-g3-development`, created directly from the baseline; no G3 commit or remote push |
| Static integrity | Baseline MANIFEST verified: 324/324 LF-normalized byte/hash subjects |
| Historical provider executions | 3, recorded in the accepted v3 closure; new executions in this phase: 0 |
| Historical drafts | Exactly three initial untracked Route D successor-custody drafts; hashes recorded in section 24; preserve unchanged and uncommitted |

The current [structured v3 closure](nexus-g2-openai-structured-v3.md), especially
“Real v3 acceptance and mainline closure,” controls the declared managed route.
The [Roadmap V2 G3 contract](nexus-roadmap-v2.md#g3--separate-capability-authorization)
and [Pre-G3 logical design](nexus-pre-g3-pre-g4-contract-and-qualification-design-v1.md)
remain useful constraints. Their historical G2 HOLD/NOT STARTED statements and
older sprint reports remain historical; this document does not rewrite them.
Managed G2 closure does not resolve the earlier approval-origin obligation or
qualify hostile same-user storage, a whole Host, or a general remote capability.

## 3. Evidence conventions and research boundary

- **OBSERVED:** inspected current source, local metadata, Git refs or hashes.
- **DOCUMENTED:** official documentation fetched during this survey. This proves
  a documented contract, not availability in this account or installed runtime.
- **INFERRED:** architecture conclusions derived from those sources; proposals
  are explicitly identified and require implementation/review later.
- **UNKNOWN:** current evidence cannot establish the claim. Unknown authority
  cannot become eligibility through a fallback or a model interpretation.

All external sources below were checked on **2026-10-08**. Research used public
documentation retrieval only. No Responses call, hosted execution, paid provider
operation, credential inspection/use, new connection, resource creation or purchase
occurred. Tool metadata available to this chat is a current surfaced subset; it
does not establish global inventory, private account identity or Nexus CLI access.

## 4. A — Existing Nexus: primitives to reuse

The following table records **OBSERVED** source mechanisms at the G2 baseline.
Function names are lookup anchors; none was invoked as an executor in this phase.

| Existing primitive | Evidence anchor | Reuse and exact limitation |
|---|---|---|
| Heterogeneous capability IDs, types, source provenance, commit/content digest, lifecycle, permissions, execution mechanisms | `ash/capabilities.py`: `validate_capability`, `_validate_provenance`, `updated_revision_state`, `select_minimum_sufficient_capabilities`; `config/capability-foundation.json` | Reuse logical IDs and catalog validation. Changed repository/commit/hash quarantines prior approved metadata. Historical `approved`/`available` metadata has no authenticated issuer, independent durable approval, expiry or revocation service; do not import it as a G3 grant. |
| Immutable source/revision/tree/component identities, canonical bytes, bounded parser | `ash/ecosystem_models.py`: `source_identity`, `build_revision_identity`, `build_component_revision_identity`, `parse_json_bytes`, `canonical_json_bytes` | Reuse existing exact identities and serializers. `typed_id`/`domain_sha256` are closed ecosystem domains; do not pass invented G3 domains or edit frozen domains to fit. G3 can use its own small envelope over canonical bytes. |
| Quarantine, review evidence, intake-policy identity and lineage | `ash/ecosystem_bridge.py`: `_revalidate_revision_subject`, `load_state_lineage`, `append_state_transition`; `ash/ecosystem_evidence.py` | Consume validated subject/policy/evidence references. Keep immutable Slice 3C states and `zero_authority` unchanged. Review PASS is evidence, never approval. Source-policy coverage is bounded; uncovered adoption needs a separate successor intake boundary. |
| G1 model/Host profiles and executor conformance | `ash/g1_profiles.py`: `model_profile`, `host_profile`, `candidate`, `binding_digest`, `conformance`, `TrustedObservations` | Reuse provider/model/deployment/configuration identity and current technical facts. Process-local observation seals establish scoped evidence in trusted Python, not human approval origin or durable cross-process authority. |
| G1 policy intersection, task suitability, expiry/freshness, deterministic reason codes | `ash/g1_selection.py`: `select_capabilities`; `ash/g1_profiles.py`: `fresh` | Keep existing mandatory controls and ranking. A SELECTED decision grants zero authority. G3 adds independent approval checks; it does not replace G1 with another general policy engine. |
| Skill discovery, duplicate resolution, applicability and validation | `ash/discovery.py`: `_resolve_duplicates`, `discover_skills`; Slice 3A/3B contracts | Reuse provenance, ambiguity refusal and reviewed applicability. Do not let an unapproved instruction/script enter a trusted execution pool merely because discovery found it. |
| Host inventory tickets, canonical provider/capability mapping, freshness and execution-start binding | `ash/mcp/host_inventory.py`: `approved_mapping_identity`, `snapshot_digest`, `claim_inventory_bound_execution_start`, `validate_inventory_bound_host_receipt`; `ash/mcp/host_mapping.py` | Reuse exact tuple and receipt binding. Existing mapping approval is descriptive accepted mapping metadata, not a generic G3 Owner decision. Current-turn subset is not global discovery. |
| Workspace authorization and stable file guards | `ash/mcp/authorization.py`: `WorkspaceAuthorizer.resolve`, `guard_regular_file`, `verify_unchanged` | Reuse startup workspace ID-to-root mapping and reparse/path checks. Workspace access is narrower and different from capability approval; it does not authenticate the Owner. |
| Core trusted hook closure and per-task approval | `ash/core.py`: `_catalog`, `prepare_task`, `_dispatch`; `ash/core_profiles.py`: `prepare_project`, `verify_scope`, `approval_summary` | Reuse catalog/script/interpreter/input/baseline checks and task grant. Accepted internal Core is a closed same-user trusted-hook path, not a new external-capability approval store. |
| G2 managed request/receipt, scope, deadlines, checkpoints, lock and owner boundary | `ash/managed_execution.py`: `ExecutionCapability`, `ExecutionRequest`, `route_backend`, `_scope`, `export_handoff`, `parse_receipt`; `ash/core.py`: `_atomic`; `ash/core_host.py`: `exclusive_run` | Reuse existing execution contracts and conservative recovery. Checksums detect corruption; the caller-supplied request digest does not authenticate an issuer. A task grant is separate from reusable capability approval. |
| Managed OpenAI identity, byte closure, one-dispatch custody and original-result import | `ash/openai_hosted.py`: `_source_digest`, `prepare_openai`, `OpenAIHostedExecutionBackend.submit`; `ash/openai_structured.py`, `ash/openai_import.py`, `ash/openai_reconciliation.py`, `ash/openai_staging.py` | Keep reviewed model/configuration, original request/response and independent acceptance. `_source_digest` covers nine adapter/Core source files. Request binding also includes exact Nexus/project baselines and provider config. None is a universal remote-service implementation attestation. |
| Existing planner plugin and MCP invocation contract | `plugins/nexus-desktop/.codex-plugin/plugin.json`, `.mcp.json`; `ash/mcp/server.py`, `ash/mcp/adapter.py` | Existing plugin declares read/planning/handoff behavior and nine tools; it does not install/authenticate/adopt arbitrary tools or execute a plan. Keep that boundary. |
| Local manifest and regression facilities | `scripts/build_manifest.py`; `tests/g1_fixtures.py`; `tests/test_capability_foundation.py`, `tests/test_ecosystem_policy_models.py`, `tests/test_mcp_authorization.py`, `tests/test_core.py`, `tests/test_openai_hosted.py`, `tests/test_managed_execution.py` | Reuse canonical golden vectors, temporary fixtures, synthetic `FixtureHTTP`, clocks, scope/refusal and package checks. No new G3 suite is implemented here. |

Repository survey result: **INFERRED — a general separate G3 authorization plane
is absent** from the inspected baseline. Approval-like primitives already exist,
so the gap is not basic IDs, discovery, routing, hashing, transport or per-task
execution consent. The missing composition is independently originated,
scope-bound, reusable approval plus authoritative revocation and current-use checks.

## 5. B — OpenAI / Codex / ChatGPT Work / Host

| Source (official, checked 2026-10-08) | DOCUMENTED capability | Limitation relevant to Nexus |
|---|---|---|
| [Host MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) | Local STDIO and HTTP MCP, bearer/OAuth, configured tool filters and approval policy; connected/enabled/authentication views | Host configuration/connection state does not provide a durable, exact-subject Nexus approval receipt. A surfaced tool is not automatically callable by the standalone Nexus CLI. |
| [Plugin authentication](https://developers.openai.com/plugins/build/auth) | Host OAuth client flow; provider/server token checks; stable opaque authenticated profile identity contract | Reuse Host/provider authentication. Profile identity must be independently supplied by validated credentials; model-supplied IDs and labels do not prove the connected account. Actual profile exposure to a Nexus bridge is UNKNOWN. |
| [Agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) | Host sandbox/approval mechanisms and configurable prompt categories | These govern Host actions. No examined contract establishes the exact G3 subject/scope/revocation receipt or makes Host auto-review the Owner's delegated G3 issuer. |
| [Workspace connections](https://learn.chatgpt.com/docs/enterprise/shared-connections) | Admin-authorized company accounts, provider resource/action permissions and connection lifecycle | Availability depends on workspace/surface. Disabling a connection does not replace provider authorization revocation. Neither event revokes a Nexus approval automatically without a separately specified G3 decision. |
| [Codex App Server](https://learn.chatgpt.com/docs/app-server) | Client-handled approval requests; turn/session network/filesystem permission grants; MCP server/tool/auth status; connector action approvals | A promising existing interaction/status bridge. Its documented operation approvals and permission subsets do not establish a protected durable Nexus subject grant or authenticate an arbitrary client response as an Owner decision. No local app-server was started or connected. |
| [OpenAI platform permissions](https://developers.openai.com/api/docs/guides/rbac) | Organization/project roles, resource/API permissions and key access controls | Reuse provider-side restrictions. They govern platform access, not the exact Nexus component/task subject; do not mirror this RBAC system inside G3. Account settings were not inspected. |

Credential custody remains with the Host/provider for their connections. G3 stores
only non-secret identity/evidence references. The existing direct G2 adapter has
its own admitted runtime credential path, which G3 does not move or duplicate.
Exact custody protections, exportable grant evidence and account access in this
installation are **UNKNOWN / NOT INSPECTED**. No secret store was opened.

## 6. C — Plugins and connectors

| Source (official, checked 2026-10-08) | DOCUMENTED ownership | Nexus limitation |
|---|---|---|
| [Plugins on supported surfaces](https://learn.chatgpt.com/docs/plugins) | Discovery, installation, bundled Skills/MCP, connecting a service; features vary by surface | Package presence is not approval of all bundled tools, scripts, accounts or effects. This account's complete installed/connected catalog was not inspected. |
| [Package your plugin](https://developers.openai.com/plugins/build/plugins) | Manifest metadata and MCP packaging; plugin-scoped enablement, tool policy and reviewed hook trust | Metadata/version/name are inputs to identity resolution, not immutable implementation proof. Refresh can alter package bytes; Nexus must validate the exact reviewed component. No new installer is needed. |
| [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server) | Tool schemas, structured results, auth integration, behavior annotations and invocation contract | Annotations assist Host behavior; server authorization remains separate. G3 cannot infer read-only authority solely from a tool hint. |

The local Nexus plugin manifest/configuration was **OBSERVED** in section 4.
Chat-surfaced plugin tools provide callable contracts within this Host turn, not
an authenticated general Nexus adoption/approval bridge. No such bridge was
established by this survey. Reuse connection/credential lifecycle; add only the
Nexus decision binding. No connector account was queried or changed.

## 7. D — MCP

Current researched protocol revision: **2026-07-28**. Do not assume a particular
Host or the pinned Nexus SDK implements every feature of that revision.

| Source (official, checked 2026-10-08) | DOCUMENTED mechanism | Exact limitation |
|---|---|---|
| [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28) and [base protocol](https://modelcontextprotocol.io/specification/2026-07-28/basic) | JSON-RPC, stateless self-contained requests, per-request metadata/capability negotiation, version compatibility | Protocol metadata is not human approval or unique authenticated server identity. Do not equate transport continuity with task/session authority. |
| [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | `tools/list`, input/output schemas, `tools/call`, paginated discovery and tool-list changes | Tool names are server-scoped and case-sensitive; server names need not be unique. Annotations are untrusted unless the server is trusted. Schema equality cannot prove implementation equality. |
| [Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources) | Resource URIs/templates and retrieval contracts | A URI identifies a resource location/contract, not necessarily immutable content, account scope or an approval subject. Bind content separately when it affects behavior. |
| [HTTP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) | Provider authorization discovery and token/resource authorization contract | OAuth protects resource access; it does not answer Nexus task approval. STDIO uses its launch/process boundary rather than HTTP OAuth. |
| [Historical 2025 lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) | Initialize-based capability negotiation, `serverInfo`, connection lifecycle in older revision | Historical compatibility reference only. Do not design a new generic handshake or apply old session assumptions to current stateless metadata. |

Reuse the existing client/Host transport and protocol adapters. Resolve a tool
using the authenticated provider/server binding plus exact action name, not a
global name registry. Refresh/revalidate execution-relevant metadata; list-change
notifications help invalidate a cache but their absence never proves freshness.
No new MCP registry, transport, proxy, protocol or account system is justified.

## 8. E — Existing SDK, runtime and provider mechanics

| Existing source | Evidence / grade | Decision and remaining gap |
|---|---|---|
| Pinned Python MCP SDK | OBSERVED `requirements-r2-mcp.txt` / lock: `mcp==2.0.0`, `mcp-types==2.0.0`; [official Python authorization guide](https://py.sdk.modelcontextprotocol.io/run/authorization/) checked 2026-10-08 | REUSE protocol/server primitives. SDK supplies HTTP auth plumbing but relies on a token verifier and existing authorization server; STDIO/in-memory use does not gain HTTP authentication. Installed runtime and newest SDK parity were not measured. |
| TypeScript MCP SDK | DOCUMENTED [2026 protocol migration](https://ts.sdk.modelcontextprotocol.io/v2/migration/support-2026-07-28), checked 2026-10-08 | DEFER language/runtime migration. Existing SDKs handle version-dependent discovery/server metadata and subscriptions; no custom implementation needed merely for this survey. |
| OpenAI official SDKs | DOCUMENTED [SDKs and CLI](https://developers.openai.com/api/docs/libraries), checked 2026-10-08 | DEFER transport replacement. Existing G2 standard-library transport already covers its declared workflow. An SDK would not establish Nexus Owner approval. |
| OpenAI SDK human review | DOCUMENTED [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals), checked 2026-10-08: sensitive tool-call review and paused-run continuation | DEFER runtime migration; reuse such an existing review surface if already selected later. Run/tool approval plumbing does not itself establish this installation's protected reusable G3 subject record, review origin or revocation store. No SDK run was created. |
| Nexus parser, hashes, JSON, atomic writes and exclusive lock | OBSERVED section 4 source | REUSE bounded parsing and persistence mechanics. They detect integrity/state faults, not issuer authenticity or hostile-writer rollback. |
| Existing provider/Host account and credential service | DOCUMENTED sections 5–7 | REUSE existing authentication and custody. UNKNOWN whether a protected, exportable Owner decision channel can serve G3. Do not implement OAuth/vault to conceal that uncertainty. |

No remaining Phase 1 mechanical need justifies a new dependency. A closed Nexus
eligibility predicate can reuse current Python validation. Universal IAM/policy
libraries are NOT_NEEDED for the concrete scope; they cannot supply a trusted
Owner decision without a trust root. Signature verification libraries, if a
future accepted issuer needs them, must be reused rather than invented; selecting
an issuer/key service or installing anything is deferred.

## 9. Explicit REUSE / BUILD_GAP / DEFER / NOT_NEEDED / UNKNOWN table

Each row has exactly one classification. BUILD_GAP identifies a proposed domain
gap after A–E; it is not authorization to implement it in this phase.

| Capability / mechanism | Existing source | Evidence | Decision | Nexus gap |
|---|---|---|---|---|
| OAuth and provider login | Host/provider | §§5–7 official contracts | REUSE | None; consume identity facts, never tokens as approvals |
| Credential custody | Host/provider; existing direct G2 credential path | §§4–5 | REUSE | Non-secret references only |
| Plugin installation | Host plugin infrastructure | §6 | REUSE | Validate subject after install/update |
| Connector connection lifecycle | Host/provider | §§5–6 | REUSE | Current availability is separate from authorization |
| MCP discovery/schemas/invocation | MCP + existing SDK | §§7–8 | REUSE | Small resolver binding, no general registry |
| Existing capability/component identity | Catalog, Slice 3C, G2/G1 | §4 anchors | REUSE | Keep existing identities authoritative for their own domains |
| G3 subject envelope and comparison | Existing IDs + canonical bytes, no general cross-kind approval subject | §§4–8 compared | BUILD_GAP | Typed view over existing exact subject, no duplicate component identity |
| Independent reusable capability approval | Catalog states/task request approvals are insufficient | §§4–8 compared | BUILD_GAP | Bind verified issuer decision to subject/scope/evidence |
| Approval-origin bridge available to this installation | Host approvals/OAuth/local CLI | No exact independently authenticated G3 decision contract established | UNKNOWN | Must establish before real approval admission |
| Minimal explicit approval scope | Workspace guards, G1/task policy, G2 scopes | §4 | BUILD_GAP | Compose bounded scope with existing restrictions |
| Approval validity/optional expiry | Existing time/freshness and request TTL | §4 | BUILD_GAP | Independent reusable approval window, no automatic renewal |
| Nexus approval revocation | Host disconnect and legacy terminal lifecycle do not supply it | §§4–8 compared | BUILD_GAP | Authoritative immutable revocation, current generation/check |
| Current task approval eligibility | Existing G1 technical eligibility | §4 | BUILD_GAP | Deterministic conjunctive evaluator |
| Schema/version/source hashing primitives | Existing pin/content/adapter binding | §4 | REUSE | Per-kind materiality projection in G3 envelope |
| Remote implementation identity / attestation | Provider metadata + tool schema | §§5–8 do not establish exact implementation | UNKNOWN | Refuse strict exact-revision use unless sufficient provider evidence exists |
| Audit integrity/checkpoints and locking | Core/G2/Slice 3C | §4 | REUSE | Keep truthful corruption-vs-authentication limits |
| Authorization decision/registration evidence | Existing receipts not reusable capability decisions | §§4–8 compared | BUILD_GAP | Small decision record and disposable registration projection |
| Owner summary / boundary prompts | Core/G2 boundary reports; Host UI | §§4–6 | REUSE | One capability-specific review summary at changed authority |
| Existing execution routing/recovery | Core, G2 managed, Host handoff | §4 | REUSE | Insert gate, keep budget/task grants/cancellation |
| G3 gate integration | Existing independent execution paths | §17 | BUILD_GAP | Prevent bypass via CLI/direct adapter/legacy handoff |
| Remote tool/connector admission beyond first local fixture | Host discovery/auth could supply inputs | §§5–8, U2/U3 | DEFER | Prove exact binding and bridge before enabling |
| SDK replacement/new provider runtime | Existing SDK/transport adequate | §8 | DEFER | No current product gap |
| Session-lifetime approval mode | No stable trusted session issuer established | §§7,14 | DEFER | Task-bound or timestamp/persistent modes suffice initially |
| Generic IAM/RBAC/ABAC/policy language | Existing G1 intersections + closed checks | §§4,8,13 | NOT_NEEDED | No demonstrated universal policy requirement |
| OAuth implementation/IdP/vault/broker/marketplace/installer/generic MCP registry/PKI | Existing external infrastructure | §§5–8 | NOT_NEEDED | None justified by the authorization gap |
| Self-hosted G2 / production Host qualification | Accepted G2 direction | §2 | DEFER | Independent later qualification work |

## 10. Proposed minimum Nexus-owned architecture

**INFERRED / PROPOSED:** one thin authorization module plus a bounded store/issuer
adapter and integration seams. No service platform or independent executor.

```text
Existing Host/provider/plugin/MCP: authentication, install, connection, discovery
Existing reviewed subject/evidence: Slice 3C / Core / G2 / G1
                              |
                 exact G3 subject envelope
                              |
      independently verified Owner decision + authoritative revocation view
                              |
           bounded registration projection + approval evaluator
                              |
         existing G1 suitability and task/Host/G2 execution authority
                              |
             fresh final admission before existing dispatch/handoff
```

Four small logical records are sufficient: Subject, Approval, Revocation and
EligibilityDecision. Registration is a rebuildable projection referring to those
records, reviewed applicability and existing mechanism identity; it is not a
second approval database. The projection must be revalidated, never trusted alone.

Records live outside Slice 3C and outside candidate/executor-writable output.
Use existing atomic/locking mechanics only where their assumptions hold. Whether
an actual protected authoritative store/issuer is available is U1; a directory,
checksum chain, claimed `issuer=owner` or sealed Python handle is insufficient.

## 11. Capability subject model and stability boundary

Reuse each existing subject ID, then bind a small typed canonical envelope.
Logical `capability_id` is a lookup key; the envelope digest binds what was approved.
All fields must have a per-kind meaning, not a universal bag of optional metadata.

| Component | Classification | Minimum use |
|---|---|---|
| capability_id | REQUIRED | Existing canonical logical ID; never display name |
| provider/source binding | REQUIRED | Exact canonical provider/source and reviewed connection/resource identity; no alias/name match |
| capability kind | REQUIRED | Distinguishes component/Skill, internal adapter and remote action contracts |
| action/tool name | REQUIRED for action tools; NOT_NEEDED for a whole pinned component | Preserve actual provider case-sensitive name separately from lower-case Nexus ID |
| immutable revision/content binding | REQUIRED where exact component bytes/revision exist | Slice 3C component-revision/tree identity; Core hook closure; G2 adapter closure; version label alone insufficient |
| version label | OPTIONAL display if stronger revision exists; REQUIRED when part of declared contract | Never silently map `latest` to an approved immutable revision |
| schema digest | REQUIRED for remote action contract; OPTIONAL/NOT_NEEDED for component-only use | Input, output, behavior-relevant tool contract/instructions and pinned local references; exclude only explicit cosmetic fields |
| configuration digest | REQUIRED if configuration changes effects/privacy/backend/permissions; otherwise NOT_NEEDED | Bind execution-relevant adapter configuration, not credentials or volatile counters |
| provider account/context identity | REQUIRED for account/tenant/project-scoped access; otherwise NOT_NEEDED | Trusted opaque stable ID; editable email, label and token hash are unsuitable |
| observed_at / valid_until / evidence reference | REQUIRED in current-use observation, outside stable subject identity | Freshness changes should not change the approved subject |
| credentials/token/session cookie, icon/title, latency/cost counters | NOT_NEEDED as authority identity | Never store secrets; cosmetic/measurement changes alone do not broaden authority |

Per-kind boundary:

1. **Reviewed local/ecosystem component:** exact existing component-revision and
   manifest/tree binding plus reviewed dependency/script/resource closure. A new
   pinned revision requires new review/approval even if described as harmless.
   Approval does not mutate Slice 3C. A top-level SKILL.md hash alone cannot cover
   unbound scripts or referenced instructions.
2. **Internal/G2 adapter:** existing capability/version/implementation closure
   plus stable execution configuration. Keep existing stricter G2 request Git
   baselines/input bindings; G3 does not relax them. A documentation-only commit
   may leave reusable subject approval unchanged while an old G2 task request
   still refuses baseline drift and needs its normal replan.
3. **Remote action:** authenticated provider/server/resource + exact tool/action
   + contract/configuration digest + account where necessary. A schema hash or
   self-reported server version is not proof of immutable remote implementation.
   Initial strict exact-revision admission remains denied if that proof is absent.
   A provider-managed contract/trust boundary requires separately reviewed,
   explicit acceptance; no automatic equivalence to pinned code. G2's accepted
   managed trust applies only to its declared adapter configuration.

Canonicalize bounded objects with the existing serializer; object-key order and
serialization whitespace do not change identity. Preserve array order unless a
specific field is defined as a set. Exclude only reviewed display title/icons and
observation time/telemetry. Treat instructions, descriptions that affect behavior,
schema annotations/extensions, endpoint/account, dependencies and effect-changing
configuration as material by default. No generic semantic-diff engine or automatic
“harmless upgrade” rule. Unknown new fields fail closed.

G1/Slice 3C parser limits are suitable for the first small subject. Arbitrary
provider JSON Schemas can contain floats, large strings, external references or
graphs incompatible with the closed Nexus format. Reuse SDK/schema validation;
pin bounded validated contract bytes or a reviewed projection instead of weakening
the frozen parser. Unsupported/unresolved contracts remain denied (U4).

## 12. Approval model, origin and registration

Minimum authoritative events: immutable **grant** and immutable **revoke**.
Do not persist EXPIRED or SUBJECT_MISMATCH as mutable approval states. Derive the
current view: UNAPPROVED, APPROVED, REVOKED or EXPIRED; malformed/origin/mismatch
failures are decision reasons. A not-yet-effective grant is not currently approved.

```text
No valid grant -> UNAPPROVED
Verified exact grant, now in validity interval, no revoke -> APPROVED
Verified applicable revoke -> REVOKED (terminal for that grant)
now >= expires_at -> EXPIRED (no renewal on resume)
New approval after expiry/revocation -> new grant ID and explicit decision
```

Proposed grant fields: schema/id; exact subject reference and digest; permitted
scope; effective_at; nullable expires_at; issuer reference; independently verified
decision evidence reference/digest; same-subject review evidence and intake-policy
identity when applicable. Use UTC integer timestamps and explicit null for no
time expiry. Do not require intake policy for internal adapters with a different
accepted provenance chain. Approval ID binds the canonical grant body.

Only the Owner, or a separately and explicitly authorized issuer with bounded
delegation, can create approval. Initial model is single Owner; no roles/tenant
directory or automated model/scanner issuer. Delegated issuer management is deferred.
The existing Host review UI may collect a decision only if a reviewed bridge binds
the human action to the exact proposal. Agent-generated JSON/CLI arguments cannot
cross that boundary. Same-user writable files are evidence, not authenticated origin.

U1 must establish origin authenticity, intended Nexus/workspace, subject/scope,
anti-replay, revocation ordering and protected storage. The executor must lack
write authority to authoritative grants/revocations; where this is unenforceable,
real admission remains blocked. Do not invent a certificate/vault/IdP system.
Pure records and synthetic trusted-issuer fixtures can be designed/implemented
later without claiming a live approval service.

Registration references a validated grant, same subject/evidence and reviewed
applicability/mechanism. Derive it on demand or rebuild it; registration alone
cannot install, invoke, delegate, grant a tool, or override Host/G2 policy.

## 13. Minimal scope model

Use closed explicit sets and subset checks, with empty sets meaning no permission;
missing mandatory scope fails. No glob/regex policy language or implicit wildcard.

| Scope dimension | Initial decision and existing reuse |
|---|---|
| Capability/provider/action | Required through exact subject; do not duplicate a broader provider grant |
| Workspace/project binding | Required explicit allowed bindings for first usable grant; reuse workspace ID/root guards and G2 project scope. Project basename alone is not cross-project identity. |
| Task class | Required allowed class set using reviewed applicability/G1 normalized task classes |
| Allowed effects/operations | Required closed set; reuse declared permissions, G2 effects and Core profile constraints; read and write are distinct |
| Task ID | Optional narrowing, required for one-task grants |
| Account/tenant | Required where the subject is account-dependent; trusted connection identity, not nickname |
| Data domain | Deferred independent policy dimension; reuse actual input/output path/data restrictions already in task/G1 policy. Do not claim a domain restriction can be enforced without evidence. |
| Time window | Approval validity, not another scope language |
| Broad cross-workspace/all-actions approval | Not in initial workflow; any later expansion is explicit changed authority |

Effective permissions = approval scope intersection with task grant, Host/provider
permissions and existing G1/G2 restrictions. No grant union: one valid grant must
cover the entire requested invocation; combining partial grants cannot manufacture
a broader invocation. Workspace move, account replacement or changed requested
effects requires resolved fresh context. Provider OAuth scopes may be broader;
Nexus keeps its narrower limits. Credentials/payments/elevation/destructive or
deployment boundaries remain genuine Owner boundaries, even with G3 approval.

## 14. Expiry and revocation

Initial supported proposal: one task (task ID), until explicit timestamp, or
persistent until revoked. Persistent approval still has narrow subject/workspace/
class/effect scope. Do not force expiry on stable internal/local subjects.
Session mode is DEFER until a trusted stable session identifier exists; an MCP
connection/process is not a session grant. Evidence freshness remains required
even when the approval has no expiry.

Revocation targets exact grant IDs, with issuer/evidence, effective time and
bounded reason. To revoke a subject, resolve its existing grants and write explicit
revocations; no wildcard future-grant ban or generic policy engine in the first
slice. Any new grant after revocation requires a new deliberate Owner decision.

New task eligibility and every new dispatch/retry/replan refuse effective
revocations. No cached positive survives a changed authorization generation.
Grant/revoke writes and final admission need the same accepted authoritative
serialization boundary. If a revocation is committed before admission, no new
dispatch can be admitted. Admission committed first identifies already-running
work; this ordering is explicit and does not pretend instantaneous remote stopping.
Corrupt/missing/rolled-back store, stale generation or unknown ordering -> deny.
Existing file locks/atomic writes help mechanics but do not prove hostile rollback
resistance or cross-process authority; U1 remains a gate.

Already-running work: record revocation, stop subsequent admissions; preserve the
original G2 dispatch/request/receipt. G3 does not automatically cancel a remote
execution or claim cessation. Original-result observation/cancellation/reconciliation
continues only under its existing G2 cleanup authority, which revocation does not
expand. Accepting or applying a result requiring new effects needs current approval
and task authority. Unknown remote effects/billing remain UNKNOWN.

## 15. Eligibility decision and proposed reason codes

Eligibility is the conjunction of **valid Nexus approval**, **current usable
subject**, **G1 suitability/controls where applicable**, and **independent task/
Host/G2 execution authority**. A G3 approval cannot make an unavailable Host eligible.

Proposed bounded machine result: schema; ELIGIBLE/NOT_ELIGIBLE; primary reason and
ordered reason_codes; subject/grant digest references; scope/request/observation
digests; authoritative authorization generation; evaluated_at; evidence references.
It is explainable evidence with `dispatch_authority=none`, not a portable bearer
grant. An executor rechecks current admission rather than trusting copied JSON.

Repository convention uses uppercase deterministic strings (e.g.
`G1_INVALID_INPUT`, `G1_AMBIGUOUS_IDENTITY`, `OWNER_AUTHORITY_REQUIRED`) and closed
schema versions. Proposed G3 names below follow that convention; they are not
newly implemented API constants.

| Ordered gate | Proposed denial reasons / behavior |
|---|---|
| Parse and resolve one exact subject | `G3_INVALID_INPUT`, `G3_CAPABILITY_IDENTITY_UNKNOWN`, `G3_CAPABILITY_IDENTITY_AMBIGUOUS`; unsafe/incomplete identity stops dependent checks |
| Read authoritative records and validate issuer/evidence | `G3_APPROVAL_STORE_UNVERIFIED`, `G3_APPROVAL_ORIGIN_UNVERIFIED`, `G3_APPROVAL_INVALID`; cannot fall back to catalog JSON |
| Find a grant for requested subject | `G3_CAPABILITY_UNAPPROVED`; missing exact subject after a logical-ID match: `G3_CAPABILITY_SUBJECT_MISMATCH` |
| Validate provider/revision/configuration/account/evidence match | `G3_CAPABILITY_SUBJECT_MISMATCH`, `G3_CAPABILITY_EVIDENCE_UNVERIFIED`; approval does not migrate |
| Check effective revocation and validity | `G3_CAPABILITY_REVOKED`, `G3_APPROVAL_NOT_EFFECTIVE`, `G3_CAPABILITY_EXPIRED` |
| Require one grant to cover scope | `G3_CAPABILITY_SCOPE_DENIED`; no widening or union |
| Validate current-use observation / availability | `G3_CAPABILITY_METADATA_STALE`, `G3_CAPABILITY_UNAVAILABLE`; Host repair is separate from approval |
| Compose existing technical/task gates | Preserve upstream reason codes with source namespace; `G3_TASK_AUTHORITY_REQUIRED` or existing Owner-boundary route; approval PASS alone is insufficient |
| Final atomic admission | Changed generation/subject/context -> `G3_ADMISSION_STALE`; no new intent/export/effect |

Collect deterministically only reasons whose inputs are valid; unsafe input/store
failures stop dependent evaluation. For multiple grants, evaluate independently;
select a single fully covering valid grant with stable ID ordering. Revoked or
expired grants cannot poison another independently valid grant, and never repair
one another. If no valid grant exists, retain bounded per-grant explanations in
stable order. Evaluated_at is supplied by a trusted caller; unknown time/rollback
of time cannot silently validate expiring authority. Positive caching is limited
to planning and never replaces final checks.

## 16. Owner interaction

Approve once for the correct subject/workspace/task-class/effects and reuse while
valid. Existing Core/G2 review summaries supply the format: exact subject and
material revision, provider/account context, scope, validity, evidence/limitations
and intended effects. No credentials in the summary.

One actual Owner review may bind both a reusable capability grant and an exact
task grant, if the reviewed bridge records both decisions explicitly. Never infer
G3 approval from OAuth consent. Do not add prompts on every deterministic action
inside unchanged approved scope or repeat OAuth merely for a Nexus record.
Prompt only for a missing/new/revoked/expired approval, material subject/scope
change or an existing hard authority boundary. Ambiguous identity first requires
resolution, not a broad approval prompt; ordinary unavailability/stale metadata
first requests safe refresh/diagnosis. Revocation does not invite automatic regrant.
Repeated identical refusals reuse one pending boundary report rather than prompting
on each retry. The exact Host UI bridge remains U1/U2; no UI was created here.

## 17. G2 integration and migration requirements

Routing previews may explain unapproved candidates; the executable/handoff pool
must include only admitted candidates. **NO ELIGIBLE CAPABILITY -> NO EXECUTION.**
Read-only metadata discovery can precede approval, but it cannot activate candidate
instructions, run scripts, export task data or create execution authority.

| Existing entry point | Proposed integration seam and compatibility |
|---|---|
| Capability selection / `route_backend` | Intersect G3-approved subjects with existing suitability/route facts. `local_supported`/`managed_supported` booleans are not authority; a route choice remains advisory. |
| `prepare_execution` / `prepare_openai` | Resolve subject and show approval disposition without new authority. If records bind a real request, bind the decision reference into a new versioned envelope; no silently adding fields to closed v1 requests. |
| `export_handoff` / `retry_execution` | Fresh G3 admission under the accepted lock before HANDOFF_INTENT/data export and before any renewed attempt. Keep exact task request approval and G2 expiry/scope checks. |
| `OpenAIHostedExecutionBackend.submit` | Gate direct method calls as well as CLI, before credential access and DISPATCH_INTENT/POST. Keep exact request digest, separate live/spend authority, one slot, baseline/configuration and no-replay checks. |
| `ash/core.py::_dispatch` | For newly adopted external hooks, final gate before charging/intent/invoke, including verify/repair hooks if they introduce effects. Preserve accepted Core scope/catalog/interpreter/cancel checks. |
| Host inventory/handoff | Bind the G3 decision to existing provider/capability mapping and fresh Host execution-start claim. Local planner alone cannot enforce Host invocation; require a reviewed Host consumer. No new MCP execution tool. |
| Legacy `ash/execution.py::execute_route`; `scripts/hub.py` run/`--allow-skill-commands` | Existing opt-in hook path is a separate bypass risk. Future G3 adoption must cover command and validation hooks plus instruction handoff, or explicitly refuse external G3 subjects on this path. CLI-only gating is insufficient. |
| Original G2 poll/cancel/import/reconcile | Preserve original operation identity and historical task ledgers. Cleanup cannot redispatch or regrant. New local output application/effects require current admission; mere result reconciliation is not a new provider execution. |

Migration is explicit, not auto-approval:

- Keep frozen Slice 3C/G1 APIs and zero-authority semantics. Add composition at
  consumers; never introduce APPROVED into Slice 3C state transitions.
- Accepted fixed internal Core capabilities retain their current closed catalog,
  bytes, task approval and trusted-hook contract. Do not disable Core because a
  new empty external G3 store exists. This is a limited pre-existing authority
  path, not a namespace/provider-wide exemption for arbitrary new capabilities.
- No bulk import of historical `approved`/`available`, mappings or Host installs
  into G3 grants. A real migration needs exact decision evidence. G2 adapter reuse
  does not create cross-task persistent approval from a historical spend grant.
- Keep old G2 ledgers immutable for status/reconciliation. New authorization-bound
  requests/receipts need an explicit version/sidecar binding and compatibility
  tests; old pending requests cannot acquire new dispatch permission by migration.
- A model selection change is material if model/provider/deployment/configuration
  affects the approved capability. G1 suitability remains separately mandatory.
- Standalone CLI cannot gate independent actions in this chat outside Nexus.
  Coverage claims must name actual Nexus entry points/Host consumers. G3 does not
  become an OS/Host-wide reference monitor.

## 18. Fail-closed analysis

| Case | Required disposition |
|---|---|
| Unknown or ambiguous capability identity | Deny; do not choose a same-name tool/provider or silent fallback |
| Host connected, tool installed/visible, no Nexus grant | Deny capability use; metadata discovery alone remains non-authorizing |
| Approval forged/modified, invalid issuer, unreadable authoritative store | Deny; checksums or candidate claims cannot repair origin |
| Changed schema/version/source/dependency/configuration | Deny old grant; review and new grant for material change |
| Same schema, different remote implementation | Schema equality insufficient; strict revision claim denied absent stronger evidence |
| Revoked/expired/not-yet-effective grant | Deny new eligibility/admission; preserve original work evidence |
| Broader workspace/class/action/effects/data paths | Deny; no scope union, wildcard escalation or guessed domain match |
| Provider/endpoint/account identity mismatch | Deny; label, email or OAuth availability is not subject equality |
| Stale cached metadata or missed list-change event | Refuse final admission until fresh validated binding exists |
| Capability disappears / Host disconnected | NOT_ELIGIBLE even with valid approval; keep approval history, no substitute |
| Registration projection tampered/stale | Rebuild/read through authoritative records; deny if validation fails |
| Approval/revoke store rollback or ordering unknown | Deny new admissions; file hashes/chain alone do not prove latest state |
| Subject or approval changes between review and dispatch | Fresh check under authoritative serialization; no effect on stale decision |
| Host permission or task/spend authority missing | Deny/Owner boundary; capability approval cannot supply it |
| Uncovered intake policy or review evidence for new external component | Deny adoption; no change to frozen quarantine to force eligibility |
| Candidate metadata/instructions contain approval-shaped JSON | Treat as untrusted data; no issuer/store write access or authority |

## 19. Explicit non-builds

G3 will not build OAuth, identity provider, account system, secret vault, password
manager, credential broker, generic marketplace, plugin installer, generic MCP
registry/protocol, universal permission system, certificate infrastructure,
generic IAM/RBAC/ABAC/policy engine, provider authentication protocol, executor,
remote cancellation engine, scanner trust authority, or automatic upgrade adoption.
No general cryptographic identity or hostile-Host qualification is claimed.
Self-hosted G2 and broad remote bridges remain deferred.

## 20. Unresolved UNKNOWNs and dependent paths

| ID | UNKNOWN | Consequence / smallest next evidence |
|---|---|---|
| U1 | Independently authenticated Owner decision bridge, executor-excluded authoritative store, revocation serialization and rollback freshness | Block real grant issuance/admission. Inspect an existing protected Host/operator channel against an exact proposal; explicit issuer/security-boundary acceptance is required. No assumption that same-user CLI/files authenticate the Owner. |
| U2 | Host exposes a stable non-secret provider/server/account identity and a current contract snapshot to a Nexus consumer | Block that connector/Host binding until its actual interface is reviewed. Chat-visible tool metadata alone is insufficient. |
| U3 | Remote tools provide stable revision/implementation evidence or an explicitly accepted managed-service contract boundary | Block strict remote exact-revision admission; first local controlled fixture can proceed independently in a future authorized phase. |
| U4 | Concrete provider schemas fit bounded validated contract representation; installed SDK/Host protocol parity | Do not weaken frozen parser or assume newest specification support; inspect a selected contract/runtime only when needed. |
| U5 | Authenticated stable task/workspace/session context, trusted clock and protected store generation in the chosen deployment | Task scope must be independently bound; session grants remain deferred, uncertain expiry/ordering denies. |
| U6 | Actual migrated Core/managed/legacy/Host consumer coverage and old/new request compatibility | Cannot claim enforcement coverage until later regression and adversarial evidence exists. |

These do not block completion of Phase 1. No credential, paid call, account,
privilege, external authority or direction change was necessary to finish this
survey, so no new NEXT-OWNER-DECISION is needed now. If future implementation
reaches a genuine U1/other authority boundary, produce the required concrete
NEXT-OWNER-DECISION then and stop only that dependent path. This survey is not an
accepted approval-origin mechanism and cannot pre-authorize it.

## 21. Recommended smallest Phase 2 slices

These are recommendations only; Phase 2 is not started or authorized here.
Derive them from actual primitives and the origin risk, rather than implementing
a six-stage universal authorization platform.

| Slice | Minimal deliverable and reuse | Exit / dependency |
|---|---|---|
| G3-A — Subject and decision contracts | Small typed envelope over existing identities/canonical bytes; per-kind stability rules; first bounded local fixture; proposed reason codes | Golden/canonical/substitution tests; no authority or executor changes. Safe first implementation slice after explicit Phase 2 authorization. |
| G3-B — Issuer boundary and immutable records | Review existing Owner channel/store first; grant/revoke/registration schemas and persistence using existing mechanics; trusted-issuer fixtures | Real adapter stays disabled until U1 is evidenced and its security boundary accepted. Do not replace U1 with editable files or a new IAM platform. |
| G3-C — Eligibility evaluator | Pure bounded evaluator, single covering grant, freshness/validity/revocation/scope; compose existing G1/task decisions | Deterministic refusal and explanation matrix. Synthetic approval is clearly fixture-only. |
| G3-D — One vertical gate and Owner workflow | Start with one reviewed local fixture and exact Owner summary; integrate core/direct entry admission and decision binding; prevent relevant legacy bypass | Real issuance depends on B; end-to-end fixture shows deny/use/revoke/deny with no silent regrant. Keep installed planner MCP read-only. |
| G3-E — Managed/Host compatibility and acceptance | Versioned G2 binding, no live provider execution by default; Core/migration/legacy tests and docs; add a Host consumer only with U2/U3 evidence | Coverage named precisely; negative quarantine/forgery/rollback tests and independent review before trust-increasing acceptance. Broad remote adoption stays DEFER. |

Owner workflow belongs with the first usable vertical slice, not a separate UI
platform. Regression/doc work accompanies every slice; E completes integration
coverage. Phase 2 planning is ready. Real authorization/enforcement readiness is
conditional on U1 and the selected subject/consumer evidence; it is not established.

## 22. Deterministic test strategy (design only)

Reuse `tests/g1_fixtures.py` for synthetic profiles/time, existing canonical golden
vectors in `tests/test_ecosystem_policy_models.py`, catalog revision tests, Core
temporary fixtures, workspace guards, and `FixtureHTTP` from OpenAI adapter tests.
All provider responses remain synthetic; use no live transport/credentials.

| Required case | Oracle / reusable facility |
|---|---|
| Approved exact capability eligible | Verified fixture issuer, one covering grant, fresh subject, technical/task gates PASS -> ELIGIBLE |
| Unapproved denied | Empty grant set, even with Host connected/installed -> G3_CAPABILITY_UNAPPROVED |
| Revoked denied | Commit fixture revocation before admission -> no intent/export/invoke; no regrant on retry |
| Expired denied | At expires_at and later -> deny; frozen clock before expiry -> allow; resume cannot reset expiry |
| Subject mismatch denied | Source/revision/closure/schema/config/account swap -> mismatch; existing component revision helpers |
| Scope too broad denied | Different workspace/class/action/effects/task or input/output path escape -> deny; workspace/Core guards |
| Exact subject match allowed | Stable canonical digest across object-key order/serialization whitespace -> same subject |
| Harmless metadata change | Title/icon, observation timestamp or telemetry only -> same approval; freshness still checked |
| Material capability change | Instruction/script/dependency/schema/effect/account change -> new subject; no inherited approval |
| Host connected but Nexus unapproved | Discovery/connection cannot manufacture approval; no handoff/data export |
| Approval exists but Host unavailable | NOT_ELIGIBLE; unchanged grant history; no same-name substitute |
| Owner prompt boundary only | Repeated valid invocation -> zero extra prompts; actual new authority -> one deduplicated review; unavailable metadata -> refresh/diagnosis |
| Forged/modified issuer or registration | Reject candidate-shaped grant, copied seal, changed scope/decision evidence, tampered projection |
| Review/evidence mismatch and quarantine | Wrong intake policy, missing same-subject evidence, uncovered source -> denied; Slice 3C zero-authority remains unchanged |
| Stale positive decision and revocation race | Final gate rejects old generation; order grant/revoke/admission deterministically; no effect when revoke wins |
| Store corruption/rollback/clock unknown | No fallback to stale approval; checksums alone cannot satisfy authoritative freshness |
| Multiple grants | No permission union; invalid/revoked grant cannot invalidate independently valid covering grant; stable result order |
| G1/Core/G2 migration | Accepted closed Core behavior retains its contract; new external hook requires G3; old ledgers status/reconcile only; direct methods cannot bypass CLI gate |
| Managed route denial | FixtureHTTP call count stays zero on failed eligibility; one-slot/no-replay/request digest/receipt verification preserved |
| In-flight revocation | Next effect denied; G2 observation/reconciliation remains original-bound; no automatic cancel or remote-stop claim |
| Resource/encoding limits | Duplicate keys, cycles, oversized graphs, unknown fields, Unicode ambiguity, invalid digests and unresolved schema references -> deny |

Negative tests must observe absence of effects, not merely an error string.
Approval-origin/store tests need a real accepted boundary to establish production
properties; fixture PASS is not human authentication or Host qualification.

## 23. Phase 1 validation convention

The manifest covers static package source. The live checkout contains historical
untracked drafts and mutable state; running its broad rglob builder directly can
include drafts or encounter protected-storage guards. Reuse the established clean
static-source snapshot convention, not a builder/guard change:

1. Verify all 324 baseline entries against normalized bytes.
2. Export exactly those entries plus this new document into a clean ignored
   validation snapshot; no Route D drafts, credentials, runtime output or Git.
3. Run existing `build_manifest_bytes` on that snapshot and compare the 324 old
   entries byte-for-byte with the baseline; exactly one new document entry.
4. Update only the working manifest with the generated 325-entry result. This is
   required source integrity maintenance, not release/freeze or historical rewrite.
5. Verify document sections, local links, classification values, external source
   dates, fences, placeholders and secret patterns; run diff whitespace checks,
   including a no-index check of the new untracked document.
6. Compare all original tracked-file hashes and the Git index; only MANIFEST may
   change, original G2/code/tests remain identical, draft hashes match. Confirm
   branch/checkpoint ancestry and no staged files.

No application test suite is warranted for a documentation-only change. The
future test matrix above was designed, not run. Validation commands/results are
retained in ignored `state/g3-phase1-20261008/`; no runtime/provider tool was used.

## 24. Preservation and final receipt

Initial historical draft SHA-256 values (raw bytes):

| Untracked historical draft | SHA-256 |
|---|---|
| `docs/nexus-route-d-successor-custody-domain-adversarial-review-v1.md` | `08daa1ca3568151f5ae1d54525456e1a72e2c10e5438131be2ae1203fca937e4` |
| `docs/nexus-route-d-successor-custody-domain-architecture-v1.md` | `418a3b54ef4ea509b85e195b81797a83ba84ea5a24298aaaa1909d5b3186f98a` |
| `docs/nexus-route-d-successor-custody-domain-setup-authorization-spec-v1.md` | `e977f897102c63d91c7367686cc37d3534d771a9a2179b2713af7877334b54c5` |

Final local documentation checks on 2026-10-08:

| Check | Result |
|---|---|
| Branch / checkpoint / ancestry | PASS; local G3 branch HEAD remains the exact G2 checkpoint; baseline is an ancestor; cached G2 remote ref unchanged |
| Static MANIFEST | PASS, 325 subjects; all 324 prior entries identical; exactly this document added; two identical builder outputs |
| Tracked-file preservation | PASS; original raw-byte tracked hashes match except the intended MANIFEST addition; no code, tests or G2 evidence changed |
| Historical Route D drafts | PASS, all three raw-byte hashes unchanged; remain untracked and uncommitted |
| Documentation structure | PASS, 24 numbered sections, balanced fences, valid local file/anchor links, no planning placeholders |
| Classification table | PASS, 26 rows each with one allowed decision: REUSE 10; BUILD_GAP 8; DEFER 4; NOT_NEEDED 2; UNKNOWN 2 |
| Secret-pattern check | PASS for bounded key/token/private-key patterns in the new document; no credentials accessed; not a general DLP claim |
| Whitespace / diff | `git diff --check` PASS; new document no-index check has no whitespace diagnostics (exit 1 denotes added content), independent trailing-space check PASS |
| Git index / history | PASS, index raw hash unchanged and no staged files; no commit/push/merge/tag/freeze/release |
| Provider activity | New execution and provider API access zero; historical total retained as 3 from G2 closure |
| Git status | `M MANIFEST.json`; new survey untracked; three preserved historical drafts untracked; nothing else changed in the tracked tree |

Git emitted the existing LF-to-CRLF checkout notices for MANIFEST/new document;
these are not whitespace failures. No Git setting was changed. Manifest checks
use the existing LF-normalized byte convention; draft preservation uses raw
bytes. Final artifact hashes and check output are in the ignored validation JSON,
avoiding a self-referential document hash. Application tests were not run because
no application code changed; no G3 implementation or runtime qualification occurred.

```text
G3_REUSE_SURVEY_COMPLETE
G3_IMPLEMENTATION_NOT_STARTED
REUSE_FIRST = ENFORCED
NO_ROUTINE_OWNER_INTERRUPTION = ENFORCED
NEW_PROVIDER_EXECUTIONS = 0
HISTORICAL_PROVIDER_EXECUTIONS = 3 (accepted G2 closure; unchanged by this phase)
CREDENTIAL_USE = NONE
NEXT = G3_PHASE_2_MINIMUM_GAP_IMPLEMENTATION (requires separate authorization)
PHASE_2_PLANNING_READY = YES
REAL_APPROVAL_ADMISSION_READY = NO / U1 AND SUBJECT-SPECIFIC EVIDENCE REQUIRED
```
