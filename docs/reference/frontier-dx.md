# Frontier & DX — Reference

**Status:** normative (M20). Implementation: `src/agentdrill/dx/`. Design:
[frontier-dx](../design/frontier-dx.md). Spec: [PRD 22](../prd/22-frontier-dx-features.md).

## Pack diff (20.1, F67)

`diff_packs(a, b)` → `PackDiff` (added/removed/changed + tag `coverage_delta`); CLI `pack diff <a> <b>`.

## Dry-run (20.2, F69)

`dry_run(pack, explain=False)` → `DryRunPlan` (`cases`, `executions == 0`); `render_dry_run(plan)`.

## Templates (20.3, F70)

`TEMPLATES` = mcp-poisoning / exfil-chain / destructive-command / supply-chain; `scaffold(template,
name=)` → `AttackPack` (attack + benign twin, cleanup, ATLAS/OWASP tags); `scaffold_yaml`.

## CI-matrix (20.4, F72)

`build_ci_matrix(packs, manifest=, attestation=)` → `CiMatrix`; `validate_ci_matrix`; `render_ci_matrix
(matrix, fmt=)` for `github-actions` / `gitlab`; CLI `export ci`.

## Assertions (20.5, F73)

`assert_blocked` / `assert_missed` / `assert_degraded` (over a `Verdict` or outcome string) and
`assert_kill_time_under(elapsed, seconds=)`; `DxAssertionError`.

## Provenance cards (20.6, F74)

`build_card(pack_ref=, author=, reviewers=, sources=, dates=, mutation_policy=)` → `ProvenanceCard`;
`render_card`; `validate_card` (reviewers + sources non-empty).

## MCP drill surface (20.7, F77)

`McpDrillSurface` (`tools()`, `call(name, **kwargs)`, `queries()`); `is_write_tool`; `require_read_only`.

## Fleet mode (20.8, F45)

`build_fleet(pack_ref, stacks)` → `FleetRollup`; `coverage()` per stack; `outliers(threshold=)`.
