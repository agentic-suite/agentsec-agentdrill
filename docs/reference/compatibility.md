# Compatibility

**Status:** built (v0.1.0). Honest coverage — a harness is compatible only when **its pack passes in
CI**. Release notes carry this table ([PRD 05](../prd/05-features.md) §Compatibility).

## Support levels (graded — [PRD 41](../prd/41-platform-compatibility.md))

Binary "compatible" is replaced with a graded scale; every row carries a level and a pinned version.

| Level | Name | Meaning | Evidence |
|---|---|---|---|
| **L0** | Listed | named; no code | none |
| **L1** | Config-aware | parses config/permission/instruction surfaces; flags risky settings | ≥10 config-risk tests |
| **L2** | Driven | attack delivered through the harness's own surface; decision read back | ≥1 end-to-end case, `live` attestation |
| **L3** | Observed | L2 + independent effect witness + stage timing | ≥25 cases, witness coverage ≥90% |
| **L4** | Gated | L3 + defense-contract pack gates *our* CI per harness release | contract pack green on N-1 and N |

**Reference-harness policy:** ≥2 open-source harnesses always at L3+; headline benchmark tables use open
harnesses; proprietary results appear in a separate table. **AWC** (adoption-weighted coverage) is the one
published number.

## Tiers (target inventory)

| Tier | Harness / Ecosystem | Support model |
|---|---|---|
| **1 — Coding agents** | Claude Code · Codex CLI · OpenCode · Cursor · GitHub Copilot · Gemini CLI/Antigravity · Cline · Windsurf · Aider · (long tail) | per-harness attack packs |
| **2 — Frameworks** | LangGraph/LangChain · OpenAI Agents SDK · Claude Agent SDK · CrewAI · Google ADK · Microsoft Agent Framework · PydanticAI · smolagents | OTel `gen_ai.*` + adapters; promptfoo/garak interop |
| **3 — Protocol/enterprise** | MCP clients/gateways (dated revisions) · A2A 1.0 · enterprise platforms | MCP layer via agentgate; enterprise via standards |

Full target lists, per-harness surfaces, defenses-under-test and host/CI/model runtimes:
[PRD 41](../prd/41-platform-compatibility.md).

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
