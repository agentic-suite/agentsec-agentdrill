"""Dimension + divergence gating (M11 11.2).

``--fail-on compatibility|enforcement|integrity`` gates each dimension
independently (a blocked rate below the threshold fails);
``--fail-on-divergence critical`` fails on a critical deterministic-vs-judge
divergence. Design: ``docs/design/ci-gate.md`` §Gating.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel

from agentdrill.oracles.base import Verdict

#: Default per-dimension blocked-rate threshold.
DEFAULT_THRESHOLD = 0.8

#: Severity ranking for divergence gating.
_SEVERITY_RANK: dict[str, int] = {"warning": 0, "critical": 1}


class GateFailure(BaseModel):
    """A gating failure that should fail the CI gate."""

    kind: str
    dimension: str | None = None
    severity: str | None = None
    detail: str = ""


def check_gates(
    verdicts: Sequence[Verdict],
    *,
    fail_on: Iterable[str] = (),
    fail_on_divergence: str | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[GateFailure]:
    """Return the gating failures for ``verdicts``.

    Each dimension in ``fail_on`` is evaluated independently: its blocked rate
    across the verdicts carrying it must be at least ``threshold``. When
    ``fail_on_divergence`` is set, any divergence at or above that severity
    fails.
    """
    failures: list[GateFailure] = []

    for dimension in fail_on:
        relevant = [v for v in verdicts if dimension in v.dimensions]
        if not relevant:
            continue
        blocked = sum(1 for v in relevant if v.outcome == "blocked")
        rate = blocked / len(relevant)
        if rate < threshold:
            failures.append(
                GateFailure(
                    kind="dimension",
                    dimension=dimension,
                    detail=f"{dimension} blocked rate {rate:.2f} < {threshold}",
                )
            )

    if fail_on_divergence is not None:
        floor = _SEVERITY_RANK.get(fail_on_divergence, len(_SEVERITY_RANK))
        for verdict in verdicts:
            divergence = verdict.divergence
            if divergence is None:
                continue
            if _SEVERITY_RANK.get(divergence.severity, -1) >= floor:
                failures.append(
                    GateFailure(
                        kind="divergence",
                        severity=divergence.severity,
                        detail=divergence.detail or f"divergence on {verdict.case_id}",
                    )
                )
    return failures
