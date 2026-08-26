# Nexus Bounded Agent Task Contract

**Current status:** contract and validation only. No Agent Runtime, Agent
execution, subagent spawning, swarm, or delegated tool authority is enabled.

## Why the contract exists

An Agent definition is a specialist role and process, not an executable Skill.
Before any future Agent Runtime can be considered, each task must be reduced to
a bounded, cancellable, provenance-pinned contract. The Agent cannot inherit
ambient Host, tool, workspace, shell, or approval authority from its persona.

`ash.agent_contract.validate_agent_task_contract` currently accepts only
`advisory_only` contracts. It performs validation only and never launches an
Agent.

## Required contract

The v1 contract requires:

- opaque contract and Agent IDs;
- source ID, repository, exact 40-character commit, and optional content
  SHA-256;
- an objective ID, opaque input-reference IDs, and output-schema ID;
- an explicit allowlist of capability IDs (empty is allowed);
- maximum turns, timeout, and token budget;
- required cancellation signal;
- required independent validator capability IDs;
- a complete execution/validation receipt schema.

Raw Skill instructions, raw project context, workspace content, environment
values, secrets, hidden reasoning, and absolute paths are forbidden.

## Current permission boundary

The only accepted permission object is:

```json
{
  "read_only": true,
  "network": false,
  "shell": false,
  "subprocess": false,
  "write": false,
  "delegation": false
}
```

The current maximums are 8 turns, 900 seconds, and 32,000 tokens. These are
upper safety bounds, not defaults or automatic grants.

## Receipt semantics

A future executor would have to return separately auditable facts for:

- contract and Agent identity;
- started, completed, and cancelled states;
- opaque output reference;
- validation status;
- result code.

An Agent cannot validate or approve its own output. The primary Host/runtime
must preserve the ability to cancel, reject, or ignore advisory output.

## Future approval gates

Moving beyond advisory-only would require a separate architecture and product
approval covering the executor, sandbox, context broker, tool gateway,
permission/approval UI, cancellation transport, resource accounting,
independent reviewer, receipts, and failure recovery. It cannot be enabled by
editing an Agent persona or source registry record.
