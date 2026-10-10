"""``agentdrill pack`` — pack lifecycle operations.

Surface wired in M1; the pack operations land with the pack/registry milestones.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.group(name="pack")
def pack_group() -> None:
    """Pack lifecycle: lint, diff, publish, verify, outdated, deprecate."""


@pack_group.command()
@click.argument("path", required=False)
def lint(path: str | None) -> None:
    """Lint a pack for format/validation issues."""
    planned("pack lint")


@pack_group.command()
@click.argument("left")
@click.argument("right")
def diff(left: str, right: str) -> None:
    """Diff two pack versions."""
    planned("pack diff")


@pack_group.command()
@click.argument("path", required=False)
def publish(path: str | None) -> None:
    """Publish a pack to the registry."""
    planned("pack publish")


@pack_group.command()
@click.argument("pack_ref", required=False)
@click.option("--trust", default=None, help="Trust level to verify against.")
def verify(pack_ref: str | None, trust: str | None) -> None:
    """Verify a pack (signature/trust)."""
    planned("pack verify")


@pack_group.command()
def outdated() -> None:
    """List packs with a newer version available."""
    planned("pack outdated")


@pack_group.command()
@click.argument("pack_ref", required=False)
def deprecate(pack_ref: str | None) -> None:
    """Mark a pack version deprecated."""
    planned("pack deprecate")
