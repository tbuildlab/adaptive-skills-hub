# Nexus G2 Route B Expansion P5 P6 P7 Deep Review v1

Version: `1.0.0`

Retrieval / checkpoint date: **2026-10-03**

Baseline: `fa40fb3447e20bebcb0b293f23afad406b72c61f` / `nexus-v2-g2-development`

Status: **FACTUAL PUBLIC-EVIDENCE CHECKPOINT ONLY - NO ACCEPTANCE, SELECTION OR EXPERIMENT AUTHORITY**

Authority/source binding: [nexus-g2-route-b-expansion-source-register-v1.md](nexus-g2-route-b-expansion-source-register-v1.md). Exact P rows/entry/HQ mapping: [nexus-g2-route-b-expansion-screening-matrix-v1.md](nexus-g2-route-b-expansion-screening-matrix-v1.md). The following are documented semantics or expressly labelled inference/UNKNOWN; no provider account/instance was observed.

## 1. P5 - all fifteen questions

| P5 question | Blaxel | Runloop | Vercel | Cloudflare |
| --- | --- | --- | --- | --- |
| 1. Total wall-clock maximum? | B02 creation-age policy exists; ultimate fault envelope UNKNOWN. | R01 fixed maximum; R09 max 48h parameter; clock phases UNKNOWN. | V02 session cap only; V03 total persistent lifetime unbounded. | C01 only inactivity; no whole-unit maximum established. |
| 2. Provider enforcement? | Expiry service documented; applied exact-mode behavior unverified. | Automatic shutdown documented; actual timer/fault semantics unverified. | Session automatic stop documented; object cap not supplied. | Provider inactivity/VM destroy documented; total deadline not supplied. |
| 3. Hard bound or default? | Configured age expiry differs from standby/default; no immutable fault-tail proof. | 1h default versus explicit fixed seconds <=48h; not idle combination. | 5m default versus plan session ceiling; not total object ceiling. | 6h maximum inactivity interval; no maximum continuous activity. |
| 4. Workload disable/reset/extend/descendant evasion? | B10 non-root isolation candidate; default root/localhost API unsafe; mutation-exclusion UNKNOWN. | Platform key exclusion possible; R09 keep_alive resets idle, not documented fixed timer; guest/descendant exclusion UNKNOWN. | Control credential exclusion possible; guest authority to mutate/resume not qualified. | C02 root guest must be separated from Worker; requests/channels may sustain DO; actual closure UNKNOWN. |
| 5. Controller indefinite extension/reset? | B02 can clear/update configured expiry; excluded future no-extension actor graph could matter. | R09 idle reset documented; no evidence fixed lifetime mutates via same endpoint; resume/recreate authority separate. | V03 repeated resume indefinitely; V04 updates/extension; forbid those paths in any candidate composition. | Legacy C07 keepAlive indefinite; native C01 alarms/requests sustain activity. |
| 6. Ultimate bound after controller loss? | Creation-age expiry plausible independent mechanism; failure and alternate actor coverage missing. | Fixed shutdown plausible independent mechanism; provision/resume/suspend/fault scope missing. | One session cap plausible; auto-persistence/storage/new sessions need separate closure. | Inactive DO eventually stops instance; pending request/stream/alarm failure tail not whole-unit bounded. |
| 7. Elapsed setup/main/desc/background/paused/stopped/resume/cleanup? | From creation supports age across standby; build/setup boundary and cleanup tails not quantified. | Fixed clock origin/setup/paused/resume coverage UNKNOWN; storage continues while suspended. | Session covers running work; stopped retention/resume starts separate clock; setup/cleanup tail UNKNOWN. | Activity timeout covers inactivity after DO work; no summed setup/active/pause/resume/cleanup envelope. |
| 8. Expiry outcome? | B02 delete; B01 TERMINATED distinct from standby process restore. | R01 automatic shutdown; R09 permanent stop; detailed expiration/fault outcomes UNKNOWN. | V02/V03 session stop, possibly snapshot; entity/drive may remain. | C01 SIGTERM then instance stop; instance processes/files end; snapshots/DO remain separately. |
| 9. Sync or async? | B01 DELETING transition; B12 request not proven terminal barrier. | R09 shutdown + status wait; endpoint return not universal cessation proof. | V04 awaited stop resolves VM fully stopped; snapshot metadata distinct. | C09 destroy promise resolves destruction; legacy C07 not mixed into native guarantee. |
| 10. Maximum termination delay? | No numerical fault-path maximum established. | No numerical fault-path maximum established. | No numerical fault-path maximum established. | C01 shortly after is not a numerical fault-path maximum. |
| 11. Descendant/process-tree guaranteed termination? | Whole-VM deletion intent; process kill not full tree; failure coverage UNKNOWN. | R09 group kill optional; VM shutdown intent; ultimate tree bound UNKNOWN. | V04 stopped microVM strongest unit observation; external/persistent effects not descendants. | C01 instance stop ends every command; C09 kill only direct process; full failure-bound UNKNOWN. |
| 12. Provider CPU ceiling? | B01 memory-derived allocation; hard burst/ceiling contract UNKNOWN. | R03/R09 allocated tuple; hard enforcement details UNKNOWN. | V02 plan/vCPU tuples; entitlement not measured runtime ceiling. | C03 VM size; exact applied hard ceiling needs qualification. |
| 13. Provider memory ceiling? | Configured memory exists; authoritative non-workload-relaxable scope not fully proven. | RAM request exists; conflicting R03 example not binding. | 2GB/vCPU and plan maxima documented; actual applied ceiling unverified. | C03 instance memory; actual applied ceiling unverified. |
| 14. Disk/persistence separately bounded? | B08 volumes and B04 memory/filesystem snapshots; quantity/retention tails open. | R03 disk tuple; R08 snapshots and R09 suspended storage; residual bound open. | V02 ephemeral disk + V06 snapshots/drives; persistence false possible, scope must verify. | C03 disk + snapshot retention, optional R2/DO/image storage independent. |
| 15. Outside resources after compute? | Volumes/images/snapshots/archives can survive; optional graph not admitted here. | Suspended disk/snapshots/blueprints/objects/service effects may survive. | Persistent sandbox snapshots/drives/images/network or service effects may survive. | DO/Worker/image/snapshot/R2/log objects and service effects may survive. |

