"""Honesty rules for publishing a report (M10 10.2, R5).

A published report must disclose its misses (and degradations): the outcome
split has to equal the rows in the report. A run cannot publish with a miss
hidden. Design: ``docs/design/reporting.md`` §Honesty rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentdrill.reporting.model import Report
from agentdrill.reporting.render import render

#: The closed outcome vocabulary a report row may carry.
_KNOWN_OUTCOMES: tuple[str, ...] = ("blocked", "missed", "degraded")


class HonestyError(ValueError):
    """Raised when a report hides a miss/degradation or is otherwise dishonest."""


@dataclass
class HonestyCheck:
    """The result of a report's honesty check."""

    ok: bool
    problems: list[str] = field(default_factory=list)

    def require(self) -> None:
        """Raise :class:`HonestyError` unless the report is publishable."""
        if self.problems:
            raise HonestyError("report is not publishable: " + "; ".join(self.problems))


def check_honesty(report: Report) -> HonestyCheck:
    """Validate that ``report`` discloses every miss/degradation.

    The outcome split must equal the rows; unknown outcomes are rejected.
    """
    problems: list[str] = []
    counts: dict[str, int] = {}
    for row in report.rows:
        if row.outcome not in _KNOWN_OUTCOMES:
            problems.append(f"unknown outcome {row.outcome!r} (case {row.case_id})")
            continue
        counts[row.outcome] = counts.get(row.outcome, 0) + 1

    outcome = report.outcome
    declared = {
        "blocked": outcome.blocked,
        "missed": outcome.missed,
        "degraded": outcome.degraded,
    }
    for name, count in declared.items():
        actual = counts.get(name, 0)
        if count != actual:
            problems.append(
                f"{name} count {count} does not match {actual} row(s) — a {name} case "
                "is missing from the report"
            )
    return HonestyCheck(ok=not problems, problems=problems)


def publish(report: Report, fmt: str) -> str | bytes:
    """Validate ``report`` is honest, then render it in ``fmt``.

    Raises:
        HonestyError: The report hides a miss/degradation or has an unknown outcome.
    """
    check_honesty(report).require()
    return render(report, fmt)
