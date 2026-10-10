# PRD 11 — Decisions

**BLUF:** Accepted decisions for v0.1.0: **Apache-2.0**, Python core with a CLI wrapper, YAML attack packs,
**reuse the agentwatch security-event schema** as the machine-readable result surface, **no injection-detection
claims**, pinned+published determinism, MITRE ATLAS + OWASP tagging, **import don't reinvent**, and the hard
architectural rule that **agentdrill owns no enforcement**.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## Design & architecture

| # | Decision | Rationale |
|---|---|---|
| **DD-01** | **agentdrill owns no enforcement** — it drives the deployed stack and reads evidence | A drill that enforces would test itself, not the user's stack (PRD 02) |
| **DD-02** | **Targets are the deployed stack**, not a simulation | R2; results must reflect the real enforcement path |
| **DD-03** | **No ground-truth leakage** — oracles/expected outcomes never sent to the driver | A drill you can read the answer to is not a drill (absorbed from the predecessor harness) |
| **DD-04** | **Deterministic oracles first, LLM judge only where needed** | Cheap, reproducible, offline-safe; judge divergences flagged, not averaged (absorbed) |
| **DD-05** | **Reuse the agentwatch record + security-event schema** for machine-readable results | Single source of truth across the ecosystem; drills flow into analytics/compliance |
| **DD-06** | **Honest reporting is mandatory** — a run cannot publish without its misses | The differentiator; enforced by R5 |
| **DD-07** | **Two-layer oracle discipline** (deterministic vs judge fail differently) | Borrowed from the predecessor's JPS-validated model |
| **DD-08** | **Harness-agnostic or explicitly harness-compatible**; per-harness packs where needed | Ecosystem non-negotiable; a harness is compatible only when its pack passes in CI |
| **DD-09** | **Custom oracles/adapters via a plugin registry** (entry points), validated at load | Extensibility without forking (absorbed) |
| **DD-10** | **Adversarial self-test is shipped, not optional** (evasion pack) | Own-threat-model operationalized (R7) |

## Scope

| # | Decision | Rationale |
|---|---|---|
| **DD-11** | **v0.1.0 = Wave 0**: incident-replay packs + CI gate + honest benchmark + kill-time + evasion pack | Matches the release-roadmap meta-MVP |
| **DD-12** | **Replay documented incidents only** — no novel model-attacking capability | Dual-use boundary (R9/PRD 08/PRD 14) |
| **DD-13** | **No injection-detection claims** from drill results | We measure controls (PRD 14) |
| **DD-14** | **Import interop (promptfoo/garak/AgentDojo/PyRIT) is P1, not P0** | Reuse the community's suites, don't block v0.1.0 on it |

## Technical

| # | Decision | Rationale |
|---|---|---|
| **DD-15** | **Python core** (library + CLI wrapper + pytest plugin), shared runner/oracle/adapter engine | Parity with the predecessor harness; one engine, three surfaces |
| **DD-16** | **YAML attack packs** (JSON secondary) | Authoring ergonomics; absorbed pack format |
| **DD-17** | **`pip install agentsec-agentdrill`**, CLI `agentdrill`, package `agentdrill` on PyPI | Ecosystem naming convention |
| **DD-18** | **Pinned seeds/models + `run-manifest.json`**; re-pin ⇒ re-publish | R6; reproducibility is the success bar |
| **DD-19** | **Local JSON artifacts under `.agentdrill/`** (runs, packs, baselines/comparisons, audit) | Local-first; sibling to the predecessor's the predecessor store |
| **DD-20** | **Sandbox + trust levels + audit + secret sanitization** for untrusted packs | Community packs are executable (PRD 06) |
| **DD-21** | **MITRE ATLAS + OWASP tagging on every pack/attack** | R10; standards posture |
| **DD-22** | **Apache-2.0 license** | Ecosystem standard; matches repo LICENSE |

## Governance

| # | Decision | Rationale |
|---|---|---|
| **DD-23** | **Packs reviewed like code** (community flow) | Packs are executable security claims |
| **DD-24** | **Public methodology or nothing** — no proprietary scoring | Non-requirement; trust |
| **DD-25** | **Signed packs + provenance** on release (governance floor) | Supply-chain trust; own-threat-model |
| **DD-26** | Each release ships **notes + compatibility table + security audit + published benchmark** | Org governance floor + R4/R5 |
| **DD-27** | **A single run is never a claim** — published numbers are mean ± std over ≥3 pinned seeds; judge metrics carry CIs; kill-time carries p50/p95/max | Benchmark-trust posture (F29); anti-"three numbers to lie" |
| **DD-28** | **Flag, never silently fix** — preregistered golden outcomes; result changes are *flagged* with a re-pin note, not quietly edited | Trust posture (F31); dispute SLA (F32) |
| **DD-29** | **Dark holdout** — each pack keeps an unpublished holdout subset in CI to catch pack-gaming | HLE dark-benchmark pattern (F33) |
| **DD-30** | **Contamination is disclosed, not hidden** — flagged cases stay visible in the table with their status | SWE-Bench lesson (F30) |
| **DD-31** | **Limitations register ships with every release** — the honest "what this does NOT test" list | agentwatch discipline (F34) |
| **DD-32** | **Signed provenance on published artifacts** — Sigstore signatures + provenance on packs, manifests, results | Supply-chain trust (F35) |
