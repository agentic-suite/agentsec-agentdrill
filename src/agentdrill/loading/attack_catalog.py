"""Catalog helpers for attack packs (M2 work item 2.6).

Fixture coverage for deterministic runs, the ``benign_twin`` linkage, and the
twin-driver hook consumed by the efficacy control (F59) at M13.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from agentdrill.models.attack_pack import AttackCase, AttackPack, Driver

#: Default fixture directory for the attack catalog.
DEFAULT_FIXTURE_DIR = "packs/fixtures"

#: Factory producing the config for a case's unguarded twin driver.
TwinDriverFactory = Callable[[AttackCase], dict[str, Any]]

_TWIN_DRIVERS: dict[str, TwinDriverFactory] = {}


def case_tools(pack: AttackPack) -> set[str]:
    """Every tool referenced by any of the pack's attack steps."""
    return {step.tool for case in pack.cases for step in case.attack.steps}


def missing_fixtures(
    pack: AttackPack, fixtures_dir: str | Path = DEFAULT_FIXTURE_DIR
) -> set[str]:
    """Tools in ``pack`` with no ``<tool>.json`` fixture in ``fixtures_dir``.

    Args:
        pack: The attack pack to check.
        fixtures_dir: Directory holding ``<tool>.json`` fixtures.

    Returns:
        The set of tools that lack a fixture (empty when coverage is complete).
    """
    directory = Path(fixtures_dir)
    available = {f.stem for f in directory.glob("*.json")} if directory.is_dir() else set()
    return case_tools(pack) - available


def pack_ref(pack: AttackPack) -> str:
    """The ``pack@version+hash`` reference every result binds to (DD-28)."""
    return f"{pack.pack.name}@{pack.pack.version}+{pack.pack.hash}"


def linked_twins(pack: AttackPack) -> dict[str, str]:
    """Map case id -> benign-twin case id for cases that declare a twin."""
    twins: dict[str, str] = {}
    for case in pack.cases:
        if case.benign_twin is not None:
            twins[case.id] = case.benign_twin
    return twins


def register_twin_driver(driver_type: str, factory: TwinDriverFactory) -> None:
    """Register a factory producing a case's unguarded twin driver config.

    The efficacy control (F59/M13) registers the real twins here; until then
    :func:`twin_driver` falls back to the case's own driver config.
    """
    _TWIN_DRIVERS[driver_type] = factory


def twin_driver(case: AttackCase) -> Driver:
    """Return the driver used to run ``case``'s benign twin (F59, consumed at M13).

    A registered factory for the case's driver type wins; otherwise the twin
    reuses the case's own driver config.
    """
    factory = _TWIN_DRIVERS.get(case.driver.type)
    config = factory(case) if factory is not None else dict(case.driver.config)
    return Driver(type=case.driver.type, config=config)
