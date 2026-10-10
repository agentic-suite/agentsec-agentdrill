"""``agentdrill watch`` — re-run affected packs on change (dev loop).

Surface wired in M1; the watch loop lands with the CI/dev-loop milestone.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.command()
@click.argument("paths", nargs=-1)
def watch(paths: tuple[str, ...]) -> None:
    """Watch for changes and re-run affected packs."""
    planned("watch")
