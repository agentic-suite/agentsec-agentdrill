# Skill: drill

A read-only skill that lets a coding agent consult the drill record mid-session — "what regressed?", "show
me the misses for agentgate this release" — without leaving the loop. Mirrors agentwatch's read-only MCP
posture (F77).

**Status:** design intent.

## Tools (read-only)

| Tool | Returns |
|---|---|
| `list_packs` | installed packs, versions, trust levels, tags |
| `list_cases` | cases (`--tag`/`--target`/`--difficulty`) |
| `show_result <case>` | a case's blocked/missed/degraded + dimensions + evidence refs |
| `show_misses` | the misses for a stack/release (the honest table) |
| `show_kill_chain <case>` | the stage timeline + findings |
| `explain <case>` | why the case exists (incident_ref, adversary profile) |

## Rules

- **No write tools.** An agent can read the record, never alter a result or a pack.
- Queries are themselves recorded as drill-record accesses.
- Content is treated as untrusted input (no eval/dynamic render) — the telemetry-injection class.

## Usage

```sh
agentdrill init --mcp-serve     # expose the read-only drill surface
# then, from a coding agent: "what regressed since v0.1.0 in my stack?"
```

See [design/observability](../../design/observability.md) and [PRD 22](../../prd/22-frontier-dx-features.md).
