# PRD 33 — Exposure Ledger & Time-Boxed Waivers

**BLUF:** The CI gate is binary; a gate that can only fail **gets disabled** the first time it blocks a revenue-critical release. Add a **finding lifecycle** and **time-boxed waivers** with owners, due dates, and expiration — with one hard rule: a waiver **annotates, never relabels**. The outcome stays `missed`; reports, heat-maps and public tables still show it; only the *gate impact* may be downgraded. Exports **OSCAL POA&M / assessment-results** and **SARIF suppressions**.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F95 · **Reqs:** R69

## Why

- R3's "the change cannot merge" has no sanctioned alternative → teams disable or bypass the gate.
- Every mature tool (vuln mgmt, BAS, CTEM, SAST) provides finding lifecycle + risk acceptance with expiry.
- Consistency with PRD 14 ("no severity theater"): a waiver must not erase visibility.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R69** | A **findings ledger** with lifecycle and signed **time-boxed waivers** (expiry, compensating control, approval) that never change the outcome label; **known-miss budget** gates releases; OSCAL/SARIF export. | 100% of waivers have expiry; waived misses visible in 100% of reports; expired/drifted waivers auto-reopen (100%); zero expired waivers still suppressing the gate. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F95** | **Exposure ledger & waivers**: lifecycle (`open → triaged → fix-in-progress → fixed → verified-fixed → decayed` + `accepted-risk`/`false-positive`/`wont-fix`); waiver object (scope, tier, reason, drilled compensating control, approvers, expiry default 90 d / critical 30 d, drift trigger, residual risk, auto-reopen); known-miss budget; per-finding **CVSS v4.0 + AIVSS** vector (never aggregated); OSCAL + SARIF exports; ticket sync | R69 | Consumes F41/F61/F44/F32; feeds [PRD 34](34-drill-attestations-and-deploy-gate.md)/[PRD 38](38-security-ecosystem-integrations.md) |

### Invariants (anti-theater)
1. The label stays `missed`; the waiver adds `waived: <id>` — **misses remain visible everywhere**.
2. A waiver may downgrade **gate impact**, never **visibility**.
3. A **known-miss budget** (count + severity-weighted list) gates the release.
4. Waivers are signed, hash-chained, and appear in the verifier (F64) — silent waivers fail verification.
5. Waiving an **integrity** finding (`witness_discrepancy`, `dirty_target`) is **not allowed**.

## CUJs

### CUJ-44 — Sanctioned exception, visible miss
A high-severity miss needs 3 weeks to fix; a 21-day waiver with a drilled compensating control (egress allowlist) is approved; the gate passes; the public table still lists the miss. **Success:** gate green, miss visible, waiver expiring.

### CUJ-45 — It expired
The waiver expires → auto-reopened, ticket re-raised, gate red. **Success:** no silent suppression survives expiry.

## Success metrics

| Metric | Target |
|---|---|
| Gate-disable events per quarter (adopting orgs, opt-in telemetry/survey) | trend → 0; baseline measured |
| Waivers with expiry | 100% |
| Median waiver duration | ≤ 45 days |
| Waivers auto-reopened on expiry/drift | 100% |
| Expired waivers still suppressing the gate | **0** |
| Waived misses visible in published/shared reports | 100% |
| Waivers with a drilled compensating control | ≥ 90% |
| MTTR by severity (critical/high/medium) | ≤ 7 / 30 / 90 days (configurable) |
| Ledger export validates (OSCAL, SARIF) | 100% |

## Dependencies
F32, F41, F44, F61, F64 · [PRD 34](34-drill-attestations-and-deploy-gate.md), [PRD 38](38-security-ecosystem-integrations.md).

## Boundaries & non-goals
- Not a ticketing system (integrates). No composite exposure score.
- Not a rubber stamp: caps, expiry, approver rules, and public visibility.

## Open questions
1. Waiver approval via in-tool RBAC or delegated to the org's GRC (recommend: external-IdP signed approvals the tool verifies).
2. Public benchmark tables carry waivers? (Recommend: no — private-ops concept.)
