# WBS v0.1.0 — Part 13: Effect Verification & Bypass Search (M23–M24)

**BLUF:** M23 makes the oracle **non-circular** — independent effect witnesses outside the defended stack
plus a reusable Adversary Lab. M24 adds the **attacker-strength dimension** (`Hold@k`, pressure curves) and
an **effect-based bypass search** with minimization and auto-regression. These are the two P0
credibility-defining additions ([PRD 26](../../prd/26-independent-effect-witness.md),
[PRD 27](../../prd/27-adversary-lab.md), [PRD 25](../../prd/25-attacker-strength-and-pressure.md),
[PRD 28](../../prd/28-policy-bypass-search.md)).

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M23 — Independent effect witness & adversary lab — ✅ COMPLETE (2026-10-23)

**Goal:** adjudicate enforcement by **observed effects**, not the defense's own log, and ship a
seed-deterministic hostile-environment kit. Closes G2 and G3.

**Status:** ✅ Complete · **Execution plan:** [m23-effect-witness-execution-plan](../../plans/m23-effect-witness-execution-plan.md) · **Issues:** #288–#300

**Requirements / PRDs:** [PRD 26](../../prd/26-independent-effect-witness.md), [PRD 27](../../prd/27-adversary-lab.md)
(R61, R62), features F87, F88.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 23.1 | Effect declarations (F87) | Cases declare **forbidden effects** and **required-preserved effects**; schema + loader support | schema | cases without effects flagged | #288 |
| 23.2 | FS + network witnesses (F87) | Canary file/dir hash+inode watcher; loopback sinkhole (HTTP/DNS/TCP) with per-run tokens | witnesses | effect seen when it happens; ≤2 s median overhead | #289 |
| 23.3 | Credential + process witnesses (F87) | Honey credentials/canary tokens (use observed by verifier); process/syscall witness (Linux) | witnesses | credential use + exec detected | #290 |
| 23.4 | Side-effect ledger + human-surface (F87) | Witness DB / mock SaaS recording calls; approval-dialog vs executed-action check | witnesses | business-logic + approval effects detected | #291 |
| 23.5 | Two-oracle verdict + integrity (F87) | Compare defense decision × witness → `blocked`/`missed`/`degraded`/`blocked_silently`/`witness_discrepancy`; `witness_unavailable`; tamper-evident log; `witness` live/none label | oracle | disagreement is a first-class finding | #292 |
| 23.6 | Adversary Lab core (F88) | Versioned loopback lab: evil MCP server (poisoning/shadow/overlap/preference/rug-pull/return-injection), test IdP/OAuth, hostile registries, rogue upstream API, evil A2A peer, sinks | lab | same seed ⇒ same lab event log (≥ 99.9%) | #293 |
| 23.7 | Poisoned content corpus (F88) | ≥12 carriers (HTML/CSS-hidden, markdown, PDF, DOCX, spreadsheet, image, email, calendar, issues/PRs/README, chat); parameterized from documented patterns | corpus | carrier matrix runnable | #294 |
| 23.8 | Lab isolation + ground truth (F88) | Loopback-only enforcement (egress allowlist); ground-truth event log; `lab@version` pinned in manifest | isolation | zero non-loopback egress | #295 |
| 23.T | Tests for this milestone | Witness detection matrix; seeded faulty-defense discrepancy detection; lab determinism; carrier matrix; egress violation | tests | all new paths covered; coverage ≥ 95% | #296 |
| 23.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #297 |
| 23.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #298 |
| 23.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #299 |
| 23.D | Design + reference docs | Witness contract, lab catalog, effect declaration format | docs | docs updated + linked here | #300 |

**Tests required:** planted faults detected via `witness_discrepancy` (≥ 99%); efficacy twin effect seen;
witness FS/network parity macOS↔Linux; lab determinism; ≥12 carriers; zero lab egress.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] ≥ 90% enforcement cases witnessed; `blocked` without witness is labeled
- [x] Disagreement (`witness_discrepancy`) is emitted as a finding
- [x] Adversary Lab deterministic, loopback-only, ground-truth-logged, version-pinned

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 26](../../prd/26-independent-effect-witness.md) · [PRD 27](../../prd/27-adversary-lab.md) ·
[PRD 06](../../prd/06-security-baseline.md).

