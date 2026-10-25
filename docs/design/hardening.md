# Hardening — NFRs, Security & Resilience — Design

**BLUF:** Meet the non-functional requirements and harden the security baseline — performance budgets,
fail-closed fault handling, OS-level sandboxing for untrusted packs, tamper-evident audit, portability,
cost controls and self-observability.

> **Status:** normative (M22). **Implementation:** `agentdrill/hardening/` — `perf.py`,
> `faults.py`, `sandbox.py` (sandbox + audit chain), `portability.py`, `cost.py`, `observability.py`.
> Reference: [hardening](../reference/hardening.md). Spec:
> [PRD 13](../prd/13-non-functional-requirements.md).

## Performance & scale (22.1)

`measure_budget` (per-pack budget), `parallel_matches_serial`, `cache_stats`.

## Fault injection & fail-closed (22.2)

`FAULT_KINDS` (runner/target/oracle/driver/tamper); `run_fault` / `require_fail_closed` — a fault is
**never silently green**; `run_pack` — a case failure never aborts the pack.

## Untrusted-pack hardening (22.3)

`sandbox_spec_for` / `require_sandbox`: an `external` pack requires `--network none`, a read-only root
and resource caps. `AuditChain` is append-only and hash-chained — tamper is detected (G4).

## Portability (22.4)

`MIN_PYTHON = (3, 10)`; `SUPPORTED_OS = (Darwin, Linux)`; **local-first** (`check_portability` /
`require_portable`).

## Cost controls (22.5)

`cost_report` / `over_budget` — an over-budget run aborts and reports; caching savings are reported.

## Self-observability (22.6)

`build_summary` → `RunSummary` (dimensions + outcome split + exit code); `render()` answers "what
happened" in one summary.
