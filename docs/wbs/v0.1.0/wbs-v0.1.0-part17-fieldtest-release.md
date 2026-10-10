# WBS v0.1.0 — Part 13: Release Readiness (M24)

**BLUF:** Execute the release-readiness checklist, ship **v0.1.0**, and make the predecessor repository
private (retained, never deleted). This is where the **release tag is cut** — do not tag before M24.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M24 — Release readiness — ⬜ NOT STARTED

**Goal:** validate the release artifacts, publish the evidence, **tag `v0.1.0`**, and make the predecessor
private (retained, never deleted).

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 07](../../prd/07-success-metrics.md), [PRD 09](../../prd/09-roadmap.md),
[PRD 10](../../prd/10-feature-parity.md), [PRD 06](../../prd/06-security-baseline.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 24.1 | Release tooling | Build + SBOM (CycloneDX) + checksums + signed provenance via `release.yml` | tooling | `make release-dry-run` green | #92 |
| 24.2 | First-run verification | Timed clean-machine run (`quickstart`) ≤15 min, zero code changes | evidence | ≤15 min recorded | #93 |
| 24.3 | Security audit published | Self-audit of agentdrill + the evasion-pack result; 0 unresolved findings | audit | published | #94 |
| 24.4 | SBOM + signed artifacts + provenance | Verifiable signed artifacts on the tag | artifacts | independent verification passes | #95 |
| 24.5 | Compliance matrix + OpenSSF checklist | OWASP/ATLAS/NIST/EU mapping + OpenSSF baseline | matrix | published | #96 |
| 24.6 | Versioning + backwards-compat policy | One version across SDK/CLI/CHANGELOG; pack-format policy | policy | documented + honored | #97 |
| 24.7 | Release notes + compatibility table | Honest release notes + harness × version compatibility table | notes | published | #98 |
| 24.8 | **Tag `v0.1.0`** | Signed tag + GitHub release + published benchmark (misses included) | release | published | #99 |
| 24.9 | **Make predecessor private** | Retain the predecessor repo (never delete); set `private` | visibility | retained + `private` | #100 |
| 24.T | Tests for this milestone | Release tooling; version consistency; first-run; artifact verification | tests | all new paths covered; coverage ≥ 95% | #101 |
| 24.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #102 |
| 24.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #103 |
| 24.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #104 |
| 24.D | Design + reference docs | Release notes, compatibility table, README, traceability | docs | docs updated + linked here | #105 |

**Tests required:** full suite + coverage gate; parity + gap-closure gate (M21); first-run timed test;
release-tooling verification (SBOM/checksums/signatures); version consistency.

**Validation evidence**

| Item | Evidence |
|---|---|
| 24.2 First run | first-run evidence; quickstart scenario in [FIELD_TEST_REPORT](../../field-test/v0.1.0/FIELD_TEST_REPORT.md) |
| 24.4 SBOM + artifacts | release-evidence; `make release-dry-run` |
| 24.5 Compliance/OpenSSF | compliance matrix + OpenSSF checklist |
| 24.6 Versioning | version-consistency test |
| 24.7 Notes/compat | release notes; compatibility table |

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · port/absorption tasks complete
- [ ] Full PRD coverage + absorption ledger delivered and tested (M21 gate green)
- [ ] First-run ≤15 min; security audit + compliance matrix + release notes published; SBOM + signed artifacts
- [ ] **`v0.1.0` tagged and released**; the published benchmark includes its misses
- [ ] **Predecessor repository retained and made private (not deleted)**

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** README · release notes · compatibility table · [PRD 10](../../prd/10-feature-parity.md) ·
[PRD 24](../../prd/24-predecessor-gap-closure.md) · [PRD 12](../../prd/12-traceability.md).

---

Part 13 green ⇒ **v0.1.0 shipped.** All M0–M24 exit criteria satisfied; field tests pass; predecessor
retained privately.
