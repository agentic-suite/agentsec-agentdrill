"""``agentdrill registry`` — signed, read-only pack registry access.

Surface wired in M1; registry sync lands with the registry/governance milestone.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.group(name="registry")
def registry_group() -> None:
    """Pack registry operations."""


@registry_group.command()
def sync() -> None:
    """Sync the local index from the registry (read-only, signature-verified)."""
    planned("registry sync")
