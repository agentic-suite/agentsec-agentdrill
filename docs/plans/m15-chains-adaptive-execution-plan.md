# agentdrill M15 — Attack Chains & Bounded Adaptive Orchestration Execution Plan

**Spec:** [WBS M15](../wbs/v0.1.0/wbs-v0.1.0-part8-evasion-chains.md#milestone-m15--attack-chains--bounded-adaptive-orchestration) ·
[PRD 16](../../prd/16-attack-chain-orchestration.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **Adaptive orchestration stays inside the dual-use boundary** (RK-2/RK-13); provenance + reviewer + caps enforced.

## Tasks
- **T1 — Chain structure (15.1):** per-step oracles + `chain_oracle` (`expect: chain_broken_before: <step>`); state conditioning (`requires:`).
- **T2 — Break point (15.2):** per-step outcome + `broke_at`; late break is a distinct finding.
- **T3 — Bounded adaptive orchestrator (15.3, F40):** mutate a *documented* pattern; caps (`parent_pattern`, `mutation_summary`, `reviewer`, `max_mutations`, cost ceiling, depth); labeled `adaptive`; excluded from golden-locked comparisons. *RED:* adaptive case without provenance rejected. *GREEN.*
- **T4 — Adaptive determinism (15.4):** pinned attacker model + seed; mutation **path** in the manifest.
- **T5 — Registry review gate (15.5):** an adaptive case entering a shipped pack requires HITL review.
- **T6 — Tests + docs (15.T, 15.D).**

**Exit:** chains run with chain oracles + `broke_at`; adaptive stays in-boundary with provenance/review/caps; deterministic. **Closure:** standard.
