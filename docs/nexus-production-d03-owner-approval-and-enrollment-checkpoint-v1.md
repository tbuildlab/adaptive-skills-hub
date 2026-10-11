# D03 Owner approval and independent account enrollment checkpoint v1

2026-10-11. Approved package checkpoint:
`ec5493f49938c116c17889815f4a45b9feed5efb`, branch
`nexus-v2-production-qualification`.

## Explicit Owner authorization

The Owner explicitly approved the
[D03 custody authorization package](nexus-production-d03-custody-authorization-package-v1.md)
in the current conversation. The approval binds that committed package and permits:

- Maximum incremental D03 qualification operation expenditure of USD 1.00,
  including applicable tax, within its resource, request, byte and time limits.
- S3 Object Lock **Compliance** retention of seven days per version.
- A Paid Plan upgrade only where necessary for this qualification.
- Automatic continuation from qualified D03 through G3 and Production Final,
  preserving the previously required upstream/live/independent-review/Owner gates.

The Owner explicitly forbids spending beyond USD 1.00, unrelated AWS resources,
premature REAL_ADMISSION, and continued operations if projected costs exceed the
approved ceiling without renewed approval. No routine cost/retention approval is
needed again inside this unchanged scope. Sustained production custody and an
expanded resource/budget/retention scope remain outside the D03-only package.

This is an audit of direct human authorization, not a bearer, runtime grant,
qualification result, independent review or final release acceptance. Copying this
document cannot authorize execution. Earlier PENDING statements remain historical
pre-approval observations and are superseded only for this exact approved scope.

## Protected session and separate account boundary

The protected AWS Console CloudShell remains available in Owner account R
`862902859484`. Its observed principal is root; its last authenticated account-plan
response is `FREE` / `ACTIVE`. This is trusted setup access, not qualified ordinary
executor authority. No second-account identity has been established. The earlier
Organizations response and two service roles do not supply the missing A account.

Preserve the approved topology: two standalone accounts, no AWS Organization.
Do not convert the current account into two local role labels and claim independent
custody. Do not infer a second account, invent a deliverable root email, extract
credentials, or substitute a structural fixture for its authenticated identity.

The official registration flow reached
`https://signin.aws.amazon.com/signup?request_type=register` through AWS's visible
Sign up (advanced) control. Only the non-secret account name
`NexusD03DiagnosticA` was filled. The root email remains empty. No registration
request, verification message, terms acceptance or new credential was submitted.
The page is handed to the Owner for second-account registration/authentication.
No email, password, OTP, payment details or account session is requested in chat.

This is a genuine account-holder boundary: the protected second-account enrollment
identity and verification are unavailable to the implementing agent. Account names
and IAM configuration are handled automatically; identity/credential enrollment and
required legal acceptance cannot be fabricated. The requested single Owner action
is to complete and sign in to the second independent account in the open official
page, then report completion. No manual IAM, ARN, resource ID or command checklist.

Keep current R CloudShell and the second-account enrollment page available for
continuation. Do not inspect user-entered password/OTP fields or save a screenshot
after sensitive values are entered. The pre-entry screenshot contains only an empty
email field and the prepared non-secret account name, outside the repository.

## Expenditure and qualification disposition

At this checkpoint no account-plan upgrade, Organization, account, IAM role, S3
bucket, billable S3 request, retained object or irreversible retention configuration
has been created. T0 for the approved resource window has **not started**.
The conditional candidate and estimated USD 0.108 metered envelope remain estimates;
there is no provider-enforced USD 1.00 account cap. No production authority or
independent-review result has been produced.

Do not start otherwise avoidable paid or irreversible custody setup while the
required A enrollment is unavailable. Once enrollment is complete, discover and
bind actual A/R identities automatically, then deploy the minimum approved roles,
exact bucket/prefixes and bounded diagnostic harness. Verify effective isolation,
version-aware retention, conditional append, current-head and complete-history
checks, crash/restart retirement, quarantine and NO_AUTOMATIC_REDISPATCH before
closing D03. No D01 ceremony or G4/G6 architecture is reopened.

```text
D03_BOUNDED_COST_APPROVAL = APPROVED_USD_1_00
D03_RETENTION_APPROVAL = APPROVED_COMPLIANCE_7_DAYS
D03_NECESSARY_PLAN_UPGRADE_APPROVAL = APPROVED_WITHIN_QUALIFICATION_SCOPE
D03_ACCOUNT_TOPOLOGY = TWO_STANDALONE_ACCOUNTS_NO_ORGANIZATION
D03_R_ACCOUNT = 862902859484
D03_A_ACCOUNT = NOT_YET_ESTABLISHED
D03_PAID_OPERATIONS = 0
D03_IRREVERSIBLE_RETENTION_OPERATIONS = 0
D03_RESOURCE_WINDOW_T0 = NOT_STARTED
D03_EFFECTIVE_CUSTODY_QUALIFICATION = BLOCKED_ACCOUNT_HOLDER_ENROLLMENT
D03_STATUS = NOT_CLOSED
G3_STATUS = INCOMPLETE
D01_STATUS = CLOSED
G4_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
G6_STATUS = COMPLETE_PREPARATION_FAIL_CLOSED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
HUMAN_ACTION_REQUIRED = SECOND_INDEPENDENT_ACCOUNT_ENROLLMENT_AND_LOGIN
```

Technical and final Owner release gates remain unmet. This checkpoint neither
weakens an accepted security property nor claims Production Final completion.
