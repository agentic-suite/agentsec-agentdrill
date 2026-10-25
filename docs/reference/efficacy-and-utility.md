# Efficacy & Utility — Reference

**Status:** normative (M13). Implementation: `src/agentdrill/efficacy/`. Design:
[../design/efficacy.md](../design/efficacy.md). PRD: [20 efficacy/freshness](../prd/20-efficacy-freshness-lifecycle.md).

**A `blocked` number is meaningless unless the attack succeeds unguarded** (ADR-0007).

## Efficacy control (13.1, F59)

`run_efficacy(case_id, unguarded=, guarded_outcome=)` runs the attack against the **unguarded twin**:
`efficacy_verified` iff the attack succeeds unguarded; otherwise the case is **inert**.
`require_efficacy_backed` fails loudly (`EfficacyError`) if any enforced (blocked) case has no unguarded
success behind it — every enforced case has an unguarded success behind it.

## Inert flagging (13.2)

`INERT_FLAG = "attack_inert"`; `inert_cases` lists them. `countable(results)` keeps only
efficacy-verified cases, and `enforcement_rate(results)` is `blocked / (blocked + missed)` over countable
cases only (`None` when nothing is countable). An inert attack can never pad a green table or be counted
as coverage.

## Utility-under-attack (13.3, F51)

Every attack case links a `benign_twin`; `assess_utility(case_id, benign_utility=, utility_under_attack=,
enforcement_rate=)` publishes **benign utility**, **utility under attack** and the **enforcement rate**
together. A `utility_cost` finding is raised when enforcement is high (≥0.8) but the benign twin no
longer passes under attack — a "100% blocked" number never stands without its price tag.

## Cleanup (13.4, F50)

`run_cleanup` / `cleanup_after_case` run cleanup after **every** case (including timeout/error); a
failure or a raise leaves the target **dirty**. `dirty_targets` lists them and `require_clean` raises
`DirtyTargetError` — a **release-blocking `dirty_target`**, since a dirty target makes every later
number untrustworthy.

## Efficacy report artifact (13.5)

`build_efficacy_report(results)` → `EfficacyReport` with per-case `CaseEfficacy` (`efficacy_verified`,
`inert`, `guarded_outcome`, `flag`); `efficacy_evidence(result)` ships one `Evidence(event="efficacy")`
per case in the evidence bundle (CUJ-11).
