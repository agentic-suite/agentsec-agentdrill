# Compatibility Matrix — v0.1.0

**Status:** ✅ **published** 2026-10-25 — **with declared gaps** (see below). Graded compatibility
([PRD 41](../../prd/41-platform-compatibility.md)): a harness row carries a level **L0–L4** and a pinned
version, never a bare "compatible". The table is **generated from data**, not hand-edited — source:
[compatibility-data.json](compatibility-data.json), generator: [`scripts/release/awc.py`](../../../scripts/release/awc.py).

**Levels:** L0 listed · L1 config-aware · **L2 driven** · **L3 observed (witnessed)** · L4 gated (contract pack
in CI). The published headline number is **AWC** (adoption-weighted coverage).

## Measured rows

| Tier | Harness | Level | Version | Evidence |
|---|---|---|---|---|
| 2 | LangGraph | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-LG-OFFICIAL` |
| 2 | OpenAI Agents SDK | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-OA-OFFICIAL` |
| 2 | AutoGen (AG2) | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-AG-OFFICIAL` |
| 2 | CrewAI | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-CREW-EXAMPLES` |
| 2 | Google ADK | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-ADK-OFFICIAL` |
| 2 | PydanticAI | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-PAI-OFFICIAL` |
| 2 | smolagents | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-SM-SMOLCC` |
| 2 | LlamaIndex | **L2 driven** | pinned SHA | `results/track-b/cases/FT-B-LI-OFFICIAL` |
| 1 | Coding agents (Claude Code, Codex CLI, Cursor, Copilot agent, Gemini CLI, Cline/Windsurf/Aider) | **L1 config-aware** | not driven | listed only — not measured in v0.1.0 |
| 3 | MCP clients/gateways · A2A 1.0 peers | **L0 listed** | not driven | listed only — not measured in v0.1.0 |

A harness reaches L2 when a **real agent loop** executed the packs (a skip counts as failure). Every L2+ row is
evidence-linked; the generator refuses an L2+ row with no evidence.

## The headline numbers (measured, and the gaps)

```
AWC: 0.5 (min 0.6) -> NOT MET
open-source at L3+: [] (min 2)
```

- **AWC = 0.50** (target **≥ 0.60**). AWC is adoption-weighted coverage; adoption is the GitHub-stars bucket
  captured 2026-10-25 (recorded in the data file). With every harness at L2 (ratio 0.5), AWC is 0.50.
- **Open-source at L3+: 0** (reference-harness policy needs **≥ 2**).

**Both are declared gaps, tracked in [#393](https://github.com/agentic-suite/agentsec-agentdrill/issues/393)
(parked under 0.2.0), not hidden.** They are unmet because no harness is yet **witnessed (L3)**: the independent
effect witness is a library, and no framework run currently records a `TwoOracleVerdict` (see
[PRD 26](../../prd/26-independent-effect-witness.md)). The witness is demonstrated only in the demo suites
(`FT-D-2`, `FT-D-3`), which are not per-harness rows. AWC rises above 0.60 once ~3 high-adoption harnesses reach
L3 ([#393](https://github.com/agentic-suite/agentsec-agentdrill/issues/393) quantifies this).

## What is not covered

- **L4 gating (contract pack in CI): no harness.** No framework runs a contract pack in CI yet.
- **L3 witnessing: no harness** (both gaps above).
- **Tier-1 coding agents and Tier-3 protocols: listed, not driven** in v0.1.0.

Reproduce the numbers: `python3 scripts/release/awc.py` (exit non-zero while a gate is unmet). Levels and
adoption: [compatibility-data.json](compatibility-data.json). Related: [compliance matrix](compliance-matrix.md).
