"""M27 27.1 — trace backtest (RED → GREEN).

Replay redacted agentwatch sessions against a candidate policy and classify each
session: ``unchanged`` / ``newly_blocked`` (a benign cluster) / ``regression`` /
``un_replayable`` (itemized, never ignored), with a replay-fidelity gate (≥99 %).
"""

from __future__ import annotations

import pytest

from agentdrill.backtest import (
    BacktestError,
    BacktestReport,
    RecordedSession,
    backtest,
    require_fidelity,
)
from agentdrill.evidence import AgentWatchEvent


class _Policy:
    """A candidate policy: blocks the given refs, allows everything else."""

    def __init__(self, blocked_refs: set[str]) -> None:
        self._blocked = blocked_refs

    def decide(self, event: AgentWatchEvent) -> bool:
        return event.ref not in self._blocked


def _sessions() -> list[RecordedSession]:
    return [
        RecordedSession(
            session_id="s-unchanged",
            events=[AgentWatchEvent(event="policy-fired", ref="read_file")],
        ),
        RecordedSession(
            session_id="s-newly-blocked",
            events=[AgentWatchEvent(event="policy-fired", ref="list_dir")],
        ),
        RecordedSession(
            session_id="s-regression",
            events=[AgentWatchEvent(event="denied", ref="exfil")],
        ),
        RecordedSession(
            session_id="s-un-replayable",
            replayable=False,
            un_replayable_reason="unknown schema v0",
        ),
    ]


def test_backtest_classifies_every_session() -> None:
    policy = _Policy(blocked_refs={"list_dir"})
    report = backtest(_sessions(), policy)
    assert isinstance(report, BacktestReport)
    labels = {v.session_id: v.label for v in report.verdicts}
    assert labels == {
        "s-unchanged": "unchanged",
        "s-newly-blocked": "newly_blocked",
        "s-regression": "regression",
        "s-un-replayable": "un_replayable",
    }
    assert report.total == 4
    assert report.unchanged == 1
    assert report.newly_blocked == 1
    assert report.regressions == 1
    assert report.un_replayable == 1


def test_newly_blocked_sessions_are_clustered() -> None:
    policy = _Policy(blocked_refs={"list_dir"})
    report = backtest(_sessions(), policy)
    assert report.clusters == {"list_dir": 1}


def test_un_replayable_sessions_are_itemized_not_ignored() -> None:
    report = backtest(_sessions(), _Policy(blocked_refs=set()))
    assert report.un_replayable_sessions == ["s-un-replayable"]


def test_fidelity_and_gate() -> None:
    report = backtest(_sessions(), _Policy(blocked_refs=set()))
    assert report.replayable == 3
    assert report.fidelity == pytest.approx(0.75)
    with pytest.raises(BacktestError):
        require_fidelity(report)  # default minimum 0.99
    require_fidelity(report, minimum=0.5)

    clean = backtest(_sessions()[:3], _Policy(blocked_refs=set()))
    assert clean.fidelity == 1.0
    require_fidelity(clean)


def test_regression_dominates_a_mixed_session() -> None:
    session = RecordedSession(
        session_id="mixed",
        events=[
            AgentWatchEvent(event="policy-fired", ref="list_dir"),  # newly blocked
            AgentWatchEvent(event="denied", ref="exfil"),  # regression
        ],
    )
    report = backtest([session], _Policy(blocked_refs={"list_dir"}))
    assert report.verdicts[0].label == "regression"
    assert "exfil" in report.verdicts[0].detail


def test_empty_backtest_is_safe() -> None:
    report = backtest([], _Policy(blocked_refs=set()))
    assert report.total == 0
    assert report.fidelity == 1.0
