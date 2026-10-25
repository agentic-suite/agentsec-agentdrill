# Security Ecosystem Integrations — Reference

**BLUF:** How agentdrill emits findings in official interchange formats, wires them into CI/SIEM/
ticketing/GRC, imports external results, and validates SIEM/EDR detection. **Normative (M26).** Package:
`agentdrill/integrations/`. Source design: [design/integrations.md](../design/integrations.md); PRD
[38](../prd/38-security-ecosystem-integrations.md) (R74 / F100), [42](../prd/42-standards-and-claims.md).

## Output-format matrix

| Target | Format | Module | Version pin | Validator |
|---|---|---|---|---|
| GitHub/GitLab code scanning, IDE | **SARIF 2.1.0** | `sarif.py` | `SARIF_VERSION` | `validate_sarif` — **official OASIS schema** (vendored `schemas/sarif-2.1.0.json`) |
| Any CI | **JUnit XML** | `junit.py` | — | `validate_junit` — well-formed + count-consistent; rejects DTD/entities |
| Trace backends | **OTel** (GenAI semconv) | `otel.py` | `GEN_AI_SEMCONV_VERSION` | span-coverage gate (`require_span_coverage`, ≥95 %) |
| SIEM/data lake | **OCSF** 1.3 detection finding | `ocsf.py` | `OCSF_VERSION` | `validate_ocsf` — required-field/enum check |
| SIEM/data lake | **ECS** 8.11 alert | `ocsf.py` | `ECS_VERSION` | `validate_ecs` — required-field/enum check |
| GRC | **OSCAL** 1.1.2 assessment-results / POA&M | `oscal.py` | `OSCAL_VERSION` | `validate_oscal` — required-field check |
| Intel | **STIX 2.1** bundle | `stix.py` | `STIX_VERSION` | `validate_stix` — required fields + `<type>--<uuid>` id form |
| GitLab SAST | GitLab SAST report 15.0.0 | `code_scanning.py` | `GITLAB_SAST_VERSION` | report shape asserted in tests |

> **Schema-validity note (honest):** SARIF is validated against the *vendored official* OASIS schema.
> OCSF/OSCAL/STIX validators enforce each format's required fields/enums derived from the specs; the full
> official JSON schemas are **not** vendored (the OCSF registry is impractical to vendor). Vendoring the
> remaining official schemas is tracked as a follow-up.

## The neutral projection

Every emitter renders `IntegrationFinding` (`model.py`) — identity (`case_id`), honest `outcome`
(`blocked`/`missed`/`degraded`/`untested`), ATLAS/OWASP tags, severity, and the evidence fields a published
number must carry: attacker `tier`/`k` (M24) and independent `witness_ref` (M23). `findings_from_report`
projects an M10 `Report`. A finding outside the honest vocabulary fails loudly.

## Integration guide

```bash
# Emit from an M10 report JSON
agentdrill export sarif  --report report.json [--out out.sarif]
agentdrill export junit  --report report.json [--out junit.xml]
agentdrill export otel   --report report.json [--out trace.json]
agentdrill export ocsf   --report report.json [--out events.json]
agentdrill export oscal  --report report.json [--title "Q4 drill"] [--out oscal.json]
agentdrill export stix   --report report.json [--out bundle.json]
```

Delivery (code scanning, tickets) is **transport-injected** so nothing in the library owns a network
client or stores credentials:

```python
from agentdrill.integrations import (
    github_code_scanning_request, to_sarif, ticket_request, deliver_tickets,
)
req = github_code_scanning_request(to_sarif(findings), owner="acme", repo="widgets",
                                   commit_sha=sha, ref="refs/heads/main", token=token)
deliver_tickets([req], transport=my_http_sender)
```

Vendors: Slack, Teams, Jira, ServiceNow, PagerDuty, GitHub Issues, Linear (`TICKET_VENDORS`). Tickets
carry a **stable key** `pack:case` (`ticket_key`) so a re-run is idempotent (duplicate rate ≤ 2 %).

### Supporting a new code-scanning host
Build an `HttpRequest` with `ticket_endpoint`/`ticket_request`, or call the emitter directly — the
transport is yours.

## Deep-link contract

- **SARIF fingerprints:** `partialFingerprints["agentdrill/v1"]` = `sha256(pack_ref \x00 case_id)` — stable
  across runs (never includes timestamps/costs), so results dedup across CI runs (≥99 %).
- **Trace links:** SARIF/OCSF/OSCAL/STIX carry the case id and, when M10 recorded one, a `trace` property
  pointing at the `TraceStore` entry (deep link to the M30 explorer).
- **Waivers:** SARIF `suppressions` (`kind="external"`) and OCSF `status_id=Suppressed` map to exposure-ledger
  waivers (M28). A waiver **suppresses a gate, never relabels a miss** (the true outcome is preserved).

## Reliability

`reliability.py`: stable ids, `RetryPolicy` exponential backoff (rate-limit aware via `parse_retry_after`),
`DeliveryLedger` (SQLite idempotent upsert across runs), HMAC-signed webhooks, and an **`OfflineSpool`**
with atomic durable writes and exactly-once replay — no request is lost across a prolonged outage.

## Inbound import

`importer.py` normalizes **Inspect / promptfoo / garak / AgentDojo / PyRIT** results into imported findings
marked `imported` (lower trust). `mapping_report`/`require_mapping` enforce the **≥95 %** field-mapping gate.
`parse_inventory` normalizes a capability inventory for M27's attack-path graph.

> Distinct from M17's `interop/importers.py`, which imports *suites/inputs* into packs; 26.5 imports
> *results/outputs* into normalized findings.

## SIEM/EDR detection validation

`siem.py` queries the customer SIEM/EDR (injected `SiemQuery`) for the expected detection within a time
budget and reports a per-case state — `alerted` / `detected` / `logged` / `missed` — plus latency
(`detection_latencies`: p50/p95/max). A query failure raises `SiemError`; a broken SIEM is **never** reported
as a silent miss (CUJ-55).

## Known limitations

- Official JSON-schema validation is full for SARIF only (see the note above).
- The live SIEM query, ticket delivery and code-scanning upload are exercised in the field (M31); the state
  machines and payload shapes are proven offline.
- No hosted viewer/service is required; the webhook relay is self-hosted.
