# PRD 14 — Non-Goals

**BLUF:** agentdrill proves defenses; it does not **detect**, does not **enforce**, does not **build an
attack arsenal**, and does not **sell a leaderboard**. There is one P0 non-goal — **no injection-detection
claims from drill results, ever** — and a small set of consolidated ones below.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Consolidated non-goals

| Non-goal | Why |
|---|---|
| **No injection-detection claims** | We measure **our enforcement controls**, never market "injection solved." A drill result is not a detection claim. |
| **No model-attacking capability development** | We **replay documented incident patterns**; agentdrill is not a red-team arsenal (dual-use line, PRD 08). |
| **No proprietary scoring** | Public methodology or nothing — an opaque score is anti-trust. |
| **No enforcement** | agentdrill composes the enforcers; it never becomes a control (PRD 02). |
| **No observability product** | That is agentwatch; agentdrill consumes it. |
| **No generic LLM eval framework** | Not "which model is better"; not agent-quality grading (waived from the predecessor harness, PRD 10). |
| **No benchmark leaderboard of models** | The benchmark is defenses vs. documented attacks, misses published. |
| **No auto-prompt/model optimizer** | We prove; we do not mutate systems. |
| **No hosted observability / SIEM** | Out of scope (agentcomply's territory for evidence). |
| **No "security score"** | A single number could hide a miss; we publish the outcome split + misses. |
| **No novel exploit publication** | Packs replay patterns that already happened; new exploits are not published. |
| **No unbounded attack generation** | The adaptive orchestrator (F40) mutates *documented* patterns only, with per-case provenance; open-ended attacker-LLM freestyle is out of scope and out of the registry. The attacker-strength tiers ([PRD 25](25-attacker-strength-and-pressure.md)) keep T0–T2 published; **T3 adaptive search is local-only, rules-of-engagement-gated, and never published** — so pressure can be measured without shipping an arsenal. |
| **No severity theater** | The rubric (F41) prioritizes; it never re-labels a miss as acceptable. |

## Explicit non-requirements (from the source PRD)

- **No injection-detection claims** from drill results.
- **No model-attacking capability development.**
- **No proprietary scoring.**

## What we *do* claim

A reproducible, honest statement of what a **specific deployed configuration** did against a **specific
documented attack** at a **specific pinned version** — plus how long revocation took — misses included.
