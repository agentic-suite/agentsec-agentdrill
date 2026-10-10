# agentdrill M2+M3 — Packs & Runner Execution Plan

**Spec:** [WBS M2](../wbs/v0.1.0/wbs-v0.1.0-part2-packs-runner.md#milestone-m2--pack-format-loader--validation) ·
[WBS M3](../wbs/v0.1.0/wbs-v0.1.0-part2-packs-runner.md#milestone-m3--runner--execution-spine) ·
[design/pack-format](../design/pack-format.md) · [design/runner](../design/runner.md) ·
[PRD 15](../prd/15-data-model.md) · [PRD 21](../prd/21-pack-catalog.md).

## Global constraints

- Exit gate: suite green · coverage ≥95% · `ruff` zero · `mypy --strict` clean.
- **Path-safety invariant:** `^[a-zA-Z0-9_-]+$` enforced before any path use (closes predecessor G3).
- **No silent pass:** unknown oracle/target/driver → `ConfigError` (exit 2).
- One ticket at a time: test **RED** → implement **GREEN** → next. Full suite at milestone end only.

---

## M2

### Task 1 — Pack schema (2.1)
Versioned `pack` + `cases[]` Pydantic models; JSON round-trip. **RED** round-trip test → **GREEN**.

### Task 2 — Loader + strict validation (2.2)
YAML primary/JSON secondary; duplicate-id, missing-field, incoherent-budget; oracle resolution; threshold
ranges; **path-safety**. **RED** malformed/traversal tests → **GREEN**.

### Task 3 — Resolution at load (2.3)
Resolve oracle/target/driver from the registry; unknown → `ConfigError`. **RED** unknown-ref test → **GREEN**.

### Task 4 — Validate + list (2.4)
`validate --strict [--pre-flight]`; `list packs/cases --tag/--target/--difficulty`.

### Task 5 — Catalog (2.5)
Author `quickstart-demo`, `incidents-core`, `incidents-security`, `kill-chain`; each reproduces its pattern.

### Task 6 — Fixtures + twin hooks (2.6) · Task 7 — Metadata & hashing (2.7)
Deterministic fixtures + `benign_twin` linkage; SHA-256 pack hashing + license/trust fields.

### Task 8 — Tests + docs (2.T, 2.D).

---

## M3

### Task 1 — Run model + artifact (3.1)
`TrajectoryStep`/`Cost`/`RunArtifact`; JSON round-trip. **RED** → **GREEN**.

### Task 2 — `run_one`/`run_all` (3.2)
Pack execution; `--tags` filter; write `.agentdrill/runs/<id>/`.

### Task 3 — Timeout + isolation (3.3) · Task 4 — Error capture / non-abort (3.4)
**RED** hung-case and failing-case tests → **GREEN** (a case failure never aborts the pack).

### Task 5 — Parallel + backpressure (3.5)
`--workers` + `--max-outstanding`; parallel == serial, order preserved.

### Task 6 — Budget governor (3.6)
Per-case budget + `--max-cost`; exceed ⇒ `aborted: cost_exceeded`, reported.

### Task 7 — Tests + docs (3.T, 3.D).
