# agentdrill M24 — Attacker Strength, Pressure & Bypass Search Execution Plan

**Spec:** [WBS M24](../wbs/v0.1.0/wbs-v0.1.0-part13-effect-witness-bypass.md) · [design](../design/attacker-strength-and-bypass.md) · [PRD 25](../prd/25-attacker-strength-and-pressure.md), [PRD 28](../prd/28-policy-bypass-search.md).

## Constraints
Every published cell carries tier + k + CI. T3 stays **deferred** (DD-44). Bypass search runs only under RoE, publishes families not payloads. Builds on M23 witnesses.

## Tasks
- **T1 — Tiers (24.1):** T0/T1/T2 (seeded, F40 caps, mutation path in manifest); T3 stub deferred.
- **T2 — Metrics (24.2–24.3):** `Hold@k`/`ASR@k` + bootstrap CI; first-break p50/p95; cost-to-break; pressure curves; claim-scope statement; `brittle`.
- **T3 — `Hold@k` gate (24.4):** configurable (5 PR / 25 nightly). *RED:* `Hold@5<100%` blocks. *GREEN.*
- **T4 — Route families (24.5):** catalogue ≥12 effects × families, reviewed like packs.
- **T5 — Search + minimize + promote (24.6–24.8):** seeded bounded search; delta-debug minimization (≥5×); family dedup; auto-regression (F61); per-effect coverage report. *RED:* seeded-bypass recall ≥95%, false-bypass ≤2%. *GREEN.*
- **T6 — Gates + docs (24.T/.C/.L/.CR/.D).**

**Exit:** tier+k+CI on every cell; ≥90% route-family coverage per P0 effect; confirmed bypass → regression same release; T3 payload leakage = 0. **Closure:** standard.
