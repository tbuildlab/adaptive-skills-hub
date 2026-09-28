# Nexus Pre-G2 Current Local LPAC Host Qualification Exit Decision v1

Decision ID: `nexus.pre-g2.current-lpac-host-exit.v1`

Version: `1.0.0`

Date: 28 September 2026

Status: **DOCUMENTARY EXIT DECISION FOR OWNER ACCEPTANCE — CURRENT HOST QUALIFICATION BLOCKED — NO EXECUTION AUTHORITY**

## 1. Decision and authority

Stop further qualification work on the current Windows build `26200.9550` local LPAC binding. Preserve the work and its unresolved results. The owner's explicit instruction to stop is operative now; this versioned record and its separate review await repository acceptance. No final acceptance record, MANIFEST integration, commit, tag or freeze is made by this task.

Repository: `D:\chatgpt\安装skills\adaptive-skills-hub`; branch `nexus-v2-g2-development`; clean starting HEAD `45407f501d4225e06105f0eafc6b010d516ed66e`.

This closes the current investigation with **HOST QUALIFICATION BLOCKED**, not qualification PASS or a security FAIL. It concerns the fixed, non-elevated interactive De Yong, empty-capability, synthetic, secret-free local LPAC configuration. It does not reject AppContainer/LPAC on other bindings, Windows generally, a provider candidate, or the Nexus G2 architecture.

## 2. Exact binding and blocking evidence

| Item | Recorded identity or result |
| --- | --- |
| OS binding | Windows build `26200.9550`; no qualification claim transfers to another build or machine |
| Owner SID | `S-1-5-21-3218463879-272414157-1910845735-1001` |
| Sealed delivery | `C:\Users\De Yong\NexusQualification\LPAC-Local-Delivery-v4` |
| Manifest | `package\07-pre-execution-package-manifest-v6.json` |
| Manifest SHA-256 | `2B907CD25868124C244E6C350EA13CFFCC041562EA0E9AD479197F6B83D3D3C4` |
| Owner collector | `package\08-owner-ci-readback-v1.ps1` |
| Collector SHA-256 | `5B855B3B3E9A0E2AE6C10154D647B27DB8219257F9F9186A06DF141C434E9735` |
| Native CI mask | `62469 = 0xF405` |
| Required known mask | `0x0405`; all required bits present |
| Additional defined set bits | `0x1000` and `0x2000`; known set portion is `0x3405` |
| Known forbidden mask | `0x08FA`; intersection with observed mask is zero |
| V4 classified range | `0x3FFF`; unclassified set portion is `0xC000` |
| Unresolved bits | `0x4000` and `0x8000`; neither classified as harmless |
| Owner diagnostic outcome | Query status `0`, returned length `8`, collector exit `0`; `CI_BUNDLE=UNKNOWN` |

The owner supplied the physical ordinary non-administrator PowerShell `Inspect` transcript outside Codex Desktop. It reports kernel/user CI and VBS status 2, memory integrity configured/running, and the mask above. Package and collector hashes were independently reread locally. The physical execution context is owner-supplied evidence, not a newly observed qualification process. The diagnostic lacks the formal attempt nonce/package-bound before/during/after qualification records. Its schema name does not make it a release receipt. No exit code, hash match or aggregate status is converted to CI PASS.

## 3. Research result and unknown-flag decision

The authorized one-time provenance investigation concluded **AUTHORITATIVE SEMANTICS NOT AVAILABLE** within its checked sources. Current Microsoft API documentation, installed SDK `10.0.26100.0`, SDK metadata and the checked Microsoft-published Win32 header did not supply the required two-bit mapping and applicability proof. Existing ntdll public PDB name discovery supplied no mapping; the attempt to obtain a usable matching public `ci.pdb` did not produce verified semantic evidence. Third-party WHQL labels remained discovery leads only. This is not a claim that Microsoft has no internal definition or that every possible public artifact was searched.

The separate bounded architecture analysis concluded **ALL UNKNOWN NATIVE CI BITS MUST REMAIN HARD STOP under the current accepted local evidence architecture**. Semantic knowledge is not itself the security property, but the accepted property still includes effective required CI enforcement without a relevant unknown audit, exemption or bypass state. Protected bytes and actual-loaded provenance establish code identity; they do not independently establish all of that execution state. A lack of authoritative weakening reports is not positive proof of irrelevance. No concrete accepted replacement mechanism closes this gap.

The accepted CI Evidence Amendment v1 §5 CI2 and its acceptance remain controlling. This exit record changes neither that gate nor the fixed classifier. It makes no claim about what the two bits actually do. The preceding research and architecture findings are owner-visible conversation evidence summarized here; they are not represented as previously accepted repository decisions or authenticated OS receipts.

## 4. Why the current binding cannot continue

The missing fact is sufficient interpretation or accepted independent proof of the effective CI boundary for this exact binding. All conjunctive CI1–CI7 gates remain required. A normal launch, a signature, a complete disk inventory, one historical block, or a later LPAC negative test cannot alone replace CI2. Runtime evidence for the other gates is also unearned; this CI blocker is not the only remaining work that would follow a legitimate reopening.

The Windows system-module provenance exception relies on the accepted kernel/loader/CI TCB at its stated scope. Using its provenance result to prove its own uncertain CI premise would be circular. The owner's exit avoids further investigation; it does not declare that premise proven or disprove Windows security.

