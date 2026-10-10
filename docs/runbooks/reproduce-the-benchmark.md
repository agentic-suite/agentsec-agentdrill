# Runbook — Reproduce the Benchmark

**Goal:** a third party re-runs a published benchmark against the published pinned config and gets the
**same numbers — including the misses**.

```sh
# 1. Fetch the published release (packs + manifest + traces)
agentdrill benchmark export --release v0.1.0 --out ./bench

# 2. Verify the artifacts offline (nothing installed but agentdrill, no network)
agentdrill verify ./bench/release-v0.1.0.json
#    → intact / complete / honest-shaped

# 3. Re-run the pinned set against your cloned stack
agentdrill run --pack ./bench/packs/incidents-core@1.3.0 \
  --target ./my-stack.yaml \
  --manifest ./bench/run-manifest.json      # pins honored

# 4. Compare
agentdrill pack diff ./bench/results.json ./my-run/
```

**Expected:** identical blocked/missed/degraded per case (or a **flagged** re-pin note if a pin changed).
Every published number is multi-seed (mean ± std) with CIs; every cell links its trajectory.

**If you disagree:** file a **dispute** — outcomes are confirmed / corrected (flagged) / withdrawn **on the
record within 14 days**. No quiet edits (golden-lock, DD-28).

**Contents of a `mock`/`fixture` result:** a `mock`-attested result never publishes; a `fixture`-attested
one publishes with its label visible (K1, ADR-0009).
