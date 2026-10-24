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
    """Diff two pack versions (case + coverage delta)."""
    from agentdrill.dx import diff_packs
    from agentdrill.loading.attack_pack_loader import load_attack_pack

    delta = diff_packs(load_attack_pack(left), load_attack_pack(right))
    click.echo(f"added: {delta.added}")
    click.echo(f"removed: {delta.removed}")
    click.echo(f"changed: {delta.changed}")
    if delta.coverage_delta:
        click.echo(f"coverage delta: {delta.coverage_delta}")


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
@click.option(
    "--from",
    "source",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Remote registry.json to compare against.",
)
@click.option(
    "--local",
    default=".agentdrill/registry.json",
    show_default=True,
    type=click.Path(dir_okay=False),
    help="Local registry index.",
)
def outdated(source: str, local: str) -> None:
    """List packs with a newer version available."""
    import json
    from pathlib import Path

    from agentdrill.registry import RegistryIndex, is_outdated

    remote = RegistryIndex.model_validate(json.loads(Path(source).read_text(encoding="utf-8")))
    local_index = RegistryIndex()
    local_path = Path(local)
    if local_path.exists():
        local_index = RegistryIndex.model_validate(
            json.loads(local_path.read_text(encoding="utf-8"))
        )
    for entry in is_outdated(local_index, remote):
        click.echo(f"{entry.name}: {entry.local_version} -> {entry.remote_version}")


@pack_group.command()
@click.argument("pack_ref", required=False)
def deprecate(pack_ref: str | None) -> None:
    """Mark a pack version deprecated."""
    planned("pack deprecate")
