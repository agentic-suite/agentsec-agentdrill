"""M20 20.3 — pack templates, F70 (RED → GREEN).

`init --template …` scaffolds oracle stubs, twins, cleanup and tags; a
template passes lint + the efficacy review.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdrill.dx import TEMPLATES, TemplateError, scaffold, scaffold_yaml
from agentdrill.registry import lint_pack


def _fixtures(tmp_path: Path, tools: list[str]) -> Path:
    d = tmp_path / "fixtures"
    d.mkdir(exist_ok=True)
    for tool in tools:
        (d / f"{tool}.json").write_text(json.dumps({"return": {"status": "ok"}}))
    return d


def test_every_template_scaffolds_a_pack() -> None:
    assert set(TEMPLATES) == {
        "mcp-poisoning",
        "exfil-chain",
        "destructive-command",
        "supply-chain",
    }
    for template in TEMPLATES:
        pack = scaffold(template, name=f"{template}-pack")
        assert pack.pack.name == f"{template}-pack"
        assert pack.cases


def test_a_template_passes_lint(tmp_path: Path) -> None:
    pack = scaffold("mcp-poisoning", name="p")
    tools = [step.tool for case in pack.cases for step in case.attack.steps]
    result = lint_pack(pack, fixtures_dir=_fixtures(tmp_path, tools), methodology="m")
    assert result.ok is True, result.findings


def test_a_template_has_a_benign_twin_for_efficacy() -> None:
    pack = scaffold("exfil-chain", name="p")
    attack = next(c for c in pack.cases if c.benign_twin)
    assert attack.benign_twin in {c.id for c in pack.cases}


def test_unknown_template_fails_loudly() -> None:
    with pytest.raises(TemplateError, match="template"):
        scaffold("cosmic", name="p")


def test_scaffold_yaml_is_renderable() -> None:
    text = scaffold_yaml("destructive-command", name="p")
    assert "destructive-command" in text
    assert "ATLAS-" in text and "OWASP-" in text
