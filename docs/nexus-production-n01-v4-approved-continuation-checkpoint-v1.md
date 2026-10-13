# N01 exact v4 approved continuation checkpoint

The Owner explicitly approved the immutable canonical v4 review package
01301b7b9652b2d54bb85402b484b9a0f519a5de311b53879e86e803ee9f315e.
Its original pending bytes remain NOT_OBTAINED. Separate acceptance
c01f6c6e8a5e08cd9b21ffc04746cbe485eff96b9ed4022e3a84018acc842fb0
records this approval without transferring any historical approval.
The exclusive window is 2026-10-13 13:45:00 through 15:45:00 Asia/Kuala_Lumpur.
Application generation is 1 and review generation is 4. This is public-key
review only, not production admission or Owner authentication.

The finite v4 selector requires OWNER_ATOMIC_FORWARD_V1. Historical selectors,
review windows, fixtures and checkpoint 7/8 remain unchanged. The source-custody
builder now accepts this exact pair, fixes RECOVER 9's predecessor to head 8 and
epoch to 6, and writes a unique v4 receipt. Wrong generation, predecessor,
deployment or native SSO protection fails closed. It cannot replay old recovery,
restore an Owner session, issue a grant or dispatch a product action.

The final isolated source regression has 229 affected PASS, no skips or failures.
Full regression has 1488 tests: 1484 PASS, four pre-existing environment SKIP,
zero FAIL/ERROR. Three skips lack embedded distribution inputs; one requires
Windows symlink privilege. Historical-clock fixtures remain offline only.
Both current-review CONFIRM and DENY models retain 174 DynamoDB RPCs and all
deterministic gates. The no-reuse worst case remains 189 within 210 remaining
RPCs and 512 aggregate. The conservative model remains USD 0.8657442 within
the existing USD 1.00 authorization. No resource, trust deadline, retention,
cleanup schedule or authentication contract is enlarged.

R native STS identified the exact existing R/root identity. CLI readback verified
the existing Vercel project/team and all_except_custom_domains SSO protection.
Neither observation is source authority. At this offline checkpoint the new
R review custody, current artifact/process binding and Owner authentication
have not been executed. Later native observations require separate records.
The implementing review is not claimed as independent security certification.

D01 and D03 remain CLOSED. N01 and G3 remain INCOMPLETE. G4/G6 remain
COMPLETE_PREPARATION_FAIL_CLOSED. REAL_ADMISSION remains NO. Historical D04
executor exclusion is not a delegated-mode release gate.

Exact source, regressions and budgets are recorded in
[the offline evidence](../research/nexus-production-n01-v4-approved-offline-evidence-v1.json).
