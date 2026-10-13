# WBS v0.1.0 — Part 2: Packs & Runner (M2–M3)

**BLUF:** M2 defines the versioned **attack-pack format**, the loader/validator, and the first packs. M3
builds the **execution spine** that runs a pack, one case at a time or all, capturing each case's attack
trajectory.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M2 — Pack format, loader & validation — ✅ COMPLETE

**Goal:** define the versioned **attack-pack format**, load and strictly validate packs, and ship the first
catalog — reproducing each documented incident pattern (R1). The **path-safety invariant** lands here,
closing the predecessor's traversal gap at the foundation.

**Status:** ✅ Complete (2026-10-12) · **Execution plan:** [m2-m3](../plans/m2-m3-packs-runner-execution-plan.md) · **Issues:** #106–#117

**Requirements / PRDs:** [PRD 15](../../prd/15-data-model.md), [PRD 21](../../prd/21-pack-catalog.md),
[PRD 05](../../prd/05-features.md) (R1), [PRD 24](../../prd/24-predecessor-gap-closure.md) (G3).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 2.1 | Pack schema | `pack` block (name, version, description, `min_agentdrill`, license, trust, hash) + `cases[]` (id, title, goal, `incident_ref`, target, driver, attack steps, oracle, `benign_twin`, cleanup, tags, difficulty, budget, ATLAS/OWASP tags, adversary profile) | versioned schema | schema published; JSON round-trip | #106 |
| 2.2 | Loader + strict validation | YAML primary / JSON secondary; duplicate-id, missing-field, incoherent-budget checks; oracle resolution; threshold ranges; **`^[a-zA-Z0-9_-]+$` identifiers enforced before any path use** | loader/validator | malformed pack → `PackParseError` with location; traversal-shaped id rejected | #107 |
| 2.3 | Oracle/target/driver resolution at load | Resolve every referenced oracle/adapter from the registry at load; unknown → `ConfigError` (exit 2), never a silent pass | resolver | unknown reference fails before any run | #108 |
| 2.4 | Validate + list commands | `agentdrill validate --strict [--pre-flight]`; `agentdrill list packs/cases --tag/--target/--difficulty` | CLI | launch catalog validates clean; selection works | #109 |
| 2.5 | Pack catalog v0.1.0 | Author `quickstart-demo`, `incidents-core` (incident-replay families), `incidents-security` (re-pointed security scenarios), `kill-chain` | packs | each pack reproduces its named incident pattern | #110 |
| 2.6 | Fixture corpus + twin hooks | Deterministic-mode fixtures for the catalog; `benign_twin:` linkage + twin-driver hook (consumed at M13) | fixtures | fixtures cover every case's tools | #111 |
| 2.7 | Pack metadata & hashing | SHA-256 pack hashing + license/trust fields + `min_agentdrill` gate | metadata | result tables bind to `pack@version+hash` | #112 |
| 2.T | Tests for this milestone | Valid/invalid packs, traversal rejection, unknown-ref failure, catalog validation, hashing | tests | all new paths covered; coverage ≥ 95% | #113 |
| 2.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #114 |
| 2.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #115 |
| 2.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #116 |
| 2.D | Design + reference docs | Pack-format spec, catalog doc, data-model notes, schema files | docs | docs updated + linked here | #117 |

**Tests required:** schema round-trip; malformed-YAML location; duplicate-id; unknown oracle/target;
path-traversal id rejection; catalog validates `--strict`; hash stability.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Every catalog pack reproduces its documented incident pattern (R1)
- [x] Path-safety invariant enforced (predecessor G3 closed at the foundation)
- [x] `agentdrill validate --strict` passes on the shipped catalog

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 15](../../prd/15-data-model.md) · [PRD 21](../../prd/21-pack-catalog.md) ·
pack-format spec · [PRD 24](../../prd/24-predecessor-gap-closure.md) (G3).

---

## Milestone M3 — Runner & execution spine — ✅ COMPLETE

**Goal:** the runner that executes a validated pack, capturing each case's **attack trajectory**, enforcing
per-case timeouts in isolation, and never aborting the pack on a case failure (absorbed from the
predecessor).

**Status:** ✅ Complete (2026-10-12) · **Execution plan:** [m2-m3](../plans/m2-m3-packs-runner-execution-plan.md) · **Issues:** #284, #118–#127

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md), [PRD 15](../../prd/15-data-model.md),
[PRD 13](../../prd/13-non-functional-requirements.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 3.1 | Run model + artifact | `Run`/`RunArtifact`: output, trajectory steps (`tool_call`/`tool_result`/`response`/`note`), cost, status (`completed\|timeout\|error\|aborted`), timing | models | full JSON round-trip | #284 |
| 3.2 | `run_one` / `run_all` | Execute a single case or the pack; `--tags` filter; write `.agentdrill/runs/<id>/` (`run.json` + `artifacts/<case_id>.json`) | runner | pack runs end to end | #118 |
| 3.3 | Per-case timeout + isolation | Hard timeout via separate process for callable drivers; timeout → `status="timeout"`, continue | runner | a hung case does not hang the pack | #119 |
| 3.4 | Error capture / non-abort | Crash/non-zero → `status="error"` with stderr; **a case failure never aborts the pack** | runner | one failing case leaves others unaffected | #120 |
| 3.5 | Parallel execution + backpressure | `--workers` concurrency with `--max-outstanding` | runner | parallel == serial results, order preserved | #121 |
| 3.6 | Budget governor | Per-case `budget` + run-level `--max-cost`; exceed → remaining `aborted: cost_exceeded` (reported, never hidden) | runner | over-budget run aborts cleanly + reports | #122 |
| 3.T | Tests for this milestone | Round-trip, timeout, crash, non-abort, parallel determinism, budget abort | tests | all new paths covered; coverage ≥ 95% | #123 |
| 3.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #124 |
| 3.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #125 |
| 3.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #126 |
| 3.D | Design + reference docs | Runner design, run-artifact spec, error-handling notes | docs | docs updated + linked here | #127 |

**Tests required:** artifact round-trip; timeout; crash; non-abort guarantee; parallel-vs-serial equality +
ordering; budget-exceeded abort.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] A validated pack runs to completion; one failing case never aborts the pack
- [x] Timeouts are hard (isolated process); budget exceedance is reported, not swallowed

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** runner design · run-artifact spec · [PRD 15](../../prd/15-data-model.md).

---

Part 2 green ⇒ packs run end to end; proceed to [Part 3 (M4–M5)](wbs-v0.1.0-part3-drivers-targets.md).
