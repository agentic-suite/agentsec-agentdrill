# agentdrill M16 — Pack Registry, Signing & Governance Execution Plan

**Spec:** [WBS M16](../wbs/v0.1.0/wbs-v0.1.0-part9-registry-interop.md#milestone-m16--pack-registry-signing--governance) · [PRD 17](../../prd/17-pack-registry-and-governance.md).

## Constraints
Exit gate + gates (`.T/.C/.L/.CR/.D`). External packs sandbox-only; registry poisoning rejected (RK-16).

## Tasks
- **T1 — Registry model + index (16.1):** signed content-addressed `registry.json`; offline-verifiable.
- **T2 — Signing + verified publishers (16.2):** Sigstore; `pack verify` before install. *RED:* unsigned/tampered pack rejected. *GREEN.*
- **T3 — Trust levels (16.3):** `built-in`/`local`/`external` enforced at load/run; external ⇒ sandbox-only.
- **T4 — Contribution flow (16.4):** `init` → `pack lint` → independent review → `publish` → `verify`.
- **T5 — Deprecation + takedown (16.5):** recorded on the signature chain.
- **T6 — Registry sync (16.6, F75):** read-only, signature-verified; `pack outdated`.
- **T7 — Gates + docs (16.T/.C/.L/.CR/.D).**

**Exit:** signed packs; trust enforced; contribution reviewed-like-code (R11); poisoning rejected. **Closure:** standard.
