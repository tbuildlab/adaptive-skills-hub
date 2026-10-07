# Nexus Route D SD05 v2 E10 Reconciliation v1

Document ID: nexus.route-d.sd05-v2-e10-reconciliation.v1
Version: 1.0.0 | Owner acceptance date: 6 October 2026 (Asia/Kuala_Lumpur)
Status: ACCEPTED NARROW DOCUMENTARY APPLICABILITY ONLY. NO EXECUTABLE GRANT.

## 1. Original rule and precise conflict

Accepted engineering E10 closes admission on revocation, expiry, attendance loss,
observer loss, contradiction or drift, preserving original/reservations/UNKNOWN
and allowing only already-authorized original stop/reconciliation/cleanup.
EO-AUTONOMY-01 retains E10. See the original
[engineering decision](nexus-route-d-engineering-only-governance-applicability-decision-v1.md)
and its [acceptance](nexus-route-d-engineering-only-governance-acceptance-v1.md),
and the [autonomy acceptance](nexus-route-d-autonomous-lab-governance-acceptance-v1.md).

A committed but not physically submitted marker was not automatically a permitted
stop action. Owner section 3 now explicitly permits this original one-shot residue
ONLY in VM_FREE / SYNTHETIC_MARKER_ONLY / LAB_ONLY /
ENGINEERING_ONLY_NON_QUALIFYING scope. This is an exact additional applicability
exception, not a claim that the earlier words always meant it.

## 2. Exact supplemental clause SD05-V2-E10-01

> Solely for the accepted Route D VM_FREE / SYNTHETIC_MARKER_ONLY / LAB_ONLY /
> ENGINEERING_ONLY_NON_QUALIFYING candidate, STOP closes new admission and new
> logical commitment in the protected original sequence. A closure/revocation/
> expiry transition ordered first forbids COMMIT_L and the eligible marker
> invocation. STOP does not retroactively erase COMMIT_L ordered first: at most
> that one already-committed fixed synthetic effect may be attempted, begin later,
> complete later or become AMBIGUOUS, under the independently issued original
> residual-completion scope and accepted N01-N16 constraints. A newly known
> custody/descriptor/capability/attendance/observer failure or contradiction before
> invocation abandons it; persistence failure/uncertainty also forbids invocation.
> There is no new grant, renewal, retry, replay, resume, replacement, recovery
> dispatch or second attempt. STOP acknowledgement identifies protected order
> and must not claim absence of a prior committed effect. Cessation, resource
> release, result, exposure and reconciliation remain separate evidence facts.
> Original slot/reservations and ambiguity remain conserved; cleanup requires its
> own valid authority and positive original safety evidence. No external-time
> cutoff, finite all-fault tail, actual Owner-presence proof, VM/provider effect,
> production eligibility or broader cancellation exception follows.

The supplemental clause is subordinate to the exact accepted
[N01-N16 normative text](nexus-route-d-sd05-v2-normative-text-v1.md) and
[amendment](nexus-route-d-sd05-v2-governance-amendment-v1.md). It cannot dispense
with independent issuance, custody, byte/object identity, sole consumer,
reservations or mandatory STOP on their uncertainty. The consumer remains
unqualified and unimplemented. A service, caller or model cannot issue authority.

## 3. State applicability table

| Evidence/order | Permissible outcome under a FUTURE separately issued grant | Forbidden inference/action |
| --- | --- | --- |
| Owner request exists but domain receipt/order unknown | Preserve uncertainty, close dependent admission; prior outcome remains separately observed | Treat click time as native cancellation or silently assume no revoke |
| CLOSE_L wins before COMMIT_L | No new commit or marker invocation | Post-stop fresh commit, second path or expiry backdating |
| COMMIT_L wins; exact persistence and custody still valid | One original fixed invocation at most; may be abandoned | Reusable permit, deferred caller queue, alternative consumer/descriptor |
| COMMIT_L wins; closure later | Record both and permit only original accepted residue, subject to N01-N16 | Claim earlier commit erased or all physical effects already ceased |
| Known custody/attendance/observer failure before invocation | Abandon invocation; conserve slot and reservations | Use completion exception to proceed through new decisive UNKNOWN |
| I/O issued, cancel/stop requested | Observe original result/cessation independently or retain AMBIGUOUS | Cancel request/ack => no effect, zero live or settled usage |
| Crash/persistence ambiguity/recovered commit record | No recovery dispatch; consumed/unavailable slot and retained original | Resume, replay, release reservation or replacement attempt |
| Clock/external expiry crossed before ordered expiry | Record the actual observations and gap; no claim of timely commit/effect | Equate earlier sample or file timestamp with commit time |
| Effect changes or numeric absolute ceiling remains unproved | Refuse new admission; v2 applicability does not transfer | Broaden to VM, provider, production, real attendance or unknown inner limits |

## 4. What remains unchanged

E01-E09, E11-E12 and every E10 rule outside this exact completion exception retain
their scope. EO-AUTONOMY-01 is not reopened for unattended/general execution.
All production A0-A6/P1-P12/HQ1-HQ6/Section 7 cancellation and recovery gates remain.
Actual U03 A-F, numeric U04, independent custody and per-effect grants remain
mandatory where applicable; no numeric value or setup/release is supplied.
All accepted source files, rejected old SD05 evidence, historical UNKNOWNs,
violations and counters remain unchanged.

No protected domain exists by virtue of this paragraph. Its sequence, durable
records and acknowledgements require actual supported independent enforcement
and observation under separately accepted exact setup/test/release authority.
