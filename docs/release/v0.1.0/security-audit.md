# Security Audit — v0.1.0

**Status:** ✅ **published** 2026-10-25. **Result: 0 unresolved findings.**

**Method.** Self-audit of agentdrill plus the field evidence. Every claim below cites the implementing module
and a passing test; the security-relevant suite was run for this audit: **192 tests, 0 failures**
(`pytest tests/test_m18_privacy.py tests/test_m16_trust.py tests/test_security*.py
tests/test_m14_evasion_pack.py tests/test_m23_*.py tests/test_m28_*.py tests/test_m29_detonation.py
tests/test_egress.py tests/test_tools_secrets.py`). Two scope statements in the pre-audit skeleton overstated
mechanisms; both are recorded as findings and corrected (F-1, F-2).

## Scope and evidence

| Area | Mechanism (module) | Evidence | Result |
|---|---|---|---|
| Credential handling / redaction | `security/sanitize.py` — redaction before any artifact/bundle is written | `tests/test_m18_privacy.py`, `tests/test_m23_credentials.py` | ✅ no secret persisted |
| Secret scanning of our own output | `tools/secrets_scanner.py` | `tests/test_tools_secrets.py` | ✅ |
| Driver/target sandbox | `security/sandbox.py` — env allowlist + `sandboxed_run`, container path `run_in_container` | `tests/test_security_sandbox_coverage.py`, `tests/test_security_sandbox_integration.py` | ✅ |
| Egress policy | `security/egress.py` — `EgressPolicy` with deny-all / air-gapped / strict-production presets | `tests/test_egress.py` | ✅ policy evaluated (see F-2) |
| Audit trail | `security/audit.py` — **append-only** JSON log under the run dir | `tests/test_security.py`, `tests/test_m22_hardening.py` | ✅ (see F-1) |
| Pack trust | trust levels + `min_agentdrill` gate; unknown/newer → `ConfigError` (exit 2) | `tests/test_m16_trust.py`, `tests/test_attack_pack_schema.py` | ✅ fail-closed |
| Evasion pack (our own surface) | `security/self_attack.py` + `security/cadence.py` | `tests/test_m14_evasion_pack.py`, `tests/test_m14_cadence.py` | ✅ |
| Effect-witness integrity | `witness/verdict.py` — a `blocked` claim requires the witness; otherwise finding `witness_unavailable` | `tests/test_m23_verdict.py`, `tests/test_m23_side_effects.py` | ✅ blocks over-claim |
| Rules of engagement / bystander safety | `roe/rules.py` — signed RoE (`sign_roe`/`verify_roe`), per-action `ScopeReceipt` (hash-chained via `hash_prev`), `preflight` gate, abort conditions | `tests/test_m28_roe.py` | ✅ zero out-of-scope actions |
| Detonation isolation | `detonation/` — isolated run path, no real egress | `tests/test_m29_detonation.py` | ✅ |
| Attestation integrity | `attestations/drill.py` — `sign_statement`/`verify_statement`; a `mock` attestation is refused | `tests/test_m28_attestation.py` | ✅ |
| Waiver integrity + freshness | `ledger/waivers.py` — per-waiver HMAC-SHA256 digest; `attestations/freshness.py` — `check_freshness`, expired waivers auto-invalidate | `tests/test_m28_waivers.py`, `tests/test_m28_freshness.py`, `tests/test_m28_ledger.py` | ✅ hash-chained + auto-invalidate |

## Findings

| # | Finding | Severity | Status |
|---|---|---|---|
| F-1 | The audit-trail scope line claimed the log is **rotated and hash-chained**. It is not: `security/audit.py` writes an **append-only** JSON log with no rotation. Hash-chaining exists only where the design requires it (RoE scope receipts, waiver digests). | Low (documentation accuracy) | **Resolved** |
| F-2 | The lab-isolation scope line implied a network firewall. `security/egress.py` is a **policy model/evaluator** (deny-all / air-gapped presets); v0.1.0 enforces isolation through the container/subprocess boundary, not a host firewall. | Low (documentation accuracy) | **Resolved** |

No product security defect was found. Both findings are overstatements in the pre-audit skeleton, corrected in
this document; the underlying mechanisms are sound and test-backed.

## Predecessor gap closure (G1–G14)

The predecessor's acknowledged gaps are closed at the foundation ([PRD 24](../../prd/24-predecessor-gap-closure.md)).
The audit re-verifies each with the test that guards it; the gap-closure ledger and its gate are green at the
M21 parity gate. Nothing in this audit re-opens a G-number.

## Posture

- **Fail-closed on tamper**: an invalid signature, an unsupported pack, a stale attestation, or a witness that
  cannot confirm a `blocked` claim all fail loudly (exit 2/3), never silently pass.
- **Secrets**: referenced by name, never persisted; every artifact and LLM capture is sanitized before write,
  and the field-test leak gate scans the committed results (`scripts/fieldtest/scan_results.py`).
- **Releases**: builds ship with a CycloneDX SBOM, `SHA256SUMS`, and signed SLSA provenance
  ([release tooling](../../../scripts/release/dry_run.py); `make release-dry-run` green).
- **OpenSSF**: baseline recorded in the [compliance matrix](compliance-matrix.md).
