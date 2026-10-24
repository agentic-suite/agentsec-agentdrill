# agentdrill M27 — Backtest, Attack-Path & Incident Intake Execution Plan

**Spec:** [WBS M27](../wbs/v0.1.0/wbs-v0.1.0-part15-context-governance.md) · [design](../design/backtest-path-intake.md) · [PRD 30](../prd/30-trace-backtest-and-shadow.md), [PRD 31](../prd/31-attack-path-and-blast-radius.md), [PRD 32](../prd/32-incident-to-pack-compiler.md).

**Status:** 🚧 In progress (2026-10-24) · **Issues:** #336–#346 · Closes predecessor gaps **G6, G7, G8**.

## Constraints

- **Privacy first:** trace-derived cases are redacted with verifiable receipts (F65); zero unredacted secrets.
- **Shadow is side-effect-free** — proven by the M23 witness, never assumed.
- **Reachability ≠ exploitability:** a path is `unproven` until a drill proves it; never a detection claim.
- **Intake content is untrusted** → it runs in the lab with no tools/secrets; the drafting model is a pinned
  tool, not an authority. Cite-or-drop: no payload invention beyond the source.
- One ticket at a time: test **RED** → implement **GREEN** → next. Full suite at milestone end only.

## Prerequisites

- Consumes **M8** (`fixtures/`, run manifest), **M13** (`efficacy/` — the unguarded control group for the
  efficacy check), **M23** (`witness/` — side-effect-free shadow + pack witness effects), **M24** (attacker
  tiers for path severity), **M26** (`integrations/` — STIX/OCSF for briefs, OSCAL for the ledger seam).
- **M28 seam:** path status `accepted` and the "new-path" gate consume the exposure ledger/waivers, owned by
  M28. Until then, `accepted` is a caller-supplied label and the diff-aware selection reuses M11's
  `affected_cases`.

## Tasks

- **T1 — Trace backtest (27.1, #336).** Replay redacted, timestamped agentwatch sessions against a candidate
  policy: `newly_blocked`, `regressions`, `unchanged`, and `un-replayable` (itemized, never ignored); replay
  fidelity ≥ 99 %. *RED:* fidelity gate + per-class itemization. *GREEN.*
- **T2 — Shadow mode + FP budget (27.2, #337).** Log-only candidate beside the enforced policy; divergence
  rate + clusters; a declared **false-block budget** with a bootstrap CI; over-budget fails loudly.
- **T3 — Trace→drill (27.3, #338).** Promote a session → redacted case + mined benign twins
  (`origin: production-trace`, HITL); redaction receipts; zero unredacted secrets.
- **T4 — Capability/attack-path graph (27.4, #339).** Build the graph from inventory (agents, tools, MCP
  servers, credentials/scopes, data sources, egress, memory, sub-agents, approvals, instruction files) with
  per-path AIVSS-compatible severity (never aggregated).
- **T5 — Structural findings + path status (27.5, #340).** trifecta / over-scope / unrestricted egress /
  auto-approve+shell / writable instructions / shared memory / identity inheritance; bind cases to paths;
  `proven_broken`/`open_missed`/`unproven`/`accepted`; new-path drift alert.
- **T6 — Incident-to-pack compiler (27.6, #341).** dedup feeds → relevance vs. inventory → cite-or-drop brief
  → draft pack (lab generators + twin + cleanup + witness effects + preregistered outcome) → efficacy check →
  dual-use screen → HITL (reviewer ≠ drafter) → registry.
- **T7 — Gates + docs (27.T #342 · 27.C #343 · 27.L #344 · 27.CR #345 · 27.D #346).** tests; coverage ≥ 95 %;
  `ruff` zero + `mypy --strict` clean; review log resolved; backtest methodology + graph design + intake
  pipeline docs.

## Module ownership (single-writer files)

- New packages `agentdrill/backtest/` (27.1–27.3), `agentdrill/pathgraph/` (27.4–27.5),
  `agentdrill/intake/` (27.6) — proposed.
- **Reuse, do not fork:** `integrations/` (STIX briefs), `efficacy/` (control group), `witness/`,
  `fixtures/`, M11 `affected_cases`, the pack schema (`loading/`).
- One writer per shared registry (the structural-finding vocabulary lives in `pathgraph`).

## Exit criteria

- [ ] All tests pass · coverage ≥ 95 % · `ruff` zero · `mypy --strict` clean · docs linked.
- [ ] Backtest + shadow with the **false-block budget** enforced.
- [ ] ≥ 95 % critical paths `proven_broken`; zero unexplained `unproven` > 14 days *(operational — field-verified at M31)*.
- [ ] Intake ≤ 48 h for ≥ 80 % *(operational)*; 100 % facts cited; dual-use screen clean.

**Closure:** standard (implemented · gates run once · committed · pushed · issue closed · docs updated · checkpoint in the index).
