# CI Integration — Reference

**Status:** normative (M11). Gate + change-driven execution: `src/agentdrill/ci/`. Design:
[../design/ci-gate.md](../design/ci-gate.md).

## Exit codes (11.1)

`run_exit_code(cases, verdicts, config_error=, oracle_error=, divergence=)` resolves the reserved
code, most-severe-first:

| Code | Meaning |
|---|---|
| 0 | all cases behaved as expected |
| 1 | one or more cases missed (regression) |
| 2 | configuration error |
| 3 | oracle/judge infrastructure error |
| 4 | critical miss — a must-block enforcement case was not blocked |
| 5 | critical divergence (deterministic vs judge) |

A must-block miss (expected `blocked`, observed `missed`) is code 4 and exits non-zero (R3). Codes are
propagated with or without `--ci`.

## Gating (11.2)

`check_gates(verdicts, fail_on=(), fail_on_divergence=None, threshold=0.8)` returns `GateFailure`s:
`--fail-on compatibility|enforcement|integrity` gates each dimension independently (blocked rate below
the threshold fails); `--fail-on-divergence critical` fails on a critical divergence.

## CI output (11.3)

`render_ci_output(exit_code, failures, output_format="github-actions"|"gitlab")` renders annotations +
a summary table; `write_step_summary(text)` appends to `$GITHUB_STEP_SUMMARY` (no-op when unset).

## Trigger watcher / CART (11.4, F22)

`TriggerWatcher.register(pack_ref, surfaces)` + `affected(ChangeEvent(kind, surface))` — a
config/policy/model/harness/drift change re-runs only the affected packs.

## Local watch (11.5, F68)

`agentdrill watch` (with `--once` for dev/CI) polls watched files via `LocalWatcher.poll(snapshot,
path_surfaces)` and reports the affected packs within one save.

## Diff-aware re-runs (11.6, F76)

`case_surfaces(case)` (target type + attack tools + tags), `affected_cases(cases, changed_surfaces)`
and `selection(...)` (`selected`, `total`, `fraction`) so CI time scales with diff size; the selected
set equals the cases bound to the changed surfaces.

## PR annotations + alerts (11.7, F47)

`annotate(change, file=, line=, stage=, evidence=, attribution=)` + `github_annotation(...)`; a
regression annotates the right file and its message names the case/stage/evidence/attribution.
`build_alert(exit_code, failures)` + `notify(webhook, payload)` post a JSON alert to a Slack/webhook
endpoint on gate failure.

## Scheduled drills (11.8, F71)

`DrillSchedule`/`ScheduledFinding` + `is_due`/`due_drills`/`record_finding` — cadence runs for
out-of-PR drift (vendor model, MCP rug-pull, marketplace skill) write a finding file labeled with its
trigger. `agentdrill schedule [--cadence] [--once]`.
