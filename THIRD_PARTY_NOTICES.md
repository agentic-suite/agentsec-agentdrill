# Third-Party Notices

agentdrill is licensed under [Apache-2.0](LICENSE). This file records third-party components and the
provenance of absorbed work.

## Absorbed work

agentdrill **absorbs the harness mechanics** of the predecessor eval harness (retired, **retained
privately**, never deleted) — scenario-pack format, adapter contract, runner, deterministic + judge scoring,
fixtures, baselines/comparison, CI exit codes, plugin registry, and sandbox/trust/audit model. Those
mechanics are re-pointed from *agent-quality grading* to *defense proof* (see
[docs/prd/10-feature-parity.md](docs/prd/10-feature-parity.md)).

- **Source:** `agent-eval-forge` (the predecessor eval harness, MIT) —
  <https://github.com/agentic-suite/agent-eval-forge>.
- **Provenance:** imported at WBS **M0** as a single import commit, from source commit
  `8a72f6ad77315a688fb22c32ab7f28f5c4427943` ("Add deprecation notice pointing to successor",
  2026-10-02), on 2026-10-10. Conflicts with agentdrill-owned paths were resolved per ruling D1
  ([docs/plans/m0-port-execution-plan.md](docs/plans/m0-port-execution-plan.md)).
- **License compatibility:** MIT → Apache-2.0 redistribution is permitted with attribution.

> The predecessor repository is retained and made private at M24; no code is deleted. Its name/history is
> documented here for provenance, not as a live dependency.

## Runtime dependencies

Enumerated by the release SBOM (CycloneDX) at M24; recorded here and in `docs/release/`.
