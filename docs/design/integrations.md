# Security Ecosystem Integrations — Design

**BLUF:** Findings must land where buyers work. Emit in official interchange formats, wire into CI/SIEM/
ticketing/GRC, import external suites, and validate SIEM/EDR detection. WBS
[M26](../wbs/v0.1.0/wbs-v0.1.0-part14-byod-integrations.md). Reference:
[PRD 38](../prd/38-security-ecosystem-integrations.md), [PRD 42](../prd/42-standards-and-claims.md).

> **Design intent** (pre-build). Rewritten against the built system at M31–M32.

## Emitters (outbound)

| Target | Format | Key mapping |
|---|---|---|
| GitHub/GitLab code scanning, IDE | **SARIF 2.1.0** | rule = case id; `properties`={tier, witness, ASI/ATLAS}; `partialFingerprints`; `suppressions` = waivers |
| Any CI | **JUnit XML** | `missed`→failure; `untested`→skipped(+reason) |
| Trace backends | **OTel** (GenAI semconv, pinned) | drill = trace; case = span; stage timestamps (F37) |
| SIEM/lake | **OCSF / ECS** | detection/finding object + ATT&CK/ATLAS |
| GRC | **OSCAL** assessment-results/POA&M | evidence index; ledger export |
| Intel | **STIX 2.1** | adversary cards (F54), incident briefs |

Plus chat/ticket/on-call adapters: Slack, Teams, Jira, ServiceNow, PagerDuty, GitHub Issues, Linear
(ticket per finding family; status synced to the ledger).

## Importers (inbound)

Inspect / promptfoo / garak / AgentDojo / PyRIT → normalized results (marked `imported`, lower trust label);
inventory import ([PRD 31](../prd/31-attack-path-and-blast-radius.md)).

## BAS-style detection validation

After a drill, query the customer SIEM/EDR for the expected detection within a time budget; report
`detected / alerted / logged / missed` per case with latency.

## Reliability

Idempotent upserts; stable IDs/fingerprints (dedup ≥99%); retries + backoff; dead-letter queue; signed
webhooks; rate-limit aware; **offline spool** (no loss across a 24 h outage).

## Invariants

1. Standard formats first; vendor-specific connectors only by demand.
2. Privacy: payloads/PII excluded by default; content capture opt-in; redaction receipts apply (F65).
3. No mandatory hosted service; webhook relay self-hosted.

## Open questions
1. OCSF class mapping (Detection vs. Vulnerability vs. Compliance Finding) — pilot with two SIEMs.
2. Community adapter model for long-tail integrations.
