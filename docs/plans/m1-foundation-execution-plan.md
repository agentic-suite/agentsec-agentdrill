# agentdrill M1 — Foundation Execution Plan

**Spec:** [WBS M1](../wbs/v0.1.0/wbs-v0.1.0-part1-port-foundation.md#milestone-m1--foundation--identity) ·
[PRD 02](../prd/02-architecture.md) · [PRD 11](../prd/11-decisions.md) · issues #—.

## Global constraints

- Exit gate: full suite green · coverage ≥ 95% · `ruff` zero · `mypy --strict` clean.
- Config is **fail-closed** — invalid config refuses to run (exit 2), never defaults silently.
- Conventional commits, signed off (DCO).

---

## Task 1 — Rebrand build config (1.1)
Port pyproject/quality-gate tooling; `name`/bin = `agentdrill`; `make setup/lint/typecheck/test`.
**Expected:** `make setup` green.

## Task 2 — CLI framework + subcommands (1.2)
Wire `run`, `list`, `validate`, `verify`, `quickstart`, `pack`, `registry`, `watch`, `schedule`,
`benchmark`, `init`, `doctor`, `version`; reserve exit codes 0–5.
**Expected:** `agentdrill --help` lists commands; each parses.

## Task 3 — Configuration model (1.3)
Target/pack config loading: precedence, `strict`, **fail-closed**. **RED** → a bad-config test that must
fail-closed → **GREEN**.
**Expected:** invalid config → exit 2.

## Task 4 — CI & quality gate (1.4)
`ruff` + `mypy --strict` + `pytest` + coverage ≥95% + DCO in `ci.yml` (replace the placeholder).
**Expected:** CI green on a PR.

## Task 5 — Self-observability (1.5)
`agentdrill doctor` + module-level structured logging + per-run audit-log skeleton.
**Expected:** doctor reports a clear verdict.

## Task 6 — Identity & governance docs (1.6, 1.D)
Finalize README/LICENSE/CODEOWNERS/SECURITY; wire PRD traceability.
**Expected:** docs match identity; traceability links resolve.
