# Kill-Chain Verification — Design

**BLUF:** Detection is not safety; **cessation is**. agentdrill measures the full kill chain —
attack_start → delivered → detected → decided → halted → revoked → **ceased** — with a **probe** for
cessation (not an event receipt) and per-stage p50/p95/max, published as a timeline with typed findings.

> **Design intent** (pre-build). WBS M12. Reference: [PRD 18](../prd/18-kill-chain-verification.md).

## Stage model

| Stage | Measured by |
|---|---|
| `attack_start` | runner clock |
| `delivered` | driver adapter |
| `detected` | agentwatch event (policy-fired / secret-detected / anomaly) |
| `decided` | agentpolicy/agentkeys decision record |
| `halted` | agentwatch `halted` event |
| `revoked` | agentwatch `revoked` event |
| **`ceased`** | **probe:** re-attempt the guarded action post-revoke; success = NOT ceased |

A stage that never happened is `null` **+ flagged** — never inferred, never back-filled.

## Measurement

- ≥5 trials per kill-time case → **p50/p95/max** per stage and total (means never alone, DD-27).
- The cessation probe is recorded in the evidence bundle (what, when, result).

## Findings

| Finding | Signature |
|---|---|
| `kill_slow` | detected→ceased exceeds `max_seconds` |
| `detect_gap` | delivered→detected dominant |
| `decision_gap` | detected→decided dominant |
| `halt_gap` | decided→halted dominant |
| **`cease_gap`** | revoked→ceased nonzero/dominant — **revoked but still acting**; highest severity |

## Budgets as policy

Per-case `max_seconds` budgets are published **inside policyweave output** alongside the rule (F78) — the
budget is versioned and drilled like the rule it accompanies, so a latency regression lands in the same PR
as the rule change that caused it.
