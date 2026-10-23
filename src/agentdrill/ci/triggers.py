"""Trigger watcher / CART (M11 11.4, F22).

Subscribe to config/policy/model/harness-change events; a change re-runs only
the **affected** packs (drift alerts are triggers too). Design:
``docs/design/ci-gate.md`` §Change-driven execution.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel

#: The kinds of change that trigger a re-run.
ChangeKind = Literal["config", "policy", "model", "harness", "drift"]


class ChangeEvent(BaseModel):
    """A change that may affect one or more packs."""

    kind: ChangeKind
    surface: str


class TriggerWatcher:
    """Maps a change event to the packs that must be re-run."""

    def __init__(self) -> None:
        self._bindings: dict[str, set[str]] = {}

    def register(self, pack_ref: str, surfaces: Iterable[str]) -> None:
        """Declare the surfaces a pack binds (its targets/tools/config)."""
        self._bindings.setdefault(pack_ref, set()).update(surfaces)

    def affected(self, event: ChangeEvent) -> list[str]:
        """The packs bound to ``event``'s surface, sorted (empty when none)."""
        return sorted(
            pack_ref for pack_ref, surfaces in self._bindings.items() if event.surface in surfaces
        )
