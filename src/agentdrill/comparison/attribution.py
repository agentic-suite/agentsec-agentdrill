"""Attribution — a flip names its cause (M9 9.4, F38, CUJ-14).

Correlate a blocked→missed flip with the target-config diff / pin change /
adapter change that caused it, reporting the **stage/mechanism** and a
confidence — never a bare diff. An unattributable flip is honestly ``unknown``,
never guessed. Design: ``docs/design/comparison.md``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import BaseModel

from agentdrill.comparison.attack_engine import CaseDelta
from agentdrill.comparison.change_detection import ChangeReport

#: What a flip could be attributed to.
AttributionSource = Literal["target_config", "adapter", "model", "oracle", "unknown"]

#: Confidence for a single, unambiguous cause vs. competing causes.
_SINGLE_CONFIDENCE = 0.9
_COMPETING_CONFIDENCE = 0.5

#: stage + mechanism per source.
_STAGE: dict[str, tuple[str, str]] = {
    "oracle": ("oracle", "oracle_version_changed"),
    "adapter": ("delivery", "adapter_changed"),
    "model": ("judge", "model_changed"),
    "target_config": ("enforcement", "target_config_changed"),
    "unknown": ("unknown", "unattributed"),
}


class Attribution(BaseModel):
    """The attributed cause of a case flip.

    Attributes:
        case_id: The case that flipped.
        direction: The flip direction (e.g. ``regressed``).
        attributed_to: The correlated cause, or ``unknown``.
        stage: The layer the cause sits in (enforcement/delivery/judge/oracle).
        mechanism: The named mechanism (e.g. ``target_config_changed``).
        confidence: 0.0 (unknown) .. 0.9 (single cause).
        detail: A human-readable explanation.
    """

    case_id: str
    direction: str
    attributed_to: AttributionSource
    stage: str
    mechanism: str
    confidence: float
    detail: str = ""


def attribute_flip(
    case_delta: CaseDelta,
    changes: ChangeReport,
    *,
    config_diffs: Mapping[str, object] | None = None,
) -> Attribution:
    """Attribute ``case_delta`` to the most likely mechanism, or ``unknown``.

    Priority (mechanism-backed): oracle change (invalidates comparability) >
    adapter change > model change > target-config diff. Unrelated changes
    lower the confidence; nothing relevant ⇒ honest ``unknown``.
    """
    if not case_delta.changed:
        return _attribution(case_delta, "unknown", "case did not change")

    diffs = dict(config_diffs or {})
    signals = len(changes.changes) + (1 if diffs else 0)

    if changes.oracle_changed:
        source: AttributionSource = "oracle"
    elif changes.adapter_changed:
        source = "adapter"
    elif changes.model_changed:
        source = "model"
    elif diffs:
        source = "target_config"
    else:
        source = "unknown"

    if source == "unknown":
        return _attribution(case_delta, "unknown", "no mechanism correlated")

    confidence = _SINGLE_CONFIDENCE if signals == 1 else _COMPETING_CONFIDENCE
    if source == "target_config":
        detail = "target config changed: " + ", ".join(f"{k}={v}" for k, v in sorted(diffs.items()))
    else:
        detail = next((c.detail for c in changes.changes if c.kind == f"{source}_changed"), "")
    return _attribution(case_delta, source, detail, confidence=confidence)


def _attribution(
    case_delta: CaseDelta, source: AttributionSource, detail: str, *, confidence: float = 0.0
) -> Attribution:
    stage, mechanism = _STAGE[source]
    return Attribution(
        case_id=case_delta.case_id,
        direction=case_delta.direction,
        attributed_to=source,
        stage=stage,
        mechanism=mechanism,
        confidence=confidence,
        detail=detail,
    )


def bisect_flip(observations: Sequence[str]) -> int | None:
    """The index of the first ``regressed`` observation, or None.

    The CI bisect discipline: re-run against intermediate configs and find
    where a flip first appears.
    """
    for index, direction in enumerate(observations):
        if direction == "regressed":
            return index
    return None
