# Attacker Strength & Effect-Based Bypass Search — Design

**BLUF:** Every number carries an **attacker-capability tier** and a **`Hold@k`/`ASR@k`** metric, so "blocked"
never masquerades as "robust". Separately, because rules are written against *forms* and attackers reach the
*effect*, a bounded **route-family search** finds equivalent bypasses, minimizes them, and auto-promotes them
to regression cases. WBS [M24](../wbs/v0.1.0/wbs-v0.1.0-part13-effect-witness-bypass.md). Reference:
[PRD 25](../prd/25-attacker-strength-and-pressure.md), [PRD 28](../prd/28-policy-bypass-search.md).

> **Design intent** (pre-build). Rewritten against the built system at M31–M32.

## Attacker-capability tiers (label on every result)

| Tier | Name | Attacker | Reproducible | Published |
|---|---|---|---|---|
| T0 | Static replay | documented payload, verbatim | yes | yes |
| T1 | Repeated attempts | T0 × k (k∈{1,5,10,25}, seeded) | yes | yes |
| T2 | Documented-pattern mutation | paraphrase/encoding/arg/order within F40 caps; mutation path in manifest | yes | yes (`adaptive`) |
| T3 | Adaptive search vs. this stack | budgeted optimizer/human-guided; **local-only** | exploratory | aggregate only (`exploratory`) |

**T3 is deferred for v0.1.0** (RoE-gated when introduced).

## Metrics (per case / per declared class; never a composite score)

- `Hold@k` — held on **all k** trials (defender's all-of-k).
- `ASR@k` — attacker succeeded ≥ once in k, with bootstrap CI (F55).
- **Pressure curve** — ASR vs. k / mutation budget / query budget.
- Time/queries-to-first-break (p50/p95); attacker cost-to-break.
- Auto **claim-scope statement**; **`brittle`** label when T0 holds but T2 breaks.

## Bypass search

```
for each effect goal E:
  for family in route_families(E):        # command/path/encoding/indirection/
    search(family, budget=seed)           #   tool-overlap/multi-step/transport/timing
      → candidate route
      judge by witness (M23)              #   effect with(out) the policy
      → if success: minimize (delta-debug) → dedup into family → promote to regression (F61)
coverage_report(E)                        # tried | blocked | bypassed | untried
```

**Effect goals** (shared with M23): delete canary tree; ≥1 byte to sink; use honey credential; spawn
outside allowlist; modify protected config; … **Route families** catalogue is curated like packs.

## Invariants

1. Route families are documented technique *classes*; runs only against the user's own stack under RoE.
2. Bounded by catalog + budget (no unbounded generation).
3. Published outputs are **family names + counts**, never weaponized payloads.
4. Deterministic: same seed ⇒ same route sequence and same mutation path.
5. T3 payloads never leak into published artifacts (scanner-verified).

## Data & artifacts

`run-manifest.json` adds `attacker_tier`, `k`, `mutation_path`, `search_seed`. Results gain
`hold_at_k`, `asr_at_k`, `pressure_curve`; a `bypass/<family>.json` artifact per confirmed bypass.

## Open questions
1. Default k (recommend 5 PR / 25 nightly).
2. `brittle` = label (+ AIVSS non-determinism factor) vs. severity.
3. Who curates route families (packs review + technique steward).
