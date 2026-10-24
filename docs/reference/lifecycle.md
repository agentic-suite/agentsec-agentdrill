# Lifecycle — Reference

**Status:** normative (M18). Implementation: `src/agentdrill/lifecycle/`. Design:
[lifecycle](../design/lifecycle.md). Spec: [PRD 20](../prd/20-efficacy-freshness-lifecycle.md).

## Intake + fix-validation (18.1/18.2, F60/F61)

`Incident` + `assess(incident, decision=, now=, days_elapsed=, reason=)` → `TriageResult` (`SLA_DAYS = 7`;
an `n/a` decision requires a reason). `require_within_sla` raises `IntakeError` past the SLA; `is_stale`
flags a stale pack. `regression_case(case_id, fix_commit=)` → `FixCase` (permanent, pinned);
`evaluate_fix(case, observed_outcome=)` marks `decayed`; `require_fix_holds` raises `FixDecayError`
(release-blocking) with `attribute_decay`.

## Seams + attestation (18.3/18.4, F62/F63)

`probe_seam(case_id, first_control=, second_control=, first_denied=, second_allowed=)` → `SeamFinding`
(`SEAM_GAP`) naming both controls. `result_attestation(levels)` = weakest link; `can_publish` /
`require_publishable` (a `mock` result never publishes — `AttestationError`).

## Verifier + privacy (18.5/18.6, F64/F65)

`Bundle` + `verify_bundle(bundle, verifier=)` → `VerifyVerdict` (`intact` / `complete` / `honest_shaped`,
`ok`). `redact(content, location=)` → `RedactionResult` + `Receipt[]`; `verify_receipts(content, receipts)`.

## Quickstart + pack classes (18.7/18.8, F66/F19/F20)

`run_quickstart()` → `QuickstartResult` (mock-attested, watermarked `demo — never evidence`, ≤15 min —
`BUDGET_MINUTES`); `within_budget`. Packs: `packs/mcp-tool-surface.yaml` (F19),
`packs/memory-multiagent.yaml` (F20).

## Closes-the-loop (18.9, F21)

`AdvisoryRule` + `suggest_rule` / `what_if` / `propose_pr` — advisory, reviewed, never auto-applied.
