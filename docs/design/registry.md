# Pack Registry, Signing & Governance — Design

**BLUF:** Packs are treated like **signed packages**: a content-addressed, signed `registry.json` that
verifies **offline**; verified publishers; trust levels enforced at load/run; a **reviewed-like-code**
contribution flow; and deprecation/takedown recorded on a signature chain. External (untrusted) packs
are sandbox-restricted and never benchmark-published.

> **Status:** normative (M16). **Implementation:** `agentdrill/registry/` — `index.py` (content address +
> signed index), `signing.py` (Signer/Verifier), `publisher.py` (verified publishers + `pack verify`),
> `trust.py` (trust matrix), `contribution.py` (lint + review gate), `governance.py` (deprecation/
> takedown chain), `sync.py` (read-only sync + outdated). Reference:
> [registry-and-governance](../reference/registry-and-governance.md). Spec:
> [PRD 17](../prd/17-pack-registry-and-governance.md).

## Registry model + index (16.1)

Each `RegistryEntry` is **content-addressed** (`content_address` = SHA-256 of the canonical pack) and the
`RegistryIndex` is signed over its canonical bytes (`sign_index`/`verify_index`) — so it verifies
**offline**, with no mandatory central service. The default `HmacSigner` is a stdlib keyed signature (no
extra dependency); the production path binds a Sigstore identity (16.2).

## Signing + verified publishers (16.2)

`sign_entry`/`verify_entry` sign a pack entry over its content address; `PublisherRegistry` binds a
verified publisher identity to a key id. `verify_pack`/`require_verified` reject an unsigned pack, a
tampered pack, or an unknown/mismatched publisher — `pack verify` before install.

## Trust levels (16.3)

`built-in` / `local` / `external`, enforced at load/run via the shared `TrustPolicy`: an `external` pack
must use a **sandboxed subprocess** only and is **never benchmark-published** (`is_benchmark_publishable`).

## Contribution flow (16.4)

`init` scaffold → `pack lint` (`lint_pack`: schema, `incident_ref`, tags, oracle, fixtures, methodology)
→ independent review (`ReviewDecision`) → `pack publish` (`require_publishable`: unreviewed or external
cannot publish) → `pack verify`.

## Deprecation + takedown (16.5)

`apply_deprecation` marks an entry with a migration note; `apply_takedown` removes it from the index —
both recorded on an append-only, hash-chained `GovernanceLog` so nothing disappears silently.

## Registry sync (16.6, F75)

`sync_index` adopts a remote index only if its signature verifies (`SyncError` otherwise) — read-only;
`is_outdated` lists newer remote versions (`pack outdated`).
