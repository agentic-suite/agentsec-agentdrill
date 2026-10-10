# WBS v0.1.0 — Part 8: Evasion & Chains (M14–M15)

**BLUF:** M14 turns the ecosystem's own threat model into a shipped **evasion pack** plus a
**drill-the-drill** meta-verification suite and a **dark holdout**. M15 models incidents as **chains** and
adds a **bounded adaptive orchestrator**.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M14 — Evasion pack & drill-the-drill — ⬜ NOT STARTED

**Goal:** continuously red-team the ecosystem's **own** products (tamper, hook-disable, policy-edit,
telemetry-inject, evidence-edit, update-hijack, evasion-attempt) and **our own oracles** (can a target fool
the scorer?), with an unpublished **dark holdout** to catch pack-gaming (R7). Runs every release cycle.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 06](../../prd/06-security-baseline.md), [PRD 05](../../prd/05-features.md)
(R7), [PRD 21](../../prd/21-pack-catalog.md), features F11, F33, F43.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 14.1 | Evasion / self-attack pack | Cases targeting our own tools: pack tamper, hook-disable, policy-edit, telemetry-injection, evidence-edit, update-hijack, agent-instructed evasion | pack | each attack has an expected fail-closed defense | #240 |
| 14.2 | Drill-the-drill (F43) | Adversarial cases against our **own oracle engine**: vacuous no-op must not score `blocked`; a must-block miss must exit non-zero; fixtures must intercept; attestation/evidence forgery; severity gaming | pack | oracle gaming is caught | #241 |
| 14.3 | Dark holdout (F33) | Private, unpublished holdout subset per pack; runs in CI; published-set green + holdout red = pack-gaming finding | holdout | holdout failure is release-blocking | #242 |
| 14.4 | CI cadence | Evasion + meta-verification + holdout run **every** release cycle; results published | CI | cadence enforced | #243 |
| 14.5 | Hidden adversarial case | Independent-reviewer-authored secret case (JPS pattern) kept inside the meta pack | case | escapes single-layer defense | #244 |
| 14.T | Tests for this milestone | Each evasion case fail-closed; each meta case catches its gap; holdout detects gaming | tests | all new paths covered; coverage ≥ 95% | #245 |
| 14.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #246 |
| 14.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #247 |
| 14.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #248 |
| 14.D | Design + reference docs | Recorder/defense attack matrix, meta-verification spec | docs | docs updated + linked here | #249 |

**Tests required:** every evasion case fails closed (blocked + loud); meta cases catch their target gap;
dark-holdout red flags pack-gaming; evasion pack runs in the release CI.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Evasion pack runs every release cycle and fails closed on tamper (R7)
- [ ] Drill-the-drill catches oracle gaming; dark holdout catches pack-gaming (F33)
- [ ] A tamper regression is release-blocking

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 06](../../prd/06-security-baseline.md) · defense attack matrix ·
[PRD 21](../../prd/21-pack-catalog.md).

---

## Milestone M15 — Attack chains & bounded adaptive orchestration — ⬜ NOT STARTED

**Goal:** model incidents as **multi-step chains** with state carried between steps and a **chain oracle**
stating where the chain must break; add a **bounded adaptive orchestrator** that mutates *documented*
patterns from live responses — hard-capped inside the dual-use boundary, always labeled (R14, R18).

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 16](../../prd/16-attack-chain-orchestration.md), [PRD 08](../../prd/08-risks.md)
(RK-2, RK-13), features F18, F40, requirements R14, R18.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 15.1 | Chain structure | Pack-level chains: per-step oracles + a `chain_oracle` (`expect: chain_broken_before: <step>`); state conditioning (`requires:`) | schema | a chain runs step by step | #250 |
| 15.2 | Break point reporting | Per-step outcome + `broke_at` (furthest stage reached); a defense that breaks too late is a distinct finding | engine | the chain names where it broke | #251 |
| 15.3 | Bounded adaptive orchestrator (F40) | Mutate a *documented* pattern from live responses; hard caps: `parent_pattern` + `mutation_summary` + `reviewer`, `max_mutations`, cost ceiling, step depth; labeled `adaptive`; excluded from golden-locked comparisons | orchestrator | adaptive cases carry provenance; no novel capability | #252 |
| 15.4 | Adaptive determinism | Pinned attacker model + seed; the mutation **path** recorded in the manifest (two identical runs ⇒ identical path) | manifest | adaptive run reproducible | #253 |
| 15.5 | Registry review gate | An adaptive case entering a *shipped* pack requires human review (HITL) | gate | unreviewed adaptive case cannot ship | #254 |
| 15.T | Tests for this milestone | Chain state + chain oracle; broke_at; adaptive caps + provenance; determinism; review gate | tests | all new paths covered; coverage ≥ 95% | #255 |
| 15.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #256 |
| 15.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #257 |
| 15.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #258 |
| 15.D | Design + reference docs | Orchestration design, dual-use boundary spec | docs | docs updated + linked here | #259 |

**Tests required:** chain carries state between steps; chain oracle marks the correct break; late break is
distinct from no break; adaptive case requires provenance + reviewer; caps enforced; adaptive run
deterministic; unreviewed adaptive case blocked from shipping.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] Chains run with per-step oracles + a chain oracle; `broke_at` reported
- [ ] Adaptive orchestration stays inside the dual-use boundary — provenance + reviewer + caps enforced (RK-2/RK-13)
- [ ] Adaptive runs are deterministic (mutation path in the manifest)

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 16](../../prd/16-attack-chain-orchestration.md) · dual-use boundary spec.

---

Part 8 green ⇒ chains + self-attack are live; proceed to [Part 9 (M16–M17)](wbs-v0.1.0-part9-registry-interop.md).
