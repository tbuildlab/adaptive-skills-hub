# G3 U1 manifest path-rule review v1

Date: 2026-10-08. Static finding; packaging policy unchanged.

Both [manifest builder](../scripts/build_manifest.py) and
[package validator](../scripts/package_nexus.py) use a case-insensitive substring
path exclusion containing `credential, token, oauth, session, cookie, private_key`.
It operates on paths, without distinguishing documentation from runtime material.
The ordinary accepted document
`docs/nexus-g3-u1-d01-managed-identity-session-reuse-survey-v1.md` therefore remains
outside MANIFEST. The exclusion is reproducible from the unchanged functions.

The rule is intentional conservative security packaging behavior, and it has an
overbroad filename consequence for this legitimate document. These are compatible
findings. It is not a content scanner: an innocently named file containing a secret
would not be excluded by this heuristic alone. An ordinary-document exception would
weaken the current path boundary unless a separately qualified content/control
replacement preserved sensitive exclusion. No such replacement is established in
this run. Changing only the builder would also disagree with the packager's rejection.

Decision: leave both rules unchanged. Do not rename the survey or add an allowlist
to force inclusion. Preserve its raw hash in the run's baseline and final excluded-
file evidence; MANIFEST PASS applies only to its eligible static-source subset,
not to every document or credential absence. State evidence remains ignored.

The packager also has a separate fixed `ALLOWED_DOCS` list. Presence in MANIFEST
does not guarantee a document is included in a distributable ZIP. No list or
release/package policy is changed. Three pre-existing unmanifested Route D documents
remain outside the G3 regeneration scope; their raw bytes/hashes are preserved.

The existing ecosystem/package regression suite is run along with new offline
preparation tests. It exercises boundary rejection, traversal/reparse and mutable
ecosystem exclusion. The new manifest-boundary regression also checks session,
OAuth, token, cookie, credentials and private-key paths remain excluded by both
builder and packager. These tests support unchanged packaging behavior, not a
claim of comprehensive secret scanning.

```text
MANIFEST_PATH_RULE = INTENTIONAL_CONSERVATIVE_HEURISTIC_WITH_DOCUMENT_FALSE_POSITIVE
MANAGED_SURVEY_MANIFEST_COVERAGE = EXCLUDED_BY_EXISTING_SESSION_SUBSTRING
MANIFEST_RULE_MODIFIED = NO
SECRET_PATH_EXCLUSION = PRESERVED
DOCUMENT_RENAMED_TO_BYPASS_RULE = NO
CONTENT_SECRET_SCANNER_QUALIFIED = NO
```
