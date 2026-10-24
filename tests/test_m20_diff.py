"""M20 20.1 — pack diff, F67 (RED → GREEN).

`pack diff <a> <b>` reports the case + coverage delta; `list cases
--tag/--target/--difficulty` already selects.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner

from agentdrill.cli.__main__ import main
from agentdrill.dx import PackDiff, diff_packs
from agentdrill.models.attack_pack import AttackPack


def _case(case_id: str, *, goal: str = "g", tags: list[str] | None = None) -> dict:
    return {
        "id": case_id,
        "title": "t",
        "goal": goal,
        "incident_ref": "incident-register#1",
        "target": {"type": "policyweave-output"},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": "shell"}]},
        "oracle": {"expect": "blocked"},
        "tags": tags or ["ATLAS-AML.T0051", "OWASP-LLM01"],
    }


def _pack(*cases: dict) -> AttackPack:
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
            "cases": list(cases),
        }
    )


def test_diff_matches_the_case_delta() -> None:
    a = _pack(_case("c1"), _case("c2"))
    b = _pack(_case("c2"), _case("c3"))
    diff = diff_packs(a, b)
    assert isinstance(diff, PackDiff)
    assert diff.added == ["c3"]
    assert diff.removed == ["c1"]
    assert diff.changed == []


def test_diff_reports_a_changed_case() -> None:
    a = _pack(_case("c1", goal="old"))
    b = _pack(_case("c1", goal="new"))
    assert diff_packs(a, b).changed == ["c1"]


def test_diff_reports_a_coverage_delta() -> None:
    a = _pack(_case("c1", tags=["destructive"]))
    b = _pack(_case("c1", tags=["destructive"]), _case("c2", tags=["destructive"]))
    assert diff_packs(a, b).coverage_delta.get("destructive") == 1


def test_pack_diff_cli(tmp_path: Path) -> None:
    def _write(name: str, *cases: dict) -> Path:
        path = tmp_path / name
        path.write_text(yaml.safe_dump(_pack(*cases).model_dump()), encoding="utf-8")
        return path

    a = _write("a.yaml", _case("c1"))
    b = _write("b.yaml", _case("c2"))
    result = CliRunner().invoke(main, ["pack", "diff", str(a), str(b)])
    assert result.exit_code == 0, result.output
    assert "c2" in result.output
