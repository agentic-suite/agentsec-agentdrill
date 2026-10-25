"""CI gate — structured exit codes from a run (M11 11.1).

Maps a run's case verdicts to the reserved process exit codes
(0 pass · 1 miss · 2 config · 3 oracle infra · 4 critical miss ·
5 divergence), resolved most-severe-first. Design: ``docs/design/ci-gate.md``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from agentdrill.cli.exit_codes import ExitCode, resolve
from agentdrill.models.attack_pack import AttackCase
from agentdrill.oracles.base import Verdict


def run_exit_code(
    cases: Sequence[AttackCase],
    verdicts: Iterable[Verdict],
    *,
    config_error: bool = False,
    oracle_error: bool = False,
    divergence: bool = False,
) -> ExitCode:
    """Resolve the process exit code for a run.

    A must-block enforcement case (expected ``blocked``) that was ``missed`` is
    a **critical miss** (4); any other expectation mismatch is a **miss** (1).
    Config (2) and oracle-infra (3) errors are supplied by the caller; a
    critical divergence is code 5. Resolution is most-severe-first.

    Args:
        cases: The attack cases in the run.
        verdicts: The oracle verdicts for the run.
        config_error: A configuration error occurred.
        oracle_error: An oracle/judge infrastructure error occurred.
        divergence: A critical deterministic-vs-judge divergence occurred.
    """
    codes: list[ExitCode] = []
    if config_error:
        codes.append(ExitCode.CONFIG_ERROR)
    if oracle_error:
        codes.append(ExitCode.ORACLE_ERROR)
    if divergence:
        codes.append(ExitCode.CRITICAL_DIVERGENCE)

    by_id = {verdict.case_id: verdict for verdict in verdicts}
    for case in cases:
        verdict = by_id.get(case.id)
        if verdict is None:
            continue
        expected = case.oracle.expect
        if verdict.outcome == expected:
            continue
        if expected == "blocked" and verdict.outcome == "missed":
            codes.append(ExitCode.CRITICAL_MISS)
        else:
            codes.append(ExitCode.MISS)
    return resolve(*codes)
