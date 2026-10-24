"""M16 16.4 — contribution flow (RED → GREEN).

`init` scaffold → `pack lint` (schema, tags, incident_ref, oracle, fixtures,
methodology) → independent review → `pack publish` → `pack verify`. An
unreviewed pack cannot be benchmark-published.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry import (
    ContributionError,
    LintResult,
    ReviewDecision,
    lint_pack,
    require_publishable,
)


def _case(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "c1",
        "title": "t",
        "goal": "g",
        "incident_ref": "incident-register#1",
        "target": {"type": "policyweave-output"},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": "shell"}]},
        "oracle": {"expect": "blocked"},
        "tags": ["destructive"],
    }
    base.update(overrides)
    return base


def _pack(*cases: dict[str, object]) -> AttackPack:
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
            "cases": list(cases) or [_case()],
        }
    )


def _fixtures(tmp_path: Path) -> Path:
    d = tmp_path / "fixtures"
    d.mkdir()
    (d / "shell.json").write_text(json.dumps({"return": {"status": "ok"}}))
    return d


def test_lint_passes_a_complete_pack(tmp_path: Path) -> None:
    result = lint_pack(_pack(), fixtures_dir=_fixtures(tmp_path), methodology="docs/methodology.md")
    assert isinstance(result, LintResult)
    assert result.ok is True, result.findings


def test_lint_catches_missing_incident_ref(tmp_path: Path) -> None:
    result = lint_pack(
        _pack(_case(incident_ref="")), fixtures_dir=_fixtures(tmp_path), methodology="m"
    )
    assert result.ok is False
    assert any(f.check == "incident_ref" for f in result.findings if not f.ok)


def test_lint_catches_missing_tags(tmp_path: Path) -> None:
    result = lint_pack(_pack(_case(tags=[])), fixtures_dir=_fixtures(tmp_path), methodology="m")
    assert any(f.check == "tags" for f in result.findings if not f.ok)


def test_lint_catches_missing_fixture(tmp_path: Path) -> None:
    result = lint_pack(_pack(), fixtures_dir=tmp_path / "empty", methodology="m")
    assert any(f.check == "fixtures" for f in result.findings if not f.ok)


def test_lint_catches_missing_methodology(tmp_path: Path) -> None:
    result = lint_pack(_pack(), fixtures_dir=_fixtures(tmp_path), methodology=None)
    assert any(f.check == "methodology" for f in result.findings if not f.ok)


def test_unreviewed_pack_cannot_be_benchmark_published() -> None:
    with pytest.raises(ContributionError, match="review"):
        require_publishable("p@1.0.0+abc", trust="local", decisions=[])


def test_approved_pack_can_be_benchmark_published() -> None:
    decisions = [ReviewDecision(pack_ref="p@1.0.0+abc", reviewer="r", approved=True)]
    require_publishable("p@1.0.0+abc", trust="local", decisions=decisions)  # no raise


def test_external_pack_cannot_be_benchmark_published() -> None:
    decisions = [ReviewDecision(pack_ref="p@1.0.0+abc", reviewer="r", approved=True)]
    with pytest.raises(ContributionError, match="external"):
        require_publishable("p@1.0.0+abc", trust="external", decisions=decisions)
