# Chains & Adaptive Orchestration — Reference

**Status:** normative (M15). Implementation: `src/agentdrill/chains/`. Design:
[attack-chains](../design/attack-chains.md). Spec: [PRD 16](../prd/16-attack-chain-orchestration.md).

## Chain structure (15.1)

`Chain`/`ChainStep`/`StepOracle`/`ChainOracle`; `run_chain(chain, run_step)` → `ChainRun` (a `StepResult`
per step). A step with `requires: ["inject.succeeded"]` is reached only when each named prior step
succeeded; a stopped step (`blocked`/`neutralized`/`denied`) halts the chain.

## Break point (15.2)

`ChainRun.broke_at` (the step that stopped the chain) and `ChainRun.furthest_reached`.
`analyze_chain(chain, run)` → `ChainBreakFinding`: `on_time` (broke before the chain oracle's step),
`late` (at/after it), `never_broke` — distinct findings.

## Bounded adaptive orchestrator (15.3, F40)

`AdaptiveCase` (id, `parent_pattern`, `mutation_summary`, `reviewer`, `mutation`, `label="adaptive"`,
`max_mutations`, `step_depth`). `validate_adaptive` requires provenance and a documented mutation
(`MUTATION_KINDS = paraphrase/encoding/argument/order`) — no novel capability. `enforce_caps` bounds
mutations, cost and depth. `is_golden_comparable` is false for adaptive cases (excluded from
golden-locked comparisons).

## Determinism (15.4)

`run_adaptive(case, model=, seed=)` → `AdaptiveRun` (pinned model + seed; the path is a pure function of
`(case, model, seed)`); `AdaptiveRun.digest()` is stable and `record_adaptive(manifest, run)` writes the
mutation path under `manifest["adaptive"]`. Two identical runs produce identical paths.

## Registry review gate (15.5)

`ReviewRecord` + `require_reviewed(cases, reviews)` / `can_ship(cases, reviews)`: an adaptive case
entering a shipped pack requires an approved human review; non-adaptive cases need none;
`ReviewGateError` blocks an unreviewed adaptive case from shipping.
