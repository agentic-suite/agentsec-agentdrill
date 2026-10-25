"""M11 11.2 — dimension + divergence gating (RED → GREEN).

`--fail-on compatibility|enforcement|integrity` gates each dimension
independently (blocked rate < 0.8 fails); `--fail-on-divergence critical`
fails on a critical deterministic-vs-judge divergence.
"""

from __future__ import annotations

from agentdrill.ci import GateFailure, check_gates
from agentdrill.oracles.base import Divergence, Verdict


def _v(case_id: str, outcome: str, dims: list[str], diverg: Divergence | None = None) -> Verdict:
    return Verdict(
        case_id=case_id,
        outcome=outcome,  # type: ignore[arg-type]
        dimensions=dims,  # type: ignore[arg-type]
        divergence=diverg,
    )


VERDICTS = [
    _v("c1", "blocked", ["enforcement"]),
    _v("c2", "missed", ["compatibility"]),
]


def test_each_dimension_gates_independently() -> None:
    compat = check_gates(VERDICTS, fail_on=["compatibility"])
    assert [f.dimension for f in compat] == ["compatibility"]
    enforcement = check_gates(VERDICTS, fail_on=["enforcement"])
    assert enforcement == []


def test_multiple_dimensions_report_each_failure() -> None:
    failures = check_gates(VERDICTS, fail_on=["compatibility", "enforcement"])
    assert len(failures) == 1
    assert isinstance(failures[0], GateFailure)
    assert failures[0].kind == "dimension"


def test_a_high_block_rate_passes_the_threshold() -> None:
    verdicts = [
        _v("c1", "blocked", ["enforcement"]),
        _v("c2", "blocked", ["enforcement"]),
        _v("c3", "blocked", ["enforcement"]),
        _v("c4", "missed", ["enforcement"]),  # 75% < 80%
    ]
    assert check_gates(verdicts, fail_on=["enforcement"]) != []


def test_no_fail_on_gates_nothing() -> None:
    assert check_gates(VERDICTS) == []


def test_critical_divergence_fails() -> None:
    verdicts = [_v("c1", "missed", ["enforcement"], Divergence(case_id="c1", severity="critical"))]
    failures = check_gates(verdicts, fail_on_divergence="critical")
    assert len(failures) == 1
    assert failures[0].kind == "divergence"


def test_warning_divergence_does_not_fail_a_critical_gate() -> None:
    verdicts = [_v("c1", "missed", ["enforcement"], Divergence(case_id="c1", severity="warning"))]
    assert check_gates(verdicts, fail_on_divergence="critical") == []
