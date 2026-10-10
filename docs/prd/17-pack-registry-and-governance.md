# PRD 17 — Pack Registry, Signing & Contribution Governance

**BLUF:** Packs are **executable security claims**, so the registry treats them like signed, semver'd,
reviewed packages: verified publishers, signatures, changelogs, deprecation + takedown, and a
reviewed-like-code contribution flow. Local-first; the public index is a publishable artifact, not a
service you must trust.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · Features: F39, R11

## Registry model

| Aspect | Decision |
|---|---|
| Unit | `pack@semver` — semver with a documented compatibility policy (pack-format majors track agentdrill majors) |
| Identity | Verified publisher (Sigstore signing key bound to a GitHub/Org identity) |
| Index | A signed, content-addressed manifest (`registry.json`) — mirroring + offline verification; no mandatory central service |
| Trust levels | `built-in` (shipped, signed by the project) · `community` (reviewed, signed by publisher) · `external` (unreviewed — sandbox-only, never in the benchmark) |
| Deprecation | Explicit, with migration notes; a deprecated pack keeps running but is flagged in results and excluded from new benchmark releases |
| Takedown | Security-motivated takedown removes the *index entry*; the signature chain records the removal (no silent disappearance) |

## Contribution flow (reviewed like code)

1. **Scaffold** — `agentdrill init` (pack scaffold + lint config + CI workflow).
2. **Lint** — `agentdrill pack lint`: schema, ID path-safety, required tags (ATLAS/OWASP), incident
   reference, oracle coverage, fixture presence, methodology note.
3. **Validate** — independent-reviewer authorship encouraged for adversarial validation (the JPS pattern);
   at least one reviewer who did not author the pack.
4. **Sign & publish** — `agentdrill pack publish` (signs `pack@version` + provenance).
5. **Verify (consumer side)** — `agentdrill pack verify` checks signature, publisher, hash, and trust level
   before install; `external` packs are sandbox-restricted at run time.

## Review criteria (what a reviewer checks)

- **Fidelity:** does the case faithfully replay the referenced incident (source cited)?
- **Oracle correctness:** does `expect` state the right defensive outcome, and is the oracle deterministic
  where it can be?
- **Dual-use boundary:** mutation/adaptivity within caps; no novel capability; no live third-party
  infrastructure as target.
- **Determinism:** fixtures or pinned live responses; seeds declared.
- **Honesty:** no case designed to always-pass; expected outcomes preregistered.

## Anti-goals

- No auto-acceptance ("pack CI green ⇒ listed") — review is human, CI is the floor.
- No un-reviewed pack ever enters a **BenchmarkRelease** (R4 tables cite `built-in`/`community` only).
- No silent updates: a pack's published numbers are bound to `pack@version` + hash.
