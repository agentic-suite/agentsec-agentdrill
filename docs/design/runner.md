# Runner — Design

**BLUF:** The runner is the execution spine — load a validated pack, run one case or all, capture each
case's **attack trajectory**, enforce per-case timeouts in isolation, never abort the pack on a case
failure, and write artifacts under `.agentdrill/runs/`. Absorbed from the predecessor runner, re-pointed.

> **Implemented (M3).** Spine in `src/agentdrill/attack_runner.py`; models in
> `src/agentdrill/models/attack_run.py` (`Run` + `CaseArtifact` — the design calls
> the per-case artifact `RunArtifact`; the name `CaseArtifact` avoids clashing with
> the ported scenario `RunArtifact`). Reference: [../reference/run-artifact-spec.md](../reference/run-artifact-spec.md).

## Flow

```
pack (validated) → Runner.run_one/run_all → driver.run(case) → RunArtifact → .agentdrill/runs/<id>/
```

## Decisions

1. **Case independence** — a case failure (timeout/crash/error) marks the case and continues; a pack is
   never aborted by one case.
2. **Hard timeouts** — callable drivers run in a separate process so a hung case cannot hang the pack.
3. **Budget governor** — per-case `budget` + run-level `--max-cost`; exceed ⇒ remaining cases
   `aborted: cost_exceeded`, reported (never hidden).
4. **Parallelism** — `--workers` + `--max-outstanding` backpressure; parallel == serial results, order
   preserved.

## Models

- `TrajectoryStep` — `tool_call` / `tool_result` / `response` / `note` (reused from `models/artifact.py`).
- `Cost` — input/output/total tokens, cost (reused).
- `CaseArtifact` (design: `RunArtifact`) — id, case_id, timestamps, output, trajectory, cost, status
  (`completed|timeout|error|aborted`), error. Full JSON round-trip.
- `Run` — pack-level index: run_id, pack_ref (`name@version+hash`), timestamps, case order.

## Artifacts

```
.agentdrill/runs/<run_id>/
  run.json              # pack-level index (pack hash, target, driver, timestamps, case order)
  run-manifest.json     # reproducibility manifest (see storage-design)
  recon.json            # recon snapshot ref
  artifacts/<case_id>.json   # per-case Result + Evidence
```

## Error handling

| Failure | Behavior |
|---|---|
| Invalid pack | `PackParseError` with location (at load) |
| Agent timeout | `status="timeout"`, continue |
| Crash / non-zero exit | `status="error"` + stderr, continue |
| HTTP/import error | `status="error"`, continue |
| Budget exceeded | remaining `aborted: cost_exceeded` |

## Testing

Unit — models round-trip, timeout, crash, non-abort, parallel equality + ordering, budget abort.
Integration — a validated pack runs to completion; one failing case leaves others unaffected.
