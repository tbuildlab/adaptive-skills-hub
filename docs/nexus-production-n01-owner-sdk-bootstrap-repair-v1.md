# N01 retained head 6 and native SDK bootstrap repair

2026-10-12. N01 remains INCOMPLETE, G3 remains INCOMPLETE and REAL_ADMISSION
remains NO. D01/D03 and G4/G6 preparation are unchanged.

## Actual continuation, without replay

[Native public observations](../research/nexus-production-n01-forward-owner-source-observed-evidence-v1.json)
retain the actual SIN1 deployment, exact R Compliance versions, and the original
FINALIZED recovery 5 and membership-retirement 6 events. Deployment
`dpl_95CToN5wALoGF64y1kh1xg9Jwf5j` was built from
`da67787b56309c4ceeffa67bc7bebb90f97491bb`.
Checkpoint 5 body SHA256 is
`138c264277fda62f78d15e308878ec566096dc36497819f5686f0706a9454ca3`.
Checkpoint 6 body SHA256 is
`0492f25ce2c1b930ed5c4f5e9b2b0956716abb09b4cd90d7f84bb606097baabd`.
Their predecessor bytes and retained objects remain unchanged.

The human reported one LOGIN and no codes entered. The earliest native LOGIN
request timestamp is 1791787745563; its response was 403. Controller and native
OIDC were present; the exact Origin and closed header guard passed. The process
then remained QUARANTINE, with 68 DynamoDB and 1615 S3 calls unchanged from
membership completion. No successful Owner-login-ready event was emitted.
Later rejected POSTs are observable; their origin is UNKNOWN. They are not
attributed to additional human clicks. No LOGIN has been submitted by Codex.

## Verified deterministic defect

The pinned maintained Stytch SDK exposes `sync_client._session` as a read-only
property. The deployed controller assigned that property after construction.
A local reproduction using the actual installed SDK and synthetic non-authority
configuration raises AttributeError. The supported `sync_session` constructor
argument gives the exact bounded transport identity. The repair uses that
argument, checks the exact public project before construction, and preserves all
transport, source, Origin, cookie, CSRF, review and time gates. The original
runtime swallowed its exception, so the exact first runtime exception was not
logged; the reproduced defect is distinguished from that unrecorded exception.

The fixed SDK-repair profile checks native SDK construction before R source
enrollment, without making an authentication request or creating a challenge.
Future bootstrap denials emit only closed stage enums and backend attempt counts,
never exceptions, credentials, bodies, private state or environment values.
Existing Production-variable presence was checked using metadata-only native
CLI output; values were not opened or pulled.

## Exact new artifact binding

The user's latest instruction authorizes repairing, redeploying and obtaining
the new artifact's exact binding. The fixed `OWNER_SDK_REPAIR_FORWARD_V1` seam
accepts only current head 6, epoch 4 and the exact old process/artifact/source.
It reads the exact independently retained RECOVER 3 and 5 custody evidence as
history only. Separate R-owned SDK-repair prefixes must bind the new deployment,
artifact, nonce, RECOVER 7 and exact predecessor 6. Explicit forward T9 advances
to epoch 5 and retires the old source; T5 membership 8 retires the generation-2
binding/registration and creates distinct generation-3 identities. All original
rows and bytes remain. No Owner context, bearer, code, cookie, challenge, decision,
grant or execution is restored. Old heads, incarnation collisions, replay,
corrupt/missing/forked evidence and wrong profiles deny.

No new resource, permission, subscription, retention period or cost cap is added.
The existing aggregate 512 DynamoDB-attempt envelope is apportioned as at most
98 earlier non-Owner attempts (86 published conservative upper bound plus
12 reserved read-only diagnostic attempts), 134 observed prior native Owner
attempts and 280 new SDK-repair attempts. This reallocates unused earlier reservation; it
does not increase the aggregate. Existing published non-Owner conservative
upper bound was 86, plus bounded read-only probes. The completed synthetic
lifecycle includes all five identity gates, fresh storage reads before challenge,
decision and revoke, PREPARED/FINALIZED for each transition, and one final
current-head verification. It requires 272 primary attempts, leaving eight
within the new reservation. The initial proposed 200 allowance was insufficient;
unused historical reservation was reapportioned from evidenced closed runs,
without changing the accepted aggregate 512 ceiling or any storage check. S3 is bounded to 10000
new native calls, 240 conditional writes and 8 MiB per backend, within the
original aggregate 50000 reads/5000 writes/64 MiB limits. Lease refresh never
resets counters. The approved review expired at 2026-10-12T07:51:51.502Z exclusive. New
live binding/authentication must wait for a separate exact Owner-reviewed
public-pin package; the old review cannot be renewed by the implementer. Cleanup
and the original resource operation window remain unchanged. Invoice is UNKNOWN.

