# PRD 40 — Trace Explorer

**BLUF:** Reviewer time dominates the cost of a drill program. Best-in-class OSS ships a viewer (promptfoo `view`, Inspect View, garak HTML). agentdrill has a static HTML report (F58) and a file-based HITL queue (F44) — good artifacts, poor investigation. Add a **local-first, offline run explorer**: run overview, case step-through with the **stage timeline**, a unique **defense-vs-witness** panel ([PRD 26](26-independent-effect-witness.md)), the **pressure curve** ([PRD 25](25-attacker-strength-and-pressure.md)), **bypass families** ([PRD 28](28-policy-bypass-search.md)), run/config/pack **diff** with attribution (F38), a keyboard-first HITL queue, and redaction-aware export. Untrusted content renders inert; the viewer is itself in the evasion pack.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F102 · **Reqs:** R76

## Why

- Reading trajectories, judging gray cases, tracing *where the chain broke*, and diffing runs is where hours go.
- The defense-vs-witness view is new and uniquely valuable — it needs a UI to be usable.
- Integrations ([PRD 38](38-security-ecosystem-integrations.md)) need a deep-link target.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R76** | A **local, offline-capable** run explorer provides overview, case step-through + stage timeline, defense-vs-witness panel, pressure curve, bypass-family tree, diff/attribution, HITL adjudication, and redaction-aware export — with untrusted content rendered inert and WCAG 2.2 AA on core flows. | Median failed-CI → root-cause ≤ 5 min (study); ≥ 30 adjudications/hour; load 10k cases ≤ 2 s p95; zero XSS. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F102** | **Trace explorer**: run overview (outcome × tier × witness; filters by ASI/ATLAS/tag/severity/stage; `untested` visible) · case page with step-through + **stage timeline** (F37) · **defense-vs-witness** panel highlighting `witness_discrepancy` · **pressure curve** (PRD 25) · **bypass-family tree** (PRD 28) · **diff** (run/config/pack) with attribution (F38) · keyboard-first **HITL queue** (verdicts export as labeled data, F83) · redaction-aware evidence export (F27/F65) · **path view** (PRD 31) · static redacted share + deep links | R76 | Renders untrusted content inert (TelemetryInjection class); viewer included in evasion pack (F11) |

## CUJs

### CUJ-58 — From red CI to root cause
A failed check deep-links into the case; the reader sees the failing stage and the witness evidence in ~30 s. **Success:** ≤ 5 min median.

### CUJ-59 — Adjudicate at speed
Clear 30 divergence cases in an hour with keyboard shortcuts. **Success:** ≥ 30/hour/reviewer.

## Success metrics

| Metric | Target |
|---|---|
| Median failed-CI → root-cause stage identified (user study, n≥10) | ≤ 5 min |
| HITL adjudication throughput | ≥ 30 cases/hour/reviewer |
| Load time, 10k-case run p95 | ≤ 2 s |
| Fully offline / zero network calls (test-verified) | 100% |
| axe critical/serious violations (WCAG 2.2 AA core flows) | **0** |
| Untrusted-content XSS/injection tests (evasion pack) | 100% neutralized |
| Deep-link resolution from SARIF/ticket | ≥ 99% |
| Viewer opened on failed gates (adoption proxy) | ≥ 60% |
| Redaction leaks in shared exports (scanner) | **0** |

## Dependencies
F27, F37, F38, F44, F48, F56, F58, F65, F83 · [PRD 25](25-attacker-strength-and-pressure.md), [PRD 26](26-independent-effect-witness.md), [PRD 28](28-policy-bypass-search.md), [PRD 31](31-attack-path-and-blast-radius.md), [PRD 38](38-security-ecosystem-integrations.md).

## Boundaries & non-goals
- Not a hosted dashboard/SaaS; no mandatory server.
- Scope discipline: ship case page, defense-vs-witness, diff first; resist UI sprawl.
- Accessibility and inert rendering are acceptance criteria, not polish.

## Open questions
1. Reuse Inspect View via export vs. build native (recommend: native witness panel; Inspect-format export for compat).
2. Web view vs. terminal (recommend: web + minimal TUI summary).
