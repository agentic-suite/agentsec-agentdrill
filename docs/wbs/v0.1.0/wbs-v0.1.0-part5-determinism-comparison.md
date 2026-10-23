# WBS v0.1.0 — Part 5: Determinism & Comparison (M8–M9)

**BLUF:** M8 makes runs **reproducible** (fixtures/ToolStub, run manifest, pins) with contamination checks.
M9 adds **golden expected results**, the comparison engine (adapter/model/oracle-change aware), and
**attribution** — so a blocked→missed flip names its cause.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M8 — Determinism — fixtures, manifest & pins — ✅ COMPLETE (2026-10-23)

**Goal:** the reproducibility harness — fixtures/ToolStub record-replay, `run-manifest.json` with pins,
and contamination checks — so *same environment ⇒ same result* (R6) and a third party can reproduce a run.

**Status:** ✅ Complete · **Execution plan:** [m8-determinism-execution-plan](../../plans/m8-determinism-execution-plan.md) · **Issues:** #171–#181

**Requirements / PRDs:** [PRD 13](../../prd/13-non-functional-requirements.md), [PRD 15](../../prd/15-data-model.md),
[PRD 05](../../prd/05-features.md) (R6).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 8.1 | Fixture system / ToolStub | Record + replay target/tool responses so two identical fixture runs score identically; `--live` (mutually exclusive) | fixtures | identical fixture runs ⇒ identical scores | #171 |
| 8.2 | Run manifest | Emit `run-manifest.json`: OS, arch, runtime+version, dependency tree, target/driver digests, pack hash, oracle versions, env **names** (never values); `--no-manifest` | manifest | manifest reproduces the environment | #172 |
| 8.3 | Pins | Pin seeds, models, pack hash, oracle versions; re-pin ⇒ re-publish rule wired | pins | a changed pin is declared | #173 |
| 8.4 | Contamination checks (F30) | Probe each case for overlap with judge/target-model training posture; contaminated cases **flagged**, never hidden | check | contaminated case appears flagged in the table | #174 |
| 8.5 | Reproducibility test | Rerun a pinned pack ⇒ identical result unless a pin changed (declared) | test | CI verifies reproduction | #175 |
| 8.6 | Deterministic methodology doc | Publish how each oracle decides `blocked`/`missed`/`degraded` | doc | methodology published (public) | #176 |
| 8.T | Tests for this milestone | Fixture determinism; manifest completeness; pin-change detection; contamination flag; reproduction | tests | all new paths covered; coverage ≥ 95% | #177 |
| 8.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #178 |
| 8.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #179 |
| 8.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #180 |
| 8.D | Design + reference docs | Determinism design, manifest spec, methodology | docs | docs updated + linked here | #181 |

**Tests required:** two identical fixture runs score identically; manifest round-trip + completeness;
undeclared pin change fails; contamination probe flags an overlapping case; reproduction test green.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Same environment ⇒ same result (R6); reproduction test green
- [x] Manifest complete; contaminated cases flagged (F30)

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** determinism design · manifest spec · [determinism methodology](../../reference/determinism-methodology.md) · [PRD 13](../../prd/13-non-functional-requirements.md).

---

## Milestone M9 — Golden results, comparison & attribution — ⬜ NOT STARTED

**Goal:** the comparison engine over **golden expected results** — per-case, per-tag, aggregate — that
distinguishes adapter/model/oracle changes from real defense regressions, and **attributes** a
blocked→missed flip to the config/pin diff that caused it (CUJ-14).

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md), [PRD 15](../../prd/15-data-model.md),
[PRD 05](../../prd/05-features.md) (R24), [PRD 23](../../prd/23-oracle-credibility.md) (F79).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 9.1 | Golden expected results | Preregistered, locked expected outcome per pack version; golden-lock rule (change ⇒ flagged + re-pin note) | goldens | a result-vs-golden change is flagged, never silent | #182 |
| 9.2 | Comparison engine | Per-case / per-tag / aggregate deltas between candidate and golden/baseline | engine | deltas correct | #183 |
| 9.3 | Change detection | Distinguish `adapter_changed` / `model_changed` / `oracle_changed` from a real regression; `--allow-adapter-change` | engine | a swap is not a regression | #184 |
| 9.4 | Attribution (F38, CUJ-14) | Correlate a blocked→missed flip with the target-config diff / pin change / adapter change that caused it; emit `attributed_to` + stage/mechanism + confidence | attribution | flip names its cause (or honest `unknown`) | #185 |
| 9.5 | Three-way outcome classification | `adapter_failed` / `agent_crashed` / `scenario_failed` (+ `blocked`/`missed`/`degraded`) in comparisons | engine | classification emitted | #186 |
| 9.6 | Golden/preregistration store | Goldens stored under `.agentdrill/goldens/` bound to `pack@version+hash` | storage | golden binds to pack | #187 |
| 9.T | Tests for this milestone | Golden-lock; comparison deltas; adapter/model/oracle-change detection; attribution (with bisect); outcome classification | tests | all new paths covered; coverage ≥ 95% | #188 |
| 9.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #189 |
| 9.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #190 |
| 9.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #191 |
| 9.D | Design + reference docs | Comparison design, attribution design, golden model | docs | docs updated + linked here | #192 |

**Tests required:** golden-lock flags an undeclared change; comparison deltas; adapter/model/oracle change
detected, not misread as regression; attribution correct (mechanism-backed) or `unknown`; classification.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Golden-lock rule enforced (flag, never silently fix)
- [ ] Adapter/model/oracle changes distinguished from regressions
- [ ] A blocked→missed flip is attributed with mechanism or honest `unknown` (CUJ-14)

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** comparison design · attribution design · [PRD 15](../../prd/15-data-model.md).

---

Part 5 green ⇒ results are reproducible and comparable; proceed to [Part 6 (M10–M11)](wbs-v0.1.0-part6-benchmark-ci.md).
