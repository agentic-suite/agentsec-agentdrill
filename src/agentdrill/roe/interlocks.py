"""Safe-fire interlocks (M28 28.7, F97).

The safety layer that lets agentdrill run anywhere: a **global abort** that is
independent of the in-band agenthalt, a **dead-man switch** that trips on a lost
heartbeat, rate/cost **watchdogs**, **verified teardown** (reusing M13's
``dirty_target`` — release-blocking), and a **consent gate** for any attack
content leaving the machine. Design: ``docs/design/exposure-attestation-roe.md``;
PRD 35 (R71).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from agentdrill.efficacy.cleanup import CleanupResult, DirtyTargetError, require_clean

#: The default dead-man-switch timeout, in seconds.
DEFAULT_DEAD_MAN_SECONDS = 30.0


class InterlockError(ValueError):
    """Raised when an interlock refuses to keep firing."""


class AbortController:
    """A global abort, independent of the in-band agenthalt.

    The first abort wins (idempotent) so the reason is not overwritten.
    """

    def __init__(self) -> None:
        self._aborted = False
        self._reason: str | None = None

    def abort(self, *, reason: str) -> None:
        """Abort the run (idempotent — the first reason is kept)."""
        if not self._aborted:
            self._aborted = True
            self._reason = reason

    def is_aborted(self) -> bool:
        """Whether the run has been aborted."""
        return self._aborted

    @property
    def reason(self) -> str | None:
        """Why the run was aborted (``None`` before the first abort)."""
        return self._reason

    def require_running(self) -> None:
        """Fail loudly if the run was aborted.

        Raises:
            InterlockError: The run is aborted.
        """
        if self._aborted:
            raise InterlockError(f"run aborted: {self._reason}")


@dataclass
class DeadManSwitch:
    """A watchdog that trips when heartbeats stop."""

    timeout_seconds: float = DEFAULT_DEAD_MAN_SECONDS
    _last_beat: float | None = field(default=None, repr=False)

    def heartbeat(self, *, now: float) -> None:
        """Record a heartbeat at ``now`` (monotonic seconds)."""
        self._last_beat = now

    def is_tripped(self, *, now: float) -> bool:
        """Whether the switch has tripped (no heartbeat within the timeout)."""
        if self._last_beat is None:
            return False
        return (now - self._last_beat) > self.timeout_seconds

    def require_alive(self, *, now: float) -> None:
        """Fail loudly if the switch has tripped (lost heartbeat).

        Raises:
            InterlockError: The heartbeat was lost.
        """
        if self.is_tripped(now=now):
            raise InterlockError(
                f"dead-man switch tripped: no heartbeat for over {self.timeout_seconds}s"
            )


def check_rate_watchdog(*, rate: int, ceiling: int) -> None:
    """Fail loudly if the observed rate exceeds its ceiling.

    Raises:
        InterlockError: The rate is over the ceiling.
    """
    if rate > ceiling:
        raise InterlockError(f"rate watchdog: {rate} exceeds the ceiling {ceiling}")


def check_cost_watchdog(*, cost_usd: float, ceiling: float) -> None:
    """Fail loudly if the accrued cost exceeds its ceiling.

    Raises:
        InterlockError: The cost is over the ceiling.
    """
    if cost_usd > ceiling:
        raise InterlockError(f"cost watchdog: ${cost_usd} exceeds the ceiling ${ceiling}")


def verified_teardown(results: Iterable[CleanupResult]) -> None:
    """Fail loudly if any case left its target dirty (release-blocking).

    Reuses M13's ``dirty_target`` contract.

    Raises:
        InterlockError: One or more targets were left dirty.
    """
    try:
        require_clean(results)
    except DirtyTargetError as exc:
        raise InterlockError(str(exc)) from exc


def require_egress_consent(*, leaving_machine: bool, consented: bool) -> None:
    """Fail loudly when attack content would leave the machine without consent.

    Raises:
        InterlockError: Content would leave the machine without consent.
    """
    if leaving_machine and not consented:
        raise InterlockError(
            "refusing to send attack content off this machine without explicit consent"
        )
