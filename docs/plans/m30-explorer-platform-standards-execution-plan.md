# agentdrill M30 — Trace Explorer, Platform Matrix & Standards Execution Plan

**Spec:** [WBS M30](../wbs/v0.1.0/wbs-v0.1.0-part16-frontier-platform-standards.md) · [design](../design/trace-explorer-and-platform-standards.md) · [PRD 40](../prd/40-trace-explorer.md), [PRD 41](../prd/41-platform-compatibility.md), [PRD 42](../prd/42-standards-and-claims.md).

**Status:** 🚧 In progress (2026-10-24) · **Issues:** #371–#382 · Closes **G16** + the platform/standards scope.

## Constraints

- **No hosted viewer/service**; the viewer is local, offline and itself in the evasion pack.
- **Untrusted content is inert** (escaped, no eval, sandboxed iframes); WCAG 2.2 **AA** on core flows.
- Levels and metrics are **measured, never asserted**; **no composite exposure score**; "defaults vs.
  auto-approve" is always labeled.
- Claims vocabulary is enforced: **"compliant/certified/secure" are banned**; the linter is the gate.
- One ticket at a time: test **RED** → implement **GREEN** → next. Full suite at milestone end only.

## Prerequisites

- Consumes **M10** (`reporting/` — `TraceStore`, trends, heat-map), **M12** (kill-chain stage timeline F37),
  **M23** (`witness/` verdicts), **M24** (pressure curves, bypass families), **M27** (path view), **M9**
  (attribution F38), **M19** (HITL adjudication F83), **M18** (`lifecycle/privacy` — redaction-aware export),
  **M17** (`interop/tagging`, compliance), **M26** (`integrations` — deep links for SARIF/tickets).

## Tasks

- **T1 — Explorer core (30.1, #371).** Run overview (outcome × tier × witness; filters; `untested` visible);
  case step-through + stage timeline (F37); **defense-vs-witness** panel (`witness_discrepancy` highlighted);
  HITL queue. *RED:* failed-CI→root-cause ≤5 min (usability, evidenced by the built flows). *GREEN.*
- **T2 — Explorer analysis (30.2, #372).** Pressure curve (M24); bypass-family tree (M24); diff + attribution
  (F38); path view (M27); redaction-aware export + deep links; **inert rendering + a11y**. *RED:* load 10 k
  ≤2 s; zero XSS; WCAG AA. *GREEN.*
- **T3 — Compatibility levels + matrix (30.3, #373).** L0–L4 with evidence; per-surface rows; prioritization
  model; reference-harness policy (≥2 open at L3+); **AWC** metric. *RED:* AWC computed; ≥2 Tier-1 at L2+.
- **T4 — Version-follow SLA + drivers (30.4, #374).** Nightly driver canary; matrix ≤7 d (L4 ≤72 h);
  "defaults vs auto-approve" labels; host/CI/model-runtime matrix incl. a local-first judge-free subset.
- **T5 — Claims linter (30.5, #375).** Claim vocabulary (Conforms/Maps/Interoperates/Aligned; **ban**
  compliant/certified/secure) enforced over docs/notes/UI.
- **T6 — Master table + pins (30.6, #376).** Master standards table with version pins + drift watcher; ASI
  coverage + ATLAS-mitigation mapping; per-framework evidence index with explicit `not covered`.
- **T7 — Standards participation (30.7, #377).** Submissions tracker (OWASP ASI, MITRE ATLAS, NIST CAISI,
  IETF BMWG, OTel SIG) + mapping repo; ≥1 in review per release.
- **T8 — Gates + docs (30.T #378 · 30.C #379 · 30.L #380 · 30.CR #381 · 30.D #382).** tests; coverage ≥95 %;
  `ruff` + `mypy --strict`; review log; viewer guide + compatibility matrix + standards/claims docs.

## Module ownership (single-writer files)

- New packages `agentdrill/explorer/` (30.1–30.2), `agentdrill/platform/` (30.3–30.4),
  `agentdrill/standards/` (30.5–30.7) — proposed.
- **Reuse, do not fork:** `reporting/` (traces/trends), `killchain/` (stages), `witness/`, `attacker/`,
  `pathgraph/`, `comparison/` (attribution), `lifecycle/privacy` (redaction), `integrations` (deep links).
- The **claims vocabulary** and the **standards master table/pins** are single-writer here.

## Exit criteria

- [ ] All tests pass · coverage ≥95 % · `ruff` zero · `mypy --strict` clean · docs linked.
- [ ] Explorer: witness-vs-defense view usable; a11y + **inert rendering** verified (zero XSS).
- [ ] Matrix L0–L4 + **AWC** published; reference-harness policy honored; version-follow SLA labeled.
- [ ] Claims linter green; master standards table pinned; evidence index lists explicit **not covered**.

**Closure:** standard (implemented · gates run once · committed · pushed · issue closed · docs updated · checkpoint).