All P5 totals remain NOT CLOSED. This does not infer undocumented failure delays are infinite; it means no conservative finite maximum is presently established. Native whole-unit versus direct-process termination are distinguished. Nexus-owned bounded output/process/input design can supplement a qualified platform ceiling, but no paper control supplies an absent provider ultimate fallback.

## 2. P6 - driver closure and finite expression

Use the following symbolic upper bound, never a live estimate:

`C_max = F_plan + sum_i(ceil(Q_i_max / increment_i) * R_i_max) + C_setup_failed_create + C_termination_delay + C_cleanup + C_retained + C_retry_internal + C_overshoot + C_late_tail + C_external_services`

Every reachable quantity, billing increment, rate and failure inclusion must be finite and authoritatively bound. Do not double-count CPU already included in memory-priced compute. Rates here are dated public observations, not immutable future promises. Freeze the current maximum applicable rate/version/region before any separately authorized dispatch. Optional resources can be zero only after verified no-create/no-mount/no-call/no-retry operation and actor closure, including controller loss. No SDK/environment was installed or tested.

| Billable driver | Blaxel | Runloop | Vercel | Cloudflare |
| --- | --- | --- | --- | --- |
| Compute / CPU | B04 active allocation-memory rate; CPU included | R04 separate CPU seconds; R02 phase-counting conflict | V02 active CPU hours and one session cap | C04 active CPU per 10ms granularity |
| Memory | B04 active allocated GB-seconds | R04 allocated GB-seconds | V02 provisioned GB-hours, >=1 minute billing | C04 provisioned GiB-seconds |
| Disk / volume / persistence | B04 snapshot/volume rates; B08 survives delete | R04 Devbox disk seconds including suspended (R09) | V02 drives storage/read/write; no drives requires closure | C04 provisioned disk; DO/R2 other products separately |
| Snapshots | B04 standby snapshot GB-months; age cleanup tail open | R04 snapshot GB-hours; R08 no all-in finite deletion tail | V06 expiry/use refresh; V02 storage rates | C03 30-day retention/restore refresh; snapshot pricing completeness UNKNOWN |
| Images / builds | B04 image storage; no custom build only a conditional exclusion | R04 blueprint builds/storage | Managed image/no owned image build conditional; custom/VCR extras UNKNOWN | Owned images registry/storage/build charges require bounded scope or exclusion |
| Stopped / paused | Standby compute zero but snapshot retained | Suspended compute zero after transition; disk remains | Stopped snapshots/drives retained; session reset on resume | Stopped instance compute ends; Worker/DO/snapshot objects persist |
| GPU | No GPU admitted; service availability/charges not assumed zero universally | No GPU admitted; exact offer UNKNOWN | No GPU in inspected Sandbox tuples; no separate service admitted | No GPU in inspected tuples; no other service admitted |
| Network egress | B04 included; financial inclusion does not grant authority | R05 describes unexpected network charges; R04 exhaustive rate/inclusions UNKNOWN | V02 outbound + exposed-port both directions; region matters | C04 egress rate by region |
| Ingress | B04 inclusion/all-in coverage needs confirmation | Exhaustive inclusion/rate UNKNOWN | Internet downloads free; exposed-port ingress billable V02 | Container/Worker ingress charging inclusion needs exact scope |
| Requests / API operations | No complete all-operation charging/failed-call inclusion proven | No complete all-operation charging/inclusion proven | V02 creation fee/control quotas; quota not cost cap | C04 Worker + DO requests/duration separately |
| Cleanup / deletion delay | Deletion/ZDR not maximum charge tail | Shutdown transition/conflict/force not settled accrual proof | Stop synchronous meaning positive; failure/storage delete tail open | Destroy promise positive; failure/multi-product tail open |
| Retention / logs / observability | B04 full observability description; exhaustive log/retention price inclusion UNKNOWN | R09 logs readable; retention/inclusion UNKNOWN | V04 session metrics not all retention/log bill inclusion | C04 Workers Logs billed separately |
| Model / gateway / external services | No model/proxy service call admitted; B06 capability still spends upstream if enabled | R06 service gateway is not usage cap; optional no gateway exclusion | No model call admitted; optional AI Gateway unrelated to Sandbox ceiling | No AI service admitted; Worker credential handlers can incur upstream charges |
| Other / plan / metering increments | Tier/custom/beta differences; B04 rate freeze required | R04 Basic usage versus Pro monthly; trial not ceiling; minimums open | Hobby explicit no additional Sandbox usage charge; other products/plan not automatically zero | C04 $5/month Workers Paid; minimum/shared-plan allocation + Worker/DO/log increments open |

