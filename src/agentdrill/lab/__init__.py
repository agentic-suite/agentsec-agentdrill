"""Adversary Lab package (M23).

The versioned loopback lab (23.6), the poisoned content corpus (23.7) and lab
isolation + ground truth (23.8). Design: ``docs/prd/27-adversary-lab.md``.
"""

from agentdrill.lab.carriers import CARRIERS, Carrier, CarrierError, carrier_matrix, render_carrier
from agentdrill.lab.core import (
    EVIL_MCP_BEHAVIORS,
    LAB_COMPONENTS,
    AdversaryLab,
    LabEvent,
    build_lab,
    event_log,
)

__all__ = [
    "CARRIERS",
    "EVIL_MCP_BEHAVIORS",
    "LAB_COMPONENTS",
    "AdversaryLab",
    "Carrier",
    "CarrierError",
    "LabEvent",
    "build_lab",
    "carrier_matrix",
    "event_log",
    "render_carrier",
]
