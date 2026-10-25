"""Change detection — swaps are not regressions (M9 9.3).

Distinguishes a driver/target swap (``adapter_changed``), a model-pin change
(``model_changed``) and an oracle-version change (``oracle_changed``) from a
real defense regression. An outcome flip with no detected change is a real
regression; a swap is not. Design: ``docs/design/comparison.md``.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentdrill.models.manifest import RunManifest

#: The kinds of run change that are not defense regressions.
ChangeKind = Literal["adapter_changed", "model_changed", "oracle_changed"]


class RunChange(BaseModel):
    """One detected non-regression change between a baseline and a candidate."""

    kind: ChangeKind
    detail: str


class ChangeReport(BaseModel):
    """Detected adapter/model/oracle changes between two runs."""

    adapter_changed: bool = False
    model_changed: bool = False
    oracle_changed: bool = False
    changes: list[RunChange] = Field(default_factory=list)

    @property
    def any(self) -> bool:
        """Whether any non-regression change was detected."""
        return bool(self.changes)

    @property
    def invalidates_comparability(self) -> bool:
        """Whether the change invalidates comparability (an oracle change)."""
        return self.oracle_changed


def _pairs(items: list[dict[str, Any]], key: str, value: str) -> list[tuple[str, str]]:
    """Normalize a manifest list to sorted ``(key, value)`` pairs."""
    return sorted((str(i.get(key, "")), str(i.get(value, ""))) for i in items)


def detect_changes(
    baseline: RunManifest,
    candidate: RunManifest,
    *,
    allow_adapter_change: bool = False,
) -> ChangeReport:
    """Detect adapter/model/oracle changes from a baseline to a candidate.

    Args:
        baseline: The baseline run's manifest.
        candidate: The candidate run's manifest.
        allow_adapter_change: When True, a deliberate driver/target swap is
            tolerated (not reported) — the ``--allow-adapter-change`` flag.

    Returns:
        A :class:`ChangeReport`; ``any`` is False only when nothing changed.
    """
    changes: list[RunChange] = []

    drivers_changed = _pairs(baseline.drivers, "type", "digest") != _pairs(
        candidate.drivers, "type", "digest"
    )
    targets_changed = _pairs(baseline.targets, "type", "digest") != _pairs(
        candidate.targets, "type", "digest"
    )
    adapter_changed = (drivers_changed or targets_changed) and not allow_adapter_change
    if adapter_changed:
        changed = "driver" if drivers_changed else "target"
        changes.append(
            RunChange(
                kind="adapter_changed",
                detail=f"{changed} digest differs between baseline and candidate",
            )
        )

    baseline_model = baseline.pins.get("model")
    candidate_model = candidate.pins.get("model")
    model_changed = baseline_model != candidate_model and (
        baseline_model is not None or candidate_model is not None
    )
    if model_changed:
        changes.append(
            RunChange(
                kind="model_changed",
                detail=f"model pin differs: {baseline_model!r} -> {candidate_model!r}",
            )
        )

    oracle_changed = _pairs(baseline.oracles, "name", "version") != _pairs(
        candidate.oracles, "name", "version"
    )
    if oracle_changed:
        changes.append(
            RunChange(
                kind="oracle_changed",
                detail="oracle versions differ; comparability invalidated (re-baseline)",
            )
        )

    return ChangeReport(
        adapter_changed=adapter_changed,
        model_changed=model_changed,
        oracle_changed=oracle_changed,
        changes=changes,
    )
