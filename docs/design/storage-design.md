# Storage & Determinism — Design

**BLUF:** Local-first JSON under `.agentdrill/` (DD-19), with a **run manifest** that makes a run
reproducible and tamper-evident: pinned inputs + environment (names, never values) + pack hash + oracle
versions. Same environment ⇒ same result (R6).

> **Design intent** (pre-build). WBS M8.

## Layout

```
.agentdrill/
  packs/            # resolved/imported packs
  runs/<run_id>/    # run.json, run-manifest.json, recon.json, artifacts/<case_id>.json
  goldens/          # golden expected results per pack version
  comparisons/      # candidate vs. golden/baseline diffs
  benchmarks/       # published BenchmarkRelease tables
  audit/            # append-only, rotated, hash-chained log
```

## Run manifest (`run-manifest.json`)

```json
{
  "run_id": "run-20261009-143022-a1b2",
  "pack": {"name": "incidents-core", "version": "1.3.0", "hash": "sha256:…"},
  "host": {"os": "macOS 15", "arch": "arm64", "python": "3.12.4"},
  "targets": [{"type": "policyweave-output", "attestation": "live", "digest": "sha256:…"}],
  "drivers": [{"type": "claude-code", "digest": "sha256:…"}],
  "oracles": [{"name": "policy_denied", "version": "2.1.0"}],
  "pins": {"seed": 7, "model": "…"},
  "environment": ["OPENAI_API_KEY", "AGENTDRILL_HOME"],
  "deps": [{"name": "…", "version": "…"}]
}
```

- **Environment:** names only, never values. `--no-manifest` for privacy-sensitive runs.
- **Determinism:** fixtures (record/replay) + pinned seeds/models; two identical fixture runs score
  identically.
- **Contamination (F30):** cases overlapping a judge/target model's training posture are flagged, not hidden.
- **Tamper evidence:** published results bind to manifest + pack hash; a silent number change is impossible
  without a flagged re-pin note (DD-28).

## Audit log

Append-only, **rotated** (size cap) and **hash-chained** entries; tamper ⇒ fail-closed. Closes the
predecessor's unbounded-flat-file gap (G4).

## Reproducibility test

CI reruns a pinned pack ⇒ identical result unless a pin changed and that change is declared.
