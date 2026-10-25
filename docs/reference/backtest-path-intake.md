# Backtest, Attack-Path Graph & Incident Intake — Reference

**BLUF:** How agentdrill turns real history and inventory into risk-driven drilling: replay recorded
sessions against a candidate policy (with a false-block budget), run a side-effect-free shadow, promote a
session into a redacted drill case, build the capability/attack-path graph and bind cases to critical paths,
and compile a fresh advisory into a reviewed pack. **Normative (M27).** Packages: `agentdrill/backtest/`,
`agentdrill/pathgraph/`, `agentdrill/intake/`. Source design:
[design/backtest-path-intake.md](../design/backtest-path-intake.md); PRD
[30](../prd/30-trace-backtest-and-shadow.md) (R66), [31](../prd/31-attack-path-and-blast-radius.md) (R67),
[32](../prd/32-incident-to-pack-compiler.md) (R68). Closes gaps G6, G7, G8.

## Trace backtest & shadow (`agentdrill/backtest/`)

| Concern | API | Notes |
|---|---|---|
| Replay a session corpus | `backtest(sessions, policy)` → `BacktestReport` | classifies each session `unchanged` / `newly_blocked` (clustered) / `regression` / `un_replayable` |
| Replay fidelity | `require_fidelity` (≥99 %) | the share of sessions replayable; a thin corpus cannot pass |
| Shadow (log-only) | `run_shadow(decisions, side_effects=…)` → `ShadowReport` | divergence rate + **false-block clusters** on benign calls |
| False-block budget | `require_false_block_budget` (default 0.5 %), bootstrap CI | reuses M10 `reporting.ci.bootstrap_ci` |
| Side-effect-free shadow | `require_side_effect_free` | the M23 witness side-effect list must be empty |
| Trace → drill | `promote_session` → `PromotedCase`; `approve_promoted`/`require_approved` | tag `origin:production-trace`, mined `benign_twin`, F65 receipts, HITL |

**Methodology.** Production sessions are read as the M7 `AgentWatchEvent` stream (SSOT); only `denied`
means production blocked an action. A **regression** is the candidate allowing what production denied — it
dominates a mixed session. A **newly_blocked** session is a candidate false-block on a call production
allowed, clustered by the action reference. `un_replayable` sessions are **itemized**, never dropped, and
they lower fidelity. Redaction uses M18 `lifecycle.privacy` with receipts; a promoted case that still
contains a known secret class is **refused**.

## Capability / attack-path graph (`agentdrill/pathgraph/`)

```
nodes: agents, tools, mcp_servers, credentials/scopes, data_sources, egress_routes,
       memory_stores, sub_agents, approval_settings, instruction_files   (+ unknown = blind spot)
edges: directed "reaches"
paths: untrusted_input → … → crown_jewel
status: proven_broken | open_missed | unproven | accepted
```

- **Build:** `build_graph(items, edges=…, crown_jewels=…, untrusted=…, attributes=…)`. An unknown inventory
  kind stays a visible **`unknown`** node; a dangling edge/crown-jewel/entry fails loudly.
- **Reachability:** `reachable_paths` enumerates simple untrusted → crown-jewel paths; **structural only** —
  a hypothesis until a drill proves it.
- **Severity (AIVSS-compatible factors, never aggregated):** `path_severity` → factors `untrusted_input`,
  `invokes_tool`, `credential_scope`, `reaches_crown_jewel`, `external_egress`; level `critical` when a crown
  jewel + external egress, else `high`/`medium`/`low`.
- **Structural findings:** `detect_findings` → `trifecta_present`, `over_scoped_token`,
  `unrestricted_egress`, `auto_approve_plus_shell`, `writable_instruction_file`, `shared_memory`,
  `identity_inheritance` (node attributes supply the flags).
- **Binding + status:** `bind_path` (status is exclusive), `require_critical_bound` (100 % of critical paths
  bound to a case), `new_paths`/`new_path_alerts` on a config change that opens a new path.

## Incident-to-pack compiler (`agentdrill/intake/`)

```
feeds → dedup(source+external_id) → relevance vs. inventory → cite-or-drop brief
  → draft pack (twin + cleanup + M23 witness effects + preregistered outcome)
  → dual-use screen → HITL review (reviewer ≠ drafter) → registry
```

The draft is a product of the **cited facts only** — an advisory with no cited fact referencing the
inventory is refused; the dual-use screen flags off-inventory or unattested steps. The **efficacy check
(F59)** and the **lab generators (F88)** operate on the draft at the pipeline boundary: 27.6 emits the draft
with a preregistered outcome and declared effects, which M13/M23 then exercise.

## Invariants

1. Backtest/shadow disclose fidelity; shadow is side-effect-free (witness-proven).
2. Trace-derived cases are redacted (receipts verified); zero unredacted secrets.
3. Cited-or-dropped; no payload invention beyond the source.
4. Reachability is a hypothesis until a drill proves the path.

## Known limitations

- Backtest/shadow replay a **model** of production (fidelity disclosed), not production itself.
- Path reachability is structural; `proven_broken` requires drill evidence (27.5 status binding).
- The intake efficacy gate and the ≤48 h / ≤1 day / ≤4 h SLAs are measured in the field (M31).
- Path status `accepted` consumes the M28 exposure ledger/waivers (seam).
