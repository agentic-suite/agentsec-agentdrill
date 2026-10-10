# PRD 37 — Break-It Program (Crowd Bypass Intake & Coordinated Disclosure)

**BLUF:** The strongest agent-robustness evidence comes from **crowds** (Gray Swan × UK AISI: ~1.8M attacks; CAISI follow-up: every frontier model broken, universal transferable attacks). Scripted packs capture *known* incidents; humans find *novel bypasses*. Add a **Break-It program**: pinned reference ranges, structured **proof-of-bypass** submissions auto-verified by the [PRD 26](26-independent-effect-witness.md) witness, triage/severity SLAs, coordinated disclosure with a CVE/CNA path, rewards, and conversion of accepted bypasses into permanent regressions. Start as a pilot.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F99 · **Reqs:** R73 · **Priority:** P2 pilot (after PRD 25/26/35)

## Why

- Crowd results (E3/E4) revealed novel bypasses and **universal, transferable** attacks that scripted packs never generate.
- F60 handles *documented incidents*; F32 handles *disputes* about published results — neither is a **safe channel for a novel bypass**.
- Without a channel, finders sit on bypasses, disclose irresponsibly, or don't bother.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R73** | A **Break-It program** (pilot) invites structured bypass submissions against pinned reference ranges, auto-verifies via the witness, triages with SLAs, discloses coordinately, and converts accepted bypasses into regressions. | ≥ 80% submissions auto-verified; acknowledgement ≤ 24 h; accepted bypass → regression within a release (100%); zero embargo breaches. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F99** | **Break-It program**: pinned reference configs in an RoE-governed range · structured proof-of-bypass (route, effect goal) auto-verified · triage SLA + CVSS v4.0 + AIVSS severity + family dedup (feeds [PRD 28](28-policy-bypass-search.md)) · coordinated disclosure (private fix window 30–90 d, embargo, credit, CVE/CNA + CWE) · tiered rewards · conversion to regression (F61) + route-family catalogue + optional ATLAS submission · import of public human-found corpora (e.g., ART benchmark — license check) | R73 | Consumes [PRD 25](25-attacker-strength-and-pressure.md)/[PRD 26](26-independent-effect-witness.md)/[PRD 28](28-policy-bypass-search.md)/[PRD 35](35-rules-of-engagement-and-safe-fire.md) |

## CUJs

### CUJ-52 — Submit and get credit
A researcher submits a bypass → witness auto-confirms in minutes → acknowledgement ≤ 24 h → fix → credit + CVE. **Success:** auto-verified; credit recorded.

### CUJ-53 — Convert to a regression
A bypass family appears; 3 variants dedupe into 1; a regression case is auto-generated at fix. **Success:** family deduped; regression shipped.

## Success metrics

| Metric | Target |
|---|---|
| Submissions auto-verified (no manual replay) | ≥ 80% |
| Acknowledgement time (median) | ≤ 24 h |
| Triage to severity (median) | ≤ 3 days |
| Time-to-fix (critical/high) | ≤ 14 / 45 days |
| Accepted bypass → regression within release | 100% |
| Repeat-bypass rate (same family reopened after fix) | ≤ 5% |
| Distinct bypass families per quarter | reported (target > 0) |
| Active participants per cycle (pilot) | ≥ 25 |
| Embargo breaches | **0** |

## Dependencies
F32, F61 · [PRD 25](25-attacker-strength-and-pressure.md), [PRD 26](26-independent-effect-witness.md), [PRD 28](28-policy-bypass-search.md), [PRD 35](35-rules-of-engagement-and-safe-fire.md); standards/ISO 29147/30111.

## Boundaries & non-goals
- Legal safe harbor and program terms required (counsel).
- Dual-use: only against reference ranges; accepted payloads private until fix + embargo; published artifacts are family-level.
- Cost: start credit-only or sponsor-funded; witness auto-verification filters spam/dupes.

## Open questions
1. Host on our range vs. partner (Gray Swan/HackerOne-class) — partner for reach, own the verification.
2. Publish reference-config known weaknesses up front? (Recommend: no.)
