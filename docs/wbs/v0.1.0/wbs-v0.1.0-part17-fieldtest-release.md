# WBS v0.1.0 — Part 17: Field Tests & Release Readiness (M31–M32)

**BLUF:** These are the **last two** milestones. M31 runs the **field tests** against a real deployed stack
(and the bundled demo) over **all CUJs (CUJ-1..CUJ-63)** and publishes the report. M32 executes the
release-readiness checklist, ships **v0.1.0**, and makes the predecessor repository private (retained, never
deleted). Nothing is tagged before M32.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M31 — Field tests — ✅ 2026-10-25

**Goal:** run the field tests against a real deployed stack (and the bundled demo), exercise **every CUJ
(CUJ-1..CUJ-63)**, and publish the report — the last validation before release readiness.

**Status:** ✅ Complete 2026-10-25 · **Execution plan:** [field-test plan](../../field-test/v0.1.0/field-test-plan.md) · **Issues:** #82–#91, #383

**Requirements / PRDs:** [PRD 07](../../prd/07-success-metrics.md), [PRD 04](../../prd/04-users-and-cujs.md)
(CUJ-1..CUJ-63), [PRD 21](../../prd/21-pack-catalog.md), [PRDs 25–42](../../prd/README.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 31.1 | Field-test harness | Harness driving the bundled demo stack + a real deployed stack (the Wave-0 enforcers) in an ephemeral/purple environment under a signed RoE (M28) | harness | runnable end to end | #82 |
| 31.2 | Execute core scenarios | Every CUJ-1..CUJ-27 end to end: run pack, gate PR, reproduce benchmark, drill incident, kill-time, evasion, intake→pack, fix-decay, seam, verifier, quickstart | results | all scenarios pass | #83 |
| 31.3 | Execute addition scenarios | Every addition CUJ-28..CUJ-63: pressure/`Hold@k`, effect witness, lab, bypass search, BYOD/head-to-head, backtest/shadow, attack-path, incident compiler, ledger/waivers, attestations, RoE/abort, detonation, break-it, frontier classes, explorer, platform matrix, standards/claims | results | all scenarios pass | #383 |
| 31.4 | Evidence + report | Collect evidence; publish `FIELD_TEST_REPORT.md` (what was tested, what was **not**, per-CUJ) | report | published; misses stated | #84 |
| 31.5 | Fix defects + regressions | Fix every defect found; add a regression test each | fixes | defects closed with evidence | #85 |
| 31.6 | Field-test CI job | Nightly field-test job | CI | scheduled + green (or explicitly not-planned) | #86 |
| 31.T | Tests for this milestone | Regression tests for every defect; all CUJ journeys exercised end to end | tests | all new paths covered | #87 |
| 31.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #88 |
| 31.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #89 |
| 31.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #90 |
| 31.D | Design + reference docs | Field-test plan + report; known-limitations updated | docs | docs updated + linked here | #91 |

**Tests required:** all field scenarios; regression tests for each defect; **every CUJ-1..CUJ-63 exercised**
end to end; the verifier run offline on a clean machine; a witness-confirmed `missed` and a
`witness_discrepancy` demonstrated; the RoE abort demonstrated.

**Exit criteria**

- [x] All field-test scenarios pass; report published with **what was not tested** stated
- [x] Defects fixed with regression evidence
- [x] CUJ-1..CUJ-63 exercised end to end
- [x] Design docs updated · port/absorption tasks complete

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** field-test plan · [FIELD_TEST_REPORT](../../field-test/v0.1.0/FIELD_TEST_REPORT.md) ·
[PRD 07](../../prd/07-success-metrics.md).

---

## Milestone M32 — Release readiness — 🚧 IN PROGRESS

**Goal:** validate the release artifacts, publish the evidence, **tag `v0.1.0`**, and make the predecessor
private (retained, never deleted). **This is the final milestone.**

**Status:** 🚧 In progress · **Execution plan:** [M32 execution plan](../../plans/m32-release-readiness-execution-plan.md) · **Issues:** #92–#105, #394

**Requirements / PRDs:** [PRD 07](../../prd/07-success-metrics.md), [PRD 09](../../prd/09-roadmap.md),
[PRD 10](../../prd/10-feature-parity.md), [PRD 06](../../prd/06-security-baseline.md),
[PRDs 25–43](../../prd/README.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 32.1 | Release tooling | Build + SBOM (CycloneDX) + checksums + signed provenance via `release.yml` | tooling | `make release-dry-run` green | #92 |
| 32.2 | First-run verification | Timed clean-machine run (`quickstart`) ≤15 min, zero code changes | evidence | ≤15 min recorded | #93 |
| 32.3 | Security audit published | Self-audit of agentdrill + the evasion-pack result + the RoE/bystander analysis; 0 unresolved findings | audit | published | #94 |
| 32.4 | SBOM + signed artifacts + provenance | Verifiable signed artifacts on the tag (SLSA target recorded) | artifacts | independent verification passes | #95 |
| 32.5 | Compliance matrix + evidence indexes + OpenSSF | OWASP ASI/ATLAS/NIST/EU mapping + per-framework **evidence index** (with `not covered`) + OpenSSF baseline | matrix | published | #96 |
| 32.6 | Versioning + backwards-compat policy | One version across SDK/CLI/CHANGELOG; pack-format policy; oracle/pack/lab version pins | policy | documented + honored | #97 |
| 32.7 | Release notes + compatibility table | Honest release notes + harness × version compatibility table (L0–L4, AWC) | notes | published | #98 |
| 32.8 | **Tag `v0.1.0`** | Signed tag + GitHub release + published benchmark (misses included, tiers/k/CIs, witness coverage) | release | published | #99 |
| 32.9 | **Make predecessor private** | Retain the predecessor repo (never delete); set `private` | visibility | retained + `private` | #100 |
| 32.10 | **PyPI publish + verification** | Publish wheel + sdist to PyPI via **trusted publishing** (OIDC, no stored token) from the tag-triggered `release.yml`; verify the published package: `pip install agentsec-agentdrill==<v>` in a clean venv (macOS + Linux), `agentdrill version` == the version, the wheel SHA-256 matches `SHA256SUMS`/provenance, `gh attestation verify` passes | distribution | published + `pip install` verified | #394 |
| 32.T | Tests for this milestone | Release tooling; version consistency; first-run; artifact verification; claims linter green | tests | all new paths covered; coverage ≥ 95% | #101 |
| 32.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #102 |
| 32.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #103 |
| 32.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #104 |
| 32.D | Design + reference docs | Release notes, compatibility table, README, traceability (R1–R79) | docs | docs updated + linked here | #105 |

**Tests required:** full suite + coverage gate; parity + gap-closure gate (M21); first-run timed test;
release-tooling verification (SBOM/checksums/signatures); version consistency; claims linter green;
attestation (M28) verifies offline; **PyPI install verification (32.10)**.

**Validation evidence**

| Item | Evidence |
|---|---|
| 32.2 First run | first-run evidence; quickstart scenario in [FIELD_TEST_REPORT](../../field-test/v0.1.0/FIELD_TEST_REPORT.md) |
| 32.4 SBOM + artifacts | release-evidence; `make release-dry-run` |
| 32.5 Compliance/OpenSSF | compliance matrix + evidence indexes + OpenSSF checklist |
| 32.6 Versioning | version-consistency test |
| 32.10 PyPI publish + verify | `docs/release/v0.1.0/pypi-evidence.md`; `pip install agentsec-agentdrill==<version>` in a clean venv |
| 32.7 Notes/compat | release notes; compatibility table |

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · port/absorption tasks complete
- [ ] Full PRD coverage + absorption ledger delivered and tested (M21 gate green)
- [ ] First-run ≤15 min; security audit + compliance matrix + evidence indexes + release notes published; SBOM + signed artifacts
- [ ] **`v0.1.0` tagged and released**; the published benchmark includes its misses, tiers/k, CIs and witness coverage; **the package installs from PyPI** (`pip install agentsec-agentdrill`, verified)
- [ ] **Predecessor repository retained and made private (not deleted)****

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** README · release notes · compatibility table · [PRD 10](../../prd/10-feature-parity.md) ·
[PRD 12](../../prd/12-traceability.md) · [PRD 43](../../prd/43-evidence-register-and-method.md).

---

Part 17 green ⇒ **v0.1.0 shipped.** All M0–M32 exit criteria satisfied; field tests pass; predecessor
retained privately.
