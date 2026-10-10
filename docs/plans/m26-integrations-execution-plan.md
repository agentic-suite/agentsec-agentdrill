# agentdrill M26 — Security Ecosystem Integrations Execution Plan

**Spec:** [WBS M26](../wbs/v0.1.0/wbs-v0.1.0-part14-byod-integrations.md) · [design](../design/integrations.md) · [PRD 38](../prd/38-security-ecosystem-integrations.md), [PRD 42](../prd/42-standards-and-claims.md).

## Constraints
Standards first; every emitted artifact validates against its official schema in CI. Offline-safe; no mandatory hosted service.

## Tasks
- **T1 — SARIF + JUnit (26.1):** rule=case; severity vector; tier; witness ref; ASI/ATLAS; fingerprints; suppressions=waivers; `untested`→skipped. *RED:* 100% schema-valid. *GREEN.*
- **T2 — OTel emit/read (26.2):** `gen_ai.*` spans; semconv pinned; read stage timing.
- **T3 — OCSF/ECS + OSCAL + STIX (26.3):** validators green.
- **T4 — CI/code-scanning + ticketing (26.4):** GitHub code scanning upload; GitLab SAST; Slack/Teams/Jira/ServiceNow/PagerDuty/Issues/Linear; ledger status sync.
- **T5 — Inbound import (26.5):** Inspect/promptfoo/garak/AgentDojo/PyRIT → normalized (`imported`); inventory import.
- **T6 — SIEM/EDR validation (26.6):** `detected/alerted/logged/missed` + latency.
- **T7 — Reliability (26.7):** idempotency; stable IDs; retries+DLQ; signed webhooks; offline spool. *RED:* no loss across 24 h outage. *GREEN.*
- **T8 — Gates + docs (26.T/.C/.L/.CR/.D).**

**Exit:** ≥10 first-party integrations; schema-valid 100%; imports 5/5; SIEM query working; no data loss. **Closure:** standard.
