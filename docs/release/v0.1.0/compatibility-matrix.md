# Compatibility Matrix — v0.1.0

**Status:** 🚧 **pending** (generated from CI at WBS M24). Honest coverage — a harness is compatible only
when **its pack passes in CI**.

| Tier | Harness | Support at v0.1.0 | Fidelity |
|---|---|---|---|
| 1 | Claude Code | per-harness pack | _pending_ |
| 1 | Cursor | per-harness pack | _pending_ |
| 1 | GitHub Copilot (agent mode) | lower-layer coverage (closed hooks) | _pending_ |
| 1 | OpenAI Codex CLI | _pending_ | _pending_ |
| 1 | Gemini CLI | _pending_ | _pending_ |
| 2 | LangGraph · CrewAI · OpenAI Agents · AutoGen/AG2 · LlamaIndex · PydanticAI · smolagents | via promptfoo/garak interop (+ adapter packs) | _pending_ |
| 3 | Generic MCP clients | via agentgate | _pending_ |
| 3 | Enterprise platforms | via standards | _pending_ |

Generating command: `make benchmark` (compatibility table is generated, not hand-edited).
Fidelity labels: `live-verified` / `fixture-verified` / `modeled` ([compatibility.md](../../reference/compatibility.md)).
