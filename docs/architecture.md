# Adaptive Skills Hub architecture

## Runtime boundary

V1.1 is a local, standard-library-only router. It does not replace Codex's native
Skill runtime and it does not download, install, or update external repositories.

```text
Task
  -> metadata discovery (SKILL.md prefix only)
  -> separate Skill / Agent indexes
  -> ranking and smallest sufficient chain
  -> full selected SKILL.md load
  -> Codex execution or explicit local command hook
  -> validation and evidence packet
```

`ash.discovery` owns filesystem inspection. `ash.router` is pure ranking and chain
ordering. `ash.execution` owns full instruction loading and optional command hooks.
This keeps scan-time I/O, selection policy, and side effects separate.

## Discovery contract

- A normal executable Skill is a local `SKILL.md` with valid opening frontmatter.
- Discovery reads at most 16 KiB from each candidate and never reads an entire Skill.
- A selected Skill is fully read by `run`, with path, content hash, and character count
  recorded in its work packet.
- `.codex/agents` and `.agents` are scanned separately. Agents remain role/process
  candidates, never executable Skills.
- Duplicate names receive an explicit group, metadata fingerprint, provenance, and
  deterministic resolution record.  The highest safe provenance tier becomes the
  canonical routable copy; lower copies remain indexed as `duplicate`/`shadowed`.
  Equal-authority copies fail closed as `duplicate_conflict`: discovery deliberately
  does not read full content merely to break a tie.  A disabled path is ineligible.
- Malformed and inaccessible candidates remain indexed with their reason rather than
  being silently treated as available.

## Ranking and chaining

Ranking combines task keyword/domain signals, description and tag overlap, project
scope, executable status, specificity, and overlap cost. The router caps the chain at
three Skills by default and drops weak overlap-only candidates. Optional `hub_after`
frontmatter expresses a genuine dependency; the router topologically orders selected
Skills and reports cycles or missing dependencies.

Registered sources are considered independently. References and frameworks are not
loaded as Skills. DeerFlow is considered only for a research/orchestration task that
signals genuinely complex coordination. `liquid-glass-react` is skipped for non-UI work.

## Invocation and validation

Natural-language Skills are instructions for Codex, not arbitrary executable code.
`run` proves their full load and hands their instructions to Codex. A local Skill can
opt into deterministic automation with JSON frontmatter arrays:

```yaml
hub_command: ["{python}", "-m", "pytest", "-q"]
hub_validate: ["{python}", "-m", "pytest", "-q"]
```

Hooks run only with `--allow-skill-commands`, use `shell=False`, resolve only
`{python}` and `{skill_dir}`, execute from that Skill directory, time out, and capture
bounded output. They are not a way to turn an arbitrary instruction file into a shell
script.

## Update policy

`check_updates.py` remains CHECK-ONLY. It records observed remote branch SHAs; it never
pulls, merges, installs, overwrites local/custom Skills, or changes an active project.

## V1.2 planner (additive)

V1.2 adds `ash.v2` and the explicit `python scripts/hub.py plan "<task>"`
entry point. It does not change the V1.1 route/run contracts and does not alter
the frozen `v1.1-final` tag.

```text
TaskProfile (Codex structured extraction when supplied; conservative parser fallback)
  -> bounded Project Context
  -> Rules and conflict detection
  -> capability requirements
  -> hard filters
  -> deterministic ranking
  -> greedy minimal-sufficient selection
  -> redundancy elimination
  -> ExecutionPlan / selected SKILL.md load / ValidationPlan / evidence packet
```

### Context and rules

Project context is read-only and progressive. V2 examines a small known set of
root-level governing/configuration files plus task-named files; it does not
recursively ingest repositories. The initial file/byte budgets are soft defaults.
Every expansion is recorded, while configurable hard ceilings reject giant files,
binary input, root escapes, secret-looking files, and silent truncation.

Rules are ordered: system/security constraints, explicit current-user
requirements, project-rule files, project Skills, installed Skills, advisory
Agents, then references. README text, external references, and ordinary repository
content are evidence only. Equal-priority incompatible rules block selection.

### Resource and execution boundary

- Skill: executable procedural instructions, loaded only after selection.
- Agent: advisory recommendation only; V2 never spawns or delegates one.
- Reference/Framework: visible reference-only metadata; never executed or loaded as a Skill.

The planner emits serializable `TaskProfile`, `ProjectContext`, `Rule`,
`CapabilityRequirement`, `ResourceCandidate`, `ExecutionPlan`, `ExecutionStep`,
`ValidationPlan`, `DecisionEvidence`, and `ReplanResult` records. A plan validates
coverage, duplicate selection, and selected-Skill loading. Artifact- and
task-specific validation checks are planned before execution handoff.

Only `wrong_resource`, `missing_capability`, and `bad_plan` can request a re-plan.
There is one re-plan maximum; implementation defects, dependency failures, and rule
conflicts report a focused repair path, blocker, or native Codex fallback instead.

V2 state is optional local evidence only. `--no-state` keeps planning in memory;
there is no cloud synchronization or automatic retention scheduler.