Do not change CI/Application Control/Device Guard, clear flags, elevate, sign/rebuild/substitute to evade a refusal, or run a qualification executable to turn this STOP into PASS. Do not repeat the same successful `Inspect` action or continue searching indefinitely. A new observation, API or passage of time alone does not reopen this binding.

## 5. Preserved assets and honest reuse

| Asset | Disposition |
| --- | --- |
| V4: all 52 manifest-bound members plus manifest and protected directory identities | Preserve exactly; unqualified static candidate, not a reusable runtime PASS |
| V1–V3, working checkpoints, prior failed/blocked attempts, source/build/static analysis and denial records | Retain historical bytes and scope; no deletion, overwrite or retroactive success |
| Fixed verifier/controller/watchdog/recovery/probe/canary and PDB helper source | Preserve reviewed source and finite roles; adapt only under later route-specific authority |
| Compiled Windows executables, Windows module inventories, PDBs, PE barriers and OS pins | Host-specific; no unconditional reuse on a changed OS or route |
| Same-process custody, ordered receipts, input denial, containment-before-release, cancellation/crash/deadline and cleanup contracts | Reusable security requirements; exact APIs and cases remain route-specific |
| G1 profiles/conformance, A0–A6, Roadmap contracts, accepted Scope & Exit and evidence amendments | Preserve accepted architecture; profile data and documentary acceptance grant no dispatch authority |
| E2B G0 Attempts 01–04 and provider/F2 screens | Preserve dated evidence; no current account, cost, resource or authorization inference |

Primary working checkpoint: `C:\Users\De Yong\AppData\Local\Temp\NexusG2BoundedEvidenceImplementation-20260928\ci-successor-final-checkpoint-v1.json`. Its historical next action was completed by the later Owner Inspect transcript; the file itself is not rewritten. The consolidated report and deterministic precreation/rollback records in that directory are retained. No qualification profile/process tree was created by this exit task; no cleanup operation or cleanup PASS is claimed.

## 6. Bounded reopening conditions

Reconsideration requires owner authorization for a named evidence change and one of the following concrete triggers; none automatically authorizes execution:

1. **Authoritative semantics:** Microsoft evidence binds both bit values and their interpretation/applicability to the exact API/build. Review its effect on every preserved security property, resolve contradictions and review a separately versioned classifier/package successor if bytes must change. A symbolic label without applicability and security analysis is insufficient.
2. **Accepted independent evidence mechanism:** a concrete finite mechanism demonstrates the required effective-state properties without relying on the unresolved semantics. It must undergo separate architecture/protocol review and explicit owner acceptance before implementation or activation; absence of a warning, code identity and finite historical negatives alone do not satisfy it.
3. **Different Host/build:** an owner-identified supported environment presents a new exact binding. Establish fresh required CI and trust evidence without reducing security, repin dependent artifacts and separately qualify that binding. A changed build is a new candidate, not continuation of this candidate's PASS.

In every case preserve V4 and earlier evidence, prohibit silent fallback, require current custody/identity/freshness and all affected mandatory gates, and obtain separate exact-byte experiment authorization. An unresolved bit, contradiction, unauthoritative interpretation, newly required privilege/broker, policy bypass, stale binding or unavailable mandatory observation retains STOP. Changes do not grant HQ6, network/E2B, runtime, commit or release authority.

## 7. State and next documentary step

`CI_BUNDLE=UNKNOWN/STOP`; qualification readiness **BLOCKED**; Scenario 01–04 **NOT RUN**; HQ1–HQ5 **NOT PASS**; Positive Host Binding **ABSENT**; G2 **HOLD**. A0–A6, G1 and frozen R2/R4/R5 remain unchanged. Option D remains current; Option A remains HOLD.

The companion [exit review](nexus-pre-g2-current-lpac-host-exit-review-v1.md) reviews this document only. After that review, the [next-route decision](nexus-g2-next-host-route-decision-v1.md) provides a finite comparison and future first experiments. Neither document grants selection, implementation, credentials, provider contact, package release or experiment authority. No final repository acceptance record is authorized here.

## 8. Sources and limits

- Owner instruction: `C:\Users\De Yong\.codex\attachments\92da3e04-fda5-4535-83fa-797af4f13ee9\已粘贴的文本.txt`; prior Owner Inspect, bounded provenance result and unknown-flag adjudication in this conversation.
- [CI evidence amendment](nexus-pre-g2-lpac-code-integrity-evidence-amendment-v1.md) §§2, 4–7 and [acceptance](nexus-pre-g2-lpac-code-integrity-evidence-acceptance-v1.md).
- [Scope & Exit](nexus-g2-host-qualification-scope-and-exit-decision-v1.md) §§2–3, 8–9 and [acceptance](nexus-g2-host-qualification-scope-and-exit-acceptance-v1.md); [system-module provenance](nexus-pre-g2-lpac-owner-release-system-module-provenance-amendment-v1.md) §§2–3 and its [acceptance](nexus-pre-g2-lpac-owner-release-system-module-provenance-acceptance-v1.md).
- Sealed V4 protocol `package\05-local-qualification-protocol-v6.md`, fixed CI contract and manifest above; working final report `ci-successor-owner-review-final-report-v1.md` in the checkpoint directory.
- [Microsoft CI readback contract](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntquerysysteminformation) and installed `C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um\winternl.h`. Documentation is not experimental qualification evidence.
