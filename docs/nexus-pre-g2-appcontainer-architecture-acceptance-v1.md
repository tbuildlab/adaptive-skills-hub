# Nexus Pre-G2 AppContainer/LPAC Architecture Acceptance Record v1

Decision ID: `nexus.pre-g2.appcontainer-architecture-acceptance.v1`

Decision version: `1.0.0`

Owner acceptance date: 24 September 2026

Status: **ACCEPTED ARCHITECTURE ALTERNATIVE AND PROTOCOL SUCCESSOR SPECIFICATION ONLY — NO EXPERIMENT OR RUNTIME AUTHORITY**

## Accepted subjects and exact bytes

The owner instructed acceptance after the independent review of the architecture/protocol pair concluded **ACCEPTABLE AS WRITTEN**. The accepted subjects are:

| Reviewed subject | Identity | UTF-8/LF SHA-256 | Bytes |
| --- | --- | --- | ---: |
| `docs/nexus-pre-g2-appcontainer-architecture-alternative-v1.md` | `nexus.pre-g2.appcontainer-execution-alternative.v1`, version 1.0.0 | `e50da530463b20d0b19b26c75d859f52f3f24e332dee975374e9ad5a38e9ec4b` | 26,790 |
| `docs/nexus-e2b-appcontainer-protocol-successor-proposal-v1.md` | `nexus.e2b.appcontainer-protocol-successor-proposal.v1`, version 1.0.0 | `b6b232efc03f93007dd5040eab67901fe168460bf1453ac3cad290b7f100e810` | 13,449 |

Their original **PROPOSED** status lines remain byte-for-byte intact. This record supplies the subsequent architecture acceptance. A hash, this record, and the acceptance commit are correlation and integrity evidence, not a credential, qualification result or execution grant.

## Accepted meaning and retained holds

- **Option D remains the current state.** No complete positive G2 Host binding exists. The accepted trusted-launch Option A remains on HOLD for the separate `NexusTest` identity model; this alternative does not reopen Option A or resolve its primary-token source.
- Alternative 3 conditionally replaces the distinct `NexusTest` executor SID only for the proposed fixed-purpose, owner-created Windows LPAC qualification path. An ordinary same-user subprocess, generic runtime, privileged broker/service, password transfer or weaker AppContainer fallback is not accepted.
- The accepted Pre-G2 A0–A6 text, frozen Roadmap V2 and G1, and R2/R4/R5 interfaces are unchanged. A positively qualified complete Host/tool graph and independent task authority remain prerequisites for G2 implementation.
- The companion protocol document is an **accepted minimum successor specification**, not the complete versioned E2B qualification protocol. The historical separate-account protocol and G0 attempts are preserved. Before any E2B G0 in this mode, a complete versioned successor protocol and fresh owner authorization remain required; earlier G0/G1 grants do not transfer.
- An empty-capability local LPAC PASS and an exact network-capable LPAC PASS, if separately authorized and achieved, are distinct. Neither is E2B qualification, `ITEM_B PASS`, a positive complete Host binding or G2 acceptance.
- This architecture acceptance alone authorizes no AppContainer profile, launcher, local experiment, credential use, E2B Sandbox, first untrusted command, G2 implementation, merge, push, tag or freeze. Any later activity must satisfy its separate owner instruction and every prerequisite in the accepted subjects.

## Repository integration and validation

This acceptance adds only the two reviewed subjects, this one record, and their generated entries in the current source `MANIFEST.json`. The portable-package document allowlist remains unchanged; these governance documents are not runtime inputs. The original E2B protocol's external `MANIFEST.sha256` and prior attempts remain untouched.

The initial clean external source snapshot, containing the two reviewed subjects but not this record, generated a deterministic 142-entry static manifest. All 11 affected package/isolation regression tests passed. Two portable-package builds were byte-identical with 114 members and SHA-256 `15ec05afea2270cea88ce0a57847cc278eca3dd65ac87cd4c72b3f0be4f407fb`, matching frozen G1. The final clean snapshot, including this record, generated a 143-entry source manifest: all prior 140 entries were unchanged and only the three governance documents were added. The same 11 tests passed; two final portable-package builds remained byte-identical with 114 members and the frozen G1 hash. The final manifest, frozen files/refs, Git whitespace, repository integrity and staged diff are checked before committing.

These checks validate documentation and package isolation only. They do not prove LPAC behavior, credential isolation, provider cost enforcement, E2B qualification or a G2 Host binding.
