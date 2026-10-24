"""Bring-your-own-defense & neutral head-to-head package (M25).

The Defense Contract + SDK (25.1), the conformance kit (25.2), the Defense Zoo
(25.3), the neutral head-to-head (25.4) and the neutrality process (25.5).
Design: ``docs/prd/29-bring-your-own-defense.md``.
"""

from agentdrill.byod.conformance import (
    ConformanceCheck,
    ConformanceError,
    ConformanceResult,
    require_conformant,
    run_conformance,
)
from agentdrill.byod.contract import (
    DefenseContract,
    DefenseSDK,
    build_contract,
    config_digest,
)

__all__ = [
    "ConformanceCheck",
    "ConformanceError",
    "ConformanceResult",
    "DefenseContract",
    "DefenseSDK",
    "build_contract",
    "config_digest",
    "require_conformant",
    "run_conformance",
]
