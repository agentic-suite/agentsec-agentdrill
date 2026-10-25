"""Run manifest model — deterministic environment snapshot for every run.

A :class:`RunManifest` captures the execution environment at the time of a
run: OS, Python version, agent metadata, dependency tree, and env var names
(never values). The manifest is emitted alongside scenario results so that
baselines are reproducible and cross-platform comparisons are meaningful.
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class RunManifest(BaseModel):
    """Immutable snapshot of the execution environment for one run.

    Fields:
        run_id: Run identifier.
        timestamp: ISO-8601 creation timestamp.
        host: OS, arch, and Python version.
        agent: Adapter type and resolved entry point (grading path).
        deps: Locked dependency tree (``pip list --format=json``).
        environment: Environment variable names only (never values).
        execution: Wall time, tool call count, retry count, adapter warnings.
        pack: Pack identity + hash (attack path; ``name``/``version``/``hash``).
        targets: Target digests bound into the run (attack path).
        drivers: Driver digests bound into the run (attack path).
        oracles: Oracle identities + versions used by the run (attack path).
        pins: Pinned seeds/models/pack-hash/oracle versions (M8 8.3).
    """

    run_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    host: dict[str, str] = Field(default_factory=dict)
    agent: dict[str, Any] = Field(default_factory=dict)
    deps: list[dict[str, str]] = Field(default_factory=list)
    environment: list[str] = Field(default_factory=list)
    execution: dict[str, Any] = Field(default_factory=dict)
    #: Pack identity + hash (attack path).
    pack: dict[str, Any] = Field(default_factory=dict)
    #: Target digests bound into the run (attack path).
    targets: list[dict[str, Any]] = Field(default_factory=list)
    #: Driver digests bound into the run (attack path).
    drivers: list[dict[str, Any]] = Field(default_factory=list)
    #: Oracle identities + versions used by the run (attack path).
    oracles: list[dict[str, Any]] = Field(default_factory=list)
    #: Pinned inputs (seed/model/pack-hash/oracle versions) — M8 8.3.
    pins: dict[str, Any] = Field(default_factory=dict)


def collect_host_info() -> dict[str, str]:
    """Collect OS, architecture, and Python version.

    Returns:
        Dict with keys ``os``, ``arch``, ``python``.
    """
    return {
        "os": platform.system() + " " + platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
    }


def collect_dependencies() -> list[dict[str, str]]:
    """Collect the locked dependency tree via ``pip list --format=json``.

    Falls back to an empty list if pip is unavailable or the command fails.

    Returns:
        A list of ``{"name": "...", "version": "..."}`` dicts.
    """
    try:
        result = subprocess.run(
            [  # noqa: S607
                "pip",
                "list",
                "--format=json",
                "--disable-pip-version-check",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)  # type: ignore[no-any-return]
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return []


def collect_environment_names() -> list[str]:
    """Collect environment variable names (sorted, never values).

    Returns:
        Sorted list of environment variable names visible to the process.
    """
    import os

    return sorted(os.environ.keys())


def build_manifest(
    run_id: str,
    agent_config: dict[str, Any] | None = None,
    execution: dict[str, Any] | None = None,
    include_deps: bool = True,
) -> RunManifest:
    """Build a complete RunManifest for the current execution environment.

    Args:
        run_id: The run identifier.
        agent_config: Agent configuration (sanitized, no secrets).
        execution: Execution metrics (wall time, tool call count, etc.).
        include_deps: Whether to collect the dependency tree (can be slow).

    Returns:
        A populated RunManifest.
    """
    manifest = RunManifest(
        run_id=run_id,
        host=collect_host_info(),
        agent=agent_config or {},
        environment=collect_environment_names(),
        execution=execution or {},
    )
    if include_deps:
        manifest.deps = collect_dependencies()
    return manifest


def build_run_manifest(
    run_id: str,
    *,
    pack: dict[str, Any] | None = None,
    targets: list[dict[str, Any]] | None = None,
    drivers: list[dict[str, Any]] | None = None,
    oracles: list[dict[str, Any]] | None = None,
    pins: dict[str, Any] | None = None,
    include_deps: bool = True,
) -> RunManifest:
    """Build the run manifest for an attack run (M8 8.2).

    Captures the environment (host, deps, env **names** only) plus the run's
    provenance: pack identity/hash, target/driver digests, oracle versions and
    pins — so a third party can reproduce the run (R6).

    Args:
        run_id: The run identifier.
        pack: Pack identity — ``{"name", "version", "hash"}``.
        targets: Target digest records bound into the run.
        drivers: Driver digest records bound into the run.
        oracles: Oracle identity/version records used by the run.
        pins: Pinned inputs (seed/model/pack-hash/oracle versions).
        include_deps: Whether to collect the dependency tree (can be slow).

    Returns:
        A populated :class:`RunManifest`.
    """
    manifest = RunManifest(
        run_id=run_id,
        host=collect_host_info(),
        environment=collect_environment_names(),
        pack=pack or {},
        targets=targets or [],
        drivers=drivers or [],
        oracles=oracles or [],
        pins=pins or {},
    )
    if include_deps:
        manifest.deps = collect_dependencies()
    return manifest
