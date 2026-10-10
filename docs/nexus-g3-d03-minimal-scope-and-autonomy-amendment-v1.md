# D03 Minimal Scope and Autonomy Amendment v1

2026-10-10. Source checkpoint: `7d1758ee6e2cdc04695bddef250eb3a9f6ee0e01`, branch `nexus-v2-g3-live-qualification`. This additive amendment records the Owner's explicit D03 scope correction. D01 is CLOSED_BOUNDED_LIVE_PROFILE and is not reopened. Historical setup/preflight findings remain historical; this amendment supersedes their requirement to pre-provision N01 resources or have the Owner manually supply discoverable AWS metadata.

## Minimal qualification boundary

D03 qualifies the independent recovery fence and its fail-closed consumer protocol. It does not build or qualify N01/N02. DynamoDB N01 transaction state, ECS tasks, ECR images, G3QualTaskExecution, G3QualDeployAdmin, G3QualExecutor, N01 application runtime and unrelated execution infrastructure are deferred to N01 or later stages. None is an entry prerequisite for minimal D03 unless an exact already accepted D03 requirement proves it indispensable; convenience is insufficient.

The existing independent journal, closed checkpoint/snapshot encoding, sequence lineage, version-aware complete-history checks, reservation uncertainty, quarantine, epoch/incarnation retirement and no-redispatch semantics are reused. Existing v1/D05 canonical bodies are unchanged. Isolated synthetic checkpoint and consumer-state fixtures are diagnostic data only and cannot become production authority. No real bearer or credential is stored in the journal. A canary harness can exercise D03 restart/retirement and unknown-outcome behavior without an N01 service or production grant.

| Required D03 gate | Minimal qualification observation |
|---|---|
| Independently protected state | Actual separate A/R account identities and effective custody/role/resource controls are verified. The accepted two-account requirement is retained. |
| Immutable / append-only history | Registered R journal versions show accepted Compliance retention; conditional creation and all-version readback are tested. Object Lock alone does not establish append-only sequencing. |
| Stale overwrite or revival | Old sequence/head/version/incarnation candidates cannot overwrite current journal state or select an older valid prefix as current. |
| Rollback / fork / gap | Standalone registered diagnostic histories, including isolated fault prefixes, reject restored old heads, duplicate versions, missing sequences/ancestors and delete markers. Normal history is not corrupted to manufacture evidence. |
| Unknown outcome | Dropped or ambiguous append acknowledgment quarantines until exact version-aware reconciliation; no alternative payload or sequence reuse. |
| Restart retirement | The D03 consumer restarts quarantined, uses current independent history, advances the required incarnation and rejects pre-restart synthetic authority references. No prior bearer is restored or serialized. |
| Generation / incarnation | Mismatched registered generation, epoch/incarnation or retained revision denies; caller input cannot replace protected registrations. |
| No automatic redispatch | Consumed/UNKNOWN diagnostic attempt references remain terminal across reconciliation and restart. Result evidence cannot authorize a retry. No real provider is dispatched. |
| Current protected recovery state | Recovery reads the latest complete independent history and all retained exact referenced bytes. Missing or unavailable evidence cannot be replaced by a new GENESIS. |
| Independent recovery administrator | Ordinary D03 caller/append permissions cannot administer R recovery state, role trust, policies or retention. Declared root/organization administrator reachability is evaluated, not hidden by a role name. |

Real fence service responses, injected faults and offline consumer assertions remain separate evidence classes. A fake-only test cannot close deployed enforcement. Successful minimal D03 closes this fence gate; N01 must subsequently qualify its actual ledger/fence crash serialization, real production provenance, restart and dispatch integration. D03 results do not claim those integrations already exist. D04 historical exclusion remains BLOCKED/unqualified and is not a Delegated Executor release gate; recovery custody and complete mediation remain independently required.

## Minimal identities and automatic discovery

Start with an existing protected, bounded A diagnostic caller. Create one D03-specific caller role only if existing legitimate access is unsuitable. R needs G3QualFenceAppendRead and an independently controlled G3QualRecoveryAdmin. Add a read-only observer or fault-injection role only when a concrete accepted test needs distinct custody; a fault role must be confined to registered fault prefixes. No N01/N02 role is pre-created.

The executor discovers caller/account IDs through authenticated provider metadata, chooses `ap-southeast-1`, and discovers exact role/resource/configuration metadata itself. Existing SSO/browser/temporary-credential mechanisms are preferred. It may draft and, within the authorized zero-cost/reversible scope and actual permissions, create minimum roles/policies. It must verify exact trust and permissions and cannot promote arbitrary local labels or a discovered account to Owner/recovery custody without the required authentication and protected context. Metadata discovery is not proof of effective controls.

