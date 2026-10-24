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
from agentdrill.lab.isolation import (
    LOOPBACK_HOSTS,
    EgressViolation,
    LabIsolation,
    enforce_loopback,
    pin_lab,
)

__all__ = [
    "CARRIERS",
    "EVIL_MCP_BEHAVIORS",
    "LAB_COMPONENTS",
    "LOOPBACK_HOSTS",
    "AdversaryLab",
    "Carrier",
    "CarrierError",
    "EgressViolation",
    "LabEvent",
    "LabIsolation",
    "build_lab",
    "carrier_matrix",
    "enforce_loopback",
    "event_log",
    "pin_lab",
    "render_carrier",
]
