# Release Notes — v0.1.0

**Status:** 🚧 **unreleased** (planned). Published at WBS M24.

## Highlights

- **The proof foundation** — curated, versioned incident-replay attack packs run against the deployed stack,
  gating policy PRs in CI, with reproducible honest results (**misses included**).
- **Kill-time verification** — revocation measured to actual cessation (probed), with a per-stage timeline.
- **Efficacy control** — every `blocked` number backed by an attack that succeeds unguarded.
- **Honest benchmark** — multi-seed, CI'd, trace-linked, coverage heat-map, limitations register.
- **Evasion pack** — the ecosystem attacks itself every release.

## Compatibility

See [compatibility-matrix.md](compatibility-matrix.md).

## Breaking changes

None (first release).

## Known limitations

See [../../reference/known-limitations.md](../../reference/known-limitations.md).

## Verification

Every published number binds to `run-manifest.json`; results verify offline with `agentdrill verify`
([first-run-evidence.md](first-run-evidence.md)).
