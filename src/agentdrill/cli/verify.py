"""``agentdrill verify`` — offline, zero-install bundle/release verification.

Surface wired in M1; verification lands with the lifecycle/verifier milestone.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.command()
@click.argument("artifact", required=False)
def verify(artifact: str | None) -> None:
    """Verify a bundle or release offline: intact, complete, honest-shaped."""
    planned("verify")
