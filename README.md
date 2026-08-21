# Adaptive Skills Hub V1.1

A Codex-first meta-skill for automatically discovering, selecting, loading, chaining, and executing relevant skills instead of merely recommending them.

## V1 capability

Task -> Discover -> Rank -> Load -> Execute -> Validate -> Report

The hub separately indexes:
- skills
- agents
- reference repositories
- frameworks

## Local use

This approved V1.1 stays at:

`D:\chatgpt\安装skills\adaptive-skills-hub`

It is intentionally not installed into the user-wide Codex Skills directory yet. In a
Codex session that has loaded this Skill, run the router and then carry out the task:

```powershell
python scripts/hub.py rescan
python scripts/hub.py route "Improve this React dashboard UI."
python scripts/hub.py run "Improve this React dashboard UI." --packet state/example-packet.json
```

The skill's description is intentionally broad enough that Codex can also select it automatically when capability routing is useful.

`route` uses metadata only. `run` then fully reads each selected Skill's `SKILL.md`.
For normal natural-language Skills, Codex follows those loaded instructions to do the
work. Optional local `hub_command` arrays can automate deterministic steps only when
the caller additionally passes `--allow-skill-commands`; execution never uses a shell.

## First commands

Rescan real local Skills and Agents, then rebuild the combined registry:

```bash
python scripts/hub.py rescan
python scripts/rebuild_registry.py
```

Check upstream revisions safely:

```bash
python scripts/check_updates.py
```

The update check is CHECK-ONLY.

## Adding another source

Edit `sources.json`, append the source, then run:

```bash
python scripts/rebuild_registry.py
```

No rewrite of `SKILL.md` is required.

## Important architecture rule

- Skill = executable workflow/instructions
- Agent = specialist role/process
- Reference = patterns/examples
- Framework = orchestration/runtime
- Project rules = highest-priority local requirements

Do not flatten all of these into one giant prompt.

See [docs/architecture.md](docs/architecture.md) for contracts, safety boundaries, and
the exact rescan/route/run flow. Run `python -m unittest discover -s tests -v` for the
acceptance suite.

The frozen V1.1 evidence snapshot is in
[docs/v1.1-final-baseline.md](docs/v1.1-final-baseline.md).
