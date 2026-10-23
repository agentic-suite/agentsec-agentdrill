"""M11 11.5 — local watch mode, F68 (RED → GREEN).

`agentdrill watch` re-runs the affected packs on file change (dev loop). The
poll detects a changed file and returns the affected packs within one save.
"""

from __future__ import annotations

from agentdrill.ci import LocalWatcher, TriggerWatcher, snapshot_paths


def _watcher() -> TriggerWatcher:
    watcher = TriggerWatcher()
    watcher.register("pack-a@1.0.0+aaa", ["policyweave-output"])
    watcher.register("pack-b@1.0.0+bbb", ["agenthalt"])
    return watcher


def test_first_poll_records_a_baseline() -> None:
    watch = LocalWatcher(_watcher())
    paths = {"/p/policy.yaml": "policyweave-output"}
    assert watch.poll({"/p/policy.yaml": 1.0}, paths) == []


def test_affected_packs_returned_within_one_save() -> None:
    watch = LocalWatcher(_watcher())
    paths = {"/p/policy.yaml": "policyweave-output"}
    watch.poll({"/p/policy.yaml": 1.0}, paths)  # baseline
    affected = watch.poll({"/p/policy.yaml": 2.0}, paths)  # one save later
    assert affected == ["pack-a@1.0.0+aaa"]


def test_an_unchanged_poll_returns_nothing() -> None:
    watch = LocalWatcher(_watcher())
    paths = {"/p/policy.yaml": "policyweave-output"}
    watch.poll({"/p/policy.yaml": 1.0}, paths)
    assert watch.poll({"/p/policy.yaml": 1.0}, paths) == []


def test_an_unmapped_file_change_affects_nothing() -> None:
    watch = LocalWatcher(_watcher())
    watch.poll({"/p/README.md": 1.0}, {})
    assert watch.poll({"/p/README.md": 2.0}, {}) == []


def test_snapshot_paths_reads_mtimes(tmp_path) -> None:
    file = tmp_path / "a.yaml"
    file.write_text("x")
    snap = snapshot_paths([file])
    assert str(file) in snap
    assert isinstance(snap[str(file)], float)


def test_watch_cli_once_exits_cleanly(tmp_path) -> None:
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    result = CliRunner().invoke(main, ["watch", "--once", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "affected" in result.output
