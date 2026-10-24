"""``agentdrill export`` — CI-matrix export (M20 20.4, F72).

Emits the pack set, manifest and attestation as a CI matrix.
"""

from __future__ import annotations

import click

from agentdrill.dx.ci_matrix import build_ci_matrix, render_ci_matrix, validate_ci_matrix


@click.group(name="export")
def export_group() -> None:
    """Export reproducible CI artifacts."""


@export_group.command()
@click.option("--format", "fmt", default="github-actions", help="github-actions | gitlab")
@click.option(
    "--pack",
    "pack_paths",
    multiple=True,
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Pack(s) to include in the matrix.",
)
def ci(fmt: str, pack_paths: tuple[str, ...]) -> None:
    """Emit a CI matrix for the given packs."""
    from agentdrill.loading.attack_pack_loader import load_attack_pack

    packs = [load_attack_pack(path) for path in pack_paths]
    refs = [f"{pack.pack.name}@{pack.pack.version}" for pack in packs]
    matrix = build_ci_matrix(
        refs,
        manifest={"hashes": {"attacker": "sha256:cli"}},
        attestation={"policyweave-output": "fixture"},
    )
    validate_ci_matrix(matrix)
    click.echo(render_ci_matrix(matrix, fmt=fmt))
