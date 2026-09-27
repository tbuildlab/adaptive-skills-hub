# Nexus Pre-G2 LPAC Owner Release Boundary Acceptance Record v1

Decision ID: `nexus.pre-g2.lpac-owner-release-acceptance.v1`

Decision version: `1.0.0`

Owner acceptance date: 27 September 2026

Status: **ACCEPTED BOUNDED ARCHITECTURE AMENDMENT — IMPLEMENTATION AND FALSIFIABLE LOCAL TESTING AUTHORIZED — LOCAL QUALIFICATION NOT PASSED**

## Accepted subjects and exact bytes

The owner explicitly accepted the Owner Release / Launch Verification Boundary Amendment v1 after the final static adversarial review concluded **ACCEPTABLE AS WRITTEN as a proposed bounded amendment**. The original owner-protected evidence files matched `evidence-index-v2.json` before integration. Exact byte copies are retained in this repository:

| Accepted subject | SHA-256 | Bytes |
| --- | --- | ---: |
| `docs/nexus-pre-g2-lpac-owner-release-boundary-amendment-v1.md` | `bb47ba854f5322238b2d78e274f264b1653855cb26aa91ee375baa7fce05bf67` | 11,129 |
| `docs/nexus-pre-g2-lpac-owner-release-verifier-implementation-spec-v1.md` | `04f1974f214b8032966d70cb81feef93b2c371c979ce13de20b5c2fcc1b285fb` | 10,716 |
| `docs/nexus-pre-g2-lpac-owner-release-adversarial-review-v1.md` | `f8cc47c34c4076f58ff7e6536a9f8aa6be6e1f73ca03cd9631cfecd3434be8c6` | 2,364 |

Their original proposal/review status wording remains unchanged. This record supplies the subsequent owner acceptance; a hash or review conclusion alone does not. The previous package-delivery decision and review retain their exact bytes.

## Accepted boundary and authorization

This is a bounded amendment to Package Delivery Boundary Decision v1 §§4–6 solely for the fixed owner-release path: one non-elevated, same-owner, fixed-purpose verifier may replace the direct owner-to-controller launch for the four predetermined local LPAC cases and the fixed case-03 recovery. It cannot become a generic launcher, generic Host executor, arbitrary-command/path/policy interface, privileged broker or service. Its exact source, binary, dependencies, destination bytes, ACL/object identity, loaded-image evidence, same-process dependency evidence, no-outer-Job state, controller/watchdog independence, crash cleanup and owner-only receipts require separate implementation and runtime verification.

The owner's continuous authorization accompanying this acceptance permits bounded implementation, strict compilation/static analysis, trusted staging, falsifiable verifier-specific local tests, and the four local LPAC scenarios **only after every preceding mandatory gate passes**. It does not turn an UNKNOWN into PASS, approve unreviewed exact package bytes where the accepted package decision requires separate exact-byte owner approval, or authorize use of the existing `qualification_authorized=false` v1 package for execution. If a physical out-of-Codex owner launch or separate exact-byte approval is mandatory, prepare all safe independent work and stop at that gate.

Pre-G2 A0–A6, the accepted LPAC identity/isolation/capability requirements, Package Delivery Boundary protections, fail-closed STOP rules, owner evidence custody and no-outer-Job requirement remain unchanged. No elevation, Task Scheduler, `CREATE_BREAKAWAY_FROM_JOB`, password transfer, privileged service/broker, NexusTest/Option A fallback, network capability, E2B, credential-value access or G2 runtime is authorized. The verifier's extra trusted-code exposure is accepted only within the reviewed fixed scope.

Actual Windows event ordering, non-null debug file handles, actual mapped main/dependency bytes, verifier/controller debugger coexistence, path stability, effective environment and handles, watchdog/recovery binding, crash cleanup and Scenario 01–04 remain **UNKNOWN** until observed and reviewed. Any missing or contradictory mandatory fact is STOP. No local LPAC PASS, network-capable LPAC qualification, E2B qualification, positive complete Host binding or G2 acceptance follows from this record. Option D and G2 HOLD remain current.

## Repository integration

The static source `MANIFEST.json` records the exact three accepted subjects and this acceptance record under the repository's existing versioned-document pattern. Portable runtime package membership is unchanged by these governance documents. No frozen Roadmap, G1, R2/R4/R5 artifact or A0–A6 text is modified. A focused commit may record this acceptance after manifest, regression, scope and integrity checks; it is not a merge, push, tag or freeze.
