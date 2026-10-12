# PRD 16 — Attack-Chain Orchestration & Adaptive Boundaries

**BLUF:** Real incidents are **chains**, not single shots (Slack-AI: inject via public channel → exfil via
image render; Replit: over-permission → destroy → cover up; Plugin4Shell: branch-name → auto-update → RCE).
agentdrill models chains as first-class pack structure with **state carried between steps** and records
**where the chain broke**. A bounded **adaptive orchestrator** can mutate documented patterns from live
target responses — hard-capped inside the dual-use boundary, always labeled, always provenance-tracked.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · Features: F18, F40

## Why chains

Single-shot tests measure whether a control stops *one action*. The documented incidents are multi-step:
each step is individually plausible, only the sequence is the attack. A defense that stops step 3 but not
steps 1–2 still shows a chain-level miss. Chains also expose **ordering** failures (controls that work in
isolation, not composition).

## Chain structure

```yaml
chain:
  id: slack-ai-exfil
  incident_ref: "incident-register#1"
  steps:
    - id: inject
      attack: {channel: public, payload: hidden_instruction}
      oracle: {expect: neutralized}     # per-step oracle
    - id: render
      attack: {tool: image_render, url: attacker}
      oracle: {expect: blocked}
      requires: [inject.succeeded]
  chain_oracle:
    expect: chain_broken_before: render   # where the chain MUST break
```

- **State carries between steps:** a step may be conditioned on prior step outcomes (`requires:`).
- **Per-step oracles + a chain oracle:** the chain oracle states *where* the chain must break; a defense
  that breaks it too late (post-exfil) is a different finding than one that never breaks it.
- **Result:** per-step outcome + `broke_at` (the furthest stage the attack reached) + evidence per step.

## Kill-chain stage model

Every case (chained or single) maps its result onto the shared stage model, which is also the timing
backbone (F37):

```
attack_start → delivered → detected → decided → halted → revoked → ceased
```

- A stage is `null` when it never happened, and **flagged**, never inferred.
- `broke_at` = the last stage the *defense* stopped the chain; the finding names the first un-guarded hop.

## Adaptive orchestration (bounded)

A PyRIT-style attacker step can **mutate a documented pattern** based on live target responses (rephrase
the payload, adjust arguments, reorder steps). Hard caps — these are product invariants, not guidelines:

1. **Parent provenance required:** every adaptive case carries `parent_pattern` (a documented incident) +
   `mutation_summary` + `reviewer`; no provenance, no publication.
2. **Mutation of documented patterns only** — paraphrase, encoding, argument/order perturbation. Never:
   new attack classes, new target surfaces, capability discovery.
3. **Bounded budget:** mutation attempts capped per case (`max_mutations`), per run cost ceiling, and
   per-chain step depth.
4. **Labeled in every result:** adaptive cases are labeled `adaptive` in the table and **excluded from
   golden-locked comparisons** (they explore, they do not anchor).
5. **Registry review:** an adaptive case entering a *shipped* pack requires human review (the HITL queue).

## Determinism with adaptivity

Adaptive runs are reproducible the same way everything else is: pinned attacker model + pinned seed +
recorded target responses in the manifest (the mutation *path* is part of the artifact). Two identical
adaptive runs produce identical mutation paths.

## What this is not

- Not an open-ended attacker agent (PRD 14 — no unbounded attack generation).
- Not novel exploit development — the parent pattern must already be documented publicly.
