# N01 source enrollment continuation v1

2026-10-12 Asia/Kuala_Lumpur. Parent checkpoint:
`a2ac2c540d4a5c3ecea3300cd5c4a7bb60230fdc`.

## Exact Owner approval and independent custody seam

The [new exact public-pin acceptance](nexus-production-n01-public-pin-owner-acceptance-v1.md)
has been received. The pending input and its canonical SHA256 are unchanged.
The additive acceptance's canonical SHA256 is
`67f612bfb60977534e3fab0efbf9ca75fe5765a2e632b4be0f63844d6f5588ae`.
It records direct Owner provenance for this public-key review only; it cannot
replace current Owner authentication, N02 consent, source qualification or release.

[Public review custody](../ash/g3_n01_public_review.py) reuses the qualified S3
version/retention reader. It admits precisely two canonical public documents under
`qualification/n01/v1/approvals/public-pin-owner-review-20261011-v1/`, requires
their exact hashes, generation-2 storage configuration, unique complete versions,
Compliance retention and unchanged before/after inventory. The fixed review
window is checked against current runtime time before and after I/O; expiry or
clock regression denies. A forged public dataclass cannot substitute another key.
This is a key-review constraint, not an authenticated session or source writer.

The [R operation builder](../scripts/build_g3_n01_public_review_custody.py) generates
one public-only CloudShell script. The native SDK verifies R account root identity,
then conditionally retains only `proposal.json` and `acceptance.json` under that
exact prefix with explicit seven-day Compliance retention, reads their exact
version bodies and retention, and
rechecks the complete inventory. It never changes policies, resource configuration
or retention settings. There are at most 16 S3 attempts and 2,421 public payload
bytes. An existing attempt receipt prevents redispatch; exceptions produce a
sanitized QUARANTINE record without SDK error text. No credentials are copied
into the script, source or evidence. These operations fit the existing N01 request,
storage and USD 1.00 envelope, subject to its cumulative bounds and deadline.

## Closed runtime/source binding

[Source enrollment binding](../ash/g3_n01_source_enrollment.py) is a narrow
deterministic equality seam for a future independently registered, bounded current
Owner source. It compares the exact existing Host project, generated deployment
host, native deployment ID, measured artifact inventory, original ephemeral process
nonce, provider Principal, service revision, application/review generations and
review hashes. It admits only D01, D03 and Owner-enrollment source kinds, with
REAL_ADMISSION=NO and NO_AUTOMATIC_REDISPATCH. It cannot register technical,
task, G1/G2 or effect sources, or create a PRODUCTION grant registration.

The native runtime fields are available at build/runtime according to
[Vercel's system environment documentation](https://vercel.com/docs/environment-variables/system-environment-variables).
The reader accesses only VERCEL_ENV, VERCEL_PROJECT_ID, VERCEL_DEPLOYMENT_ID
and VERCEL_URL; it never enumerates environment or reads credential caches.
The existing native OIDC/SDK chain remains the authenticated transport prerequisite,
not an invented token decoder or new credential interface.

The source reader accepts one exact R-only
`qualification/n01/v1/approvals/current-source-controller-v1/registration.json`.
Missing, duplicate, corrupt, expired, unretained or unavailable custody denies.
No local-file or self-declared PASS fallback exists. Current and post-I/O runtime
time bounds remain mandatory. All returned metadata is NONE; the independently
retained source record still needs actual artifact/runtime qualification before
it is written. No such source registration has been fabricated by this phase.

## Validation and continuation boundary

Twenty-one distinct new tests pass: eight exact public-review/custody cases, eight
runtime/source binding cases and five generated native-operation contract cases.
They cover immutable approval scope, malformed bytes,
expiry before/during I/O, time regression, key substitution, generation/Principal/
artifact/deployment/process mismatches, missing/duplicate/expired/unavailable
custody and no write/authority behavior. The generated-operation simulations
verify exact account/root rejection before custody access, exact conditional
public writes and seven-day parameters, existing versions read without rewriting,
unexpected inventory rejection and unknown-ack retirement without redispatch.
They are not live AWS observations. Synthetic clients remain under tests;
production imports none of them. Existing passed D01/D03/storage/recovery/runtime
qualifications and prior regression snapshots were not repeated or promoted.

No AWS service operation, Stytch operation, new deployment, billable resource or
retention write has occurred in this continuation checkpoint. The first R login
handoff did not produce a usable fresh session: current browser state returned to
AWS sign-in. The correct Root user entry is now open, and a concrete protected
login handoff is pending. Credential values are neither requested nor inspected.
The generated exact R operation has not been executed. The approved review expires
at 2026-10-12 15:51:51.502 Asia/Kuala_Lumpur, exclusive; a delayed login cannot
extend that review. The independent-custody operation must remain within it.

After usable R authentication, retain and verify the exact review first. Then
continue actual controller deployment/source enrollment, authorized recovery into
a fresh process incarnation, current Owner/context durable linkage and N01 closure.
Current-scope human authentication/decision ingress is a remaining live integration
dependency, not permission to redo the closed D01 diagnostic. Do not use a stale
storage incarnation, simulate an Owner decision, promote a structural fixture or
restore a bearer. N02 and the subsequent live/release gates remain separate.

```text
PUBLIC_PIN_REVIEW_APPROVAL = OWNER_EXPLICITLY_APPROVED_EXACT_FIXED_WINDOW
PUBLIC_PIN_REVIEW_R_CUSTODY = NOT_PERFORMED_PENDING_PROTECTED_LOGIN
CURRENT_SOURCE_ENROLLMENT_BINDING = COMPLETE_OFFLINE_PREPARATION
ACTUAL_CURRENT_SOURCE_ENROLLMENT = NOT_PERFORMED
N01_FULL_LIVE_STATUS = INCOMPLETE
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
D03_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
G3_STATUS = INCOMPLETE
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
