# agentdrill — Design Documents

Subsystem designs and architecture for agentdrill. Design decisions are centralized in
[design-decisions.md](design-decisions.md) and formalized in the PRD's [Decisions](../prd/11-decisions.md).

> **Status: design intent.** agentdrill is pre-build (v0.1.0 planned). These designs describe the intended
> subsystem interfaces so M0's port re-points existing mechanics instead of spawning parallel
> implementations. They are rewritten against reality at M31–M32.

| Document | Scope | Status |
|---|---|---|
| [design-decisions.md](design-decisions.md) | Central decision log (DD-01..DD-32) | accepted |
| [architecture-tour.md](architecture-tour.md) | The drill path end to end | design intent |
| [threat-model.md](threat-model.md) | agentdrill's own STRIDE threats + controls | **self-attack surfaces normative (M14)** |
| [threat-test-traceability.md](threat-test-traceability.md) | Threat → control → drill | design intent |
| [data-dictionary.md](data-dictionary.md) | Entities, fields, `.agentdrill/` layout | design intent |
| [pack-format.md](pack-format.md) | Attack-pack schema + validation | design intent |
| [runner.md](runner.md) | Execution spine, artifacts, timeouts | design intent |
| [adapter-contract.md](adapter-contract.md) | Driver + target adapter contract | design intent |
| [oracle-engine.md](oracle-engine.md) | Deterministic/judge/hybrid oracles, dimensions, outcome split | design intent || [evidence-integration.md](evidence-integration.md) | agentwatch schema read + expected-telemetry validation | design intent |
| [storage-design.md](storage-design.md) | `.agentdrill/` store, determinism, run manifest | **normative (M8)** |
| [comparison.md](comparison.md) | Golden results, comparison, attribution | **normative (M9)** |
| [reporting.md](reporting.md) | Honest reporter, public benchmark, heat-map | **normative (M10)** |
| [ci-gate.md](ci-gate.md) | Exit codes, gating, trigger/CART, watch, schedule, annotations | **normative (M11)** |
| [killchain.md](killchain.md) | Kill-chain stage model + cessation probe | **normative (M12)** |
| [attack-chains.md](attack-chains.md) | Attack chains, break point, bounded adaptive orchestration | **normative (M15)** |
| [registry.md](registry.md) | Signed pack registry, verified publishers, trust, governance | **normative (M16)** |
| [interop.md](interop.md) | Interop importers, standards tagging, compliance mapping, competitor benchmark | **normative (M17)** |
| [lifecycle.md](lifecycle.md) | Intake, fix-validation, seams, attestation, verifier, privacy, quickstart, pack classes | **normative (M18)** |
| [efficacy.md](efficacy.md) | Unguarded control group, utility-under-attack, cleanup | **normative (M13)** |
| [observability.md](observability.md) | Per-run signals, audit log, run summary | design intent |
| [performance-budget.md](performance-budget.md) | Per-pack budget, throughput, cost | design intent |
| [privacy-data-handling.md](privacy-data-handling.md) | Evidence privacy, redaction receipts, egress | design intent |
| [effect-witness-and-lab.md](effect-witness-and-lab.md) | Independent effect witness + adversary lab (M23) | design intent |
| [attacker-strength-and-bypass.md](attacker-strength-and-bypass.md) | Attacker tiers, `Hold@k`, pressure curves, route-family bypass search (M24) | design intent |
| [byod-and-neutral-head-to-head.md](byod-and-neutral-head-to-head.md) | Defense contract/SDK/kit, Defense Zoo, neutrality rules (M25) | design intent |
| [integrations.md](integrations.md) | SARIF/OTel/OCSF/OSCAL/STIX emitters, imports, SIEM detection validation (M26) | design intent |
| [backtest-path-intake.md](backtest-path-intake.md) | Trace backtest/shadow, attack-path graph, incident-to-pack compiler (M27) | design intent |
| [exposure-attestation-roe.md](exposure-attestation-roe.md) | Exposure ledger + waivers, drill attestations, rules of engagement (M28) | design intent |
| [detonation-breakit-frontier.md](detonation-breakit-frontier.md) | Extension detonation, Break-It program, frontier attack classes (M29) | design intent |
| [trace-explorer-and-platform-standards.md](trace-explorer-and-platform-standards.md) | Trace explorer, platform matrix (L0–L4), standards/claims (M30) | design intent |

> **The pack-format contract is normative reference.** Once implementation lands it moves to
> `docs/reference/pack-format-spec.md`; until then [pack-format.md](pack-format.md) is the draft contract.
> The **agentwatch record + security-event schema** is an external contract (not redefined here) —
> see the [agentwatch reference](https://github.com/agentic-suite/agentsec-agentwatch).
