# Nexus G2 Route D U04 Cost Bound Analysis v1

Version: `1.0.0` | Date: **2026-10-03**

Starting HEAD: `2fb939332c7c20dcbf2a528f296fa1d8a693cc5c` | Branch: `nexus-v2-g2-development`

Status: **DOCUMENTARY CHECKPOINT ONLY / NOT ACCEPTED / NO IMPLEMENTATION AUTHORITY**

Preserved: G2 HOLD; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Scenario 01-04 NOT RUN; Positive Host Binding ABSENT. UNKNOWN != PASS. No architecture selection/acceptance, P1-P12 change, D3, U05 measurement, installation, provisioning, Host execution, credentials, privilege elevation, paid activity, merge, push, tag or freeze.

## 1. Decision and six-dimensional scope

**U04-B - PLAUSIBLE BUT EXACT HOST/VENDOR CONTRACT OR ACCOUNT TERMS REQUIRED / NOT CLOSED.** A finite conservative profile can be expressed for existing infrastructure, but no applicable complete contract, actual resource inventory, enforceable horizon or numeric headroom is supplied. A fixed invoice period is not a finite lifetime. Owner intent to cancel later is not an autonomous cost boundary under loss. No vendor winner or purchase is recommended.

| Cost dimension | Scope in this closure | Required separation |
| --- | --- | --- |
| HOST_INFRASTRUCTURE_COST | Existing base compute/power/fence/hypervisor/control and cleanup exposure | Finite horizon, actor rights and supported outage/cancellation terms; independent of useful task completion |
| LLM_API_COST | No calls in contemplated first mechanics fixture | No zero-cost assertion for future model tasks; separate owner authority/profile |
| EXTERNAL_API_COST | No task API calls | Later call count/rate/cost cap and original effects separately accepted |
| EXTERNAL_SIDE_EFFECT_COST | No task external effects | Local cessation cannot cancel a previously accepted remote effect |
| STORAGE_COST | Host scratch/images/logs/control/evidence plus bounded retained copies | Capacity AND retention horizon, paid resources and cleanup tails |
| NETWORK_COST | Host control/evidence transport and possible infrastructure services; guest NO_NETWORK | Guest isolation does not erase base/IP/Host egress bills |

