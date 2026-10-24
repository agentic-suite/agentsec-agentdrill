# Attack Chains & Adaptive Orchestration — Design

**BLUF:** Real incidents are **chains**, not single shots. agentdrill models a chain as first-class pack
structure with **state carried between steps**, a **chain oracle** stating where the chain must break, and
`broke_at` recording where it did. A bounded **adaptive orchestrator** mutates *documented* patterns from
live responses — hard-capped inside the dual-use boundary, always labelled and provenance-tracked.

> **Status:** normative (M15). **Implementation:** `agentdrill/chains/` — `model.py` (Chain/step/run),
> `runner.py` (step-by-step execution), `breakpoint.py` (`broke_at` + late-break finding), `adaptive.py`
> (bounded mutations), `adaptive_run.py` (determinism + manifest), `review_gate.py` (HITL). Spec:
> [PRD 16](../prd/16-attack-chain-orchestration.md). Reference:
> [chains-and-adaptive](../reference/chains-and-adaptive.md).

## Chain structure (15.1)

```yaml
chain:
  id: slack-ai-exfil
  incident_ref: "incident-register#1"
  steps:
    - {id: inject, tool: post_message, oracle: {expect: neutralized}}
    - {id: render, tool: image_render, oracle: {expect: blocked}, requires: [inject.succeeded]}
    - {id: exfil,  tool: send_external, oracle: {expect: blocked}, requires: [render.succeeded]}
  chain_oracle: {expect_break_before: render}
```

- **State carries between steps:** a step is reached only when each `requires` condition's prior step
  succeeded.
- **Per-step oracles + a chain oracle:** the chain oracle states *where* the chain must break.
- A stopped step (`blocked`/`neutralized`/`denied`) halts the chain.

## Break point (15.2)

`run_chain` records per-step outcome + `broke_at` (the step that stopped the chain) and
`furthest_reached`. `analyze_chain` classifies the run against the chain oracle: `on_time` (broke
before the expected step), `late` (broke at/after it), or `never_broke` — **distinct findings**: a
defense that stops the chain too late is a chain-level miss.

## Bounded adaptive orchestrator (15.3, F40) — the dual-use boundary

A PyRIT-style attacker step mutates a documented pattern from live target responses. These caps are
**product invariants**, not guidelines:

1. **Provenance required:** `parent_pattern` (a documented incident) + `mutation_summary` + `reviewer`;
   no provenance, no publication.
2. **Documented mutations only:** `paraphrase` / `encoding` / `argument` / `order`. Never new attack
   classes, new surfaces, or capability discovery.
3. **Bounded budget:** `max_mutations` per case, a per-run cost ceiling, and a per-chain step depth.
4. **Labelled & excluded:** adaptive cases carry the `adaptive` label and are **excluded from
   golden-locked comparisons** (`is_golden_comparable` false) — they explore, they do not anchor.
5. **Registry review:** an adaptive case entering a *shipped* pack requires an approved human review
   (the HITL queue).

## Determinism with adaptivity (15.4)

Adaptive runs are reproducible: a **pinned** attacker model + seed, with the mutation **path** recorded
in the manifest (`record_adaptive`). Two identical runs produce identical paths (`AdaptiveRun.digest`).

## What this is not

- Not an open-ended attacker agent (PRD 14 — no unbounded generation).
- Not novel exploit development — the parent pattern must already be documented publicly.
