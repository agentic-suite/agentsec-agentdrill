# Attacker Strength & Bypass Search — Reference

**Status:** normative (M24). Implementation: `src/agentdrill/attacker/`. Design:
[attacker-strength-and-bypass](../design/attacker-strength-and-bypass.md). Specs:
[PRD 25](../prd/25-attacker-strength-and-pressure.md) · [PRD 28](../prd/28-policy-bypass-search.md).

## Tiers + metrics (24.1/24.2, F85/F86)

`label_tier(tier, k=)` → `TierLabel` (tier + k + effort); `TIERS`, `K_VALUES`, `t3_deferred`.
`hold_at_k(trials, k=, seed=, cost_to_break=)` → `HoldAtK` (`hold_rate` all-of-k, `asr_at_k` any-of-k,
both `RateCI`; first-break p50/p95; cost-to-break).

## Pressure + gate (24.3/24.4, F86)

`pressure_curve(case_id, asr_by_k=, t0_holds=, t2_breaks=)` → `PressureCurve` (points, auto `claim_scope`,
`brittle`); `claim_scope(curve)`. `hold_gate(hold_rate, k=, required=1.0)` → `HoldGateResult`;
`require_hold` raises `HoldGateError` (`Hold@5 < 100%` blocks); `DEFAULT_PR_K = 5`, `DEFAULT_NIGHTLY_K = 25`.

## Bypass search (24.5–24.8, F89)

`ROUTE_FAMILIES` / `EffectGoal` / `RouteCatalog` / `default_catalog` (≥12 effects) / `require_reviewed`.
`bounded_search(catalog, seed=, max_routes=, roe_ok=)` → `SearchResult` (seeded breadth-over-families then
depth; **RoE-gated**; same seed ⇒ same sequence). `minimize(effect, steps, essential=)` → `MinimizedBypass`;
`dedup_by_family(routes)`; `promote_to_regression(effect, fix_commit=)` → `FixCase`.
`build_coverage(effects, statuses=)` → `CoverageReport` (tried/blocked/bypassed/untried); `diff_aware`.
