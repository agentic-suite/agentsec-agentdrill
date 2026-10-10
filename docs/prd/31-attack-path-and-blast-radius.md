# PRD 31 — Attack-Path Graph & Blast Radius

**BLUF:** Per-control tests do not say *which gap reaches something that matters*. For agents, danger is **combinations** — private-data access + untrusted-content exposure + external communication (the "lethal trifecta"; Meta's "Agents Rule of Two" — **verify attribution**). AIVSS v0.8 formalizes this with ten amplification factors. agentdrill builds a **capability graph** from inventory, detects risky structures (trifecta, over-scoped tokens, unrestricted egress, auto-approve + shell), computes **reachable-harm paths**, and drives drilling by **path** — reporting **path-level proof coverage**, not just a heat-map.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F93 · **Reqs:** R67

## Why

- BAS leaders converged on **attack-path validation** (SafeBreach Propagate, Picus attack-path validation, Pentera) because unreachable findings don't matter.
- F42 recon and F26 coverage reconciliation answer "which surfaces did we exercise?", **not** "which reachable paths exist and which are proven broken?"
- Without a graph, drills are chosen by catalog rather than by risk; "is my versioned configuration still safe?" has no structural answer.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R67** | Build a **capability/attack-path graph** from inventory; emit structural findings; bind drills to reachable critical paths; report **path status** (`proven_broken`/`open_missed`/`unproven`/`accepted`) and alert on **new paths** opened by config change. | 100% of reachable critical paths have ≥1 bound case; ≥ 95% of critical paths `proven_broken` at the declared tier; zero unexplained `unproven` past 14 days. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F93** | **Attack-path graph & blast radius**: capability graph (agents, tools, MCP servers, credentials/scopes, data, egress, memory, sub-agents, approvals, instruction files) · structural findings (trifecta, over-scope, egress, auto-approve+shell, writable instructions, shared memory, identity inheritance) · reachable-harm paths → crown jewels · per-path AIVSS-compatible severity · drill selection (feeds F76) · path status · new-path drift alerts | R67 | Consumes agentwatch inventory, F26, F42; consumes [PRD 26](26-independent-effect-witness.md) for proof |

## CUJs

### CUJ-40 — Trifecta inventory
Show agents with trifecta capability and, for each, which control breaks the path and when it was last proven. **Success:** answer in ≤ 60 s.

### CUJ-41 — New path fails the gate
A PR adds a Slack MCP server to the support agent → 2 new paths, 0 proven → gate fails with the case list. **Success:** ≤ 1 CI run detection.

## Success metrics

| Metric | Target |
|---|---|
| Critical paths `proven_broken` at declared tier | ≥ 95% |
| `unproven` critical paths older than 14 days | **0** unexplained |
| Inventory completeness (vs. ground-truth test fleet) | ≥ 95% |
| New-path detection latency after config change | ≤ 1 CI run |
| Structural findings precision (reviewer-confirmed) | ≥ 90% |
| Reachable critical paths with ≥1 bound case | 100% |
| Time to answer "what can a hijacked agent X reach?" | ≤ 60 s |

## Dependencies
agentwatch inventory, F26, F41, F42, F53, F76 · [PRD 26](26-independent-effect-witness.md), [PRD 33](33-exposure-ledger-and-waivers.md).

## Boundaries & non-goals
- Graph quality is bounded by inventory (blind spots shown as `unknown nodes`).
- Not a CSPM/CIEM product; imports from them where available.
- Static reachability ≠ exploitability → path status requires **drill proof**.

## Open questions
1. Graph persistence (ephemeral per run + snapshot hash vs. long-lived store).
2. Which factors are auto-inferred vs. user-attested (see [PRD 42](42-standards-and-claims.md)).
