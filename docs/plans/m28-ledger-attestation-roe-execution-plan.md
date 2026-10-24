# agentdrill M28 — Exposure Ledger, Attestations & Rules of Engagement Execution Plan

**Spec:** [WBS M28](../wbs/v0.1.0/wbs-v0.1.0-part15-context-governance.md) · [design](../design/exposure-attestation-roe.md) · [PRD 33](../prd/33-exposure-ledger-and-waivers.md), [PRD 34](../prd/34-drill-attestations-and-deploy-gate.md), [PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md).

**Status:** 🚧 In progress (2026-10-24) · **Issues:** #347–#358 · Closes predecessor gaps **G9, G10, G11**.

## Constraints

- **A waiver never relabels a miss:** the label stays `missed`; a waiver adds `waived:<id>`. Gate impact may
  drop, **visibility never**.
- **Integrity findings are not waivable**; an expired/decayed waiver **never suppresses**.
- **A valid attestation ≠ "secure":** scope/tier/limits/WITNESS are always foregrounded; `mock`/`fixture` are
  **non-evidence**; the predicate always lists **what was NOT drilled**.
- **Fail-closed preflight:** zero out-of-scope actions; a case that cannot pass preflight **refuses to fire**.
- One ticket at a time: test **RED** → implement **GREEN** → next. Full suite at milestone end only.

## Prerequisites

- Consumes **M10** (severity/reporting, `RateCI`), **M13** (`efficacy/cleanup` — `dirty_target`,
  `require_clean`), **M18** (`lifecycle` fix validation for `verified_fixed`), **M19** (oracle versions),
  **M5** `attestation.py` (`live|fixture|mock`, `weakest_link`), **M23** (`witness/`), **M26**
  (`integrations/` — OSCAL/SARIF exports, ticket sync), **M11** (`affected_cases`) and **M27** (path status
  `accepted`).
- **This milestone closes the seams M26/M27 reference:** the SARIF `suppressions`/OCSF `Suppressed` waiver
  shape and the path status `accepted` re-point at this ledger.

## Tasks

- **T1 — Finding lifecycle + ledger (28.1, #347).** `open → triaged → fix_in_progress → fixed →
  verified_fixed → decayed` + side states (`accepted_risk`/`false_positive`/`wont_fix`); a per-finding
  CVSS v4.0 + AIVSS vector (**never aggregated**); a miss stays visible.
- **T2 — Time-boxed waivers (28.2, #348).** scope/tier/reason/**drilled compensating control**/approvers/
  **expiry** (90 d; critical 30 d)/drift trigger/residual risk; **annotate, never relabel**; auto-reopen on
  expiry/drift; **known-miss budget**; **integrity findings not waivable**; signed + hash-chained.
- **T3 — Ledger exports (28.3, #349).** OSCAL POA&M / assessment-results; SARIF `suppressions`; ticket-status
  sync. Re-points M26's waiver seam at this ledger.
- **T4 — Drill attestation (28.4, #350).** the claim model (config digest, packs@ver/hash, tiers/k,
  outcomes+CIs, witness coverage, live/fixture/mock, oracle versions, known misses/waivers, lab, standards
  pins, issued/expires); the in-toto `agentdrill/drill-result/v1` predicate; signature + transparency log.
- **T5 — Freshness + consumers (28.5, #351).** auto-invalidate (config change / security-deprecated pack /
  relevant new incident / oracle major / waiver expiry); reference consumers (CLI, GH Action, K8s policy,
  agentgate); models non-evidence.
- **T6 — Rules of engagement (28.6, #352).** signed, versioned RoE (targets+ownership, env class, effect
  classes, canary-only, windows, ceilings, caps, tier ceiling, approvers, contacts, aborts); **fail-closed
  preflight**; per-action **scope receipts**.
- **T7 — Safe-fire interlocks (28.7, #353).** global abort (independent of agenthalt); dead-man switch;
  rate/cost watchdogs; **verified teardown** (`dirty_target` release-blocking, reusing M13); consent gate for
  any attack content leaving the machine.
- **T8 — Gates + docs (28.T #354 · 28.C #355 · 28.L #356 · 28.CR #357 · 28.D #358).** tests; coverage ≥ 95 %;
  `ruff` zero + `mypy --strict` clean; review log; ledger/waiver policy, attestation predicate spec, RoE
  template + safety guide.

## Module ownership (single-writer files)

- New packages `agentdrill/ledger/` (28.1–28.3), `agentdrill/attestations/` (28.4–28.5; plural — the M5
  `attestation.py` module already exists), `agentdrill/roe/` (28.6–28.7) — proposed.
- **Reuse, do not fork:** `efficacy/cleanup` (teardown), `lifecycle` (fix validation), `attestation.py`
  (realness), `integrations` (OSCAL/SARIF/tickets), M10 `RateCI`.
- The **waiver shape** is owned here (single writer); M26's `WaiverRecord` becomes a projection of it.

## Exit criteria

- [ ] All tests pass · coverage ≥ 95 % · `ruff` zero · `mypy --strict` clean · docs linked.
- [ ] Waivers never relabel; the known-miss budget gates; **zero expired waivers suppressing**.
- [ ] The attestation verifies (forgery rejected); freshness/invalidation; ≥ 4 consumers; `mock` = non-evidence.
- [ ] Zero out-of-scope actions; abort ≤ 5 s *(operational)*; teardown clean ≥ 99 %; consent egress zero.

**Closure:** standard (implemented · gates run once · committed · pushed · issue closed · docs updated · checkpoint in the index).
