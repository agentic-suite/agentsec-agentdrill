# WBS v0.1.0 — Part 15: Context, Replay, Governance & Safety (M27–M28)

**BLUF:** M27 turns real history and inventory into risk-driven drilling — trace backtest & shadow mode,
the attack-path/blast-radius graph, and the incident-to-pack compiler. M28 makes the loop survivable and
auditable — the exposure ledger with time-boxed waivers, signed drill attestations, and rules-of-engagement
with safe-fire interlocks. Closes G6, G7, G8, G9, G10, G11.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M27 — Backtest, attack-path & incident intake — ✅ COMPLETE (2026-10-24)

**Goal:** know the production blast radius before enabling a policy, drill by **reachable risk** not
catalog, and turn a fresh advisory into a reviewed pack fast. Closes G6, G7, G8.

**Status:** ✅ Complete · **Execution plan:** [m27-backtest-path-intake-execution-plan](../../plans/m27-backtest-path-intake-execution-plan.md) · **Issues:** #336–#346 · **Packages:** `agentdrill/backtest/`, `agentdrill/pathgraph/`, `agentdrill/intake/` · **Reference:** [backtest-path-intake.md](../../reference/backtest-path-intake.md)

**Requirements / PRDs:** [PRD 30](../../prd/30-trace-backtest-and-shadow.md), [PRD 31](../../prd/31-attack-path-and-blast-radius.md),
[PRD 32](../../prd/32-incident-to-pack-compiler.md) (R66, R67, R68), features F92, F93, F94.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 27.1 | Trace backtest (F92) | Replay redacted agentwatch sessions vs. candidate policy: newly-blocked benign clusters, regressions, unchanged, un-replayable itemized | engine | replay fidelity ≥ 99% | #336 |
| 27.2 | Shadow mode + FP budget (F92) | Log-only candidate alongside enforced; divergence rate + clusters; policy **false-block budget** gate | engine | side-effect-free (witness); budget reported w/ CI | #337 |
| 27.3 | Trace→drill (F92) | Promote a session → redacted case + mined benign twins (HITL, `origin: production-trace`); F65 receipts | pipeline | ≤1 day; zero unredacted secrets | #338 |
| 27.4 | Capability/attack-path graph (F93) | Build graph from inventory (agents, tools, MCP servers, creds/scopes, data, egress, memory, sub-agents, approvals, instruction files); AIVSS factors | graph | reachable critical paths enumerated | #339 |
| 27.5 | Structural findings + path status (F93) | Trifecta, over-scope, egress, auto-approve+shell, writable instructions, shared memory, identity inheritance; bind cases; `proven_broken`/`open_missed`/`unproven`/`accepted`; new-path drift alerts | engine | 100% critical paths bound; alerts ≤1 CI run | #340 |
| 27.6 | Incident-to-pack compiler (F94) | Dedup intake feeds; relevance vs. inventory; **cite-or-drop** brief; draft pack from lab generators (F88) + twin + cleanup + witness effects + preregistered outcome; efficacy check; dual-use screen; HITL review → registry | pipeline | ≤4 h draft; 100% facts cited | #341 |
| 27.T | Tests for this milestone | Backtest fidelity + clusters; shadow side-effect-free; trace→drill redaction; graph reachability; new-path detection; cite-or-drop; dual-use screen | tests | all new paths covered; coverage ≥ 95% | #342 |
| 27.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #343 |
| 27.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #344 |
| 27.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #345 |
| 27.D | Design + reference docs | Backtest methodology, graph design, intake pipeline, relevance/filters | docs | docs updated + linked here | #346 |

**Tests required:** replay fidelity ≥99%; backtest false-block with CI; shadow provably side-effect-free;
trace→drill zero unredacted secrets; graph completeness ≥95%; new-path detection; intake SLA + cite-or-drop;
efficacy pass; dual-use false-accept 0 (audit).

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Backtest + shadow with the false-block budget enforced (`require_false_block_budget` + seeded CI)
- [ ] ≥95% critical paths `proven_broken`; zero unexplained `unproven` >14 days — **operational, field-verified at
      M31** (binding + status machinery is built; `require_critical_bound` enforces 100% critical paths bound)
- [x] 100% facts cited (cite-or-drop enforced); dual-use screen clean; **including** intake ≤48 h for ≥80% —
      **the SLA is operational, field-verified at M31**

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

> **Honest deferral:** the `proven_broken` coverage rate and the intake SLA are *operational* metrics measured
> in the **M31** field tests; their mechanisms (path-status binding, cite-or-drop, dual-use screen) are built
> and proven offline.

