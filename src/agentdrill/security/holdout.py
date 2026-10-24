"""Dark holdout (M14 14.3, F33).

A private, **unpublished** holdout subset per pack, run in CI. Published-set
green + holdout red is a **pack-gaming** finding and is release-blocking. Design:
``docs/design/threat-model.md``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel


class PackGamingError(ValueError):
    """Raised when a pack passes its published set but fails the dark holdout."""


class HoldoutResult(BaseModel):
    """The holdout check for one pack release."""

    pack_ref: str
    published_green: bool
    holdout_green: bool

    @property
    def gaming(self) -> bool:
        """Whether the pack passes published but fails the dark holdout."""
        return self.published_green and not self.holdout_green


def check_holdout(pack_ref: str, *, published_green: bool, holdout_green: bool) -> HoldoutResult:
    """Build the holdout result for ``pack_ref``."""
    return HoldoutResult(
        pack_ref=pack_ref,
        published_green=published_green,
        holdout_green=holdout_green,
    )


def require_no_gaming(results: Iterable[HoldoutResult]) -> None:
    """Fail loudly (release-blocking) if any pack gamed its holdout.

    Raises:
        PackGamingError: One or more packs are green on the published set but
            red on the dark holdout.
    """
    gamed = [result.pack_ref for result in results if result.gaming]
    if gamed:
        raise PackGamingError(
            "pack-gaming (published green, holdout red): " + ", ".join(sorted(gamed))
        )


class HoldoutRegistry:
    """The private, unpublished holdout case ids per pack ref."""

    def __init__(self) -> None:
        self._holdouts: dict[str, list[str]] = {}

    def register(self, pack_ref: str, case_ids: Iterable[str]) -> None:
        """Register the holdout subset for a pack ref."""
        self._holdouts[pack_ref] = list(case_ids)

    def holdout_ids(self, pack_ref: str) -> list[str]:
        """The holdout case ids for ``pack_ref`` (empty when none registered)."""
        return list(self._holdouts.get(pack_ref, []))

    def published_ids(self, pack_ref: str, all_ids: Sequence[str]) -> list[str]:
        """``all_ids`` minus the private holdout subset (the public set)."""
        holdout = set(self._holdouts.get(pack_ref, []))
        return [case_id for case_id in all_ids if case_id not in holdout]
