# WBS v0.1.0 — Part 12: Hardening & Field Tests (M22–M23)

**BLUF:** M22 hardens the non-functionals (performance, fail-closed fault handling, untrusted-pack
sandboxing, audit integrity, portability, cost). M23 runs the **field tests** against a real deployed
stack and publishes the report. These are the last two before release readiness.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M22 — NFRs, security hardening & resilience — ⬜ NOT STARTED

**Goal:** meet the non-functional requirements ([PRD 13](../../prd/13-non-functional-requirements.md)) and
harden the security baseline — performance budgets, fail-closed fault handling, OS-level sandboxing for
untrusted packs, tamper-evident audit, and portability.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 13](../../prd/13-non-functional-requirements.md), [PRD 06](../../prd/06-security-baseline.md),
[PRD 08](../../prd/08-risks.md) (RK-3, RK-8), [PRD 24](../../prd/24-predecessor-gap-closure.md) (G4, G5).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 22.1 | Performance & scale | Per-pack run budget; parallel + backpressure; oracle/judge cache with `cache stats` | perf | budget met; parallel == serial | #71 |
| 22.2 | Fault injection & fail-closed | Faults across runner/targets/oracles/drivers; **fail-closed on tamper**; a case failure never aborts the pack | fault suite | faults handled, never silently green | #72 |
| 22.3 | Untrusted-pack hardening | OS-level sandbox (Docker, `--network none`, read-only root, resource caps) **required** for `external` trust; audit **rotation + hash-chain integrity** (predecessor G4); secret sanitization | sandbox/audit | external pack isolated; audit tamper detected | #73 |
| 22.4 | Portability | Python 3.10+, macOS/Linux, **local-first** (no service required for core function) | portability | runs on both OSes | #74 |
| 22.5 | Cost controls | Run-level `--max-cost`; caching; reported savings | cost | over-budget aborts + reports | #75 |
| 22.6 | Self-observability | `doctor`, `validate`, audit log, shareable run summary (dimensions + outcome split + exit code) | tooling | one run summary answers "what happened" | #76 |
| 22.T | Tests for this milestone | Perf budget; fault injection; sandbox isolation; audit rotation/hash-chain; portability; cost; self-observability | tests | all new paths covered; coverage ≥ 95% | #77 |
| 22.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #78 |
| 22.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #79 |
| 22.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #80 |
| 22.D | Design + reference docs | NFR report, security-hardening notes, operations guide | docs | docs updated + linked here | #81 |

**Tests required:** perf budget; each injected fault (fail-closed); external-pack isolation (`--network
none`, read-only root, caps); audit tamper detected; portability smoke; cost abort; run summary complete.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] NFRs met ([PRD 13](../../prd/13-non-functional-requirements.md)); fault suite fail-closed
- [ ] External packs OS-isolated; audit tamper-evident (predecessor G4/G5 closed)
- [ ] Local-first on macOS + Linux

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 13](../../prd/13-non-functional-requirements.md) · [PRD 06](../../prd/06-security-baseline.md) ·
[PRD 24](../../prd/24-predecessor-gap-closure.md).

---

## Milestone M23 — Field tests — ⬜ NOT STARTED

**Goal:** run the field tests against a real deployed stack (and the bundled demo) and publish the report —
the last validation before release readiness.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 07](../../prd/07-success-metrics.md), [PRD 04](../../prd/04-users-and-cujs.md)
(CUJ-1..24), [PRD 21](../../prd/21-pack-catalog.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 23.1 | Field-test harness | Harness driving the bundled demo stack + a real deployed stack (the Wave-0 enforcers) | harness | runnable end to end | #82 |
| 23.2 | Execute field scenarios | Every CUJ end to end: run pack, gate PR, reproduce benchmark, drill incident, kill-time, evasion, intake→pack, fix-decay, seam, verifier, quickstart | results | all scenarios pass | #83 |
| 23.3 | Evidence + report | Collect evidence; publish `FIELD_TEST_REPORT.md` (what was tested, what was **not**, per-CUJ) | report | published; misses stated | #84 |
| 23.4 | Fix defects + regressions | Fix every defect found; add a regression test each | fixes | defects closed with evidence | #85 |
| 23.5 | Field-test CI job | Nightly field-test job | CI | scheduled + green (or explicitly marked not-planned) | #86 |
| 23.T | Tests for this milestone | Regression tests for every defect; CUJ journeys exercised end to end | tests | all new paths covered | #87 |
| 23.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #88 |
| 23.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #89 |
| 23.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #90 |
| 23.D | Design + reference docs | Field-test plan + report; known-limitations updated | docs | docs updated + linked here | #91 |

**Tests required:** all field scenarios; regression tests for each defect; every CUJ exercised end to end;
the verifier run offline on a clean machine.

**Exit criteria**

- [ ] All field-test scenarios pass; report published with **what was not tested** stated
- [ ] Defects fixed with regression evidence
- [ ] CUJ-1..24 exercised end to end
- [ ] Design docs updated · port/absorption tasks complete

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** field-test plan · [FIELD_TEST_REPORT](../../field-test/v0.1.0/FIELD_TEST_REPORT.md) ·
[PRD 07](../../prd/07-success-metrics.md).

---

Part 12 green ⇒ the build is hardened and field-tested; proceed to
[Part 13 (M24)](wbs-v0.1.0-part13-release.md) to tag `v0.1.0`.