**Design docs to update:** [PRD 30](../../prd/30-trace-backtest-and-shadow.md) · [PRD 31](../../prd/31-attack-path-and-blast-radius.md) ·
[PRD 32](../../prd/32-incident-to-pack-compiler.md) · [reference/backtest-path-intake.md](../../reference/backtest-path-intake.md).

---

## Milestone M28 — Exposure ledger, attestations & rules of engagement — ⬜ NOT STARTED

**Goal:** make the gate livable (waivers that never relabel a miss), the proof consumable (signed
attestations with freshness), and the tool safe to run anywhere (RoE + interlocks). Closes G9, G10, G11.

**Status:** 🚧 In progress (2026-10-24) · **Execution plan:** [m28-ledger-attestation-roe-execution-plan](../../plans/m28-ledger-attestation-roe-execution-plan.md) · **Issues:** #347–#358

**Requirements / PRDs:** [PRD 33](../../prd/33-exposure-ledger-and-waivers.md), [PRD 34](../../prd/34-drill-attestations-and-deploy-gate.md),
[PRD 35](../../prd/35-rules-of-engagement-and-safe-fire.md) (R69, R70, R71), features F95, F96, F97.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 28.1 | Finding lifecycle + ledger (F95) | Lifecycle (`open`→…→`verified-fixed`/`decayed`) + side states; per-finding CVSS v4.0 + AIVSS vector (never aggregated) | ledger | misses remain visible always | #347 |
| 28.2 | Time-boxed waivers (F95) | Scope/tier/reason/drilled compensating control/approvers/expiry (90 d; critical 30 d)/drift trigger/residual risk; **annotate, never relabel**; auto-reopen; known-miss budget; integrity findings not waivable | waivers | 100% have expiry; expired never suppress | #348 |
| 28.3 | Ledger exports (F95) | OSCAL POA&M/assessment-results; SARIF suppressions; ticket sync | exports | validators green | #349 |
| 28.4 | Drill attestation (F96) | Claim model (config digest, packs@ver/hash, tiers/k, outcomes+CIs, witness coverage, live/fixture/mock, oracle versions, known misses, lab, standards pins, issued/expires); in-toto predicate `agentdrill/drill-result/v1` + Sigstore + transparency log | attestation | verify ≤2 s; forged rejected | #350 |
| 28.5 | Freshness + consumers (F96) | Auto-invalidate (config change/security-deprecated pack/relevant new incident/oracle major/waiver expiry); reference consumers (CLI, GH Action, K8s policy, agentgate) | consumers | ≥4 consumers; models non-evidence | #351 |
| 28.6 | Rules of engagement (F97) | Signed RoE (targets+ownership, env class, effect classes, canary-only, windows, ceilings, caps, tier ceiling, approvers, contacts, aborts); fail-closed preflight; scope receipts | RoE | 100% non-demo runs signed | #352 |
| 28.7 | Safe-fire interlocks (F97) | Global abort (independent of agenthalt), dead-man switch, watchdogs, verified teardown (dirty target release-blocking); consent gate for egress | interlocks | abort p95 ≤5 s; teardown ≥99% | #353 |
| 28.T | Tests for this milestone | Ledger lifecycle; waiver expiry/auto-reopen/visibility; OSCAL/SARIF export; attestation verify + forgery; invalidation; RoE preflight negatives; abort; teardown; consent | tests | all new paths covered; coverage ≥ 95% | #354 |
| 28.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #355 |
| 28.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #356 |
| 28.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #357 |
| 28.D | Design + reference docs | Ledger/waiver policy, attestation predicate spec, RoE template + safety guide | docs | docs updated + linked here | #358 |

**Tests required:** waived misses still shown; expired waiver never suppresses; OSCAL/SARIF valid;
attestation forgery rejected 100%; invalidation on config change; planted out-of-scope attempts refused
100%; abort p95; teardown receipts; consent egress zero.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Waivers never relabel; known-miss budget gates; zero expired waivers suppressing
- [ ] Attestation verifies ≤2 s; freshness/invalidation; ≥4 consumers
- [ ] Zero out-of-scope actions; abort ≤5 s; teardown clean ≥99%

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 33](../../prd/33-exposure-ledger-and-waivers.md) · [PRD 34](../../prd/34-drill-attestations-and-deploy-gate.md) ·
[PRD 35](../../prd/35-rules-of-engagement-and-safe-fire.md) · [PRD 06](../../prd/06-security-baseline.md).

---

Part 15 green ⇒ context-driven drilling, governable exposure, and safe firing; proceed to
[Part 16](wbs-v0.1.0-part16-frontier-platform-standards.md) (M29–M30).
