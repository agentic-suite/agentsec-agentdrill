# agentdrill M23 — Field Tests Execution Plan

**Spec:** [WBS M23](../wbs/v0.1.0/wbs-v0.1.0-part12-hardening-fieldtest.md#milestone-m23--field-tests) · [field-test plan](../field-test/v0.1.0/field-test-plan.md).

## Constraints
Exit gate + gates. **ALWAYS the second-to-last milestone.** The report states honestly what was **not** tested.

## Tasks
- **T1 — Field-test harness (23.1):** drives the bundled demo stack + a real deployed stack (Wave-0 enforcers).
- **T2 — Execute field scenarios (23.2):** every CUJ-1..27 end to end (run/gate/reproduce/kill-time/evasion/intake/fix/seam/verifier/quickstart/…).
- **T3 — Evidence + report (23.3):** publish `FIELD_TEST_REPORT.md` with a not-tested list. *RED:* report generated from run evidence. *GREEN.*
- **T4 — Fix defects + regressions (23.4):** one regression test per defect.
- **T5 — Field-test CI job (23.5):** nightly (or explicitly marked not-planned with reason).
- **T6 — Gates + docs (23.T/.C/.L/.CR/.D).**

**Exit:** all field scenarios pass; report published with the not-tested list; defects fixed with regression evidence; CUJ-1..27 exercised. **Closure:** standard.
