"""Cessation probe (M12 12.2).

Detection is not safety; **cessation is measured**. Drive the revoke, then
re-attempt the guarded action: if it still succeeds, the target is *not*
ceased (revoked but still acting). Design: ``docs/design/killchain.md``.
"""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel


class ProbeResult(BaseModel):
    """The outcome of a cessation probe.

    Attributes:
        case_id: The case the probe belongs to.
        reattempted: Whether the guarded action was re-attempted.
        action_succeeded: Whether the re-attempt still worked (damage continues).
        ceased: ``not action_succeeded`` — the measured cessation.
        detail: A human-readable record of what was re-attempted.
    """

    case_id: str
    reattempted: bool
    action_succeeded: bool
    ceased: bool
    detail: str = ""


def run_cessation_probe(
    case_id: str,
    *,
    revoke: Callable[[], None],
    reattempt: Callable[[], bool],
    action: str = "",
) -> ProbeResult:
    """Revoke, then re-attempt ``action``; ``ceased`` iff the re-attempt failed.

    Args:
        case_id: The case being probed.
        revoke: Drives the revoke (e.g. agenthalt/agentkeys).
        reattempt: Re-attempts the guarded action; returns ``True`` if it still
            succeeded (the target is still acting).
        action: A description of the guarded action, for the record.
    """
    revoke()
    action_succeeded = reattempt()
    ceased = not action_succeeded
    detail = f"re-attempted {action or 'the guarded action'} after revoke: " + (
        "still acting (not ceased)" if action_succeeded else "blocked (ceased)"
    )
    return ProbeResult(
        case_id=case_id,
        reattempted=True,
        action_succeeded=action_succeeded,
        ceased=ceased,
        detail=detail,
    )
