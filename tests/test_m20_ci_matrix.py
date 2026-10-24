"""M20 20.4 — CI-matrix export, F72 (RED → GREEN).

`export ci --format github-actions|gitlab` emits the pack set + manifest +
attestation as a matrix; the emitted matrix passes a CI dry-run.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from agentdrill.cli.__main__ import main
from agentdrill.dx import (
    CI_FORMATS,
    CiMatrix,
    CiMatrixError,
    build_ci_matrix,
    render_ci_matrix,
    validate_ci_matrix,
)
from agentdrill.models.attack_pack import AttackPack


def _pack() -> AttackPack:
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
            "cases": [
                {
                    "id": "c1",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                }
            ],
        }
    )


def _matrix() -> CiMatrix:
    return build_ci_matrix(
        ["p@1.0.0+abc"],
        manifest={"hashes": {"attacker": "sha256:x"}},
        attestation={"policyweave-output": "fixture"},
    )


def test_ci_matrix_exports_pack_set_manifest_attestation() -> None:
    matrix = _matrix()
    assert isinstance(matrix, CiMatrix)
    assert matrix.packs == ["p@1.0.0+abc"]
    assert matrix.attestation == {"policyweave-output": "fixture"}


def test_matrix_passes_ci_dry_run() -> None:
    validate_ci_matrix(_matrix())  # no raise
    assert set(CI_FORMATS) == {"github-actions", "gitlab"}


def test_render_formats() -> None:
    assert "matrix" in render_ci_matrix(_matrix(), fmt="github-actions")
    assert "p@1.0.0+abc" in render_ci_matrix(_matrix(), fmt="gitlab")


def test_unknown_format_fails_loudly() -> None:
    with pytest.raises(CiMatrixError):
        render_ci_matrix(_matrix(), fmt="jenkins")


def test_export_ci_cli(tmp_path: Path) -> None:
    pack_file = tmp_path / "p.yaml"
    pack_file.write_text(yaml.safe_dump(_pack().model_dump()), encoding="utf-8")
    result = CliRunner().invoke(
        main, ["export", "ci", "--format", "github-actions", "--pack", str(pack_file)]
    )
    assert result.exit_code == 0, result.output
    assert "matrix" in result.output
