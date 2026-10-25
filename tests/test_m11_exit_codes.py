"""M11 11.1 — exit codes + `--ci` (RED → GREEN).

Structured codes: 0 pass · 1 miss · 2 config · 3 oracle infra · 4 critical miss
· 5 divergence. Resolution order: critical miss > config > oracle infra > miss
> pass. A must-block enforcement miss exits non-zero.
"""

from __future__ import annotations

from agentdrill.attack_runner import CaseOutcome
from agentdrill.ci import run_exit_code
from agentdrill.cli.exit_codes import ExitCode
from agentdrill.models.attack_pack import AttackCase, Oracle
from agentdrill.oracles.base import Verdict


def _case(case_id: str, expect: str = "blocked") -> AttackCase:
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


def _verdict(case_id: str, outcome: str) -> Verdict:
    return Verdict(case_id=case_id, outcome=outcome)  # type: ignore[arg-type]


def test_must_block_miss_exits_nonzero() -> None:
    code = run_exit_code([_case("c1")], [_verdict("c1", "missed")])
    assert code == ExitCode.CRITICAL_MISS
    assert int(code) != 0


def test_all_blocked_exits_zero() -> None:
    assert run_exit_code([_case("c1")], [_verdict("c1", "blocked")]) == ExitCode.OK


def test_degraded_must_block_is_a_miss() -> None:
    assert run_exit_code([_case("c1")], [_verdict("c1", "degraded")]) == ExitCode.MISS


def test_non_enforcement_expectation_mismatch_is_a_miss() -> None:
    # a benign twin expected to pass ("missed") but was over-blocked
    code = run_exit_code([_case("c1", expect="missed")], [_verdict("c1", "blocked")])
    assert code == ExitCode.MISS


def test_critical_miss_outranks_a_plain_miss() -> None:
    cases = [_case("c1", expect="missed"), _case("c2")]
    verdicts = [_verdict("c1", "blocked"), _verdict("c2", "missed")]
    assert run_exit_code(cases, verdicts) == ExitCode.CRITICAL_MISS


def test_config_error_outranks_oracle_error() -> None:
    code = run_exit_code([], [], config_error=True, oracle_error=True)
    assert code == ExitCode.CONFIG_ERROR


def test_oracle_error_outranks_a_miss() -> None:
    code = run_exit_code(
        [_case("c1", expect="missed")], [_verdict("c1", "blocked")], oracle_error=True
    )
    assert code == ExitCode.ORACLE_ERROR


def test_missing_verdict_is_skipped() -> None:
    assert run_exit_code([_case("c1")], []) == ExitCode.OK


def test_attacks_use_case_outcome_for_typing() -> None:
    # compile-time reminder that verdicts pair with observed CaseOutcomes
    assert isinstance(CaseOutcome(), CaseOutcome)
    assert Oracle(expect="blocked").expect == "blocked"
