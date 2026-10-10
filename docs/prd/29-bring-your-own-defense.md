# PRD 29 — Bring-Your-Own-Defense & Neutral Head-to-Head

**BLUF:** agentdrill must be a **neutral** proof layer for *any* defense, not a benchmark for the ecosystem's own products. Ship a **Defense Contract + SDK + conformance kit**, a set of OSS-first reference adapters (a "Defense Zoo"), and a **neutral head-to-head** report under published neutrality rules (pre-registration, vendor right-of-reply, licensed-config-only, conflict disclosure, no composite score). This turns the Neutrality blocker into the moat.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F90, F91 · **Reqs:** R64, R65

## Why

- In-market consolidation (Promptfoo→OpenAI Mar 2026; Lakera→Check Point; Protect AI→Palo Alto; CalypsoAI→F5; **verify each**) leaves few independent proof layers; **independence is scarce and valuable**.
- Vendor red-team tools are narrow: Microsoft's AI Red Teaming Agent's agentic categories are cloud-only and Foundry+Azure-tool-only; function tools, browser, connected agents and computer-use are listed **unsupported**.
- Neutral tools (promptfoo, garak, Giskard) already target arbitrary HTTP apps — we must at least match, then exceed.
- Today's targets are the Wave-0 stack only (RK-5), reading as "benchmark our own stuff."

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R64** | An open **Defense Contract + SDK + conformance kit** lets any defense be drilled; adapters are certified to a **conformance level**; a starting **Defense Zoo** of OSS reference adapters ships. | ≥ 2 conforming reference adapters at v0.1.0 (≥ 6 across ≥ 6 classes by v0.2); 100% conformance before listing. |
| **R65** | A **neutral head-to-head** report compares N defenses on identical packs/seeds/environment/benign twins, with published **neutrality rules** and no composite score. | 100% of head-to-heads identical-input; vendor right-of-reply offered on 100%; zero composite scores/rankings published. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F90** | **Defense Contract + SDK + conformance kit + Defense Zoo.** Contract declares decision points, I/O shape, evidence emission, config digest, fail-mode, version, ToS notes. | R64 | OSS/free defenses first; we maintain the SDK/kit, community maintains adapters (RK-5) |
| **F91** | **Neutral head-to-head** with per-case/tier `Hold@k`/`ASR@k`+CI, utility cost (false-block on twins + CI), cost/latency, fail-open/closed; **no ranking arrow**. | R65 | Extends F51/F32; consumes PRD 25/26 |

### Neutrality rules (published, binding)
1. **Pre-registered methodology** and pack list before any run.
2. **Vendor right-of-reply** (14-day window, raw bundle); reply published verbatim.
3. **Licensed/own configuration only**; no benchmarking where ToS forbids without consent; `tos_reviewed` per adapter.
4. **Conflict disclosure**; ecosystem-owned defenses are flagged and held to the same contract.
5. **Config digest** on every cell; "default" vs. "tuned" labeled separately.
6. **Counsel review** before first publication.

## CUJs

### CUJ-36 — Pick between defenses honestly
Two prompt-injection guards and one OPA rule set, same pack, same twins. **Success:** lowest false-block at equal `Hold@10`, with CIs.

### CUJ-37 — Reproduce the OSS table
An external party re-runs the OSS-only head-to-head on their laptop. **Success:** numbers match.

## Success metrics

| Metric | Target |
|---|---|
| Defense classes with ≥1 conforming adapter | ≥ 6 of 8 by v0.2 |
| OSS reference adapters in the Zoo | ≥ 6 |
| Third-party adapters passing the kit | ≥ 3 within 2 releases |
| Time to author a new adapter (request/response defense, median) | ≤ 2 days |
| Head-to-heads with identical seeds/env/twins | 100% |
| Vendor right-of-reply offered before publication | 100% |
| Cells bound to config digest | 100% |
| Published tables with a composite score/ranking | **0** |
| Third-party reproduction of an OSS head-to-head | ≥ 1 per release |

## Dependencies
F14, F32, F36, F51, F3 · [PRD 25](25-attacker-strength-and-pressure.md), [PRD 26](26-independent-effect-witness.md), [PRD 42](42-standards-and-claims.md).

## Boundaries & non-goals
- Not a purchasing recommendation engine; no endorsement mark (conformance level only).
- Measures a defense **in a configuration**, never "the product."

## Open questions
1. Where does the adapter listing live (in-project → foundation)?
2. Legal/ToS shape of competitor publication — counsel before first run.
