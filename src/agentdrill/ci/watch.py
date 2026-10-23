"""Local watch mode (M11 11.5, F68).

Poll watched files; on a change, return the affected packs so the dev loop can
re-run just those (``agentdrill watch``). Design: ``docs/design/ci-gate.md``
§Change-driven execution.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from agentdrill.ci.triggers import ChangeEvent, TriggerWatcher


def snapshot_paths(paths: Iterable[str | Path]) -> dict[str, float]:
    """Map each existing path to its mtime (a poll snapshot)."""
    snapshot: dict[str, float] = {}
    for path in paths:
        p = Path(path)
        if p.exists():
            snapshot[str(p)] = p.stat().st_mtime
    return snapshot


class LocalWatcher:
    """Detect file changes and return the affected packs (the dev loop).

    Args:
        watcher: The trigger watcher mapping surfaces to packs.
    """

    def __init__(self, watcher: TriggerWatcher) -> None:
        self._watcher = watcher
        self._last: dict[str, float] | None = None

    def poll(
        self,
        snapshot: Mapping[str, float],
        path_surfaces: Mapping[str, str],
    ) -> list[str]:
        """Compare ``snapshot`` to the previous poll; return affected packs.

        The first poll records a baseline (no events). A changed file whose
        path maps to a surface triggers that surface's packs.
        """
        if self._last is None:
            self._last = dict(snapshot)
            return []

        changed = [path for path, mtime in snapshot.items() if self._last.get(path) != mtime]
        self._last = dict(snapshot)

        events = [
            ChangeEvent(kind="config", surface=path_surfaces[path])
            for path in changed
            if path in path_surfaces
        ]
        affected: set[str] = set()
        for event in events:
            affected.update(self._watcher.affected(event))
        return sorted(affected)
