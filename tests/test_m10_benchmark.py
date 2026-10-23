"""M10 10.9 — benchmark publisher + PR submission (RED → GREEN).

Assemble the honest published table (rates with CIs, seeds, misses), export a
pinned bundle (`agentdrill benchmark export`), and verify a third party
reproduces the numbers (R4, F57).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdrill.reporting import (
    BenchmarkRelease,
    PackBenchmark,
    RateCI,
    SingleRunError,
    build_release,
    export_benchmark,
    reproduces,
)


def _rate(metric: str, point: float) -> RateCI:
    return RateCI(
        metric=metric, point=point, low=point - 0.05, high=point + 0.05, n=100, seeds=[1, 2, 3]
    )


def _pack(pack_ref: str = "p@1.0.0+deadbeef", blocked: float = 0.87) -> PackBenchmark:
    return PackBenchmark(
        pack_ref=pack_ref,
        seeds=[1, 2, 3],
        rates={"blocked": _rate("blocked", blocked), "missed": _rate("missed", 1 - blocked)},
        misses=["c2"],
    )


def _release() -> BenchmarkRelease:
    return build_release("v0.1.0", [_pack()], generated="2026-10-23T00:00:00Z")


def test_release_assembles_the_honest_table() -> None:
    release = _release()
    assert isinstance(release, BenchmarkRelease)
    assert release.packs[0].pack_ref == "p@1.0.0+deadbeef"
    assert release.packs[0].seeds == [1, 2, 3]
    assert release.packs[0].misses == ["c2"]


def test_single_seed_release_is_rejected() -> None:
    bad = PackBenchmark(pack_ref="p", seeds=[1], rates={"blocked": _rate("blocked", 1.0)})
    with pytest.raises(SingleRunError):
        build_release("v0.1.0", [bad])


def test_export_writes_a_pinned_bundle(tmp_path: Path) -> None:
    path = export_benchmark(_release(), tmp_path / "bench")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["release"] == "v0.1.0"
    assert data["packs"][0]["seeds"] == [1, 2, 3]
    assert "blocked" in data["packs"][0]["rates"]


def test_third_party_reproduction_matches_numbers() -> None:
    expected = _release()
    same = build_release("v0.1.0", [_pack()], generated="2026-10-24T00:00:00Z")
    assert reproduces(expected, same) is True


def test_reproduction_detects_a_number_change() -> None:
    expected = _release()
    changed = build_release("v0.1.0", [_pack(blocked=0.5)], generated="2026-10-24T00:00:00Z")
    assert reproduces(expected, changed) is False


def test_reproduction_detects_a_changed_miss_set() -> None:
    expected = _release()
    other = _pack()
    other.misses = []
    assert reproduces(expected, build_release("v0.1.0", [other])) is False
