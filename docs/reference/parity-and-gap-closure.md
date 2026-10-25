# Parity & Gap Closure — Reference

**Status:** normative (M21). Implementation: `src/agentdrill/parity/`. Specs:
[PRD 10 feature parity](../prd/10-feature-parity.md) ·
[PRD 24 predecessor gap closure](../prd/24-predecessor-gap-closure.md).

**Nothing carries forward silently.** Every capability is delivered + tested, delegated to a named tool,
or waived with a reason; every acknowledged predecessor gap (G1–G14) is closed with a test or waived.

## Absorption ledger (21.1)

`LedgerRow(capability, status, detail=)` with `status` in `delivered` / `delegated` / `waived`;
`AbsorptionLedger` + `build_ledger` / `validate_ledger` (`LedgerError`). A waived row needs a reason; a
delegated row needs a named tool.

## Gap closure G1–G14 (21.2)

`Gap(id, description, status, evidence=)`; `default_gaps()` returns the G1–G14 table — every gap
**closed** with a test (G1 trust enforcement, G2 signed packs, G3 path-safety, G4 audit rotation/hash-chain,
G5 OS-level sandbox, G6 SBOM, G8 trust matrix, G9 attestation, G10 exit-code/scoring meta-cases,
G11 criteria-interpolation meta-case, G12 model-surface sanity, G13 env resolution in manifest,
G14 cost governor). **G7 (SQLite) is waived by design.** `validate_gaps` (`GapError`).

## Parity gate (21.3)

`parity_gate(ledger, gaps)` → `ParityResult` (`ok`, `problems`); `require_parity` raises `ParityError`.
The gate is green for the default ledger/gaps and **blocks on drift** — it is CI-enforced.

## Predecessor retention plan (21.4)

`RetentionPlan` + `build_retention` / `retention_record`: agentdrill is **self-contained**; the
predecessor repository is **made private at M32 — never deleted** (`never_delete`).
