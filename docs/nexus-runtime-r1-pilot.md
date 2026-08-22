# Nexus Runtime R1 — Codex Daily Usage Pilot

## Status and scope

R1 is a project-level Codex pilot for `D:\chatgpt\AI Coordinator`. It uses
the existing Nexus V1.2 command, not a new runtime service:

```powershell
python "D:\chatgpt\安装skills\adaptive-skills-hub\scripts\nexus.py" plan "<task intent>" --project "D:\chatgpt\AI Coordinator" --handoff
```

It is intentionally **not** a global interceptor, MCP server, ChatGPT
integration, plugin, Agent runtime, Skill installer, or V1.3 feature. Nexus
plans and loads selected local Skill instructions; the host Codex session
retains execution authority and validates task results.

## Installation and activation

No package is installed and no global Codex configuration is changed. The R1
activation is the project-local `D:\chatgpt\AI Coordinator\AGENTS.md` file. Official OpenAI
documentation states that Codex reads project `AGENTS.md` instructions at the
start of a run, from the repository root toward the working directory. Start a
new Codex task from the AI Coordinator repository after adding or changing the
file.

The instruction consults Nexus at most once when a task is a feature, bug,
test/regression request, security review, artifact, evidence-backed research,
multi-step project task, or likely Skill-relevant work. It skips greetings,
casual conversation, simple factual questions, one-line calculations, and
trivial explanations. A user opt-out always wins.

This is **near-automatic instruction-driven activation**, not a hard runtime
interceptor. Codex must load the project instructions for a new task; it does
not invoke Nexus for a task already started before this file was loaded.

Codex's restricted workspace sandbox may not permit a process in AI
Coordinator to read Nexus from its separate directory. R1 does not widen that
sandbox: it adds no external writable directories, copies no Skills into the
project, and changes no global configuration. A session that cannot read the
fixed command or selected `SKILL.md` follows the documented native fallback
rather than bypassing the sandbox.

## Handoff and execution contract

1. Nexus discovers the fixed AI Coordinator root, applies bounded project
   rules/context, ranks the smallest sufficient set, loads only selected
   `SKILL.md` files, validates the plan load, and writes a redacted JSON
   handoff to stdout. `--handoff` is strictly stateless: it creates no packet
   or persistent state and rejects `--packet`. `--no-state` remains accepted
   with `--handoff` for compatible callers.
2. Codex reads only the JSON after `Handoff:`, opens the selected `SKILL.md`
   locations, follows the applicable instructions, performs authorized work,
   then runs relevant validation.
3. Codex reports the consultation, selected Skills and locations, planned
   validation, result, advisory-only Agents, and any fallback.

The handoff contains local paths and selected-Skill metadata only; it never
contains Skill prose, bounded project-context content, or credentials. Do not
copy raw Skill contents, credentials, tokens, private records, or
secret-bearing raw text into a planning request.

## Failure and fallback

If the Python command, fixed project-root validation, plan loading, or selected
Skill compatibility fails, Codex continues with its native tools and reports:

> Nexus unavailable — native Codex fallback used.

Nexus does not gain permission to execute arbitrary commands. A selected Skill
is guidance only; existing user, system, and AI Coordinator project boundaries
remain controlling.

## Disable, remove, or extend

To disable R1 for AI Coordinator, remove the clearly labelled `Nexus Runtime
R1 pilot` section from its root `AGENTS.md` (or remove that file if it contains
only this pilot). No global file, Nexus state file, MCP configuration, copied
Skill, or installed package must be removed.

To add the pilot to another project, create that project's own `AGENTS.md`,
adapt the fixed `--project` root, preserve the one-consult activation gate and
`--handoff` exchange, then run its project-specific routing
and safety tests. Do not copy this instruction to `~/.codex` and do not claim
that it activates every project.

## Explicit non-goals

- No R2 local MCP adapter.
- No R3 ChatGPT desktop/remote integration, tunnel, or plugin work.
- No automatic Agent delegation or multi-agent runtime.
- No automatic Skill install, update, or arbitrary Skill-command execution.
- No direct provider call, credential inspection, or cross-project discovery.
