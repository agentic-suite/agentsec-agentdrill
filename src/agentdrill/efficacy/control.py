"""Efficacy control (M13 13.1, F59).

Every case runs against an **unguarded twin** target; a case is
efficacy-verified only if the attack **succeeds unguarded**. An unguarded
failure means the case is inert. ADR-0007: a ``blocked`` number is meaningless
unless the attack succeeds unguarded. Design: ``docs/design/efficacy.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from pydantic import BaseModel


class EfficacyError(ValueError):
    """Raised when an enforced case has no unguarded success behind it."""


class EfficacyResult(BaseModel):
    """The efficacy-control outcome for one case.

    Attributes:
        case_id: The case the control ran.
        unguarded_succeeded: Whether the attack succeeded against the unguarded twin.
        guarded_outcome: The guarded run's outcome (``blocked``/``missed``/...).
    """

    case_id: str
    unguarded_succeeded: bool
    guarded_outcome: str | None = None

    @property
    def efficacy_verified(self) -> bool:
        """Whether the case is efficacy-verified (the attack works unguarded)."""
        return self.unguarded_succeeded

    @property
    def inert(self) -> bool:
        """Whether the case is inert (the attack does not work unguarded)."""
        return not self.unguarded_succeeded

    @property
    def is_real_miss(self) -> bool:
        """A real miss: the attack works unguarded but was not blocked when guarded."""
        return self.unguarded_succeeded and self.guarded_outcome == "missed"


def run_efficacy(
    case_id: str,
    *,
    unguarded: Callable[[], bool],
    guarded_outcome: str | None = None,
) -> EfficacyResult:
    """Run the unguarded control for ``case_id`` and record the guarded outcome.

    Args:
        case_id: The case under control.
        unguarded: Runs the attack against the unguarded twin; returns ``True``
            if it succeeded (the attack is real).
        guarded_outcome: The guarded run's outcome, when known.
    """
    return EfficacyResult(
        case_id=case_id,
        unguarded_succeeded=bool(unguarded()),
        guarded_outcome=guarded_outcome,
    )


def require_efficacy_backed(results: Iterable[EfficacyResult]) -> None:
    """Fail loudly if an enforced (blocked) case has no unguarded success.

    Raises:
        EfficacyError: A case reports a guarded ``blocked`` while being inert —
            an enforced number with no attack behind it.
    """
    offenders = [
        result.case_id for result in results if result.guarded_outcome == "blocked" and result.inert
    ]
    if offenders:
        raise EfficacyError(
            "enforced case(s) without an unguarded success behind them: "
            + ", ".join(sorted(offenders))
        )
