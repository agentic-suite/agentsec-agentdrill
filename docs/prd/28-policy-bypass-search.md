# PRD 28 — Effect-Based Policy Bypass Search

**BLUF:** Enforcement is written against *forms* of an action (`rm -rf /`, a path prefix, a hostname); attackers reach the same **effect** through an enormous equivalence class (`find -delete`, `python -c`, symlink/`..`, encoding, env indirection, tool substitution, multi-step decomposition, transport switch). F17 mutates arguments and F62 probes seams, but no feature claims **coverage over the ways to cause a forbidden effect**. Bypass search turns "does rule R block command C?" into "can *any* catalogued route to effect E succeed under policy P?" — with **minimization** and **auto-regression**.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F89 · **Reqs:** R63

## Why

- ASI02: "*safe tools chained in the wrong order can produce outcomes no single tool allows.*"
- A rule can be green against every listed case and still be trivially bypassable — the policy analogue of fuzzing / property-based testing.
- Fixes are only done when they hold (F61); that requires generating the *next* route, not replaying the last one.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R63** | Bounded, seeded **bypass search** over effect-goal route families, judged by the [PRD 26](26-independent-effect-witness.md) witness, with minimization, family dedup, coverage reporting, and auto-promotion to regression cases. | ≥ 90% route-family coverage per P0 effect (rest `untried`); confirmed bypass → regression within the same release (100%); false-bypass ≤ 2%. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F89** | **Effect-based bypass search**: effect goals (shared with PRD 26) × route-family library (command-equivalence, path-equivalence, encoding, indirection, tool-substitution/overlap, multi-step decomposition, transport-switch, timing/queue) → budgeted seeded search → delta-debugging minimization → family dedup → auto-regression (F61) → per-effect coverage report. | R63 | Extends F17/F62; bounded by catalog + budget (F40 caps apply) |

## CUJs

### CUJ-34 — The bypass and its minimal repro
Policy denies destructive FS ops; search finds `python -c` deletes the canary. **Success:** a 1-line minimal repro and a family name, witness-confirmed.

### CUJ-35 — Coverage, not just a green cell
After a patch, the same search re-runs; the family is now `blocked`; the report shows 2 route families still `untried`. **Success:** coverage is explicit, never implied.

## Success metrics

| Metric | Target |
|---|---|
| Route-family coverage per P0 effect (tried ÷ catalogued) | ≥ 90% (rest `untried`) |
| Effects with a catalogued route-family set | ≥ 12 at v0.2 |
| Minimization ratio (original ÷ minimal reproducer, median) | ≥ 5× |
| Confirmed bypass → regression case within the same release | 100% |
| False-bypass rate (claimed bypass not confirmed by witness) | ≤ 2% |
| Seeded-bypass recall (planted weak rules) | ≥ 95% |
| Search determinism (same seed ⇒ same route sequence) | ≥ 99% |
| CI diff-aware search time on a rule change | ≤ 5 min |

## Dependencies
F17, F38, F61, F36 · [PRD 26](26-independent-effect-witness.md), [PRD 25](25-attacker-strength-and-pressure.md) (budgets), [PRD 35](35-rules-of-engagement-and-safe-fire.md).

## Boundaries & non-goals
- **Dual-use:** route families are documented technique *classes*; no zero-day discovery claims; runs only against the user's own stack under RoE; published outputs are **family names and counts**, not weaponized payloads.
- Bounded by catalog + budget — not unbounded generation (PRD 14).

## Open questions
1. Who curates route families (same review as packs + a "technique steward").
2. Import external fuzzing corpora (shell-obfuscation lists)? (License + dual-use screen.)
