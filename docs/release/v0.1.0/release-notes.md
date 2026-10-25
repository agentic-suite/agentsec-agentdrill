# Release Notes — v0.1.0

**Status:** ✅ **v0.1.0 — release notes** (finalized at M32; the tag is cut at 32.8). Written against the built
system (M0–M31).

## Highlights

- **The proof foundation** — curated, versioned incident-replay attack packs run against the deployed stack,
  gating policy PRs in CI, with reproducible honest results (**misses included**).
- **Kill-time verification** — revocation measured to actual cessation (probed), with a per-stage timeline.
- **Efficacy control** — every `blocked` number backed by an attack that succeeds unguarded.
- **Honest benchmark** — multi-seed, CI'd, trace-linked, coverage heat-map, limitations register.
- **Evasion pack** — the ecosystem attacks itself every release.
- **World-class additions** — independent effect witness; attacker-strength pressure curves (`Hold@k`/`ASR@k`);
  effect-based bypass search; bring-your-own-defense + neutral head-to-head; ecosystem integrations
  (SARIF/OTel/OCSF/OSCAL/STIX); trace backtest/shadow; attack-path graph; incident-to-pack compiler; exposure
  ledger + time-boxed waivers; signed drill attestations; rules of engagement; extension detonation;
  Break-It program; frontier attack classes; trace explorer; platform compatibility matrix (L0–L4); standards/claims.

## Install

```sh
pip install agentsec-agentdrill==0.1.0
agentdrill quickstart
```

PyPI: <https://pypi.org/project/agentsec-agentdrill/>. Verify the download (hash + SBOM + signed provenance):
[release-evidence.md](release-evidence.md).

## Compatibility

See [compatibility-matrix.md](compatibility-matrix.md) (graded L0–L4; the published headline is AWC) and the
[compliance matrix](compliance-matrix.md) (OWASP ASI + ATLAS + NIST + EU + OpenSSF, gaps stated).

## Field-tested

The v0.1.0 field test ran **every CUJ-1..CUJ-63** end to end against the bundled demo stack and the
system-under-test container: **73 PASS · 0 FAIL · 0 declared** (73/73), every PASS grounded, with real LLM
request/response pairs captured for both pinned models. Track B drove **19 agents across 8 frameworks**
(19/19 green) and cross-OS parity measured **100 % over 176 deterministic outcomes** (macOS arm64 vs Linux
aarch64). Full evidence: [FIELD_TEST_REPORT.md](../../field-test/v0.1.0/FIELD_TEST_REPORT.md).

## Breaking changes

None (first release).

## Known limitations

See [../../reference/known-limitations.md](../../reference/known-limitations.md).

## Verification

Every published number binds to `run-manifest.json`; results verify offline with `agentdrill verify`
([first-run-evidence.md](first-run-evidence.md)).
