# Nexus G2 Host Qualification Scope and Exit Acceptance Record v1

Decision ID: `nexus.g2.host-qualification-scope-exit-acceptance.v1`

Decision version: `1.0.0`

Owner acceptance date: 27 September 2026

Status: **ACCEPTED G2 HOST QUALIFICATION SCOPE AND FINITE EXIT BOUNDARY — G2 HOLD**

## Accepted subjects

The owner explicitly accepted the following exact documents after the separate adversarial review concluded **ACCEPTABLE AS WRITTEN**. Their original proposal and review status wording remains unchanged; this record supplies the subsequent owner acceptance.

| Accepted subject | SHA-256 | Bytes |
| --- | --- | ---: |
| `docs/nexus-g2-host-qualification-scope-and-exit-decision-v1.md` | `6cf3ab004b66580531185e7e0ce7394aa349ecb3e1e3905f224ed0259bbfcd69` | 29,767 |
| `docs/nexus-g2-host-qualification-scope-and-exit-review-v1.md` | `9d37d862f0a599ce309e3d31e5d03e35d6ddb59774f46a5bb8cab8deaa1df47c` | 8,387 |

## Accepted meaning and remaining gates

HQ1–HQ5 define the finite exit for the exact local LPAC qualification boundary. A complete positive G2 Host binding additionally requires HQ6 on one accepted capability and exact supported Host configuration. Other Host candidates must establish equivalent security properties within their actual boundary. Qualification PASS, if later obtained, does not itself grant task authority, G2 implementation authority or G2 acceptance.

This acceptance governs scope and the future change-control rule; it does **not** replace the controlling local protocol's pre-resume zero-entry PSS gate, the accepted Owner Release mapped-byte gate, or any current STOP condition. A replacement evidence mechanism requires a separately reviewed and owner-accepted versioned protocol and, where an accepted architecture promise changes, a bounded architecture amendment. Exact implementation/package bytes and experiment execution require their own approvals. Historical accepted documents and evidence remain unchanged.

Pre-G2 A0–A6, G1, R2/R4/R5, the accepted LPAC identity/capability and package/evidence boundaries, Option D, and Option A HOLD remain unchanged. Local LPAC Scenarios 01–04 remain **NOT RUN**; local qualification is **UNKNOWN**; positive complete Host binding is **ABSENT**; G2 remains **HOLD**. This record authorizes no PSS replacement, controller/watchdog/verifier change, qualification package, LPAC scenario, E2B/HQ6 experiment, G2 runtime implementation, merge, push, tag or freeze.

## Repository integration

The static source `MANIFEST.json` records the two unchanged accepted subjects and this acceptance record under the existing versioned-document pattern. The portable runtime package allowlist remains unchanged. Only a focused local acceptance commit is authorized; this record is not a qualification or release receipt.
