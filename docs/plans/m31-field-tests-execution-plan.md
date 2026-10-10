# agentdrill M31 — Field Tests Execution Plan

**Spec:** [WBS M31](../wbs/v0.1.0/wbs-v0.1.0-part17-fieldtest-release.md) · [field-test plan](../field-test/v0.1.0/field-test-plan.md).

## Constraints
Exit gate + gates. **The second-to-last milestone** (release readiness M32 is last). The report states honestly what was **not** tested.

## Tasks
- **T1 — Field-test harness (31.1):** drives the bundled demo stack + a real deployed stack (Wave-0 enforcers) in an ephemeral/purple environment under a signed RoE (M28).
- **T2 — Execute core scenarios (31.2):** every CUJ-1..CUJ-27 end to end (run/gate/reproduce/kill-time/evasion/intake/fix/seam/verifier/quickstart/…).
- **T3 — Execute addition scenarios (31.3):** every CUJ-28..CUJ-63 (pressure/`Hold@k`, effect witness, lab, bypass search, BYOD/head-to-head, backtest/shadow, attack-path, incident compiler, ledger/waivers, attestations, RoE/abort, detonation, break-it, frontier classes, explorer, platform matrix, standards/claims).
- **T4 — Evidence + report (31.4):** publish `FIELD_TEST_REPORT.md` with a not-tested list. *RED:* report generated from run evidence. *GREEN.*
- **T5 — Fix defects + regressions (31.5):** one regression test per defect.
- **T6 — Field-test CI job (31.6):** nightly (or explicitly marked not-planned with reason).
- **T7 — Gates + docs (31.T/.C/.L/.CR/.D).**

**Exit:** all field scenarios pass; report published with the not-tested list; defects fixed with regression evidence; **CUJ-1..CUJ-63 exercised**; a witness-confirmed `missed`/`witness_discrepancy` and the RoE abort demonstrated. **Closure:** standard.
