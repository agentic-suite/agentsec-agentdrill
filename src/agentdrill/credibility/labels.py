"""Oracle honesty labels (M19 19.6, F84).

Every oracle carries an honesty label — ``calibrated`` / ``reviewed`` /
``experimental`` — on every result; an ``experimental`` oracle **cannot gate
CI**. Design: ``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel

#: An oracle's honesty label.
HonestyLabel = Literal["calibrated", "reviewed", "experimental"]


class LabelError(ValueError):
    """Raised when a non-gate-capable oracle would gate CI."""


class OracleLabel(BaseModel):
    """An oracle's honesty label."""

    oracle: str
    label: HonestyLabel


def can_gate_ci(label: str) -> bool:
    """Whether an oracle at ``label`` may gate CI (``experimental`` never may)."""
    return label != "experimental"


def require_gate_capable(label: str) -> None:
    """Fail loudly if a non-gate-capable oracle would gate CI.

    Raises:
        LabelError: The oracle is experimental.
    """
    if not can_gate_ci(label):
        raise LabelError(f"an experimental oracle cannot gate CI (label={label!r})")


def label_result(labels: Iterable[OracleLabel]) -> dict[str, str]:
    """The per-oracle label mapping attached to a result."""
    return {labelled.oracle: labelled.label for labelled in labels}
