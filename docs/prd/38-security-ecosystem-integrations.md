# PRD 38 — Security Ecosystem Integrations

**BLUF:** Findings must land where the buyer already works: code scanning, SIEM/SOAR, ticketing, GRC, trace backends. BAS vendors advertise dozens of integrations (Picus 75+; SafeBreach "dozens"). The PRD lists output formats but names **no interchange standards** (grep for SARIF/OCSF/OpenTelemetry/OSCAL/SLSA/in-toto → 0). Add **outbound** emitters (SARIF 2.1.0, JUnit, OTel GenAI spans, OCSF/ECS, OSCAL, STIX 2.1; chat/ticket/on-call adapters), **inbound** import (Inspect/promptfoo/garak/AgentDojo/PyRIT; inventory) and a **BAS-style SIEM/EDR detection-validation query**.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F100 · **Reqs:** R74

## Why

- Enterprise security does not adopt a tool that lives in its own tab.
- A grep of PRD/design/reference for SARIF/OCSF/OpenTelemetry/OSCAL/SLSA/in-toto found **zero** mentions.
- Detection engineering is a BAS core use-case ("did the SOC alert?") — F52's expected-telemetry check is agentwatch-only.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R74** | Emit findings/results in official interchange formats (SARIF, JUnit, OCSF/ECS, OSCAL, STIX, OTel) and integrate with CI/ticketing/SIEM; import external suites; support a SIEM/EDR detection-validation query. | 100% of emitted artifacts validate against official schemas in CI; ≥ 10 first-party integrations; imports 5/5 sources ≥ 95% field mapping; no data loss across a 24 h offline outage. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F100** | **Security ecosystem integrations**: **outbound** SARIF 2.1.0 (rule=case, severity vector, tier, witness ref, ASI/ATLAS tags, stable fingerprints, suppressions=waivers), JUnit, OTel traces/metrics (GenAI semconv pinned), OCSF/ECS, OSCAL (assessment-results/POA&M), STIX 2.1; chat/ticket/on-call (Slack, Teams, Jira, ServiceNow, PagerDuty, GitHub Issues, Linear); **inbound** import (Inspect, promptfoo, garak, AgentDojo, PyRIT; inventory); **SIEM/EDR detection-validation** query (`detected/alerted/logged/missed` + latency); reliability (idempotency, stable IDs, retries, DLQ, signed webhooks, rate-limit aware, offline spool) | R74 | Consumes [PRD 33](33-exposure-ledger-and-waivers.md)/[PRD 42](42-standards-and-claims.md); deep links to [PRD 40](40-trace-explorer.md) |

## CUJs

### CUJ-54 — Inline in the PR
A PR shows a SARIF annotation on the policy line that un-blocked an ATLAS technique, linking to the explorer. **Success:** annotation resolves; deep link works ≥ 99%.

### CUJ-55 — Did the SOC see it?
Weekly drill: of 40 simulated attacks, 31 raised SIEM alerts within 5 min (p95), 6 logged-only, 3 silent. **Success:** per-case detection states + latency reported.

## Success metrics

| Metric | Target |
|---|---|
| Emitted artifacts validate (SARIF/OSCAL/OCSF/STIX/CycloneDX) in CI | 100% |
| First-party integrations shipped | ≥ 10 by v0.1.x |
| Time to wire CI + code-scanning (new repo) | ≤ 10 min |
| Result → ticket latency p95 | ≤ 5 min |
| Duplicate-ticket rate | ≤ 2% |
| Round-trip lossless on required fields | 100% |
| Imports from Inspect/promptfoo/garak/AgentDojo/PyRIT | 5/5 sources, ≥ 95% mapping |
| SIEM-detection validation latency reported p50/p95 | measured per case |
| Offline spool: no data loss across 24 h outage | 100% |

## Dependencies
F23, F24, F37, F47, F58, F65, F72 · [PRD 33](33-exposure-ledger-and-waivers.md), [PRD 40](40-trace-explorer.md), [PRD 42](42-standards-and-claims.md).

## Boundaries & non-goals
- Integrations are adapters, not a platform; standards first, vendor connectors by demand.
- Privacy: payloads/PII excluded by default; content capture opt-in.
- We don't run a required hosted service; webhook relay self-hosted.

## Open questions
1. OCSF class mapping (Detection vs. Vulnerability vs. Compliance Finding) — pilot with two SIEMs.
2. Community adapter model for long-tail integrations.
