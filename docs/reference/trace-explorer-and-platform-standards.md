# Trace Explorer, Platform Matrix & Standards — Reference

**BLUF:** Make investigation fast, "compatible" measurable, and every claim defensible. A local run
explorer (including the **defense-vs-witness** view), a graded platform compatibility matrix, and the
claims vocabulary + standards tables. **Normative (M30).** Packages: `agentdrill/explorer/`,
`agentdrill/platform/`, `agentdrill/standards/`. Source design:
[design/trace-explorer-and-platform-standards.md](../design/trace-explorer-and-platform-standards.md); PRD
[40](../prd/40-trace-explorer.md) (R76), [41](../prd/41-platform-compatibility.md) (R77),
[42](../prd/42-standards-and-claims.md) (R78). Closes **G16** + the platform/standards scope.

## Trace explorer (`agentdrill/explorer/`)

Local, offline, no service, no scripts, no network.

| Surface | API | Notes |
|---|---|---|
| Run overview | `build_overview`, `filter_rows` | outcome × tier × witness; **`untested` never hidden**; filters by outcome/tier/tag/severity |
| Case page | `build_case_view` | step-through + **stage timeline** (F37) |
| Defense-vs-witness | `DefenseWitnessPanel` | decision vs. observed effect; `witness_discrepancy` highlighted |
| HITL queue | `hitl_queue` | discrepancies + degraded results (verdicts export as labeled data) |
| Analysis | `render_explorer_html` | pressure curve (M24), bypass families (M24), diff + attribution (F38), attack paths (M27) |
| Share | `export_bundle`, `deep_link` | **redaction-aware** export (F27/F65 receipts); stable `#case-<id>` deep links |

**Security & a11y (gates):** all untrusted content is **escaped/inert** — `a11y_report`/`require_a11y`
enforce **zero XSS** (no `<script>`, no inline event handlers) plus WCAG 2.2 **AA** structural checks; a
10 000-row render is budgeted under **2 s** (`require_load_time`).

## Platform compatibility (`agentdrill/platform/`)

Levels: **L0 listed · L1 config-aware · L2 driven · L3 observed (witnessed) · L4 gated (contract pack in
CI)**. **Evidence is required from L2** — levels are measured, never asserted (`require_levels`).

- Prioritization: `0.30·Adoption + 0.25·AttackSurface + 0.20·Driveability + 0.15·Reproducibility +
  0.10·Strategic` (`priority_score`, `rank_entries`).
- **Reference-harness policy:** ≥2 open-source harnesses at L3+ (`require_reference_harnesses`).
- One published number: **AWC** = adoption-weighted coverage (`awc`, gate ≥ 0.60). **No composite exposure
  score.**
- Version-follow SLA: matrix ≤ 7 days (L4 ≤ 72 h, `require_freshness`); nightly driver canary must catch
  ≥ 90 % of known breakage (`require_canary_detection`); the **"defaults vs auto-approve"** posture is always
  labelled; a **local-first, judge-free** runtime subset is required.

## Standards & claims (`agentdrill/standards/`)

- **Claims linter:** the vocabulary is *Conforms to · Maps to · Interoperates with · Aligned with*.
  **"compliant" / "certified" / "secure" are banned** unless quoted, negated or declared banned
  (`lint_claims`, `require_claims_clean`). The reference docs lint clean.
- **Master table + pins:** `StandardPin` rows with a **drift watcher** (`detect_drift`/`require_no_drift`) and
  a pin-age gate (≤ 30 days). **ASI coverage** shows `untested`; an **ATLAS-mitigation** mapping is published.
- **Evidence index:** per-framework `covered` / `not_covered`; a silent "fully covered" claim is refused
  (`require_explicit_gaps` — set `fully_covered=True` to claim no gaps).
- **Participation:** OWASP ASI, MITRE ATLAS, NIST CAISI, IETF BMWG, OTel SIG; **≥ 1 submission in review per
  release** (`require_bodies_covered`); the **mapping-repository** layout via `mapping_index`.

## Known limitations

- The viewer is a **renderer + data model**, not a running web server; host it as a static file (the
  `agentdrill view` command and browser wiring land in the M31 field run).
- Compatibility levels/metrics are **measured**; the published matrix values are populated at M31/M32.
- The standards submissions and mapping-repo hosting are program work; the rules and layout are enforced here.