The longer retained history requires independently rereading RECOVER 3/5/7;
the modeled head-8 read costs 185 calls before source-reader accounting. One
private ingress fence must cover email, OTP, TOTP and current display/decision
gates. The repair profile constructs a fresh observation reader for each identity
gate, each still bounded to 1000 attempts. It does not reuse a cached current-head
verdict or reset the shared native client's process-wide counters. A retired reader
or pending unknown append cannot create a successor; an identity-gate failure
retires the private ingress and quarantines the controller. The original profile retains its
existing reader behavior. Both adjustments apportion the existing aggregate, not a new spending envelope;
the original profiles and their bounds/tests remain unchanged.

The new seam does not guarantee platform process affinity. Cold or quarantined
processes still deny; there is no automatic recovery, LOGIN retry or redispatch.
Actual human email OTP, Authenticator, exact decision, persistence and revoke
remain live gates. Offline SDK and retirement tests cannot qualify them.

## Regression environment

The first complete run recorded 1447 tests, 1433 passes, four historical
environment skips, three failures and seven errors. Nine failures/errors
originated from a stale MANIFEST before the intended newly staged SDK-repair
files were inventoried. The remaining failure was the existing governance CLI
byte comparison against CRLF checkout bytes; LF normalization was verified
against the unchanged Git blob. No historical test assertions were edited.

After the real public review expired, legacy N01 tests still froze time.time
to their historical fixture interval but used current datetime.now in custody.
A local external offline runner aligns datetime with that existing fixture clock
for those cases and restores symbols after each case. The reviewed package,
source expiry and production clocks are untouched; this runner is excluded from
source artifacts and provides no live evidence. A clean LF source snapshot with
its exact MANIFEST is used for distribution/reproducibility checks.

The local runner initially bypassed unittest's class lifecycle and produced ten
fixture initialization errors. The corrected runner uses standard TestSuite.run;
it attaches historical_clock only at each legacy N01 case's _callSetUp and lets
standard setUpClass/tearDownClass and doCleanups run unchanged. A second isolated
setup exposed .git/objects to the strict package boundary. Git metadata is now
outside the source snapshot via git init --separate-git-dir; the boundary remains
unchanged. Both failed diagnostic runs remain failed evidence, not passing counts.

The clock alignment can be reproduced on a clean LF source snapshot with its
verified MANIFEST and external Git metadata using this test-only wrapper:

```python
import unittest
from tests.test_g3_n01_owner_sdk_bootstrap import historical_clock
suite = unittest.defaultTestLoader.discover("tests")
def align(node):
    for case in node:
        if isinstance(case, unittest.TestSuite):
            align(case)
        elif "n01" in case.__class__.__module__ and "owner_sdk_bootstrap" not in case.__class__.__module__:
            original = case._callSetUp
            def setup(case=case, original=original):
                historical_clock(case)
                original()
            case._callSetUp = setup
align(suite)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
```

No fixtures, assertions or skip conditions are rewritten. Synthetic snapshot Git
metadata is only a build-test dependency, never a production checkpoint. The
actual development checkpoint will be committed/pushed separately after checks.
A separate [pending review-2 package](nexus-production-n01-sdk-repair-bounded-public-pin-owner-review-v2.md)
records the newly fetched identical public keyset and one fixed four-hour window.
Its approval remains NOT_OBTAINED; it cannot create current source authority.

## Final offline verification and held deployment

The corrected standard lifecycle runner completed 191 affected tests: 191 PASS,
zero skips and failures. Complete regression completed 1450 tests: 1446 PASS,
four unchanged environment skips and zero failures/errors. Three skips lack the
existing real embedded-runtime inputs; one lacks Windows symlink privilege.
They are not PASS. [The bounded verification record](../research/nexus-production-n01-sdk-repair-offline-verification-v1.json)
retains the initial failed-run digest, final counts, environment classifications
and the final full-log digest. Package bytes reproduce exactly with SHA256
`e9ce7100c82aad06076f81e500dd7c0d406393828b279f835c4c49a5e7a4590f`.
The manifest, secret/import isolation and diff checks pass. All executable source
bytes match the complete tested LF snapshot; subsequent changes are documentary
verification and the exact pending review input only.

No new AWS call, Owner LOGIN, OTP/TOTP operation, source enrollment, RECOVER or
deployment occurred during this repair. One unauthenticated current public JWKS
read confirmed unchanged project/issuer/keyset. The old approved review is expired;
the new exact review is NOT_OBTAINED. No new process can use expired review 1 to
establish a current R binding or Owner authentication. Deployment/live binding
remain held at that genuine explicit Owner-keyset gate. N01 and G3 remain
INCOMPLETE; D01/D03 CLOSED, G4/G6 preparation and REAL_ADMISSION=NO remain
unchanged. No release tag or independent-review PASS is claimed.
