"""Reserved process exit codes (see ``docs/reference/errors.md``).

Resolution precedence, most severe wins:
critical miss (4) > config (2) > oracle infra (3) > miss (1) > pass (0).
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Reserved agentdrill process exit codes."""

    OK = 0
    MISS = 1
    CONFIG_ERROR = 2
    ORACLE_ERROR = 3
    CRITICAL_MISS = 4
    CRITICAL_DIVERGENCE = 5


# Ordered most-severe first so the first match is the winning code.
_PRECEDENCE: tuple[ExitCode, ...] = (
    ExitCode.CRITICAL_MISS,
    ExitCode.CRITICAL_DIVERGENCE,
    ExitCode.CONFIG_ERROR,
    ExitCode.ORACLE_ERROR,
    ExitCode.MISS,
    ExitCode.OK,
)


def resolve(*codes: ExitCode) -> ExitCode:
    """Return the most severe of ``codes`` per the documented precedence."""
    for code in _PRECEDENCE:
        if code in codes:
            return code
    return ExitCode.OK
