"""Effect declarations (M23 23.1, F87).

Cases declare **forbidden effects** and **required-preserved effects**; a case
without effects is flagged. Design: ``docs/prd/26-independent-effect-witness.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EffectError(ValueError):
    """Raised when a case declares no effects."""


class Effect(BaseModel):
    """A declared effect (a forbidden or required-preserved behaviour)."""

    kind: str
    target: str
    detail: str = ""


class EffectDeclaration(BaseModel):
    """A case's effect declarations."""

    case_id: str
    forbidden: list[Effect] = Field(default_factory=list)
    required_preserved: list[Effect] = Field(default_factory=list)


def declares_effects(declaration: EffectDeclaration) -> bool:
    """Whether a declaration names any effect."""
    return bool(declaration.forbidden or declaration.required_preserved)


def require_effects(declaration: EffectDeclaration) -> None:
    """Fail loudly if a case declares no effects.

    Raises:
        EffectError: The case declares neither forbidden nor preserved effects.
    """
    if not declares_effects(declaration):
        raise EffectError(
            f"case {declaration.case_id}: declares no effects (forbidden or required-preserved)"
        )
