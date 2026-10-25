"""M23 23.2 — FS + network witnesses, F87 (RED → GREEN).

Canary file/dir hash+inode watcher; loopback sinkhole (HTTP/DNS/TCP) with
per-run tokens. Effects are seen when they happen; overhead is small.
"""

from __future__ import annotations

from pathlib import Path

from agentdrill.witness import (
    CanaryWatch,
    Sinkhole,
    file_fingerprint,
    measure_overhead,
    watch_canary,
)


def test_canary_file_change_is_seen(tmp_path: Path) -> None:
    canary = tmp_path / "canary.txt"
    canary.write_text("original")
    before = file_fingerprint(canary)
    canary.write_text("modified")
    after = file_fingerprint(canary)
    watch = watch_canary(str(canary), before=before, after=after)
    assert isinstance(watch, CanaryWatch)
    assert watch.changed is True


def test_an_unchanged_canary_is_not_changed(tmp_path: Path) -> None:
    canary = tmp_path / "canary.txt"
    canary.write_text("same")
    fp = file_fingerprint(canary)
    assert watch_canary(str(canary), before=fp, after=fp).changed is False


def test_sinkhole_records_hits_with_a_per_run_token() -> None:
    sink = Sinkhole(token="per-run-abc")  # noqa: S106 - a test fixture token, not a secret
    assert "per-run-abc" in sink.url("http")
    sink.record("GET /")
    assert sink.hits == ["GET /"]


def test_overhead_is_under_two_seconds() -> None:
    assert measure_overhead(lambda: None) < 2.0
