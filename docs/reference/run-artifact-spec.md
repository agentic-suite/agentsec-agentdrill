# Run Artifact — Specification

**Status:** normative (M3). Models: `src/agentdrill/models/attack_run.py`; spine:
`src/agentdrill/attack_runner.py`. Design: [../design/runner.md](../design/runner.md).

Each run writes to `.agentdrill/runs/<run_id>/`:

```
.agentdrill/runs/<run_id>/
  run.json                 # pack-level index (Run)
  artifacts/<case_id>.json # per-case result (CaseArtifact)
```

## `run.json` (`Run`)

| Field | Meaning |
|---|---|
| `run_id` | The run identifier |
| `pack_ref` | `name@version+hash` the run binds to (DD-28) |
| `target` / `driver` | Run-level target/driver config (populated from M5) |
| `timestamps` | `{start, end, duration_ms}` (ISO-8601 UTC) |
| `case_order` | The case ids in the order they were run |

## `artifacts/<case_id>.json` (`CaseArtifact`)

| Field | Meaning |
|---|---|
| `id` | `<run_id>::<case_id>` |
| `case_id` | The attack case id |
| `timestamps` | `{start, end, duration_ms}` |
| `output` | `{final, structured}` |
| `trajectory` | `TrajectoryStep[]` — `tool_call` / `tool_result` / `response` / `note` |
| `cost` | `{input_tokens, output_tokens, total_tokens, cost_usd}` |
| `status` | `completed` \| `timeout` \| `error` \| `aborted` |
| `error` | The captured traceback (on `error`) or the abort reason (e.g. `cost_exceeded`) |

The model round-trips losslessly through JSON; artifacts re-load identically across processes and CI runs.

## Status semantics

| Status | Set when |
|---|---|
| `completed` | The driver returned an outcome |
| `timeout` | The case exceeded the per-case hard timeout (isolated process, killed) |
| `error` | The driver raised / crashed (traceback captured) |
| `aborted` | A budget governor stopped the case (`error="cost_exceeded"`) |

A case failure **never** aborts the pack — every case yields an artifact (runner design decision 1).
