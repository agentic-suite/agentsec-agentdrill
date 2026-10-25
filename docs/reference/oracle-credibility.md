# Oracle Credibility — Reference

**Status:** normative (M19). Implementation: `src/agentdrill/credibility/`. Design:
[oracle-credibility](../design/oracle-credibility.md). Spec: [PRD 23](../prd/23-oracle-credibility.md).

## Versioning (19.1, F79)

`OracleVersion(name, version, behavior_notes=)`; `pin_versions(oracles)` → manifest pins;
`version_changed(prev, cur)`; `major_changed(prev, cur)`; `rebaseline_note(name, prev, cur)` (a major
change invalidates comparability).

## Calibration (19.2, F80)

`CalibrationCase(case_id, expected, oracle_outcome)`; `calibrate(cases, release=, seed=)` →
`CalibrationReport` (agreement / false_block / false_miss as `RateCI`).

## Drift (19.3, F81)

`CanaryCase`; `detect_drift(canaries, previous_outcomes=, pin_changed=, judge_prompt_hash=)` →
`DriftReport` (`drift` = a flip without a pin change); `require_no_drift` raises `JudgeDriftError`
(release-blocking `judge_drift`); `hash_prompt(text)`.

## Battery (19.4, F82)

`DEFAULT_BATTERY` (blocked / missed / degraded / inert / seam); `run_battery(answers, verdict_of=)` →
`BatteryResult`; `require_battery_green(result)` raises `BatteryError`.

## Adjudication + labels (19.5/19.6, F83/F84)

`AdjudicationStore` + `HitlVerdict`; `adjudication_coverage(store, total=)`. `OracleLabel` +
`can_gate_ci` / `require_gate_capable` (an `experimental` oracle cannot gate CI) + `label_result`.

## Dispute (19.7, CUJ-13)

`Dispute` + `resolve_dispute(dispute, outcome=, note=, resolved_at=, days_elapsed=)` (14-day SLA —
`DISPUTE_SLA_DAYS`, `within_dispute_sla`, `DisputeError`) + `dispute_record`.
