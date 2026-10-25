"""Oracle registry + discovery (M6 work item 6.1).

Register oracles with ``@register_oracle`` or the ``agentdrill.oracles``
entry-point group. An unknown oracle name fails loudly with :class:`ConfigError`
at load — never a silent pass.
"""

from __future__ import annotations

import importlib.metadata
from collections.abc import Iterable
from typing import Any, Protocol

from agentdrill.models.errors import ConfigError
from agentdrill.oracles.base import Oracle

#: Entry-point group community oracles are discovered from.
ENTRY_POINT_GROUP = "agentdrill.oracles"

#: Registered oracles by name (the design calls this registry ``SCORERS``).
SCORERS: dict[str, type[Oracle]] = {}

#: Alias for readability at call sites.
ORACLES = SCORERS


class EntryPointLike(Protocol):
    """The subset of ``importlib.metadata.EntryPoint`` discovery needs."""

    name: str

    def load(self) -> Any: ...


def register_oracle(cls: type[Oracle]) -> type[Oracle]:
    """Register an oracle class under its ``name`` (usable as a decorator)."""
    if not cls.name:
        raise ConfigError(f"oracle {cls.__name__} must set a class-level name")
    SCORERS[cls.name] = cls
    return cls


def get_oracle(name: str) -> Oracle:
    """Return an instance of the oracle registered under ``name``.

    Raises:
        ConfigError: If no oracle is registered under ``name``.
    """
    oracle_cls = SCORERS.get(name)
    if oracle_cls is None:
        raise ConfigError(f"unknown oracle: {name!r}; registered: {sorted(SCORERS)}")
    return oracle_cls()


def discover(entry_points: Iterable[EntryPointLike] | None = None) -> list[str]:
    """Register community oracles from entry points; returns their names."""
    eps = (
        entry_points
        if entry_points is not None
        else importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)
    )
    registered: list[str] = []
    for entry_point in eps:
        register_oracle(entry_point.load())
        registered.append(str(entry_point.name))
    return registered
