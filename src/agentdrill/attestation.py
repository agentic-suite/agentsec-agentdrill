"""Attestation hooks (M5 work item 5.4).

Every component (target, driver) records its realness: ``live`` (the real
component), ``fixture`` (recorded/replayed), or ``mock``. A run's published label
is the **weakest link** in its chain — a ``mock`` anywhere makes the run a mock.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, cast

from pydantic import BaseModel

#: Realness of a component: live > fixture > mock.
AttestationLevel = Literal["live", "fixture", "mock"]

#: Higher rank = weaker (used by :func:`weakest_link`).
_RANK: dict[str, int] = {"live": 0, "fixture": 1, "mock": 2}


class Attestation(BaseModel):
    """A component's declared realness."""

    component: str
    level: AttestationLevel = "mock"


def weakest_link(levels: Iterable[str]) -> AttestationLevel:
    """Return the weakest level in ``levels``.

    An empty chain (or unknown levels) is conservatively treated as ``mock`` —
    never over-claimed as ``live``.
    """
    weakest: str | None = None
    for level in levels:
        normalized = level if level in _RANK else "mock"
        if weakest is None or _RANK[normalized] > _RANK[weakest]:
            weakest = normalized
    if weakest is None:
        return "mock"
    return cast(AttestationLevel, weakest)


def chain_attestation(components: Iterable[object]) -> AttestationLevel:
    """Weakest level across ``components`` (reads each one's ``attestation``)."""
    return weakest_link(str(getattr(component, "attestation", "mock")) for component in components)
