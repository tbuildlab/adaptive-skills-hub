# D01 fixed identity-denial classification review

Source checkpoint: `a84729ab995bcba871763ed68002c8944a663163`.

After the Owner reported both authentication actions completed, the public diagnostic evidence showed DENY/IDENTITY with a null context expiry, authority NONE, admission DISABLED and qualified_live=false. The context is retired. The page did not retain action-specific evidence, so neither the exact failing operation nor successful TOTP session qualification is established. No OTP, TOTP, cookie, bearer, signed token or provider response is inspected or retained.

This additive diagnostic revision splits existing IDENTITY refusal predicates into nine closed labels: IDENTITY_JWT_SHAPE, IDENTITY_JWT_JSON, IDENTITY_SIGNED_PROOF, IDENTITY_TOKEN_SHAPE, IDENTITY_SESSION_CONTINUITY, IDENTITY_TOKEN_CONTINUITY, IDENTITY_PRIMARY_TIME, IDENTITY_OTP_RESPONSE and IDENTITY_TOTP_RESPONSE. Signature failure remains a compound fixed classification; no claims, values, lengths, token hashes, free text or credentials are projected. This narrows fault localization without treating metadata as authority.

The original boolean predicates and evaluation order are retained. In particular, a provider token differing from retained custody still denies; it is not adopted after MFA, and neither another session nor another primary authentication time can be substituted. Native User/method/factor response checks remain exact. Session/factor projection, signed JWT verifier, HTTP/CSRF/cookie/origin controls and credential custody are byte-preserved. No accepted contract body changes. The [official Authenticate TOTP reference](https://stytch.com/docs/api-reference/consumer/api/totp/authenticate) documents adding authentication to an existing session and the returned opaque token; it does not establish static-token continuity for this observed ceremony. If actual evidence proves the existing token-continuity condition fails, that condition remains BLOCKED until a separately accepted compatibility amendment is justified; no relaxation is made in this slice.

Four runtime files differ from the preceding code-only UI artifact: deployment revision, error-class allowlist, exact transport refusal labels and public fixed-label allowlist. The default artifact remains disabled and server credentials cannot be read while either build gate is off. The live artifact is diagnostic-only; browser input cannot choose an issuer, project, native Owner, session, keyset, generation, transport or authority mode. Application generation 3 and the original public review window are unchanged.

The new tests use generated synthetic RSA keys and fixture transport only. They exercise normal same-lineage success, absent/oversize/malformed JWT, wrong issuer/audience/subject/expiry, absent/malformed/changed token, changed session, changed primary time, wrong native response User/factor, disabled-before-custody behavior, error-label client projection and deterministic source mutation rejection. A fixture cannot become production authority. An initial fixture import referenced an absent non-runtime dry-run module; the unused import was removed from the new test fixture only, and all new classification tests then passed.

Live candidate artifact: 20 files; SHA256 `2b48a9014f724b987eb27fc59afe557e3b1b48b85da3a310fb32a503e4c71114`. Offline validation passed: 366 Node diagnostic tests, 134 G3 Python regressions, 348 artifact tests (including 23 new classification tests), 30 historical deployment tests and 11 isolated package tests: 889 unique tests. After naming the malformed-token fixture with the existing OFFLINE_ convention, the secret scan and the 23 tests were rerun without weakening scanning or token validation. Static bounded secret/private-field checks, client/server boundary, byte preservation of all historical tracked files, deterministic MANIFEST (485 entries) and `git diff --check` passed. Commands: `node --test diagnostics/g3-d01-rp/tests/*.test.js`, `python -B -m unittest discover -s tests -p test_g3*.py`, `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py`, `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py`, and `python -B -m unittest tests.test_ecosystem_isolation_package` in a fresh accepted-file snapshot. Deployed source UIDs matched all 20 files; all four public assets matched byte-for-byte. The unaliased hostname denied REQUEST_ORIGIN. The exact staged deployment `dpl_2VXBn3TaYwn9fKs8oFFB5n9at8WV` was promoted to the stable diagnostic domain; independent stable verification is retained in ignored evidence. No provider calls occur during source/asset/preflight verification, and no credentials, cookies or CSRF values are retained by the executor. The source/artifact hashes identify reviewed bytes, not runtime authority. Actual failing classification remains UNKNOWN pending a fresh human-entered ceremony. A point-time factor metadata read alone proves neither authentication nor D01 closure.

```text
OBSERVED_DIAGNOSTIC_RESULT = DENY_IDENTITY
FAILED_IDENTITY_PREDICATE = NOT_YET_LOCALIZED
IDENTITY_ACCEPTANCE_PREDICATES = UNCHANGED
TOKEN_CONTINUITY_RELAXED = NO
RAW_CREDENTIAL_ACCESS = NONE
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
D01 = NOT_QUALIFIED
D04 = UNQUALIFIED
```
