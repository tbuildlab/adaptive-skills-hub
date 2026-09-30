# Nexus G2 OpenAI-First Proposed Minimized Clarification Pack v1

Status: **PROPOSED / NOT SUBMITTED — NO PROVIDER OUTREACH OR EXPERIMENT AUTHORITY**

Target: OpenAI Agents API with the OpenAI-managed Codex harness and `environment.type: "openai_hosted"`, using one minimal network-disabled session, no multi-agent, MCP, tools, skills, plugins, vaults or extra packages unless later explicitly admitted.

These questions are the minimum provider-side semantics that the current accepted evidence, Nexus controller and a bounded experiment cannot safely manufacture. Each answer must identify an official supported contract/API reference and distinguish hard behavior from current implementation or best effort.

1. **Configuration mutation boundary:** After creation of an OpenAI-hosted session, which customer/project actors or APIs can change its network policy, container size, setup/package/capability configuration, attached credentials or other security-relevant environment settings, and what exact interval guarantees those settings cannot change while an admitted turn runs?
2. **Disabled-network enforcement scope:** For `network.access: "disabled"`, what outbound channels and destinations are hard-blocked for the complete sandbox and descendants, including IPv4/IPv6, DNS, redirects, link-local/metadata/private services and alternate protocols, and what provider-internal exceptions remain?
3. **Whole-unit hard resource and lifetime bounds:** Which non-workload-relaxable CPU, memory, storage/process/output and maximum active wall-clock bounds apply to the sandbox and every descendant, including continuous activity, keep-alives and loss of the application controller; what hard fallback ends work if cancellation is lost?
4. **Managed agent/model-loop bound:** Which supported session/agent settings or service limits impose a finite maximum on root-agent model calls, automatic retries, reasoning/output tokens and tool-loop steps when multi-agent and optional tools are disabled?
5. **Complete finite charge composition:** For that exact minimal mode, what are all billable dimensions and minimum increments, including model, container active/idle/cleanup time, files/artifacts/storage and delayed or residual charges; which provider-enforced bounds or cutoff/overshoot semantics allow a conservative finite worst-case amount before dispatch?
6. **Settlement and cleanup tail:** After turn cancellation and session deletion, what queryable states or billing rules bound continued descendants, physical cleanup and further charge accrual until settlement, even when public API deletion completes first?

The following are no longer proposed as provider-answer prerequisites to the first bounded experiment:

- internal image/harness/enforcement byte identity;
- proof of every dynamically loaded dependency;
- a distinct command-operation API when stable session/turn/item references suffice;
- a monolithic applied-policy receipt;
- native create/input idempotency when Nexus enforces at-most-one attempt and UNKNOWN/STOP;
- indefinite post-delete history;
- one monolithic security receipt;
- complete active-session key-revocation propagation;
- hidden deployment revision or push change feed;
- universal trace completeness.

Their underlying properties remain covered by Nexus-owned controls, composite evidence, exact qualification tests, short expiry or fail-closed STOP as specified in the review/matrix. This pack does not assert that OpenAI can answer positively and does not upgrade the accepted OpenAI classification.

No question has been submitted. No account, credential, authenticated API, sandbox, experiment, cost, Host selection, adapter implementation or G2 Runtime authority is granted. Scenario 01–04 remain **NOT RUN**; HQ1–HQ5 **NOT PASS**; HQ6 **NOT STARTED**; Positive Host Binding **ABSENT**; G2 **HOLD**.
