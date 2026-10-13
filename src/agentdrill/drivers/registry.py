"""Driver registry + plugin discovery (M4 work item 4.6).

Built-in drivers register on import; community drivers are discovered via the
``agentdrill.drivers`` entry-point group. An unknown name fails loudly with
:class:`ConfigError` (never a silent no-op). Each driver carries an
:class:`~agentdrill.models.adapter_manifest.AdapterManifest` whose SHA-256 digest
is bound into the run so a swap is detectable.
"""

from __future__ import annotations

import importlib.metadata
from collections.abc import Iterable
from typing import Any, Protocol

from agentdrill.drivers.base import Driver
from agentdrill.drivers.harness import ClaudeCodeDriver, CursorDriver
from agentdrill.drivers.http_driver import HttpDriver
from agentdrill.drivers.python_driver import PythonDriver
from agentdrill.drivers.subprocess_driver import SubprocessDriver
from agentdrill.models.adapter_manifest import AdapterManifest
from agentdrill.models.errors import ConfigError

#: Entry-point group community drivers are discovered from.
ENTRY_POINT_GROUP = "agentdrill.drivers"

#: Registered drivers by name.
DRIVERS: dict[str, type[Driver]] = {
    SubprocessDriver.name: SubprocessDriver,
    PythonDriver.name: PythonDriver,
    HttpDriver.name: HttpDriver,
    ClaudeCodeDriver.name: ClaudeCodeDriver,
    CursorDriver.name: CursorDriver,
}


class EntryPointLike(Protocol):
    """The subset of ``importlib.metadata.EntryPoint`` discovery needs."""

    name: str

    def load(self) -> Any: ...


def register(driver_cls: type[Driver]) -> str:
    """Register a driver class by its ``name``; returns the name."""
    name = driver_cls.name
    if not name:
        raise ConfigError(f"driver {driver_cls.__name__} must set a class-level name")
    DRIVERS[name] = driver_cls
    return name


def get_driver(name: str) -> Driver:
    """Return an instance of the driver registered under ``name``.

    Raises:
        ConfigError: If no driver is registered under ``name``.
    """
    driver_cls = DRIVERS.get(name)
    if driver_cls is None:
        raise ConfigError(f"unknown driver: {name!r}; registered: {sorted(DRIVERS)}")
    return driver_cls()


def discover(entry_points: Iterable[EntryPointLike] | None = None) -> list[str]:
    """Register community drivers from entry points; returns their names.

    Args:
        entry_points: Entry points to load. Defaults to the installed
            ``agentdrill.drivers`` group (empty when none are installed).
    """
    eps = (
        entry_points
        if entry_points is not None
        else importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)
    )
    registered: list[str] = []
    for entry_point in eps:
        register(entry_point.load())
        registered.append(str(entry_point.name))
    return registered


def manifest_for(driver_cls: type[Driver]) -> AdapterManifest:
    """Build the :class:`AdapterManifest` for a driver class (digest computed)."""
    from agentdrill import __version__

    manifest = AdapterManifest(
        name=driver_cls.name,
        version=__version__,
        capabilities=["stdin_stdout"],
        output_schema={"$id": "agentdrill.run_envelope.v1"},
        tool_event_stream_version="agentdrill.run_envelope.v1",
    )
    manifest.digest = manifest.compute_digest()
    return manifest
