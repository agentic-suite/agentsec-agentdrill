# WBS v0.1.0 — Part 14: BYOD & Security Ecosystem Integrations (M25–M26)

**BLUF:** M25 makes agentdrill **neutral** — a Defense Contract + SDK + conformance kit, an OSS-first
Defense Zoo, and a neutral head-to-head under published rules. M26 makes findings **land where buyers work**
— SARIF/JUnit/OTel/OCSF/OSCAL/STIX out, imports in, and BAS-style SIEM detection validation. Closes G5 and
G14.

> **Standard exit criteria + closure apply to every milestone.**

---

## Milestone M25 — Bring-your-own-defense & neutral head-to-head — ⬜ NOT STARTED

**Goal:** drill *any* defense and compare fairly: an open contract any defense implements, a conformance
kit, a starting Zoo of OSS reference adapters, and a neutral head-to-head with published rules.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 29](../../prd/29-bring-your-own-defense.md) (R64, R65), features F90, F91.

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 25.1 | Defense Contract + SDK (F90) | Contract (decision points, I/O shape, evidence, **config digest**, fail-mode, version, ToS notes) + SDK | contract/sdk | a request/response defense adapts in ≤ 2 days | #314 |
| 25.2 | Conformance kit (F90) | Round-trip, determinism, evidence integrity, fail-mode; awards a conformance level | kit | 100% pass before listing | #315 |
| 25.3 | Defense Zoo (F90) | OSS-first reference adapters: OPA/Cedar, Llama Guard/Prompt Guard, NeMo Guardrails, Docker/gVisor profiles, harness-native sandboxes | adapters | ≥ 2 at v0.1.0 (≥ 6 across ≥ 6 classes by v0.2) | #316 |
| 25.4 | Neutral head-to-head (F91) | Same pack/seeds/env/twins across N defenses: `Hold@k`/`ASR@k`+CI, false-block on twins, $/1k + latency, fail-open/closed; **no composite/ranking** | report | identical-input 100%; zero rankings | #317 |
| 25.5 | Neutrality process (F91) | Pre-registration; vendor right-of-reply (14 d, raw bundle, verbatim reply); `tos_reviewed`; conflict disclosure; default-vs-tuned split; counsel sign-off | process | right-of-reply offered 100% | #318 |
| 25.T | Tests for this milestone | Contract round-trip; kit conformance; Zoo adapters conform; head-to-head identical-input; no-composite render; config-digest binding | tests | all new paths covered; coverage ≥ 95% | #319 |
| 25.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #320 |
| 25.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #321 |
| 25.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #322 |
| 25.D | Design + reference docs | Adapter API, conformance spec, neutrality rules, head-to-head methodology | docs | docs updated + linked here | #323 |

**Tests required:** contract round-trip; kit pass/fail correctly; Zoo adapters certified; head-to-head
identical seeds/env/twins; no composite score rendered; cells bound to config digest; third-party adapter
passes the kit.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] ≥ 2 OSS reference adapters conforming (≥ 6 classes by v0.2); a third-party adapter passes the kit
- [ ] Head-to-head identical-input with right-of-reply; **zero** composite scores/rankings
- [ ] Neutrality rules published; counsel sign-off recorded

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 29](../../prd/29-bring-your-own-defense.md) · [PRD 05](../../prd/05-features.md) ·
[PRD 08](../../prd/08-risks.md) (R12 shape).

---

## Milestone M26 — Security ecosystem integrations — ⬜ NOT STARTED

**Goal:** emit findings/results in official interchange formats and wire them into CI, code scanning, SIEM,
ticketing and GRC; import external suites; validate SIEM/EDR detection (BAS-style). Closes G14.

**Status:** ⬜ Not started · **Execution plan:** _(to be added)_ · **Issues:** _(to be assigned)_

**Requirements / PRDs:** [PRD 38](../../prd/38-security-ecosystem-integrations.md) (R74), feature F100;
[PRD 42](../../prd/42-standards-and-claims.md).

**Work items**

| # | Task | Description | Deliverable | Acceptance | Issue |
|---|---|---|---|---|---|
| 26.1 | SARIF + JUnit emitters | SARIF 2.1.0 (rule=case, severity vector, tier, witness ref, ASI/ATLAS tags, stable fingerprints, suppressions=waivers); JUnit (`missed`→failure, `untested`→skipped) | emitters | 100% schema-valid | #324 |
| 26.2 | OTel emit/read | Emit drill spans (`gen_ai.*`, semconv version pinned); read stage timing from instrumented targets | OTel | pin recorded; ≥95% span coverage | #325 |
| 26.3 | OCSF/ECS + OSCAL + STIX | SIEM/lake events; OSCAL assessment-results/POA&M (from ledger); STIX 2.1 bundles (adversary cards, intake) | emitters | validators green | #326 |
| 26.4 | CI/code-scanning + ticketing | GitHub code scanning upload; GitLab SAST artifact; Slack/Teams/Jira/ServiceNow/PagerDuty/Issues/Linear adapters; status sync ↔ ledger | adapters | ≤10 min wiring; ≤5 min ticket p95 | #327 |
| 26.5 | Inbound import | Inspect / promptfoo / garak / AgentDojo / PyRIT → normalized results (marked `imported`); inventory import | importers | 5/5 sources ≥95% mapping | #328 |
| 26.6 | SIEM/EDR detection validation | Query the customer SIEM for expected detection in a time budget; report `detected/alerted/logged/missed` + latency | BAS query | per-case states + latency | #329 |
| 26.7 | Reliability | Idempotent upserts; stable IDs; retries+backoff; DLQ; signed webhooks; rate-limit aware; offline spool | reliability | no loss across 24 h outage | #330 |
| 26.T | Tests for this milestone | All emitters schema-valid; round-trip lossless; imports; SIEM query; spool; dedup fingerprints | tests | all new paths covered; coverage ≥ 95% | #331 |
| 26.C | Coverage gate | Enforce coverage ≥ 95% on this milestone's modules | coverage report | ≥ 95%; no untested new path | #332 |
| 26.L | Lint & type gate | `ruff` zero violations; `mypy --strict` clean across the milestone | CI | zero violations | #333 |
| 26.CR | Code review | Record findings in [codereview-log.md](codereview-log.md); resolve all before closure | review log | no open findings | #334 |
| 26.D | Design + reference docs | Output-format matrix, integration guide, deep-link contract | docs | docs updated + linked here | #335 |

**Tests required:** SARIF/OSCAL/OCSF/STIX/CycloneDX validate in CI; round-trip lossless; SARIF suppressions
map waivers; JUnit `untested`→skipped; imports 5/5; SIEM query latency; offline spool; stable fingerprints
≥99% dedup.

**Exit criteria**

- [ ] All tests pass · coverage ≥ 95% · lint strict clean · design docs updated · traceability updated
- [ ] ≥ 10 first-party integrations; SARIF code-scanning upload ≥ 99%
- [ ] Imports 5/5 sources; SIEM/EDR detection validation working
- [ ] Offline spool: no data loss over 24 h

**Milestone closure**

- [ ] Implemented · Tests green (gates once) · Committed · Pushed · Tracking issue closed · Docs updated · Checkpoint recorded in the index

**Design docs to update:** [PRD 38](../../prd/38-security-ecosystem-integrations.md) · [PRD 42](../../prd/42-standards-and-claims.md).

---

Part 14 green ⇒ agentdrill is neutral across defenses and integrated into buyer tooling; proceed to
[Part 15](wbs-v0.1.0-part15-context-governance.md) (M27–M28).
