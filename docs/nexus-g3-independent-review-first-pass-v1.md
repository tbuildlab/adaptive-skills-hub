# Original G3 independent review: first pass

Date: 2026-10-14. Reviewer: separately instantiated, Owner-authorized read-only
`g3_independent_review` Agent, not the implementation author. Scope SHA256:
`9e90cfc2b664020f9c2adbba004ca8bf401dced7086bb605037e30aa9cac9c7d`.
All 21 scoped raw file hashes matched before review. No files were modified.

**Result: FAIL. One High finding; no Critical finding identified.**

## High: relocated checkout can bypass terminal revocation

`scripts/g3_signed_local_approval.py:42-49` stores the only consumed marker under
`origin.ROOT/output`; `scripts/verify_g3_owner_signature.py:20` derives ROOT from
the checkout. An ordinary second checkout with the identical signed material,
payload, public key and signature can have a fresh output directory. While the
signed interval is valid and the key remains enrolled, it can create another
reservation and grant without consulting the first checkout's terminal revocation.
Neither deletion of original state nor malicious replacement of trusted Host
code is necessary. This violates the signed terminal instruction and original
G3 field 10's requirement that revocation block subsequent eligibility.

The reviewer recommended a stable spent-approval namespace independent of
checkout location, preservation of consumed state, and a relocated-checkout
negative regression. The live qualification must not be repeated.

## Independently checked supporting evidence

- In-memory SSHSIG Ed25519 verification succeeded for the exact retained public
  key, namespace and payload. Fingerprint matched
  `SHA256:5FV4/OvvMPzivK/4YIolW2kPQBGoik/llHbviTDpf98`.
- Exact signed subject, component/configuration/review digests, grant ID and
  registration bytes reproduced.
- Ten structured Host records reproduced their canonical hashes; the Markdown
  hash matched. Four action batches reconciled with twelve Git processes.
- Scope, revision, registration and validity comparisons were confirmed in code.
- Within the original live instance, invalidation precedes revocation persistence.
- Quarantine/fixture isolation and the unchanged production G3/G4 DENY boundaries
  were confirmed in the reviewed source.
- The bounded serializer preserves the valid retained registration bytes and
  grant identity. No second live task was claimed.

## Review limitations and disposition

The reviewer did not independently requery GitHub or rerun native OpenSSH. The
external Host harness was represented only by its digest and was outside the
21-file scope; eligibility-to-action and terminal-outcome wiring therefore remain
a review coverage limitation, not a finding that the retained run did not occur.
The reviewer did not run the suite, invoke the qualification constructor, create
reservations, invoke signers, inspect private material, or access cloud resources.

This record preserves the original FAIL. A later remediation/review must be a
separate successor. It grants no approval or execution authority. No G3 final
tag is permitted while the High remains unresolved. REAL_ADMISSION=NO.
