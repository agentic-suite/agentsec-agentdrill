# agentdrill M28 — Exposure Ledger, Attestations & Rules of Engagement Execution Plan

**Spec:** [WBS M28](../wbs/v0.1.0/wbs-v0.1.0-part15-context-governance.md) · [design](../design/exposure-attestation-roe.md) · [PRD 33](../prd/33-exposure-ledger-and-waivers.md), [PRD 34](../prd/34-drill-attestations-and-deploy-gate.md), [PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md).

## Constraints
Waivers **annotate, never relabel**; integrity findings not waivable. Attestation ≠ "secure". RoE required for any non-demo run; canary-only invariants.

## Tasks
- **T1 — Ledger lifecycle (28.1):** states + per-finding CVSS v4.0 + AIVSS vector.
- **T2 — Waivers (28.2):** expiry, drilled compensating control, approvers, auto-reopen, known-miss budget. *RED:* waived miss still visible; expired never suppresses. *GREEN.*
- **T3 — Ledger exports (28.3):** OSCAL POA&M/assessment-results; SARIF suppressions; ticket sync.
- **T4 — Attestation (28.4–28.5):** in-toto `agentdrill/drill-result/v1` + Sigstore; freshness/invalidation; consumers (CLI, GH Action, K8s policy, agentgate). *RED:* forged attestation rejected; verify ≤2 s. *GREEN.*
- **T5 — RoE (28.6):** signed RoE; fail-closed preflight. *RED:* planted out-of-scope attempts refused 100%. *GREEN.*
- **T6 — Interlocks (28.7):** global abort (p95 ≤5 s), dead-man switch, watchdogs, verified teardown, consent gate.
- **T7 — Gates + docs (28.T/.C/.L/.CR/.D).**

**Exit:** zero out-of-scope actions; zero expired waivers suppressing; attestation freshness/consumer checks; abort p95. **Closure:** standard.