### Dated compute terms, not closed totals

| Provider | Positive documented term | Exact missing term / result |
| --- | --- | --- |
| Blaxel | B04: active memory $0.0000115/GB-second; snapshot $0.20/GB-month; image $0.045/GB-month; egress included. | `M_max*T_active_max*r + S_max*T_retained_max*r + extras/tails`; quantities and failure tail UNKNOWN. P6 NOT CLOSED. |
| Runloop | R04: CPU $0.00003/second, RAM $0.000007/GB-second, Devbox disk $0.0000000951/GB-second. | `V*T_cpu*r + M*T_ram*r + D*T_disk*r + optional builds/objects/tails`; fixed-clock and storage/fault tail, billing conflict UNKNOWN. P6 NOT CLOSED. |
| Vercel | V02 iad1 Pro CPU $0.128/hour; RAM $0.0212/GB-hour; creation $0.60/million; Hobby explicitly no additional Sandbox usage charges. | One nonpersistent/no-resume/no-drive session and Hobby-only charge scope could narrow cost; unsupported ancillary/fault/resource graph and no current account/controller binding. P6 NOT CLOSED; do not ignore explicit no-charge evidence. |
| Cloudflare | C04 CPU $0.000020/vCPU-second; RAM $0.0000025/GiB-second; disk $0.00000007/GB-second; additional products required. | `T*(V*r_cpu+M*r_ram+D*r_disk)+Worker+DO+egress+logs+retention+tails+plan`; total T and product terms UNKNOWN. P6 NOT CLOSED. |

A financial no-charge assurance can supply a component of P6 where its exact scope applies; it never substitutes for P5 containment. No USD/RM exposure is offered for an experiment, since all-in safety premises remain open. Historical RM5 ceiling is not reused as fresh provider creation authority. Storage bounded size alone cannot bound an unknown retention duration. Measuring charges or cancellation once cannot supply its own safety envelope.

## 3. P7 - eleven distinct states

