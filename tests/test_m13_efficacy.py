"""M13 13.1 — efficacy run against an unguarded twin (F59) (RED → GREEN).

A case is efficacy-verified only if the attack **succeeds unguarded**. Every
enforced case must have an unguarded success behind it.
"""

from __future__ import annotations

import pytest

from agentdrill.efficacy import (
    EfficacyError,
    EfficacyResult,
    require_efficacy_backed,
    run_efficacy,
)


def test_unguarded_success_verifies_efficacy() -> None:
    result = run_efficacy("c1", unguarded=lambda: True, guarded_outcome="blocked")
    assert isinstance(result, EfficacyResult)
    assert result.unguarded_succeeded is True
    assert result.efficacy_verified is True
    assert result.inert is False


def test_unguarded_failure_is_not_verified() -> None:
    result = run_efficacy("c1", unguarded=lambda: False, guarded_outcome="blocked")
    assert result.efficacy_verified is False
    assert result.inert is True


def test_true_positive_is_unguarded_success_and_guarded_block() -> None:
    result = run_efficacy("c1", unguarded=lambda: True, guarded_outcome="blocked")
    assert result.efficacy_verified is True
    assert result.guarded_outcome == "blocked"


def test_unguarded_success_with_guarded_miss_is_a_real_miss() -> None:
    result = run_efficacy("c1", unguarded=lambda: True, guarded_outcome="missed")
    assert result.is_real_miss is True


def test_enforced_case_without_unguarded_success_fails_loudly() -> None:
    inert = run_efficacy("c1", unguarded=lambda: False, guarded_outcome="blocked")
    with pytest.raises(EfficacyError, match="c1"):
        require_efficacy_backed([inert])


def test_require_efficacy_backed_accepts_verified_results() -> None:
    ok = run_efficacy("c1", unguarded=lambda: True, guarded_outcome="blocked")
    require_efficacy_backed([ok])  # no raise


def test_efficacy_result_round_trips() -> None:
    result = run_efficacy("c1", unguarded=lambda: True, guarded_outcome="blocked")
    assert EfficacyResult.model_validate_json(result.model_dump_json()) == result
