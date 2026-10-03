# Nexus G2 Route B Candidate Expansion Screening Matrix v1

Version: `1.0.0`

Retrieval / checkpoint date: **2026-10-03**

Baseline: `fa40fb3447e20bebcb0b293f23afad406b72c61f` / `nexus-v2-g2-development`

Status: **FACTUAL PUBLIC-EVIDENCE CHECKPOINT ONLY - NO ACCEPTANCE, SELECTION OR EXPERIMENT AUTHORITY**

Authority, source tiers/hashes and state: [nexus-g2-route-b-expansion-source-register-v1.md](nexus-g2-route-b-expansion-source-register-v1.md). All statuses below are documentary coverage, never measured PASS. Missing-property owner uses PROVIDER/NEXUS/COMPOSITE/EXPERIMENT. A future bounded experiment column is CONDITIONAL only after amendment section 7 premises close; none is safe now.

## 1. Entry screens

| Provider | Isolated / managed boundary | Lifecycle / resource-time interface | Result observation | Credentials / public pricing | Entry result |
| --- | --- | --- | --- | --- | --- |
| Blaxel | Hosted VM (B01) | Lifecycle + creation-age expiry + memory (B01/B02) | Sandbox name/status; process/log references (B01/B03/B11) | External API key + scoped session; B04/B07/B10 | LEGITIMATE CANDIDATE; hard-envelope evidence incomplete |
| Runloop | Hosted Devbox microVM (R04) | Fixed lifetime/size/shutdown/suspend (R01/R03/R09) | Devbox/execution IDs/status/logs (R07/R09) | Control bearer external; optional opaque gateway (R06); R04 rates | LEGITIMATE CANDIDATE; shutdown/timer/cost gaps |
| Vercel | Linux microVM (V01) | Session timeout/stop/resources (V02/V04) | Status/session/command results (V04) | OIDC/access token external (V07); V02 pricing | LEGITIMATE CANDIDATE; session versus object scope distinct |
| Cloudflare | Container Linux VM separated from Worker/DO (C02/C09) | Native lifecycle/instance sizes; legacy SDK distinct (C01/C03/C06) | Native exec/monitor/inspect; durable example (C08/C09) | Worker-bound control/secrets; public multi-product rates (C02/C04) | LEGITIMATE CANDIDATE; whole-unit lifetime not closed |

## 2. Exact P1-P12 screening

Property names retain the accepted contract meaning. Required provenance covers actual Nexus-controlled bytes/dependencies, not a universal provider kernel transcript. No source silence is an UNSUPPORTED finding. No EXPERIMENT_RESOLVABLE label can defer a safety premise beyond its first effect.

### Blaxel

| ID | Property | Status | Opened evidence | Remaining UNKNOWN / missing proof | Missing-property owner | Future safe experiment? |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Deployment / instance identity | PARTIAL | B01/B11: name, state and configured image; B02 expiresIn. | Actual admitted Nexus-controlled image/code/dependency and operation identity substitution/freshness proof. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P2 | Control/data-plane separation | PARTIAL | B07 restricted sandbox session; B10 non-root API isolation; B06 optional proxy. | Actual actor exclusion, effective custody and indirect mutation/credential reachability. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P3 | Effective isolation / policy observation | PARTIAL | B05 explicit immutable-at-create firewall; B10 API deny pre-workload. | Subject-external applied control binding and drift-safe release; stored settings alone insufficient. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P4 | Execution input boundary | PARTIAL | B03 command/cwd/timeout; B05/B10 guest boundary; inputs require Nexus closure. | Closed command/file/env/mount/network/service/descendant graph and independent effective observations. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P5 | Resource limits | PROVIDER_CLARIFICATION_REQUIRED | B02 max-age basis; B01 memory-linked CPU/standby. | Whole-unit fixed deadline, hard allocations/output and bounded fault termination; see deep review. | PROVIDER | NO - hard premise unresolved |
| P6 | Hard cost boundary | PROVIDER_CLARIFICATION_REQUIRED | B04 compute/retention rates and included egress; B08 survivor volumes; B09 delayed accounting. | All reachable driver maxima, current rate/minimum/tail/cutoff plus protected conservative reservation. | NEXUS | NO - hard premise unresolved |
| P7 | Cancellation | PARTIAL | B03 kill; B12 delete; B01 DELETING versus TERMINATED. | Whole-unit ultimate bound, exact cessation/resources/billing/effect observations; see eleven-state split. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P8 | Observation | PARTIAL | B03 status/exit/output and B11 config/name; B09 usage series. | Authenticated exact operation/effect and retention/gap coverage; result not task acceptance. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P9 | Interruption / unknown effects | PARTIAL | B01 standby restores processes; pinned SDK resume can recreate after lookup failure. | Durable original references/exposure and no retry while UNKNOWN; SDK replacement must be disabled/excluded. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P10 | Evidence integrity | PARTIAL | B11 external config/name readback + protected Nexus receipt composition needed. | Qualified external controller receipt custody, scope/source/time and replay/tamper protection. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P11 | BYOK / credential model | PARTIAL | B03 external BL_WORKSPACE/BL_API_KEY; B07 no platform rights for scoped session. | Owner account custody, compute-versus-model separation and revocation/invalidation proof. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P12 | Version / capability drift | PARTIAL | B01 in-place API upgrades possible; B05 Mark3-only firewall; exact versions must bind. | Pinned SDK/API/mode/config, expiry/revalidation and material drift STOP. No hidden backend digest required. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |

