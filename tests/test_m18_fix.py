"""M18 18.2 — remediation validation, F61 (RED → GREEN).

Every fixed miss becomes a permanent pinned regression case; `fix_decay` is
release-blocking with attribution — a decayed fix blocks the drift PR.
"""

from __future__ import annotations

import pytest

from agentdrill.lifecycle import (
    FIX_DECAY,
    FixCase,
    FixDecayError,
    attribute_decay,
    evaluate_fix,
    regression_case,
    require_fix_holds,
)


def test_fixed_miss_becomes_a_pinned_regression_case() -> None:
    case = regression_case("c1", fix_commit="abc123")
    assert isinstance(case, FixCase)
    assert case.pinned is True
    assert case.fix_commit == "abc123"


def test_a_holding_fix_is_not_decayed() -> None:
    case = regression_case("c1", fix_commit="abc123")
    held = evaluate_fix(case, observed_outcome="blocked")
    assert held.decayed is False


def test_a_decayed_fix_blocks_release() -> None:
    case = regression_case("c1", fix_commit="abc123")
    decayed = evaluate_fix(case, observed_outcome="missed")
    assert decayed.decayed is True
    with pytest.raises(FixDecayError, match="c1"):
        require_fix_holds([decayed])


def test_decay_attribution_names_the_fix_commit() -> None:
    case = evaluate_fix(regression_case("c1", fix_commit="abc123"), observed_outcome="missed")
    note = attribute_decay(case)
    assert FIX_DECAY in note
    assert "abc123" in note


def test_a_clean_set_does_not_block() -> None:
    case = evaluate_fix(regression_case("c1", fix_commit="abc"), observed_outcome="blocked")
    require_fix_holds([case])  # no raise
