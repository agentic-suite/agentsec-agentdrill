"""Oracle base + core verdict types (M6 work item 6.1).

An :class:`Oracle` turns a case's **observation** (the attack trajectory + the
agentwatch evidence it produced) into a :class:`Verdict` — ``blocked`` /
``missed`` / ``degraded`` across the three defense dimensions. Deterministic
oracles run first; judge oracles only where needed (ADR-0006).

Design: ``docs/design/oracle-engine.md``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Literal

from pydantic import BaseModel, Field

from agentdrill.attack_runner import CaseOutcome
from agentdrill.models.attack_pack import AttackCase
from agentdrill.models.evidence import Evidence

#: The honest outcome of a case.
Outcome = Literal["blocked", "missed", "degraded"]

#: The three defense dimensions (hierarchy: enforcement > integrity > efficiency).
Dimension = Literal["compatibility", "enforcement", "integrity"]

#: Failure taxonomy (design/oracle-engine.md).
FailureType = Literal[
    "safety_miss",
    "policy_miss",
    "evidence_gap",
    "telemetry_gap",
    "kill_slow",
    "target_error",
    "pack_error",
    "timeout",
    "adapter_error",
    "unknown",
]

#: Finding / divergence severity.
Severity = Literal["critical", "warning"]

#: Oracle kind — deterministic first, judge where needed, hybrid to combine.
OracleKind = Literal["deterministic", "judge", "hybrid"]


class Finding(BaseModel):
    """A problem worth surfacing for a case."""

    case_id: str
    type: FailureType
    severity: Severity = "warning"
    detail: str = ""


class Divergence(BaseModel):
    """A deterministic-vs-judge divergence (flagged, never averaged away)."""

    case_id: str
    severity: Severity
    detail: str = ""


class Verdict(BaseModel):
    """An oracle's verdict for one case."""

    case_id: str
    outcome: Outcome
    dimensions: list[Dimension] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    #: True when the deterministic gate stood because no judge was available.
    judge_not_evaluated: bool = False
    #: The deterministic gate's outcome, when a judge adjudicated (for divergence).
    gate_outcome: Outcome | None = None
    #: A deterministic-vs-judge divergence, when the two disagree.
    divergence: Divergence | None = None
    score: float | None = None
    rationale: str = ""


class Oracle(ABC):
    """Base class for oracles.

    Subclasses set :attr:`name`, :attr:`kind` and :attr:`dimensions`, and
    implement :meth:`evaluate`.
    """

    #: Registered oracle name.
    name: ClassVar[str] = ""

    #: ``deterministic`` | ``judge`` | ``hybrid``.
    kind: ClassVar[OracleKind] = "deterministic"

    #: Dimensions this oracle assesses.
    dimensions: ClassVar[tuple[Dimension, ...]] = ()

    @abstractmethod
    def evaluate(
        self,
        case: AttackCase,
        observed: CaseOutcome,
        evidence: list[Evidence] | None = None,
    ) -> Verdict:
        """Evaluate one case into a :class:`Verdict`."""
