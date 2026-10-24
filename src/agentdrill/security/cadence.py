"""CI cadence for the self-attack suites (M14 14.4).

The evasion pack, drill-the-drill meta-verification and the dark holdout must
run **every** release cycle; a missing or red suite fails the cadence, and the
results are published. Design: ``docs/design/threat-model.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from pydantic import BaseModel, Field

#: The suites that must run every release cycle.
CADENCE_SUITES: tuple[str, ...] = ("evasion", "meta", "holdout")

#: A suite runner: returns True when the suite is green.
SuiteRunner = Callable[[], bool]


class CadenceError(ValueError):
    """Raised when a required self-attack suite is missing or red."""


class CadenceResult(BaseModel):
    """The result of one release-cycle cadence run."""

    release: str
    suites: dict[str, bool] = Field(default_factory=dict)

    @property
    def all_green(self) -> bool:
        """Whether every required suite ran and is green."""
        return all(self.suites.get(suite, False) for suite in CADENCE_SUITES)


def plan_cadence(release: str) -> list[str]:
    """The suites a release cycle must run (always the full set)."""
    return list(CADENCE_SUITES)


def run_cadence(release: str, runners: Mapping[str, SuiteRunner]) -> CadenceResult:
    """Run each required suite and record its result.

    Raises:
        CadenceError: A required suite has no runner.
    """
    missing = [suite for suite in CADENCE_SUITES if suite not in runners]
    if missing:
        raise CadenceError(
            f"cadence missing required suite(s): {missing}; required {list(CADENCE_SUITES)}"
        )
    return CadenceResult(
        release=release,
        suites={suite: bool(runners[suite]()) for suite in CADENCE_SUITES},
    )


def require_cadence_green(result: CadenceResult) -> None:
    """Fail loudly unless every required suite ran and is green.

    Raises:
        CadenceError: A required suite is missing or red.
    """
    missing = [suite for suite in CADENCE_SUITES if suite not in result.suites]
    red = [suite for suite, green in result.suites.items() if not green]
    if missing or red:
        raise CadenceError(f"cadence failed for {result.release}: missing={missing} red={red}")


def publish_cadence(result: CadenceResult) -> dict[str, Any]:
    """The published cadence record for a release."""
    return {"release": result.release, "suites": dict(result.suites)}
