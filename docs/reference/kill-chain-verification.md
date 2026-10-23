# Kill-Chain Verification — Reference

**Status:** normative (M12). Implementation: `src/agentdrill/killchain/`. Design:
[../design/killchain.md](../design/killchain.md). PRD: [18 kill-chain verification](../prd/18-kill-chain-verification.md).

**Detection is not safety; cessation is.** agentdrill measures the whole kill chain and **probes**
cessation rather than trusting an event receipt.

## Stage model + timeline (12.1)

`KILL_CHAIN_STAGES` = `attack_start → delivered → detected → decided → halted → revoked → ceased`.
`build_timeline(case_id, timestamps)` fills absent stages with `null` and records them in `missing`
(`flagged`) — never inferred. `KillChainTimeline.stages[stage]` is seconds since `attack_start`. An
unknown stage raises `ValueError`.

## Cessation probe (12.2)

`run_cessation_probe(case_id, revoke=, reattempt=, action=)` drives the revoke, then **re-attempts the
guarded action**: `ceased = not action_succeeded`. A revoked-but-still-acting target yields
`ceased=False`. The re-attempt is recorded as an evidence event
(`probe_evidence(result, at=)` → `Evidence(event="cease-probe", summary=what/when/result)`, 12.6).

## Timing policy (12.3)

≥5 trials per kill-time case → **p50/p95/max** per stage segment and total (`compute_timing` →
`TimingReport`); `require_trials` raises `InsufficientTrialsError` below 5. Means are never published
alone (DD-27). A segment whose two stages are both present contributes a duration; a total needs
`attack_start` and a later stage.

## Findings (12.4)

`analyze_timeline(timeline, max_seconds=)`:

| Finding | Signature | Severity |
|---|---|---|
| `kill_slow` | total > `max_seconds` | warning |
| `detect_gap` | `delivered→detected` dominant | warning |
| `decision_gap` | `detected→decided` dominant | warning |
| `halt_gap` | `decided→halted` dominant | warning |
| `cease_gap` | revoked but never ceased, or `revoked→ceased` dominant | critical |

A segment is "dominant" when it is the largest and at least `min_gap_seconds` (default 0.5). `cease_gap`
(revoked but still acting) is first-class and highest severity.

## Budgets as policy (12.5, F78)

`publish_budget(case_id, rule_id, max_seconds)` produces a **versioned** `kill_time` block published
inside policyweave output alongside the rule; `read_budgets(policy)` reads them back. A changed budget
changes its version, so a latency regression lands in the same PR as the rule change that caused it. A
rule without a budget is absent, never inferred.
