# Field Test Plan (v0.1.0)

**Status:** plan (design intent). Executed at WBS M23.

## Goal

Run every critical user journey end to end against a **real deployed stack** (the Wave-0 enforcers) plus the
bundled demo, and publish an honest report — including what was **not** tested.

## Scope (CUJ-1..24)

| Group | Cases |
|---|---|
| Core | run a pack (CUJ-1), gate a policy PR (CUJ-2), reproduce the benchmark (CUJ-3), drill an incident (CUJ-4) |
| Kill chain | verify kill-time (CUJ-5, CUJ-16) |
| Self-attack | evasion pack (CUJ-6), drill-the-drill, dark holdout |
| Lifecycle | intake→pack (CUJ-20), fix holds (CUJ-21), seams (CUJ-22), verify offline (CUJ-23), quickstart (CUJ-24) |
| Trust | efficacy (CUJ-19), attribution (CUJ-14), dispute (CUJ-13), HITL (CUJ-17), defense contract (CUJ-15) |
| Scale | fleet rollup (CUJ-18), trigger re-drill (CUJ-12), trend (CUJ-9), coverage (CUJ-10) |

## Environment

- **Demo stack** (bundled): offline, `mock`-attested, watermarked `never evidence`.
- **Real stack**: the Wave-0 enforcers (agentgate, agentkeys, agentseatbelt/kernel, policyweave output,
  agenthalt) + agentwatch, on Claude Code + Cursor (≥2 Tier-1).

## Method

1. Fresh machine; timed first run (≤15 min) via `quickstart`.
2. Execute each CUJ; capture evidence; classify failures (shim / wrong config / adapter / oracle).
3. Fix defects + add a regression test each.
4. Publish `FIELD_TEST_REPORT.md` — pass/fail **and the not-tested list**.

## Exit gate

All field scenarios pass; defects fixed with regression evidence; the report states honestly what was not
tested; every CUJ exercised end to end.
