# agentdrill M22 — NFRs, Security Hardening & Resilience Execution Plan

**Spec:** [WBS M22](../wbs/v0.1.0/wbs-v0.1.0-part12-hardening-fieldtest.md#milestone-m22--nfrs-security-hardening--resilience) · [PRD 13](../prd/13-non-functional-requirements.md) · [PRD 06](../prd/06-security-baseline.md).

## Constraints
Exit gate + gates. **Fail-closed under faults**; `external` packs OS-isolated; audit tamper-evident.

## Tasks
- **T1 — Performance & scale (22.1):** per-pack budget; parallel + backpressure; oracle/judge cache + `cache stats`. *RED:* perf-budget test. *GREEN.*
- **T2 — Fault injection & fail-closed (22.2):** faults across runner/targets/oracles/drivers; never silently green.
- **T3 — Untrusted-pack hardening (22.3):** OS-level sandbox (Docker, `--network none`, read-only root, caps) required for `external`; audit **rotation + hash-chain integrity** (G4); secret sanitization. *RED:* audit-tamper detected. *GREEN.*
- **T4 — Portability (22.4):** Python 3.10+, macOS/Linux, local-first.
- **T5 — Cost controls (22.5):** `--max-cost`; caching; reporting.
- **T6 — Self-observability (22.6):** doctor / validate / audit log / run summary.
- **T7 — Gates + docs (22.T/.C/.L/.CR/.D).**

**Exit:** NFRs met; fault suite fail-closed; external packs isolated; audit tamper-evident; local-first both OSes. **Closure:** standard.
