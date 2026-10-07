# Route D cryptographic attendance prototype v1

Status: IMPLEMENTED FOR VM-FREE UNIT TESTING ONLY; UNACCEPTED.
Lineage: LAB_ONLY / ENGINEERING_ONLY_NON_QUALIFYING.

## 1. Scope and authority

The current Owner attachment authorizes this isolated prototype and synthetic
tests. It does not authorize enrollment, actual authentication, credential access,
VM queries, input injection, recovery admission or task/budget authority.
No production module imports this prototype. No native authentication API,
network client, shell, dispatch callback or lifecycle controller is provided.

Implementation: `prototypes/cryptographic_attendance_v1.py`.
Qualification harness and known non-secret fixtures:
`tests/test_cryptographic_attendance_v1.py`.

## 2. Fixed model

A challenge binds exact incident/operation, a 32-byte unpredictable nonce,
sequence, previous status, policy/version, RP/origin/public binding, UTC and
monotonic issuance/expiry, clock epoch, purpose, lineage and one-use state.
The 5,000 ms default is a synthetic test profile, not recovery budget authority.
Clock samples are trusted inputs in this model; their live independent source
and rollback-resistant custody are UNKNOWN.

The narrow assertion profile is ES256 / P-256, exact RP hash and origin, signed
client challenge, UP and policy-required UV, no backup/extension flags, and
counter consistency. Zero counters do not establish replay protection. The
profile deliberately rejects unsupported fields/configurations. It is not a
complete WebAuthn implementation, credential enrollment or attestation verifier.

The existing bundled Python cryptography backend performs ECDSA verification;
absence of that backend refuses verification and does not trigger installation.
The Owner's normal Python lacks this backend. No repository production
dependency or installation requirement is changed.

## 3. Journal, result and failure semantics

The bounded journal has at most 128 events and 65,536 serialized bytes. A
retained checkpoint detects changes/rollback within its trust assumption.
Delivery reserves VERIFYING before verification; success closes CONSUMED;
verification failure closes REFUSED. Restart closes unfinished records
AMBIGUOUS. Completed, refused and ambiguous records cannot be reused.
Any storage failure refuses output. Exclusive pending files, flush/fsync and
replacement reduce partial-write ambiguity; crash-complete Windows durability
is not established. Pending residue is not silently removed or retried.
Concurrent verification is serialized only within the same ledger instance;
there is no qualified multi-process custody or lock service.

Results bind the challenge/result sequence, purpose, lineage and journal head.
They always say ASSERTION_VALIDATED_IN_LAB_MODEL, owner_presence=UNKNOWN,
source_custody=UNQUALIFIED, authority=NONE, dispatch_requested=false. Their
unkeyed hash and equality to a retained result detect modeled mutation; they do
not authenticate a record read from attacker-writable storage. Constructing a
Python result object never establishes actual Owner presence.

## 4. Decisive protection gap

ProtectedChallengeLedger is a logical role name, not an OS protection claim.
An actual same-user fixture test replaces the journal and supplied checkpoint;
the old consumed history disappears without a trusted independent reference.
The unfinished replacement challenge still closes AMBIGUOUS, so this test does
not claim a forged real signature or a successfully replayed old assertion.
It demonstrates that history/reference custody is insufficient. A same-SID
attacker can also replace unprotected code, policy, binding or output before a
consumer reads it. The prototype cannot close that architectural boundary.

No ACL, identity, service or privilege change is made. A protected verifier,
accepted binding, challenge/checkpoint state, trusted clock and consumer must
be independently established before source qualification. A physical key touch
alone would not close these gaps.

## 5. UP, UV and real ceremony

UP describes presence interaction, not proof of the intended human identity.
This synthetic policy requires UP + UV + an exact credential/public-key binding.
Real UV semantics, freshness, caching, enrollment provenance and private-key
custody remain UNKNOWN until an exact authenticator/client path is accepted and
tested. No positive mechanism result is issued.

External FIDO2, platform WebAuthn, Windows Hello and TPM-backed mechanisms are
conditional candidates only. No real path is integrated or qualified. Assertions
alone do not establish hardware identity or non-exportability. The FakeAuthenticator
uses openly known test scalars solely for synthetic signing, stores no private
material in the evidence packet, and cannot represent an Owner credential.

Real ceremony readiness is OWNER_PHYSICAL_PRESENCE_REQUIRED with additional
protected-consumer prerequisites. No API prompt, enrollment, PIN/password,
biometric, TPM/CredMan read or private-key extraction is performed.

## 6. Verification and disposition

CRYPTO-01 through CRYPTO-25 and additional malformed, timing, mutation,
concurrency, storage, binding and software-acknowledgement tests exercise the
model. SendInput/PowerShell/C#/Work/Codex cases are parser/attack-model fixtures,
not actual UI injection. Exact results, hashes and the adversarial assessment
are in the additive external evidence packet. Unit PASS cannot establish
acceptance-standard properties 3, 5, 6, 7 or 8 for a real source.

Disposition: CRYPTOGRAPHIC_ATTENDANCE_REQUIRES_ADDITIONAL_PROTECTION.
Next: separately bounded protected verifier/state/consumer feasibility review;
do not authorize a physical ceremony as a substitute for custody evidence.

P1 Section 3 remains PARTIAL; boot/session UNKNOWN; input UNVERIFIED;
Section 4 NOT STARTED; P2 NOT READY; U02-C / D2-C retained;
Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED;
Positive Host Binding ABSENT; G2 HOLD; D3 / D3-lab NOT AUTHORIZED.
VM poweroff is preserved from prior Owner evidence, not a new live query.
Historical accounting and violations are unchanged. No commit or acceptance.

## 7. Source basis

- [WebAuthn assertion verification](https://www.w3.org/TR/webauthn-3/#sctn-verifying-assertion): algorithm basis, not experimental proof.
- [cryptography ECDSA documentation](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/): backend interface, not Owner source qualification.
- Existing accepted Route D engineering-only and autonomous-lab governance:
  `nexus-route-d-engineering-only-governance-acceptance-v1.md` and
  `nexus-route-d-autonomous-lab-governance-acceptance-v1.md`.
- Prior additive attendance closure/design packets remain historical evidence;
  the current explicit Owner grant authorizes only this prototype/test scope.
