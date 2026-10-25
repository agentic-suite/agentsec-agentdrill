# Oracle Credibility — Design

**BLUF:** Make the measuring instruments trustworthy: versioned oracles with behavior release notes, a
public **calibration corpus** with published agreement / false-block / false-miss rates, **judge-drift**
detection via canaries, a **meta-eval battery** before release, a **human adjudication** layer, honesty
**labels** on every result and a public **dispute** process.

> **Status:** normative (M19). **Implementation:** `agentdrill/credibility/` — `versioning.py` (F79),
> `calibration.py` (F80), `drift.py` (F81), `battery.py` (F82), `adjudication_store.py` (F83),
> `labels.py` (F84), `dispute.py` (CUJ-13). Reference:
> [oracle-credibility](../reference/oracle-credibility.md). Spec:
> [PRD 23](../prd/23-oracle-credibility.md).

## Oracle versioning + release notes (19.1, F79)

Every oracle is semver'd (`OracleVersion`) and pinned in the manifest (`pin_versions`); behavior deltas
are released as notes. An **oracle major** change invalidates comparability (`major_changed`,
`rebaseline_note`).

## Calibration corpus (19.2, F80)

A published labeled corpus (`CalibrationCase`); `calibrate` computes per-release **agreement /
false-block / false-miss** rates with bootstrap CIs.

## Judge drift detection (19.3, F81)

Seeded **canary** cases track agreement. A canary flip **without a pin change** is `judge_drift` —
release-blocking (`require_no_drift`). Judge prompts are hashed into the manifest (`hash_prompt`).

## Meta-eval battery (19.4, F82)

`DEFAULT_BATTERY` of known-answer cases (blocked / missed / degraded / inert / seam) must verdict
correctly before release (`run_battery` / `require_battery_green`).

## Human adjudication + labels (19.5/19.6, F83/F84)

`AdjudicationStore` records HITL verdicts as labeled data (feeding the corpus); `adjudication_coverage`
publishes the coverage stat. Every oracle carries an honesty label (`calibrated` / `reviewed` /
`experimental`); an `experimental` oracle **cannot gate CI**.

## Dispute process (19.7, CUJ-13)

A public dispute resolves within a **14-day** SLA as confirm / correct / withdraw — on the record.
