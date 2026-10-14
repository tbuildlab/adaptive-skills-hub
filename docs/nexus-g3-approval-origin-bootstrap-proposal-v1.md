# Original G3 approval-origin audit and single bootstrap proposal v1

Date: 2026-10-14. **PROPOSED / NOT ACCEPTED / NO AUTHORITY CREATED**.
Baseline: `9a6760ad9ed584a03db3b0e6c5e5e882e0e280f7`.
Scope: original Roadmap V2 G3 approval origin only. This is not N01 or an
authentication redesign. G2/G4 and the historical research HOLD remain unchanged.

## Narrow audit of existing mechanisms

| Existing mechanism inspected | Observed fact | G3 disposition |
| --- | --- | --- |
| Actual current Host tool interface | No callable exact-subject human-approval attestation/export verifier is surfaced. This session has approval policy `never`; no human command-approval event was generated or claimed | NO ADMISSIBLE SOURCE DEMONSTRATED in this surfaced subset; not a claim about every possible Host |
| Official Codex App Server protocol | Documents client approval decisions and account information as separate interfaces; neither document establishes an already integrated Nexus exact-subject approval verifier | REUSABLE TRANSPORT / UNQUALIFIED ORIGIN. No new app-server, login, credential read or account operation was started |
| Existing Nexus Host approval bridge | `OFFLINE_CONTRACT_ONLY`, `owner_authenticated=false`, `approval_authority=none` | NOT AN AUTHENTICATED SOURCE |
| Existing Core opt-in, Host mappings, inventory tickets and receipts | Bind tasks, descriptive mappings and observations; do not authenticate a separate capability-approval issuer | NOT AN APPROVAL SOURCE; unchanged |
| Existing Slice 3C signature evidence | Supports `NOT_EVALUATED`, `MISSING`, `PRESENT_UNVERIFIED`; present bytes remain zero-authority evidence | NOT A VERIFIED ISSUER; unchanged |
| Existing accepted repository acceptance/binding documents | Preserve historical Owner acceptance and exact subjects, but supply no generic cryptographically verified G3 issuer mechanism | HISTORICAL ACCEPTANCE ONLY; not reinterpreted |
| Locally reachable Git history | 224 commit objects inspected: zero embedded commit signatures; 16 annotated tags inspected: zero SSH/PGP signatures | No signed approval source found in this exact inventory. An annotated tag is not a cryptographic signature |
| Actual connected GitHub identity | Read-only `github.get_user_login` returned login `TDY0225`, immutable numeric user ID `223441940` | AUTHENTICATED CONNECTOR ACCOUNT OBSERVED; this alone proves no component decision or human click |
| Public signing-key registry for that account | HTTP 200 from `/users/TDY0225/ssh_signing_keys` and `/users/TDY0225/gpg_keys`, each returned `[]` | No existing published signing key found at observation time. Private keys/key agents were not searched |

One unauthenticated public account-profile lookup failed with `URLError`; the
failure is retained as UNKNOWN, not silently reported successful. The connected
identity observation above came from the separate authenticated Host connector.
The browser search tool could not retrieve the public API URLs; bounded public
HTTPS reads subsequently obtained the two actual empty key lists. Neither the
initial read failure nor absence of published keys proves that the Owner has no
private signing facility elsewhere. Owner-controlled signer readiness is UNKNOWN.

