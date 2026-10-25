"""M11 11.4 — trigger watcher / CART, F22 (RED → GREEN).

Subscribe to config/policy/model/harness-change events; a change re-runs only
the affected packs (drift alerts are triggers too).
"""

from __future__ import annotations

from agentdrill.ci import ChangeEvent, TriggerWatcher


def _watcher() -> TriggerWatcher:
    watcher = TriggerWatcher()
    watcher.register("pack-a@1.0.0+aaa", ["policyweave-output", "shell"])
    watcher.register("pack-b@1.0.0+bbb", ["agenthalt"])
    watcher.register("pack-c@1.0.0+ccc", ["policyweave-output"])
    return watcher


def test_a_change_reruns_only_the_affected_set() -> None:
    affected = _watcher().affected(ChangeEvent(kind="config", surface="policyweave-output"))
    assert affected == ["pack-a@1.0.0+aaa", "pack-c@1.0.0+ccc"]


def test_a_policy_change_matches_by_surface() -> None:
    affected = _watcher().affected(ChangeEvent(kind="policy", surface="agenthalt"))
    assert affected == ["pack-b@1.0.0+bbb"]


def test_an_unbound_surface_affects_nothing() -> None:
    assert _watcher().affected(ChangeEvent(kind="model", surface="unknown")) == []


def test_a_drift_alert_is_a_trigger() -> None:
    affected = _watcher().affected(ChangeEvent(kind="drift", surface="shell"))
    assert affected == ["pack-a@1.0.0+aaa"]


def test_model_and_harness_changes_use_the_same_selection() -> None:
    watcher = _watcher()
    assert watcher.affected(ChangeEvent(kind="model", surface="shell")) == ["pack-a@1.0.0+aaa"]
    assert watcher.affected(ChangeEvent(kind="harness", surface="agenthalt")) == [
        "pack-b@1.0.0+bbb"
    ]
