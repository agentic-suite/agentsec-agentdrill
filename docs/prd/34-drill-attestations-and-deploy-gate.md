# PRD 34 — Drill Attestations & Deploy Gate

**BLUF:** Proof has value only if others can **consume it mechanically**. Define a standard, signed **drill attestation** — "this exact configuration was drilled with these packs at these tiers on this date, outcomes X, witness coverage Y, known misses Z, valid until T" — as an **in-toto predicate** signed with **Sigstore**, with **freshness/invalidation** semantics, and reference **consumers** (CLI, GitHub Action, K8s admission policy, `agentgate` start-time check, procurement export). agentdrill **never enforces**; the *consumer* does.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F96 · **Reqs:** R70

## Why

- Supply chains solved "prove it was built safely" with attestations (in-toto/SLSA) + admission control; agents need the analogue.
- F35 signs artifacts and F64 verifies, but there is no **typed predicate**, **freshness window**, or **consumer-side verification**.
- AIVSS v0.8 positions scoring as a foundation for underwriting/risk transfer; procurement and insurers want the same machine-consumable proof.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R70** | Produce a signed **drill attestation** (in-toto predicate `agentdrill/drill-result/v1`) bound to a config digest, with freshness/invalidation and reference consumers; mock/fixture attestations are labeled non-evidence. | Verify ≤ 2 s offline; 100% of attestations list non-drilled scope; forged attestations rejected (meta-verification); ≥ 4 reference consumers. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F96** | **Drill attestations & deploy gate**: claim model (subject = config digest, packs@version/hash, tiers/k, outcomes+CIs, witness coverage, `live/fixture/mock`, oracle versions, known misses/waivers by ID, lab version, standards pins, issue/expiry); in-toto predicate + Sigstore + transparency log; **auto-invalidate** on config change / security-deprecated pack / relevant new incident unrun / oracle major bump / waiver expiry; reference consumers | R70 | Consumes F31/F34/F35/F63/F64/F79 and PRD 25/26/29/33 |

## CUJs

### CUJ-46 — Admission gate on freshness
Promote only if a valid attestation exists with witness coverage ≥ 90%, no unwaived critical misses, and age ≤ 30 days. **Success:** stale/invalid → blocked → re-drill.

### CUJ-47 — Underwriter verification
Verify offline that an agent was drilled last week at T1/`Hold@10` with CIs, and see the exclusions. **Success:** verify ≤ 2 s; scope stated.

## Success metrics

| Metric | Target |
|---|---|
| Attestation verify time (offline, typical) | ≤ 2 s |
| Forged/modified attestations rejected (adversarial) | 100% |
| Auto-invalidation latency after config-digest change | ≤ 1 pipeline run / ≤ 5 min |
| Attestations listing non-drilled scope | 100% |
| Mock/fixture attestations accepted by default consumers | **0** |
| Reference consumers shipped (CLI, GH Action, K8s policy, agentgate) | ≥ 4 |
| Independent third-party verifier passing conformance vectors | ≥ 1 within 2 releases |

## Dependencies
F24, F31, F34, F35, F63, F64, F79 · [PRD 25](25-attacker-strength-and-pressure.md), [PRD 26](26-independent-effect-witness.md), [PRD 29](29-bring-your-own-defense.md), [PRD 33](33-exposure-ledger-and-waivers.md), [PRD 42](42-standards-and-claims.md).

## Boundaries & non-goals
- A valid attestation ≠ "secure": the predicate/UI must foreground scope, tier, and limits (claims linter applies).
- Gaming (drilling a weak pack set) → attestation lists the pack set + ASI coverage; consumers may require minimum coverage.
- No enforcement by agentdrill; consumers enforce.

## Open questions
1. Propose the predicate upstream to in-toto (after a design-partner pilot).
2. Do AIUC-1/AICM assessors accept our attestation as evidence? (Interview first.)
