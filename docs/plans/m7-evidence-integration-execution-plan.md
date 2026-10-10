# agentdrill M7 — Evidence Integration Execution Plan

**Spec:** [WBS M7](../wbs/v0.1.0/wbs-v0.1.0-part4-oracles-evidence.md#milestone-m7--evidence-integration) ·
[design/evidence-integration](../design/evidence-integration.md).

## Global Constraints

- Exit gate: suite green · coverage ≥95% · lint strict clean.
- **Reuse the agentwatch schema** (ADR-0004) — consume, never fork.
- **Evidence binding is mandatory:** no result without evidence or an explicit `evidence_gap`.

## Tasks

### T1 — agentwatch schema reader (7.1)
Parse records + events (`denied`, `policy-fired`, `secret-detected`, `revoked`, `halted`). **RED** → fixture
parse test → **GREEN**.

### T2 — Evidence binding (7.2)
Every result references its evidence; missing ⇒ `evidence_gap` finding.

### T3 — Expected-telemetry validation (7.3, F52)
Cases declare `expect_telemetry`; `blocked` without it ⇒ `telemetry_gap`. **RED** → blocked-without-event test
→ **GREEN**.

### T4 — Evidence in artifacts (7.4)
Evidence refs written into `artifacts/<case_id>.json`.

### T5 — Coverage reconciliation (7.5, F26)
Consume the agentwatch inventory; report exercised vs. unexercised; `gap:unexplained` = 0.

### T6 — Tests + docs (7.T, 7.D).

**Exit:** every result evidence-bound; blocked-without-event flagged; coverage reconciliation reaches
`gap:unexplained = 0`. **Closure:** standard.
