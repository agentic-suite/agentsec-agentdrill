# Roadmap

**Status:** design intent. v0.1.0 is the first release; milestones live in the
[WBS](docs/wbs/v0.1.0/wbs-v0.1.0-index.md).

## v0.1.0 — the proof foundation

The whole PRD is v0.1.0. Headline capabilities:

- Curated, versioned **incident-replay attack packs** run against the **deployed stack** in CI.
- **Reproducible, honest results** — misses included; multi-seed, CI'd, trace-linked.
- **Kill-time verification** — revocation measured to actual cessation.
- **Efficacy control** — every `blocked` number backed by an unguarded success.
- **Evasion pack** — the ecosystem attacks itself every release.
- The trust layer, BAS-class detection validation, chains + bounded adaptive orchestration, the pack
  registry, interop + standards, and the lifecycle features (intake, fix-validation, seams, attestation,
  verifier, quickstart).

## Beyond v0.1.0 (directions, not commitments)

- Enterprise/platform coverage via standards; A2A attack packs as the spec stabilizes.
- Richer competitor-benchmark automation (starts as PR submissions).
- Deferred decisions: re-pin cadence (DD-33), dual-use boundary (DD-34).

See [maintenance backlog](docs/maintenance-backlog.md) for the full deferred list.

## Ecosystem

Part of the [agentsec-ecosystem](https://github.com/agentsec-ecosystem) Wave 0 (*stop it*): agentwatch,
agentpolicy, agentkeys, agenthalt, agentdrill ship together as one install. agentdrill is the **proof
layer** — it needs targets and grows with them.
