#!/usr/bin/env python3
"""M32 32.1 release dry-run: build + SBOM + checksums + provenance + verify.

Local mirror of the release steps in ``.github/workflows/release.yml`` *minus*
publishing and *minus* signing (signing needs the CI OIDC identity). It is the
``make release-dry-run`` entry point and must exit non-zero on any failure:

  1. version consistency (pyproject == ``agentdrill.__version__``)
  2. build the wheel + sdist (``python -m build``)
  3. SBOM (CycloneDX) for the built artifacts
  4. ``SHA256SUMS`` over every artifact
  5. an unsigned SLSA provenance statement (CI replaces it with a signed one)
  6. re-verify the checksums from disk

Usage::

    python3 scripts/release/dry_run.py [--dist dist] [--no-build]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbom import build_sbom  # noqa: E402


def version_consistency(pyproject: Path | None = None, init: Path | None = None) -> str:
    """Assert pyproject and ``__init__`` agree on the version; return it."""
    pyproject = pyproject or (REPO / "pyproject.toml")
    init = init or (REPO / "src" / "agentdrill" / "__init__.py")
    declared = str(tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"])
    source = ""
    for line in init.read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            source = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not source:
        raise SystemExit(f"FATAL: no __version__ in {init}")
    if declared != source:
        raise SystemExit(f"FATAL: version mismatch: pyproject {declared!r} != __init__ {source!r}")
    return declared


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifacts(dist: Path) -> list[Path]:
    """Release artifacts (wheel/sdist), sorted."""
    return sorted(p for p in dist.glob("*") if p.suffix in (".whl", ".gz"))


def write_checksums(dist: Path) -> Path:
    """Write ``SHA256SUMS`` (sha256sum format) over every artifact."""
    files = artifacts(dist)
    if not files:
        raise SystemExit(f"FATAL: no artifacts in {dist}")
    lines = [f"{sha256(p)}  {p.name}" for p in files]
    out = dist / "SHA256SUMS"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def verify_checksums(dist: Path) -> None:
    """Recompute the hashes from disk and compare with ``SHA256SUMS``."""
    sums = dist / "SHA256SUMS"
    if not sums.exists():
        raise SystemExit(f"FATAL: {sums} missing")
    expected = {}
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        expected[name.strip()] = digest
    actual = {p.name: sha256(p) for p in artifacts(dist)}
    if expected != actual:
        raise SystemExit(f"FATAL: checksum mismatch: {expected} != {actual}")


def write_provenance(dist: Path) -> Path:
    """An in-toto SLSA statement over the artifacts (unsigned; CI signs it)."""
    subjects = [
        {"name": p.name, "digest": {"sha256": sha256(p)}} for p in artifacts(dist)
    ]
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": subjects,
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://agentdrill/release@v1",
                "externalParameters": {"version": version_consistency()},
            },
            "runDetails": {
                "builder": {"id": "local-dry-run"},
                "metadata": {"note": "unsigned locally; signed in CI via the release workflow"},
            },
        },
    }
    out = dist / "provenance.json"
    out.write_text(json.dumps(statement, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def build(dist: Path) -> None:
    """Build the wheel + sdist into ``dist``."""
    dist.mkdir(parents=True, exist_ok=True)
    for stale in dist.glob("*"):
        stale.unlink()
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "build", "--outdir", str(dist)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"FATAL: python -m build failed (rc={proc.returncode})")


def write_sbom(dist: Path) -> Path:
    doc = build_sbom()
    out = dist / "sbom.cdx.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dist", default=str(REPO / "dist"))
    ap.add_argument("--no-build", action="store_true", help="reuse the existing dist/")
    args = ap.parse_args(argv)
    dist = Path(args.dist)

    version = version_consistency()
    print(f"release-dry-run: version {version} consistent")
    if not args.no_build:
        build(dist)
    sbom = write_sbom(dist)
    sums = write_checksums(dist)
    prov = write_provenance(dist)
    verify_checksums(dist)

    files = artifacts(dist)
    print(f"release-dry-run: {len(files)} artifact(s), sbom + checksums + provenance, verified")
    for p in files:
        print(f"  {p.name}  sha256={sha256(p)[:16]}...")
    for p in (sbom, sums, prov):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
