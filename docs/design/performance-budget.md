# Performance Budget — Design

**BLUF:** A drill must gate every policy PR cheaply: local-first packs run in minutes; the CI smoke subset
(deterministic oracles + fixtures, no judge) runs per-commit; parallelism scales with `--workers`; the judge
costs money only where a case needs it, and is cached.

> **Design intent** (pre-build). WBS M22. NFR reference: [PRD 13](../prd/13-non-functional-requirements.md).

## Budgets

| Path | Target |
|---|---|
| Single pack (deterministic, fixtures) | minutes, local |
| CI smoke subset | per-commit; no judge, no API keys |
| Full pack + judge | nightly / pre-release |
| Kill-time case | ≥5 trials, p50/p95/max (not a single sample) |

## Throughput & backpressure

- `--workers N` concurrency with `--max-outstanding` backpressure to cap in-flight cases.
- Parallel == serial results; case order preserved.
- Per-case **hard timeout** in an isolated process (a hung case can't hang the pack).

## Cost

- Deterministic oracles are free; the judge runs only where needed.
- **Judge/oracle cache** (TTL) dedupes repeated calls; `cache stats` reports savings.
- `--max-cost` run ceiling; exceed ⇒ remaining cases `aborted: cost_exceeded`, reported.

## Efficiency vs integrity

The evaluation hierarchy is **enforcement > integrity > efficiency**: a fast run never excuses a missed
attack or a broken evidence path. Efficiency regressions are informational unless promoted.

## Gate

A perf budget test (M22) fails CI if the deterministic smoke subset exceeds its budget — the same discipline
the predecessor enforced in its own CI.
