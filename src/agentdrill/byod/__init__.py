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
from agentdrill.byod.head_to_head import (
    DefenseCell,
    HeadToHead,
    NeutralityError,
    build_head_to_head,
    rank_defenses,
)
from agentdrill.byod.zoo import ZOO_CLASSES, ZooAdapter, default_zoo, zoo_classes

__all__ = [
    "ZOO_CLASSES",
    "ConformanceCheck",
    "ConformanceError",
    "ConformanceResult",
    "DefenseCell",
    "DefenseContract",
    "DefenseSDK",
    "HeadToHead",
    "NeutralityError",
    "ZooAdapter",
    "build_contract",
    "build_head_to_head",
    "config_digest",
    "default_zoo",
    "rank_defenses",
    "require_conformant",
    "run_conformance",
    "zoo_classes",
]
