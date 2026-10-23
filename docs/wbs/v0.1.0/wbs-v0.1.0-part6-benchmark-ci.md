# WBS v0.1.0 — Part 6: Benchmark & CI (M10–M11)

**BLUF:** M10 publishes the **honest benchmark** (JSON/Markdown/HTML/PDF, heat-map, traces-per-row,
multi-seed statistics). M11 enforces it as the **CI gate** (exit codes, dimension/divergence gating) and
adds the **trigger/CART + local-loop** surfaces.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M10 — Honest reporter & public benchmark — ✅ COMPLETE (2026-10-23)

**Goal:** the reporter (machine + human + exec-shareable) and the public per-release benchmark — every
number efficacy-backed, multi-seed, CI'd, and trace-linked; misses first-class.

**Status:** ✅ Complete · **Execution plan:** [m10-benchmark-execution-plan](../../plans/m10-benchmark-execution-plan.md) · **Issues:** #193–#206

**Requirements / PRDs:** [PRD 07](../../prd/07-success-metrics.md), [PRD 19](../../prd/19-detection-validation-bas.md),
[PRD 05](../../prd/05-features.md) (R4, R5, R19, R25), features F8, F16, F23, F29, F41, F53, F55, F56, F57, F58.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 10.1 | Multi-format reporter | JSON (machine) / Markdown (PR) / GitHub-Actions / self-contained HTML (offline) / PDF (Caldera pattern) | reporter | all formats render one run | #193 |
| 10.2 | Honest report | Outcome split `blocked`/`missed`/`degraded`; a run **cannot publish without its misses** (R5) | report | misses always present | #194 |
| 10.3 | Statistical rigor (F29) | Every published number is mean ± std over **≥3 pinned seeds**; a single-run number fails the publish check | stats | bare single-run numbers rejected | #195 |
| 10.4 | Bootstrap CIs (F55) | Bootstrap confidence intervals on outcome rates (`blocked 87% [81%, 92%] (n, seeds)`) | stats | bare percentages rejected | #196 |
| 10.5 | Severity rubric (F41) | Findings scored attack-class × exposure with rationale; sortable across packs | rubric | severity + rationale emitted | #197 |
| 10.6 | Coverage heat-map (F53) | pack/tag × control matrix (`blocked/partial/missed/untested`) per release + delta | heat-map | generated in CI each release | #198 |
| 10.7 | Traces per row (F56) | Every benchmark cell links full trajectory + evidence in one hop | links | cell → trajectory works | #199 |
| 10.8 | Trend store (F23) | Per-defense-class deltas across releases; "what got worse" query | store | trend query answers in one call | #200 |
| 10.9 | Benchmark publisher + PR submission (F57) | Publish the honest table; `agentdrill benchmark export` for fork→run→PR submissions (R4) | publisher | a third party re-runs and matches numbers | #201 |
| 10.T | Tests for this milestone | Reporter formats; misses-mandatory; single-run rejection; CI width; heat-map; trace links; trend; reproduction | tests | all new paths covered; coverage ≥ 95% | #202 |
| 10.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #203 |
| 10.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #204 |
| 10.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #205 |
| 10.D | Design + reference docs | Reporting spec, benchmark schema, statistics policy | docs | docs updated + linked here | #206 |

**Tests required:** each format renders; a run without misses fails publish; single-seed number rejected;
bootstrap CI computed; heat-map + delta; trace link resolves; trend query; benchmark reproduction (CUJ-3).

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Published benchmark includes misses (R5); third party reproduces numbers (R4)
- [x] Every number multi-seed + CI'd; single-run and bare-percentage outputs rejected (F29/F55)
- [x] Heat-map + trend + trace links generated per release

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** reporting spec · benchmark schema · [PRD 07](../../prd/07-success-metrics.md) ·
[PRD 19](../../prd/19-detection-validation-bas.md).

---

## Milestone M11 — CI gate, trigger/CART & local loop — ⬜ NOT STARTED

**Goal:** enforce the drill in CI (structured exit codes; a policy change that un-blocks an attack is
rejected, R3) and provide the change-driven surfaces — trigger watcher, local watch, diff-aware re-runs,
PR annotations, scheduled drills.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 05](../../prd/05-features.md) (R3), [PRD 22](../../prd/22-frontier-dx-features.md),
features F22, F47, F68, F71, F76.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 11.1 | Exit codes + `--ci` | Structured codes (0 pass · 1 miss · 2 config · 3 oracle/judge infra · 4 critical miss · 5 divergence); propagated with or without `--ci` | CLI | a must-block miss exits non-zero | #207 |
| 11.2 | Dimension + divergence gating | `--fail-on compatibility\|enforcement\|integrity`; `--fail-on-divergence critical` | CLI | each dimension gates independently | #286 |
| 11.3 | CI output | GitHub Actions / GitLab output + `$GITHUB_STEP_SUMMARY` | CI | gate visible in the PR | #208 |
| 11.4 | Trigger watcher (CART, F22) | Subscribe to config/policy/model/harness-change events; re-run the affected packs (drift alerts are triggers) | watcher | a change re-runs only the affected set | #209 |
| 11.5 | Local watch mode (F68) | `agentdrill watch` — re-run affected packs on file change (dev loop) | CLI | affected re-runs within 1 save | #210 |
| 11.6 | Diff-aware re-runs (F76) | Compute affected cases from the changed surface; CI time scales with diff size | selection | changed-surface set == bound set | #211 |
| 11.7 | PR annotations + alerts (F47) | Annotate the PR with case/stage/evidence/attribution; Slack/webhook on release-gate failure | notifier | regression annotates the right file | #212 |
| 11.8 | Scheduled drills (F71) | `agentdrill schedule` — cadence runs for out-of-PR drift (vendor model, MCP rug-pull, marketplace skill) | scheduler | scheduled finding files with trigger label | #213 |
| 11.T | Tests for this milestone | Exit codes; dimension/divergence gating; trigger selection; watch; diff-aware selection; annotations; schedule | tests | all new paths covered; coverage ≥ 95% | #214 |
| 11.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #215 |
| 11.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #216 |
| 11.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #217 |
| 11.D | Design + reference docs | CI integration guide, trigger design, DX spec | docs | docs updated + linked here | #218 |

**Tests required:** each exit code; `--fail-on` per dimension; divergence gate; trigger re-runs only
affected packs; watch re-runs affected; diff-aware set == bound set; annotation content; scheduled run.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] CI rejects a policy change that un-blocks an attack (R3)
- [ ] Trigger + watch + diff-aware re-run only the affected set
- [ ] PR annotations name case/stage/evidence/attribution (F47)

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed + pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** CI integration guide · trigger design · [PRD 22](../../prd/22-frontier-dx-features.md).

---

Part 6 green ⇒ the drill gates CI and follows change; proceed to [Part 7 (M12–M13)](wbs-v0.1.0-part7-killchain-efficacy.md).
