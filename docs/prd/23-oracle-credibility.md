# PRD 23 — Oracle & Judge Credibility (Who Evaluates the Evaluators?)

**BLUF:** Every published number rests on agentdrill's oracles — yet the oracles themselves are software
that drifts, mis-calibrates, and gets gamed. This PRD makes oracle credibility a first-class program:
**versioned oracles**, a **public calibration corpus** with published agreement rates, **judge drift
detection**, and **oracle release notes** — the same honesty applied to our measuring instruments that we
apply to the stacks they measure.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · Features: F79–F84 · Reqs: R53–R58

## Why this is a gap

F29–F55 make the *numbers* trustworthy (seeds, CIs, contamination flags). But none of it matters if the
oracle itself quietly changes what "blocked" means. A benchmark whose scorers drift between releases
without disclosure is contamination at one remove. The 2026 benchmark-trust literature convicts
benchmarks on exactly this: instrumentation changes silently re-baseline results.

## The oracle credibility program

### F79 — Oracle versioning & release notes
- Every oracle (deterministic and judge) is **semver'd and pinned in the run manifest** — oracle
  `name@version` rides with every result, like pack hash and model pin.
- Oracle changes ship with **release notes describing verdict-behavior deltas** ("v2.1 tightens
  `blocked` for partial denials"). An oracle major that changes verdict semantics **invalidates
  comparability** — a re-baseline note publishes with the next release, never silently.
- The comparison engine (F7) treats oracle-version change like adapter/model change (F38): flagged,
  attributed, never mistaken for a defense regression.

### F80 — Public calibration corpus
- A published, versioned **labeled corpus** of (case, evidence, expected-verdict) triples — drawn from
  real runs, redacted per F65 — used to measure oracle health.
- **Published per release**: per-oracle **agreement rate, false-block rate, false-miss rate** against the
  corpus, with CIs (F55 discipline).
- Third parties can run *their* oracle implementation against our corpus and compare — the same
  reproduction posture as the benchmark itself (CUJ-3).

### F81 — Judge drift detection
- The LLM-judge layer is the softest instrument: model updates, prompt drift, and provider changes all
  move it. Measures:
  - **Judge agreement tracking**: judge-vs-deterministic and judge-vs-human-verdict (HITL queue, F44)
    agreement rates, tracked **per release** in the trend store (F23).
  - **Canary cases**: a fixed set of seeded judge-canary cases runs every cycle; a canary flip without a
    judge/model pin change = **`judge_drift` finding**, release-blocking.
  - Judge prompts and temperature are **hashed into the manifest** — a prompt edit is a pin change.

### F82 — Oracle meta-evaluation in CI
- The drill-the-drill suite (F43) gains a **calibration battery**: known-answer cases (blocked, missed,
  degraded, inert, seam) must verdict correctly across oracle versions; a regression in oracle
  behavior fails CI **before** it can pollute a release.

### F83 — Human-verdict adjudication layer
- Every HITL review verdict (F44) is stored as **labeled data**: (case, evidence, oracle verdict, human
  verdict, rationale). Feeds: calibration corpus growth (F80), judge agreement tracking (F81), and
  future deterministic-oracle promotion (the gray-area-shrinking loop, CUJ-17, made explicit and
  measured).
- Published stat: **human-adjudication coverage** — what fraction of judge-divergent outcomes got human
  eyes this release. A release with zero adjudication of divergences says so (limitations register, F34).

### F84 — Oracle honesty labels
- Each oracle carries a declared **calibration tier** — `calibrated` (measured vs. corpus), `reviewed`
  (human-validated, no corpus yet), `experimental` (neither) — rendered on every result that used it.
- `experimental` oracles **cannot gate CI** (advisory only) and cannot appear in BenchmarkReleases
  without the label visible. Same posture as target attestation (F63): the weakest instrument labels
  the run.

## CUJs

### CUJ-25 — Check the instrument before trusting the reading (P2/public)
1. Ravi (or a reviewer) opens the oracle credibility page for a release: per-oracle agreement rates,
   false-block/miss rates, judge drift status, calibration tier.
2. **Success:** every oracle behind every published number shows its calibration status and version —
   and a drifted judge is caught by the canary, not by a wrong published number.

### CUJ-26 — Run my oracle against your corpus (P5/researcher)
1. A researcher points their own oracle implementation at the published calibration corpus.
2. **Success:** they get their agreement rates against our labels, offline, comparable to our published
   numbers — the corpus is a submission surface for better oracles (feeds R11 community flow).

## Traceability

| Req | Feature | Test |
|---|---|---|
| R53 Oracle versioning | F79 | Manifest carries oracle@version; comparison flags version change |
| R54 Calibration corpus | F80 | Per-release agreement rates published with CIs |
| R55 Judge drift | F81 | Canary flip without pin change = release-blocking `judge_drift` |
| R56 Oracle CI battery | F82 | Calibration battery green before release |
| R57 Adjudication layer | F83 | Divergence→verdict stored; coverage stat published |
| R58 Honesty labels | F84 | `experimental` oracle cannot gate CI (enforced) |

## Sequencing

- All features F79-F84 land in **v0.1.0** (this release): the credibility floor ships before the first externally disputed finding can arrive; F80/F83 seed from the first HITL reviews of this release.