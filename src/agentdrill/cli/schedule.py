"""``agentdrill schedule`` — cadence runs for out-of-PR drift.

Surface wired in M1; scheduled runs land with the lifecycle milestone.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.command()
@click.option("--cadence", default=None, help="Run cadence (e.g. 'daily').")
def schedule(cadence: str | None) -> None:
    """Run packs on a cadence to catch out-of-PR drift."""
    planned("schedule")
