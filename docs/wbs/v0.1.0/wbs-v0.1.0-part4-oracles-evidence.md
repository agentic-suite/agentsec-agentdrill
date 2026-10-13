# WBS v0.1.0 — Part 4: Oracles & Evidence (M6–M7)

**BLUF:** M6 builds the **oracle engine** (deterministic first, judge where needed, hybrid) with the three
dimensions and the honest outcome split. M7 wires **evidence** — reading the agentwatch security-event
schema, binding evidence to results, and validating expected telemetry.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M6 — Oracle engine — ✅ COMPLETE

**Goal:** score each case into `blocked` / `missed` / `degraded` via deterministic oracles first, an
optional LLM judge for qualitative cases, and hybrid gating — with the three dimensions and the failure
taxonomy (absorbed and re-pointed from the predecessor scoring engine).

**Status:** ✅ Complete (2026-10-12) · **Execution plan:** [m6-oracle-engine](../plans/m6-oracle-engine-execution-plan.md) · **Issues:** #285, #150–#160

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md) (oracles), [PRD 05](../../prd/05-features.md)
(R5), [PRD 07](../../prd/07-success-metrics.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 6.1 | Oracle base + registry | `Oracle` ABC + `@register_oracle` + entry-point discovery; `kind` deterministic\|judge\|hybrid; unknown metric → `ConfigError` | registry | unknown oracle fails at load | #285 |
| 6.2 | Deterministic oracles | deny/allowed, confinement, budget, sequence, grounding — read only the trajectory/evidence/config | scorers | deterministic verdicts reproducible | #150 |
| 6.3 | Judge oracles | Qualitative cases (refusal quality, explanation adequacy); judge client (OpenAI/Anthropic/Ollama/MLX/mock); `temperature=0`; verdict `{score, rationale}` | scorers | judge runs only where needed | #151 |
| 6.4 | Hybrid + offline safety | Deterministic gate always runs; missing judge → gate result + `judge_not_evaluated: true`; safety checks never silently skipped | engine | offline runs stay safe | #152 |
| 6.5 | Dimensions + outcome split | `compatibility` / `enforcement` / `integrity`; honest split `blocked`/`missed`/`degraded`; hierarchy enforcement > integrity > efficiency | engine | outcome split emitted per run | #153 |
| 6.6 | Divergence + failure taxonomy | Divergence `critical`/`warning`; failure taxonomy (`safety_miss`, `policy_miss`, `evidence_gap`, `kill_slow`, …) | engine | divergences classified; `--fail-on-divergence` | #154 |
| 6.7 | Defense contracts (R22/CUJ-15) | Each ecosystem enforcer ships a **required minimal pack** that gates its own release | contract packs | a contract regression blocks the enforcer's release | #155 |
| 6.T | Tests for this milestone | Deterministic/judge/hybrid verdicts; offline safety; outcome split; divergence; taxonomy; contract pack | tests | all new paths covered; coverage ≥ 95% | #156 |
| 6.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #157 |
| 6.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #158 |
| 6.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #159 |
| 6.D | Design + reference docs | Oracle design, metric catalog, failure taxonomy | docs | docs updated + linked here | #160 |

**Tests required:** each deterministic oracle; judge path with a mock; hybrid gate (judge skipped on clean
pass/fail); offline `judge_not_evaluated`; outcome split; divergence classification; failure taxonomy;
defense-contract pack runs.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Every case resolves to `blocked`/`missed`/`degraded` with dimensions
- [x] Offline runs never silently skip enforcement checks
- [x] Defense contracts run for the Wave-0 enforcers (CUJ-15)

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** oracle design · metric catalog · failure taxonomy · [PRD 02](../../prd/02-architecture.md).

---

## Milestone M7 — Evidence integration — ⬜ NOT STARTED

**Goal:** read the **agentwatch** record + security-event schema, bind evidence to every result, and
validate **expected telemetry** — a `blocked` verdict with no corresponding event is a `telemetry_gap`
finding (the observability of the defense, proven too).

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md), [PRD 11](../../prd/11-decisions.md)
(DD-05), feature F52, [PRD 24](../../prd/24-predecessor-gap-closure.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 7.1 | agentwatch schema reader | Read records/security events (`denied`, `policy-fired`, `secret-detected`, `revoked`, `halted`) in the agentwatch schema | reader | events parsed + typed | #161 |
| 7.2 | Evidence binding | Every result references the agentwatch evidence behind it; missing evidence → explicit `evidence_gap` finding | binder | no result without evidence (or an explicit gap) | #162 |
| 7.3 | Expected-telemetry validation (F52) | Cases declare the events a true block must produce; `blocked` without them → `telemetry_gap` finding | validator | blocked-without-telemetry is flagged | #163 |
| 7.4 | Evidence in artifacts | Evidence refs written into `artifacts/<case_id>.json`; machine-consumable per result | artifacts | a result reconstructs its evidence | #164 |
| 7.5 | Coverage reconciliation (F26) | Consume the agentwatch inventory; report exercised vs. unexercised surfaces; `gap:unexplained` = 0 | reconciler | coverage report generated | #165 |
| 7.T | Tests for this milestone | Reader parsing; binding; telemetry-gap detection; evidence-gap; coverage reconciliation | tests | all new paths covered; coverage ≥ 95% | #166 |
| 7.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #167 |
| 7.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #168 |
| 7.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #169 |
| 7.D | Design + reference docs | Evidence-integration design, expected-telemetry spec | docs | docs updated + linked here | #170 |

**Tests required:** schema reader against fixture events; evidence binding; `blocked` + no event →
`telemetry_gap`; missing evidence → `evidence_gap`; coverage reconciliation reaches `gap:unexplained = 0`.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Every result is evidence-bound (or explicitly `evidence_gap`)
- [ ] Expected-telemetry validation flags blocked-without-event (F52)
- [ ] Coverage reconciliation reports zero unexplained gaps

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** evidence-integration design · [PRD 02](../../prd/02-architecture.md) ·
[PRD 19](../../prd/19-detection-validation-bas.md).

---

Part 4 green ⇒ results are decided and evidence-bound; proceed to [Part 5 (M8–M9)](wbs-v0.1.0-part5-determinism-comparison.md).
