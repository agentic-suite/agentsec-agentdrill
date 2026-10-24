"""M15 15.3 — bounded adaptive orchestrator, F40 (RED → GREEN).

An adaptive case mutates a **documented** pattern from live responses. Hard
caps: provenance (`parent_pattern` + `mutation_summary` + `reviewer`),
`max_mutations`, cost ceiling, step depth; labelled `adaptive`; excluded from
golden-locked comparisons.
"""

from __future__ import annotations

import pytest

from agentdrill.chains import (
    AdaptiveCase,
    AdaptiveError,
    enforce_caps,
    is_golden_comparable,
    validate_adaptive,
)


def _case(**overrides: object) -> AdaptiveCase:
    base: dict[str, object] = {
        "id": "a1",
        "parent_pattern": "incident-register#1",
        "mutation_summary": "paraphrased the injected instruction",
        "reviewer": "reviewer@example",
        "mutation": "paraphrase",
        "max_mutations": 2,
        "step_depth": 3,
    }
    base.update(overrides)
    return AdaptiveCase(**base)  # type: ignore[arg-type]


def test_adaptive_case_requires_provenance() -> None:
    with pytest.raises(AdaptiveError, match="provenance"):
        validate_adaptive(_case(parent_pattern=""))
    with pytest.raises(AdaptiveError, match="provenance"):
        validate_adaptive(_case(reviewer=""))


def test_novel_mutation_is_rejected() -> None:
    with pytest.raises(AdaptiveError, match="mutation"):
        validate_adaptive(_case(mutation="new-capability"))


def test_a_documented_mutation_is_allowed() -> None:
    validate_adaptive(_case(mutation="encoding"))


def test_mutation_cap_enforced() -> None:
    with pytest.raises(AdaptiveError, match="mutations"):
        enforce_caps(_case(), mutations_used=3, cost_usd=0.0, depth=1)


def test_cost_ceiling_enforced() -> None:
    with pytest.raises(AdaptiveError, match="cost"):
        enforce_caps(_case(), mutations_used=1, cost_usd=99.0, depth=1)


def test_step_depth_cap_enforced() -> None:
    with pytest.raises(AdaptiveError, match="depth"):
        enforce_caps(_case(), mutations_used=1, cost_usd=0.0, depth=9)


def test_within_caps_passes() -> None:
    enforce_caps(_case(), mutations_used=2, cost_usd=0.5, depth=3)


def test_adaptive_is_excluded_from_golden_locked_comparisons() -> None:
    assert is_golden_comparable(_case()) is False
