"""M32 32.4 — independent artifact verification (integrity + provenance + SBOM)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

RELEASE = Path(__file__).resolve().parents[1] / "scripts" / "release"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, RELEASE / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dry_run = _load("dry_run")
verify = _load("verify_artifacts")


def _dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "agentsec_agentdrill-0.1.0-py3-none-any.whl").write_bytes(b"wheel")
    (dist / "agentsec_agentdrill-0.1.0.tar.gz").write_bytes(b"sdist")
    dry_run.write_checksums(dist)
    dry_run.write_provenance(dist)
    (dist / "sbom.cdx.json").write_text(
        json.dumps({"bomFormat": "CycloneDX", "specVersion": "1.5", "components": [{"name": "x"}]}),
        encoding="utf-8",
    )
    return dist


def test_verification_passes_on_a_good_dist(tmp_path: Path) -> None:
    dist = _dist(tmp_path)
    assert verify.verify_checksums(dist) == []
    assert verify.verify_provenance(dist) == []
    assert verify.verify_sbom(dist) == []


def test_verification_detects_a_tampered_artifact(tmp_path: Path) -> None:
    dist = _dist(tmp_path)
    (dist / "agentsec_agentdrill-0.1.0.tar.gz").write_bytes(b"tampered")
    assert verify.verify_checksums(dist)  # checksum mismatch
    assert verify.verify_provenance(dist)  # subject digest differs


def test_verification_reports_missing_files(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    assert verify.verify_checksums(empty) == ["missing SHA256SUMS"]
    assert verify.verify_provenance(empty) == ["missing provenance.json"]
    assert verify.verify_sbom(empty) == ["missing sbom.cdx.json"]
