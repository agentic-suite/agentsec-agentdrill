"""``agentdrill quickstart`` — boot the bundled demo stack (M18 18.7, F66).

Reaches a first honest result in ≤15 minutes; the result is mock-attested and
watermarked ``demo — never evidence``.
"""

from __future__ import annotations

import click

from agentdrill.lifecycle.quickstart import run_quickstart


@click.command()
@click.option("--pack", "pack_path", default=None, help="Demo pack to run.")
def quickstart(pack_path: str | None) -> None:
    """Boot the bundled demo stack and produce a first honest result."""
    result = run_quickstart(pack_path=pack_path)
    click.echo(
        f"outcome: blocked {result.outcome.blocked}, "
        f"missed {result.outcome.missed}, degraded {result.outcome.degraded}"
    )
    click.echo(f"attestation: {result.attestation}")
    click.echo(f"watermark: {result.watermark} (took {result.elapsed_seconds:.2f}s)")
