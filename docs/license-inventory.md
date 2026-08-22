# Nexus restricted distribution license inventory

| Component | Origin | License/status | Distribution decision |
| --- | --- | --- | --- |
| Nexus source and Desktop Plugin | Nexus private repository | Proprietary restricted release candidate; no public license grant | May be shared only through owner-authorized private GitHub Releases. |
| Nexus personal Marketplace adapter and copied Plugin bridge | Nexus private repository; Marketplace state under `~/.agents/plugins/nexus-marketplace`, host-indexed Plugin under `~/plugins/nexus-desktop` | Same restricted Nexus source status; generated machine-local paths are not release payload | Created only by the verified installer; no ChatGPT/Codex binary, cache, or host configuration is redistributed. |
| Nexus-owned CPython runtime (RC2) | Python.org `python-3.13.15-embed-amd64.zip` | PSF-2.0; official `LICENSE.txt` retained in artifact | Bundled only after pin/hash verification in `release/windows-runtime.json`; no system-wide installation. |
| Nexus Runtime R2 MCP dependency and resolved wheels | `mcp==2.0.0` plus reviewed wheelhouse | Third-party notices/license review required before public release | Vendored only in owner-authorized private RC artifacts; retain complete notices before public redistribution. |
| Personal/local Skills and workspace data | User machine | Unknown or user-controlled | Never copied, packaged, or redistributed. |
| ChatGPT/Codex runtime and plugin host | OpenAI product | Not redistributed | Required host only; no binaries or caches included. |

This release candidate does not claim public-release rights. A separate owner
decision is required before a public repository, marketplace submission, or
public GitHub Release asset.
