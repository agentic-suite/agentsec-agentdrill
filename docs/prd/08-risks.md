# PRD 08 — Risks

**BLUF:** agentdrill's credibility *is* the product, so its top risks are the ones that would fake or
degrade credibility: **model/seed drift** quietly changing results, crossing the **dual-use line** in what
we publish, and non-determinism in CI. Second tier: harness/config churn, target sprawl, and scope creep
into a red-team arsenal. Each has a trigger and a mitigation.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Risk register

| # | Risk | Likelihood | Impact | Trigger | Mitigation |
|---|---|---|---|---|---|
| **RK-1** | **Pinned-model drift/death** silently changes numbers | High | High | A pinned model is deprecated or changes behavior | Re-pin + **re-publish** with a manifest note; never silently change a number; packs prefer deterministic oracles over model-dependent ones |
| **RK-2** | **Dual-use boundary** crossed — packs become an attack arsenal | Medium | High | A pack teaches novel exploitation rather than replaying a documented pattern | Packs replay **documented** incidents only; publish the boundary; review contributions like code; no novel model-attacking capability (R9/PRD 14) |
| **RK-3** | **Non-determinism** makes the CI gate flaky | Medium | High | A gate passes/fails on re-run with no code change | Deterministic oracles first; fixtures/ToolStub record-replay; `run-manifest.json`; treat flakiness as a bug |
| **RK-4** | **Harness/config churn** — targets move under us | Medium | Medium | Claude Code / Cursor / MCP config surfaces change | Per-harness packs versioned; harness watchlist; drift alerts (ecosystem policyweave watchlist) |
| **RK-5** | **Target sprawl** — too many deployed-stack targets to maintain | Medium | Medium | Each enforcer needs its own adapter | v0.1.0 targets the Wave-0 stack only; community adapters for the rest |
| **RK-6** | **Credibility** — we ship a "green" result that is wrong | Medium | High | A drill exercises a mock or a stale config | CUJ-1 acceptance forbids mock-only greens; evidence (agentwatch) required per result; reproduction gate (R4) |
| **RK-7** | **Scope creep** into enforcement/observability | Medium | Medium | A PR adds enforcement "to make the drill work" | Architecture rule: agentdrill owns no enforcement (PRD 02); non-goals (PRD 14) |
| **RK-8** | **Untrusted packs** execute malicious code | Low | High | A community pack is hostile | Trust levels + sandbox + OS isolation + audit (PRD 06) |
| **RK-9** | **Reproduction fails** on a third party's machine | Medium | High | Missing pin/manifest or undocumented methodology | Publish manifests + methodology; CUJ-3 is the acceptance test |
| **RK-10** | **Benchmark contamination** — pack content ingested into judge/target training data inflates results | High | High | A pinned model's training corpus absorbed a documented incident | F30 contamination probes; flag contaminated cases; dark holdout (F33) detects gaming; prefer live-stack evidence over model-memory (F29/F31 discipline) |
| **RK-11** | **Pack-gaming** — defenses overfit the published pack set | Medium | High | Published-set green but holdout red | F33 dark holdout runs in CI every cycle; holdout failure = release-blocking finding |
| **RK-12** | **Cherry-picked reporting** — a disputed finding is quietly dropped | Medium | High | A published miss embarrasses a downstream tool | F32 public dispute process + 14-day SLA (PRD 07); golden-lock rule (F31): changes are flagged, never silent |
| **RK-13** | **Adaptive orchestration escapes the dual-use boundary** — target-response-driven mutation drifts into novel attack generation | Medium | High | An `adaptive` case succeeds where no documented pattern exists | F40 hard caps: mutation-of-documented-patterns only, per-case provenance (`parent_pattern`), review required for any adaptive case entering a shipped pack; PRD 14 non-goal stands |
| **RK-14** | **Oracle gaming** — a target/harness learns to satisfy the scorer without actually blocking (bluff the judge, forge evidence shape) | Medium | High | Published-set green + meta-verification red | F43 drill-the-drill suite in CI every cycle; evidence binding (agentwatch refs) required per result; divergence gating |
| **RK-15** | **Attribution wrong** — the flagged config diff is correlation, not cause | Medium | Medium | Two changes land in one release window | F38 reports `attributed_to` with confidence + the mechanism (stage timing), not a bare diff; CI can bisect by re-running against intermediate configs |
| **RK-16** | **Registry poisoning** — a malicious/typo-squatted community pack enters the registry | Low | High | Supply-chain attack via the pack index | F39: signed packs, verified publishers, deprecation + takedown process, trust levels enforced at install |

## Hard parts

1. **Determinism across a live stack.** Enforcement paths are stateful; making a drill repeatable requires
   fixtures, pinned seeds, and careful isolation.
2. **Faithful incident replay.** A pack must reproduce a *documented* pattern, not a strawman — hard to get
   right and easy to fake.
3. **Honest reporting under commercial pressure.** Publishing misses is the differentiator and the hardest
   discipline to keep.
4. **Kill-time measurement.** Measuring real cessation (not reported success) is subtle.
5. **Staying trustworthy as a benchmark.** Contamination, pack-gaming, and silent updates are how real
   benchmarks (SWE-Bench Verified) lost reporting credibility — the trust layer (F29–F35) is
   release-blocking, not aspirational.

## Triggers to revisit

- A pinned model dies → RK-1 re-pin cadence review.
- A published number is disputed → CUJ-3 reproduction escalation.
- A contribution pushes the dual-use line → RK-2 boundary review.
- Gate flakiness in the ecosystem's own CI → RK-3 escalation to a release-blocking bug.

## Open questions

- **Re-pin cadence:** what schedule keeps packs meaningful across model updates without rewriting results
  every month?
- **Dual-use line:** how much red-team capability is safe to publish? Where exactly is the boundary
  between "replay a documented pattern" and "teach a new exploit"?
- **Target matrix:** how many deployed-stack targets can v0.1.0 bind before it is unmaintainable?
- **Competitor benchmark (R12):** what is the ethical + legal shape of publishing other tools' honest
  coverage?
