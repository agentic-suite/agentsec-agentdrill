"""M29 29.4 — frontier class 4: identity, delegation & OAuth (RED → GREEN).

The frontier-class registry (each class ships as a pack class with twins +
witnesses + cleanup) and the class-4 acceptance: audience/passthrough rejection is
100 %; ASI coverage counts only efficacy-verified + witnessed categories.
"""

from __future__ import annotations

import pytest

from agentdrill.frontier import (
    ASI_CATEGORIES,
    FRONTIER_CLASSES,
    FrontierClass,
    FrontierError,
    asi_coverage,
    require_asi_coverage,
    require_audience_rejection,
    require_dual_use_signed,
)


def test_the_registry_knows_class_four() -> None:
    klass = FRONTIER_CLASSES[4]
    assert isinstance(klass, FrontierClass)
    assert klass.name.lower().startswith("identity")
    assert "ASI03" in klass.asi
    assert klass.atlas.startswith("ATLAS-")
    assert klass.validates


def test_there_are_ten_asi_categories() -> None:
    assert ASI_CATEGORIES == tuple(f"ASI{i:02d}" for i in range(1, 11))
    assert "ASI03" in ASI_CATEGORIES


def test_audience_and_passthrough_are_rejected_one_hundred_percent() -> None:
    require_audience_rejection(
        [("audience-mismatch", True), ("token-passthrough", True), ("cross-agent", True)]
    )
    with pytest.raises(FrontierError):
        require_audience_rejection([("audience-mismatch", True), ("token-passthrough", False)])


def test_asi_coverage_counts_verified_categories_only() -> None:
    assert asi_coverage(verified=["ASI03", "ASI03", "ASI06"]) == 2
    require_asi_coverage(verified=[f"ASI{i:02d}" for i in range(1, 7)])  # 6/10
    with pytest.raises(FrontierError):
        require_asi_coverage(verified=["ASI01", "ASI02", "ASI03"])


def test_dual_use_sign_off_is_required_per_class() -> None:
    klass = FRONTIER_CLASSES[4]
    with pytest.raises(FrontierError):
        require_dual_use_signed(klass)
    require_dual_use_signed(klass.model_copy(update={"dual_use_signed": True}))
