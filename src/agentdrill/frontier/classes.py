"""Frontier attack classes (M29 29.4-29.7, F101).

The classes that close the OWASP **ASI** gaps. Each ships as a pack class with
benign twins, witness effects and cleanup; a class is only useful once its
category is **efficacy-verified and witnessed** (never asserted). Documented
patterns only — oversight subversion, never capability uplift. Design:
``docs/design/detonation-breakit-frontier.md``; PRD 39 (R75).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

#: The OWASP Agentic Security Initiative categories.
AsiCategory = Literal[
    "ASI01",
    "ASI02",
    "ASI03",
    "ASI04",
    "ASI05",
    "ASI06",
    "ASI07",
    "ASI08",
    "ASI09",
    "ASI10",
]

#: The ASI categories as a runtime tuple.
ASI_CATEGORIES: tuple[str, ...] = tuple(f"ASI{i:02d}" for i in range(1, 11))

#: The default minimum number of ASI categories that must be verified.
DEFAULT_MIN_ASI_COVERAGE = 6


class FrontierError(ValueError):
    """Raised when a frontier class fails its acceptance check."""


class FrontierClass(BaseModel):
    """One frontier attack class (a pack class + its acceptance criteria)."""

    number: int
    name: str
    asi: list[str] = Field(default_factory=list)
    atlas: str = ""
    validates: str = ""
    twin_driver: str = "subprocess"
    witness_effects: list[str] = Field(default_factory=list)
    cleanup: bool = True
    implemented: bool = True
    #: True for a class gated on an external spec (e.g. AP2 payments).
    spec_gated: bool = False
    dual_use_signed: bool = False
    #: Payload carriers for multimodal classes (≥12 required).
    carriers: int = 0


#: The frontier-class registry (single writer).
FRONTIER_CLASSES: dict[int, FrontierClass] = {
    4: FrontierClass(
        number=4,
        name="Identity, delegation & OAuth",
        asi=["ASI03"],
        atlas="ATLAS-AML.T0055",
        validates="broker scoping, RFC 8707 audience, task-scoped tokens",
        witness_effects=["cross_agent_token_use"],
    )
}


def require_audience_rejection(results: Sequence[tuple[str, bool]]) -> None:
    """Fail loudly unless every audience/passthrough probe was rejected.

    Raises:
        FrontierError: A probe was not rejected (audience/passthrough rejection
            must be 100 %).
    """
    accepted = [kind for kind, rejected in results if not rejected]
    if accepted:
        raise FrontierError(
            f"class 4: these probes were not rejected (must be 100%): {accepted}"
        )


def asi_coverage(*, verified: Sequence[str]) -> int:
    """The number of distinct ASI categories efficacy-verified and witnessed."""
    return len({category for category in verified if category in ASI_CATEGORIES})


def require_asi_coverage(
    *, verified: Sequence[str], minimum: int = DEFAULT_MIN_ASI_COVERAGE
) -> None:
    """Fail loudly unless at least ``minimum`` ASI categories are verified.

    Raises:
        FrontierError: The coverage is below the gate.
    """
    coverage = asi_coverage(verified=verified)
    if coverage < minimum:
        raise FrontierError(
            f"ASI coverage {coverage}/{len(ASI_CATEGORIES)} is below the required {minimum}"
        )


def require_dual_use_signed(klass: FrontierClass) -> None:
    """Fail loudly unless the class has a dual-use review sign-off.

    Raises:
        FrontierError: The class is not signed off.
    """
    if not klass.dual_use_signed:
        raise FrontierError(
            f"frontier class {klass.number} ({klass.name}) has no dual-use review sign-off"
        )
