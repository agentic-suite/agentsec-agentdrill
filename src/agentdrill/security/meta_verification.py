"""Drill-the-drill meta-verification (M14 14.2, F43).

Adversarial checks against our **own oracle engine**: a vacuous no-op must not
score ``blocked``, a must-block miss must exit non-zero, fixtures must
intercept, attestation/evidence forgery and severity gaming are caught. The
gate is itself drilled — a silent pass-everything gate is caught (predecessor
G10). Design: ``docs/design/threat-model.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel

from agentdrill.attack_runner import CaseOutcome
from agentdrill.ci.gate import run_exit_code
from agentdrill.models.attack_pack import AttackCase
from agentdrill.oracles.base import Verdict
from agentdrill.reporting.severity import rate_finding

#: Severity rank (lower = more severe).
_SEVERITY_RANK: dict[str, int] = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class MetaVerificationError(ValueError):
    """Raised when the oracle engine or gate can be gamed."""


class MetaFinding(BaseModel):
    """The outcome of one meta-verification check."""

    check: str
    gamed: bool
    detail: str = ""


def check_no_vacuous_block(observed: CaseOutcome, verdict: Verdict) -> MetaFinding:
    """A vacuous no-op (no trajectory, no output) must never score ``blocked``."""
    vacuous = not observed.trajectory and not (observed.output.final or "")
    gamed = vacuous and verdict.outcome == "blocked"
    return MetaFinding(
        check="no_vacuous_block",
        gamed=gamed,
        detail=(
            "a vacuous no-op scored 'blocked' — the scorer was fooled"
            if gamed
            else "no vacuous block"
        ),
    )


def check_must_block_exits_nonzero(
    cases: Sequence[AttackCase],
    verdicts: Sequence[Verdict],
    *,
    forced_exit_code: int | None = None,
) -> MetaFinding:
    """A must-block case that is not confirmed blocked must exit non-zero."""
    code = (
        int(forced_exit_code)
        if forced_exit_code is not None
        else int(run_exit_code(cases, verdicts))
    )
    by_id = {verdict.case_id: verdict for verdict in verdicts}
    unconfirmed = [
        case.id
        for case in cases
        if case.oracle.expect == "blocked"
        and (by_id.get(case.id) is None or by_id[case.id].outcome != "blocked")
    ]
    gamed = bool(unconfirmed) and code == 0
    return MetaFinding(
        check="must_block_exits_nonzero",
        gamed=gamed,
        detail=(
            f"gate exited 0 with unconfirmed must-block case(s): {unconfirmed}"
            if gamed
            else "must-block gate is non-zero"
        ),
    )


def check_fixtures_intercept(live_calls: int, fixture_used: bool) -> MetaFinding:
    """In fixture mode, no live call may occur — fixtures must intercept."""
    gamed = fixture_used and live_calls > 0
    return MetaFinding(
        check="fixtures_intercept",
        gamed=gamed,
        detail=(
            f"{live_calls} live call(s) in fixture mode — fixtures did not intercept"
            if gamed
            else "fixtures intercepted"
        ),
    )


def check_no_forged_attestation(claimed: str, actual: str) -> MetaFinding:
    """A claimed attestation must match the actual realness level."""
    gamed = claimed != actual
    return MetaFinding(
        check="no_forged_attestation",
        gamed=gamed,
        detail=(
            f"attestation forged: claimed {claimed!r}, actual {actual!r}"
            if gamed
            else "attestation honest"
        ),
    )


def check_no_severity_gaming(claimed: str, *, attack_class: str, exposure: str) -> MetaFinding:
    """A claimed severity may not be weaker than the rubric's."""
    rubric = rate_finding("probe", attack_class=attack_class, exposure=exposure).severity
    gamed = _SEVERITY_RANK.get(claimed, 99) > _SEVERITY_RANK.get(rubric, 0)
    return MetaFinding(
        check="no_severity_gaming",
        gamed=gamed,
        detail=(
            f"severity gamed: claimed {claimed!r}, rubric {rubric!r}"
            if gamed
            else "severity honest"
        ),
    )


def require_meta_clean(findings: Sequence[MetaFinding]) -> None:
    """Fail loudly if any meta-verification check found gaming.

    Raises:
        MetaVerificationError: One or more checks were gamed.
    """
    gamed = [finding.check for finding in findings if finding.gamed]
    if gamed:
        raise MetaVerificationError("oracle engine is gameable: " + ", ".join(sorted(gamed)))
