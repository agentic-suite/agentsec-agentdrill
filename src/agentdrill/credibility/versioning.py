"""Oracle versioning + release notes (M19 19.1, F79).

Every oracle is semver'd and pinned in the manifest; behavior deltas are
released as notes; an **oracle major** invalidates comparability (a re-baseline
note). Design: ``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from pydantic import BaseModel


class OracleVersion(BaseModel):
    """An oracle's pinned version and behavior release notes."""

    name: str
    version: str
    behavior_notes: str = ""


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse ``MAJOR.MINOR.PATCH`` (missing parts default to 0)."""
    parts = version.split(".")
    padded = [*parts, "0", "0", "0"][:3]
    return (int(padded[0]), int(padded[1]), int(padded[2]))


def pin_versions(versions: Iterable[OracleVersion]) -> dict[str, str]:
    """The manifest ``pins`` mapping of oracle name → version."""
    return {version.name: version.version for version in versions}


def version_changed(previous: Mapping[str, str], current: Mapping[str, str]) -> list[str]:
    """Oracle names whose version differs between ``previous`` and ``current``."""
    return sorted(
        name for name in set(previous) | set(current) if previous.get(name) != current.get(name)
    )


def major_changed(previous: str, current: str) -> bool:
    """Whether an oracle-version change is a major (comparability-invalidating) one."""
    return parse_semver(previous)[0] != parse_semver(current)[0]


def rebaseline_note(name: str, previous: str, current: str) -> str | None:
    """A re-baseline note when a major oracle change invalidates comparability."""
    if major_changed(previous, current):
        return (
            f"oracle {name} major change {previous} -> {current}: comparability "
            "invalidated — re-baseline required"
        )
    return None
