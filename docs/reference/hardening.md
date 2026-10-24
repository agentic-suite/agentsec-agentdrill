# Hardening — Reference

**Status:** normative (M22). Implementation: `src/agentdrill/hardening/`. Design:
[hardening](../design/hardening.md). Spec: [PRD 13](../prd/13-non-functional-requirements.md).

## Performance & scale (22.1)

`measure_budget(pack_ref, elapsed_seconds=, budget_seconds=)` → `PerfBudget` (`met`);
`parallel_matches_serial(serial, parallel)`; `cache_stats(cache)`.

## Faults (22.2)

`FAULT_KINDS = (runner, target, oracle, driver, tamper)`; `run_fault(kind, fn)` → `FaultOutcome`;
`require_fail_closed(outcomes)` raises `FaultError` on a silently-green fault; `run_pack(cases)` never
aborts on a case failure.

## Sandbox + audit (22.3)

`SandboxSpec(network="none", read_only_root=True, memory_limit="512m", cpu_limit=1.0)`;
`sandbox_spec_for(trust)`; `require_sandbox(trust, spec)` (`SandboxError`). `AuditChain` — append-only,
hash-chained; `.add(payload)`, `.verify()`, `.head`.

## Portability (22.4)

`MIN_PYTHON = (3, 10)`; `SUPPORTED_OS = ("Darwin", "Linux")`; `check_portability(...)` →
`PortabilityReport` (`local_first=True`); `require_portable` (`PortabilityError`).

## Cost (22.5)

`over_budget(spent_usd, budget_usd)`; `cost_report(spent_usd=, budget_usd=, cached_savings_usd=)` →
`CostReport` (`aborted`, `savings_usd`).

## Observability (22.6)

`build_summary(run_id, verdicts=, exit_code=)` → `RunSummary` (`outcome`, `dimensions`, `exit_code`,
`render()`).
