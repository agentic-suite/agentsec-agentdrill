"""M14 14.2 — drill-the-drill, F43 (RED → GREEN).

Adversarial cases against our **own oracle engine**: a vacuous no-op must not
score `blocked`; a must-block miss must exit non-zero; fixtures must intercept;
attestation/evidence forgery and severity gaming are caught.
"""

from __future__ import annotations

from agentdrill.attack_runner import CaseOutcome
from agentdrill.models.artifact import RunOutput, TrajectoryStep
from agentdrill.models.attack_pack import AttackCase
from agentdrill.oracles.base import Verdict
from agentdrill.security.meta_verification import (
    MetaFinding,
    check_fixtures_intercept,
    check_must_block_exits_nonzero,
    check_no_forged_attestation,
    check_no_severity_gaming,
    check_no_vacuous_block,
    require_meta_clean,
)


def _case(case_id: str = "c1", expect: str = "blocked") -> AttackCase:
    return AttackCase.model_validate(
        {
            "id": case_id,
            "title": "t",
            "goal": "g",
            "incident_ref": "incident-register#1",
            "target": {"type": "policyweave-output"},
            "driver": {"type": "subprocess"},
            "attack": {"steps": [{"tool": "shell"}]},
            "oracle": {"expect": expect},
        }
    )


def test_vacuous_noop_is_not_scored_blocked() -> None:
    vacuous = CaseOutcome()  # no trajectory, no output
    gamed = check_no_vacuous_block(vacuous, Verdict(case_id="c1", outcome="blocked"))
    assert isinstance(gamed, MetaFinding)
    assert gamed.gamed is True


def test_a_real_block_is_not_flagged() -> None:
    real = CaseOutcome(
        output=RunOutput(final="denied"),
        trajectory=[TrajectoryStep(type="tool_result", result={"denied": True})],
    )
    assert check_no_vacuous_block(real, Verdict(case_id="c1", outcome="blocked")).gamed is False


def test_must_block_miss_must_exit_nonzero() -> None:
    cases = [_case("c1")]
    verdicts = [Verdict(case_id="c1", outcome="missed")]
    finding = check_must_block_exits_nonzero(cases, verdicts)
    assert finding.gamed is False  # the gate exits non-zero (4) — not gamed


def test_a_silent_pass_gate_is_gamed() -> None:
    # a gate that reports OK while a must-block case missed is gaming
    finding = check_must_block_exits_nonzero([_case("c1")], [], forced_exit_code=0)
    assert finding.gamed is True


def test_fixtures_must_intercept() -> None:
    assert check_fixtures_intercept(live_calls=0, fixture_used=True).gamed is False
    assert check_fixtures_intercept(live_calls=2, fixture_used=True).gamed is True


def test_forged_attestation_is_caught() -> None:
    assert check_no_forged_attestation(claimed="live", actual="mock").gamed is True
    assert check_no_forged_attestation(claimed="live", actual="live").gamed is False


def test_severity_gaming_is_caught() -> None:
    # the rubric says critical; claiming low is gaming
    gamed = check_no_severity_gaming(
        claimed="low", attack_class="destructive", exposure="privileged"
    )
    assert gamed.gamed is True
    honest = check_no_severity_gaming(
        claimed="critical", attack_class="destructive", exposure="privileged"
    )
    assert honest.gamed is False


def test_require_meta_clean_raises_on_a_gamed_finding() -> None:
    from agentdrill.security.meta_verification import MetaVerificationError

    gamed = check_no_forged_attestation(claimed="live", actual="mock")
    import pytest

    with pytest.raises(MetaVerificationError):
        require_meta_clean([gamed])
