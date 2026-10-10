# PRD 07 — Success Metrics

**BLUF:** agentdrill succeeds when a **third party reproduces our published numbers** and when **CI rejects
a policy PR** because a drill caught a regression the author didn't. The headline metric is not a detection
rate — it is **reproduction** and **honesty**: misses published within a week, external submissions to the
benchmark, community packs reviewed like code.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## Outcome metrics

| Metric | Target | Why it is the right metric |
|---|---|---|
| Third-party reproduction | **≥1 verified external run per release** | The success bar (R4): our numbers are only credible if someone else gets them |
| Misses surfaced → public | **within 7 days** | The radical-transparency loop: the honest table updates fast |
| **Disputed findings resolved** | **within 14 days** (public SLA) | Trust = disputes get answered, not ignored (F32) |
| Community pack contributions | grow per release | Health of the pack ecosystem (R11) |
| External tools submitting to the benchmark | ≥1 by v1.x | The convention-winning signal (standards-authorship moat) |
| Pack pass in CI gate | regression PRs rejected | R3 dogfooding: the ecosystem's own policies are gated |
| Kill-time published | every release, **p50/p95/max over repeated trials** | R8: latency is a first-class result — and means hide tails |
| Evasion pack cadence | every release cycle | R7: we red-team ourselves continuously |
| **Every published number** | **mean ± std over ≥3 pinned seeds** | F29: a single run is never a claim |

## Release gate (v0.1.0)

A release is not "done" unless:

1. Every shipped pack reproduces its named incident pattern (R1).
2. All packs run against the deployed stack end-to-end (R2).
3. The CI gate demonstrably rejects an un-blocking policy change (R3).
4. Results + `run-manifest.json` are published so a third party can reproduce (R4, R6).
5. The published report includes the **misses** (R5) **and the limitations register (F34)**.
6. Every published number is **multi-seed (mean ± std)**, judge metrics carry CIs, kill-time carries
   p50/p95/max (F29).
7. Contaminated cases are **flagged**, not hidden (F30).
8. The evasion pack ran this cycle **including the dark holdout**, and its result is published (R7, F33).
9. Kill-time numbers are published (R8).
10. Compatibility table (harness × version) is published.
11. All published artifacts are **signed** with provenance (F35).

## Anti-metrics (what we refuse to optimize)

- **"Detection rate" as a marketing number** — no injection-detection claims from drill results.
- **Green-by-construction runs** — a result with **zero misses** is suspicious, not a win.
- **Scoring theater** — no composite "security score" that hides misses in an average.
- **Coverage inflation** — we do not add packs we cannot faithfully reproduce.
- **Benchmark vanity** — we do not rank models; we prove defenses against documented attacks.

## Instrumentation of success

- Reproduction attempts (external) are tracked as first-class issues and reported on the public table.
- Every published number links its `run-manifest.json` + pack hash.
- The compatibility table is regenerated from CI, not hand-edited.
