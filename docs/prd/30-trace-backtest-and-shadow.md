# PRD 30 — Trace Backtest & Shadow Mode

**BLUF:** Teams will not enable blocking until they know **what it breaks**. Mature controls all have this: SIEM retro-hunt, WAF/IPS monitor-only mode, policy-engine decision-log replay. agentdrill adds **backtest** (replay recorded agentwatch sessions against a candidate policy offline), **shadow mode** (candidate runs log-only alongside the enforced one), a **false-block budget** measured on real traffic, and **trace → drill** promotion (a real suspicious session becomes a redacted case + mined benign twins, with human review).

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F92 · **Reqs:** R66

## Why

- F51 measures utility with **synthetic** benign twins; F21 does a what-if only for *a confirmed miss*. Neither answers "what happens to my last 30 days of *real* work if I ship this rule?"
- Without that answer, strong policies live in warn-only forever or get rolled back after the first outage — the exact path to a **disabled CI gate** (see [PRD 33](33-exposure-ledger-and-waivers.md)).
- Real traces are the best source of realistic benign twins and of real suspicious sessions to promote into drills (agentwatch already records them).

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R66** | Backtest candidate defenses against recorded sessions with **replay-fidelity disclosure**; **shadow mode** runs side-effect-free in log-only; a **false-block budget** is measured with a CI; **trace→drill** promotion is redacted and human-reviewed. | Replay decision fidelity ≥ 99% on unchanged policy; 100% of backtests report false-block rate with CI; zero unredacted secrets in derived cases. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F92** | **Trace backtest & shadow mode**: offline replay of redacted sessions vs. candidate policy (newly-blocked benign clusters, regressions, unchanged, un-replayable itemized); log-only shadow with divergence rate; false-block budget gate; trace→case + mined benign twins (HITL-reviewed, `origin: production-trace`); privacy via F65 with verified receipts. | R66 | Consumes agentwatch records, F44, F51, F65; proves side-effect-free via [PRD 26](26-independent-effect-witness.md) |

## CUJs

### CUJ-38 — Don't ship the outage
A new egress rule is backtested on 30 days of traffic → 3 clusters of newly-blocked benign calls (package mirror, internal wiki, CI artifact store) → fixed before enabling. **Success:** clusters shown; false-block rate with CI.

### CUJ-39 — Shadow, then promote
Candidate shadowed for 7 days; divergence 0.3% CI [0.2, 0.4]. **Success:** promote with evidence; candidate never affected execution.

## Success metrics

| Metric | Target |
|---|---|
| Backtest coverage (replayable ÷ available sessions) | ≥ 85%; remainder itemized |
| Replay decision fidelity vs. recorded (unchanged policy) | ≥ 99% |
| Backtests reporting false-block rate with CI | 100% |
| Clusters needed to explain 90% of newly-blocked benign calls | ≤ 20 |
| Backtest runtime on 30 days × 1M calls | ≤ 30 min (laptop-class) |
| Shadow-mode divergence overhead on production latency | ≤ 5 ms p95 |
| Trace→case lead time (median) | ≤ 1 day |
| Unredacted secrets/PII in derived cases (scanner-verified) | **0** |
| Enforcing policies shipped with a declared false-block budget | ≥ 90% |

## Dependencies
agentwatch records, F21, F44, F51, F65 · [PRD 26](26-independent-effect-witness.md), [PRD 33](33-exposure-ledger-and-waivers.md).

## Boundaries & non-goals
- Replay is a model of reality; non-deterministic/stateful tools reduce fidelity — always disclosed.
- Shadow mode must be **provably side-effect-free**. Not a SIEM; not a data lake.

## Open questions
1. Minimum trace schema required from third-party harnesses (OTel GenAI spans may suffice).
2. Replay scope: enforcement decisions vs. LLM-driven decisions (recommend: enforcement decisions).
