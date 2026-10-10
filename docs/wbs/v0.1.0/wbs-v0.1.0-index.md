# WBS — agentdrill v0.1.0 (Index)

**BLUF:** **M0 is a bulk port of the entire predecessor eval-harness codebase** (urgent — it makes
agentdrill self-contained; the predecessor repo is retained and made private, never deleted). After the
port, v0.1.0 delivers the **entire PRD scope** — the proof engine (attack packs, runner, driver/target
adapters, oracle engine, evidence, honest benchmark), the trust layer (efficacy control, kill-chain
verification, oracle credibility), the BAS/detection-validation features, chains + bounded adaptive
orchestration, the pack registry, interop + standards, the lifecycle features, and absorption + gap
closure. **Twenty-five milestones (M0–M24)** across **thirteen detail files (2 milestones per file)**.

## Standard milestone exit criteria (applies to EVERY milestone)

- [ ] **All tests pass** (`make test`) — the milestone's `.T` work item
- [ ] **Code coverage ≥ 95%** (enforced in CI) — the `.C` work item
- [ ] **Lint strict clean** — `ruff` zero violations; `mypy --strict` clean — the `.L` work item
- [ ] **Code review complete** — findings recorded in [codereview-log.md](codereview-log.md), all resolved — the `.CR` work item
- [ ] **Design docs updated** (milestone-specific list in each file) — the `.D` work item
- [ ] **Traceability updated** — the [PRD 12](../../prd/12-traceability.md) requirement → test row moves with the work
- [ ] **Port / absorption / gap items complete** — each milestone frontloads its predecessor-port tasks and its [PRD 24](../../prd/24-predecessor-gap-closure.md) items

> Every milestone therefore carries five standing gate work items — **`.T` tests · `.C` coverage · `.L` lint/types ·
> `.CR` code review · `.D` docs** — in addition to its implementation items.

## Standard milestone closure (applies to EVERY milestone)

A milestone is **closed** only when all of these hold (mirrors agentwatch's closure model + the org
definition of done):

1. **Implemented** — every work item done; no "core slice", no partials.
2. **Tests green** — the milestone's tests pass, and the standard gates run **once at milestone end**
   (full suite, coverage ≥95%, `ruff`, `mypy --strict`) — not per ticket.
3. **Committed & pushed** — the work is on the feature branch, pushed.
4. **Tracking issue closed** — or explicitly commented with status.
5. **Docs updated** — the milestone's design/reference docs updated and linked from this WBS.
6. **Checkpoint recorded** — a dated line appended to the Progress section below (commit refs + gate result).
7. **Field tests (M23) and release readiness (M24) are milestones**, not cleanup — **M24 tags `v0.1.0`**.

> **One ticket at a time:** per work item, write the test first (RED) → implement (GREEN) → next. Do **not**
> run the full suite between tickets; run it at milestone end only.

## Milestones

