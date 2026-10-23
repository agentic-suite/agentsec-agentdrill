"""M9 9.1 — golden expected results + golden-lock (RED → GREEN).

A golden is a preregistered, locked expected outcome per pack version (bound to
`pack@version+hash`). A candidate result differing from its golden is **flagged**
with a re-pin note — never silently corrected (DD-28).
"""

from __future__ import annotations

from agentdrill.comparison import Golden, GoldenCheck, check_golden


def _golden() -> Golden:
    return Golden.from_outcomes(
        pack_ref="p@1.0.0+deadbeef",
        outcomes={"c1": "blocked", "c2": "blocked"},
        tags={"c1": ["destructive"], "c2": ["secret"]},
    )


def test_golden_binds_to_pack_ref() -> None:
    golden = _golden()
    assert golden.pack_ref == "p@1.0.0+deadbeef"
    assert golden.locked is True
    assert [c.case_id for c in golden.cases] == ["c1", "c2"]


def test_golden_preregisters_expected_outcomes_and_tags() -> None:
    golden = _golden()
    by_id = {c.case_id: c for c in golden.cases}
    assert by_id["c1"].outcome == "blocked"
    assert by_id["c1"].tags == ["destructive"]


def test_identical_candidate_is_clean() -> None:
    result = check_golden(_golden(), {"c1": "blocked", "c2": "blocked"})
    assert isinstance(result, GoldenCheck)
    assert result.changed == []
    assert result.note is None
    assert result.ok is True


def test_undeclared_change_is_flagged() -> None:
    result = check_golden(_golden(), {"c1": "missed", "c2": "blocked"})
    assert [c.case_id for c in result.changed] == ["c1"]
    assert result.changed[0].golden_outcome == "blocked"
    assert result.changed[0].candidate_outcome == "missed"
    assert result.note is not None
    assert "c1" in result.note
    assert result.ok is False


def test_golden_is_locked_never_silently_corrected() -> None:
    golden = _golden()
    check_golden(golden, {"c1": "missed", "c2": "blocked"})
    by_id = {c.case_id: c for c in golden.cases}
    assert by_id["c1"].outcome == "blocked"  # unchanged by the check


def test_a_declared_repin_note_is_attached() -> None:
    result = check_golden(
        _golden(), {"c1": "missed", "c2": "blocked"}, declared_repin="re-pin declared: seed 7 -> 9"
    )
    assert result.note is not None
    assert "re-pin declared" in result.note
    assert result.changed  # still flagged — a declared re-pin never hides the change