---

## Milestone M24 — Attacker strength, pressure & bypass search — ✅ COMPLETE (2026-10-23)

**Goal:** label every number by **attacker capability** (`Hold@k`/`ASR@k` + CIs, pressure curves) and search
the **route space** to a forbidden effect with minimization + auto-regression. Closes G1, G4, and the T1
tension (T3 deferred). Builds on M23's witness.

**Status:** ✅ Complete · **Execution plan:** [m24-attacker-strength-execution-plan](../../plans/m24-attacker-strength-execution-plan.md) · **Issues:** #301–#313

**Requirements / PRDs:** [PRD 25](../../prd/25-attacker-strength-and-pressure.md), [PRD 28](../../prd/28-policy-bypass-search.md)
(R59, R60, R63), features F85, F86, F89.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 24.1 | Attacker tiers (F85) | T0 static · T1 repeated (k∈{1,5,10,25}, seeded) · T2 documented-pattern mutation (F40 caps; mutation path in manifest) · **T3 stub deferred, RoE-gated, local-only** | tiers | results carry tier + k + effort | #301 |
| 24.2 | `Hold@k` / `ASR@k` metrics (F86) | All-of-k and any-of-k per case/class; bootstrap CIs (F55); first-break distribution (p50/p95); attacker cost-to-break | metrics | bare percentage not renderable | #302 |
| 24.3 | Pressure curves + claim scope (F86) | Curves (ASR vs k / budget); auto claim-scope statement; `brittle` label (T0-hold/T2-break) | report | curve + scope on every tiered case | #303 |
| 24.4 | `Hold@k` CI gate (F86) | Configurable gate (default k=5 PR, 25 nightly) on critical must-block cases | gate | `Hold@5 < 100%` blocks | #304 |
| 24.5 | Route-family library (F89) | Effect goals × families (command/path/encoding/indirection/tool-overlap/multi-step/transport/timing); ≥12 effects catalogued | catalog | families reviewed like packs | #305 |
| 24.6 | Bounded search engine (F89) | Seeded breadth-over-families then depth; budgets; family-level pruning; runs only under RoE | engine | same seed ⇒ same sequence (≥ 99%) | #306 |
| 24.7 | Minimization + dedup + promotion (F89) | Delta-debug minimization (≥5× median); family dedup; auto-promote confirmed bypass to regression (F61) with attribution (F38) | engine | bypass → regression same release (100%) | #307 |
| 24.8 | Coverage report (F89) | Per-effect tried/blocked/bypassed/untried; diff-aware subset for rule changes | report | coverage explicit; rest `untried` | #308 |
| 24.T | Tests for this milestone | Tier labeling; Hold@k/ASR@k math + CIs; gate; seeded-bypass recall; determinism; minimization; promotion | tests | all new paths covered; coverage ≥ 95% | #309 |
| 24.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #310 |
| 24.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #311 |
| 24.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #312 |
| 24.D | Design + reference docs | Tier taxonomy, metric definitions, route-family catalog, dual-use boundary note | docs | docs updated + linked here | #313 |

**Tests required:** tier + k + CI present on every published cell; determinism of T1/T2; seeded-bypass
recall ≥ 95% and false-bypass ≤ 2%; minimization ratio; auto-regression wiring; coverage report; zero T3
payload leakage; governed by [PRD 35](../../prd/35-rules-of-engagement-and-safe-fire.md).

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Every published number carries tier + k + CI; `brittle` surfaced
- [x] Bypass search has ≥90% route-family coverage per P0 effect; confirmed bypass → regression
- [x] T3 remains deferred (decision recorded), local-only when introduced

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 25](../../prd/25-attacker-strength-and-pressure.md) · [PRD 28](../../prd/28-policy-bypass-search.md) ·
[PRD 14](../../prd/14-non-goals.md).

---

Part 13 green ⇒ the oracle is effect-based and attacker-strength-aware; proceed to
[Part 14](wbs-v0.1.0-part14-byod-integrations.md) (M25–M26).
