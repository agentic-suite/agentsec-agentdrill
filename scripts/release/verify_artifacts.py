#!/usr/bin/env python3
"""Independently verify released artifacts (M32 32.4).

Verifies a built ``dist/`` **from disk**, without trusting the build step:

  1. every artifact's SHA-256 matches ``SHA256SUMS``,
  2. every artifact is a subject of ``provenance.json`` with a matching digest,
  3. ``sbom.cdx.json`` is a valid CycloneDX document for this project,
  4. if ``gh`` is available and an attestation exists, the GitHub build
     attestation verifies (the keyless Sigstore signature produced in CI).

Signature *creation* is keyless and CI-only (``actions/attest-build-provenance``,
OIDC); this script never fabricates a signature. Exit non-zero on any failure.

Usage::

    python3 scripts/release/verify_artifacts.py [--dist dist] [--repo OWNER/REPO]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifacts(dist: Path) -> list[Path]:
    return sorted(p for p in dist.glob("*") if p.suffix in (".whl", ".gz"))


def verify_checksums(dist: Path) -> list[str]:
    problems: list[str] = []
    sums = dist / "SHA256SUMS"
    if not sums.exists():
        return [f"missing {sums.name}"]
    expected = {}
    for line in sums.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            expected[name.strip()] = digest
    for art in _artifacts(dist):
        if expected.get(art.name) != sha256(art):
            problems.append(f"{art.name}: checksum mismatch")
    return problems


def verify_provenance(dist: Path) -> list[str]:
    problems: list[str] = []
    prov = dist / "provenance.json"
    if not prov.exists():
        return ["missing provenance.json"]
    statement = json.loads(prov.read_text(encoding="utf-8"))
    if statement.get("predicateType") != "https://slsa.dev/provenance/v1":
        problems.append("provenance.predicateType is not SLSA v1")
    subjects = {s["name"]: s["digest"]["sha256"] for s in statement.get("subject", [])}
    for art in _artifacts(dist):
        actual = sha256(art)
        if subjects.get(art.name) != actual:
            problems.append(f"{art.name}: not bound by provenance (subject digest differs)")
    return problems


def verify_sbom(dist: Path) -> list[str]:
    sbom = dist / "sbom.cdx.json"
    if not sbom.exists():
        return ["missing sbom.cdx.json"]
    doc = json.loads(sbom.read_text(encoding="utf-8"))
    problems: list[str] = []
    if doc.get("bomFormat") != "CycloneDX":
        problems.append("sbom.bomFormat is not CycloneDX")
    if not doc.get("components"):
        problems.append("sbom has no components")
    return problems


def verify_attestation(dist: Path, repo: str) -> tuple[list[str], str]:
    """Verify the CI keyless attestation if the tool + artifact are available."""
    gh = shutil.which("gh")
    if gh is None:
        return ([], "skipped (gh not installed)")
    arts = _artifacts(dist)
    if not arts:
        return ([], "skipped (no artifacts)")
    problems: list[str] = []
    for art in arts:
        proc = subprocess.run(  # noqa: S603
            [gh, "attestation", "verify", str(art), "--repo", repo],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            problems.append(f"{art.name}: attestation did not verify")
    return (problems, "verified" if not problems else "FAILED")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dist", default=str(REPO_ROOT / "dist"))
    ap.add_argument("--repo", default="agentic-suite/agentsec-agentdrill")
    ap.add_argument(
        "--attestation",
        action="store_true",
        help="also verify the CI keyless attestation (needs a published release + network)",
    )
    args = ap.parse_args(argv)
    dist = Path(args.dist)

    integrity = verify_checksums(dist) + verify_provenance(dist) + verify_sbom(dist)
    attest_note = "skipped (pass --attestation to verify)"
    attest_problems: list[str] = []
    if args.attestation and not integrity:
        attest_problems, attest_note = verify_attestation(dist, args.repo)

    print(f"== verify artifacts ({dist}) ==")
    print(f"  artifacts: {len(_artifacts(dist))}")
    print(f"  integrity + provenance + sbom: {'OK' if not integrity else 'FAIL'}")
    print(f"  build attestation: {attest_note}")
    for problem in integrity + attest_problems:
        print(f"  PROBLEM: {problem}", file=sys.stderr)
    return 1 if (integrity or attest_problems) else 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
