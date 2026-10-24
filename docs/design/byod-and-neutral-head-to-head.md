# Bring-Your-Own-Defense & Neutral Head-to-Head — Design

**BLUF:** agentdrill is neutral: an open **Defense Contract** + SDK + conformance kit lets any defense be
drilled and compared fairly, under published neutrality rules, with no composite score. WBS
[M25](../wbs/v0.1.0/wbs-v0.1.0-part14-byod-integrations.md). Reference:
[PRD 29](../prd/29-bring-your-own-defense.md).

> **Status:** normative (M25) — implemented in `agentdrill/byod/`. See the reference:
> [byod-and-neutral-head-to-head](../reference/byod-and-neutral-head-to-head.md).

## Defense contract (concept; adapter API lives in [adapter-contract](adapter-contract.md))

Each adapter declares:

| Field | Meaning |
|---|---|
| `decision_points` | where it returns a verdict (input filter, tool authorize, egress, revoke, …) |
| `io_shape` | request/response schema |
| `evidence` | what it emits (verdict, latency, decision log) |
| `config_digest` | hash of the exact configuration (binds every result) |
| `fail_mode` | open \| closed |
| `version` | adapter + defense version |
| `tos_notes` | license/ToS constraints (benchmarking clauses) |

## Conformance kit

Exercises round-trip, determinism, evidence integrity, fail-mode; awards a **conformance level**. 100% pass
before listing. A **Defense Zoo** ships OSS-first reference adapters (OPA/Cedar, Llama Guard/Prompt Guard,
NeMo Guardrails, Docker/gVisor profiles, harness-native sandboxes).

## Head-to-head report (no composite score)

Same pack, seeds, environment, benign twins; **N** defenses. Columns per case/tier: `Hold@k`, `ASR@k`+CI,
witness-confirmed; **utility cost** (false-block on twins + CI); **$ / 1k calls** and p50/p95 added latency;
fail-open/closed. **No ranking arrow, no aggregated score, misses shown.**

## Neutrality rules (published, binding)

1. Pre-registered methodology + pack list before any run.
2. Vendor **right-of-reply** (14 d, raw bundle; reply published verbatim) — extends F32.
3. **Licensed/own configuration only**; no benchmarking where ToS forbids without consent; `tos_reviewed` recorded.
4. Conflict disclosure; ecosystem-owned defenses flagged and held to the same contract.
5. Config digest on every cell; default vs. tuned labeled separately.
6. Counsel review before first publication.

## Invariants

1. Measures a defense **in a configuration**, never "the product".
2. No composite score or ranking, ever.
3. Our own defenses are held to the same contract and kit.

## Open questions
1. Where the adapter listing lives (in-project → foundation).
2. Legal/ToS shape of competitor publication (counsel first).
