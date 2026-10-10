# Compatibility Matrix — v0.1.0

**Status:** 🚧 **pending** (generated from CI at WBS M32). Graded compatibility ([PRD 41](../../prd/41-platform-compatibility.md)):
a harness row carries a **level L0–L4** and a **pinned version** — never a bare "compatible".

**Levels:** L0 listed · L1 config-aware · L2 driven · L3 observed (witnessed) · L4 gated (contract pack in CI).
The published headline number is **AWC** (adoption-weighted coverage).

| Tier | Harness | Target level @ v0.1.0 | Level (measured) | Version | Witness coverage |
|---|---|---|---|---|---|
| 1 | Claude Code | L3 | _pending_ | _pending_ | _pending_ |
| 1 | Codex CLI (open reference) | L3 | _pending_ | _pending_ | _pending_ |
| 1 | OpenCode (open reference) | L3 | _pending_ | _pending_ | _pending_ |
| 1 | Cursor | L2 | _pending_ | _pending_ | _pending_ |
| 1 | GitHub Copilot (agent mode) | L2 (coding agent → L3 via Actions) | _pending_ | _pending_ | _pending_ |
| 1 | Gemini CLI / Antigravity CLI | L2 | _pending_ | _pending_ | _pending_ |
| 1 | Cline · Windsurf · Aider | L1–L2 | _pending_ | _pending_ | _pending_ |
| 2 | LangGraph · OpenAI Agents SDK · Claude Agent SDK · CrewAI · Google ADK · MS Agent Framework · PydanticAI · smolagents | L2 (L3 for 3 by v0.2) | _pending_ | _pending_ | _pending_ |
| 3 | Generic MCP clients / gateways (dated revisions) | L2 | _pending_ | _pending_ | _pending_ |
| 3 | A2A 1.0 peers · enterprise platforms | L2 | _pending_ | _pending_ | _pending_ |

**Reference-harness policy:** ≥2 **open-source** harnesses always at L3+; headline tables use open harnesses;
proprietary-harness results appear in a **separate table**. A harness's own built-in defenses are part of the
target — results label "harness defaults" vs. "auto-approve".

**AWC** at v0.1.0: _pending_ (target ≥ 0.60).

Generating command: `make benchmark` (the compatibility table is generated, not hand-edited). Full target
inventory: [PRD 41](../../prd/41-platform-compatibility.md). Levels + evidence: [compatibility.md](../../reference/compatibility.md).
