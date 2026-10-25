"""M32 32.7 — the compatibility dataset + AWC generator (adoption half)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
RELEASE = REPO / "scripts" / "release"
DATA = REPO / "docs" / "release" / "v0.1.0" / "compatibility-data.json"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, RELEASE / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


awc_mod = _load("awc")


def test_adoption_buckets_are_deterministic() -> None:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    buckets = doc["adoption_buckets"]
    assert awc_mod._adoption(61559, buckets) == 5
    assert awc_mod._adoption(43882, buckets) == 4
    assert awc_mod._adoption(22003, buckets) == 3
    assert awc_mod._adoption(999, buckets) == 1


def test_dataset_lists_the_eight_driven_frameworks() -> None:
    entries = awc_mod.load_entries(DATA)
    assert len(entries) == 8
    assert all(e.level == "L2" for e in entries)
    assert all(e.evidence for e in entries)  # L2+ must carry evidence


def test_report_surfaces_the_current_gaps() -> None:
    result = awc_mod.report(awc_mod.load_entries(DATA))
    assert result["awc"] == 0.5  # all L2
    assert result["awc_met"] is False
    assert result["open_l3_plus"] == []  # no harness is witnessed yet
