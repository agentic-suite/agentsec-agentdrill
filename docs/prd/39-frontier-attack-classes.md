# PRD 39 — Frontier Attack Classes

**BLUF:** Against the final **OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)**, several categories have no efficacy-verified pack today (estimated: ASI08/09/10 absent; ASI03/05/06/07 partial or spec-gated; a PRD grep for *approval, browser, computer-use, multimodal, OAuth, confused deputy, cascad, trifecta, sabotage* returned **~zero** hits). Microsoft's own agent red-team tool lists browser automation, computer use, connected agents and function tools as **unsupported**. Ship these classes as pack classes with twins, witnesses, and cleanup.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F101 · **Reqs:** R75

## Why

- Coverage gaps leave whole ASI categories unproven — and buyers check the ASI list.
- Vendor tools have explicit blind spots (browser/computer-use/connected agents/function tools) — ownership whitespace.
- Each class has documented incidents or benchmarks behind it (documented-pattern rule holds).

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R75** | Seven frontier attack classes ship as pack classes (benign twins, witnesses, cleanup): human-in-the-loop/approval abuse, computer-use/browser, multimodal injection, identity+OAuth/delegation, memory+persistence, multi-agent cascade & rogue agents, resource-exhaustion/denial-of-wallet. AP2 payments is a spec-gated add-on. | ≥ 6/10 ASI categories efficacy-verified+witnessed at v0.1.0; ≥ 9/10 by v0.2; ≤ 10 cases/class minimum at v0.2. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F101** | **Frontier attack classes** (each = pack class with PRD 26 witnesses + PRD 27 lab + PRD 35 RoE): **(1)** approval abuse / lies-in-the-loop (ASI09) · **(2)** computer-use/browser injection (ASI01/02/05) · **(3)** multimodal injection (ASI01) · **(4)** identity, delegation & OAuth: token passthrough, confused deputy, RFC 8707 audience (ASI03) · **(5)** memory & persistence incl. instruction-file self-mod (ASI06) · **(6)** multi-agent cascade & rogue-agents: handoff/A2A propagation, oversight subversion, goal drift (ASI07/08/10) · **(7)** resource exhaustion / denial-of-wallet (LLM10) · **(8)** AP2 payments — spec-gated, P2 (ASI03) | R75 | Feeds PRD 21 pack catalog; maps to OWASP ASI (PRD 42) and ATLAS |

## CUJs

### CUJ-56 — Does the approval dialog tell the truth?
Drill 20 obfuscation cases; measure **approval fidelity** (displayed action ≡ executed action). **Success:** fidelity measured; anything below 99% is a finding.

### CUJ-57 — Contain the cascade
A compromised sub-agent tries to propagate via handoff; show containment depth and time-to-halt. **Success:** propagation depth ≤ 1 hop (target); halt p95 ≤ 10 s.

## Success metrics

| Metric | Target |
|---|---|
| ASI categories with ≥1 efficacy-verified, witnessed pack | ≥ 6/10 at v0.1.0 → ≥ 9/10 by v0.2 |
| Cases per class | ≥ 10 each at v0.2 (class 8 ≥ 3) |
| Approval fidelity (displayed ≡ executed) on drilled UIs | ≥ 99% (else finding) |
| Cascade containment propagation depth | ≤ 1 hop (target) |
| Time-to-halt of runaway sub-agent/loop p95 | ≤ 10 s |
| Cost amplification vs. budget ceiling | ≤ 105% |
| OAuth audience/passthrough rejection | 100% |
| Memory poisoning persistence across sessions | **0** (else finding) |
| Cases with independent witness | ≥ 90% |
| Dual-use review sign-off per class | 100% |

## Dependencies
F19, F20 · [PRD 26](26-independent-effect-witness.md), [PRD 27](27-adversary-lab.md), [PRD 35](35-rules-of-engagement-and-safe-fire.md), [PRD 41](41-platform-compatibility.md), [PRD 42](42-standards-and-claims.md).

## Boundaries & non-goals
- Documented patterns only; rogue/self-modification framed as **oversight subversion**, not capability uplift.
- Computer-use drilling needs isolated desktops/VMs (cost/flake) — start browser-only.
- Model-behavior auditing (Petri-style) is out of scope for enforcement proof.

## Open questions
1. Class order for v0.1.0 (recommend: identity → approval → memory → wallet → cascade → computer-use → multimodal).
2. Rogue-agent behavioral auditing: separate add-on?
