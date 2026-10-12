# N01 closed authentication stages and inactive HTTP evidence

## Accepted boundary and retained checkpoint

This amendment adds closed, non-secret diagnostics to the existing deterministic
Owner controller and relying party. It does not change authentication authority,
current source enrollment, custody, review windows, Origin/OIDC requirements,
Cookie/CSRF equality, timeout, retirement, or automatic redispatch rules.
Checkpoints 7/8 and all earlier retained bytes remain unchanged. The deployed
Owner artifact remains dpl_EufrmzcN5baE2c8k2APkXyfbjiVD at source 79e3992;
the working-tree diagnostic amendment is not registered as that deployed source.

D01 and D03 remain CLOSED. N01 and G3 remain INCOMPLETE. G4 and G6 retain
COMPLETE_PREPARATION_FAIL_CLOSED. REAL_ADMISSION remains NO.

## Closed diagnostic contract

`n01_owner_closed_stage` accepts only fixed stage/result/method/route identifiers.
Results are ENTER, PASS or DENY. Method classes are GET, POST or OTHER. Route
classes are START, LOGIN, CONFIRM, STATUS, RECOVER, ENROLL, DECISION, REVOKE,
PROBE or OTHER. The records always carry authority=NONE and real_admission=NO.
No arbitrary diagnostic fields, exception messages, request body, email, Cookie,
CSRF, OTP/TOTP, token, secret, or private key value is accepted by this lens.
The protected handler continues to process necessary private inputs internally;
the operator and audit records do not acquire those inputs.

The instrumented boundaries are:

| Stage | Meaning |
| --- | --- |
| REQUEST / REQUEST_GUARD | Closed method/route class and unchanged native header gate |
| MAINTENANCE_FORM_SHAPE / MAINTENANCE_LOGIN | Initial maintenance input and native PREAUTH construction |
| AUTH_PHASE / AUTH_FORM_SHAPE | Authentication lifecycle and exact phase-specific form shape |
| AUTH_FORM_AUTHENTICATION | Parent operation for private browser form authentication |
| CSRF_PRESENT / CSRF_MATCH / COOKIE_MATCH | Private shape/equality results, without values |
| CURRENT_STATE_GATE | Exact current custody/source/primary/runtime checks |
| PROVIDER_SEND_PREPARATION / PROVIDER_SEND_RESULT | Local guarded preparation and remote outcome boundary |
| AUTH_DISPATCH | Parent authentication operation, not a provider success assertion |
| REDIRECT_TARGET / REDIRECT_303 | Fixed local target selection and 303 header generation |
| GET_FORM_RENDER | Buffered form rendering before any form response |
| PREAUTH_COOKIE_ISSUANCE / CURRENT_COOKIE_ISSUANCE | Private cookie header generation in the correct phase |
| GET_FORM_DELIVERY | Completed server-side form write; browser display needs separate evidence |

Nested failures remain distinguishable from parent failures. A parent DENY must
not be interpreted as a previously passed child equality changing to DENY.
Unknown outcomes still retire/quarantine, and no new retry path is introduced.
Redirect destinations are checked against the four existing fixed local targets;
no request can supply a redirect destination.

## Original request findings: provenance limits remain explicit

The original LOGIN request `nbvws-1791804516122-3c81572183d5` returned 303 and
recorded NATIVE_CURRENT_OWNER_LOGIN_READY_NONE. The exact artifact, process nonce
and checkpoint 8 matched the previously finalized lineage. Stytch's supported
sync_session constructor, current custody read and private PREAUTH construction
succeeded in that runtime, while the approved review v2 was valid.

The bounded original native logs contain 15 later distinct-ID POST 403 records
and no GET /api/n01/login. The earliest failing request's start timestamp is
250 ms before the original success event. Therefore the logs do not establish
that a completed 303 alone caused a method-preserving redirect. The initiator of
those POSTs is UNKNOWN; no record attributes them to repeated human clicks.

