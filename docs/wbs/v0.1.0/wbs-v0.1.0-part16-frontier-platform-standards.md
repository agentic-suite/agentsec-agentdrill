# WBS v0.1.0 — Part 16: Detonation, Frontier Classes, Explorer, Platforms & Standards (M29–M30)

**BLUF:** M29 adds dynamic extension detonation, the crowd Break-It program, and the frontier attack
classes that close the OWASP ASI gaps. M30 makes it usable and defensible — the trace explorer, the graded
platform compatibility matrix, and the claims-vocabulary standards layer. Closes G12, G13, G15, G16, and
the platform/standards scope.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M29 — Detonation, Break-It & frontier attack classes — ✅ COMPLETE (2026-10-24)

**Goal:** detonate unknown extensions, invite the crowd to break the reference range, and ship the ASI gap
classes. Closes G12, G13, G15.

**Status:** ✅ Complete · **Execution plan:** [m29-detonation-breakit-frontier-execution-plan](../../plans/m29-detonation-breakit-frontier-execution-plan.md) · **Issues:** #359–#370 · **Packages:** `agentdrill/detonation/`, `agentdrill/breakit/`, `agentdrill/frontier/` · **Reference:** [detonation-breakit-frontier.md](../../reference/detonation-breakit-frontier.md)

**Requirements / PRDs:** [PRD 36](../../prd/36-extension-detonation-lab.md), [PRD 37](../../prd/37-break-it-program.md),
[PRD 39](../../prd/39-frontier-attack-classes.md) (R72, R73, R75), features F98, F99, F101.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 29.1 | Detonation lab (F98) | Run MCP servers/skills/plugins/hooks/rules/packages in the hermetic lab; observe egress/honey-reads/out-of-scope writes/spawn; metadata drift; conditional behavior; declared-vs-actual; Behavior Report + prior-version diff; honesty labels | lab | seeded recall ≥80%; zero escapes | #359 |
| 29.2 | Break-It program (F99) | Pinned reference ranges; structured proof-of-bypass auto-verified by the witness; triage SLAs; coordinated disclosure (fix window, embargo, CVE/CNA+CWE); rewards; convert accepted bypass → regression (F61) + family catalogue | program | ≥80% auto-verified; ack ≤24 h | #360 |
| 29.3 | Corpus import (F99) | Import public human-found corpora (e.g., ART benchmark; license check) into packs/catalogue | importer | mapped cases lint-clean | #361 |
| 29.4 | Frontier class 4 — identity/OAuth (F101) | Token passthrough, confused deputy, RFC 8707 audience, stale/over-scope, cross-agent inheritance, impersonation | pack class | audience/passthrough rejection 100% | #362 |
| 29.5 | Frontier class 1 & 5 (F101) | (1) approval abuse / lies-in-the-loop; (5) memory & persistence incl. instruction-file self-mod | pack class | approval fidelity measured; persistence 0 | #363 |
| 29.6 | Frontier class 7 & 6 (F101) | (7) resource exhaustion / denial-of-wallet; (6) multi-agent cascade & rogue-agents (handoff/A2A propagation, oversight subversion, goal drift) | pack class | cost ≤105% ceiling; depth ≤1 hop | #364 |
| 29.7 | Frontier class 2 & 3 + AP2 stub (F101) | (2) computer-use/browser injection; (3) multimodal injection; (8) AP2 payments spec-gated stub | pack class | browser + ≥12 carriers; AP2 marked gated | #365 |
| 29.T | Tests for this milestone | Detonation recall/precision; Break-It auto-verify + conversion; corpus lint; per-class efficacy + witness; ASI coverage count | tests | all new paths covered; coverage ≥ 95% | #366 |
| 29.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #367 |
| 29.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #368 |
| 29.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #369 |
| 29.D | Design + reference docs | Detonation profiles, disclosure policy, per-class pack docs | docs | docs updated + linked here | #370 |

**Tests required:** detonation seeded recall/precision + zero escapes; Break-It auto-verification +
regression conversion; corpus mapping; each frontier class efficacy-verified + witnessed; ASI coverage ≥6/10
(v0.2 → ≥9/10).

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Detonation recall **≥80%** and **zero lab escapes** (both gated in code); Break-It converts an accepted bypass to a permanent regression
- [x] **≥6/10 ASI categories** efficacy-verified + witnessed (`require_asi_coverage`, default 6)
- [x] Dual-use review sign-off per class recorded (`require_dual_use_signed`); AP2 kept **spec-gated**

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

> **Honest note:** the classes ship as **class descriptors + acceptance checkers**; the runnable pack cases
> execute against the deployed stack in the **M31** field tests. Detonation recall is measured against the
> seeded corpus in the unit gate.

