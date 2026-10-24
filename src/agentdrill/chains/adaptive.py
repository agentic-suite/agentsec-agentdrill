"""Bounded adaptive orchestrator (M15 15.3, F40).

A PyRIT-style attacker step **mutates a documented pattern** from live target
responses (paraphrase, encoding, argument/order perturbation) — never new
attack classes, surfaces or capability discovery. Hard caps are product
invariants: provenance (``parent_pattern`` + ``mutation_summary`` +
``reviewer``), ``max_mutations``, a cost ceiling and step depth. Adaptive cases
are labelled ``adaptive`` and **excluded from golden-locked comparisons**.
Design: ``docs/prd/16-attack-chain-orchestration.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

#: The documented-pattern mutations an adaptive case may apply.
MUTATION_KINDS: tuple[str, ...] = ("paraphrase", "encoding", "argument", "order")

#: The label every adaptive case carries.
ADAPTIVE_LABEL = "adaptive"

#: Default hard caps.
DEFAULT_MAX_MUTATIONS = 2
DEFAULT_COST_CEILING = 1.0
DEFAULT_MAX_DEPTH = 3


class AdaptiveError(ValueError):
    """Raised when an adaptive case exceeds the dual-use boundary."""


class AdaptiveCase(BaseModel):
    """An adaptive case that mutates a documented parent pattern."""

    id: str
    parent_pattern: str = ""
    mutation_summary: str = ""
    reviewer: str = ""
    mutation: str = ""
    label: str = ADAPTIVE_LABEL
    max_mutations: int = DEFAULT_MAX_MUTATIONS
    step_depth: int = DEFAULT_MAX_DEPTH


def validate_adaptive(case: AdaptiveCase) -> None:
    """Enforce provenance and the documented-pattern-only rule.

    Raises:
        AdaptiveError: Provenance is missing, or the mutation is not a
            documented-pattern mutation (a novel capability).
    """
    if not case.parent_pattern or not case.mutation_summary or not case.reviewer:
        raise AdaptiveError(
            f"adaptive case {case.id}: provenance required "
            "(parent_pattern + mutation_summary + reviewer)"
        )
    if case.mutation not in MUTATION_KINDS:
        raise AdaptiveError(
            f"adaptive case {case.id}: mutation {case.mutation!r} is not a documented "
            f"pattern mutation {list(MUTATION_KINDS)}"
        )


def enforce_caps(
    case: AdaptiveCase,
    *,
    mutations_used: int,
    cost_usd: float,
    depth: int,
    cost_ceiling: float = DEFAULT_COST_CEILING,
) -> None:
    """Enforce the numeric caps (mutations, cost, depth).

    Raises:
        AdaptiveError: Any cap is exceeded.
    """
    if mutations_used > case.max_mutations:
        raise AdaptiveError(
            f"adaptive case {case.id}: used {mutations_used} mutations > cap {case.max_mutations}"
        )
    if cost_usd > cost_ceiling:
        raise AdaptiveError(f"adaptive case {case.id}: cost {cost_usd} > ceiling {cost_ceiling}")
    if depth > case.step_depth:
        raise AdaptiveError(f"adaptive case {case.id}: depth {depth} > cap {case.step_depth}")


def is_golden_comparable(case: AdaptiveCase) -> bool:
    """Whether a case may anchor a golden-locked comparison (adaptive may not)."""
    return case.label != ADAPTIVE_LABEL
