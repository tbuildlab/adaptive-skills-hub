# D01 fixed Owner factor metadata observation

Source checkpoint: `cb7838fb8195732f55788a2686d4858ba33b7811`.

The fresh primary ceremony returned PASS, but TOTP preparation returned DENY/UNKNOWN and retired its context. No new QR was handed to the Owner. The existing native transport destroys non-200 response bodies and classifies HTTP 400 as UNKNOWN; therefore neither the provider error type nor the failing operation is established from this observation. No successful TOTP or qualified session is inferred.

The [official Get User API](https://stytch.com/docs/api-reference/consumer/api/users/get-user) documents a fixed native user lookup and TOTP metadata consisting of identifiers and verified flags. The [official Create TOTP API](https://stytch.com/docs/api-reference/consumer/api/totp/create) documents a bounded initial authentication window; expiry makes an unverified TOTP unusable and does not establish factor deletion. These capabilities are distinct from deployed observations.

This separate five-file diagnostic package is a temporary, protected metadata reader. It has only a fixed GET to the exact reviewed Test project and native Owner user; it cannot create, authenticate, revoke or delete any factor or session. Browser-selected users, routes, origins, generations, methods and scope substitutions deny. The stable diagnostic domain is forbidden. Production-tier execution is restricted to the existing Vercel project and an unaliased deployment hostname, existing platform protection, explicit request marker, exact scope digest and a maximum 30-minute window. Disabled configuration rejects before credential custody. Existing credentials are consumed only by the protected server runtime, never downloaded or inspected by the executor.

The response projection contains only user-match, bounded TOTP counts, project/Owner-bound hashes of native factor identifiers, verified flags, call counts and fixed classification. No full provider body, arbitrary metadata, setup material, recovery codes, session material, authentication headers or credential values may reach logs, evidence or chat. The duplicate-member/depth/size parser is reused from accepted cleanup source; no deletion code or endpoint is included. Success means point-time metadata observation with authority NONE and admission DISABLED, not successful two-factor authentication.

The package has no imports from production Nexus authority or diagnostic service, and is never promoted to the stable domain. Both the accepted diagnostic service and the exact exposed-factor cleanup remain byte-preserved. No issuer/client/subject, generation, review-window or fail-closed semantics change. After one read and, if necessary, one independent confirmation read, remove the temporary deployment and verify its URL no longer serves the endpoint. A verified factor cannot be deleted merely because a local context retired; unknown lineage and results remain unqualified.

```text
FACTOR_OBSERVATION_DESIGN = READ_ONLY_FIXED_OWNER_METADATA
PROVIDER_CALLS_OFFLINE_VALIDATION = 0
FACTOR_MUTATION_CALLS = 0
RAW_CREDENTIAL_ACCESS = NONE
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
LIVE_FACTOR_STATE = ONE_VERIFIED_TOTP_ZERO_UNVERIFIED
D01 = NOT_QUALIFIED
D04 = UNQUALIFIED
```

## Deployed observation and retirement

The reviewed five-file artifact SHA256 is `fc74eb138ec9dfb0b33d1d0433acd88cd611ed7dbac9246ef1d6e71f63e8b82c`. Deployment source UIDs matched all five files; its unauthenticated URL returned HTTP 302 and protected preflight performed zero provider calls. Two separately dispatched fixed GET observations each returned PASS/NONE, exact native Owner match, one verified TOTP and zero unverified TOTPs, with identical project/Owner-bound factor hashes. Total provider calls: two reads, zero mutations. No factor identifier or private material is retained in this document.

The temporary deployment was removed and its protected endpoint independently returned HTTP 404. The stable diagnostic domain was not changed. This establishes current verified-factor presence, not the exact cause of the previous UNKNOWN or successful session qualification. It does not justify deleting a verified factor or issuing another enrollment. Existing accepted transport and offline integration tests already permit current-Owner TOTP authentication after a fresh primary ceremony without TOTP_CREATE; a separately reviewed code-only UI can reuse that operation while preserving all existing server checks.

Validation: 32 new artifact tests; 366 diagnostic Node tests, 134 G3 Python regressions, 295 artifact tests (including the 32 new tests), 30 historical deployment tests and 11 isolated package tests passed: 836 unique offline tests. Commands: `node --test diagnostics/g3-d01-rp/tests/*.test.js`; `python -B -m unittest discover -s tests -p test_g3*.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_*artifact.py`; `python -B -m unittest discover -s diagnostics/g3-d01-rp/tests -p test_deployment_prep.py`; and `python -B -m unittest tests.test_ecosystem_isolation_package` in the accepted-file snapshot. Static bounded secret/private-field/import scan, historical-byte preservation, deterministic MANIFEST (478 entries) and `git diff --check` passed. No offline test made a provider call. Ignored validation evidence is not packaged or committed.