### Runloop

| ID | Property | Status | Opened evidence | Remaining UNKNOWN / missing proof | Missing-property owner | Future safe experiment? |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Deployment / instance identity | PARTIAL | R09 Devbox/execution/blueprint references and query API. | Actual admitted Nexus-controlled image/code/dependency and operation identity substitution/freshness proof. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P2 | Control/data-plane separation | PARTIAL | R06 origin-bound gateway and R05 separate toggles; raw platform key need not enter guest. | Actual actor exclusion, effective custody and indirect mutation/credential reachability. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P3 | Effective isolation / policy observation | PARTIAL | R05 deny-all interface; policy-ID and actor graph remain necessary. | Subject-external applied control binding and drift-safe release; stored settings alone insufficient. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P4 | Execution input boundary | PARTIAL | R07 shells/env/async execution; R09 file/tunnel/secret/gateway surfaces must be closed. | Closed command/file/env/mount/network/service/descendant graph and independent effective observations. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P5 | Resource limits | PROVIDER_CLARIFICATION_REQUIRED | R01 fixed versus idle; R09 max 172800s; R03 resource tuples. | Whole-unit fixed deadline, hard allocations/output and bounded fault termination; see deep review. | PROVIDER | NO - hard premise unresolved |
| P6 | Hard cost boundary | PROVIDER_CLARIFICATION_REQUIRED | R04 prices; R02 counted lifecycle phases; R09 suspended disk usage. | All reachable driver maxima, current rate/minimum/tail/cutoff plus protected conservative reservation. | NEXUS | NO - hard premise unresolved |
| P7 | Cancellation | PARTIAL | R09 shutdown/force, command process-group kill and status-query methods. | Whole-unit ultimate bound, exact cessation/resources/billing/effect observations; see eleven-state split. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P8 | Observation | PARTIAL | R07 execution results; R09 logs/status/usage and shutdown reason. | Authenticated exact operation/effect and retention/gap coverage; result not task acceptance. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P9 | Interruption / unknown effects | PARTIAL | R08 disk snapshots; R09 status/query; pinned SDK resume can reprovision. | Durable original references/exposure and no retry while UNKNOWN; SDK replacement must be disabled/excluded. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P10 | Evidence integrity | PARTIAL | R09 provider IDs/queries; protected ordered receipt is Nexus-owned. | Qualified external controller receipt custody, scope/source/time and replay/tamper protection. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P11 | BYOK / credential model | PARTIAL | Control bearer separate from optional service gateway secret (R06/R09). | Owner account custody, compute-versus-model separation and revocation/invalidation proof. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P12 | Version / capability drift | PARTIAL | R09 schema version 0.1; R03 contradictory size example; pin mode/SDK. | Pinned SDK/API/mode/config, expiry/revalidation and material drift STOP. No hidden backend digest required. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |

### Vercel

