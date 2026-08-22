# Nexus GitHub Distribution Architecture

## Scope

This release-candidate distribution layer packages accepted Nexus Runtime
R1/R2/R3 and the Desktop Plugin without changing Core routing, planning,
redaction, workspace allowlists, or the read/plan-only MCP boundary. It is
Windows-first, local-only, and does not introduce GitHub Skill Scout, Agent
runtime, remote MCP, OAuth, or V1.3.

## Artifact contract

Each GitHub Release candidate supplies a versioned ZIP, its SHA-256 receipt,
a PowerShell bootstrap, and a receipt for that bootstrap. The ZIP has exactly
one `Nexus-<version>` top-level directory. `release-manifest.json` contains an
exact allowlisted file set with a byte size and SHA-256 for each payload file.
The installer verifies that tree before it changes local configuration.

The release builder rejects missing/malformed wheelhouses and conflicting
wheels. It writes a generated lock with every wheel hash. Installation creates
the R2 virtual environment using `pip --no-index --require-hashes`, so it never
resolves packages from PyPI during normal release installation. It never
packages a developer checkout, workspace, credentials, cache, runtime state,
or absolute development path.

## Local lifecycle

Mutable data is restricted to `%LOCALAPPDATA%\Nexus` (or an explicit
`--data-root`): verified releases, the Nexus-owned virtual environment,
workspace allowlist, launch config, backups, and transaction journals. These
files are Git-ignored and are never part of a release artifact.

The lifecycle is `verify -> preflight -> journal -> host activation -> atomic
Nexus config -> commit`. A failure restores prior Nexus config and a safely
captured standalone registration. `uninstall` removes only Nexus-owned config;
`rollback` restores the state before the activation; `upgrade` is another
explicit verified activation, never an automatic download or downgrade.

## Host modes

| Mode | Purpose | Rule |
| --- | --- | --- |
| `plugin` | ChatGPT Desktop `@Nexus` and Codex Plugin workflow | Default; official `codex plugin` lifecycle only. |
| `standalone` | Existing R3 `nexus-r2-local` local MCP workflow | Does not install the Plugin. |

Only one Nexus MCP registration may be active. If `nexus-r2-local` exists,
Plugin installation fails closed. `--migrate-standalone` is explicit and only
accepts a losslessly restorable stdio mapping returned by the official CLI. It
uses the CLI to remove/restore the mapping and never edits Codex TOML.

## Threat controls

| Threat | Control |
| --- | --- |
| Artifact tampering | ZIP receipt plus exact per-file manifest validation. |
| Archive traversal/symlinks | Bootstrap and extractor reject absolute, drive, `..`, multi-root, and symlink entries. |
| Local configuration tampering | Strict schema and real-path validation; only Nexus-owned state is written. |
| Dependency confusion | Reviewed offline wheelhouse and hash-locked installation. |
| Interrupted activation | Fresh extraction target, durable journal, atomic writes, prior-state restoration. |
| Privilege or execution expansion | Per-user paths, no shell, no elevation, no remote/OAuth; existing fixed read/plan-only MCP tools remain unchanged. |

SHA-256 proves integrity only when the user obtains the receipt from a trusted
project-owned GitHub Release. Public distribution additionally needs an owner
decision on licensing and a signed-publisher/provenance policy; this RC makes
neither claim.

## Versioning and future compatibility

Frozen Core tags stay unchanged. Distribution has a separate SemVer stream in
`release/VERSION`; `0.1.0-rc.1` is a release candidate, not a Core tag. A
future GitHub Skill Scout must remain separately approved, preserve provenance,
license/reputation/pinned-hash review, and never turn this installer into an
automatic Skill installation channel.
