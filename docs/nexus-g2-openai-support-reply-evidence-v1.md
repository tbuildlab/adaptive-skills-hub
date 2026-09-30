# Nexus G2 OpenAI Support Reply Evidence v1

Document ID: `nexus.g2.openai-support-reply.evidence.v1`

Version: `1.0.0`

Evidence ingestion date: 30 September 2026, Asia/Kuala_Lumpur

Status: **OWNER-SUPPLIED SUPPORT EVIDENCE — NOT A CONTRACT OR QUALIFICATION; G2 HOLD**

## 1. Provenance and preservation

Channel: **OpenAI Help Center / AI-assisted support**, as identified by the owner's authorization and the response itself. The owner supplied the complete response through this conversation. Original provider receipt date/time, ticket identity and independently authenticated support export: **UNKNOWN / not supplied**. The ingestion date is not invented as the provider receipt date. No mailbox, account or credential was accessed; no claim of independent sender authentication is made.

The text in §2 preserves the complete supplied reply, including every documented/not-documented distinction and original URL spelling. Only transport CRLF is normalized to LF for the repository's canonical UTF-8 representation. No sentence, quotation, punctuation or URL is corrected inside the preserved reply. Its content basis is the owner's supplied text, not a regenerated provider response. The [adjudication](nexus-g2-openai-support-reply-adjudication-v1.md) separately verifies cited public sources and records scope limitations. Hashes bind custody/content, not authorship or truth.

**An AI-assisted support response is not automatically equivalent to a contractual provider guarantee.** Support interpretation and absence-of-documentation assertions do not establish missing enforcement semantics, numerical bounds, deployed account state or non-existence of a capability. No human/platform engineering guarantee is present. The final invitation to supply a flow is quoted evidence, not an instruction or authority to contact support, disclose secrets or execute anything.

## 2. Exact complete owner-supplied reply

```text
I’m AI-assisted support. Below is what is explicitly documented today for environment.type: "openai_hosted"; where the docs don’t define a hard bound, I’m stating that plainly.

Configuration mutation boundary (during an active turn)

Documented: Session agent settings updates (model / reasoning.effort / service_tier / metadata) apply only to new turns; “messages already in flight can use the previous settings” and “an active turn keeps its settings” (including steering messages).

Not documented: Any supported “immutable interval”/ordering barrier beyond the above, or any supported API to mutate environment/network/capabilities/env vars/files mid-turn as a hard security boundary.
Source: https://developers.openai.com/api/docs/guides/agents-api/configuration/

network.access: "disabled" exact denial semantics

Documented: “Block outbound access.” For restricted, redirects/subdomains must be explicitly allowlisted. Also: “Hosted stdio MCP servers currently require enabled access.”

Not documented: Whether “block outbound” is defined at the level of IPv4 vs IPv6, DNS resolution, link-local/metadata IPs, redirect handling in disabled, or “other outbound channels,” nor an explicit list of intrinsic OpenAI harness/service connections that remain permitted.
Source: https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted/

Whole-unit containment / ultimate forced termination bound

Documented: If activity + keep-alives stop for 1 hour, “the sandbox can be deleted” (not configurable). “Connected sandboxes receive keep-alives, including between turns.” You can delete the session to request cleanup; deletion may return 409 while setup/execution finishes; retry.

Not documented: A hard maximum active lifetime under continuous activity, a guaranteed forced-termination time, or any additional non-workload-relaxable envelope beyond the chosen container size.
Source: https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted/

Managed agent/model loop hard cumulative bound (incl. session_budget_exceeded)

Not documented (in the public docs retrieved here): Any hard, user-computable cumulative cap for a single turn/session covering model calls, internal retries, reasoning/output tokens, or tool steps; nor units/defaults/overshoot/termination semantics for session_budget_exceeded.
(Closest related: input request size limit 4 MiB; and usage reporting is “best-effort” and may be null/change.)
Sources:

https://developers.openai.com/api/docs/guides/agents-api/sessions/

https://developers.openai.com/api/docs/guides/agents-api/observability/

Financial worst-case bound (pre-dispatch conservative maximum; spend-limit overshoot)

Documented pricing surfaces: OpenAI-hosted sandboxes use standard container rates, and model usage is billed separately at model API rates.

Documented hard spend limits: You can enforce org/project hard monthly spend limits; when reached, requests return 429 with organization_spend_limit_exceeded / project_spend_limit_exceeded. Enforcement is “not instantaneous,” so spend can “slightly exceed” the configured amount (no numeric max overshoot documented).

Not documented: A supported mechanism to compute a finite conservative maximum charge per dispatch that includes container time, model/cache, retries, failures/cleanup, and any retained storage/artifacts.
Sources:

https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted/

https://developers.openai.com/api/docs/guides/spend-limits/

Cancellation/failure tail (continued execution + billing after cancel/delete/stream loss) & authoritative status/usage sources

Documented cancellation semantics: Sending agent.session.input.cancel “cancel[s] the current turn” and you should observe lifecycle events like agent.session.turn.cancelled (alongside completed/failed). “Closing an event stream does not cancel the task.” If a stream disconnects, retrieve the session and saved items to recover state.

Not documented: A hard bound on continued execution/billing after agent.session.input.cancel, session deletion request, controller/transport loss, or other failures (including any guaranteed maximum tail).

Documented sources of truth for status/usage (with caveats): event stream + saved session items + dashboard logs; token usage fields are “best-effort,” can be null, and “are not a final bill.”
Sources:

https://developers.openai.com/api/docs/guides/agents-api/sessions/

https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted/

https://developers.openai.com/api/docs/guides/agents-api/observability/

https://help.openai.com/articles/20001551

If you want, paste the exact session create/update flow you plan (templates, network mode, tools, expected runtime), and I’ll map which of your six requirements are satisfiable with documented controls vs which currently lack a documented hard bound.
```

## 3. Evidentiary boundary

See the [claim classifications and blocker adjudication](nexus-g2-openai-support-reply-adjudication-v1.md), [unsent human escalation](nexus-g2-openai-human-escalation-request-v1.md) and [separate adversarial pass](nexus-g2-openai-support-reply-adversarial-review-v1.md). This preserves new evidence additively; all earlier UNSENT/no-support headings remain historical facts at their original checkpoint. The owner's later contact changes neither those bytes nor their earlier authority.

Scenario 01–04 = **NOT RUN**; HQ1–HQ5 = **NOT PASS**; HQ6 = **NOT STARTED**; Positive Host Binding = **ABSENT**; G2 = **HOLD**. No Host selection, execution, normative acceptance or provider guarantee is created by this evidence record.
