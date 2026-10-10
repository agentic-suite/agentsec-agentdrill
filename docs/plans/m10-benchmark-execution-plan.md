# agentdrill M10 — Honest Reporter & Public Benchmark Execution Plan

**Spec:** [WBS M10](../wbs/v0.1.0/wbs-v0.1.0-part6-benchmark-ci.md#milestone-m10--honest-reporter--public-benchmark) ·
[design/reporting](../design/reporting.md) · [PRD 07](../../prd/07-success-metrics.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **Misses mandatory; single-run numbers rejected** (DD-06, DD-27).

## Tasks
- **T1 — Multi-format reporter (10.1):** JSON / Markdown / GitHub-Actions / self-contained HTML / PDF.
- **T2 — Honest report (10.2, R5):** outcome split; a run **cannot publish without its misses**. *RED:* no-misses publish fails. *GREEN.*
- **T3 — Statistical rigor (10.3, F29):** mean ± std over ≥3 seeds; single-run number fails publish.
- **T4 — Bootstrap CIs (10.4, F55):** `blocked 87% [81%, 92%] (n, seeds)`; bare percentages rejected.
- **T5 — Severity rubric (10.5, F41):** attack-class × exposure + rationale.
- **T6 — Coverage heat-map (10.6, F53):** pack/tag × control matrix + delta, generated in CI.
- **T7 — Traces per row (10.7, F56):** every cell → trajectory + evidence in one hop.
- **T8 — Trend store (10.8, F23):** per-defense-class deltas across releases.
- **T9 — Publisher + PR submission (10.9, F57, R4):** `benchmark export`; a third party reproduces.
- **T10 — Tests + docs (10.T, 10.D).**

**Exit:** misses present; third party reproduces; multi-seed + CI'd; heat-map/trend/traces generated. **Closure:** standard.
