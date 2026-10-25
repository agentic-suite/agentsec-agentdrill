"""M14 14.4 — CI cadence (RED → GREEN).

Evasion + meta-verification + dark holdout run **every** release cycle, and
their results are published.
"""

from __future__ import annotations

import pytest

from agentdrill.security.cadence import (
    CADENCE_SUITES,
    CadenceError,
    CadenceResult,
    plan_cadence,
    publish_cadence,
    require_cadence_green,
    run_cadence,
)


def _green() -> dict[str, object]:
    return {suite: (lambda: True) for suite in CADENCE_SUITES}


def test_cadence_requires_the_three_suites() -> None:
    assert set(plan_cadence("v0.1.0")) == {"evasion", "meta", "holdout"}
    assert set(CADENCE_SUITES) == {"evasion", "meta", "holdout"}


def test_run_cadence_records_each_suites_result() -> None:
    result = run_cadence("v0.1.0", _green())
    assert isinstance(result, CadenceResult)
    assert result.all_green is True
    assert set(result.suites) == {"evasion", "meta", "holdout"}


def test_a_missing_suite_fails_the_cadence() -> None:
    runners = _green()
    del runners["meta"]
    with pytest.raises(CadenceError, match="meta"):
        run_cadence("v0.1.0", runners)


def test_a_red_suite_fails_the_cadence() -> None:
    runners = _green()
    runners["holdout"] = lambda: False
    with pytest.raises(CadenceError, match="holdout"):
        require_cadence_green(run_cadence("v0.1.0", runners))


def test_all_green_passes() -> None:
    require_cadence_green(run_cadence("v0.1.0", _green()))  # no raise


def test_results_are_published() -> None:
    published = publish_cadence(run_cadence("v0.1.0", _green()))
    assert published["release"] == "v0.1.0"
    assert published["suites"] == {"evasion": True, "meta": True, "holdout": True}
