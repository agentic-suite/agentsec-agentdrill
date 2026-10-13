# WBS v0.1.0 — Part 3: Drivers & Targets (M4–M5)

**BLUF:** M4 adds the **driver adapters** that deliver an attack through a harness/agent (with the
no-ground-truth-leakage contract). M5 adds the **target adapters** that drive the *deployed stack*
(agentgate, agentkeys, agentseatbelt/agentkernel, policyweave output, agenthalt) and the **recon/scoping**
phase that binds cases to real surfaces.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M4 — Driver adapters — ✅ COMPLETE

**Goal:** the adapters that **deliver** an attack — `subprocess`, `python`, `http` (absorbed contract),
plus per-harness drivers (Claude Code, Cursor) — with the **invocation-payload / run-envelope** contract
and **no ground-truth leakage**.

**Status:** ✅ Complete (2026-10-12) · **Execution plan:** [m4-m5](../plans/m4-driver-adapters-execution-plan.md) · **Issues:** #128–#138

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md) (adapter contract),
[PRD 05](../../prd/05-features.md) §Compatibility, [PRD 11](../../prd/11-decisions.md) (DD-03).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 4.1 | Adapter base + contract | `Driver` ABC: `run(case, config) → RunArtifact`; payload building, timing, error normalization; **payload excludes `oracle`/`expect`/thresholds** | base | a driver never receives the expected outcome | #128 |
| 4.2 | `subprocess` driver | stdin JSON payload → stdout run-envelope; raw-text fallback unless `strict_output`; logs to stderr; timeout/crash handling | adapter | envelope + fallback + timeout handled | #129 |
| 4.3 | `python` driver | Import module, call `run(payload)`; hard timeout in a separate process | adapter | callable invoked; timeout isolated | #130 |
| 4.4 | `http` driver | POST payload; handle connection/timeout/non-200 | adapter | errors normalized to `status` | #131 |
| 4.5 | Per-harness drivers | `claude-code` and `cursor` drivers delivering the attack through the harness surface (≥2 Tier-1 at v0.1.0) | adapters | each harness pack runs end to end | #132 |
| 4.6 | Adapter registry + plugin discovery | `ADAPTERS` registry + entry-point discovery for community drivers; unknown → `ConfigError`; driver manifest + SHA-256 digest | registry | digest bound into results | #133 |
| 4.T | Tests for this milestone | Each driver: pass, envelope, raw fallback, timeout, crash, non-zero; leakage assertion | tests | all new paths covered; coverage ≥ 95% | #134 |
| 4.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #135 |
| 4.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #136 |
| 4.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #137 |
| 4.D | Design + reference docs | Adapter API, custom-adapter guide, envelope schema | docs | docs updated + linked here | #138 |

**Tests required:** per-driver happy + error paths; **ground-truth-leakage guard** (assert `oracle`/`expect`
never in the payload); digest stability; registry unknown-name failure.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] subprocess/python/http + ≥2 Tier-1 harness drivers run a pack end to end
- [x] Ground-truth-leakage guard passes for every driver

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** adapter API · custom-adapter guide · [PRD 02](../../prd/02-architecture.md).

---

## Milestone M5 — Target adapters & recon/scoping — ⬜ NOT STARTED

**Goal:** the target adapters that (a) drive a deployed-stack component into an attack posture and (b) read
back its decision + evidence — plus the **recon/scoping** phase that probes exposed surfaces and binds
cases to what actually exists (R2). A case referencing a nonexistent surface fails loudly, never silently.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 02](../../prd/02-architecture.md), [PRD 04](../../prd/04-users-and-cujs.md)
(CUJ-1), [PRD 05](../../prd/05-features.md) (R2), feature F42.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 5.1 | Target adapter base | `Target` ABC: `drive(case)` + `read_decision()` + `read_evidence()`; per-target config | base | contract documented | #139 |
| 5.2 | Deployed-stack targets | `agentgate` (MCP proxy), `agentkeys` (broker), `agentseatbelt`/`agentkernel` (confinement), `policyweave-output` (compiled policy), `agenthalt` (halt/revoke) | adapters | each drives its real enforcement path | #140 |
| 5.3 | Recon/scoping phase (F42) | Probe exposed surface (tools, MCP servers, capabilities via agentwatch inventory); produce a `ReconSnapshot`; bind cases; missing surface fails loudly | recon | a case on a nonexistent surface fails, never silently passes | #141 |
| 5.4 | Target config + attestation hooks | Per-component config; attestation fields (`live`/`fixture`/`mock`) recorded (enforced at M13/M18) | config | weakest-link label computable | #142 |
| 5.5 | Model/target sanity | Declare `model`/`base_url`; recon fails loudly on an unreachable model surface before cases run (predecessor G12) | recon | opaque model 404 becomes a clear failure | #143 |
| 5.6 | `.agentdrill/` run layout | Target metadata stored with each run (`run.json` + recon snapshot ref) | storage | run reconstructs its target | #144 |
| 5.T | Tests for this milestone | Each target: drive + decision + evidence; recon binding + missing-surface failure; attestation record | tests | all new paths covered; coverage ≥ 95% | #145 |
| 5.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #146 |
| 5.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #147 |
| 5.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #148 |
| 5.D | Design + reference docs | Target-adapter API, recon design, attestation notes | docs | docs updated + linked here | #149 |

**Tests required:** per-target drive/decision/evidence; recon binds cases + fails on absent surface;
model-surface sanity failure; attestation field recorded.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Packs exercise the real enforcement path end-to-end (R2)
- [ ] Recon binds cases to existing surfaces; nonexistent surface fails loudly
- [ ] Unreachable model surfaces fail before any case runs (predecessor G12)

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** target-adapter API · recon design · [PRD 02](../../prd/02-architecture.md) ·
[PRD 24](../../prd/24-predecessor-gap-closure.md) (G12).

---

Part 3 green ⇒ agentdrill drills the deployed stack; proceed to [Part 4 (M6–M7)](wbs-v0.1.0-part4-oracles-evidence.md).
