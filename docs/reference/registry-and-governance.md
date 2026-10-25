# Registry & Governance — Reference

**Status:** normative (M16). Implementation: `src/agentdrill/registry/`. Design:
[registry](../design/registry.md). Spec: [PRD 17](../prd/17-pack-registry-and-governance.md).

## Registry index (16.1)

`content_address(content)` = `sha256:` of the canonical content. `entry_for_pack(pack, publisher=, trust=)`
→ `RegistryEntry`; `build_index(entries)` → `RegistryIndex`. `sign_index(index, signer)` /
`verify_index(index, verifier)` verify **offline** (a tampered or unsigned index fails).

## Signing + verified publishers (16.2)

`Signer`/`Verifier` (default `HmacSigner`, stdlib). `sign_entry`/`verify_entry`; `PublisherRegistry` binds
a verified identity to a key id. `verify_pack(entry, verifier=, publishers=)` → `PackVerification`;
`require_verified` raises `PackVerificationError` for an unsigned/tampered/unknown-publisher pack.

## Trust levels (16.3)

`normalize_trust` (`built-in`/`local`/`external`); `enforce_trust(trust, adapter_type=, sandbox=)` —
`external` ⇒ sandboxed subprocess only; `is_sandbox_required`; `is_benchmark_publishable` (external never).

## Contribution flow (16.4)

`lint_pack(pack, fixtures_dir=, methodology=)` → `LintResult` (schema, `incident_ref`, tags, oracle,
fixtures, methodology). `ReviewDecision` + `require_publishable(pack_ref, trust=, decisions=)` — an
unreviewed or external pack cannot be benchmark-published.

## Deprecation + takedown (16.5)

`GovernanceLog` (append-only, hash-chained); `apply_deprecation(index, log, name=, version=, note=)` marks
an entry with a migration note; `apply_takedown(index, log, name=, version=, reason=)` removes it — both
recorded on the chain.

## Registry sync (16.6, F75)

`sync_index(remote, verifier=)` adopts a remote index only if its signature verifies (`SyncError`
otherwise). `is_outdated(local, remote)` → `OutdatedEntry[]`. CLI: `agentdrill registry sync --from --key
[--out]`; `agentdrill pack outdated --from`.
