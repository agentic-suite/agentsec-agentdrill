# ADR-0014 — Graded platform compatibility (L0–L4) with a reference-harness policy

- **Status:** proposed (2026-10-10)
- **Context:** "Compatible only when its pack passes in CI" is binary and depth-less; one "Cursor ✓" can
  mean config-lint or full drive. Harnesses release weekly, so a level claim rots without an SLA. Third-party
  reproduction (the project's success bar) requires the reproducer to *have* the harness.
- **Decision:** Adopt a graded scale — **L0 listed · L1 config-aware · L2 driven · L3 observed (witnessed) ·
  L4 gated (contract pack in CI)** — with per-surface rows, a transparent prioritization model, a
  version-follow SLA (matrix ≤7 d; L4 ≤72 h; nightly driver canary), and one published number
  (**adoption-weighted coverage**). **Reference-harness policy:** ≥2 open-source harnesses always at L3+;
  headline benchmark tables use open harnesses; proprietary results appear in a separate table
  ([PRD 41](../prd/41-platform-compatibility.md)).
- **Consequences:** auditable, reproducible claims; more maintenance (drivers, canary); a harness's own
  built-in defenses are treated as part of the target and results label "defaults vs. auto-approve".
