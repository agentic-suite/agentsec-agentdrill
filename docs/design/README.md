# agentdrill — Design Documents

Subsystem designs and architecture for agentdrill. Design decisions are centralized in
[design-decisions.md](design-decisions.md) and formalized in the PRD's [Decisions](../prd/11-decisions.md).

> **Status: built (v0.1.0).** These designs describe the shipped subsystem interfaces, written against
the ported mechanics and re-checked as each milestone landed.

| Document | Scope | Status |
|---|---|---|
| [design-decisions.md](design-decisions.md) | Central decision log (DD-01..DD-32) | accepted |
| [architecture-tour.md](architecture-tour.md) | The drill path end to end | built (v0.1.0) |
| [threat-model.md](threat-model.md) | agentdrill's own STRIDE threats + controls | **self-attack surfaces normative (M14)** |
| [threat-test-traceability.md](threat-test-traceability.md) | Threat → control → drill | built (v0.1.0) |
| [data-dictionary.md](data-dictionary.md) | Entities, fields, `.agentdrill/` layout | built (v0.1.0) |
| [pack-format.md](pack-format.md) | Attack-pack schema + validation | built (v0.1.0) |
| [runner.md](runner.md) | Execution spine, artifacts, timeouts | built (v0.1.0) |
| [adapter-contract.md](adapter-contract.md) | Driver + target adapter contract | built (v0.1.0) |
| [oracle-engine.md](oracle-engine.md) | Deterministic/judge/hybrid oracles, dimensions, outcome split | built (v0.1.0) |
| [evidence-integration.md](evidence-integration.md) | agentwatch schema read + expected-telemetry validation | built (v0.1.0) |
| [storage-design.md](storage-design.md) | `.agentdrill/` store, determinism, run manifest | **normative (M8)** |
| [comparison.md](comparison.md) | Golden results, comparison, attribution | **normative (M9)** |
| [reporting.md](reporting.md) | Honest reporter, public benchmark, heat-map | **normative (M10)** |
| [ci-gate.md](ci-gate.md) | Exit codes, gating, trigger/CART, watch, schedule, annotations | **normative (M11)** |
| [killchain.md](killchain.md) | Kill-chain stage model + cessation probe | **normative (M12)** |
| [attack-chains.md](attack-chains.md) | Attack chains, break point, bounded adaptive orchestration | **normative (M15)** |
| [registry.md](registry.md) | Signed pack registry, verified publishers, trust, governance | **normative (M16)** |
| [interop.md](interop.md) | Interop importers, standards tagging, compliance mapping, competitor benchmark | **normative (M17)** |
| [lifecycle.md](lifecycle.md) | Intake, fix-validation, seams, attestation, verifier, privacy, quickstart, pack classes | **normative (M18)** |
| [oracle-credibility.md](oracle-credibility.md) | Oracle versioning, calibration corpus, drift, battery, labels, disputes | **normative (M19)** |
| [frontier-dx.md](frontier-dx.md) | Pack diff/dry-run/templates/CI-matrix/assertions/provenance/MCP/fleet | **normative (M20)** |
| [hardening.md](hardening.md) | NFRs, fault handling, sandbox, audit chain, portability, cost, observability | **normative (M22)** |
| [effect-witness-and-lab.md](effect-witness-and-lab.md) | Effect witnesses, two-oracle verdict, Adversary Lab | **normative (M23)** |
| [attacker-strength-and-bypass.md](attacker-strength-and-bypass.md) | Attacker tiers, Hold@k/ASR@k, pressure curves, bypass search | **normative (M24)** |
| [byod-and-neutral-head-to-head.md](byod-and-neutral-head-to-head.md) | Defense contract/SDK/kit, Defense Zoo, neutral head-to-head, neutrality rules | **normative (M25)** |
| [efficacy.md](efficacy.md) | Unguarded control group, utility-under-attack, cleanup | **normative (M13)** |
| [observability.md](observability.md) | Per-run signals, audit log, run summary | built (v0.1.0) |
| [performance-budget.md](performance-budget.md) | Per-pack budget, throughput, cost | built (v0.1.0) |
| [privacy-data-handling.md](privacy-data-handling.md) | Evidence privacy, redaction receipts, egress | built (v0.1.0) |
| [integrations.md](integrations.md) | SARIF/OTel/OCSF/OSCAL/STIX emitters, imports, SIEM detection validation (M26) | **built (M26)** |
| [backtest-path-intake.md](backtest-path-intake.md) | Trace backtest/shadow, attack-path graph, incident-to-pack compiler (M27) | **built (M27)** |
| [exposure-attestation-roe.md](exposure-attestation-roe.md) | Exposure ledger + waivers, drill attestations, rules of engagement (M28) | **built (M28)** |
| [detonation-breakit-frontier.md](detonation-breakit-frontier.md) | Extension detonation, Break-It program, frontier attack classes (M29) | **built (M29)** |
| [trace-explorer-and-platform-standards.md](trace-explorer-and-platform-standards.md) | Trace explorer, platform matrix (L0–L4), standards/claims (M30) | **built (M30)** |

> **The pack-format contract is normative reference** ([pack-format-spec.md](../reference/pack-format-spec.md));
> [pack-format.md](pack-format.md) is the design record.
> The **agentwatch record + security-event schema** is an external contract (not redefined here) —
> see the [agentwatch reference](https://github.com/agentic-suite/agentsec-agentwatch).