| ID | Property | Status | Opened evidence | Remaining UNKNOWN / missing proof | Missing-property owner | Future safe experiment? |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Deployment / instance identity | PARTIAL | V04 sandbox/project/name/session/command and status references. | Actual admitted Nexus-controlled image/code/dependency and operation identity substitution/freshness proof. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P2 | Control/data-plane separation | PARTIAL | V07 external OIDC/access token; V05 provider firewall transforms. | Actual actor exclusion, effective custody and indirect mutation/credential reachability. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P3 | Effective isolation / policy observation | PARTIAL | V05 deny-all supported; V04 runtime network policy mutable. | Subject-external applied control binding and drift-safe release; stored settings alone insufficient. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P4 | Execution input boundary | PARTIAL | V04 command/env/cwd/ports/mounts; fixed deny-all/no ports/no drives not observed. | Closed command/file/env/mount/network/service/descendant graph and independent effective observations. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P5 | Resource limits | PROVIDER_CLARIFICATION_REQUIRED | V02 hard session maxima; V03 resume resets; V04 persistent default. | Whole-unit fixed deadline, hard allocations/output and bounded fault termination; see deep review. | PROVIDER | NO - hard premise unresolved |
| P6 | Hard cost boundary | PROVIDER_CLARIFICATION_REQUIRED | V02 eight rates and explicit no-additional-Sandbox-charge Hobby policy; V06 retained snapshots. | All reachable driver maxima, current rate/minimum/tail/cutoff plus protected conservative reservation. | NEXUS | NO - hard premise unresolved |
| P7 | Cancellation | PARTIAL | V04 stop resolves VM stopped with session metrics; persistence/deletion separate. | Whole-unit ultimate bound, exact cessation/resources/billing/effect observations; see eleven-state split. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P8 | Observation | PARTIAL | V04 exit/status/metrics; persistent name can span sessions, bind exact session. | Authenticated exact operation/effect and retention/gap coverage; result not task acceptance. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P9 | Interruption / unknown effects | PARTIAL | V03 new-session resume; V06 retained snapshots; SDK fallback can create anew. | Durable original references/exposure and no retry while UNKNOWN; SDK replacement must be disabled/excluded. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P10 | Evidence integrity | PARTIAL | V04 provider final session record plus required protected Nexus receipts. | Qualified external controller receipt custody, scope/source/time and replay/tamper protection. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P11 | BYOK / credential model | PARTIAL | V07 user-controlled project/team OIDC or access token; no bundled Nexus key. | Owner account custody, compute-versus-model separation and revocation/invalidation proof. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P12 | Version / capability drift | PARTIAL | V02 >=3.0 resource semantics vs pinned OpenAI JS development peer 1.9.3; qualification cannot mix. | Pinned SDK/API/mode/config, expiry/revalidation and material drift STOP. No hidden backend digest required. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |

### Cloudflare