Documented interfaces below are not actual events in this run. D = documented state/interface at limited scope; P = partial/not comprehensive; U = insufficiently documented. All measured results remain NOT RUN/UNKNOWN. Compound cells explicitly preserve downstream gaps.

| P7 state | Blaxel | Runloop | Vercel | Cloudflare |
| --- | --- | --- | --- | --- |
| CANCEL_REQUESTED | D B03 process kill / B12 delete | D R09 kill/shutdown | D V04 command kill/stop/delete | D C09 kill/signal/destroy |
| CANCEL_ACKNOWLEDGED | P response/operation return, not final tree | P response, shutdown conflict possible | D stop resolution has VM meaning; command ack differs | D awaited destroy, direct signal queues only |
| EXECUTION_STOPPING | D B01 DELETING/deactivating | P lifecycle transitions/status | D V04 stopping | P monitor/stop path, no identical native enum claimed |
| EXECUTION_CEASED | P process completed/exit; VM end separate | P execution terminal/exit; full unit separate | D final command/session VM stop scope | D C09 exitCode; whole instance stop separate |
| DESCENDANTS_CEASED | U process kill does not prove complete tree | P R09 process-group option, not escaped tree proof | P VM fully stopped supports local descendants, failure tail unproven | P C01 instance stop ends commands; C09 process kill excludes descendants |
| SANDBOX_TERMINATED | D B01 TERMINATED at expiry; B12 deletion intent | D R09 shutdown permanently stops Devbox | D V04 stopped VM; named object may survive | D C09 destroyed instance; DO identity may survive |
| PERSISTENT_RESOURCE_STATE_KNOWN | P B08 volume references separate | P R08/R09 disk/snapshot IDs separate | P V04 snapshot metadata; drives separately | P C03/C09 snapshots and DO/R2 state separately |
| RESOURCE_RELEASED | U complete resource release after faults not proved | P permanent stop/no active compute; disk/all extras cutoff gap | P stopped VM; deletion of persistent objects distinct | P container destroyed; Worker/DO/storage separate |
| BILLING_CEASED | P standby compute zero; B09 delayed bills; tail unknown | P suspended phases/pricing conflict; storage continues | P stop metrics/free-Hobby evidence not all billed objects settlement | P C04 instance sleep cutoff; other products/tail open |
| RESULT_OBSERVED | D B03 status/exit/log interfaces | D R07/R09 execution/output/query | D V04 exit/session output/metrics | D C09 exec/output/monitor; C08 retained stop example |
| EFFECTS_RECONCILED | U generic effect finality; Nexus specific receipt needed | U exact task effects + late charge reconciliation needed | U exact task effects + retention/bill reconciliation needed | U exact task effects + durable external storage/bill reconciliation needed |

P7 remains PARTIAL for each. None has a complete finite failure/cost envelope allowing a cancellation experiment today. Actual response loss may preserve UNKNOWN indefinitely with original references, reserved exposure and retry refusal; this is safe handling, not final reconciliation PASS. Local controller death/stream close does not prove remote cancellation or stop billing. No unit was created, queried or stopped.

## 4. Provider-specific findings and SDK compatibility

### Blaxel

The possible composition is explicit creation-age expiry plus a verified no-mutation actor graph and non-root/API isolation, rather than assuming default root confinement or standby is termination. Network proxy enforcement must be explicitly selected on the supported generation; empty allowlist is not deny-all. A process waiting timeout cannot be promoted to a unit hard deadline. Volumes, archived state and image objects require separate no-use or finite-retention proof. B02/B05/B10 are controls to investigate later, not newly accepted configuration.

### Runloop Credential Gateway

R06/R09 support provider-held raw secrets and exact-Devbox origin-bound opaque credentials. Gateway-call capability is still authority to invoke the configured upstream endpoint. Per-request method/path/model/amount attenuation, token expiry/revocation across shutdown/suspend/resume and inability to widen scope without control authority remain UNKNOWN. The token-mint API says it is not reissued on resume, which is not a universal expiry guarantee for every token. Direct account-secret env injection is a different, guest-visible mode, not gateway isolation. No gateway or secret was created, inspected or used. A minimal future synthetic no-network/no-model mode can omit gateways only after operation-graph closure. R02/R03 versus R04 suspending billing and R03 MEDIUM example discrepancy require conservative clarification, not cherry-picking the cheaper interpretation.

### Vercel

