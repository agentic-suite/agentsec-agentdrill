# agentdrill M13 — Efficacy Control & Utility-Under-Attack Execution Plan

**Spec:** [WBS M13](../wbs/v0.1.0/wbs-v0.1.0-part7-killchain-efficacy.md#milestone-m13--efficacy-control--utility-under-attack) ·
[design/efficacy](../design/efficacy.md) · [PRD 20](../prd/20-efficacy-freshness-lifecycle.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **A `blocked` number is meaningless unless the attack succeeds unguarded** (ADR-0007). A dirty target blocks release.

## Tasks
- **T1 — Efficacy run (13.1, F59):** each case vs an **unguarded twin**; efficacy-verified only if it succeeds unguarded. *RED:* enforced-without-unguarded-success fails. *GREEN.*
- **T2 — Inert flagging (13.2):** unguarded failure ⇒ `attack_inert`; excluded from rates; never pads a green table.
- **T3 — Utility-under-attack (13.3, F51):** `benign_twin`; publish benign utility + utility-under-attack + enforcement rate; `utility_cost` finding.
- **T4 — Per-case cleanup (13.4, F50):** runs after every case (incl. failed/timeout); failure ⇒ release-blocking `dirty_target`.
- **T5 — Efficacy report (13.5):** efficacy status per case in the evidence bundle.
- **T6 — Tests + docs (13.T, 13.D).**

**Exit:** every enforcement rate efficacy-backed; inert excluded; utility price tag on every block; cleanup failure blocks release. **Closure:** standard.
