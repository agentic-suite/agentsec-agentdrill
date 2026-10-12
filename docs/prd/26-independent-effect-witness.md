# PRD 26 — Independent Effect Witness

**BLUF:** The oracle must not grade a defense using the defense's own log. Every enforcement case declares the **effect** it must prevent (a canary deleted, bytes reaching a sink, a honey credential used), and **witnesses outside the defended stack** confirm whether it happened. The defense's verdict and the witness are compared; **disagreement is a first-class finding** (`witness_discrepancy`). This closes the circularity of F52 (expected telemetry) and makes stealth-class attacks visible.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F87 · **Reqs:** R61

## Why

Today the oracle decides `blocked/missed/degraded` mainly from **agentwatch events** and expected telemetry (F52) — the thing under test is also the witness. Failure modes:
- Defense logs `denied` while a **side effect still lands** (partial/async execution, retry on another route).
- Defense silently works but emits no telemetry → false `telemetry_gap`.
- **Stealth attacks** (agent reports success while compromised) are invisible to log-based oracles — MCP-SafetyBench reports **53%** of its attacks are stealth class.
- Best-in-class benchmarks (AgentDojo, τ-bench, MCP-SafetyBench) grade **world state**, not text. We are currently weaker than the benchmarks we import.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R61** | Enforcement cases declare **forbidden effects** and are adjudicated by **independent witnesses** outside the defended stack; a `blocked` claim without witness confirmation is labeled. | ≥ 75% of enforcement cases witnessed at v0.1.0 (≥ 90% target); results carry `witness: live\|none`; `witness_discrepancy` is emitted whenever defense verdict ≠ witness. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F87** | **Independent effect witnesses + two-oracle verdict**: canary FS diff, network sinkhole (HTTP/DNS/TCP with per-run tokens), honey credentials/canary tokens, process/syscall witness, side-effect ledger (witness DB / mock SaaS), human-surface check. Verdict = compare defense decision × witness observation. | R61 | Consumes F59 (unguarded twin proves the effect is reachable), F63 (`witness` label), F43 (meta-verification) |

### Verdict model
| Defense says | Witness says | Verdict |
|---|---|---|
| denied | effect absent | `blocked` (confirmed) |
| denied | **effect present** | **`witness_discrepancy: false_block`** (highest-severity integrity finding) |
| no log / allowed | effect absent | `blocked_silently` (works; telemetry gap noted) |
| allowed | effect present | `missed` |
| denied | effect partial | `degraded` (partial detail) |
| — | witness failed/untrusted | `witness_unavailable` (cannot publish as `blocked`) |

### Witness integrity
Tamper-evident (hash-chained log, separate trust domain), started before / verified after each case; witness health is a precondition (extends F63). Witnesses double as the sinks for [PRD 27](27-adversary-lab.md).

## CUJs

### CUJ-30 — The log lied
A gateway logs `denied`; the sinkhole received 412 bytes. **Success:** the case is a `witness_discrepancy`, with packet-level proof and the stage where the chain really broke.

### CUJ-31 — Proof without telemetry
A defense emits no telemetry but does block. **Success:** the case is `blocked_silently` — provable, with the telemetry gap recorded.

## Success metrics

| Metric | Target |
|---|---|
| Enforcement cases with ≥1 independent witness | ≥ 75% (v0.1.0); ≥ 90% target |
| Published `blocked` cells with witness confirmation | ≥ 95% |
| `witness_discrepancy` detection on seeded faulty defenses (meta-verification) | ≥ 99% |
| Witness false-positive rate (clean unguarded run flagged as effect) | ≤ 0.5% |
| Witness false-negative on unguarded twins (efficacy control) | ≤ 1% |
| Witness overhead per case (median) | ≤ 2 s |
| Cross-OS parity of FS + network witnesses (macOS/Linux) | ≥ 99% outcome-identical |
| Results labeled `witness: none` shown distinctly | 100% |

## Dependencies
F43, F51, F59, F63 · [PRD 27](27-adversary-lab.md) (sink services), [PRD 35](35-rules-of-engagement-and-safe-fire.md) (canary-only invariant).

## Boundaries & non-goals
- **Canary-only:** destructive effects are only ever performed on canaries/ephemeral clones (hard invariant).
- Sinkhole is **local-only**; real egress is blocked at the host firewall and recorded.
- Not a detector; the witness observes *our own* drill's effects, never production traffic.

## Open questions
1. eBPF is Linux-only; on macOS run drill targets in a Linux VM/container for L3 witnesses.
2. Effect witnessing inside third-party SaaS agents: canary egress sink primary, cloud audit logs secondary.