A persistent resumable object is documented as unbounded overall and cannot by itself supply P5 whole-unit maximum. This is not a provider-wide impossibility: an actor-excluded single nonpersistent session may be a different composition. Current provider JS SDK docs default to persistence and >=3.0 disk semantics; OpenAI pinned peer development dependency is older, so do not import current defaults into a historical client unchecked. Current `stop()` final-VM semantics and Hobby no-charge assertion are favorable; neither supplies fault-tail/persistence/all-channel qualification. Never let SDK fallback silently create a replacement unit while the original is UNKNOWN.

### Cloudflare

Current 1.0 is a native Worker/DO/Container boundary, not legacy `getSandbox` options. Native inactivity is timed from DO inactivity, not creation; streams, WebSockets, pending monitor and recurring alarms can sustain activity. Legacy keepAlive is expressly indefinite; migrating it to an alarm pattern does not create a total hard deadline. Native whole-instance destroy differs from direct-process kill. Separate Linux user IDs do not protect peers inside this root-capability guest. Worker credentials must remain outside the guest; service handlers still need bounded task authority. No supported universal total deadline or finite multi-product failure ceiling is established. No Worker/deployment/bridge implementation is authorized here.

### Official OpenAI Agents SDK, compatibility only

All four have official named Python and JS clients (O01-O03 and pinned source in the register). Common client create/resume and session lifecycle methods are application harness integration, not managed Agents API or a Nexus HostAdapter. Package metadata and source were read, never installed/imported. Methods differ by language/client; cancellation in a client is not provider cessation.

| Provider | Python 0.23.1 optional dependency | JS extensions 0.18.0 optional peer / development version | Inspected options / credential boundary / lifecycle caveat |
| --- | --- | --- | --- |
| Blaxel | blaxel>=0.2.50; aiohttp>=3.14.3,<4 | @blaxel/core optional peer ^0.2.82; dev 0.2.82 | Image/memory/region/TTL/env/name/ports/timeouts/pause-on-exit; BL_WORKSPACE/BL_API_KEY external controller. create-if-missing; resume fallback may recreate; pause retains state. Network/API-isolation controls not fully exposed by these options. |
| Runloop | runloop_api_client>=1.16.0,<2.0.0 | @runloop/api-client optional peer ^1.16.2; dev 1.32.0 | Blueprint/user/launch parameters/env/tunnels/gateways/MCP/managed secrets/metadata; external bearer. Reconnect/suspend-resume can reprovision on failure; SDK timeouts not hard lifetime. Optional secrets/MCP/tunnels not admitted. |
| Vercel | vercel-sandbox>=0.7.0,<0.8; cbor2>=5.9.0 | @vercel/sandbox optional peer ^1.9.3; dev 1.9.3 | Project/team/timeout/resources/runtime/env/ports/network/persistence/snapshot settings; external OIDC/access token. Resume reconnects or creates; S3 credential-exposure opt-in forbidden for candidate. Current provider >=3.0 behavior not proven for pinned older SDK. |
| Cloudflare | aiohttp>=3.14.3,<4; HTTP bridge | No @cloudflare/sandbox peer in extensions metadata; HTTP bridge | worker_url/api_key/exposed ports and request/exec timers; external CLOUDFLARE_SANDBOX_API_KEY for bridge, separate provider credentials. Create obtains service ID; resume uses existing state/running check. Existing bridge authentication, workload mapping and 1.0 compatibility not independently qualified. |

The pinned Python Blaxel session shutdown deletes unless pause-on-exit, and logs deletion exceptions; Runloop shutdown suspends or shuts down and catches exceptions. Returning from SDK shutdown is therefore not a universal successful cleanup receipt. Vercel session lifecycle stops its attached Sandbox; Cloudflare uses the HTTP bridge lifecycle. Common start/stop/shutdown methods must be inspected at their exact client scope; no local close or request timeout proves remote cutoff.

The native provider controls not exposed by a client cannot be assumed enabled. Any future fixed provider client composition needs separate scope authorization, dependency/byte/actor and actual configuration review; this run introduces no runtime/broker/trust boundary. SDK create/resume examples are not approved execution.

## 5. Exactly one decision per provider and minimum clarification

