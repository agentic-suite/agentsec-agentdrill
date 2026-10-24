# BYOD & Neutral Head-to-Head — Reference

**Status:** normative (M25). Implementation: `src/agentdrill/byod/`. Design:
[byod-and-neutral-head-to-head](../design/byod-and-neutral-head-to-head.md). Spec:
[PRD 29](../prd/29-bring-your-own-defense.md).

## Defense contract + SDK (25.1, F90)

`config_digest(config)` → `sha256:...`. `build_contract(name=, decision_points=, io_shape=, evidence=,
config=, fail_mode=, version=, tos_notes=)` → `DefenseContract` (decision points, I/O shape, evidence,
config digest, fail-mode, version, ToS notes). `DefenseSDK(contract, decide=)` wraps a request/response
defense; `.evaluate(request)` → response.

## Conformance kit (25.2, F90)

`run_conformance(contract, sdk, sample_requests=)` → `ConformanceResult` (`passed`, `level`) over the
`round_trip` / `determinism` / `evidence_integrity` / `fail_mode` checks; `require_conformant` raises
`ConformanceError` unless 100% pass.

## Defense Zoo (25.3, F90)

`ZOO_CLASSES` (policy-engine, model-guard, guardrails, sandbox, harness-native); `ZooAdapter(name, klass,
contract)`; `default_zoo()` (≥2 adapters across ≥2 classes); `zoo_classes(adapters)`.

## Neutral head-to-head (25.4, F91)

`DefenseCell(defense, config_digest, hold_at_k, asr_at_k, false_block, cost_per_1k, latency_ms,
fail_mode)`; `build_head_to_head(pack_ref, seeds=, cells=)` → `HeadToHead` (shared pack + seeds; no
composite). `rank_defenses` always raises `NeutralityError` — zero rankings.

## Neutrality process (25.5, F91)

`NeutralityRules(rules, published, preregistered, equal_rules)`; `default_rules()`; `require_neutrality`
raises `NeutralityError` unless published + pre-registered + equal. `CorrectionsLog().add(when=, what=)`;
`author_review_needed(authors=, reviewers=)` → author-overlap disclosure.
