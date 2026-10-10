# agentdrill M18 — Lifecycle Execution Plan

**Spec:** [WBS M18](../wbs/v0.1.0/wbs-v0.1.0-part10-lifecycle-oracle.md#milestone-m18--lifecycle--intake-fix-validation-seams-attestation-verifier-quickstart) · [PRD 20](../prd/20-efficacy-freshness-lifecycle.md).

## Constraints
Exit gate + gates. Freshness (7-day intake), fix-validation, seams, attestation (`mock` never publishes), verifier (offline), privacy (receipts), quickstart (≤15 min).

## Tasks
- **T1 — Incident-intake pipeline (18.1, F60):** watchlist → triage ≤7 days (pack draft or N/A + reason) → template → review; deprecate stale packs. *RED:* SLA test. *GREEN.*
- **T2 — Remediation validation (18.2, F61):** fixed miss ⇒ permanent pinned regression; `fix_decay` release-blocking.
- **T3 — Seam probing (18.3, F62):** denied-then-retried + multi-enforcer composition; `seam_gap` names both controls.
- **T4 — Target attestation (18.4, F63):** live/fixture/mock weakest-link; `mock` never publishes. *RED:* mock-publish rejected. *GREEN.*
- **T5 — Standalone verifier (18.5, F64):** offline, zero-install; three verdicts.
- **T6 — Evidence privacy (18.6, F65):** redaction-before-bundling + receipts; verifier checks receipts.
- **T7 — Quickstart + demo stack (18.7, F66):** ≤15 min; watermarked `never evidence`.
- **T8 — MCP + memory pack classes (18.8, F19/F20).**
- **T9 — Closes-the-loop policy suggestion (18.9, F21):** advisory rule + what-if replay.
- **T10 — Gates + docs (18.T/.C/.L/.CR/.D).**

**Exit:** intake ≤7 days; fix holds; seams named; attestation enforced; verifier offline; quickstart ≤15 min. **Closure:** standard.
