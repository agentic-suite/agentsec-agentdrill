# PRD 43 — Evidence Register & Method (Gap Analysis)

**BLUF:** This document preserves the **research base** for the v0.1.0 additions (PRDs 25–42): the external evidence (E1–E14) with sources, the gap analysis, and the PRD tensions that must be decided. It is a **living register**: each claim is labeled **evidence** (sourced), **target** (our proposal), or **verify** (re-check against the primary before use). It exists so that the analysis is not lossy and stale citations cannot silently propagate.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** — · **Reqs:** R79

## Method
1. Read PRDs 00–24 in full.
2. Surveyed 2025–26 research (adaptive attacks, crowd red-teaming, agent/MCP benchmarks), commercial BAS and AI-red-team products, current standards (OWASP/MITRE/NIST/ISO/EU), platform/adoption landscape, and best-in-class OSS.
3. Wrote up only gaps that matter; added PRDs 25–42.
4. This register keeps the evidence and the still-open decisions.

> **Time-sensitivity:** rankings, prices, spec revisions and regulatory dates change. Every time-sensitive item carries an "as of" date and is **verify**-flagged. No claim marked *verify* may be quoted externally until confirmed.

## Evidence register

| # | Evidence | Source | Implication → PRD |
|---|---|---|---|
| **E1** | 12 recent defenses reported near-zero ASR; adaptive attackers (gradient, RL, random search, human-guided) reached **>90%** against most. | Nasr, Carlini, Tramèr et al., *The Attacker Moves Second*, arXiv 2510.09023 (2025-10) | Static replay ≠ robustness → [PRD 25](25-attacker-strength-and-pressure.md) |
| **E2** | Novel tailored attacks raised hijack ASR **11% → 81%**; **25 repeated attempts** raised avg ASR **57% → 80%**. | NIST CAISI technical blog (2025-01) | Report attacker effort; `Hold@k` → [PRD 25](25-attacker-strength-and-pressure.md) |
| **E3** | ~1.8M attacks, 22 agents, 44 behaviors; nearly all violated policy within **10–100 queries**; attacks transfer. | Gray Swan × UK AISI, arXiv 2507.20526 | Crowds find what scripts miss → [PRD 37](37-break-it-program.md) |
| **E4** | 13 frontier models, 250K+ attempts, 400+ participants: **≥1 success against every model**; "universal" attacks transfer (robust→less-robust). | NIST CAISI × Gray Swan × UK AISI (2026-03) | Same; corpus reuse → [PRD 37](37-break-it-program.md) |
| **E5** | τ-bench `pass^k`: success only if **all k** trials pass; reliability collapses with k. | Sierra, arXiv 2406.12045 | `Hold@k` for defenders → [PRD 25](25-attacker-strength-and-pressure.md) |
| **E6** | MCPTox: up to **72.8%** ASR (1,348 cases / 45 servers); MCP-SafetyBench: 20 attack types, **53% stealth**; MCPSecBench: 17 attacks / 4 surfaces, >85% compromise ≥1 platform. | arXiv 2508.14925 / 2512.15163 / 2508.13220 | MCP taxonomy coverage; stealth ⇒ witness → [PRD 26](26-independent-effect-witness.md), [PRD 27](27-adversary-lab.md) |
| **E7** | AgentDojo / τ-bench / MCP-SafetyBench score **environment state**, not text. | benchmark designs | Effect verification is best-in-class → [PRD 26](26-independent-effect-witness.md) |
| **E8** | BAS leaders sell attack-path validation, AI intel→simulation (~9 min claim), vendor-specific mitigation + re-run, detection-rule validation, 75+ integrations. | Picus, SafeBreach, AttackIQ public material (**verify claims**) | Enterprise expectations → [PRD 31](31-attack-path-and-blast-radius.md), [PRD 32](32-incident-to-pack-compiler.md), [PRD 38](38-security-ecosystem-integrations.md) |
| **E9** | MS AI Red Teaming Agent: agentic categories **cloud-only**, Foundry agents + Azure tools only; function tools, browser, connected agents, computer-use **unsupported**. | MS Learn (as of 2026) | Heterogeneous-stack whitespace → [PRD 29](29-bring-your-own-defense.md), [PRD 39](39-frontier-attack-classes.md) |
| **E10** | Consolidation: Promptfoo→OpenAI (2026-03); Lakera→Check Point; Protect AI→Palo Alto; CalypsoAI→F5; Robust Intelligence→Cisco (**verify each**). | vendor/press | Independence is a moat → [PRD 29](29-bring-your-own-defense.md) |
| **E11** | OWASP **Top 10 for Agentic Applications 2026** (ASI01–10) published 2025-12-09; **AIVSS v0.8** (2026-03); ATLAS **v5.4.0** (2026-02) added agent techniques. | OWASP, MITRE | Update citations → [PRD 42](42-standards-and-claims.md) |
| **E12** | EU AI Act Annex III high-risk moved **2026-08-02 → 2027-12-02**; Annex I → 2028-08-02 (Reg. (EU) 2026/1744, in force 2026-07-27). | legal summaries (**verify with counsel**) | Compliance is 2027+ → [PRD 42](42-standards-and-claims.md) |
| **E13** | MCP current revision **2026-07-28** (prior 2025-11-25, 2025-06-18); OAuth 2.1 + RFC 8707 + RFC 9728; DCR deprecated for Client ID Metadata Docs. A2A **1.0** stable, Signed Agent Cards. MCP + AGENTS.md under Agentic AI Foundation (Linux Foundation). | modelcontextprotocol.io, Linux Foundation (**verify**) | Version matrix + auth drills → [PRD 41](41-platform-compatibility.md) |
| **E14** | Sandboxing varies: Codex CLI kernel-level by default; Claude Code namespace + network block; Cursor OS sandbox (early 2026); Windsurf approval-prompt-only (**verify**). | third-party comparison (2026-03) | Per-harness drivers model the harness's own defenses → [PRD 41](41-platform-compatibility.md) |

