# WBS v0.1.0 — Part 9: Registry & Interop (M16–M17)

**BLUF:** M16 turns packs into signed, semver'd, reviewed registry entries with enforced trust levels. M17
imports the community's attack suites (promptfoo/garak/AgentDojo/PyRIT), tags every pack with
MITRE ATLAS + OWASP, and emits compliance-mapped reports.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M16 — Pack registry, signing & governance — ✅ COMPLETE (2026-10-23)

**Goal:** the registry that treats packs like signed packages — verified publishers, signatures, semver,
trust levels enforced at load/run, deprecation/takedown, and a **reviewed-like-code** contribution flow
(R11). External (untrusted) packs are sandbox-restricted and never benchmark-published.

**Status:** ✅ Complete · **Execution plan:** [m16-registry-governance-execution-plan](../../plans/m16-registry-governance-execution-plan.md) · **Issues:** #260–#270

**Requirements / PRDs:** [PRD 17](../../prd/17-pack-registry-and-governance.md), [PRD 06](../../prd/06-security-baseline.md),
features F14, F15, F39, F75, requirement R11.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 16.1 | Registry model + index | Content-addressed, signed `registry.json`; mirrored + offline-verifiable (no mandatory central service) | registry | index verifies offline | #260 |
| 16.2 | Signing + verified publishers | Sigstore signing bound to a GitHub/Org identity; `pack verify` before install | signing | unsigned/tampered pack rejected | #261 |
| 16.3 | Trust levels | `built-in` / `local` / `external` enforced at load/run; `external` → sandboxed subprocess only; matrix documented | policy | external pack sandbox-restricted | #262 |
| 16.4 | Contribution flow | `init` scaffold → `pack lint` (schema, tags, `incident_ref`, oracle, fixtures, methodology) → independent review → `pack publish` → `pack verify` | flow | unreviewed pack cannot be benchmark-published | #263 |
| 16.5 | Deprecation + takedown | Explicit deprecation with migration notes; takedown removes the index entry, recorded on the signature chain (no silent disappearance) | policy | deprecated/takedown recorded | #264 |
| 16.6 | Registry sync (F75) | `agentdrill registry sync` (read-only, signature-verified); `pack outdated` | CLI | sync rejects a bad signature | #265 |
| 16.T | Tests for this milestone | Signature failure; trust enforcement; lint criteria; deprecation/takedown; sync | tests | all new paths covered; coverage ≥ 95% | #266 |
| 16.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #267 |
| 16.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #268 |
| 16.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #269 |
| 16.D | Design + reference docs | Registry spec, contribution guide, trust policy | docs | docs updated + linked here | #270 |

**Tests required:** signature failure rejects a pack; `external` pack runs sandbox-only; lint catches a
missing `incident_ref`/tag; deprecation + takedown recorded; sync rejects bad signature; registry poisoning
(RK-16) rejected.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] Packs are signed; trust levels enforced; `external` packs sandbox-restricted and never benchmark-published
- [x] Contribution flow is reviewed-like-code (R11); registry poisoning rejected

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 17](../../prd/17-pack-registry-and-governance.md) · trust policy ·
[PRD 06](../../prd/06-security-baseline.md).

---

## Milestone M17 — Interop, standards tagging & compliance — ✅ COMPLETE (2026-10-23)

**Goal:** import the community's attack suites instead of reinventing them; tag every pack/attack with
MITRE ATLAS + OWASP; emit compliance-mapped reports and the standards-submission surface; run the
competitor honest-coverage benchmark (R9, R10, R12).

**Status:** ✅ Complete · **Execution plan:** [m17-interop-compliance-execution-plan](../../plans/m17-interop-compliance-execution-plan.md) · **Issues:** #271–#281

**Requirements / PRDs:** [PRD 03](../../prd/03-landscape.md), [PRD 05](../../prd/05-features.md)
(R9, R10, R12), features F12, F13, F24, F28, F54.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 17.1 | Interop importer (F12) | Connector layer importing promptfoo / garak / AgentDojo / PyRIT suites → attack packs; **format translation only**, never touches the core runner | connectors | an imported suite runs unchanged | #271 |
| 17.2 | Standards tagging (F13) | MITRE ATLAS + OWASP (LLM Top-10 + Agentic) on every pack/attack; lint requires tags | tagger | untagged pack rejected | #272 |
| 17.3 | Adversary profiles (F54) | Pack-level threat-intel card (who, what, source, objective) rendered on results | profiles | card renders on the result | #273 |
| 17.4 | Compliance-mapped reporting (F24) | Findings mapped to EU AI Act Art. 12, NIST AI RMF, ISO 42001; evidence export to agentcomply | report | a compliance report generates offline | #274 |
| 17.5 | Standards-submission surface (F28) + fuzzing (R13) | Submit packs/results to NIST CAISI / AgentDojo-Inspect and OWASP Agentic; OSS-Fuzz as a pack class | surface | a submission artifact generates | #275 |
| 17.6 | Competitor benchmark (R12) | Run packs against third-party stacks; honest-coverage table via PR submission (F57) | benchmark | a third-party row is reproducible | #276 |
| 17.T | Tests for this milestone | Import fidelity per connector; tag-required lint; profile render; compliance mapping; submission export; competitor row | tests | all new paths covered; coverage ≥ 95% | #277 |
| 17.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #278 |
| 17.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #279 |
| 17.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #280 |
| 17.D | Design + reference docs | Interop guide, tagging reference, compliance mapping | docs | docs updated + linked here | #281 |

**Tests required:** each importer produces a runnable pack; tagging enforced by lint; adversary profile
renders; compliance report is offline + reproducible; submission export valid; competitor row reproduces.

**Exit criteria**

- [x] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [x] promptfoo/garak/AgentDojo/PyRIT suites import and run (R9)
- [x] Every pack/attack tagged ATLAS + OWASP (R10); lint enforces it
- [x] Compliance report + standards submission generate offline

**Milestone closure**

- [x] Implemented · Tests green (gates once) · Committed & pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** interop guide · tagging reference · [PRD 03](../../prd/03-landscape.md).

---

Part 9 green ⇒ packs are governed and interop-ready; proceed to [Part 10 (M18–M19)](wbs-v0.1.0-part10-lifecycle-oracle.md).
