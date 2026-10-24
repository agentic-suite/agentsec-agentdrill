"""Target attestation (M18 18.4, F63).

Every component records its realness (``live`` / ``fixture`` / ``mock``); a
result is labeled at the **weakest link**, and a ``mock``-attested result can
never publish. Reuses the M5 :mod:`agentdrill.attestation` SSOT. Design:
``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

from collections.abc import Iterable

from agentdrill.attestation import AttestationLevel, weakest_link


class AttestationError(ValueError):
    """Raised when a mock-attested result would be published."""


def result_attestation(levels: Iterable[str]) -> AttestationLevel:
    """The result's label — the weakest link in the chain (empty ⇒ ``mock``)."""
    return weakest_link(levels)


def can_publish(level: str) -> bool:
    """Whether a result at ``level`` may publish (``mock`` never may)."""
    return level != "mock"


def require_publishable(level: str) -> None:
    """Fail loudly if a ``mock``-attested result would publish.

    Raises:
        AttestationError: The result is mock-attested.
    """
    if not can_publish(level):
        raise AttestationError(f"mock-attested result cannot publish (attestation={level!r})")
