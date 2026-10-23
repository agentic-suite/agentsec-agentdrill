# WBS v0.1.0 — Part 7: Kill-Chain & Efficacy (M12–M13)

**BLUF:** M12 verifies the **whole kill chain** (detected → … → *ceased*, probed not inferred) with p50/p95
timing. M13 proves the **attack is even possible** (unguarded control group), measures the **utility cost**
of a block, and enforces per-case **cleanup**.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M12 — Kill-time & kill-chain verification — ✅ COMPLETE (2026-10-23)

**Goal:** measure the full kill chain — attack_start → delivered → detected → decided → halted → revoked →
**ceased** — with a cessation **probe** (not an event receipt), per-stage p50/p95/max over repeated trials,
published as a timeline with typed findings (R8, R23).

**Status:** ✅ Complete · **Execution plan:** [m12-killchain-execution-plan](../../plans/m12-killchain-execution-plan.md) · **Issues:** #219–#229

**Requirements / PRDs:** [PRD 18](../../prd/18-kill-chain-verification.md), [PRD 05](../../prd/05-features.md)
(R8, R23), features F37, F78.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 12.1 | Stage model + timestamps | Shared stage model; each case records per-stage timestamps; a missing stage is `null` **+ flagged**, never inferred | model | timeline reconstructs per case | #219 |
| 12.2 | Cessation probe | Drive agenthalt/agentkeys revoke; verify cessation by **re-attempting the guarded action** post-revoke; success = not ceased | probe | `ceased` is measured, not believed | #220 |
| 12.3 | Repeated trials → percentiles | ≥5 trials per kill-time case; p50/p95/max per stage and total (means never alone) | timing | percentiles reported | #221 |
| 12.4 | Kill-chain timeline + findings | Emit the timeline; findings `kill_slow`, `detect_gap`, `decision_gap`, `halt_gap`, **`cease_gap`** (dashboard-green/damage-continues) | artifact | a stage bottleneck is named | #222 |
| 12.5 | Kill-time budgets in policy (F78) | Per-case `max_seconds` published **inside policyweave output** alongside the rule; budget versioned + drilled | policy | budget change lands in the same PR as the rule | #223 |
| 12.6 | Evidence for the probe | The re-attempt recorded in the evidence bundle (what, when, result) | evidence | probe is auditable | #224 |
| 12.T | Tests for this milestone | Stage reconstruction; probe (still-acting → not ceased); percentiles; findings; budget versioning | tests | all new paths covered; coverage ≥ 95% | #225 |
| 12.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #226 |
| 12.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #227 |
| 12.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #228 |
| 12.D | Design + reference docs | Kill-chain design, stage model, timing policy | docs | docs updated + linked here | #229 |

**Tests required:** stage timestamps reconstruct; a revoked-but-still-acting target yields
`cease_gap`/not-ceased; p50/p95 computed; each finding type triggers; budget appears in the policy diff.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] `ceased` is probe-verified; per-stage percentiles published (R8)
- [x] `cease_gap` (revoked but still acting) is a first-class finding
- [x] Kill-time budgets versioned in policyweave output (F78)

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** kill-chain design · [PRD 18](../../prd/18-kill-chain-verification.md).

---

## Milestone M13 — Efficacy control & utility-under-attack — ⬜ NOT STARTED

**Goal:** the control group that makes the benchmark scientific — every case runs against an **unguarded
twin**; only efficacy-verified cases count (inert attacks flagged `attack_inert`, excluded from rates).
Plus the **utility cost** of a block (benign twin) and per-case **cleanup** (`dirty_target` is
release-blocking).

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 20](../../prd/20-efficacy-freshness-lifecycle.md), [PRD 19](../../prd/19-detection-validation-bas.md),
features F50, F51, F59, requirements R26, R27, R33.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 13.1 | Efficacy run (F59) | Run each case against an **unguarded twin** target; a case is efficacy-verified only if it **succeeds** unguarded | efficacy runner | every enforced case has an unguarded success behind it | #230 |
| 13.2 | Inert flagging | Unguarded failure ⇒ `attack_inert`; excluded from enforcement rates; **never pads a green table** | flag | inert case cannot be counted as coverage | #231 |
| 13.3 | Utility-under-attack (F51) | Every attack case carries a **benign twin**; publish benign utility + utility-under-attack + enforcement rate; `utility_cost` finding | report | a `blocked` number carries its utility price tag | #232 |
| 13.4 | Per-case cleanup (F50) | Every case declares cleanup; runs after every case (incl. failed/timeout); cleanup failure ⇒ release-blocking `dirty_target` | cleanup | a dirty target blocks release | #233 |
| 13.5 | Efficacy report artifact | Efficacy status per case shipped in the evidence bundle (CUJ-11) | artifact | efficacy visible per case | #234 |
| 13.T | Tests for this milestone | Efficacy control; inert exclusion; utility cost; cleanup + dirty_target; report | tests | all new paths covered; coverage ≥ 95% | #235 |
| 13.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #236 |
| 13.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #237 |
| 13.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #238 |
| 13.D | Design + reference docs | Efficacy design, twin harness, cleanup spec | docs | docs updated + linked here | #239 |

**Tests required:** efficacy run flags inert cases; enforced cases require unguarded success; benign twin
produces utility-under-attack; a blocked-without-utility number fails publish; failing cleanup ⇒
`dirty_target` release-block.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Every published enforcement rate is efficacy-backed; inert attacks excluded (F59)
- [ ] Utility cost published with every block (F51); no "100% blocked" without its price tag
- [ ] Cleanup failure blocks release (`dirty_target`, F50)

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** efficacy design · twin harness · [PRD 20](../../prd/20-efficacy-freshness-lifecycle.md) ·
[PRD 19](../../prd/19-detection-validation-bas.md).

---

Part 7 green ⇒ the benchmark is efficacy-backed and the kill chain is measured; proceed to
[Part 8 (M14–M15)](wbs-v0.1.0-part8-evasion-chains.md).
