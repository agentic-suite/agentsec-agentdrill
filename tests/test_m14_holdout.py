"""M14 14.3 — dark holdout, F33 (RED → GREEN).

A private, unpublished holdout subset per pack; published-set green + holdout
red is a pack-gaming finding and is release-blocking.
"""

from __future__ import annotations

import pytest

from agentdrill.security.holdout import (
    HoldoutRegistry,
    HoldoutResult,
    PackGamingError,
    check_holdout,
    require_no_gaming,
)


def test_published_green_and_holdout_red_is_gaming() -> None:
    result = check_holdout("p@1.0.0+aaa", published_green=True, holdout_green=False)
    assert isinstance(result, HoldoutResult)
    assert result.gaming is True


def test_both_green_is_not_gaming() -> None:
    assert check_holdout("p@1.0.0+aaa", published_green=True, holdout_green=True).gaming is False


def test_published_red_with_holdout_red_is_not_gaming() -> None:
    # a genuine failure, not gaming
    assert check_holdout("p@1.0.0+aaa", published_green=False, holdout_green=False).gaming is False


def test_holdout_gaming_blocks_release() -> None:
    gamed = check_holdout("p@1.0.0+aaa", published_green=True, holdout_green=False)
    with pytest.raises(PackGamingError, match="pack-gaming"):
        require_no_gaming([gamed])


def test_a_clean_run_does_not_block() -> None:
    require_no_gaming([check_holdout("p@1.0.0+aaa", published_green=True, holdout_green=True)])


def test_registry_keeps_the_holdout_subset_separate() -> None:
    registry = HoldoutRegistry()
    registry.register("p@1.0.0+aaa", ["secret-1", "secret-2"])
    assert registry.holdout_ids("p@1.0.0+aaa") == ["secret-1", "secret-2"]
    assert registry.holdout_ids("absent@1.0.0+bbb") == []
