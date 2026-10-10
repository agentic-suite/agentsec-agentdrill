# agentdrill M32 — Release Readiness Execution Plan

**Spec:** [WBS M32](../wbs/v0.1.0/wbs-v0.1.0-part17-fieldtest-release.md) · [PRD 07](../prd/07-success-metrics.md) · [PRD 09](../prd/09-roadmap.md).

## Constraints
Exit gate + gates. **ALWAYS the last milestone.** Nothing is tagged before M32; the predecessor is made private (never deleted).

## Tasks
- **T1 — Release tooling (32.1):** build + CycloneDX SBOM + checksums + signed provenance via `release.yml`; `make release-dry-run` green.
- **T2 — First-run verification (32.2):** timed clean-machine `quickstart` ≤15 min. *RED:* timing test. *GREEN.*
- **T3 — Security audit (32.3):** self-audit + evasion result + RoE/bystander analysis; 0 unresolved findings.
- **T4 — SBOM + signed artifacts + provenance (32.4):** verify independently; SLSA target recorded.
- **T5 — Compliance matrix + evidence indexes + OpenSSF (32.5):** OWASP ASI/ATLAS/NIST/EU + per-framework evidence index (with `not covered`) + OpenSSF baseline.
- **T6 — Versioning + backwards-compat policy (32.6):** one version across package/CLI/CHANGELOG; oracle/pack/lab pins. *RED:* version-consistency test. *GREEN.*
- **T7 — Release notes + compatibility table (32.7):** honest notes; generated compat table (L0–L4, AWC).
- **T8 — Tag v0.1.0 (32.8):** signed tag + GitHub release + published benchmark (misses included; tiers/k/CIs; witness coverage).
- **T9 — Predecessor private (32.9):** retained + `private`, never deleted.
- **T10 — Gates + docs (32.T/.C/.L/.CR/.D).**

**Exit:** full PRD coverage + absorption ledger tested (R1–R79); first-run ≤15 min; audit + compliance + evidence indexes + notes published; SBOM + signed artifacts + drill attestation; **v0.1.0 tagged**; predecessor private. **Closure:** standard.
