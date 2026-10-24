# agentdrill M26 — Security Ecosystem Integrations Execution Plan

**Spec:** [WBS M26](../wbs/v0.1.0/wbs-v0.1.0-part14-byod-integrations.md) · [design](../design/integrations.md) · [PRD 38](../prd/38-security-ecosystem-integrations.md), [PRD 42](../prd/42-standards-and-claims.md).

**Status:** 🚧 In progress (2026-10-24) · **Issues:** #324–#335 · Closes predecessor gap **G14**.

## Constraints

- **Standards first:** every emitted artifact validates against its official schema in CI (100%); vendor connectors only by demand.
- **Offline-safe:** no mandatory hosted service; the webhook relay is self-hosted.
- **Privacy:** payloads/PII excluded by default; content capture opt-in; redaction receipts (F65) apply to any emitted evidence.
- **Stable identity:** stable `partialFingerprints`/ids; dedup ≥ 99%; upserts idempotent.
- One ticket at a time: test **RED** → implement **GREEN** → next. Full suite at milestone end only.

## Prerequisites

- Consumes **M10** (`reporting/` findings + `TraceStore`), **M17** (`interop/` importers for promptfoo/garak/AgentDojo/PyRIT), `observability/` (OTLP-compatible tracer), **M19** (oracle versions → SARIF rule versions).
- **M28 seam:** SARIF `suppressions = waivers` requires the exposure-ledger waiver model, which M28 owns. Until M28 lands, 26.1 defines a **minimal read-only waiver interface** and records a re-point task at M28 — a compatibility seam, never a parallel waiver registry.

## Tasks

- **T1 — SARIF + JUnit emitters (26.1, #324).** SARIF 2.1.0 (rule = case id; severity vector; `properties` = tier + witness ref + ASI/ATLAS; stable `partialFingerprints`; `suppressions` = waivers); JUnit XML (`missed`→failure, `untested`→skipped + reason). *RED:* a fixture run emits both, each validating against the official schema. *GREEN.*
- **T2 — OTel emit/read (26.2, #325).** drill = trace, case = span; `gen_ai.*` per a **pinned** semconv version; read stage timings from instrumented targets (F37). Pin recorded; ≥ 95% span coverage.
- **T3 — OCSF/ECS + OSCAL + STIX (26.3, #326).** OCSF/ECS detection/finding + ATT&CK/ATLAS; OSCAL assessment-results/POA&M from the ledger; STIX 2.1 bundles (adversary cards, incident briefs). Validators green.
- **T4 — CI/code-scanning + ticketing (26.4, #327).** GitHub code-scanning upload; GitLab SAST artifact; Slack/Teams/Jira/ServiceNow/PagerDuty/GitHub Issues/Linear adapters; status sync ↔ ledger. ≤ 10 min to wire; ticket p95 ≤ 5 min.
- **T5 — Inbound import (26.5, #328).** Inspect/promptfoo/garak/AgentDojo/PyRIT → normalized results marked `imported` (lower trust); inventory import. 5/5 sources ≥ 95% field mapping.
- **T6 — SIEM/EDR detection validation (26.6, #329).** Query the customer SIEM for the expected detection within a time budget; per-case `detected/alerted/logged/missed` + latency (CUJ-55).
- **T7 — Reliability (26.7, #330).** Idempotent upserts; stable IDs; retries + backoff; dead-letter queue; signed webhooks; rate-limit aware; offline spool. *RED:* no loss across a 24 h outage. *GREEN.*
- **T8 — Gates + docs (26.T #331 · 26.C #332 · 26.L #333 · 26.CR #334 · 26.D #335).** Tests; coverage ≥ 95%; `ruff` zero + `mypy --strict` clean; review log resolved; output-format matrix + integration guide + deep-link contract.

## Module ownership (single-writer files)

- New package `agentdrill/integrations/` (proposed) owns the emitter/importer/SIEM/reliability adapters and **one** adapter registry — exactly one writer for the registry.
- **Reuse, do not fork:** `reporting/` (findings source), `interop/` (existing importers), `observability/` (tracer), ledger/waivers (M28).

## Exit criteria

- [ ] 100% schema-valid emissions in CI (SARIF/OSCAL/OCSF/STIX/CycloneDX validators green); round-trip lossless 100%.
- [ ] ≥ 10 first-party integrations; SARIF code-scanning upload ≥ 99%; duplicate-ticket rate ≤ 2%.
- [ ] Imports 5/5 sources ≥ 95%; SIEM/EDR per-case states + latency reported; deep links resolve ≥ 99% (CUJ-54).
- [ ] Offline spool: no data loss across a 24 h outage.
- [ ] All tests pass · coverage ≥ 95% · `ruff` zero · `mypy --strict` clean · review log resolved · docs linked from the WBS.

**Closure:** standard (implemented · gates run once · committed · pushed · issue closed · docs updated · checkpoint in the index).
