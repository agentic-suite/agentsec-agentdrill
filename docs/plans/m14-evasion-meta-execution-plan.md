# agentdrill M14 — Evasion Pack & Drill-the-Drill Execution Plan

**Spec:** [WBS M14](../wbs/v0.1.0/wbs-v0.1.0-part8-evasion-chains.md#milestone-m14--evasion-pack--drill-the-drill) ·
[design/threat-model](../design/threat-model.md) · [PRD 06](../../prd/06-security-baseline.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **Self-attack is shipped, not optional** (R7); a tamper regression is release-blocking.

## Tasks
- **T1 — Evasion/self-attack pack (14.1):** pack tamper, hook-disable, policy-edit, telemetry-injection, evidence-edit, update-hijack, agent-instructed evasion; each fails closed.
- **T2 — Drill-the-drill (14.2, F43):** adversarial cases vs our own oracles — vacuous no-op must not score blocked; a must-block miss must exit non-zero; fixtures must intercept; attestation/evidence forgery; severity gaming.
- **T3 — Dark holdout (14.3, F33):** unpublished holdout subset in CI; published-green + holdout-red ⇒ pack-gaming finding (release-blocking).
- **T4 — CI cadence (14.4):** evasion + meta + holdout run **every** release cycle; results published.
- **T5 — Hidden adversarial case (14.5):** independent-reviewer-authored secret case.
- **T6 — Tests + docs (14.T, 14.D).**

**Exit:** evasion fails closed; meta catches oracle gaming; holdout catches pack-gaming; cadence enforced. **Closure:** standard.
