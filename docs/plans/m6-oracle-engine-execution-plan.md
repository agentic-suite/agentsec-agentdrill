# agentdrill M6 — Oracle Engine Execution Plan

**Spec:** [WBS M6](../wbs/v0.1.0/wbs-v0.1.0-part4-oracles-evidence.md#milestone-m6--oracle-engine) ·
[design/oracle-engine](../design/oracle-engine.md).

## Global constraints

- Exit gate: suite green · coverage ≥95% · lint strict clean.
- **Deterministic first; judge only where needed** (ADR-0006); divergences flagged, not averaged.
- Unknown oracle → `ConfigError` at load.

## Tasks

### T1 — Oracle base + registry (6.1)
`Oracle` ABC + `@register_oracle` + entry-point discovery; `kind` deterministic|judge|hybrid.

### T2 — Deterministic oracles (6.2)
deny/allowed, confinement, budget, sequence, grounding. **RED** → reproducible-verdict tests → **GREEN**.

### T3 — Judge oracles (6.3)
Qualitative cases; judge client (OpenAI/Anthropic/Ollama/MLX/mock); `temperature=0`; `{score, rationale}`.

### T4 — Hybrid + offline safety (6.4)
Deterministic gate always runs; missing judge → gate result + `judge_not_evaluated: true`.

### T5 — Dimensions + outcome split (6.5)
`compatibility`/`enforcement`/`integrity`; `blocked`/`missed`/`degraded`; hierarchy enforcement > integrity >
efficiency.

### T6 — Divergence + failure taxonomy (6.6)
`critical`/`warning` divergences; taxonomy (`safety_miss`, `policy_miss`, `evidence_gap`, `kill_slow`, …);
`--fail-on-divergence`.

### T7 — Defense contracts (6.7)
Each Wave-0 enforcer ships a required minimal pack gating its own release (R22, CUJ-15).

### T8 — Tests + docs (6.T, 6.D).

**Exit:** every case resolves to blocked/missed/degraded with dimensions; offline never skips enforcement;
defense contracts run. **Closure:** standard.
