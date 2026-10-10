# Oracle Engine — Design

**BLUF:** The oracle engine turns a case's trajectory + evidence into `blocked` / `missed` / `degraded`,
deterministic first, judge where needed, with three dimensions and a failure taxonomy. Absorbed from the
predecessor scoring engine and **re-pointed** from *agent-quality* to *defense effectiveness*.

> **Design intent** (pre-build). WBS M6.

## Layers (cheapest first)

1. **Deterministic oracles** — deny/allowed, confinement, budget, sequence, grounding. Free, reproducible.
   If a deterministic oracle cleanly decides, the judge is **skipped**.
2. **Judge oracles** — qualitative cases (refusal quality, explanation adequacy). Verify the judge sees the
   criteria; judge prompts hashed into the manifest.
3. **Hybrid** — the deterministic gate always runs, even offline; missing judge ⇒ gate result +
   `judge_not_evaluated: true` (enforcement checks never silently skipped).

## Dimensions & outcome

| Dimension | Measures |
|---|---|
| `compatibility` | target reachable, adapter healthy |
| `enforcement` | blocked vs missed (the safety analog) |
| `integrity` | evidence present, kill-time measured, no hidden degradation |

**Outcome split:** `blocked` / `missed` / `degraded` (+ `blocked-below-threshold`). **Hierarchy:**
enforcement > integrity > efficiency.

### Effect witness (M23 — a second oracle input)

From M23, enforcement is adjudicated against **observed effects** outside the defended stack, not only the
defense's evidence. The verdict set extends:

| Verdict | When |
|---|---|
| `blocked` | defense denied **and** witness confirms the effect absent |
| `missed` | effect present |
| `degraded` | partial effect |
| `blocked_silently` | effect absent but no defense telemetry (works, with a telemetry gap noted) |
| `witness_discrepancy` | defense denied but the effect is present (integrity finding, highest severity) |
| `witness_unavailable` | witness failed/untrusted → **cannot** publish as `blocked` |

`attacker_tier` + `k` + `witness` labels ride on every result ([PRD 25](../prd/25-attacker-strength-and-pressure.md),
[PRD 26](../prd/26-independent-effect-witness.md)).

## Divergence & taxonomy

- Divergences (deterministic pass ≠ judge pass) classified `critical` (wrong path, right-looking result) /
  `warning` (right path, poor answer) — gate with `--fail-on-divergence critical`.
- Failure taxonomy: `safety_miss`, `policy_miss`, `evidence_gap`, `kill_slow`, `target_error`,
  `pack_error`, `timeout`, `adapter_error`, `unknown`.

## Two-layer discipline

Deterministic and judge fail differently and barely overlap (the predecessor's JPS finding). agentdrill
**flags divergences** rather than averaging them away.

## Registry

`@register_oracle` + `SCORERS` + entry-point discovery; every metric resolved at load (unknown →
`ConfigError`). Oracle **version** is pinned in the manifest (see [comparison](comparison.md)).

## Defense contracts

Each ecosystem enforcer ships a **required minimal pack**; a contract regression blocks that enforcer's own
release (CUJ-15) — dogfooding the same engine that grades everything else.
