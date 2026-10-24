# WBS v0.1.0 — Part 11: Frontier/DX & Absorption (M20–M21)

**BLUF:** M20 delivers the frontier/developer-experience surface (pack selection/diff, dry-run, templates,
CI-matrix export, assertions, provenance cards, MCP drill surface, fleet mode). M21 verifies the
**absorption ledger** and closes the predecessor's **acknowledged gaps** (G1–G14).

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M20 — Frontier & DX — ✅ COMPLETE (2026-10-23)

**Goal:** the surfaces that make the proof engine disappear into the developer's loop and scale across a
fleet — pack selection/diff, dry-run/explain, templates, CI-matrix export, programmatic assertions,
provenance cards, a read-only MCP drill surface, and fleet mode (R41–R52).

**Status:** ✅ Complete · **Execution plan:** [m20-frontier-dx-execution-plan](../../plans/m20-frontier-dx-execution-plan.md) · **Issues:** #51–#61, #282, #283

**Requirements / PRDs:** [PRD 22](../../prd/22-frontier-dx-features.md), [PRD 05](../../prd/05-features.md)
(R41–R52), features F67, F69, F70, F72, F73, F74, F77, F45.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 20.1 | Pack diff & selection (F67) | `pack diff <a> <b>` (case + coverage delta); `list cases --tag/--target/--difficulty` | CLI | diff matches the case delta | #51 |
| 20.2 | Dry-run & explain (F69) | `run --dry-run` prints bound cases, targets, expected verdicts + evidence; `--explain` annotates why each case exists | CLI | dry-run performs **zero** executions | #52 |
| 20.3 | Pack templates (F70) | `init --template mcp-poisoning\|exfil-chain\|destructive-command\|supply-chain\|…` scaffolds oracle stubs, twins, cleanup, tags | templates | template passes lint + efficacy review | #282 |
| 20.4 | CI-matrix export (F72) | `export ci --format github-actions\|gitlab` emits pack set + manifest + attestation as a matrix | CLI | emitted matrix passes CI dry-run | #283 |
| 20.5 | Programmatic assertions (F73) | Python API (`assert_blocked(case)`, `assert_missed()`, `assert_kill_time_under(x)`) over the same run objects | SDK | assertions green/red against fixtures | #53 |
| 20.6 | Provenance cards (F74) | Machine-readable card per pack (sources, dates, mutation policy, author, reviewers); rendered on results | cards | card renders; reviewer fields non-empty | #54 |
| 20.7 | MCP drill surface (F77) | Read-only MCP server exposing pack/run/result queries; **no write tools**; queries recorded | MCP | tool list contains no write tools | #55 |
| 20.8 | Fleet mode (F45) | One pack across many stacks (opt-in, self-hosted); per-stack honest coverage rollups (CUJ-18) | fleet | per-stack outlier query works | #56 |
| 20.T | Tests for this milestone | Diff; dry-run zero-exec; templates lint+efficacy; CI matrix; assertions; provenance; MCP read-only; fleet rollup | tests | all new paths covered; coverage ≥ 95% | #57 |
| 20.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #58 |
| 20.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #59 |
| 20.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #60 |
| 20.D | Design + reference docs | DX guide, templates catalog, fleet design | docs | docs updated + linked here | #61 |

**Tests required:** pack diff case-delta; dry-run executes nothing (probe); template scaffolds pass lint +
efficacy; CI matrix valid; assertions correct; provenance card fields present; MCP surface has no write
tools; fleet rollup + per-stack breakdown.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Dry-run performs zero executions; assertions embed in a host test suite
- [x] MCP drill surface is read-only (no write tools present)
- [x] Fleet mode produces per-stack honest coverage (CUJ-18)

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 22](../../prd/22-frontier-dx-features.md) · templates catalog · fleet design.

---

## Milestone M21 — Predecessor absorption & gap closure — ⬜ NOT STARTED

**Goal:** verify the **absorption ledger** — every capability inherited from the predecessor is delivered,
delegated, or waived — and that every **acknowledged predecessor gap (G1–G14)** is closed or waived with a
reason. This is the parity gate; nothing carries forward silently.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 10](../../prd/10-feature-parity.md), [PRD 24](../../prd/24-predecessor-gap-closure.md),
[PRD 03](../../prd/03-landscape.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 21.1 | Absorption ledger verification | Every row of [PRD 10](../../prd/10-feature-parity.md) §A/§B is delivered **and tested**, delegated to a named tool, or waived with a reason | ledger | no capability silently dropped | #62 |
| 21.2 | Gap closure G1–G14 | For each gap: a passing test proving closure, or a written waiver (G7 SQLite is waived by design) | closure tests | every gap closed or waived | #63 |
| 21.3 | Parity gate | Executable gate asserting the ledger + closure (fails CI on a regression) | gate | gate green; blocks on drift | #64 |
| 21.4 | Predecessor retention plan | Confirm agentdrill is self-contained; record the M32 instruction to make the predecessor private (never delete) | plan | retention recorded | #65 |
| 21.T | Tests for this milestone | Ledger gate; one test per closed gap; waiver assertions | tests | all new paths covered; coverage ≥ 95% | #66 |
| 21.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #67 |
| 21.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #68 |
| 21.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #69 |
| 21.D | Design + reference docs | Parity + gap-closure status; ledger updated | docs | docs updated + linked here | #70 |

**Tests required:** parity gate green; a test per closed gap (G1 trust enforcement, G2 signed packs, G3
path-safety, G4 audit rotation/hash-chain, G5 OS-level sandbox, G6 SBOM, G8 trust matrix, G9 attestation,
G10 exit-code/scoring meta-cases, G11 criteria-interpolation meta-case, G12 model-surface sanity, G13 env
resolution in manifest, G14 cost governor); G7 waiver asserted.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Absorption ledger complete: delivered + tested / delegated / waived — no silent drops
- [ ] Every predecessor gap G1–G14 closed with a test or waived with a reason (G7 waived)
- [ ] Parity gate green and CI-enforced

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 10](../../prd/10-feature-parity.md) · [PRD 24](../../prd/24-predecessor-gap-closure.md).

---

Part 11 green ⇒ the developer surface is complete and the predecessor is fully and visibly absorbed;
proceed to [Part 12 (M22)](wbs-v0.1.0-part12-hardening-fieldtest.md).
