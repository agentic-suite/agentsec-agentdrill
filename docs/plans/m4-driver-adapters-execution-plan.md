# agentdrill M4 — Driver Adapters Execution Plan

**Spec:** [WBS M4](../wbs/v0.1.0/wbs-v0.1.0-part3-drivers-targets.md#milestone-m4--driver-adapters) ·
[adapter-contract](../design/adapter-contract.md) · [reference/adapter-api](../reference/adapter-api.md).

## Global constraints

- Exit gate: suite green · coverage ≥95% · `ruff` zero · `mypy --strict` clean.
- **No ground-truth leakage** — the driver payload never carries `oracle`/`expect`/thresholds (ADR-0005).
- One ticket at a time: test RED → GREEN → next.

## Tasks

### T1 — Adapter base + contract (4.1)
`Driver` ABC (`run` → `RunArtifact`; implement `_invoke`); payload builder strips evaluation fields; error
normalization. **RED** → a leakage guard test asserting the payload has no `oracle`/`expect` → **GREEN**.

### T2 — `subprocess` driver (4.2)
stdin JSON → stdout envelope; raw-text fallback unless `strict_output`; logs to stderr; timeout/crash.
**RED** → envelope + fallback + timeout tests → **GREEN**.

### T3 — `python` driver (4.3)
Import module, call `run(payload)`; hard timeout in a separate process. **RED** hung-callable test → **GREEN**.

### T4 — `http` driver (4.4)
POST payload; normalize connection/timeout/non-200.

### T5 — Per-harness drivers (4.5)
`claude-code` and `cursor` drivers delivering through the harness surface (≥2 Tier-1).

### T6 — Registry + plugin discovery (4.6)
`ADAPTERS` registry + entry points; unknown → `ConfigError`; `AdapterManifest` + SHA-256 digest.

### T7 — Tests + docs (4.T, 4.D).

**Exit:** subprocess/python/http + ≥2 Tier-1 drivers run a pack end to end; leakage guard passes for every
driver. **Closure:** implemented · gates once · committed · pushed · issue closed · docs · checkpoint.
