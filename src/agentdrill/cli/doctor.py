"""``agentdrill doctor`` — environment and target sanity check.

Surface wired in M1 1.2; the check report is delivered by M1 1.5.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.command()
def doctor() -> None:
    """Report environment and target sanity (a clear verdict)."""
    planned("doctor")
