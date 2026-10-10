# agentdrill M25 — BYOD & Neutral Head-to-Head Execution Plan

**Spec:** [WBS M25](../wbs/v0.1.0/wbs-v0.1.0-part14-byod-integrations.md) · [design](../design/byod-and-neutral-head-to-head.md) · [PRD 29](../prd/29-bring-your-own-defense.md).

## Constraints
Neutrality is binding: pre-registration, right-of-reply, licensed-config-only, **no composite score/ranking**. OSS/free defenses first.

## Tasks
- **T1 — Contract + SDK (25.1):** decision points, I/O, evidence, **config digest**, fail-mode, version, ToS notes. *RED:* a request/response defense adapts in ≤2 days. *GREEN.*
- **T2 — Conformance kit (25.2):** round-trip/determinism/evidence/fail-mode → conformance level.
- **T3 — Defense Zoo (25.3):** OSS-first adapters (OPA/Cedar, Llama Guard/Prompt Guard, NeMo, Docker/gVisor, harness sandboxes).
- **T4 — Neutral head-to-head (25.4):** identical inputs across N defenses; utility/false-block+CI; cost/latency; fail-open/closed; no ranking.
- **T5 — Neutrality process (25.5):** pre-registration, right-of-reply (14 d), `tos_reviewed`, conflict disclosure, default-vs-tuned, counsel sign-off.
- **T6 — Gates + docs (25.T/.C/.L/.CR/.D).**

**Exit:** ≥2 conforming OSS adapters (≥6 classes by v0.2); third-party adapter passes kit; head-to-head identical-input with right-of-reply; zero composite scores. **Closure:** standard.
