"""``agentdrill list`` — enumerate packs, cases, oracles, targets, drivers.

Surface wired in M1; the listing engine lands with the pack/target milestones.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.group(name="list")
def list_group() -> None:
    """List packs, cases, oracles, targets, or drivers."""


@list_group.command()
@click.option("--tag", default=None, help="Filter cases by tag.")
@click.option("--target", default=None, help="Filter cases by target.")
@click.option("--difficulty", default=None, help="Filter cases by difficulty.")
def cases(tag: str | None, target: str | None, difficulty: str | None) -> None:
    """List cases (optionally filtered)."""
    planned("list cases")


@list_group.command()
def packs() -> None:
    """List available packs."""
    planned("list packs")


@list_group.command()
def oracles() -> None:
    """List available oracles."""
    planned("list oracles")


@list_group.command()
def targets() -> None:
    """List available targets."""
    planned("list targets")


@list_group.command()
def drivers() -> None:
    """List available drivers."""
    planned("list drivers")