| M | Name | Detail file |
|---|---|---|
| **M0** | **Port the predecessor codebase** (urgent) | [Part 1](wbs-v0.1.0-part1-port-foundation.md#milestone-m0--port-the-predecessor-codebase) |
| M1 | Foundation & identity | [Part 1](wbs-v0.1.0-part1-port-foundation.md#milestone-m1--foundation--identity) |
| M2 | Pack format, loader & validation | [Part 2](wbs-v0.1.0-part2-packs-runner.md#milestone-m2--pack-format-loader--validation) |
| M3 | Runner & execution spine | [Part 2](wbs-v0.1.0-part2-packs-runner.md#milestone-m3--runner--execution-spine) |
| M4 | Driver adapters | [Part 3](wbs-v0.1.0-part3-drivers-targets.md#milestone-m4--driver-adapters) |
| M5 | Target adapters & recon/scoping | [Part 3](wbs-v0.1.0-part3-drivers-targets.md#milestone-m5--target-adapters--reconscoping) |
| M6 | Oracle engine | [Part 4](wbs-v0.1.0-part4-oracles-evidence.md#milestone-m6--oracle-engine) |
| M7 | Evidence integration | [Part 4](wbs-v0.1.0-part4-oracles-evidence.md#milestone-m7--evidence-integration) |
| M8 | Determinism — fixtures, manifest & pins | [Part 5](wbs-v0.1.0-part5-determinism-comparison.md#milestone-m8--determinism--fixtures-manifest--pins) |
| M9 | Golden results, comparison & attribution | [Part 5](wbs-v0.1.0-part5-determinism-comparison.md#milestone-m9--golden-results-comparison--attribution) |
| M10 | Honest reporter & public benchmark | [Part 6](wbs-v0.1.0-part6-benchmark-ci.md#milestone-m10--honest-reporter--public-benchmark) |
| M11 | CI gate, trigger/CART & local loop | [Part 6](wbs-v0.1.0-part6-benchmark-ci.md#milestone-m11--ci-gate-triggercart--local-loop) |
| M12 | Kill-time & kill-chain verification | [Part 7](wbs-v0.1.0-part7-killchain-efficacy.md#milestone-m12--kill-time--kill-chain-verification) |
| M13 | Efficacy control & utility-under-attack | [Part 7](wbs-v0.1.0-part7-killchain-efficacy.md#milestone-m13--efficacy-control--utility-under-attack) |
| M14 | Evasion pack & drill-the-drill | [Part 8](wbs-v0.1.0-part8-evasion-chains.md#milestone-m14--evasion-pack--drill-the-drill) |
| M15 | Attack chains & bounded adaptive orchestration | [Part 8](wbs-v0.1.0-part8-evasion-chains.md#milestone-m15--attack-chains--bounded-adaptive-orchestration) |
| M16 | Pack registry, signing & governance | [Part 9](wbs-v0.1.0-part9-registry-interop.md#milestone-m16--pack-registry-signing--governance) |
| M17 | Interop, standards tagging & compliance | [Part 9](wbs-v0.1.0-part9-registry-interop.md#milestone-m17--interop-standards-tagging--compliance) |
| M18 | Lifecycle — intake, fix-validation, seams, attestation, verifier, quickstart | [Part 10](wbs-v0.1.0-part10-lifecycle-oracle.md#milestone-m18--lifecycle--intake-fix-validation-seams-attestation-verifier-quickstart) |
| M19 | Oracle credibility | [Part 10](wbs-v0.1.0-part10-lifecycle-oracle.md#milestone-m19--oracle-credibility) |
| M20 | Frontier & DX | [Part 11](wbs-v0.1.0-part11-dx-absorption.md#milestone-m20--frontier--dx) |
| M21 | Predecessor absorption & gap closure | [Part 11](wbs-v0.1.0-part11-dx-absorption.md#milestone-m21--predecessor-absorption--gap-closure) |
| M22 | NFRs, security hardening & resilience | [Part 12](wbs-v0.1.0-part12-hardening-fieldtest.md#milestone-m22--nfrs-security-hardening--resilience) |
| **M23** | **Field tests** | [Part 12](wbs-v0.1.0-part12-hardening-fieldtest.md#milestone-m23--field-tests) |
| **M24** | **Release readiness** | [Part 13](wbs-v0.1.0-part13-release.md#milestone-m24--release-readiness) |

## Progress

**🚧 M0–M24 not started.** Design complete ([PRD 00–24](../../prd/README.md)). As milestones close, dated
checkpoints (commit refs + gate result) are appended here — matching agentwatch's per-milestone checkpoints.

## Porting map (predecessor → agentdrill)

Source: the predecessor eval harness (`docs/PRD.md`, `docs/spec.md`, `docs/architecture.md`, scoring,
scenarios, CI, lessons) — **MIT; retired, retained privately, never deleted**. The port is a **bulk move
(M0)**; later milestones re-point the mechanics from *agent-quality grading* to *defense proof*.

| Shipped artifact | Ported at |
|---|---|
| Entire repo tree (`src/`, `tests/`, `scenarios/`, tooling, packaging, docs subset) | **M0** |
| Scenario-pack format; adapter contract; runner; trajectory capture | M0 → re-pointed M2–M4 |
| Deterministic + judge + hybrid scoring engine | M0 → re-pointed M6 |
| Fixture system / ToolStub; run manifest | M0 → re-pointed M8 |
| Baselines + comparison engine; report generation; CI exit codes | M0 → re-pointed M9–M11 |
| Sandbox / trust / audit / sanitization | M0 → re-pointed M16, M22 |
| Plugin registry (custom scorers/adapters) | M0 → re-pointed M4, M6 |
| Launch + security + adversarial packs | M0 → re-pointed M2, M14 |

> **Predecessor retention:** once M0 lands (code fully represented, ported suite green), agentdrill is
> self-contained; the predecessor is **made private and retained at M24 — never deleted**.

## PRD coverage matrix (every doc 00–24)

| PRD | Topic | Milestone(s) |
|---|---|---|
| **PRD 00** | Press Release / FAQ | narrative; validated at M24 |
| **PRD 01** | Why | context (all milestones) |
| **PRD 02** | Architecture | M0–M12 |
| **PRD 03** | Landscape / migration / predecessor (private) | M0, M21 |
| **PRD 04** | Users & CUJs (CUJ-1..24) | M2–M20 |
| **PRD 05** | What (Features) R1–R52 | M2–M22 |
| **PRD 06** | Security baseline / own threat model | M14, M22 |
| **PRD 07** | Success metrics / release gate | M10, M23, M24 |
| **PRD 08** | Risks (RK-1..RK-16) | cross-cutting; M22 |
| **PRD 09** | Roadmap | M24 |
| **PRD 10** | Feature parity (absorption ledger) | M0–M20; gate M21, M24 |
| **PRD 11** | Decisions DD-01..DD-32 | cross-cutting (honored every milestone) |
| **PRD 12** | Traceability (maintained) | every milestone |
| **PRD 13** | Non-Functional Requirements | M22 |
| **PRD 14** | Non-goals (scope guard) | every milestone |
| **PRD 15** | Data model + lifecycle | M2, M9 |
| **PRD 16** | Attack-chain orchestration | M15 |
| **PRD 17** | Pack registry, signing & governance | M16 |
| **PRD 18** | Kill-chain verification & kill-time | M12 |
| **PRD 19** | Detection validation & BAS-class | M13 |
| **PRD 20** | Efficacy, freshness & lifecycle | M13, M18 |
| **PRD 21** | Pack catalog | M2, M14, M18 |
| **PRD 22** | Frontier & DX features | M11, M20 |
| **PRD 23** | Oracle credibility | M19 |
| **PRD 24** | Predecessor gap closure | M21 |

## Requirements detail (R1–R58)

| Req | Milestone(s) |
|---|---|
| R1 incident-replay packs | M2 |
| R2 run vs. deployed stack | M5 |
| R3 CI gate on policy PRs | M11 |
| R4 public reproducible benchmark | M10 |
| R5 honest reporting (misses) | M6, M10 |
| R6 determinism | M8 |
| R7 evasion pack | M14 |
| R8 kill-time | M12 |
| R9 interop import | M17 |
| R10 ATLAS/OWASP tagging | M17 |
| R11 community pack flow | M16 |
| R12–R13 competitor benchmark / fuzzing | M17, M20 |
| R14–R18 chains / MCP packs / memory packs / mutation / closes-the-loop | M15, M18, M18, M15, M18 |
| R19–R21 statistical rigor / contamination / adjudication | M10 |
| R22–R25 defense contracts / kill-chain timing / attribution / severity | M7, M12, M9, M10 |
| R26–R32 BAS-class (cleanup, utility, telemetry, heat-map, profiles, CIs, traces, PR-submit) | M13 |
| R33–R40 efficacy / freshness / lifecycle | M13, M18 |
| R41–R52 frontier & DX | M20 |
| R53–R58 oracle credibility | M19 |

Full feature→requirement→test mapping: [PRD 05](../../prd/05-features.md) · [PRD 12](../../prd/12-traceability.md).

## CUJs (PRD 04)

CUJ-1 run pack → M5 · CUJ-2 gate PR → M11 · CUJ-3 reproduce benchmark → M10 · CUJ-4 drill incident → M2 ·
CUJ-5 kill-time → M12 · CUJ-6 evasion pack → M14 · CUJ-7 contribute/import → M17 · CUJ-8 close the loop →
M18 · CUJ-9 trend → M10 · CUJ-10 coverage → M10 · CUJ-11 offline bundle → M18 · CUJ-12 trigger re-drill →
M11 · CUJ-13 dispute → M19 · CUJ-14 attribute → M9 · CUJ-15 defense contract → M7 · CUJ-16 kill-chain →
M12 · CUJ-17 HITL → M19 · CUJ-18 fleet → M20 · CUJ-19 efficacy → M13 · CUJ-20 intake → M18 · CUJ-21 fix
holds → M18 · CUJ-22 seams → M18 · CUJ-23 verify standalone → M18 · CUJ-24 quickstart → M18 ·
CUJ-25 check the instrument → M19 · CUJ-26 run my oracle against the corpus → M19 · CUJ-27 schedule a
drill for a live adversary → M18.

## Decisions (PRD 11)

DD-01..DD-32 are honored across milestones (e.g., DD-01 no-enforcement → all; DD-05 agentwatch schema →
M7; DD-18 pins/manifest → M8; DD-20 untrusted packs → M16; DD-27 multi-seed → M10; DD-29 dark holdout →
M14).

## v0.1.0 release gate (all milestones)

- [ ] M0–M24 exit criteria satisfied (incl. absorption + gap closure + design docs)
- [ ] Full PRD coverage delivered + tested; every R1–R58 demonstrated by an acceptance test
- [ ] The CI gate rejects an un-blocking policy change; the published benchmark reproduces; misses included
- [ ] NFRs met; fail-closed on tamper; untrusted packs sandboxed
- [ ] Field tests pass (M23); security audit + compliance matrix + release notes published (M24)
- [ ] SBOM + signed artifacts; OpenSSF Scorecard grade recorded
- [ ] **Predecessor repository retained and made private (not deleted)**

Review log: [codereview-log.md](codereview-log.md).
