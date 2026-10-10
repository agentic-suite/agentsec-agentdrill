# agentdrill M24 — Release Readiness Execution Plan

**Spec:** [WBS M24](../wbs/v0.1.0/wbs-v0.1.0-part13-release.md#milestone-m24--release-readiness) · [PRD 07](../../prd/07-success-metrics.md) · [PRD 09](../../prd/09-roadmap.md).

## Constraints
Exit gate + gates. **ALWAYS the last milestone.** Nothing is tagged before M24; the predecessor is made private (never deleted).

## Tasks
- **T1 — Release tooling (24.1):** build + CycloneDX SBOM + checksums + signed provenance via `release.yml`; `make release-dry-run` green.
- **T2 — First-run verification (24.2):** timed clean-machine `quickstart` ≤15 min. *RED:* timing test. *GREEN.*
- **T3 — Security audit (24.3):** self-audit + evasion result; 0 unresolved findings.
- **T4 — SBOM + signed artifacts + provenance (24.4):** verify independently.
- **T5 — Compliance matrix + OpenSSF checklist (24.5):** OWASP/ATLAS/NIST/EU + OpenSSF baseline.
- **T6 — Versioning + backwards-compat policy (24.6):** one version across package/CLI/CHANGELOG. *RED:* version-consistency test. *GREEN.*
- **T7 — Release notes + compatibility table (24.7):** honest notes; generated compat table.
- **T8 — Tag v0.1.0 (24.8):** signed tag + GitHub release + published benchmark (misses included).
- **T9 — Predecessor private (24.9):** retained + `private`, never deleted.
- **T10 — Gates + docs (24.T/.C/.L/.CR/.D).**

**Exit:** full PRD coverage + absorption ledger tested; first-run ≤15 min; audit + compliance + notes published; SBOM + signed artifacts; **v0.1.0 tagged**; predecessor private. **Closure:** standard.
