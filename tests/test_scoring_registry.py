"""Tests for Scorer ABC and registration registry."""

from __future__ import annotations

import pytest

from agentdrill.models.artifact import RunArtifact
from agentdrill.models.pack import Scenario
from agentdrill.scoring.base import Scorer
from agentdrill.scoring.registry import get_scorer, register_scorer
from agentdrill.scoring.result import ScoreResult


class _TestScorer(Scorer):
    name = "test_metric"
    category = "correctness"

    def score(
        self,
        artifact: RunArtifact,
        scenario: Scenario,
        metric_config: dict,
    ) -> ScoreResult:
        return ScoreResult(
            metric=self.name,
            score=0.5,
            threshold=0.8,
            passed=False,
            category=self.category,
            blocking=False,
            detail={},
            source="deterministic",
            error=None,
        )


def test_scorer_abc_enforces_name() -> None:
    with pytest.raises(TypeError):
        type("MissingName", (Scorer,), {})()


def test_register_scorer_decorator() -> None:
    registered = register_scorer(_TestScorer)
    assert registered is _TestScorer
    assert get_scorer("test_metric") is _TestScorer


def test_get_scorer_unknown_returns_none() -> None:
    assert get_scorer("nonexistent") is None


def test_get_scorer_via_alias() -> None:
    from agentdrill.scoring.registry import ALIASES

    ALIASES["spec_alias"] = "test_metric"
    assert get_scorer("spec_alias") is _TestScorer
    del ALIASES["spec_alias"]
