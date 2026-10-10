# agentdrill — Product Requirements (v0.1.0)

Requirements for **agentdrill** — the continuous adversarial-testing (**proof**) engine for AI-agent
defenses. Part of the [agentsec-ecosystem](https://github.com/agentsec-ecosystem).

> **Status: v0.1.0 proposed (draft, 2026-10-09).** PRDs 00–24 define the **entire v0.1.0 (Wave 0)** release: the
> curated, versioned incident-replay attack packs and the CI proof loop that gates the ecosystem's own
> policies. This folder mirrors the `agentwatch` PRD structure. agentdrill **absorbs the red-team predecessor idea**
> and the eval-harness patterns of the shipped/retired **predecessor eval harness (retained privately)** (see
> [PRD 10](10-feature-parity.md)).

## Documents

| # | Document | Covers |
|---|---|---|
| 00 | [Press Release / FAQ](00-press-release.md) | Working-backwards PR/FAQ |
| 01 | [Why](01-why.md) | Problem, evidence, supersession of the predecessors, non-goals |
| 02 | [Architecture](02-architecture.md) | Composition, the pack→run→prove pipeline, adapters, components, data flow, standards |
| 03 | [Landscape](03-landscape.md) | Existing red-team/eval tooling, whitespace, migration from the predecessor harness |
| 04 | [Users and CUJs](04-users-and-cujs.md) | Personas + critical user journeys (run, gate, reproduce, drill, kill-time, contribute) |
| 05 | [What (Features)](05-features.md) | v0.1.0 P0 (R1–R8), P1 (R9–R11), P2 (R12–R13), feature catalog, non-requirements, compatibility |
| 06 | [Security Baseline](06-security-baseline.md) | Assets, controls, agentdrill's own attack surface (the evasion pack), disclosure |
| 07 | [Success Metrics](07-success-metrics.md) | Outcome metrics, release gate, anti-metrics |
| 08 | [Risks](08-risks.md) | Risk register, hard parts, triggers, open questions |
| 09 | [Roadmap](09-roadmap.md) | Versions, compatibility by version, migration/deprecation |
| 10 | [Feature Parity](10-feature-parity.md) | Every absorbed predecessor capability → delivered / delegated / waived |
| 11 | [Decisions](11-decisions.md) | Accepted decisions (design, scope, technical, governance) |
| 12 | [Traceability](12-traceability.md) | Requirements → CUJ → WBS → test → parity |
| 13 | [Non-Functional Requirements](13-non-functional-requirements.md) | Determinism, reproducibility, performance, portability, security, cost |
| 14 | [Non-Goals](14-non-goals.md) | Consolidated non-goals |
| 15 | [Data Model & Lifecycle](15-data-model.md) | Entities, pack/run/result lifecycle, coverage mapping, invariants |
| 16 | [Attack-Chain Orchestration & Adaptive Boundaries](16-attack-chain-orchestration.md) | Chains as first-class pack structure; bounded adaptive orchestration |
| 17 | [Pack Registry, Signing & Governance](17-pack-registry-and-governance.md) | Semver'd signed packs, contribution flow, deprecation/takedown |
| 18 | [Kill-Chain Verification & Kill-Time](18-kill-chain-verification.md) | Stage timestamps, `ceased` probing, kill-chain timeline findings |
| 19 | [Detection Validation & BAS-Class Features](19-detection-validation-bas.md) | Cleanup, expected-telemetry validation, utility-under-attack, heat-maps, bootstrap CIs, PR submission |
| 20 | [Efficacy, Freshness & Lifecycle](20-efficacy-freshness-lifecycle.md) | Unguarded control group, incident intake, fix validation, seams, attestation, verifier, quickstart |
| 21 | [Pack Catalog](21-pack-catalog.md) | The 7 v0.1.0 packs (3 absorbed from the predecessor harness, re-pointed) + pack roadmap |
| 22 | [Frontier & DX Features](22-frontier-dx-features.md) | Pack diff/selection, watch, dry-run, templates, schedules, CI export, assertions, MCP surface, budget versioning, frontier pack classes |
| 23 | [Oracle Credibility](23-oracle-credibility.md) | Oracle versioning, calibration corpus, judge drift, meta-eval, adjudication, honesty labels |
| 24 | [Predecessor Gap Closure](24-predecessor-gap-closure.md) | Every predecessor-acknowledged gap (G1–G14) → closed or waived at the foundation |

## Reviewers start here

1. **Scope:** does [PRD 05](05-features.md) define the right v0.1.0 (incident-replay packs + CI gate + honest public results, against the deployed stack)?
2. **Journeys:** is [PRD 04](04-users-and-cujs.md) CUJ-1..27 the right set?
3. **Composition:** is the "drill the deployed stack, don't simulate" stance in [PRD 02](02-architecture.md) correctly drawn (agentdrill owns **no** enforcement)?
4. **Honesty:** do [PRD 05](05-features.md) R5 and [PRD 07](07-success-metrics.md) make **misses** a first-class output?
5. **Parity:** every absorbed capability from the red-team predecessor idea and predecessor eval harness (retained privately) is delivered / delegated / waived in [PRD 10](10-feature-parity.md).

## Sources

- Ecosystem PRD 09 (agentdrill, #218) — requirements R1–R13, harness-compatibility mandate, non-goals,
  standards. Public home: [agentsec-ecosystem](https://github.com/agentsec-ecosystem) docs.
- Predecessor eval harness (retired, retained privately): its PRD, spec, architecture, scoring, scenarios, CI, and
  lessons-learned docs — all absorbed into this PRD set (see [PRD 10](10-feature-parity.md),
  [PRD 21](21-pack-catalog.md)) and the agentdrill design docs.
- Incident register and evidence citations: primary sources cited inline (AgentDojo, InjecAgent, Invariant,
  PromptArmor, Anthropic threat-intel, The Register / Help Net Security for Plugin4Shell).
