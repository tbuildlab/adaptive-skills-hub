# Nexus Pre-G2 LPAC Verifier/Watchdog Responsibility Acceptance Record v1

Decision ID: `nexus.pre-g2.lpac-verifier-watchdog-responsibility-acceptance.v1`

Decision version: `1.0.0`

Owner acceptance date: 28 September 2026

Status: **ACCEPTED BOUNDED RESPONSIBILITY AMENDMENT — QUALIFICATION UNKNOWN; G2 HOLD**

## Accepted subjects and exact bytes

The owner explicitly accepted the following exact amendment and its reviewed scope. The separate adversarial document review concluded **ACCEPTABLE AS WRITTEN FOR OWNER ACCEPTANCE**. Historical proposal/review headings remain intact; this record supplies acceptance.

| Accepted subject | SHA-256 | Bytes |
| --- | --- | ---: |
| `docs/nexus-pre-g2-lpac-verifier-watchdog-responsibility-amendment-v1.md` | `4c49754a1e25db097cbb2d17bec1611a9306b971b75795c17b98b14902d821b3` | 26,452 |
| `docs/nexus-pre-g2-lpac-verifier-watchdog-responsibility-review-v1.md` | `586c5aac40f591ef4cb957004f38812c1931bb8375e2762cece20a0f332561ab` | 14,226 |

## Exact supersession and preserved boundary

Amendment §2 supersedes **“Verifier watches only controller”** in the accepted Owner Release Verifier Implementation Spec v1, its controller-only creation/observation scope, and the expressly named controller-created watchdog/temporary debug-detach/cross-check-only allocations in the Owner Release Boundary Amendment and Evidence Successor Protocol. The existing fixed-purpose verifier directly creates and continuously observes the corresponding fixed watchdog from creation through required actual-loaded provenance, late loads, cleanup and exit. No detach/attach handoff is permitted. The controller retains LPAC creation/observation and Job-management duties; the watchdog retains independent controller-loss/deadline cleanup under the accepted failure contract A–I and bounded observer-loss abort requirements.

The verifier remains confined to the four fixed sequential qualification scenarios and existing exact recovery path. No generic debugger, launcher, Host executor, arbitrary observer, service/broker, recursive verifier or production Nexus runtime capability is authorized. A0–A6, finite HQ1–HQ5 criteria, actual-loaded Nexus-controlled provenance, bounded Windows TCB provenance, same-process held-object/PID/creation-time binding, protected custody, Job, effective environment/workdir/TEMP, HQ3 handle evidence and fail-closed UNKNOWN/STOP remain controlling. Every unaffected historical clause and accepted artifact is preserved; V2 is not modified.

## Remaining authority gates

Acceptance does not ratify the interrupted unaccepted handoff implementation, approve a package, establish runtime PASS or authorize formal qualification. In the same explicit owner request, the owner separately authorizes bounded implementation/static analysis/safe nonqualification tests and, only after an acceptable implementation review, preparation/sealing of a new V3 candidate. That separate authority does not come from this acceptance record and remains subject to the amendment, exact-byte review, existing package boundary and all stated hard STOP conditions.

Scenario 01–04 are **NOT RUN** and not authorized by that preparation request. HQ1–HQ5 are **NOT PASS**. HQ6, E2B/provider contact, Positive Host Binding and G2 runtime remain prohibited; Positive Host Binding is **ABSENT** and G2 is **HOLD**. Option D and Option A HOLD remain unchanged. No password/credential transfer, elevation, security-policy weakening, breakaway, privileged broker/service or fallback is permitted.

## Repository integration

The repository's existing source `MANIFEST.json` pattern records the two accepted subjects and this minimal acceptance record using LF-normalized bytes. The portable runtime package allowlist is unchanged. One focused acceptance commit records only these architecture documents and their manifest additions. No merge, push, tag or freeze is authorized.
