"""M22 22.6 — self-observability (RED → GREEN).

A shareable run summary (dimensions + outcome split + exit code); one summary
answers "what happened".
"""

from __future__ import annotations

from agentdrill.hardening import RunSummary, build_summary
from agentdrill.oracles.base import Verdict


def _verdict(case_id: str, outcome: str, dims: list[str]) -> Verdict:
    return Verdict(case_id=case_id, outcome=outcome, dimensions=dims)  # type: ignore[arg-type]


VERDICTS = [
    _verdict("c1", "blocked", ["enforcement"]),
    _verdict("c2", "missed", ["enforcement", "integrity"]),
]


def test_run_summary_answers_what_happened() -> None:
    summary = build_summary("r1", verdicts=VERDICTS, exit_code=4)
    assert isinstance(summary, RunSummary)
    assert summary.outcome.blocked == 1
    assert summary.outcome.missed == 1
    assert summary.exit_code == 4
    rendered = summary.render()
    assert "blocked" in rendered
    assert "enforcement" in rendered
    assert "4" in rendered


def test_summary_dimensions_are_counted() -> None:
    summary = build_summary("r1", verdicts=VERDICTS, exit_code=0)
    assert summary.dimensions["enforcement"] == 2
    assert summary.dimensions["integrity"] == 1
