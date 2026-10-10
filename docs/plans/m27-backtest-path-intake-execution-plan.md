# agentdrill M27 — Backtest, Attack-Path & Incident Intake Execution Plan

**Spec:** [WBS M27](../wbs/v0.1.0/wbs-v0.1.0-part15-context-governance.md) · [design](../design/backtest-path-intake.md) · [PRD 30](../prd/30-trace-backtest-and-shadow.md), [PRD 31](../prd/31-attack-path-and-blast-radius.md), [PRD 32](../prd/32-incident-to-pack-compiler.md).

## Constraints
Privacy first (redaction receipts, local-first). Shadow is side-effect-free. Intake content is untrusted → runs in the lab. Reachability ≠ exploitability.

## Tasks
- **T1 — Backtest (27.1):** replay redacted sessions vs. candidate policy; clusters/regressions/un-replayable itemized. *RED:* replay fidelity ≥99%. *GREEN.*
- **T2 — Shadow + FP budget (27.2):** log-only divergence; false-block budget gate with CI.
- **T3 — Trace→drill (27.3):** redacted case + mined benign twins (HITL); zero unredacted secrets.
- **T4 — Capability graph (27.4–27.5):** nodes/edges from inventory; structural findings (trifecta, over-scope, egress, auto-approve+shell, writable instructions, shared memory, identity inheritance); path status; new-path alerts.
- **T5 — Incident compiler (27.6):** dedup feeds → relevance → cite-or-drop brief → draft pack (lab generators, twin, cleanup, witness effects, preregistered outcome) → efficacy → dual-use screen → HITL → registry.
- **T6 — Gates + docs (27.T/.C/.L/.CR/.D).**

**Exit:** ≥95% critical paths `proven_broken`; zero unexplained `unproven` >14 d; intake ≤48 h for ≥80%; 100% facts cited. **Closure:** standard.
