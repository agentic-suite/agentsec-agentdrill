"""M17 17.2 — standards tagging, F13 (RED → GREEN).

Every pack/attack carries a MITRE ATLAS + OWASP tag; lint requires them, so an
untagged pack is rejected.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdrill.interop import (
    TaggingError,
    has_atlas,
    has_owasp,
    untagged_cases,
    validate_tagging,
)
from agentdrill.models.attack_pack import AttackPack


def _pack(*tags: list[str]) -> AttackPack:
    cases = [
        {
            "id": f"c{i}",
            "title": "t",
            "goal": "g",
            "incident_ref": "incident-register#1",
            "target": {"type": "policyweave-output"},
            "driver": {"type": "subprocess"},
            "attack": {"steps": [{"tool": "shell"}]},
            "oracle": {"expect": "blocked"},
            "tags": t,
        }
        for i, t in enumerate(tags)
    ]
    return AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
            },
            "cases": cases,
        }
    )


def test_tagged_pack_passes() -> None:
    validate_tagging(_pack(["ATLAS-AML.T0051", "OWASP-LLM01"]))  # no raise


def test_untagged_pack_is_rejected() -> None:
    with pytest.raises(TaggingError, match="c0"):
        validate_tagging(_pack(["ATLAS-AML.T0051"]))  # missing OWASP
    with pytest.raises(TaggingError, match="c0"):
        validate_tagging(_pack(["OWASP-LLM01"]))  # missing ATLAS


def test_owasp_agentic_prefix_counts() -> None:
    assert has_owasp(["OWASP-AGENTIC-ASI01"]) is True
    assert has_atlas(["ATLAS-AML.T0051"]) is True
    assert has_atlas(["something"]) is False


def test_untagged_cases_lists_offenders() -> None:
    pack = _pack(["ATLAS-AML.T0051", "OWASP-LLM01"], ["prompt-injection"])
    assert untagged_cases(pack) == ["c1"]


def test_lint_requires_standards_tags() -> None:
    from agentdrill.registry import lint_pack

    fixtures = Path(__file__).parent / ".." / "packs" / "fixtures"
    result = lint_pack(_pack(["prompt-injection"]), fixtures_dir=fixtures, methodology="m")
    assert any(f.check == "standards" and not f.ok for f in result.findings)
