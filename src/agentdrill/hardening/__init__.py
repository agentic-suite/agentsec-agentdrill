"""Security hardening & resilience package (M22).

Performance & scale (22.1), fault injection & fail-closed (22.2), untrusted-pack
hardening (22.3), portability (22.4), cost controls (22.5) and self-observability
(22.6). Design: ``docs/prd/13-non-functional-requirements.md``.
"""

from agentdrill.hardening.cost import CostReport, cost_report, over_budget
from agentdrill.hardening.faults import (
    FAULT_KINDS,
    FaultError,
    FaultOutcome,
    require_fail_closed,
    run_fault,
    run_pack,
)
from agentdrill.hardening.perf import (
    PerfBudget,
    cache_stats,
    measure_budget,
    parallel_matches_serial,
)
from agentdrill.hardening.portability import (
    MIN_PYTHON,
    SUPPORTED_OS,
    PortabilityError,
    PortabilityReport,
    check_portability,
    require_portable,
)
from agentdrill.hardening.sandbox import (
    AuditChain,
    AuditEntry,
    SandboxError,
    SandboxSpec,
    require_sandbox,
    sandbox_spec_for,
)

__all__ = [
    "FAULT_KINDS",
    "MIN_PYTHON",
    "SUPPORTED_OS",
    "AuditChain",
    "AuditEntry",
    "CostReport",
    "FaultError",
    "FaultOutcome",
    "PerfBudget",
    "PortabilityError",
    "PortabilityReport",
    "SandboxError",
    "SandboxSpec",
    "cache_stats",
    "check_portability",
    "cost_report",
    "measure_budget",
    "over_budget",
    "parallel_matches_serial",
    "require_fail_closed",
    "require_portable",
    "require_sandbox",
    "run_fault",
    "run_pack",
    "sandbox_spec_for",
]
