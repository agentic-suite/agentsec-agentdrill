# PRD 18 — Kill-Chain Verification & Kill-Time Measurement

**BLUF:** Detection is not safety; **cessation is**. agentdrill measures the full kill chain — attack-start
→ detected → decided → halted → revoked → ceased — with per-stage timestamps and p50/p95/max over repeated
trials, and publishes the **timeline**, not one latency number. "Revoked in 2s but the agent kept acting
for 11s" is the finding this exists to surface.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · Features: F37, R8, R23

## Why stage timing

Revocation that *reports* success while the agent keeps acting is the worst failure mode: the dashboard is
green and the damage continues. A single "detection latency" number hides exactly this. Stage timestamps
make the gap measurable and attributable.

## Stage model

| Stage | Meaning | Measured by |
|---|---|---|
| `attack_start` | The attack case begins executing | runner clock |
| `delivered` | Attack payload reached the harness/agent | driver adapter |
| `detected` | A control observed/flagged it | agentwatch event (`policy-fired`, `secret-detected`, anomaly) |
| `decided` | The PDP/broker decision issued | agentpolicy/agentkeys decision record |
| `halted` | agenthalt issued the halt | agentwatch `halted` event |
| `revoked` | agentkeys revoked the credential | agentwatch `revoked` event |
| `ceased` | The agent **actually stopped acting** | probe: can the agent still perform the guarded action? |

**`ceased` is a probe, not an event receipt.** The drill verifies cessation by re-attempting the guarded
action post-revocation; success = not ceased. This is the difference between measuring and believing.

## Measurement rules

- Repeated trials (≥5 per kill-time case) → **p50/p95/max per stage and per total**; means are reported but
  never alone (DD-27).
- Missing stage = `null` **+ flagged** (`evidence_gap` finding) — never inferred, never back-filled.
- The probe that establishes `ceased` is itself recorded in the evidence bundle (what was re-attempted,
  when, with what result).
- Stages recorded in the agentwatch schema so downstream compliance (agentcomply) consumes the same
  timeline.

## Findings the timeline produces

| Finding | Signature |
|---|---|
| `kill_slow` | detected→ceased exceeds the case's `max_seconds` |
| `detect_gap` | delivered→detected is the dominant interval (detection is the bottleneck) |
| `decision_gap` | detected→decided dominant (PDP/broker latency) |
| `halt_gap` | decided→halted dominant (halt path latency) |
| **`cease_gap`** | revoked→ceased dominant or nonzero — **the dashboard-green/damage-continues failure**; highest severity |

## What this is not

- Not a load/latency benchmark of the enforcers — only the kill path the attack exercised.
- Not inference: if the chain never reached a stage, that's the finding, not an assumed zero.
