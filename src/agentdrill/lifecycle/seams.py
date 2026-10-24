"""Seam probing (M18 18.3, F62).

Controls that work in isolation but not in composition leave a **seam**: a
denied action re-attempted through another control slips past. ``seam_gap``
names **both** controls. Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

#: The finding raised when a composition gap is found.
SEAM_GAP = "seam_gap"


class SeamFinding(BaseModel):
    """A composition gap between two controls."""

    case_id: str
    gap: str = SEAM_GAP
    controls: list[str] = Field(default_factory=list)
    detail: str = ""


def probe_seam(
    case_id: str,
    *,
    first_control: str,
    second_control: str,
    first_denied: bool,
    second_allowed: bool,
) -> SeamFinding | None:
    """Probe a denied-then-retried composition.

    A ``seam_gap`` is returned when the first control denied the action but the
    re-attempt through the second control was allowed.

    Args:
        case_id: The case under probe.
        first_control: The control that first saw the action.
        second_control: The control the action was retried through.
        first_denied: Whether the first control denied the action.
        second_allowed: Whether the re-attempt was allowed through.
    """
    if first_denied and second_allowed:
        return SeamFinding(
            case_id=case_id,
            controls=[first_control, second_control],
            detail=(f"{SEAM_GAP}: denied by {first_control} but allowed through {second_control}"),
        )
    return None
