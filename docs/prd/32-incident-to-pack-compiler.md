# PRD 32 — Incident-to-Pack Compiler & Threat Feed

**BLUF:** Freshness is the moat and the bottleneck. A **7-day** human pipeline (CUJ-20) lags the 2026 agent-incident cadence. Add an **assisted, reviewer-gated compiler**: intake feeds (GHSA/CVE, ATLAS, incident databases, vendor advisories, arXiv) are filtered against *your* inventory, extracted into a **cite-or-drop** incident brief, compiled into a **draft pack** (lab-based cases, benign twin, cleanup, witness effects, preregistered outcome), **efficacy-checked**, dual-use screened, then human-reviewed into the registry. Speed without crossing the dual-use line.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F94 · **Reqs:** R68

## Why

- BAS vendors compete on intel-to-simulation speed (Picus claims ~9 min URL/PDF/CVE/actor → ATT&CK-mapped simulation — **vendor claim, verify**).
- 2026 produced a steady stream (EchoLeak, Amazon Q wiper prompt, MCP rug-pulls, OpenClaw CVEs, rules-file backdoors).
- Manual drafting cannot keep the 7-day SLA; but speed must not break fidelity (PRD 08) or the dual-use line (PRD 14).

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R68** | An **assisted, reviewer-gated** intake-to-draft-pack pipeline with **cite-or-drop** extraction, inventory-aware relevance, automatic efficacy check, dual-use screen, and independent review before registry. | ≥ 80% assessed within 48 h (100% ≤ 7 days); 100% of facts cited; dual-use false-accept 0 (audit). |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F94** | **Incident-to-pack compiler & threat feed**: dedup intake feeds · relevance filter vs. [PRD 31](31-attack-path-and-blast-radius.md) inventory · cite-or-drop incident brief · draft pack from [PRD 27](27-adversary-lab.md) generators (documented parameters only) + twin + cleanup + witness effects + preregistered outcome (F31) · automatic efficacy check (F59) · dual-use screen · HITL review (reviewer ≠ drafter) → registry (F39) | R68 | Extends F60/F70/F46; consumes [PRD 26](26-independent-effect-witness.md) |

## CUJs

### CUJ-42 — Hours, not days
A GHSA drops for an MCP server we run → within hours, a reviewed draft pack and a pass/fail result against our stack. **Success:** ≤ 48 h end-to-end.

### CUJ-43 — Cite or drop
The reviewer sees brief + citations + efficacy report; every fact links to a source span; unsupported statements are absent. **Success:** 100% cited; hallucination ≤ 1% on audit.

## Success metrics

| Metric | Target |
|---|---|
| Source published → draft ready for review (median) | ≤ 4 h |
| Intake SLA (assessed: pack-draft or N/A with reason) | 100% ≤ 7 days; ≥ 80% ≤ 48 h |
| Draft acceptance after review | ≥ 60% |
| Reviewer edit distance (median) | ≤ 30% |
| Efficacy pass on first draft | ≥ 70% |
| Facts with a source citation | 100% |
| Hallucinated-fact rate (review audit, sampled) | ≤ 1% |
| Dual-use screen false-accept (audit) | **0** |
| Source families covered | ≥ 5 |
| Relevance precision ("affects my stack") | ≥ 85% |

## Dependencies
F31, F39, F44, F50, F54, F59, F60, F70 · [PRD 27](27-adversary-lab.md), [PRD 26](26-independent-effect-witness.md), [PRD 31](31-attack-path-and-blast-radius.md).

## Boundaries & non-goals
- LLM drafting is a **tool**, not authority: reviewer-gated, cited, reproducible (model pinned).
- **Intake is untrusted content** → runs in the lab with no tools/secrets (self-applied evasion class).
- Store citations/extracts, not full third-party text.

## Open questions
1. Hosted vs. local drafting model policy.
2. Publish incident briefs as a public STIX feed? (Recommend: yes.)
