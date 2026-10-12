# PRD 25 — Attacker Strength & Pressure Curves

**BLUF:** A published `blocked` is meaningless without saying **against whom** and **how hard they tried**. agentdrill labels every number with an **attacker-capability tier** (T0 static → T1 repeated → T2 documented-pattern mutation → T3 adaptive search) and reports **`Hold@k`** (held on *all k* trials), **`ASR@k`** with confidence intervals, and **pressure curves** — so a defense that holds against a fixed pack is never silently presented as *robust*. Closes the largest credibility gap versus the 2025–26 research record.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F85, F86 · **Reqs:** R59, R60

## Why

- 12 recent defenses reported near-zero attack success; adaptive attackers (gradient, RL, search, human-guided) reached **>90%** against most (Nasr/Carlini/Tramèr et al., arXiv 2510.09023).
- CAISI: attacks tailored to a target raised hijack ASR **11% → 81%**; **25 repeated attempts** raised average ASR **57% → 80%**.
- Gray Swan × UK AISI/CAISI: nearly all agents violated policy within **10–100 queries**; **every** frontier model had at least one successful attack.
- τ-bench `pass^k`: reliability is **all-of-k**. For a defender, the attacker tries many times; the defender must hold every time.

Existing PRD coverage (F29 multi-seed, F40 bounded adaptive, F55 bootstrap CIs) makes numbers *trustworthy* but does not make the **attacker-effort dimension** explicit. A skeptical reader currently cannot tell "blocked a fixed string" from "resisted an optimizer for 40 queries."

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R59** | Every case/result carries an **attacker-strength tier** (T0–T3) and the effort parameters (k, mutation budget, query budget). | No published cell lacks a tier + k; a schema check fails the run otherwise. |
| **R60** | **`Hold@k`** (all-of-k) and **`ASR@k`** (any-of-k, with CI) are first-class per-case and per-defense-class metrics; a **pressure curve** is produced for tiered cases. | Report renders `Hold@k`, `ASR@k` + CI, first-break distribution, and a curve; a bare percentage is not renderable. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F85** | **Attacker-capability tiers** — T0 static replay · T1 repeated attempts (k ∈ {1,5,10,25}, seeded) · T2 documented-pattern mutation (within the F40 caps; mutation path recorded in the manifest) · T3 adaptive search against *this* stack (local-only, RoE-gated, **artifacts never published**) | R59 | Extends F40 (mutation) and F29 (seeding); adds the *label* dimension |
| **F86** | **Pressure metrics & curves** — `Hold@k`, `ASR@k` + bootstrap CI (F55), time/queries-to-first-break (p50/p95), attacker cost-to-break; auto-generated **claim-scope statement** ("held 25/25 at T1; not evaluated at T2/T3") | R60 | Per-case scalars only; **no composite security score** (PRD 14) |

### Rules
1. **No bare `blocked %`** in any published table: tier + k + CI mandatory (extends F55).
2. CI may gate on **`Hold@k`** for critical must-block cases (k policy-configurable; default 5 on PR, 25 nightly).
3. T3 results never enter **golden-locked comparisons** (consistent with F40) and never publish payloads.
4. A defense strong at T0 but weak at T2/T3 is surfaced as **`brittle`** — a finding, not a footnote.

### The T3 decision (recorded)
T3 (adaptive search) is **deferred for v0.1.0** and, when introduced, is bound by [PRD 35](35-rules-of-engagement-and-safe-fire.md) (RoE), runs **local-only**, and publishes aggregates + bypass-family counts only — never payloads. This preserves the PRD 14 non-goal ("no unbounded attack generation") while acknowledging that static replay alone understates risk. v0.1.0 ships **T0–T2**.

## CUJs

### CUJ-28 — Gate on "did it hold every time?"
A contributor changes a policy rule; CI runs critical must-block cases at **T1, k=5**. A case that passed once but failed on trial 3 of 5 fails the gate with the pressure curve attached. **Success:** `Hold@5 < 100%` blocks the PR and names the failing trial.

### CUJ-29 — Read an honest public number
An external reader sees "*Defense X — T0 100% [97,100]; T1 Hold@25 96%; T2 ASR@25 31%*" and the claim-scope statement. **Success:** the reader cannot mistake the result for "robust."

## Success metrics

| Metric | Target |
|---|---|
| Published cells with tier + k + CI | **100%** |
| Critical must-block cases with `Hold@25` computed (deterministic controls) | ≥ 95% |
| Deterministic enforcement controls: `Hold@25` on T0 critical | **100%** (else a finding) |
| Model/judge-based controls: reported as `ASR@k` + CI, not gated at 100% | 100% |
| T1/T2 reproducibility (same seed ⇒ same outcome) | ≥ 99% case-level |
| T2 mutation path stored in manifest | 100% |
| `brittle` findings surfaced when T0-hold/T2-break | 100% |
| T3 payload leakage in published artifacts | **0** |
| CI overhead of T1 gate (k=5) on the smoke subset | ≤ +50% wall time vs. T0 |

## Dependencies
F29, F40, F55, [PRD 26](26-independent-effect-witness.md) (success judgment), [PRD 28](28-policy-bypass-search.md) (deterministic bypass search), [PRD 35](35-rules-of-engagement-and-safe-fire.md) (RoE for T3).

## Boundaries & non-goals
- No composite security score. `Hold@k`/`ASR@k` are per-case; any aggregate is per *declared class*, with CIs, never a single headline number.
- Repeated trials of a **deterministic** control measure *route coverage*, not stochastic variance — stated in the report (route coverage is [PRD 28](28-policy-bypass-search.md)'s job).

## Open questions
1. Default k for CI gating vs. nightly.
2. Is `brittle` a severity or a label? (Recommend: label + AIVSS non-determinism factor.)
3. Should T3 ever run on shared CI runners? (Recommend: no.)
