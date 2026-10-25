# Recon / Scoping — Design

**BLUF:** Before any case runs, recon **probes the exposed surface** (tools, MCP servers, capabilities),
produces a `ReconSnapshot`, and **binds every case** to what actually exists. A case bound to a nonexistent
surface fails **loudly** — never silently passes. An unreachable model surface fails before cases run.

**Status:** implemented (M5). Code: `src/agentdrill/recon.py`. Spec:
[../wbs/v0.1.0/wbs-v0.1.0-part3-drivers-targets.md](../wbs/v0.1.0/wbs-v0.1.0-part3-drivers-targets.md).

## Flow

```
surface (inventory | probe command) → ReconSnapshot → bind_cases(pack)  # missing surface → ConfigError
model surface (model + base_url) → check_model_surface()  # unreachable/404 → ConfigError (G12)
```

## ReconSnapshot (data-dictionary entity)

| Field | Meaning |
|---|---|
| `tools` | Tools exposed to the agent at run time |
| `mcp_servers` | Connected MCP servers |
| `capabilities` | Declared capabilities (e.g. `filesystem_write`) |
| `case_bindings` | `case_id → [tool, …]` the case actually touches |

`has_tool(t)`: a plain tool is present if listed; an MCP tool `mcp__<server>__<tool>` is present when
`<server>` is in `mcp_servers`.

## Sources

- **Inventory** — an agentwatch inventory mapping (`probe(inventory=…)`).
- **Probe command** — a command that emits the inventory JSON on stdout (`probe(command=…)`).

## Rules

- **Bind before run.** `bind_cases` walks the pack; any attack step whose tool is absent raises
  `ConfigError` naming the case and the missing surface(s).
- **Model sanity (G12).** When a `ModelSurface(model, base_url)` is declared, `check_model_surface` GETs
  `{base_url}/models` first; a 404 or a connection error becomes a clear `ConfigError` before any case runs.
- **Never silent.** No inventory and no command ⇒ `ConfigError`; a probe that crashes or emits non-JSON ⇒
  `AdapterError`.

## Storage

The snapshot is written to `.agentdrill/runs/<run_id>/recon.json` and referenced from `run.json`
(`recon_ref`), so a run reconstructs what it targeted (see [storage-design.md](storage-design.md)).
