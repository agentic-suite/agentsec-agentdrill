# Effect Witness & Adversary Lab — Reference

**Status:** normative (M23). Implementation: `src/agentdrill/witness/` + `src/agentdrill/lab/`. Design:
[effect-witness-and-lab](../design/effect-witness-and-lab.md). Specs:
[PRD 26](../prd/26-independent-effect-witness.md) · [PRD 27](../prd/27-adversary-lab.md).

## Effect declarations (23.1, F87)

`Effect(kind, target, detail=)`; `EffectDeclaration(case_id, forbidden, required_preserved)` +
`declares_effects` / `require_effects` (`EffectError` — a case with no effects is flagged).

## Witnesses (23.2–23.4, F87)

- `CanaryWatch` / `file_fingerprint` / `watch_canary` — FS hash+inode canary.
- `Sinkhole(token)` — loopback (http/dns/tcp) with a per-run token; `measure_overhead`.
- `HoneyCredential` (observe_use) + `ProcessWitness` (observe_exec / detected).
- `MockSaas` / `SideEffectLedger` + `ApprovalCheck` / `check_approval` (executed-without-approval).

## Two-oracle verdict (23.5, F87)

`two_oracle_verdict(case_id, defense=, effect_seen=, witness_available=)` → `TwoOracleVerdict` with the
outcome `blocked` / `missed` / `degraded` / `blocked_silently` / `witness_discrepancy`; a
`witness_unavailable` finding and a `live`/`none` witness label. A defense `blocked` with the effect
seen is a `witness_discrepancy` — a first-class finding.

## Adversary Lab (23.6–23.8, F88)

- `AdversaryLab` / `build_lab` / `event_log`; `LAB_COMPONENTS` and `EVIL_MCP_BEHAVIORS`; same seed ⇒ same
  event log.
- `CARRIERS` (≥12) / `carrier_matrix` / `render_carrier`.
- `LabIsolation` / `enforce_loopback` (`EgressViolation` — zero non-loopback egress) + `pin_lab`
  (`lab@version` in the manifest).
