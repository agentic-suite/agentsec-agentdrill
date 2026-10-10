# agentdrill — Design Documents

Subsystem designs and architecture for agentdrill. Design decisions are centralized in
[design-decisions.md](design-decisions.md) and formalized in the PRD's [Decisions](../prd/11-decisions.md).

> **Status: design intent.** agentdrill is pre-build (v0.1.0 planned). These designs describe the intended
> subsystem interfaces so M0's port re-points existing mechanics instead of spawning parallel
> implementations. They are rewritten against reality at M23–M24.

| Document | Scope | Status |
|---|---|---|
| [design-decisions.md](design-decisions.md) | Central decision log (DD-01..DD-32) | accepted |
| [architecture-tour.md](architecture-tour.md) | The drill path end to end | design intent |
| [threat-model.md](threat-model.md) | agentdrill's own STRIDE threats + controls | design intent |
| [threat-test-traceability.md](threat-test-traceability.md) | Threat → control → drill | design intent |
| [data-dictionary.md](data-dictionary.md) | Entities, fields, `.agentdrill/` layout | design intent |
| [pack-format.md](pack-format.md) | Attack-pack schema + validation | design intent |
| [runner.md](runner.md) | Execution spine, artifacts, timeouts | design intent |
| [adapter-contract.md](adapter-contract.md) | Driver + target adapter contract | design intent |
| [oracle-engine.md](oracle-engine.md) | Deterministic/judge/hybrid oracles, dimensions, outcome split | design intent |
| [evidence-integration.md](evidence-integration.md) | agentwatch schema read + expected-telemetry validation | design intent |
| [storage-design.md](storage-design.md) | `.agentdrill/` store, determinism, run manifest | design intent |
| [comparison.md](comparison.md) | Golden results, comparison, attribution | design intent |
| [reporting.md](reporting.md) | Honest reporter, public benchmark, heat-map | design intent |
| [ci-gate.md](ci-gate.md) | Exit codes, gating, trigger/CART | design intent |
| [killchain.md](killchain.md) | Kill-chain stage model + cessation probe | design intent |
| [efficacy.md](efficacy.md) | Unguarded control group, utility-under-attack, cleanup | design intent |
| [observability.md](observability.md) | Per-run signals, audit log, run summary | design intent |
| [performance-budget.md](performance-budget.md) | Per-pack budget, throughput, cost | design intent |
| [privacy-data-handling.md](privacy-data-handling.md) | Evidence privacy, redaction receipts, egress | design intent |

> **The pack-format contract is normative reference.** Once implementation lands it moves to
> `docs/reference/pack-format-spec.md`; until then [pack-format.md](pack-format.md) is the draft contract.
> The **agentwatch record + security-event schema** is an external contract (not redefined here) —
> see the [agentwatch reference](https://github.com/agentsec-ecosystem/agentwatch).
