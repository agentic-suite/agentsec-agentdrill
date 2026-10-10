# agentdrill M19 — Oracle Credibility Execution Plan

**Spec:** [WBS M19](../wbs/v0.1.0/wbs-v0.1.0-part10-lifecycle-oracle.md#milestone-m19--oracle-credibility) · [PRD 23](../prd/23-oracle-credibility.md).

## Constraints
Exit gate + gates. **Who evaluates the evaluators?** — oracles are versioned, calibrated, and drift-checked.

## Tasks
- **T1 — Oracle versioning + release notes (19.1, F79):** semver + pinned in manifest; behavior deltas; major ⇒ re-baseline note.
- **T2 — Calibration corpus (19.2, F80):** published labeled corpus; per-release agreement/false-block/false-miss with CIs.
- **T3 — Judge drift detection (19.3, F81):** canary cases; flip without a pin change ⇒ release-blocking `judge_drift`; prompts hashed in manifest. *RED:* canary-flip test. *GREEN.*
- **T4 — Oracle meta-eval CI battery (19.4, F82):** known-answer battery green before release.
- **T5 — Human adjudication layer (19.5, F83):** HITL verdicts stored as labeled data; coverage stat published.
- **T6 — Honesty labels (19.6, F84):** calibrated/reviewed/experimental; `experimental` cannot gate CI. *RED:* experimental-gate rejected. *GREEN.*
- **T7 — Adjudication / dispute process (19.7, CUJ-13):** 14-day SLA; confirm/correct/withdraw on the record.
- **T8 — Gates + docs (19.T/.C/.L/.CR/.D).**

**Exit:** oracles versioned; agreement rates published; drift caught; experimental can't gate; disputes ≤14 days. **Closure:** standard.
