"""Per-case cleanup (M13 13.4, F50).

Every case declares cleanup; it runs after every case — including failed and
timed-out ones. A cleanup failure is a **release-blocking ``dirty_target``**: a
dirty target makes every later number untrustworthy. Design:
``docs/design/efficacy.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from pydantic import BaseModel

#: The release-blocking finding raised when cleanup fails.
DIRTY_TARGET = "dirty_target"


class DirtyTargetError(ValueError):
    """Raised when a case left its target dirty (cleanup failed)."""


class CleanupResult(BaseModel):
    """The outcome of one case's cleanup."""

    case_id: str
    ran: bool
    succeeded: bool
    dirty: bool
    detail: str = ""


def run_cleanup(case_id: str, *, cleanup: Callable[[], bool]) -> CleanupResult:
    """Run ``cleanup``; a failure (or a raise) leaves the target dirty."""
    try:
        succeeded = bool(cleanup())
    except Exception as exc:  # a cleanup that raises is still a dirty target
        return CleanupResult(
            case_id=case_id,
            ran=True,
            succeeded=False,
            dirty=True,
            detail=f"cleanup raised: {exc}",
        )
    return CleanupResult(
        case_id=case_id,
        ran=True,
        succeeded=succeeded,
        dirty=not succeeded,
        detail="" if succeeded else f"{DIRTY_TARGET}: cleanup did not succeed",
    )


def cleanup_after_case(case_id: str, *, status: str, cleanup: Callable[[], bool]) -> CleanupResult:
    """Run cleanup after a case regardless of its ``status`` (timeout/error included)."""
    return run_cleanup(case_id, cleanup=cleanup)


def dirty_targets(results: Iterable[CleanupResult]) -> list[str]:
    """Case ids whose target was left dirty."""
    return [result.case_id for result in results if result.dirty]


def require_clean(results: Iterable[CleanupResult]) -> None:
    """Fail loudly (release-blocking) if any case left a dirty target.

    Raises:
        DirtyTargetError: One or more cases left the target dirty.
    """
    dirty = dirty_targets(results)
    if dirty:
        raise DirtyTargetError(
            f"{DIRTY_TARGET}: target left dirty by case(s): " + ", ".join(sorted(dirty))
        )
