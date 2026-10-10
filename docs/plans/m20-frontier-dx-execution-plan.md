# agentdrill M20 — Frontier & DX Execution Plan

**Spec:** [WBS M20](../wbs/v0.1.0/wbs-v0.1.0-part11-dx-absorption.md#milestone-m20--frontier--dx) · [PRD 22](../../prd/22-frontier-dx-features.md).

## Constraints
Exit gate + gates (`.T/.C/.L/.CR/.D`). Dry-run must perform **zero** executions; the MCP surface is read-only.

## Tasks
- **T1 — Pack diff & selection (20.1, F67):** `pack diff`; `list cases --tag/--target/--difficulty`.
- **T2 — Dry-run & explain (20.2, F69):** plan without executing. *RED:* zero-execution probe test. *GREEN.*
- **T3 — Templates (20.3, F70):** `init --template` scaffolds oracle stubs, twins, cleanup, tags; passes lint.
- **T4 — CI-matrix export (20.4, F72):** `export ci` emits a matrix config.
- **T5 — Programmatic assertions (20.5, F73):** `assert_blocked` / `assert_missed` / `assert_kill_time_under`.
- **T6 — Provenance cards (20.6, F74):** per-pack card rendered on results.
- **T7 — MCP drill surface (20.7, F77):** read-only; **no write tools**. *RED:* tool-list has no writers. *GREEN.*
- **T8 — Fleet mode (20.8, F45, CUJ-18):** same pack across stacks; per-stack rollups.
- **T9 — Gates + docs (20.T/.C/.L/.CR/.D).**

**Exit:** dry-run zero-exec; assertions embed; MCP read-only; fleet per-stack coverage. **Closure:** standard.
