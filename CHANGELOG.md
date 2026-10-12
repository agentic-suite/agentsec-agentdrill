# Changelog

All notable changes to this project are documented here, in the spirit of
[Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **M0** — ported the predecessor eval harness (`agent-eval-forge`, MIT) as a single import commit:
  `src/` (package `evalforge`), `tests/`, `scenarios/`, `schemas/`, `examples/`, `field/`, tooling, and
  the non-colliding docs subset. Source commit
  `8a72f6ad77315a688fb22c32ab7f28f5c4427943`. Provenance in
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); namespace rename + packaging adaptation follow.

### Added (design)
- Requirements + design for **v0.1.0** — the proof engine: attack packs, runner, driver/target adapters,
  oracle engine, evidence, honest benchmark, kill-chain verification, efficacy control.
- The trust layer: statistical rigor, contamination disclosure, adjudication, dark holdout, signed provenance.
- Pack catalog (incident-replay, security, evasion, meta-verification, kill-chain, quickstart) + roadmap classes.
- World-class additions (PRDs 25–43): independent effect witness, attacker-strength pressure curves
  (`Hold@k`), effect-based bypass search, bring-your-own-defense + neutral head-to-head, ecosystem
  integrations, trace backtest/shadow, attack-path graph, incident-to-pack compiler, exposure ledger +
  waivers, drill attestations, rules of engagement, extension detonation, Break-It program, frontier attack
  classes, trace explorer, platform compatibility matrix (L0–L4), standards/claims, and the evidence register.
- `docs/wbs/v0.1.0/` — 33 milestones (M0–M32) across 17 detail files.
- `docs/design/`, `docs/plans/`, `docs/reference/`, `docs/adr/`, `docs/architecture/`, `docs/runbooks/`,
  `docs/tutorials/`, `docs/guides/`, `docs/compliance/`, `docs/release/`, `schema/pack.schema.json`.

> Build work (M0–M32) lands as it is implemented; this file is updated per release (M32 tags `v0.1.0`).
