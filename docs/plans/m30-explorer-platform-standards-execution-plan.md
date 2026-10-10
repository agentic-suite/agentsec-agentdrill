# agentdrill M30 — Trace Explorer, Platform Matrix & Standards Execution Plan

**Spec:** [WBS M30](../wbs/v0.1.0/wbs-v0.1.0-part16-frontier-platform-standards.md) · [design](../design/trace-explorer-and-platform-standards.md) · [PRD 40](../prd/40-trace-explorer.md), [PRD 41](../prd/41-platform-compatibility.md), [PRD 42](../prd/42-standards-and-claims.md).

## Constraints
Local/offline viewer; untrusted content inert; WCAG 2.2 AA. Levels/metrics measured, never asserted. Claims linter mandatory.

## Tasks
- **T1 — Explorer core (30.1):** overview (outcome × tier × witness); case step-through + stage timeline; **defense-vs-witness**; HITL queue. *RED:* failed-CI→root-cause ≤5 min; XSS neutralized. *GREEN.*
- **T2 — Explorer analysis (30.2):** pressure curve; bypass-family tree; diff + attribution; path view; redaction-aware export + deep links; a11y. *RED:* load 10k ≤2 s; axe = 0. *GREEN.*
- **T3 — Matrix (30.3–30.4):** L0–L4 + per-surface rows; prioritization; reference-harness policy (≥2 open at L3+); AWC; nightly canary; host/CI/runtime matrix. *RED:* AWC computed; breakage caught ≥90%. *GREEN.*
- **T4 — Standards (30.5–30.7):** claims linter; master table + version pins + drift watcher; ASI + ATLAS-mitigation coverage; evidence index; participation. *RED:* 0 linter violations; 0 drift. *GREEN.*
- **T5 — Gates + docs (30.T/.C/.L/.CR/.D).**

**Exit:** explorer usable + a11y verified; AWC ≥0.60 published; claims linter green; evidence index with explicit gaps. **Closure:** standard.
