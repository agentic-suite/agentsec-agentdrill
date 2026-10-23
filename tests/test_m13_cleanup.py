"""M13 13.4 — per-case cleanup (F50) (RED → GREEN).

Cleanup runs after every case (including failed/timeout ones); a cleanup
failure is a release-blocking `dirty_target`.
"""

from __future__ import annotations

import pytest

from agentdrill.efficacy import (
    DIRTY_TARGET,
    CleanupResult,
    DirtyTargetError,
    cleanup_after_case,
    dirty_targets,
    require_clean,
    run_cleanup,
)


def test_cleanup_runs_and_reports_success() -> None:
    result = run_cleanup("c1", cleanup=lambda: True)
    assert isinstance(result, CleanupResult)
    assert result.ran is True
    assert result.succeeded is True
    assert result.dirty is False


def test_cleanup_failure_is_dirty_target() -> None:
    result = run_cleanup("c1", cleanup=lambda: False)
    assert result.dirty is True
    assert dirty_targets([result]) == ["c1"]
    assert DIRTY_TARGET == "dirty_target"


def test_cleanup_that_raises_is_dirty_but_ran() -> None:
    def boom() -> bool:
        raise RuntimeError("rm failed")

    result = run_cleanup("c1", cleanup=boom)
    assert result.ran is True
    assert result.dirty is True
    assert "rm failed" in result.detail


def test_cleanup_runs_even_after_a_timeout_case() -> None:
    calls: list[str] = []
    cleanup_after_case("c1", status="timeout", cleanup=lambda: calls.append("cleanup") or True)
    assert calls == ["cleanup"]


def test_dirty_target_blocks_release() -> None:
    dirty = run_cleanup("c1", cleanup=lambda: False)
    with pytest.raises(DirtyTargetError, match="c1"):
        require_clean([dirty])


def test_a_clean_run_does_not_block() -> None:
    require_clean([run_cleanup("c1", cleanup=lambda: True)])  # no raise