The old artifact collapsed authentication failures into generic quarantine.
Its missing stage record cannot be retroactively recovered by adding new code.
The precise original failing internal check and why no GET was issued remain
INSUFFICIENT_EVIDENCE. A synthetic resubmission of operation=login after PREAUTH
now demonstrably fails first at AUTH_FORM_SHAPE, before any provider call; this
is a tested hypothesis, not a statement about the unseen historical request body.

## Inactive verification

1. A loopback HTTP test used the actual revised handler, production request
   grammar, local synthetic identity headers and an inactive controller. POST
   produced 303 with the exact local Location; the subsequent GET produced 200,
   rendered the email form and generated the unchanged Secure/HttpOnly/Strict
   PREAUTH cookie. No native identity or storage client was invoked.
2. The same in-app browser performed one local TEST_ONLY click with 6.7 seconds
   of artificial processing latency. Recorded requests were exactly GET start
   200, POST login 303, GET login 200. The email form was visibly present.
3. A separate protected preview in the existing Vercel project tested the same
   BaseHTTPRequestHandler/rewrite/relative-303 wire pattern with that browser and
   latency. It contains no AWS/Stytch implementation, no authority, no active
   source registration and no production target or alias promotion. Native
   records show exactly one POST 303 followed by GET 200 and GET_FORM_DELIVERY=PASS;
   the disabled TEST_ONLY email field was visibly present. This is HTTP transport
   evidence only, never N01 authentication or production authority.

The first isolated preview harness had an HTTPMessage method-name collision and
returned GET 500 before any form submission. It was retained as failed harness
evidence, corrected in a separate preview, and never counted as a passing Owner
qualification. The successful preview is dpl_3nJyNXwAQLCehGhJrqF7ydSvim2N.

These checks contradict a deterministic claim that this browser or Vercel
always preserves POST on a 303. They do not identify the original POST initiator
or prove the new diagnostic artifact has a production lifecycle binding.

## Regression and deployment disposition

Seven new tests cover the closed lens, value suppression, distinct equality
failures, stale maintenance form rejection, actual HTTP handoff, current-gate
failure before provider send, render failure before cookie delivery, and closed
redirect targets. Historical tests are retained unchanged. The current affected
and complete regression receipts are recorded in the companion evidence JSON.
The affected regression passed 205/205 tests. The full repository regression ran
1464 tests: 1460 passed, zero failed/errored, and four existing environment checks
were explicitly skipped (three unavailable embedded-runtime inputs and one
Windows symlink privilege). The isolated LF-normalized executable snapshot
matches both changed production modules and the new test file. Historical-clock
fixture alignment applies only to offline tests; no live review was renewed.

No real LOGIN, OTP/TOTP, RECOVER, ENROLL, R binding or primary/custody mutation
was dispatched. No new paid resource, permission or plan was introduced. The
preview-only checks reused the existing protected Hobby project. The USD 1.00
AWS envelope, cleanup schedule, review window and retention policy are unchanged.

No new Owner production deployment or lifecycle binding is started here. An
inactive transport fixture requires no Owner source binding and cannot inherit
one. Deploying the revised Owner artifact would require a new exact forward
restart-retirement binding from retained head 8, a fresh incarnation and bounded
remaining aggregate quota; reusing the old 7/8 binding is prohibited. That step
does not repair missing historical observations and must not be reported as a
known root-cause fix. No additional human LOGIN is requested or scheduled.

The existing SDK-repair profile is pinned to predecessor 6 and cannot be reused
against retained head 8. Its old per-process reservation is not a fresh aggregate
allowance: the accepted approval caps all runs/restarts/cleanup at 512 DynamoDB
attempts. The retained conservative allocation is 98 earlier non-Owner attempts,
134 prior Owner attempts, and 70 observed SDK-repair attempts, leaving at most
210. The existing complete SDK-repair model requires 272 attempts. These facts
do not establish a cost overrun, but they prohibit resetting the 280-attempt
process budget and starting another unchanged lifecycle. No new paid operation
or independent R retention write is dispatched on that unsupported basis.

See [bounded evidence](../research/nexus-production-n01-closed-authentication-stage-evidence-v1.json).
