# Field Test Plan (v0.1.0)

**Status:** plan (design intent). Executed at WBS M31.

## Goal

Run every critical user journey end to end against a **real deployed stack** (the Wave-0 enforcers) plus the
bundled demo, and publish an honest report — including what was **not** tested.

## Scope (CUJ-1..63)

| Group | Cases |
|---|---|
| Core | run a pack (CUJ-1), gate a policy PR (CUJ-2), reproduce the benchmark (CUJ-3), drill an incident (CUJ-4) |
| Kill chain | verify kill-time (CUJ-5, CUJ-16) |
| Self-attack | evasion pack (CUJ-6), drill-the-drill, dark holdout |
| Lifecycle | intake→pack (CUJ-20), fix holds (CUJ-21), seams (CUJ-22), verify offline (CUJ-23), quickstart (CUJ-24) |
| Trust | efficacy (CUJ-19), attribution (CUJ-14), dispute (CUJ-13), HITL (CUJ-17), defense contract (CUJ-15) |
| Scale | fleet rollup (CUJ-18), trigger re-drill (CUJ-12), trend (CUJ-9), coverage (CUJ-10) |
| **Additions — strength & proof** | `Hold@k` gate (CUJ-28), read an honest number (CUJ-29), the log lied / witness discrepancy (CUJ-30), proof without telemetry (CUJ-31) |
| **Additions — lab & bypass** | author a rug-pull case (CUJ-32), carrier matrix (CUJ-33), bypass + minimal repro (CUJ-34), coverage not just green (CUJ-35) |
| **Additions — neutrality & integration** | pick between defenses (CUJ-36), reproduce the OSS table (CUJ-37), inline in the PR (CUJ-54), did the SOC see it (CUJ-55) |
| **Additions — context & governance** | don't ship the outage (CUJ-38), shadow then promote (CUJ-39), trifecta inventory (CUJ-40), new path fails the gate (CUJ-41), hours not days (CUJ-42), cite or drop (CUJ-43), sanctioned exception, visible miss (CUJ-44), it expired (CUJ-45), admission gate on freshness (CUJ-46), underwriter verification (CUJ-47), authorized to fire (CUJ-48), abort in seconds (CUJ-49) |
| **Additions — detonation & frontier** | before allowlisting (CUJ-50), registry admission (CUJ-51), submit and get credit (CUJ-52), convert to a regression (CUJ-53), approval dialog truth (CUJ-56), contain the cascade (CUJ-57) |
| **Additions — explorer, platform & standards** | red CI to root cause (CUJ-58), adjudicate at speed (CUJ-59), per-harness depth (CUJ-60), add my harness (CUJ-61), auditor evidence index (CUJ-62), contributor tag lint (CUJ-63) |

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
