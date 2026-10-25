# WBS v0.1.0 — Part 10: Lifecycle & Oracle Credibility (M18–M19)

**BLUF:** M18 delivers the lifecycle features (incident intake, fix-validation, seams, attestation,
standalone verifier, evidence privacy, quickstart) plus the MCP/memory pack classes. M19 makes the oracles
themselves trustworthy (versioning, calibration corpus, judge drift, adjudication).

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M18 — Lifecycle — intake, fix-validation, seams, attestation, verifier, quickstart — ✅ COMPLETE (2026-10-23)

**Goal:** the features that keep the benchmark honest and fresh — a 7-day incident-intake SLA, fix-decay
detection, **seam** probing between controls, target **attestation**, a zero-install **verifier**,
**evidence privacy**, and a ≤15-minute **quickstart** — plus the MCP and memory/multi-agent pack classes.

**Status:** ✅ Complete · **Execution plan:** [m18-lifecycle-execution-plan](../../plans/m18-lifecycle-execution-plan.md) · **Issues:** #25–#38

**Requirements / PRDs:** [PRD 20](../../prd/20-efficacy-freshness-lifecycle.md), [PRD 21](../../prd/21-pack-catalog.md),
[PRD 05](../../prd/05-features.md) (R15, R16, R17, R34–R40), features F19, F20, F21, F60–F66.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 18.1 | Incident-intake pipeline (F60) | Watchlist → triage SLA (**assessed ≤7 days**: pack draft or explicit N/A + reason) → draft via template → review; deprecate stale packs | intake | new incident reaches pack-or-N/A in 7 days | #25 |
| 18.2 | Remediation validation (F61) | Every fixed miss becomes a **permanent pinned regression case**; `fix_decay` release-blocking with attribution | fix-cases | a decayed fix blocks the drift PR | #26 |
| 18.3 | Seam probing (F62) | Denied-then-retried + multi-enforcer composition cases; `seam_gap` names both controls | seam pack | a composition gap is named | #27 |
| 18.4 | Target attestation (F63) | `live`/`fixture`/`mock` per component; results labeled at the weakest link; `mock` never publishes | attestation | mock-attested result cannot publish | #28 |
| 18.5 | Standalone verifier (F64) | Zero-install, offline verification of bundles/releases: signatures, hashes, manifest, labels, statistical shape; three verdicts (`intact/complete/honest-shaped`) | verifier | a clean machine verifies offline | #29 |
| 18.6 | Evidence privacy (F65) | Redaction-before-bundling with **receipts** (class, count, location); verifier checks receipts | bundler | a bundle redacts + proves it | #30 |
| 18.7 | Quickstart + demo stack (F66) | `agentdrill quickstart` boots a bundled demo target; first honest result in minutes; watermarked `demo — never evidence` | CLI | ≤15 min to first result, mock-attested | #31 |
| 18.8 | MCP + memory pack classes (F19, F20) | Tool poisoning / rug-pull / shadowing / WhatsApp-class (via agentgate); memory poisoning / cross-task leakage / multi-agent abuse | packs | each class reproduces its pattern | #32 |
| 18.9 | Closes-the-loop policy suggestion (F21) | A confirmed miss emits an **advisory** rule + what-if replay (never auto-applied) | CLI | fix proposed as a reviewed PR | #33 |
| 18.T | Tests for this milestone | Intake SLA; fix-decay; seam gap; attestation weakest-link; verifier verdicts; redaction receipts; quickstart; pack classes; policy what-if | tests | all new paths covered; coverage ≥ 95% | #34 |
| 18.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #35 |
| 18.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #36 |
| 18.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #37 |
| 18.D | Design + reference docs | Lifecycle design, verifier reference, quickstart guide | docs | docs updated + linked here | #38 |

