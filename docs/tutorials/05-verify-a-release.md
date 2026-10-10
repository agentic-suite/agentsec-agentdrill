# Tutorial 05 — Verify a Release

**You'll get:** confidence in a published benchmark without trusting the publisher.

```sh
# 1. Fetch + verify artifacts (offline, zero-install verifier)
agentdrill benchmark export --release v0.1.0 --out ./bench
agentdrill verify ./bench/release-v0.1.0.json
#    → intact / complete / honest-shaped

# 2. Reproduce against the pinned config
agentdrill run --pack ./bench/packs/incidents-core@1.3.0 \
  --target ./my-stack.yaml --manifest ./bench/run-manifest.json
```

## What the verifier checks

- **Signatures + provenance** on packs, manifests, and results.
- **Hash bindings** (`pack@version+hash` ↔ numbers).
- **Labels**: efficacy status, attestation (`live`/`fixture`/`mock`), severity.
- **Statistical shape**: multi-seed numbers with CIs — bare percentages are rejected.
- **Redaction receipts** in evidence bundles.

## What "honest-shaped" means

The artifact is internally consistent and reports what it claims — including the **misses**. A result with
no misses is suspicious, not impressive.

## If you disagree

File a **dispute**: the outcome is confirmed / corrected (flagged) / withdrawn **on the record within 14
days** ([reproduce-the-benchmark](../runbooks/reproduce-the-benchmark.md)). No silent edits.