Official references: [Codex App Server](https://learn.chatgpt.com/docs/app-server)
describes account/approval interfaces; [plugin annotations](https://developers.openai.com/plugins/reference)
are hints, not server authorization. This audit does not infer a general G3 grant
from either. [GitHub signing-key APIs](https://docs.github.com/en/rest/users/ssh-signing-keys)
provide public readback and authenticated enrollment of account signing keys.

**Finding: no existing admissible approval source was demonstrated.** No adapter
is activated, no approval/registration is issued, and no G3 positive PASS or
independent final review is claimed. The retained 107/107 tests remain historical
contract regression, not new live origin qualification.

## The one proposal: account-bound Owner-held SSH signatures

Reuse the existing GitHub account as the identity/key-publication anchor and the
already installed OpenSSH verifier for signed decision bytes. Add only a thin
future verifier binding to the existing G3 codec. No identity provider, web login,
signing service, CA, background process, protected database or cloud resource.

### Exact issuer and security boundary

- Proposed issuer principal: **GitHub user ID `223441940`**, observed login
  **`TDY0225`**. The binding must be explicitly accepted in the bootstrap; current
  connection does not automatically authorize it as a G3 issuer.
- Signing authority: one **Owner-controlled SSH signing key**, registered by the
  Owner to that account. Its actual key ID and fingerprint are **NOT ENROLLED**.
  They are obtained from the verified signature and the exact matching published
  signing-key record, not filled in or chosen by the implementer. Until that
  concrete match is established, origin remains DENY/UNKNOWN.
- The Owner retains the private signing operation in an environment outside this
  assistant/Nexus execution's access. No key generation, signing-agent access,
  public-key enrollment or private-key handling is performed by this task.
- GitHub's authenticated account/key-registration boundary supplies the identity
  association. OpenSSH verifies possession of the matching key over the exact
  signed message. GitHub membership without the signature, or a signature without
  this accepted identity association, is insufficient.
- Same-user candidate/receipt/repository files are untrusted inputs. Trust must
  come from the accepted Host/operator issuer binding, fresh independent GitHub
  account/key readback and signature verification. A caller-supplied account,
  allowed-signers file, booleans or cached JSON cannot select its own trust root.
- This does not claim complete malicious-executor exclusion, GitHub-compromise
  resistance or protection if the trusted verifier/Host itself is replaced.
  D04 executor exclusion is not added as a release gate.

### Minimum proposed interface

```text
verify_g3_origin(
    exact_envelope_bytes, detached_signature,
    expected_subject, expected_scope, expected_purpose, now,
    accepted_host_issuer_binding, fresh_account_key_observation
) -> VERIFIED_ORIGIN_ONLY | DENY_OR_UNKNOWN
```

The message must bind the existing exact G3 subject/revision/configuration,
review-evidence digest, purpose (`APPROVE` or `REVOKE`), issuer, scope and finite
decision validity. Unsupported fields/schemas, wrong purpose/namespace, stale or
unavailable identity/key observations, missing signature, changed bytes, unknown
issuer, ambiguous key identity, removed key, invalid time or scope mismatch deny.
Individual-grant revocation remains a separate existing G3 requirement; account
key removal is not misreported as proof of that complete lifecycle.

Use the exact namespace `nexus-g3-approval-v1` and verifier principal
`github-user-223441940`. The [OpenSSH manual](https://man.openbsd.org/ssh-keygen)
documents `ssh-keygen -Y verify` with an allowed signer and namespace.
`check-novalidate` is expressly not accepted for issuer verification. The temporary
allowed-signers input must be constructed from the independently checked identity
association, never from the candidate's claimed key. Namespace and exact message
binding prevent a Git/code/email signature from being reused as G3 approval.

The public GitHub account/key observation must be a complete current successful
read, bound to numeric identity and exact key, with acquisition/completion times
and at most 30 seconds of age at verification. Pagination, unavailable reads,
cache-only evidence or identity mismatch cannot turn into PASS. No general signing
permission, automatic renewal or trust for every future key is implied.

The result authenticates only origin and its bound decision. It creates no task,
Host, install, network, runtime or production execution authority. Registration,
current eligibility, task authority, revision drift, revocation, isolation,
regression and independent final review remain separate G3 gates.

### The unavoidable one-time human bootstrap

The Owner must personally complete **one signing-key enrollment/acceptance
ceremony**: designate an Owner-controlled signing key, register its public part
as a Signing key on the existing `TDY0225` GitHub account, and attest acceptance
of this exact issuer/purpose/scope with that key. Only the public registration and
detached signature are delivered to Nexus. A private key or passphrase must never
be supplied to the assistant. This is one finite bootstrap ceremony, not a claim
that it takes one click or that an Owner signer is already configured.

For the first controlled-fixture qualification, the same ceremony can sign one
fully specified decision bundle after the exact existing benign component and
review evidence are displayed. Approval and any bounded revocation instruction
must both be explicit in those signed bytes. This proposal itself issues neither.
Do not generate later approval/revocation decisions from a bootstrap signature
that only enrolled an issuer. Future unrelated component decisions still require
that accepted issuer or a separately authorized reviewer; no blanket preapproval.

This ceremony cannot be delegated to the implementing assistant: choosing its
own trusted key, enrolling it through an Owner account and calling its own output
Owner approval would recreate the precise origin flaw. A text reply approving a
proposal does not replace the published identity association and signed decision.
If the Owner has no suitable independent signing environment, signer setup is
still an unresolved bootstrap prerequisite; do not pretend enrollment succeeded
or generate a replacement private key here.

### Cost, exclusions and stopping rule

No new paid infrastructure or resource is proposed. Reuse existing GitHub and
local OpenSSH; do not purchase hardware or services. No N01, PREAUTH, OTP/TOTP,
Stytch public-pin schema/window, DynamoDB, S3 custody, distributed recovery,
production IAM or admission is involved. This proposal does not amend those
historical checkpoints or ask to resume their research.

Current action: **HOLD_FOR_NONDELEGABLE_ISSUER_BOOTSTRAP**. No signing key is
installed, no trust store is activated, no new authentication attempt is started,
and no runtime verifier is implemented. After actual bootstrap evidence arrives,
first qualify this narrow origin chain; only then continue the previously
authorized original G3 work. G6 remains gated by legitimate G3 freeze.

The accompanying canonical JSON is the exact documentary proposal, with
`approval=NOT_OBTAINED`. Its SHA-256 is supplied separately; its digest is not an
approval. G2/G4 stay frozen, historical research stays HOLD, production adapter
stays DENY, and **REAL_ADMISSION=NO**.