**Tests required:** intake assessment within SLA; fix-decay blocks; seam gap names both controls;
mock-attested result cannot publish; verifier returns three verdicts offline; redaction receipts verify;
quickstart ≤15 min; each new pack class reproduces its pattern; what-if replay proves a rule closes a miss.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] New incidents assessed ≤7 days; fixed misses become permanent regression cases (F60/F61)
- [x] `mock`-attested results never publish; verifier works offline (F63/F64)
- [x] Quickstart reaches a first honest result in ≤15 min, watermarked (F66)

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 20](../../prd/20-efficacy-freshness-lifecycle.md) · verifier reference ·
[PRD 21](../../prd/21-pack-catalog.md).

---

## Milestone M19 — Oracle credibility — ✅ COMPLETE (2026-10-23)

**Goal:** make the measuring instruments trustworthy — versioned oracles with behavior release notes, a
public calibration corpus with published agreement rates, judge-drift detection, a meta-eval CI battery,
human adjudication, and honesty labels (R53–R58).

**Status:** ✅ Complete · **Execution plan:** [m19-oracle-credibility-execution-plan](../../plans/m19-oracle-credibility-execution-plan.md) · **Issues:** #39–#50

**Requirements / PRDs:** [PRD 23](../../prd/23-oracle-credibility.md), [PRD 07](../../prd/07-success-metrics.md),
features F79–F84, requirements R53–R58.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 19.1 | Oracle versioning + release notes (F79) | Every oracle semver'd + pinned in the manifest; behavior-delta release notes; an oracle major invalidates comparability (re-baseline note) | versioning | comparison flags an oracle-version change | #39 |
| 19.2 | Calibration corpus (F80) | Published labeled corpus; per-release agreement / false-block / false-miss rates with CIs | corpus | rates published per release | #40 |
| 19.3 | Judge drift detection (F81) | Judge-vs-deterministic & judge-vs-human agreement tracked; seeded **canary** cases; a flip without a pin change ⇒ `judge_drift` (release-blocking); judge prompts hashed into the manifest | drift | drift caught by the canary | #41 |
| 19.4 | Oracle meta-eval CI (F82) | A calibration battery (known-answer blocked/missed/degraded/inert/seam) must verdict correctly before release | battery | a regression fails CI | #42 |
| 19.5 | Human adjudication layer (F83) | Every HITL verdict stored as labeled data (feeds corpus + future deterministic oracles); **human-adjudication coverage** published | store | coverage stat published | #43 |
| 19.6 | Oracle honesty labels (F84) | `calibrated`/`reviewed`/`experimental` per oracle on every result; `experimental` cannot gate CI | labels | experimental oracle cannot gate | #44 |
| 19.7 | Adjudication / dispute process (CUJ-13) | Public dispute process with a **14-day** resolution SLA; confirm / correct (flagged) / withdraw — all on the record | process | dispute resolved ≤14 days | #45 |
| 19.T | Tests for this milestone | Oracle-version change flagged; agreement rates computed; canary drift release-blocking; battery; adjudication store; label enforcement; dispute SLA | tests | all new paths covered; coverage ≥ 95% | #46 |
| 19.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #47 |
| 19.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #48 |
| 19.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #49 |
| 19.D | Design + reference docs | Oracle-credibility design, calibration corpus spec, adjudication policy | docs | docs updated + linked here | #50 |

**Tests required:** oracle-version change flagged (not a regression); canary flip without pin change is
release-blocking; battery green before release; experimental oracle cannot gate CI; adjudication store
feeds corpus; dispute resolves with an on-record outcome within SLA.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Oracles versioned + pinned; agreement rates published (F79/F80)
- [x] Judge drift caught by canary; `experimental` oracle cannot gate CI (F81/F84)
- [x] Dispute process resolves on the record within 14 days (CUJ-13)

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 23](../../prd/23-oracle-credibility.md) · calibration corpus spec ·
adjudication policy.

---

Part 10 green ⇒ the benchmark is fresh, verifiable, and its instruments are credible; proceed to
[Part 11 (M20–M21)](wbs-v0.1.0-part11-dx-absorption.md).
