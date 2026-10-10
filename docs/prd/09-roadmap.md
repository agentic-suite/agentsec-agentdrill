# PRD 09 — Roadmap

**BLUF:** **v0.1.0** ships the proof foundation — curated incident-replay packs, run against the deployed
stack, gating policy PRs in CI, with reproducible honest results and kill-time verification, plus the
evasion pack. **v0.1.0** adds interop import, ATLAS/OWASP tagging, and the community pack flow. **Later**
versions add the competitor benchmark, fuzzing, and framework packs — no deferred proof.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## Versions

| Version | Theme | Scope |
|---|---|---|
| **v0.1.0** (Wave 0) | **The proof foundation** | R1–R8: incident-replay packs (Replit, tool-poisoning/shadowing/rug-pull, Plugin4Shell supply-chain, Slack-AI exfil, credential-evasion); run vs. deployed stack; CI gate; public reproducible benchmark; honest reporting; determinism; evasion pack; kill-time. ≥2 Tier-1 harness packs. Absorbs the predecessor harness harness mechanics (PRD 10) |
| **v0.1.0 (continued)** | **Interop, tagging, community + BAS floor** | R9 promptfoo/garak/AgentDojo/PyRIT import; R10 ATLAS + OWASP tagging on every pack; R11 community contribution flow (reviewed like code); MCP attack packs (Wave 1 growth); **authoring SDK + `init` (F46), pack lint, PR annotations (F47), HITL review queue (F44), severity rubric (F41), recon/scoping (F42), defense contracts for the 5 Wave-0 enforcers (F36), full kill-chain timing (F37), plugin discovery (F49), per-case cleanup (F50), utility-under-attack (F51), expected-telemetry validation (F52)** — see [PRD 19](19-detection-validation-bas.md) |
| **v0.1.0 (continued)** | **Breadth + comparison** | Cross-stack comparison + **regression attribution (F38)** + defense regression attribution; more deployed-stack targets; per-harness packs for Codex/Gemini; richer coverage-gap reports; **trend analytics (F23), coverage reconciliation (F26), evidence bundles (F27), IR replay (F48), drill-the-drill suite (F43), bounded adaptive orchestration (F40), adversary profiles (F54), bootstrap CIs (F55), traces per row (F56), coverage heat-map (F53)** |
| **v0.1.0 (continued)** | **Framework reach + registry** | ≥3 Tier-2 framework adapters/packs (LangGraph, CrewAI, PydanticAI, …); all 5 Tier-1 harness packs; **pack registry + signing + deprecation governance (F39), closes-the-loop policy suggestion (F21), trigger-driven CART (F22)** |
| **v0.1.0 (continued)** | **Fleet + convention** | **Fleet mode (F45)**, multi-stack aggregate honest coverage; R12 competitor/other-tool honest-coverage benchmark **via PR-based submission (F57)**; R13 OSS-Fuzz pack class; **standards submission surface (F28)** — NIST CAISI/AgentDojo-Inspect, OWASP Agentic |
| **v0.1.0 (continued)** | **Depth** | Enterprise/platform coverage via standards; A2A attack packs as the spec stabilizes; memory-poisoning depth (F20) |
| **v0.1.0 (additions, 2026-10-10)** | **World-class gap closure** | PRDs 25–43 (R59–R79): attacker-strength pressure curves (`Hold@k`), independent effect witness, adversary lab, bypass search, BYOD + neutral head-to-head, trace backtest/shadow, attack-path blast radius, incident-to-pack compiler, exposure ledger + waivers, drill attestations + deploy gate, rules-of-engagement, extension detonation lab, break-it program, security-ecosystem integrations, frontier attack classes (ASI coverage), trace explorer, platform compatibility matrix, standards/claims |

## Compatibility targets by version

| Version | Tier-1 coding agents | Tier-2 frameworks |
|---|---|---|
| **v0.1.0** | ≥2 of Claude Code · Cursor · Copilot · Codex CLI · Gemini CLI (per-harness packs) | via promptfoo/garak interop |
| v0.1.0 | +MCP attack packs (via agentgate) | — |
| v0.1.0 | all 5 (or documented lower-layer coverage) | ≥3 adapters |
| v0.1.0 | + Copilot via lower layer; enterprise via standards | + more frameworks |

> Fidelity is declared per harness; a harness is "compatible" only when **its pack passes in CI**, and the
> release compatibility table states honest coverage (same rule as the capability table).

## Migration & deprecation

- **Predecessor:** the predecessor harness is retired and superseded; its mechanics live on inside
  agentdrill (see [PRD 10](10-feature-parity.md)).
- **Superseded ideas:** the red-team predecessor idea is absorbed into the attack-pack + continuous-red-team framing.
- **No silent number changes:** any change to a published result is accompanied by a re-pin note and a new
  `run-manifest.json`.

## Release cadence

Each version ships with: release notes, a **compatibility table**, a **security audit** (org governance
floor), and the **published benchmark** including misses. Articles accompany each release per the
ecosystem content plan.

## Ecosystem dependency

agentdrill needs **targets**: it drills agentgate, agentkeys, agentseatbelt/agentkernel, policyweave
output, and agenthalt, and reads agentwatch. It ships early in Wave 0 (the thin-slice meta-MVP) and grows
as more enforcers land.
