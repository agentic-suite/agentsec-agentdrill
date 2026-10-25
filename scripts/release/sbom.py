#!/usr/bin/env python3
"""CycloneDX 1.5 SBOM for agentdrill (M32 32.1).

Dependency-free and deterministic: reads the runtime dependencies declared in
``pyproject.toml``, resolves each to the version present in the build
environment, and emits a sorted CycloneDX JSON document. No timestamp, so the
same input always produces byte-identical output (checksummable).

Usage::

    python3 scripts/release/sbom.py --out dist/sbom.cdx.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")


def project_version(pyproject: Path) -> str:
    """The version declared in ``[project]``."""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def project_name(pyproject: Path) -> str:
    """The distribution name declared in ``[project]`` (single source of truth)."""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return str(data["project"]["name"])


def _purl(name: str, version: str) -> str:
    norm = name.lower().replace("_", "-")
    return f"pkg:pypi/{norm}@{version}" if version else f"pkg:pypi/{norm}"


def runtime_components(pyproject: Path) -> list[dict[str, str]]:
    """One CycloneDX component per declared runtime dependency, sorted by name."""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"].get("dependencies", [])
    components: list[dict[str, str]] = []
    for spec in sorted(deps):
        match = _NAME_RE.match(spec.strip())
        if not match:
            continue
        name = match.group(0)
        try:
            version = metadata.version(name)
        except metadata.PackageNotFoundError:
            version = ""
        components.append(
            {
                "type": "library",
                "name": name,
                "version": version,
                "purl": _purl(name, version),
            }
        )
    return components


def build_sbom(pyproject: Path | None = None) -> dict[str, object]:
    """A CycloneDX 1.5 document for agentdrill + its runtime dependencies."""
    pyproject = pyproject or (REPO / "pyproject.toml")
    version = project_version(pyproject)
    name = project_name(pyproject)
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "tools": [{"vendor": "agentdrill", "name": "sbom.py", "version": version}],
            "component": {
                "type": "application",
                "name": name,
                "version": version,
                "purl": _purl(name, version),
            },
        },
        "components": runtime_components(pyproject),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="SBOM output path (JSON)")
    ap.add_argument("--pyproject", default=None)
    args = ap.parse_args(argv)

    doc = build_sbom(Path(args.pyproject) if args.pyproject else None)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    root = doc["metadata"]["component"]  # type: ignore[index]
    print(
        f"sbom: {root['name']} {root['version']} "
        f"+ {len(doc['components'])} component(s) -> {out}"  # type: ignore[arg-type]
    )
    if not doc["components"]:
        print("sbom: FATAL no runtime components resolved", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
