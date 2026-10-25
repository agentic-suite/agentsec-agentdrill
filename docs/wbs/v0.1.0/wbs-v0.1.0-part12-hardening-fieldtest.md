# WBS v0.1.0 — Part 12: Hardening (M22)

**BLUF:** M22 hardens the non-functionals (performance, fail-closed fault handling, untrusted-pack
sandboxing, audit integrity, portability, cost). The v0.1.0 additions (M23–M30, [Parts 13–16](../v0.1.0/))
follow, and then — **last** — field tests and release readiness ([Part 17](wbs-v0.1.0-part17-fieldtest-release.md), M31–M32).

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M22 — NFRs, security hardening & resilience — ✅ COMPLETE (2026-10-23)

**Goal:** meet the non-functional requirements ([PRD 13](../../prd/13-non-functional-requirements.md)) and
harden the security baseline — performance budgets, fail-closed fault handling, OS-level sandboxing for
untrusted packs, tamper-evident audit, and portability.

**Status:** ✅ Complete · **Execution plan:** [m22-hardening-execution-plan](../../plans/m22-hardening-execution-plan.md) · **Issues:** #71–#81

**Requirements / PRDs:** [PRD 13](../../prd/13-non-functional-requirements.md), [PRD 06](../../prd/06-security-baseline.md),
[PRD 08](../../prd/08-risks.md) (RK-3, RK-8), [PRD 24](../../prd/24-predecessor-gap-closure.md) (G4, G5).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 22.1 | Performance & scale | Per-pack run budget; parallel + backpressure; oracle/judge cache with `cache stats` | perf | budget met; parallel == serial | #71 |
| 22.2 | Fault injection & fail-closed | Faults across runner/targets/oracles/drivers; **fail-closed on tamper**; a case failure never aborts the pack | fault suite | faults handled, never silently green | #72 |
| 22.3 | Untrusted-pack hardening | OS-level sandbox (Docker, `--network none`, read-only root, resource caps) **required** for `external` trust; audit **rotation + hash-chain integrity** (predecessor G4); secret sanitization | sandbox/audit | external pack isolated; audit tamper detected | #73 |
| 22.4 | Portability | Python 3.10+, macOS/Linux, **local-first** (no service required for core function) | portability | runs on both OSes | #74 |
| 22.5 | Cost controls | Run-level `--max-cost`; caching; reported savings | cost | over-budget aborts + reports | #75 |
| 22.6 | Self-observability | `doctor`, `validate`, audit log, shareable run summary (dimensions + outcome split + exit code) | tooling | one run summary answers "what happened" | #76 |
| 22.T | Tests for this milestone | Perf budget; fault injection; sandbox isolation; audit rotation/hash-chain; portability; cost; self-observability | tests | all new paths covered; coverage ≥ 95% | #77 |
| 22.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #78 |
| 22.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #79 |
| 22.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #80 |
| 22.D | Design + reference docs | NFR report, security-hardening notes, operations guide | docs | docs updated + linked here | #81 |

**Tests required:** perf budget; each injected fault (fail-closed); external-pack isolation (`--network
none`, read-only root, caps); audit tamper detected; portability smoke; cost abort; run summary complete.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] NFRs met ([PRD 13](../../prd/13-non-functional-requirements.md)); fault suite fail-closed
- [x] External packs OS-isolated; audit tamper-evident (predecessor G4/G5 closed)
- [x] Local-first on macOS + Linux

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 13](../../prd/13-non-functional-requirements.md) · [PRD 06](../../prd/06-security-baseline.md) ·
[PRD 24](../../prd/24-predecessor-gap-closure.md).

---

Part 12 green ⇒ the base engine is hardened; proceed to [Part 13](wbs-v0.1.0-part13-effect-witness-bypass.md)
(M23–M24) for the v0.1.0 world-class additions. Field tests (M31) and release readiness (M32) are **last** —
[Part 17](wbs-v0.1.0-part17-fieldtest-release.md).
