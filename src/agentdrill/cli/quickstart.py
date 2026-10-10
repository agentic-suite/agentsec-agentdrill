"""``agentdrill quickstart`` — boot the bundled demo stack for a first result.

Surface wired in M1; the demo stack lands with the lifecycle milestone.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.command()
def quickstart() -> None:
    """Boot the bundled demo stack and produce a first honest result."""
    planned("quickstart")