Second-account discovery or creation may use a supported existing AWS mechanism only if its actual permission, legal, payment and custody boundaries are satisfied. No new paid/irreversible resource or long-lived access key is inferred. Root passwords/MFA, token/cache/cookie values and credential files are not extracted or exposed. Lack of a browser/CLI session is an access blocker, not an instruction for the Owner to write IAM JSON or copy ARNs.

## Current access evidence and continuation

At entry, AWS CLI was absent from PATH and the known system/current-user install locations. Config and shared-credential files at the configured/default locations were absent; relevant credential/profile environment presence checks were negative. Only presence was checked: no credential values, caches or browser cookies were read. No boto3/botocore/awscli Python module or AWS connector was available.

Available in-app tabs contained Nexus diagnostic/help pages. Chrome inventory failed its browser access-policy check, including one bounded focused retry; Chrome authentication remains UNKNOWN, not proved absent. It was not bypassed with browser-profile or credential-file extraction. The official AWS Console navigation selected Singapore and redirected to the visible official AWS IAM sign-in form with no authenticated account context.

Official CLI v2 current-user installation is authorized reversible preparation. Its vendor installer must pass Authenticode verification before execution; it needs no admin elevation. Version and profile/caller discovery are retained separately in ignored preparation evidence. Public documentation/installer downloads are distinct from authenticated AWS account actions. Installation alone does not establish access or a qualified fence.

The official AWSCLIV2-User.msi passed valid Amazon Web Services Authenticode verification and installed successfully for the current user, without elevation or restart. Installer SHA256: `ae7ec26348143a0a08210209b737ff6bc6b1e9b7e105c5c3f6c252d2fc006fd1`; installed CLI version: `2.37.12`. Profile enumeration returned zero profiles. One bounded read-only STS caller-discovery attempt, with local EC2 metadata probing disabled, reported no usable CLI credentials. Raw errors and credential values were not retained. The official browser remained at the actual IAM sign-in form. The only requested human action is account login and required MFA; no account ID, role ARN, IAM JSON or resource configuration is requested from the Owner.

At the unavailable login/MFA/account-holder boundary, hand off only that concrete action. Account IDs, Region, role ARNs, policies and bucket configuration are subsequently discovered/generated automatically where possible. Human legal/payment/signup/MFA/hardware steps cannot be synthesized. No manual architecture setup checklist is requested.

## Cost and irreversible retention gate

D03_BUDGET and S3_COMPLIANCE_RETENTION remain NOT_YET_ACCEPTED. No billable qualification operation or irreversible Object Lock configuration occurs before explicit bounded acceptance. When the first such action is concrete, present only its exact requested maximum cost, exact resource, exact retention effect, reversibility and necessity. Prior USD 25 and 7-day proposals are not acceptance or a hard billing cutoff. An estimate requires the actual minimal resource set; no N01 infrastructure is included to inflate that estimate.

After explicit acceptance of the bounded scope, do not ask repeated routine approvals. Stop on a materially different cost, irreversible effect or unavoidable human gate. Close D03 once all ten minimal gates pass; proceed directly to N01 without expanding D03.

Documentary validation passed all ten scope entries, 134 G3 regressions and 11 isolated package tests. Deterministic MANIFEST contains 503 accepted entries. All prior tracked source, contracts and documents remain unchanged except the regenerated manifest. Bounded secret/private-key scanning, unchanged diagnostic artifact validation and git diff --check passed. Ignored installer/access evidence and the three unrelated Route D files are excluded. This validates the correction and preparation only; actual D03 service enforcement remains unverified.

```text
D01_STATUS = CLOSED_BOUNDED_LIVE_PROFILE
D03_SCOPE = MINIMAL_INDEPENDENT_RECOVERY_FENCE
D03_N01_N02_PREBUILD = FORBIDDEN
D03_DYNAMODB_ECS_ECR_CREATED = 0
D03_N01_ROLES_CREATED = 0
D03_TWO_ACCOUNT_REQUIREMENT = PRESERVED
D03_METADATA_DISCOVERY = AUTONOMOUS_AUTHENTICATED_ONLY
D03_MANUAL_IAM_SETUP_REQUIRED = NO
AWS_CLI_PREPARATION = COMPLETE_CURRENT_USER_NO_ELEVATION
AWS_ACCESS = HUMAN_LOGIN_REQUIRED
D03_OFFLINE_PROTOCOL = DEFINED
D03_DEPLOYED_ENFORCEMENT = UNVERIFIED
D03_RECOVERY_FENCE = CONDITIONAL
D03_BUDGET = NOT_YET_ACCEPTED
S3_COMPLIANCE_RETENTION = NOT_YET_ACCEPTED
REAL_ADMISSION_ENABLED = NO
FAIL_CLOSED_BOUNDARY = PRESERVED
```
