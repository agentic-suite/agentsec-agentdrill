# CI Gate — Design

**BLUF:** agentdrill enforces the drill in CI — structured exit codes, per-dimension gating, divergence
gating — and follows change: a **trigger watcher** re-runs the affected packs when config/policy/model/
harness changes. A policy PR that un-blocks a known attack is **rejected before merge** (R3).

> **Status:** normative (M11). Implementation: `agentdrill/ci/` — `gate.py` (exit codes), `gating.py`
> (dimension + divergence), `output.py` (GitHub/GitLab + step summary), `triggers.py` (CART),
> `watch.py` (local dev loop), `selection.py` (diff-aware), `annotations.py` (PR + webhook),
> `schedule.py` (cadence drills). CLI: `agentdrill watch` / `agentdrill schedule`. Reference:
> [ci-integration](../reference/ci-integration.md).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all cases behaved as expected |
| 1 | one or more cases **missed** (regression) |
| 2 | configuration error |
| 3 | oracle/judge infrastructure error |
| 4 | **critical miss** (a must-block enforcement case was not blocked) |
| 5 | critical divergence (deterministic vs judge) |

Resolution order: critical miss (4) > config (2) > oracle infra (3) > miss (1) > pass (0). Codes are
propagated with or without `--ci`.

## Gating

- `--fail-on compatibility|enforcement|integrity` — each dimension gated independently (<0.8 fails).
- `--fail-on-divergence critical` — forks a critical-divergence failure.
- `--hold-k <n>` — gate critical must-block cases on **`Hold@k` = 100%** (M24).
- `--ci` — suppresses interactive output; writes `$GITHUB_STEP_SUMMARY` when available.
- `--output-format github-actions|gitlab`.

### Additional release-blocking signals (M23–M28)

- **`witness_discrepancy`** (defense said blocked, effect landed) — integrity failure (M23).
- **Out-of-scope action** (an RoE preflight violation) — **release-blocking** (M28).
- **`dirty_target`** (cleanup failure) — release-blocking.
- **Expired waiver still suppressing** the gate — fails (M28).
- **Attestation invalid/stale** where a consumer requires one — fails (M28).
- **`unproven` critical attack-path older than SLA** — fails (M27).

## Change-driven execution

| Surface | Behavior |
|---|---|
| **Trigger watcher (CART, F22)** | subscribe to config/policy/model/harness-change events; re-run the **affected** packs (drift alerts are triggers, scheduled runs labeled) |
| **Watch mode (F68)** | `agentdrill watch` — local re-run on file change (dev loop) |
| **Diff-aware (F76)** | affected cases computed from the changed surface; CI time scales with diff size, `--full` for release |
| **Scheduled drills (F71)** | `agentdrill schedule` for out-of-PR drift (vendor model, MCP rug-pull, marketplace skill) |
| **PR annotations (F47)** | case/stage/evidence/attribution annotated on the PR; Slack/webhook on gate failure |

## Guardrail

The CI gate is itself drilled: a meta-verification case asserts a must-block miss **exits non-zero** — so a
silent pass-everything gate is caught by the gate (predecessor G10).
