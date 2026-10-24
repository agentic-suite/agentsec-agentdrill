# Trace Explorer, Platform Matrix & Standards — Design

**BLUF:** Make investigation fast, "compatible" measurable, and every claim defensible. A local run explorer
(including the unique **defense-vs-witness** view), a graded platform compatibility matrix, and the claims
vocabulary + standards tables. WBS [M30](../wbs/v0.1.0/wbs-v0.1.0-part16-frontier-platform-standards.md).
Reference: [PRD 40](../prd/40-trace-explorer.md), [PRD 41](../prd/41-platform-compatibility.md),
[PRD 42](../prd/42-standards-and-claims.md).

> **Built (M30).** Packages: `agentdrill/explorer/` (`view.py`, `analysis.py`),
> `agentdrill/platform/` (`matrix.py`, `versioning.py`), `agentdrill/standards/` (`claims.py`, `registry.py`,
> `participation.py`). See the [reference](../reference/trace-explorer-and-platform-standards.md). Rewritten
> against the built system at M31–M32.

## Trace explorer (F102)

`agentdrill view` — local, offline, no service:

- **Run overview:** outcome × tier × witness; filters by ASI/ATLAS/tag/severity/stage; `untested` visible.
- **Case page:** chain step-through + **stage timeline** (F37).
- **Defense-vs-witness panel:** decision log vs. observed effect (M23); `witness_discrepancy` highlighted.
- **Pressure curve** (M24); **bypass-family tree** (M24); **diff** + attribution (F38); **path view** (M27).
- **HITL queue:** keyboard-first adjudication; verdicts export as labeled data (F83).
- **Export/share:** redaction-aware bundle (F27/F65); static redacted share; deep links for SARIF/tickets.

**Security:** untrusted content (payloads, tool names) rendered **inert** (no eval, escaped, sandboxed
iframes); the viewer is itself in the evasion pack. **A11y:** WCAG 2.2 AA on core flows.

## Platform compatibility (F103)

Levels: **L0 listed · L1 config-aware · L2 driven · L3 observed (witnessed) · L4 gated (contract pack in
CI)**. Prioritization model `0.30·Adoption + 0.25·AttackSurface + 0.20·Driveability + 0.15·Reproducibility +
0.10·Strategic`. **Reference-harness policy:** ≥2 open-source harnesses at L3+; headline tables use open
harnesses; proprietary results in a separate table. **Version-follow SLA:** matrix ≤7 d (L4 ≤72 h); nightly
driver canary. One published number: **adoption-weighted coverage (AWC)**. Per-surface rows (CLI vs. IDE).
Target inventory + per-harness surfaces: [PRD 41](../prd/41-platform-compatibility.md).

## Standards & claims (F104)

**Claim vocabulary:** *Conforms to · Maps to · Interoperates with · Aligned with* — "compliant/certified/
secure" **banned**, enforced by a **claims linter** over docs/notes/UI. Master standards table, **version
pins + drift watcher**, ASI/ATLAS coverage incl. `untested`, a **ATLAS-mitigation** mapping, and a per-release
**evidence index** with explicit `not covered`. Full tables: [PRD 42](../prd/42-standards-and-claims.md).

## Invariants

1. No hosted viewer/service required; no composite exposure score.
2. Levels/metrics are measured, never asserted; "defaults vs. auto-approve" always labeled.
3. Untrusted content is inert in the UI.

## Open questions
1. Reuse Inspect View via export vs. native viewer (recommend native witness panel + Inspect export).
2. Per-surface rows as separate matrix rows.
3. OCSF class mapping; AIUC-1/AICM assessor acceptance of attestations.
