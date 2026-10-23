"""M9 9.3 — change detection (RED → GREEN).

Distinguish an adapter/model/oracle swap from a real regression. A swap is not
a regression; `--allow-adapter-change` tolerates a deliberate driver/target
swap; an oracle change invalidates comparability.
"""

from __future__ import annotations

from typing import Any

from agentdrill.comparison import ChangeReport, RunChange, detect_changes
from agentdrill.models.manifest import RunManifest

DRIVERS = [{"type": "subprocess", "digest": "d1"}]
TARGETS = [{"type": "policyweave-output", "digest": "t1"}]
ORACLES = [{"name": "deny", "version": "1.0.0"}]


def _manifest(
    *,
    drivers: list[dict[str, Any]] | None = None,
    targets: list[dict[str, Any]] | None = None,
    oracles: list[dict[str, Any]] | None = None,
    model: str = "judge-x",
) -> RunManifest:
    return RunManifest(
        run_id="r",
        drivers=DRIVERS if drivers is None else drivers,
        targets=TARGETS if targets is None else targets,
        oracles=ORACLES if oracles is None else oracles,
        pins={"seed": 7, "model": model},
    )


def test_no_changes_is_clean() -> None:
    report = detect_changes(_manifest(), _manifest())
    assert isinstance(report, ChangeReport)
    assert report.any is False
    assert report.adapter_changed is False
    assert report.model_changed is False
    assert report.oracle_changed is False


def test_driver_digest_change_is_an_adapter_change() -> None:
    report = detect_changes(
        _manifest(), _manifest(drivers=[{"type": "subprocess", "digest": "d2"}])
    )
    assert report.adapter_changed is True
    assert report.any is True
    assert any(c.kind == "adapter_changed" for c in report.changes)


def test_target_digest_change_is_an_adapter_change() -> None:
    report = detect_changes(
        _manifest(), _manifest(targets=[{"type": "policyweave-output", "digest": "t2"}])
    )
    assert report.adapter_changed is True


def test_allow_adapter_change_tolerates_a_swap() -> None:
    candidate = _manifest(drivers=[{"type": "subprocess", "digest": "d2"}])
    report = detect_changes(_manifest(), candidate, allow_adapter_change=True)
    assert report.adapter_changed is False
    assert report.any is False


def test_model_pin_change_is_a_model_change() -> None:
    report = detect_changes(_manifest(), _manifest(model="judge-y"))
    assert report.model_changed is True
    assert report.adapter_changed is False
    assert [c.kind for c in report.changes] == ["model_changed"]


def test_oracle_version_change_invalidates_comparability() -> None:
    report = detect_changes(_manifest(), _manifest(oracles=[{"name": "deny", "version": "2.0.0"}]))
    assert report.oracle_changed is True
    assert report.invalidates_comparability is True


def test_a_swap_is_not_a_regression() -> None:
    """A detected swap is reported as a change — distinct from a bare regression."""
    swap = detect_changes(_manifest(), _manifest(drivers=[{"type": "subprocess", "digest": "d2"}]))
    clean = detect_changes(_manifest(), _manifest())
    assert isinstance(swap.changes[0], RunChange)
    assert swap.any is True  # the flip is explained by a change
    assert clean.any is False  # with no change, an outcome flip is a real regression