Source IDs resolve in the [closure register](nexus-g2-route-d-u01-u04-closure-v1.md#7-evidence-register-and-consistency). Cost expressions below are PROPOSAL, not account-specific prices or financial recommendations.

## 2. Four Host models

| Model | Base / billing period | Storage and network / IP | Snapshots, overage, fees | Deletion / renewal tail | Finite maximum before use? |
| --- | --- | --- | --- | --- | --- |
| C1 Fixed-price VPS / VM | Fixed stated period or monthly cap; idle/off may remain chargeable | Bundle storage quota; extra volumes/evidence, bandwidth/egress and IP may be separate | Backups/snapshots, auxiliary services, support/taxes/fees must be included or prohibited; alerts are not hard caps | Exact effective cancellation, retained resources and no automatic renewal/resize/recreation must be bound | CONDITIONAL: finite nonrenewable funded period plus all extras disabled/capped and supported tail; actual terms UNKNOWN. |
| C2 Fixed-price dedicated server | Fixed contract period; setup/minimum term/notice can affect total | Physical disks may be included; outside evidence/IP/network/fence can be separate | Product-specific traffic/overage, remote services/power/fence, replacement/fees/tax | Poweroff is not contract cancellation. Notice period, disks/backup retention and continued renewal need exact terms | CONDITIONAL: complete finite period and independently bounded renewal/cancellation/resource exposure; actual terms UNKNOWN. |
| C3 Owner-owned hardware | Existing sunk purchase is separate from incremental operation; time and shared base allocation defined | Fixed local allocation still uses electricity, UPS/power-fence/control/network and durable evidence destination | Electricity/network tariffs, hardware wear/maintenance contingency and external storage not assumed zero | No vendor compute delete needed, but power use/service retention and unattended reboot/restore need finite limits | CONDITIONAL: finite upper power draw/energy horizon and conservative applicable rates plus all auxiliary resource horizons; actual facts UNKNOWN. |
| C4 Metered IaaS | Rate per admitted machine/resource/time with billing granularity | Separate disk/storage/IP, egress, evidence/control logging by time/bytes/operations | Snapshot, autoscale, GPU, persistent auxiliaries, price changes/fees/tax must be capped or denied | VM stop/delete does not prove all resource billing ceased; control-plane outage tail essential | CONDITIONAL only with enforceable total resource counts/rates/time/bytes including failure tails or contractual all-in cap; missing factor remains unbounded for admission. |

FACT: N08 describes monthly server caps yet bills while the server exists even powered off; traffic beyond allowance remains billed, alerts do not cap charges, and snapshots/backups and IP resources can be separate. These published mechanics are a counterexample to 'fixed monthly price closes U04', not the owner's tariff. [Cloud billing FAQ](https://docs.hetzner.com/cloud/billing/faq/).

FACT: N09 distinguishes unlimited traffic for specified dedicated-server categories from capped/overage categories, including 10-Gbit uplinks. A provider name or 'dedicated' label is not an all-product bandwidth cap. [Product traffic rules](https://docs.hetzner.com/robot/general/traffic/).

FACT: N10 says most products continue until explicit cancellation, with product-dependent periods including immediate cancellation or 30 days to month-end. A monthly price maximum is not an automatic endpoint. [Cancellation overview](https://docs.hetzner.com/general/billing-and-account-management/cancellation/cancellations-overview/).

Taxes/fees and currency/rounding/price-change allowances remain applicable-term UNKNOWN; none are inferred from these examples. No contractual/legal conclusion about the owner's obligations is made.

## 3. Exact conservative profile condition

PROPOSAL: Before dispatch independently bind a finite exposure reservation to the original attempt/slot and the existing resource graph. No Controller/Agent/workload actor may increase resource count, horizon, tariff class or auxiliary services beyond that grant. A budget alert, expected short experiment, idle shutdown, or owner availability is not an enforcement mechanism.

For finite billing periods and already bounded resource lifetimes, define:

`E_host_max = base_periods_max * base_period_price_max + setup_fee_max + storage_max + network_max + address_max + fence_control_max + cleanup_retention_max + applicable_tax_fee_max + conservative_headroom`.

Every term must have a numeric supported upper bound, applicable units, rounding/minimum periods and evidence owner. Costs must not be double-counted when included in base. Metered terms have the form `resource_count_max * rate_max * billable_duration_max`, or `bytes/operations_max * rate_max`, with exact billing rounding and fixed fees. If any duration/rate/count/byte cap or renewal/tail is UNKNOWN, the expression does not prove a finite exposure. It is not valid to truncate ongoing contractual charges at an arbitrary planning horizon.

| Required profile fact | Necessary pre-dispatch condition | Current status |
| --- | --- | --- |
| Existing product / ownership | Applicable identified contract or owned-resource inventory; explicitly funded reservation | UNKNOWN; no existing Host/account terms supplied |
| Period / horizon | Fixed nonrenewable endpoint or enforceable capped tail even if Controller/Host/evidence fails | UNKNOWN; monthly billing is not enough |
| Compute graph | One attempt/unit with capped enclosing Host resources; no autoscale/GPU/pool/replacement | Documentary model only; actual policy UNKNOWN |
| Storage | Fixed allocation/inodes for image/scratch/control/log/evidence, no paid snapshot or new persistent volume | Actual allocation and all retained copies UNKNOWN |
| Network | Guest NO_NETWORK plus capped Host control/evidence traffic or applicable all-in non-metered bundle | Actual routes/channels/egress terms UNKNOWN |
| Auxiliary resources | IP, fence, backup, monitoring/log ingestion/control plane and detached retained objects included/capped or absent | UNKNOWN; do not assume zero |
| Renewal / cancellation | No runtime extension; original finite period, effective notice/termination, no unattended reactivation | Applicable terms and independent enforcement UNKNOWN |
| Tax / fees / rates | Conservative applicable maxima including currency/minimum billing and changes during authorized horizon | UNKNOWN; owner/contract evidence needed |
| Failure tail | Supported finite compute/residue/retention consequences and billing cessation/contract cap during failed cleanup | U02/U04 unresolved; deletion intent is insufficient |
| Headroom | Owner-authorized complete reservation covering worst-case already bounded expense | UNKNOWN; no amount approved here |

A prepaid allowance that keeps rebilling an attached payment method, a top-up/renewal rule, or a spending notification is not automatically a hard cap. A technically bounded namespace cannot cap a separately recurring Host contract. Conversely an all-in fixed service can conservatively absorb leftover local data ONLY when its finite nonrenewable contract horizon and included capacity/traffic/fence are supported; cleanup evidence still remains separate.

## 4. Network and storage residuals

Guest NO_NETWORK remains the contemplated prototype restriction, not an implemented mode. If effectively enforced across network namespaces, inherited descriptors, UNIX control sockets, metadata, proxy/Host broker, vsock and helper/TAP paths, it can remove guest-originated external traffic/effects. Host admission/status/evidence transfer and independent fence traffic still exist, and IP/base/network service or metered infrastructure charges can survive guest cutoff. Those channels require fixed byte/operation caps or an applicable included finite bundle. Metadata denial must not rely solely on absent public internet routes.

Storage simplifications remain PROPOSAL: bounded local workspace and inode allocation; no paid snapshots/backup creation; no paid persistent volumes outside an included fixed allocation; bounded evidence E/F. A VM root disk, image/backing file, provider boot disk, control journal and Host evidence may still be persistent even when no new guest 'persistent volume' is created. Guest output/log bytes can trigger Host storage/IO; guest disk cap does not cap host VMM logs, metadata, journal or transferred copies.

Cessation, mount/resource cleanup, external disk/IP/snapshot inventory, evidence retention expiry, resource release and billing cessation remain distinct. Native off/delete response is not a receipt for every separately billed resource. If U03 evidence must be retained after a missing result, its capacity AND maximum retention expense need an independent finite bound; permanent large-data retention is not an unstated exception. Original UNKNOWN/reservation metadata must remain conserved within a reviewed bounded governance record, not recreated by a retry.

Owner hardware must explicitly account for incremental electricity, network and storage/fence costs or define a supported all-in existing allocation and conservative upper bound. 'Already owned' establishes no numeric energy exposure. No runtime wattage, tariff, account or payment method was accessed.

## 5. Classification and evidence owners

U04-A cannot be assigned because no actual complete documented Host cost profile produces a numeric conservative maximum. U04-C universal unboundedness is too strong: finite fixed-term all-in or metered capped profiles are conceptually feasible. U04-B retains the exact contract/account-policy gap without authorizing account access.

Remaining documentary/owner evidence is: one existing product/owned-resource context; applicable finite nonrenewable horizon and exact inclusions/rates/fees; enforceable cost caps through declared faults and cleanup; separate resource inventories and retention; narrow actor/no-resize/no-snapshot/no-renew/recreate rules; cancellation/billing endpoint; funded worst-case headroom. Public terms alone cannot prove account configuration, and status alone cannot supply missing contract guarantees. Later safe validation is needed for effective limits/cleanup only after the safety gate and separate owner authority. No charge, cancellation or cost-control change occurred.
