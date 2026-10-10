# Maintenance Backlog

Living list of post-v0.1.0 work and deferred decisions. Milestones live in the [WBS](wbs/v0.1.0/wbs-v0.1.0-index.md).

## Deferred decisions

| # | Item | Direction |
|---|---|---|
| MB-1 | **Re-pin cadence** (DD-33) | Schedule for when a pinned model drifts/dies; re-publish with a note |
| MB-2 | **Dual-use boundary** (DD-34) | Exact line for mutation/adaptive content; review gate for shipped packs |
| MB-8 | **T3 adaptive attacker tier** (DD-44) | Deferred for v0.1.0; local-only, RoE-gated, unpublished when introduced ([PRD 25](prd/25-attacker-strength-and-pressure.md)) |
| MB-9 | **Competitor/defense benchmark publication shape** (DD-45) | Neutrality rules + right-of-reply + licensed-config-only; counsel review before first publication ([PRD 29](prd/29-bring-your-own-defense.md)) |

## Post-v0.1.0 candidates

| # | Item | Why deferred |
|---|---|---|
| MB-3 | Database backend (was "SQLite planned" in the predecessor) | Local JSON covers v0.1.0; add only when a workload demands it ([PRD 14](prd/14-non-goals.md)) |
| MB-4 | Enterprise platform **native connectors** (Copilot Studio, Agentforce, Bedrock) | drillable as **remote targets now** ([PRD 41](prd/41-platform-compatibility.md)); native connectors deferred |
| MB-5 | A2A attack packs (deeper) | A2A **1.0 is stable** → in scope ([PRD 39](prd/39-frontier-attack-classes.md) class 6, [PRD 41](prd/41-platform-compatibility.md)); depth deferred |
| MB-6 | Richer competitor benchmark automation | starts as PR submissions (F57) |
| MB-7 | Per-adapter sandbox profiles | replaced by the trust matrix; revisit if adapters proliferate |

## Known limitations to shrink

Tracked in [reference/known-limitations.md](reference/known-limitations.md) — Tier-1 Copilot lower-layer
coverage, re-pin cadence, contamination scope.
