# agentdrill M21 — Predecessor Absorption & Gap Closure Execution Plan

**Spec:** [WBS M21](../wbs/v0.1.0/wbs-v0.1.0-part11-dx-absorption.md#milestone-m21--predecessor-absorption--gap-closure) · [PRD 10](../../prd/10-feature-parity.md) · [PRD 24](../../prd/24-predecessor-gap-closure.md).

## Constraints
Exit gate + gates. **No capability or gap carries forward silently** — delivered+tested / delegated / waived.

## Tasks
- **T1 — Absorption ledger verification (21.1):** every PRD 10 §A/§B row delivered+tested, delegated, or waived. *RED:* a ledger-gate test failing on an unowned row. *GREEN.*
- **T2 — Gap closure G1–G14 (21.2):** a passing test per closed gap (G1 trust, G2 signing, G3 path-safety, G4 audit integrity, G5 OS sandbox, G6 SBOM, G8 trust matrix, G9 attestation, G10 exit-code meta, G11 criteria meta, G12 model sanity, G13 env resolution, G14 cost); G7 waived with a reason.
- **T3 — Parity gate (21.3):** executable gate; fails CI on drift.
- **T4 — Predecessor retention plan (21.4):** agentdrill self-contained; M24 makes the predecessor private (never delete).
- **T5 — Gates + docs (21.T/.C/.L/.CR/.D).**

**Exit:** ledger complete; every gap closed-or-waived; parity gate CI-enforced. **Closure:** standard.
