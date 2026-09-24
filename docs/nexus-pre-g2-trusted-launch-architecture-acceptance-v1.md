# Nexus Pre-G2 Trusted-Launch Architecture Acceptance Record v1

Decision ID: `nexus.pre-g2.trusted-launch-architecture-acceptance.v1`

Decision version: 1.0.0

Owner acceptance date: 24 September 2026

Status: **ACCEPTED ARCHITECTURE HOLD — NO IMPLEMENTATION OR RUNTIME AUTHORITY**

## Owner decision and accepted subject

The owner explicitly instructed formal acceptance of `docs/nexus-pre-g2-trusted-launch-architecture-decision-v1.md` after its independent review concluded **ACCEPTABLE AS WRITTEN**. The accepted subject is document ID `nexus.pre-g2.trusted-launch-decision.v1`, version 1.0.0, with unchanged UTF-8/LF SHA-256 `c672d58d56de3aedff9189ecc2df0bce1936095e214dc3f659cee1604732d41e` (20,900 bytes).

The subject's original **PROPOSED** status line is preserved byte-for-byte as the reviewed document state. This acceptance record supplies the subsequent owner acceptance status; it does not rewrite the reviewed evidence. Neither the document hash nor this record is an executable grant, Host qualification, or credential.

## Accepted boundary

- **Option D remains the current architecture state.** No positive G2 Host binding exists, and independently verifiable trusted launch is unresolved.
- **Option A remains conditional.** No launcher implementation or implementation experiment is authorized. `NexusTest` primary-token provenance remains unresolved. Password transfer and privileged broker/service approaches do not satisfy this decision's Option A exit-from-HOLD criteria; considering either requires a separate explicit architecture alternative decision and separate owner acceptance.
- E2B Sandbox creation, first untrusted execution, and G2 implementation remain prohibited. Accepting this decision is neither E2B qualification nor G2 acceptance.
- The accepted Pre-G2 addendum's A0–A6, the frozen Roadmap V2 and G1 baselines, and R2/R4/R5 interfaces remain unchanged. This record grants no execution, installation, activation, approval, delegation, concurrency, or release authority.

## Repository integration

This acceptance adds only the reviewed decision, this minimal acceptance record, and their generated entries in the current source `MANIFEST.json`. The existing portable-package document allowlist is unchanged; these governance documents are not portable runtime inputs. No existing frozen artifact or tag is modified, and no push, merge, tag, or G2 freeze is part of this acceptance.

## Validation boundary

A clean external source snapshot was used for release-source checks because the live development checkout contains local state and Git object directories rejected by the existing package boundary. The manifest was deterministic with 140 entries: the prior 138 were unchanged and only the two governance documents were added. All 11 affected package/isolation regression tests passed. Two portable-package builds were byte-identical, retained 114 members, excluded these governance documents, and matched the frozen G1 package SHA-256 `15ec05afea2270cea88ce0a57847cc278eca3dd65ac87cd4c72b3f0be4f407fb`.

The current source manifest validated against all 140 file bytes and hashes. The accepted A0–A6 addendum retained SHA-256 `b6680c710dda8fb7808e06cc2569fd1bb6a4aeed47b2223f9626e411e298be14`; frozen tag targets were unchanged. Git whitespace and integrity checks found no errors; `git fsck --full` reported only dangling blobs. These documentation-only checks do not rerun or recertify the full frozen G1 regression and do not establish any Host capability.
