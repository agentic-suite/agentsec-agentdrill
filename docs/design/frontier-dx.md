# Frontier & DX — Design

**BLUF:** The surfaces that make the proof engine disappear into the developer's loop and scale across a
fleet — pack selection/diff, dry-run/explain, templates, CI-matrix export, programmatic assertions,
provenance cards, a read-only MCP drill surface and fleet mode.

> **Status:** normative (M20). **Implementation:** `agentdrill/dx/` — `diff.py` (F67), `dry_run.py`
> (F69), `templates.py` (F70), `ci_matrix.py` (F72), `assertions.py` (F73), `provenance.py` (F74),
> `mcp_surface.py` (F77), `fleet.py` (F45). CLI: `pack diff`, `export ci`. Reference:
> [frontier-dx](../reference/frontier-dx.md). Spec: [PRD 22](../prd/22-frontier-dx-features.md).

## Pack diff & selection (20.1, F67)

`diff_packs(a, b)` → `PackDiff` (added / removed / changed case delta + tag coverage delta);
`pack diff <a> <b>`. `list cases --tag/--target/--difficulty` selects.

## Dry-run & explain (20.2, F69)

`dry_run(pack, explain=)` → `DryRunPlan` (bound cases, targets, expected verdicts, evidence; `executions
== 0`); `render_dry_run`. A dry-run performs **zero** executions.

## Templates (20.3, F70)

`scaffold(template, name=)` / `scaffold_yaml` for `mcp-poisoning` / `exfil-chain` / `destructive-command`
/ `supply-chain` — attack cases with oracle stubs, **benign twins**, cleanup and ATLAS/OWASP tags.

## CI-matrix export (20.4, F72)

`build_ci_matrix` / `validate_ci_matrix` / `render_ci_matrix(fmt=github-actions|gitlab)`; `export ci`.

## Programmatic assertions (20.5, F73)

`assert_blocked` / `assert_missed` / `assert_degraded` / `assert_kill_time_under` over run objects
(`DxAssertionError`).

## Provenance cards (20.6, F74)

`ProvenanceCard` (sources, dates, mutation policy, author, reviewers) + `build_card` / `render_card` /
`validate_card` (reviewers non-empty).

## MCP drill surface (20.7, F77)

`McpDrillSurface` exposing read-only tools (`list_packs` / `get_pack` / `list_runs` / `get_run` /
`query_results`); `require_read_only` rejects any write tool; queries are recorded.

## Fleet mode (20.8, F45)

`FleetRollup` / `StackResult` + `build_fleet`; `coverage()` per stack and `outliers(threshold=)` —
per-stack honest coverage rollups (opt-in, self-hosted).
