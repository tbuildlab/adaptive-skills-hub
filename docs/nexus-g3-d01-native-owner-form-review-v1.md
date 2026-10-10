# Nexus G3 D01 native Owner form review v1

Date: 2026-10-10. Source checkpoint: `d4a1d05538761e03ed5426a87ddb766a3d42f7c2`. Branch: `nexus-v2-g3-live-qualification`. Additive diagnostic-only transport correction under standing delegated authorization. No canonical authority contract or historical source is modified.

## Observed primary factor and failed view

After the Owner reported clicking Authenticate OTP, the retained request-stage page showed PASS / NONE. Because that generic projection does not name an operation, the executor did not infer authentication from it alone. The next protected TOTP_CREATE action was performed once and its completed request returned PASS / NONE. The reviewed server requires an authenticated primary session, checks the fixed native user/project, verifies signed issuer/audience/subject against the pinned public keyset, performs a direct remote session recheck, creates one disposable pending TOTP enrollment, and performs another direct remote recheck. Those guards accepted. The successful step comprises three provider exchanges. Raw JWT/token, OTP, seed, recovery codes, private fields and provider body were not read or retained by the executor.

This is a positive primary-identity/runtime-mapping observation. It is not full D01 qualification: TOTP authentication, the five later observation points, revocation and required live negatives remain incomplete. No two-factor session, OwnerDecision, receipt, grant, AdmissionIntent or dispatch claim is certified. Principal body and identity expectations remain unchanged; runtime mapping stays CONDITIONAL pending the remaining matrix.

The one requested Display transient Owner channel interaction did not produce a private page. The retained URL and visible structure stayed on the original diagnostic page, with a generated hidden form and no owner-transient element. No seed or recovery material was observed. The specific protected display request outcome is UNKNOWN, so it was not retried or treated as displayed. The absolute context expired at 2026-10-10 03:24:32.179 UTC / 11:24:32.179 Asia/Kuala_Lumpur. It is never extended or revived. The existing provider session's independent lifetime is not treated as local OwnerContext validity; local expiry is not proof of external session revocation.

## Zero-provider reproduction

A separate fresh unauthenticated context exercised the same scripted Display control once. It remained on the original page with a generated form. A subsequent fresh read retained the same absolute deadline and DENY / NONE state. The reviewed server would retire a page if it handled an unauthenticated OWNER_TOTP_DISPLAY form request. This bounds the failure to the form/navigation path before that page's successful diagnostic handling; it does not uniquely identify a browser mechanism, intermediary or platform defect. No matching form-action CSP violation was observed in the bounded browser error classification check. No raw console message was retained. This reproduction has no authenticated backend, and therefore cannot call Stytch or expose TOTP material.

## Exact versioned correction

`verify_owner_form.py` preserves the reviewed request-stage server bytes and changes exactly three files relative to that artifact: the fixed deployment revision and public index/app. The profile is LIVE_DIAGNOSTIC_NATIVE_OWNER_FORM; revision g3-d01-owner-live-native-form-v3. The deterministic source/package SHA256 is `c8cc3405fade529dd0b11a378872c17bb4155bb5ffe9d29c7e62a10f48b4e31f`. Inventory stays exactly 19 files, with no dependency or endpoint added.

The existing Display button becomes the submitter of one fixed native same-origin POST form. Its only named fields are the constant OWNER_TOTP_DISPLAY action and the current server-issued CSRF marker. CSRF is never placed in a URL. The client denies submission when disabled, busy, cross-origin or without a valid current marker; a submission locks controls against duplicates. Credential/identity selection, arbitrary HTML parsing, document.write, innerHTML, scripted form.submit, discovery and remote form destinations are forbidden. Owner-private HTML continues to be rendered by the unchanged protected server and cleared by the unchanged one-use channel. Existing origin, exact route, current page, CSRF, primary session, expiry, remote recheck and envelope-consumption gates stay mandatory.

The native form is a qualification candidate until actual hosted navigation is observed. First stage it, verify all 19 source UIDs and three public asset bytes, promote only the verified diagnostic version, then run an independent unauthenticated Display negative. It must produce an actual server DENY / RETIRED before any new OTP send. This negative performs zero provider calls. If the navigation still fails, stop sends and record the unresolved browser transport blocker; do not weaken CSRF/origin, put tokens in URLs or add client bearer storage. Only after this check passes may a fresh bounded OTP ceremony proceed.

Application/registration/keyset generation remain 3 because exact registered identity/application inputs are unchanged; the code revision is distinct. Owner/project/binding generation remain unchanged. Public key fields and original review interval are unchanged, expiring at 2026-10-10 15:35:37 UTC. No review window renewal, unreviewed key source, provider account change, secret change or new authority is introduced. The repository's public real-admission entrypoint remains fail closed and historical compile gates remain disabled.

## Offline checks

The 29 new tests cover fixed native submission, disabled/busy/origin/CSRF failure, duplicate submission prevention, marker clearing after logout/error, unauthenticated form denial with zero provider IO, malformed/duplicate/foreign form input, no cross-profile or input substitution, unchanged one-use server, no unsafe HTML/GET/token routing, exact inventory, deterministic packaging and historical source hashes. All fake transports remain offline only. Existing tests are preserved.

Relevant full validation commands:

```text
node --test tests/*.test.js
python -B -m unittest tests.test_g3_offline_control tests.test_g3_production_metadata tests.test_g3_authorization tests.test_g3_host_approval_bridge
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py
python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py
python -B -m unittest tests.test_ecosystem_isolation_package
python -B diagnostics/g3-d01-rp/scripts/verify_owner_form.py --output state/g3-d01-autonomous-20261010/native-owner-form-artifact
git diff --check
```

Expected unique passing count: 639 = 323 diagnostic + 134 G3 + 141 artifact + 30 historical deployment + 11 isolated package. Secret/private-key scan, exact baseline preservation, closed import/client boundary, fresh deterministic MANIFEST and diff checks must pass before checkpoint or deployment. Only this document, the new builder/test and MANIFEST are eligible for the source commit. Ignored evidence and the three unrelated Route D files are excluded. Hosted qualification evidence is additive after actual verification.

```text
D01_PRIMARY_OWNER_IDENTITY = OBSERVED_ACCEPTED_PROTECTED_GUARDS
D01_TOTP_PREPARATION = OBSERVED_PASS
D01_PRIVATE_OWNER_CHANNEL = NOT_OBSERVED_SCRIPTED_FORM_NAVIGATION_BLOCKED
D01_NATIVE_OWNER_FORM_DESIGN = DEFINED_DIAGNOSTIC_CANDIDATE
D01_NATIVE_OWNER_FORM_HOSTED_QUALIFICATION = PENDING
D01_STATUS = INCOMPLETE_TWO_FACTOR_AND_LIFECYCLE_PENDING
STYTCH_PRINCIPAL_RUNTIME_MAPPING = CONDITIONAL_PRIMARY_POSITIVE_OBSERVED
D03_STATUS = CONDITIONAL_D01_ENTRANCE_NOT_SATISFIED
N01_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
N02_STATUS = NOT_IMPLEMENTED_ENTRANCE_BLOCKED
REAL_AUTHORITY_PATH_PRESENT = NO
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
CUMULATIVE_PROVIDER_EXCHANGES = UNKNOWN
SECRET_VALUE_ACCESS_BY_EXECUTOR = NONE
```