| Provider | Decision | Material basis / exact remaining safety barrier |
| --- | --- | --- |
| Blaxel | **B. PUBLIC EVIDENCE IS PROMISING BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | Creation-age expiry and narrower guest/network API boundaries are promising; hard allocation/fault destruction and retained/all-in charge envelope incomplete. |
| Runloop | **B. PUBLIC EVIDENCE IS PROMISING BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | Fixed lifetime API upper range and gateway/status interfaces are promising; fixed clock/paused/fault semantics, counted storage and billing conflict incomplete. |
| Vercel | **B. PUBLIC EVIDENCE IS PROMISING BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | Hard session ceiling, final stop record and explicit Hobby charge rule are promising; single-session authority/fault/persistence envelope and exact client generation incomplete. |
| Cloudflare | **B. PUBLIC EVIDENCE IS PROMISING BUT BOUNDED EXPERIMENT REMAINS BLOCKED** | Native VM/Worker separation, Internet-off and awaited destroy are promising; total/controller-loss lifetime and multi-product financial envelope incomplete. |

No A: no experiment design/executable/package/configuration authorization is produced. No D/E is asserted provider-wide from a documented incompatible optional mode. Minimum unsent clarification, not another generic questionnaire:

| Provider | Minimum P5 question | Minimum P6 question | P7 only where necessary | Exact evidence that would close readiness / outreach value |
| --- | --- | --- | --- | --- |
| Blaxel | For non-root/API-isolated Mark3 sandbox with fixed creation-age expiry, no update/clear/fork/archive/volume: confirm CPU/RAM/disk/output ceilings, guest exclusion and absolute shutdown including setup/standby/fault delay. | Confirm maximum billed setup/expiry-failure/deletion/storage retention, priced/included drivers/minimums and no residual objects for that mode. | Which external terminal/object/bill observations establish cutoff after lost response? Can share same fault/cutoff answer. | Versioned supported mode contract/API guarantee with finite maxima and observation semantics; conditional outreach worth doing, no permission to send. |
| Runloop | For fixed seconds only/no idle/suspend/resume/snapshots: identify clock start, <=48h parameter-limit enforcement, descendants/guest exclusion and maximum failed shutdown duration. | Resolve suspending-phase billing disagreement; supply exact Devbox disk release/storage/all other driver inclusion and bounded failed-create/termination charges. | Authoritative shutdown/result/usage evidence and residual cutoff, including snapshot conflict/force, if same answer does not already cover it. | Consistent API/lifecycle/billing contract with hard quantity/time/rate/inclusion bounds; conditional outreach worth doing. |
| Vercel | For one nonpersistent session/no resume/extensions/ports/drives: confirm hard session clock scope/controller-loss fault/tree bound and no automatic resurrection/storage. | Confirm exact Hobby no-additional-charge scope or paid all-in bounded failure/retention/network/ancillary rates, including server-side retries; SDK generation must match. | Confirm final stop/delete/usage retention and failure path versus successful stop barrier. | Versioned supported single-session contract + complete charge scope and fault bound; conditional outreach worth doing. |
| Cloudflare | For one native1.0 instance with no periodic keepalive/public calls/streams: is there a supported non-workload-relaxable total bound that survives Worker/controller/DO failure? If not, say so. | Supply finite Container/Worker/DO/image/storage/log/egress and cleanup-failure inclusion/cutoff for the proposed fixed graph. | Resolve whole-instance destroy failure/monitor/no-live and multi-product cutoff observations, not only direct-process exit. | Supported total-envelope primitive/guarantee plus bounded product charging; outreach useful only on that specific hard primitive, no Worker implementation to discover safety. |

The pool remains OpenAI, Daytona, Modal, E2B, Blaxel, Runloop, Vercel, Cloudflare without ranking or selection. OpenAI human escalation remains pending; the previous three B findings stay unchanged. No whole provider is factually excluded here. Exclude only the *configurations* that substitute Blaxel standby/wait timeout/default-root proxy, Runloop idle-only/mixed-policy timeout, Vercel indefinitely resumed persistent sessions, or Cloudflare legacy keepAlive/native activity-only timeout for a total bound. Other supported compositions may be reconsidered on exact authoritative evidence. Missing evidence does not permanently remove a provider.

Exact next task: owner review of this factual checkpoint, followed only by separately authorized targeted authoritative clarification of the above hard-envelope questions. No readiness/qualification/G2 acceptance or implementation follows. SAFE RESUME POINT ESTABLISHED.
