"""M32 32.1 — release tooling: version consistency, SBOM, checksums, provenance.

Pure tests: no network, no packaging build. They exercise the functions the
``make release-dry-run`` path depends on.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
RELEASE = REPO / "scripts" / "release"
sys.path.insert(0, str(RELEASE))


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, RELEASE / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sbom = _load("sbom")
dry_run = _load("dry_run")


# --- version consistency ----------------------------------------------------
def test_version_consistency_returns_the_shared_version() -> None:
    version = dry_run.version_consistency()
    assert version == "0.1.0"


def test_version_consistency_rejects_a_mismatch(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\nversion = "1.0.0"\n', encoding="utf-8")
    init = tmp_path / "__init__.py"
    init.write_text('__version__ = "2.0.0"\n', encoding="utf-8")
    with pytest.raises(SystemExit):
        dry_run.version_consistency(pyproject, init)


# --- SBOM -------------------------------------------------------------------
def test_sbom_is_cyclonedx_with_the_project_and_deps() -> None:
    doc = sbom.build_sbom()
    assert doc["bomFormat"] == "CycloneDX"
    assert doc["specVersion"] == "1.5"
    root = doc["metadata"]["component"]
    assert root["name"] == "agentsec-agentdrill"
    assert root["version"] == "0.1.0"
    assert root["purl"] == "pkg:pypi/agentsec-agentdrill@0.1.0"
    names = [c["name"] for c in doc["components"]]
    assert names, "a release SBOM must list runtime components"
    assert names == sorted(names), "components must be sorted (deterministic)"
    assert all(c["purl"].startswith("pkg:pypi/") for c in doc["components"])
    assert "pydantic" in names


def test_sbom_is_deterministic() -> None:
    assert sbom.build_sbom() == sbom.build_sbom()


# --- checksums --------------------------------------------------------------
def _fake_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "agentdrill-0.1.0-py3-none-any.whl").write_bytes(b"wheel-bytes")
    (dist / "agentdrill-0.1.0.tar.gz").write_bytes(b"sdist-bytes")
    return dist


def test_checksums_round_trip(tmp_path: Path) -> None:
    dist = _fake_dist(tmp_path)
    sums = dry_run.write_checksums(dist)
    assert sums.name == "SHA256SUMS"
    dry_run.verify_checksums(dist)  # must not raise
    lines = sums.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert all(len(line.split()[0]) == 64 for line in lines)


def test_checksums_detect_tampering(tmp_path: Path) -> None:
    dist = _fake_dist(tmp_path)
    dry_run.write_checksums(dist)
    (dist / "agentdrill-0.1.0.tar.gz").write_bytes(b"tampered")
    with pytest.raises(SystemExit):
        dry_run.verify_checksums(dist)


def test_checksums_refuse_an_empty_dist(tmp_path: Path) -> None:
    dist = tmp_path / "empty"
    dist.mkdir()
    with pytest.raises(SystemExit):
        dry_run.write_checksums(dist)


# --- provenance -------------------------------------------------------------
def test_provenance_matches_the_artifacts(tmp_path: Path) -> None:
    dist = _fake_dist(tmp_path)
    out = dry_run.write_provenance(dist)
    statement = json.loads(out.read_text(encoding="utf-8"))
    assert statement["_type"] == "https://in-toto.io/Statement/v1"
    assert statement["predicateType"] == "https://slsa.dev/provenance/v1"
    subjects = {s["name"]: s["digest"]["sha256"] for s in statement["subject"]}
    for artifact in dry_run.artifacts(dist):
        assert subjects[artifact.name] == dry_run.sha256(artifact)
    assert statement["predicate"]["buildDefinition"]["externalParameters"]["version"] == "0.1.0"