| ID | Property | Status | Opened evidence | Remaining UNKNOWN / missing proof | Missing-property owner | Future safe experiment? |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Deployment / instance identity | PARTIAL | C09 digest-pinned images map/labels/inspect; DO name is not caller authentication (C02). | Actual admitted Nexus-controlled image/code/dependency and operation identity substitution/freshness proof. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P2 | Control/data-plane separation | PARTIAL | C02 Worker/Container separation and external secrets; all guest processes share root capabilities. | Actual actor exclusion, effective custody and indirect mutation/credential reachability. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P3 | Effective isolation / policy observation | PARTIAL | C02 1.0 Internet-off + interception; no independent same-user boundary assumed. | Subject-external applied control binding and drift-safe release; stored settings alone insufficient. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P4 | Execution input boundary | PARTIAL | C09 exec direct argv/env/cwd/std-stream options; C06 legacy bridge differs. | Closed command/file/env/mount/network/service/descendant graph and independent effective observations. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P5 | Resource limits | PROVIDER_CLARIFICATION_REQUIRED | C01 inactivity <=6h, activity defers it; C03 instance sizes. | Whole-unit fixed deadline, hard allocations/output and bounded fault termination; see deep review. | PROVIDER | NO - hard premise unresolved |
| P6 | Hard cost boundary | PROVIDER_CLARIFICATION_REQUIRED | C04 Container+Worker+DO+network+logs; C03 retained snapshot duration. | All reachable driver maxima, current rate/minimum/tail/cutoff plus protected conservative reservation. | NEXUS | NO - hard premise unresolved |
| P7 | Cancellation | PARTIAL | C09 direct-process kill versus awaited container destroy; C08 stop-record pattern. | Whole-unit ultimate bound, exact cessation/resources/billing/effect observations; see eleven-state split. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P8 | Observation | PARTIAL | C09 exec exit/result/monitor/inspect; C08 durable stop records are example, not deployed receipt. | Authenticated exact operation/effect and retention/gap coverage; result not task acceptance. | COMPOSITE | CONDITIONAL - after P5/P6 and pre-effect protections |
| P9 | Interruption / unknown effects | PARTIAL | C01 restart/restore gives new instance; C08 durable state pattern; no deployed closure. | Durable original references/exposure and no retry while UNKNOWN; SDK replacement must be disabled/excluded. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P10 | Evidence integrity | PARTIAL | C09 provider observation in trusted Worker plus protected Nexus receipt still required. | Qualified external controller receipt custody, scope/source/time and replay/tamper protection. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P11 | BYOK / credential model | PARTIAL | C02 Worker custody; OpenAI bridge auth distinct from platform/account/model keys. | Owner account custody, compute-versus-model separation and revocation/invalidation proof. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |
| P12 | Version / capability drift | PARTIAL | C06 native 1.0 versus legacy 0.12; pinned OpenAI HTTP bridge does not prove 1.0 migration. | Pinned SDK/API/mode/config, expiry/revalidation and material drift STOP. No hidden backend digest required. | NEXUS | CONDITIONAL - after P5/P6 and pre-effect protections |

## 3. Qualification responsibility mapping (none PASS)

PROVIDER-MANDATORY identifies platform facts; COMPOSITE identifies provider enforcement plus Nexus binding; NEXUS-OWNED retains governance/evidence; QUALIFICATION-EXPERIMENT labels later measurement only under an already safe envelope. Each provider below has these four distinct categories; no provider-only receipt substitutes for Nexus HQ5/HQ6.

| ID / class | Blaxel | Runloop | Vercel | Cloudflare |
| --- | --- | --- | --- | --- |
| HQ1 / COMPOSITE | B01/B11 image/API + Nexus-controlled actual-byte proof missing | R09 blueprint/ID + actual-byte proof missing | V04 image/session + actual-byte proof missing | C09 image/label + actual-byte proof missing |
| HQ2 / PROVIDER-MANDATORY + COMPOSITE | B05/B10 exact VM/API/egress negatives unrun | R05 exact Devbox/policy/actor negatives unrun | V05 exact microVM/firewall negatives unrun | C02/C09 VM/Worker/Internet boundary negatives unrun |
| HQ3 / COMPOSITE | B07/B10 custody/env/guest API reachability unproven | R06/R09 control key/gateway/env reachability unproven | V07/V04 key/env/drive boundary unproven | C02 Worker secrets/guest shared-root inputs unproven |
| HQ4 / PROVIDER-MANDATORY + COMPOSITE | B02 expiry/failure/descendant/cost tail open | R01/R09 fixed clock/fault/tree/cost tail open | V02/V04 session plus no-resume/persistence closure open | C01/C09 activity/ultimate hard deadline/cost tail open |
| HQ5 / NEXUS-OWNED | Protected same-unit issuer/source/time receipts missing | Protected same-unit issuer/source/time receipts missing | Protected same-session issuer/source/time receipts missing | Protected DO/instance/version receipts missing |
| HQ6 / NEXUS-OWNED + COMPOSITE | Admission/reservation/one-attempt/cancel/recovery/reconcile NOT STARTED | Admission/reservation/one-attempt/cancel/recovery/reconcile NOT STARTED | Admission/reservation/one-attempt/cancel/recovery/reconcile NOT STARTED | Admission/reservation/one-attempt/cancel/recovery/reconcile NOT STARTED |

For all four, QUALIFICATION-EXPERIMENT = actual applied-byte/input/channel/credential negatives, lost-response/cancel/controller-loss, artifact/effect/usage binding after safety premises close. These are NOT RUN and not presently authorized. No local/remote HQ or P-item is PASS. The designated workload may be one deterministic synthetic capability without a model; a generic agent runtime is neither needed nor authorized.
