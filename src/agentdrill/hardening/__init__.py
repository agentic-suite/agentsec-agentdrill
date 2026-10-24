"""Security hardening & resilience package (M22).

Performance & scale (22.1), fault injection & fail-closed (22.2), untrusted-pack
hardening (22.3), portability (22.4), cost controls (22.5) and self-observability
(22.6). Design: ``docs/prd/13-non-functional-requirements.md``.
"""

from agentdrill.hardening.perf import (
    PerfBudget,
    cache_stats,
    measure_budget,
    parallel_matches_serial,
)

__all__ = [
    "PerfBudget",
    "cache_stats",
    "measure_budget",
    "parallel_matches_serial",
]
