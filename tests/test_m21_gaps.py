"""M21 21.2 — predecessor gap closure G1-G14 (RED → GREEN).

Each gap is closed with a passing test, or waived with a written reason (G7
SQLite is waived by design).
"""

from __future__ import annotations

import pytest

from agentdrill.parity import (
    Gap,
    GapError,
    closed_gaps,
    default_gaps,
    validate_gaps,
    waived_gaps,
)


def test_all_fourteen_gaps_are_present() -> None:
    gaps = default_gaps()
    assert {gap.id for gap in gaps} == {f"G{i}" for i in range(1, 15)}


def test_every_gap_is_closed_or_waived_with_evidence() -> None:
    validate_gaps(default_gaps())  # no raise


def test_g7_is_waived_by_design() -> None:
    g7 = next(gap for gap in default_gaps() if gap.id == "G7")
    assert g7.status == "waived"
    assert "SQLite" in g7.evidence
    assert "G7" in {gap.id for gap in waived_gaps(default_gaps())}


def test_closed_gaps_have_test_evidence() -> None:
    for gap in closed_gaps(default_gaps()):
        assert gap.evidence


def test_a_gap_without_evidence_fails() -> None:
    bad = [Gap(id="GX", description="d", status="closed", evidence="")]
    with pytest.raises(GapError, match="GX"):
        validate_gaps(bad)