## Gap analysis (v0.1.0 additions)
| # | Gap | Proposal | Pri |
|---|---|---|---|
| G1 | No attacker-strength dimension / `Hold@k` | PRD 25 | P0 |
| G2 | Circular oracles (defense grades itself) | PRD 26 | P0 |
| G3 | No reusable hostile counterparty | PRD 27 | P1 |
| G4 | No effect-based bypass search | PRD 28 | P0 |
| G5 | Drills only own stack; neutrality risk | PRD 29 | P0 |
| G6 | Unknown production blast radius (false-block) | PRD 30 | P0 |
| G7 | No attack-path/trifecta reachability | PRD 31 | P1 |
| G8 | Manual intel→pack drafting bottleneck | PRD 32 | P1 |
| G9 | Gate can only fail → gets disabled | PRD 33 | P0 |
| G10 | No machine-consumable, fresh proof | PRD 34 | P1 |
| G11 | No target/bystander protection (RoE) | PRD 35 | P0 |
| G12 | Static-only extension scanning | PRD 36 | P1 |
| G13 | No channel for novel bypasses | PRD 37 | P2 |
| G14 | Findings don't reach buyer tools | PRD 38 | P0 |
| G15 | Several ASI classes unpacks | PRD 39 | P1 |
| G16 | Review time / no witness-vs-defense view | PRD 40 | P1 |

## PRD tensions to decide
| # | Tension | Where | Recommendation |
|---|---|---|---|
| T1 | "No unbounded attack generation" vs. adaptive evidence (E1/E2) | PRD 14/16 | Keep the public non-goal; add local-only, RoE-gated **T3**, unpublished (PRD 25/35). Needs a DD entry. |
| T2 | "No security score" vs. buyer expectation of CVSS/AIVSS | PRD 14/F41 | Keep no composite; per-finding CVSS v4.0 + AIVSS vector (PRD 42). |
| T3 | Targets = Wave-0 only vs. neutrality whitespace (E9/E10) | PRD 02/08/R12 | Promote BYOD to P0 as SDK + conformance kit (PRD 29). |
| T4 | Oracles read agentwatch evidence (circularity) | PRD 02/F52 | Add independent witness; disagreement is a finding (PRD 26). |
| T5 | "OWASP Agentic drafts" (R10) | PRD 05 | Update to final ASI01–10 + ASI coverage table (PRD 39/42). |
| T6 | Adaptive attacker excluded from golden locks (F40) | PRD 16 | Fine; pressure curves stay reproducible via seeded T1/T2 (PRD 25). |
| T7 | Competitor benchmarking legal/ethical shape | PRD 08/R12 | Neutrality rules + right-of-reply + licensed-config-only (PRD 29). |
| T8 | Feature count already large (F1–F84) | PRD 05 | Consolidate around five buyer questions; cut what answers none. |

## The five buyer questions (a spine for the PRD)
| Question | Existing | Added |
|---|---|---|
| "Is it *really* blocked?" | F59, F63 | PRD 26, PRD 28 |
| "Against *whom*, how hard?" | F29, F40, F55 | PRD 25 |
| "What does turning it on cost?" | F51 | PRD 30 |
| "Does it work with *my* stack?" | Wave-0 adapters | PRD 29, PRD 41 |
| "Can I prove it — and keep proving it?" | F35, F64, F24 | PRD 33, PRD 34, PRD 38 |

## Requirement / CUJ index (this addition)
- **Reqs:** R59–R79 (with [PRD 25](25-attacker-strength-and-pressure.md)…[PRD 43](43-evidence-register-and-method.md)).
- **Features:** F85–F104.
- **CUJs:** CUJ-28–CUJ-63 (PRDs 25–42); see [PRD 12](12-traceability.md).

## Maintenance
- Every PRD 25–42 citation marked **verify** must be confirmed before external use.
- Re-verify E8/E9/E10/E12/E13/E14 quarterly; re-check E1–E7/E11 on each research refresh.
- A **claims linter** ([PRD 42](42-standards-and-claims.md)) enforces the *evidence / target / verify* labels.