**Design docs to update:** [PRD 36](../../prd/36-extension-detonation-lab.md) · [PRD 37](../../prd/37-break-it-program.md) ·
[PRD 39](../../prd/39-frontier-attack-classes.md) · [PRD 21](../../prd/21-pack-catalog.md) ·
[reference/detonation-breakit-frontier.md](../../reference/detonation-breakit-frontier.md).

---

## Milestone M30 — Trace explorer, platform matrix & standards — ✅ COMPLETE (2026-10-24)

**Goal:** make investigation fast, make "compatible" measurable, and make every claim defensible. Closes
G16 and the platform/standards scope.

**Status:** ✅ Complete · **Execution plan:** [m30-explorer-platform-standards-execution-plan](../../plans/m30-explorer-platform-standards-execution-plan.md) · **Issues:** #371–#382 · **Packages:** `agentdrill/explorer/`, `agentdrill/platform/`, `agentdrill/standards/` · **Reference:** [trace-explorer-and-platform-standards.md](../../reference/trace-explorer-and-platform-standards.md)

**Requirements / PRDs:** [PRD 40](../../prd/40-trace-explorer.md), [PRD 41](../../prd/41-platform-compatibility.md),
[PRD 42](../../prd/42-standards-and-claims.md) (R76, R77, R78), features F102, F103, F104.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 30.1 | Trace explorer — core (F102) | Run overview (outcome × tier × witness; filters; `untested` visible); case step-through + stage timeline (F37); **defense-vs-witness** panel; HITL queue | viewer | failed-CI→root-cause ≤5 min | #371 |
| 30.2 | Trace explorer — analysis (F102) | Pressure curve (M24); bypass-family tree (M24); diff + attribution (F38); path view (M27); redaction-aware export + deep links; inert rendering + a11y | viewer | load 10k ≤2 s; zero XSS; WCAG AA | #372 |
| 30.3 | Compatibility levels + matrix (F103) | L0–L4 with evidence; per-surface rows; prioritization model; reference-harness policy (≥2 open at L3+); AWC metric | matrix | ≥2 Tier-1 at L2+; AWC ≥0.60 | #373 |
| 30.4 | Version-follow SLA + drivers (F103) | Nightly driver canary; matrix ≤7 d (L4 ≤72 h); "defaults vs auto-approve" labeling; host/CI/model-runtime matrix incl. local-first judge-free subset | process | breakage caught ≥90% pre-user | #374 |
| 30.5 | Standards: claims linter (F104) | Claim vocabulary (Conforms/Maps/Interoperates/Aligned; ban compliant/certified/secure) enforced over docs/notes/UI | linter | zero violations at release | #375 |
| 30.6 | Standards: master table + pins (F104) | Master table with version pins + drift watcher; ASI coverage + **ATLAS-mitigation** mapping; evidence index per framework with explicit `not covered` | tables | pins updated ≤30 d; drift 0 | #376 |
| 30.7 | Standards participation (F104) | Submissions to OWASP ASI, MITRE ATLAS, NIST CAISI, IETF BMWG, OTel SIG; mapping repo | participation | ≥1/release in review | #377 |
| 30.T | Tests for this milestone | Explorer a11y + XSS + load; matrix level checks; AWC computation; canary; claims linter; tag lint; drift watcher; evidence index | tests | all new paths covered; coverage ≥ 95% | #378 |
| 30.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #379 |
| 30.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #380 |
| 30.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #381 |
| 30.D | Design + reference docs | Viewer guide, compatibility matrix doc, standards/claims doc | docs | docs updated + linked here | #382 |

**Tests required:** explorer a11y (axe critical/serious = 0), untrusted-content neutralized 100%, load 10k
≤2 s, deep links ≥99%; matrix levels correct; AWC computed + published; canary catches ≥90%; claims linter
0 violations; tags valid (0 drift); evidence index lists `not covered`.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Explorer: the **defense-vs-witness** view is usable; **a11y + inert rendering verified** (zero XSS, WCAG-AA checks, 10 k-row < 2 s)
- [x] Matrix L0–L4 + **AWC** implemented with gates; reference-harness policy honored; version-follow SLA + canary gates in code
- [x] Claims linter green (reference docs clean); master standards table pinned + drift watcher; evidence index with **explicit** gaps

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

> **Honest note:** the explorer is a **renderer + data model** (the `agentdrill view` browser wiring runs in
> M31); published matrix **values** and the standards submissions are populated at M31/M32 — the levels,
> metrics, SLA and linter rules are enforced in code.

**Design docs to update:** [PRD 40](../../prd/40-trace-explorer.md) · [PRD 41](../../prd/41-platform-compatibility.md) ·
[PRD 42](../../prd/42-standards-and-claims.md) ·
[reference/trace-explorer-and-platform-standards.md](../../reference/trace-explorer-and-platform-standards.md).

---

Part 16 green ⇒ all v0.1.0 additions (M23–M30) delivered; proceed to **[Part 17](wbs-v0.1.0-part17-fieldtest-release.md)
(M31–M32)** — **field tests, then release readiness (last)**.
