"""Benchmark publisher + PR submission (M10 10.9, F57, R4).

Assemble the honest published table (rates with CIs, seeds, misses), export a
pinned bundle (``agentdrill benchmark export``) and verify a third party
reproduces the numbers. Design: ``docs/design/reporting.md`` §Submission.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from agentdrill.reporting.ci import RateCI
from agentdrill.reporting.stats import require_multi_seed


class PackBenchmark(BaseModel):
    """A pack's published benchmark: rates with CIs, seeds and misses."""

    pack_ref: str
    seeds: list[int]
    rates: dict[str, RateCI] = Field(default_factory=dict)
    misses: list[str] = Field(default_factory=list)
    manifest: dict[str, object] = Field(default_factory=dict)


class BenchmarkRelease(BaseModel):
    """A published benchmark release: a table per pack, bound to a manifest."""

    release: str
    generated: str
    packs: list[PackBenchmark] = Field(default_factory=list)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def build_release(
    release: str,
    packs: list[PackBenchmark],
    *,
    generated: str | None = None,
) -> BenchmarkRelease:
    """Assemble a benchmark release, rejecting any single-seed pack (F29).

    Raises:
        SingleRunError: A pack has fewer than 3 distinct pinned seeds.
    """
    for pack in packs:
        require_multi_seed(pack.seeds)
    return BenchmarkRelease(release=release, generated=generated or _now(), packs=list(packs))


def export_benchmark(release: BenchmarkRelease, dest: str | Path) -> Path:
    """Write the pinned benchmark bundle to ``dest/benchmark.json``.

    The bundle carries the packs, seeds, rates and misses so a third party can
    fork → run → submit (F57).
    """
    directory = Path(dest)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "benchmark.json"
    path.write_text(release.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def reproduces(
    expected: BenchmarkRelease, actual: BenchmarkRelease, *, tolerance: float = 1e-9
) -> bool:
    """Whether ``actual`` reproduces ``expected``'s numbers (and miss sets)."""
    expected_packs = {pack.pack_ref: pack for pack in expected.packs}
    actual_packs = {pack.pack_ref: pack for pack in actual.packs}
    if expected_packs.keys() != actual_packs.keys():
        return False
    for ref, wanted in expected_packs.items():
        got = actual_packs[ref]
        if sorted(wanted.misses) != sorted(got.misses):
            return False
        if set(wanted.rates) != set(got.rates):
            return False
        for metric, rate in wanted.rates.items():
            if abs(rate.point - got.rates[metric].point) > tolerance:
                return False
    return True
