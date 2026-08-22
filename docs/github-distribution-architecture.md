# Nexus GitHub Distribution Architecture

## Scope

This release-candidate distribution layer packages accepted Nexus Runtime
R1/R2/R3 and the Desktop Plugin without changing Core routing, planning,
redaction, workspace allowlists, or the read/plan-only MCP boundary. It is
Windows-first, local-only, and does not introduce GitHub Skill Scout, Agent
runtime, remote MCP, OAuth, or V1.3.

## RC2 embedded-runtime correction

RC1 correctly rejected an unavailable Python command, but that made a fresh
standard Windows user fail before Nexus could configure itself. RC2 therefore
ships a **Nexus-owned CPython 3.13.15 x64 embeddable runtime**. Its official
Python.org archive name, source URL, version, and SHA-256 are pinned in
`release/windows-runtime.json`; the builder rejects any substitute archive.
The archive is extracted beneath the Nexus-owned release directory, never
added to `PATH`, never installed system-wide, and never used to change another
Python installation.

The release builder vendors the reviewed, hash-locked R2 wheels beside that
runtime and retains the full generated dependency hash lock. This is required because the official embeddable distribution omits
`pip`, and Python's Windows documentation recommends treating third-party
packages as application-vendored content for an embedded application. The
runtime remains offline at installation time. A duplicate wheelhouse is not
shipped because the verified vendored payload is already the offline runtime;
the duplication would only inflate the archive. A release update is a newly
verified artifact; it is never an automatic runtime download or downgrade.

| Option | Result | Decision |
| --- | --- | --- |
| A. Embedded official CPython bundled in the Release | Standard-user, offline activation; no Store, PATH, or developer runtime dependency; larger Windows-x64 artifact. | **Selected for RC2**. |
| B. Download Python during installation | Smaller initial artifact, but adds a network/supply-chain window and failure mode. | Rejected. |
| C. System Python prerequisite | Small artifact, but repeats RC1's fresh-user blocker and relies on user configuration/aliases. | Rejected. |
| D. Third-party runtime manager/packager | Could provide a launcher, but adds an unrelated distributor and update authority. | Deferred. |

The packaged Plugin MCP manifest points to the release-local runtime using the
fixed path `../../runtime/python/python.exe` from the Plugin directory. The
launcher still reads only its existing user-owned Nexus configuration and then
starts the fixed R2 stdio entry point. This avoids a second `python` lookup at
Plugin launch. The PowerShell bootstrap reports whether it found no system
Python, a Windows App Execution Alias placeholder, or a system Python command,
but treats all of them as informational and always uses the verified
Nexus-owned runtime.

The official CPython `LICENSE.txt` is retained inside the runtime. Before a
public release, the owner must retain/ship complete third-party notices for the
vendored wheels and make the Nexus public-license decision separately.

## RC3 host-CLI preflight correction

RC2 removed the Python prerequisite, but a fresh user without a runnable
Codex CLI still reached the first Plugin registration command and received an
opaque Windows `WinError 2`. RC3 treats the Codex CLI as a distinct, required
host dependency for **Plugin mode only**. Before it reads an existing MCP
registration, writes a lifecycle journal, changes Nexus-local configuration,
or invokes a Plugin command, it resolves the requested CLI and runs the
non-mutating `codex plugin --help` probe.

The installer reports one of three bounded errors: unavailable CLI, CLI that
cannot start, or CLI without the Plugin command. It does not fall back to
editing Codex or ChatGPT configuration files, copying an OpenAI binary, or
switching to standalone mode invisibly. A user who only has a ChatGPT Desktop
UI but no supported local Codex CLI therefore receives a precise prerequisite
error rather than a partial installation. Standalone mode remains available
for local MCP use, but it deliberately cannot claim `@Nexus` Plugin visibility.

## Artifact contract

Each GitHub Release candidate supplies a versioned ZIP, its SHA-256 receipt,
a PowerShell bootstrap, and a receipt for that bootstrap. The ZIP has exactly
one `Nexus-<version>` top-level directory. `release-manifest.json` contains an
exact allowlisted file set with a byte size and SHA-256 for each payload file.
The installer verifies that tree before it changes local configuration.

The release builder rejects missing/malformed wheelhouses, conflicting wheels,
and a Python archive that fails its pinned official hash. It writes a generated
lock with every wheel hash and vendors those wheels into the embedded runtime,
so installation never resolves packages from PyPI. It never
packages a developer checkout, workspace, credentials, cache, runtime state,
or absolute development path.

## Local lifecycle

Mutable data is restricted to `%LOCALAPPDATA%\Nexus` (or an explicit
`--data-root`): verified releases, the Nexus-owned embedded runtime,
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
`release/VERSION`; `0.1.0-rc.3` is a release candidate, not a Core tag. A
future GitHub Skill Scout must remain separately approved, preserve provenance,
license/reputation/pinned-hash review, and never turn this installer into an
automatic Skill installation channel.
