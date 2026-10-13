"""Oracle engine (M6).

``Oracle`` evaluates a case's observation into a ``Verdict``; the registry
resolves oracles by name; deterministic oracles run first, judge oracles where
needed. Design: ``docs/design/oracle-engine.md``.
"""

from __future__ import annotations

from agentdrill.oracles import deterministic, judge
from agentdrill.oracles.base import (
    Dimension,
    Finding,
    Oracle,
    OracleKind,
    Outcome,
    Verdict,
)
from agentdrill.oracles.registry import SCORERS, get_oracle, register_oracle

__all__ = [
    "SCORERS",
    "Dimension",
    "Finding",
    "Oracle",
    "OracleKind",
    "Outcome",
    "Verdict",
    "deterministic",
    "get_oracle",
    "judge",
    "register_oracle",
]
