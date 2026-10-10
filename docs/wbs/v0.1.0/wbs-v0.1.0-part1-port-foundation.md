# WBS v0.1.0 — Part 1: Port the Codebase & Foundation (M0–M1)

**BLUF:** **M0 is a bulk port of the entire predecessor eval-harness codebase** (urgent — it makes
agentdrill self-contained; the predecessor is retained and made private, never deleted). M1 rebrands and
adapts the foundation.

> **Standard exit criteria + closure apply to every milestone** (tests · coverage ≥95% · lint strict ·
> docs · traceability · absorbed/ported items · committed+pushed+issue closed+checkpoint).

---

## Milestone M0 — Port the predecessor codebase — ✅ COMPLETE

**Goal:** move **all** of the predecessor eval-harness codebase into agentdrill, rename the namespace, and
get the ported test suite green — after which the source repository is **retained and made private** (never
deleted). This makes agentdrill self-contained; later milestones re-point the harness mechanics from
*agent-quality grading* to *defense proof*.

**Status:** ✅ Complete · **Execution plan:** [M0 port plan](../../plans/m0-port-execution-plan.md) ·
**Issues:** #2–#13 · **Provenance:** [THIRD_PARTY_NOTICES](../../../THIRD_PARTY_NOTICES.md) ·
**Layout/setup:** [development](../../development.md).

**Requirements / PRDs:** [PRD 10](../../prd/10-feature-parity.md) (absorption is mandatory and in-repo),
[PRD 03](../../prd/03-landscape.md) (migration), [PRD 24](../../prd/24-predecessor-gap-closure.md).

**Work items (this milestone *is* the port)**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 0.1 | **Port** the entire repo tree | Bulk-move `src/`, `tests/`, `scenarios/`, packaging, tooling, CI, and the docs subset into agentdrill | full tree present | tree mirrors the source | #2 |
| 0.2 | **Rename namespace** | predecessor package → `agentdrill` across code, tests, configs, docs | renamed | zero predecessor-namespace references remain | #3 |
| 0.3 | **Preserve git history** | `git filter-repo` / subtree merge | merged history | provenance intact | #4 |
| 0.4 | Adapt packaging metadata | `pyproject.toml` for `agentdrill` / `agentsec-agentdrill`, CLI entry | packaging | `pip install -e .` works | #5 |
| 0.5 | **Ported suite green** | Get the ported test suite passing with minimal adaptation only | passing tests | ported suite passes | #6 |
| 0.6 | Record provenance + porting notes | `THIRD_PARTY_NOTICES`, `CHANGELOG` | docs | MIT attribution recorded | #7 |
| 0.7 | Update design docs | architecture + development describe the ported tree | docs | docs describe the port | #8 |
| 0.T | Tests for this milestone | Unit + integration + fault-injection for the ported tree | tests | all new paths covered; coverage ≥ 95% | #9 |
| 0.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #10 |
| 0.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #11 |
| 0.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #12 |
| 0.D | Design + reference docs | Porting notes, architecture, THIRD_PARTY_NOTICES | docs | docs updated + linked here | #13 |

**Tests required:** the entire ported suite (runner, scoring, adapters, fixtures, baselines, security)
passes after the namespace rename.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · port tasks complete
- [x] The full predecessor codebase is represented in agentdrill
- [x] Zero predecessor-namespace references remain; history preserved as a single import commit (SHA recorded)
- [x] Ported suite green → **predecessor retained and made private (not deleted)** at M32

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** architecture · development · THIRD_PARTY_NOTICES · CHANGELOG · README.

---

## Milestone M1 — Foundation & identity — ✅ COMPLETE

**Goal:** agentdrill identity, CLI, configuration, packaging, and CI — rebranded from the ported tooling.

**Status:** ✅ Complete · **Execution plan:** [M1 plan](../../plans/m1-foundation-execution-plan.md) ·
**Issues:** #14–#24.

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md), [PRD 11](../../prd/11-decisions.md)
(DD-15..DD-19), [PRD 13](../../prd/13-non-functional-requirements.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 1.1 | Rebrand build config | Port pyproject/quality-gate tooling; name/bin = agentdrill | build config | `make setup` green | #14 |
| 1.2 | CLI framework + subcommands | Wire the full command surface (`run`, `list`, `validate`, `verify`, `quickstart`, `pack`, `registry`, `watch`, `schedule`, `benchmark`, `init`, `doctor`, `version`) with reserved exit codes | CLI | `agentdrill --help` lists commands | #15 |
| 1.3 | Configuration model | Target/pack config loading: precedence, `strict`, **fail-closed** on invalid config | config loader | invalid config fails closed (exit 2) | #16 |
| 1.4 | CI & quality gate | `ruff` + `mypy --strict` + `pytest` + coverage ≥95% + DCO | GitHub Actions | CI green on PR | #17 |
| 1.5 | Self-observability | `agentdrill doctor` + structured logging + per-run audit-log skeleton | CLI + logs | doctor reports a verdict | #18 |
| 1.6 | Identity & governance docs | README/LICENSE/CODEOWNERS/SECURITY finalized; PRD traceability wired | docs | docs match identity | #19 |
| 1.T | Tests for this milestone | Config fail-closed, CLI smoke, doctor | tests | all new paths covered; coverage ≥ 95% | #20 |
| 1.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #21 |
| 1.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #22 |
| 1.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #23 |
| 1.D | Design + reference docs | Development guide, CLI reference, README, traceability | docs | docs updated + linked here | #24 |

**Tests required:** config precedence + fail-closed; CLI smoke; doctor verdict on clean vs. broken env.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] `make setup/lint/typecheck/test` work; `agentdrill --help` lists subcommands
- [x] Bad config fails closed; CI green

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** README · [PRD 11](../../prd/11-decisions.md) · [PRD 13](../../prd/13-non-functional-requirements.md).

---

Part 1 green ⇒ agentdrill is self-contained (the predecessor is retained privately); proceed to
[Part 2 (M2–M3)](wbs-v0.1.0-part2-packs-runner.md).
