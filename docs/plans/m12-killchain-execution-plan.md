# agentdrill M12 — Kill-Time & Kill-Chain Verification Execution Plan

**Spec:** [WBS M12](../wbs/v0.1.0/wbs-v0.1.0-part7-killchain-efficacy.md#milestone-m12--kill-time--kill-chain-verification) ·
[design/killchain](../design/killchain.md) · [PRD 18](../../prd/18-kill-chain-verification.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **Detection is not safety; cessation is.** `ceased` is probed, never inferred.

## Tasks
- **T1 — Stage model + timestamps (12.1):** attack_start→delivered→detected→decided→halted→revoked→ceased; missing stage ⇒ null **+ flagged**.
- **T2 — Cessation probe (12.2):** drive agenthalt/agentkeys revoke; **re-attempt the guarded action**; success ⇒ not ceased. *RED:* revoked-but-acting test → `cease_gap`. *GREEN.*
- **T3 — Percentiles (12.3):** ≥5 trials; p50/p95/max per stage + total.
- **T4 — Timeline + findings (12.4):** `kill_slow`, `detect_gap`, `decision_gap`, `halt_gap`, **`cease_gap`**.
- **T5 — Budgets as policy (12.5, F78):** per-case `max_seconds` published in policyweave output.
- **T6 — Probe evidence (12.6):** the re-attempt recorded in the bundle.
- **T7 — Tests + docs (12.T, 12.D).**

**Exit:** `ceased` probe-verified; per-stage percentiles published; `cease_gap` first-class; budgets versioned. **Closure:** standard.
