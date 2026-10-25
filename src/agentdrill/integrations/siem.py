"""SIEM/EDR detection validation (M26 26.6, R74).

After a drill, query the customer SIEM/EDR for the expected detection within a
**time budget** and report a per-case state — ``alerted`` / ``detected`` /
``logged`` / ``missed`` — plus the detection latency (CUJ-55). The SIEM is
injected behind a small protocol, so this is offline-testable and no SIEM
credentials live in the library. A query failure is **not** silently reported as
a miss: it fails loudly.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Literal, Protocol

from pydantic import BaseModel

#: The normalized per-case detection state, strongest first.
DetectionState = Literal["alerted", "detected", "logged", "missed"]

#: The default time budget (5 minutes) within which a detection is expected.
DEFAULT_SIEM_BUDGET_MS = 300_000


class SiemError(ValueError):
    """Raised when a SIEM query fails (never reported as a silent miss)."""


class SiemEvidence(BaseModel):
    """What the SIEM returned for one case (any subset may be present)."""

    alerted: bool = False
    detected: bool = False
    logged: bool = False
    latency_ms: float | None = None


class DetectionResult(BaseModel):
    """The per-case detection outcome and latency."""

    case_id: str
    state: DetectionState
    latency_ms: float | None
    within_budget: bool
    budget_ms: int


class SiemQuery(Protocol):
    """The injected SIEM/EDR query surface (implemented per customer)."""

    def query(self, case_id: str, *, since_ms: int, budget_ms: int) -> SiemEvidence:
        """Return the evidence for ``case_id`` witnessed since ``since_ms``."""
        ...


def strongest_state(evidence: SiemEvidence) -> DetectionState:
    """The strongest reported state (alert > detection > log > miss)."""
    if evidence.alerted:
        return "alerted"
    if evidence.detected:
        return "detected"
    if evidence.logged:
        return "logged"
    return "missed"


def validate_detection(
    cases: Sequence[str],
    siem: SiemQuery,
    *,
    since_ms: int,
    budget_ms: int = DEFAULT_SIEM_BUDGET_MS,
) -> list[DetectionResult]:
    """Query ``siem`` for each case and report its state + latency.

    Raises:
        SiemError: A query raised — a broken SIEM is not a detection miss.
    """
    results: list[DetectionResult] = []
    for case_id in cases:
        try:
            evidence = siem.query(case_id, since_ms=since_ms, budget_ms=budget_ms)
        except Exception as exc:
            raise SiemError(f"SIEM query failed for {case_id}: {exc}") from exc
        latency = evidence.latency_ms
        results.append(
            DetectionResult(
                case_id=case_id,
                state=strongest_state(evidence),
                latency_ms=latency,
                within_budget=latency is not None and latency <= budget_ms,
                budget_ms=budget_ms,
            )
        )
    return results


def summarize_detection(results: Sequence[DetectionResult]) -> dict[str, int]:
    """Count cases per state (all four keys present, zero when absent)."""
    summary: dict[str, int] = {"alerted": 0, "detected": 0, "logged": 0, "missed": 0}
    for result in results:
        summary[result.state] += 1
    return summary


def _percentile(values: Sequence[float], fraction: float) -> float:
    """A nearest-rank percentile of a non-empty ascending ``values``."""
    index = max(0, min(len(values) - 1, math.ceil(fraction * len(values)) - 1))
    return values[index]


def detection_latencies(results: Sequence[DetectionResult]) -> dict[str, float]:
    """The p50 / p95 / max detection latency over cases that reported one.

    Raises:
        SiemError: No case reported a latency.
    """
    latencies = sorted(
        result.latency_ms for result in results if result.latency_ms is not None
    )
    if not latencies:
        raise SiemError("no detection latency reported by the SIEM")
    return {
        "p50": _percentile(latencies, 0.50),
        "p95": _percentile(latencies, 0.95),
        "max": latencies[-1],
    }
