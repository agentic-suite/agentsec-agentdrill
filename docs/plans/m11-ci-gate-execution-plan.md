# agentdrill M11 — CI Gate, Trigger/CART & Local Loop Execution Plan

**Spec:** [WBS M11](../wbs/v0.1.0/wbs-v0.1.0-part6-benchmark-ci.md#milestone-m11--ci-gate-triggercart--local-loop) ·
[design/ci-gate](../design/ci-gate.md) · [PRD 22](../prd/22-frontier-dx-features.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **A policy PR that un-blocks an attack is rejected** (R3).

## Tasks
- **T1 — Exit codes + `--ci` (11.1):** 0/1/2/3/4/5; propagated with or without `--ci`. *RED:* a must-block miss exits non-zero. *GREEN.*
- **T2 — Dimension + divergence gating (11.2):** `--fail-on compatibility|enforcement|integrity`; `--fail-on-divergence critical`.
- **T3 — CI output (11.3):** GitHub Actions / GitLab + `$GITHUB_STEP_SUMMARY`.
- **T4 — Trigger watcher / CART (11.4, F22):** config/policy/model/harness change ⇒ rerun affected packs.
- **T5 — Local watch (11.5, F68):** `agentdrill watch` re-runs affected packs on save.
- **T6 — Diff-aware re-runs (11.6, F76):** affected cases from the changed surface; CI time scales with diff size.
- **T7 — PR annotations + alerts (11.7, F47):** case/stage/evidence/attribution; Slack/webhook on gate failure.
- **T8 — Scheduled drills (11.8, F71):** cadence for out-of-PR drift.
- **T9 — Tests + docs (11.T, 11.D).**

**Exit:** CI rejects an un-blocking change; trigger/watch/diff-aware run only the affected set; annotations name the cause. **Closure:** standard.
