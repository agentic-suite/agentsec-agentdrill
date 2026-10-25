#!/usr/bin/env python3
"""Generate the v0.1.0 compatibility table numbers: AWC + policy checks (M32 32.7).

Reads ``docs/release/v0.1.0/compatibility-data.json`` (adoption buckets + measured
levels), builds the platform matrix, and reports the graded rows, the
**adoption-weighted coverage (AWC)**, and the reference-harness policy result.
Fails loudly when a row claims L2+ without evidence, or when a gate is unmet.

Usage::

    python3 scripts/release/awc.py [--data PATH] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from agentdrill.platform.matrix import (  # noqa: E402
    LEVELS,
    MIN_AWC,
    MIN_REFERENCE_HARNESSES,
    PlatformEntry,
    PlatformError,
    awc,
    require_levels,
    require_reference_harnesses,
)


def _adoption(stars: int, buckets: list[dict[str, int]]) -> int:
    for bucket in sorted(buckets, key=lambda b: -b["min_stars"]):
        if stars >= bucket["min_stars"]:
            return int(bucket["value"])
    return 1


def load_entries(data_path: Path) -> list[PlatformEntry]:
    doc = json.loads(data_path.read_text(encoding="utf-8"))
    buckets = doc["adoption_buckets"]
    return [
        PlatformEntry(
            name=row["name"],
            surface=row.get("surface", "framework-sdk"),
            level=row["level"],
            open_source=bool(row.get("open_source")),
            adoption=_adoption(int(row["stars"]), buckets),
            evidence=list(row.get("evidence", [])),
        )
        for row in doc["platforms"]
    ]


def report(entries: list[PlatformEntry]) -> dict[str, object]:
    coverage = awc(entries)
    open_l3 = [
        e.name
        for e in entries
        if e.open_source and LEVELS.index(e.level) >= LEVELS.index("L3")
    ]
    return {
        "awc": round(coverage, 4),
        "awc_min": MIN_AWC,
        "awc_met": coverage >= MIN_AWC,
        "open_l3_plus": sorted(open_l3),
        "reference_harnesses_min": MIN_REFERENCE_HARNESSES,
        "rows": [
            {"name": e.name, "level": e.level, "adoption": e.adoption, "open": e.open_source}
            for e in entries
        ],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=str(REPO / "docs/release/v0.1.0/compatibility-data.json"))
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = ap.parse_args(argv)

    entries = load_entries(Path(args.data))
    result = report(entries)

    problems: list[str] = []
    try:
        require_levels(entries)  # L2+ rows must carry evidence
    except PlatformError as exc:
        problems.append(str(exc))
    try:
        require_reference_harnesses(entries)
    except PlatformError as exc:
        problems.append(str(exc))
    if not result["awc_met"]:
        problems.append(f"AWC {result['awc']} < required {MIN_AWC}")

    if args.json:
        print(json.dumps({**result, "problems": problems}, indent=2, sort_keys=True))
    else:
        print("== compatibility (v0.1.0) ==")
        for row in result["rows"]:  # type: ignore[union-attr]
            print(f"  {row['level']}  adoption={row['adoption']}  {row['name']}")
        print(f"AWC: {result['awc']} (min {MIN_AWC}) -> "
              f"{'met' if result['awc_met'] else 'NOT MET'}")
        print(f"open-source at L3+: {result['open_l3_plus']} "
              f"(min {MIN_REFERENCE_HARNESSES})")
        for p in problems:
            print(f"  PROBLEM: {p}")
    return 1 if problems else 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
