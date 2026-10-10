# Security Audit — v0.1.0

**Status:** 🚧 **pending** (published at WBS M32). 0 unresolved findings required for release.

## Scope

- API/credential handling in artifacts and bundles (redaction before bundle).
- Driver/target sandbox (untrusted packs).
- Audit-trail integrity (append-only, rotated, hash-chained).
- Pack trust (signatures, trust levels, registry poisoning).
- agentdrill's own surface — the [evasion pack](../../prd/06-security-baseline.md) result.
- **Effect-witness integrity** — witness in a separate trust domain; tamper detected; `witness_unavailable`
  blocks a `blocked` claim ([PRD 26](../../prd/26-independent-effect-witness.md)).
- **Adversary Lab isolation** — zero non-loopback egress; ground-truth log ([PRD 27](../../prd/27-adversary-lab.md)).
- **Rules of engagement / bystander safety** — zero out-of-scope actions; independent abort
  ([PRD 35](../../prd/35-rules-of-engagement-and-safe-fire.md)).
- **Detonation isolation** — VM/microVM; no real egress ([PRD 36](../../prd/36-extension-detonation-lab.md)).
- **Attestation + waiver integrity** — signatures, freshness/invalidation, hash-chained waivers
  ([PRD 33](../../prd/33-exposure-ledger-and-waivers.md), [PRD 34](../../prd/34-drill-attestations-and-deploy-gate.md)).

## Findings

| # | Finding | Severity | Status |
|---|---|---|---|
| — | — | — | — |

## Predecessor gap closure

The predecessor's acknowledged security gaps are closed at the foundation (G1–G14) —
[PRD 24](../../prd/24-predecessor-gap-closure.md). The audit re-verifies each with a test.

## Posture

Fail-closed on tamper; `external` packs sandbox-only; secrets referenced by name, never persisted; signed
releases with SBOM + provenance. OpenSSF baseline recorded in [release evidence].
