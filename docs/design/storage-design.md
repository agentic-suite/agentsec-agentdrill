# Storage & Determinism — Design

**BLUF:** Local-first JSON under `.agentdrill/` (DD-19), with a **run manifest** that makes a run
reproducible and tamper-evident: pinned inputs + environment (names, never values) + pack hash + oracle
versions. Same environment ⇒ same result (R6).

> **Status:** normative (M8). Implementation: `agentdrill/fixtures/driver_fixture.py` (record/replay),
> `agentdrill/models/manifest.py` (`RunManifest` + `build_run_manifest`),
> `agentdrill/determinism/pins.py` (pins + re-pin rule), `agentdrill/determinism/contamination.py` (F30),
> `agentdrill/determinism/reproduction.py` (reproduction check). Oracle decision rules:
> [determinism-methodology](../reference/determinism-methodology.md).

## Layout

```
.agentdrill/
  packs/            # resolved/imported packs
  runs/<run_id>/    # run.json, run-manifest.json, recon.json, artifacts/<case_id>.json
  goldens/          # golden expected results per pack version
  comparisons/      # candidate vs. golden/baseline diffs
  benchmarks/       # published BenchmarkRelease tables
  audit/            # append-only, rotated, hash-chained log
  witness/          # per-case witness records + hash chain (M23)
  lab/              # pinned adversary-lab definitions (M23)
  bypass/           # confirmed bypass families + minimized reproducers (M24)
  waivers/          # signed time-boxed waivers (M28)
  attestations/     # signed drill attestations (M28)
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
  "pins": {"seed": 7, "model": "…", "semconv": "1.41.0"},
  "attacker": {"tier": "T1", "k": 5, "mutation_path": null},
  "witness": {"live": true, "version": "0.1.0", "coverage": 0.93},
  "lab": {"version": "0.3.0"},
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
