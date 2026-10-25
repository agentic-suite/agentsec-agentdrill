# Observability — Design

**BLUF:** agentdrill observes itself the same way it observes defenses: structured per-run signals, a
tamper-evident audit log, a shareable run summary, and an offline verifier. If agentdrill can't explain its
own run, it shouldn't grade anyone else's.

> **Built (v0.1.0)** (pre-build). WBS M7/M22.

## Per-run signals

| Signal | Where |
|---|---|
| Run summary | dimensions (compatibility/enforcement/integrity) + outcome split + exit code |
| Artifacts | `.agentdrill/runs/<id>/` (run.json, manifest, per-case artifacts) |
| Audit log | `.agentdrill/audit/` — append-only, rotated, hash-chained (DD/PRD 06) |
| Manifest | pins, target/driver digests, oracle versions, env names (never values) |

## Commands (`doctor` / `validate`)

- `agentdrill doctor` — environment + target sanity; a clear verdict, never a false "ok".
- `agentdrill validate --strict [--pre-flight]` — pack/target validation before a run.
- `agentdrill list` — packs/oracles/targets/drivers + `plugin info` (garak-style introspection).

## Trust surfaces

- **Fail-closed** on the harness's own integrity failures (tamper → block, not warn).
- **Shareable run summary** — one object answers "what happened," with evidence refs.
- **Offline verifier** (F64) — a bundle verifies on a machine that never ran the drill (three verdicts:
  intact / complete / honest-shaped).

## Meta-observability

The drill-the-drill suite (F43) checks the observability itself: does a `blocked` verdict carry its
expected telemetry (`telemetry_gap` otherwise)? Does a must-block miss exit non-zero? These are CI-enforced,
not aspirations (predecessor G10).
