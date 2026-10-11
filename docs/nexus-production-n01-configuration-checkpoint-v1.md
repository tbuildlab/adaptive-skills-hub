# N01 exact bounded configuration checkpoint v1

2026-10-11. Implements only the scope in the explicit
[Owner budget receipt](nexus-production-n01-owner-budget-receipt-v1.md).
Configuration is not source authentication, runtime qualification or release.
The [bound input](../research/nexus-production-n01-bound-configuration-v1.json)
records the exact approved scope. Actual deployment is described separately below.

## Actual A configuration

The authenticated native A CloudShell identity was root in account 175880707430.
Preflight proved the exact new roles, table and cleanup group absent. Native
account metadata reported PAID/ACTIVE; no upgrade, payment-method modification
or static access key was performed. The configuration's conservative window began
2026-10-11T10:51:37Z; runtime trust/permissions expire 2026-10-13T10:51:37Z.

Actual exact resources: NexusG3QualificationCaller, NexusG3QualificationCleanup,
Singapore NexusG3QualificationCleanupV1 group and its single
NexusG3QualificationDeleteTableV1 job, then ON_DEMAND NexusG3AuthorityV1 table.
The cleanup role permits only DeleteTable on that exact table and trusts only the
native Scheduler service with exact account and group SourceArn. Target input,
zero retries, UTC/no-flex schedule and deletion-after-completion were read back.
Deletion is scheduled for 2026-10-13T11:01:37Z, not demonstrated as completed.

The first create_schedule response was ValidationException; read-only reconciliation
found the job/table absent and exact role policies intact. A later explicit setup
repair succeeded before table creation. No unknown authority write was retried.
Seven successful resource mutations; zero DDB data-plane calls and zero new S3
objects at this configuration checkpoint. The table's immediate readback was
CREATING, not an asserted ACTIVE/service-qualified result.

Authenticated existing Vercel project security settings showed Team issuer
https://oidc.vercel.com/tdy0225, audience https://vercel.com/tdy0225 and subject
owner:tdy0225:project:nexus-g3-qual:environment:production. Only after that actual
native setting verification, one exact IAM OIDC provider and the second approved
Caller trust statement were applied/read back. GitHub's exact immutable-ID branch
binding and original Caller permissions were preserved. Both origins are bounded
by the same deadline; there is no subject, issuer or audience wildcard.

That proves configuration equality only. No Vercel runtime token was inspected,
logged, exported or copied. Actual Vercel-to-A federation remains NOT_PERFORMED.
IAM retrieves CA thumbprints natively; no custom signing or credential subsystem
was introduced. [Official native provider API](https://docs.aws.amazon.com/IAM/latest/APIReference/API_CreateOpenIDConnectProvider.html).

## Actual R configuration

Authenticated native R CloudShell root identity was 862902859484. Four successful
mutations created NexusG3N01AppendRead, its sole N01ExactCustodyOnly inline policy,
four exact new bucket DENY statements and six new prefix lifecycle rules.
Readback confirmed exact A Caller trust/session/deadline, conditional normal-only
append and three-prefix version/retention reads; no attached policies, admin,
delete, retention change or fault/approval write permissions. Approval mutations
are independently limited to R root. New prefix inventory was empty.

All four prior D03 bucket statements and four lifecycle rules remained unchanged.
The old diagnostic role's explicit denial and absence of inline/attached grants
were preserved. Versioning and Compliance seven-day bucket defaults were read
only to establish configuration compatibility; D03 was not requalified.

Native sanitized receipt reported 12 S3 configuration/read attempts, zero new
objects, bucket policy SHA-256
`63987cbec2dad09c2cd756632e4c834eb83b76856794aa949c4a510a93a12ec8`,
and bound R input SHA-256
`3632c49345ea111aa992b27a8645e44f479fe7685c98ac04515147891fd0a2d1`.
Lifecycle/table deletion remain scheduled, not observed completed. Across setup,
there were 13 successful resource/IAM mutations, zero DDB data-plane attempts and
zero new retained versions. This is CONFIGURED_NOT_QUALIFIED.

## Current limits

 D03's closed diagnostic
registration/role remains retired; old Object Lock, retention and offline closure
are not rerun. No N01 production membership, Owner enrollment/CONFIRM, receipt,
grant, positive G4 admission, G6 live gate or independent review is asserted.
Additional ceiling remains USD 1.00 inclusive of tax; actual invoice is UNKNOWN.
All data-plane/failure/restart work must retain the approved aggregate bounds.

```text
A_BOUNDED_RESOURCE_CONFIGURATION = EXACT_READ_BACK
VETTED_VERCEL_NATIVE_OIDC_CONFIGURATION = EXACT_READ_BACK_NOT_RUNTIME_QUALIFIED
R_NEW_PREFIX_CONFIGURATION = EXACT_READ_BACK_NOT_RUNTIME_QUALIFIED
N01_LIVE_QUALIFICATION = NOT_PERFORMED
CLEANUP_STATUS = SCHEDULED_NOT_COMPLETED
REAL_ADMISSION_ENABLED = NO
```
