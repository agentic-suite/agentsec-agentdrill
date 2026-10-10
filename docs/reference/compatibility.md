# Compatibility

**Status:** draft (design intent). Honest coverage — a harness is compatible only when **its pack passes in
CI**. Release notes carry this table ([PRD 05](../prd/05-features.md) §Compatibility).

## Tiers

| Tier | Harness / Ecosystem | Support model |
|---|---|---|
| **1 — Coding agents** | Claude Code · Cursor · GitHub Copilot (agent mode) · OpenAI Codex CLI · Gemini CLI | per-harness attack packs |
| **2 — Frameworks** | LangChain/LangGraph · CrewAI · OpenAI Agents SDK · AutoGen/AG2 · LlamaIndex · PydanticAI · smolagents | promptfoo/garak interop; framework adapter packs |
| **3 — Protocol/enterprise** | Generic MCP clients · enterprise platforms | MCP layer via agentgate; enterprise via standards |

## Minimums

- **v0.1.0:** ≥2 Tier-1 harness packs; Tier-2 reached via promptfoo/garak interop.
- **target:** all 5 Tier-1 (or documented lower-layer coverage, e.g. Copilot's closed hooks); ≥3 Tier-2 adapters.

## Fidelity

Each harness row carries a fidelity label (agentwatch discipline):

| Label | Meaning |
|---|---|
| `live-verified` | exercised against a real harness/stack; pack passes |
| `fixture-verified` | exercised deterministically (fixtures); no live capture yet |
| `modeled` | declared-compatible on analysis, pack not yet passing |

> **Honesty rule:** no row claims more than it demonstrates. A `modeled` row is stated as such until its
> pack passes in CI.
