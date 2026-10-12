"""``agentdrill list`` — enumerate packs, cases, oracles, targets, drivers.

``list packs`` and ``list cases`` are wired for the attack-pack catalog
(M2 2.4); the oracle/target/driver listings land with their registries.
"""

from __future__ import annotations

import click

from agentdrill.cli._planned import planned


@click.group(name="list")
def list_group() -> None:
    """List packs, cases, oracles, targets, or drivers."""


@list_group.command()
@click.option(
    "--dir",
    "dirs",
    multiple=True,
    help="Directory to search (repeatable; default: packs).",
)
def packs(dirs: tuple[str, ...]) -> None:
    """List available attack packs."""
    from agentdrill.loading.attack_pack_loader import discover_attack_packs

    found = discover_attack_packs(list(dirs) if dirs else None)
    if not found:
        click.echo("no packs found")
        return
    for pack in found:
        click.echo(f"{pack.pack.name} {pack.pack.version} ({len(pack.cases)} cases)")


@list_group.command()
@click.option("--tag", default=None, help="Filter cases by tag.")
@click.option("--target", default=None, help="Filter cases by target type.")
@click.option("--difficulty", default=None, help="Filter cases by difficulty.")
@click.option(
    "--dir",
    "dirs",
    multiple=True,
    help="Directory to search (repeatable; default: packs).",
)
def cases(
    tag: str | None,
    target: str | None,
    difficulty: str | None,
    dirs: tuple[str, ...],
) -> None:
    """List cases (optionally filtered)."""
    from agentdrill.loading.attack_pack_loader import discover_attack_packs

    rows: list[tuple[str, str, str, str]] = []
    for pack in discover_attack_packs(list(dirs) if dirs else None):
        for case in pack.cases:
            if tag is not None and tag not in case.tags:
                continue
            if target is not None and case.target.type != target:
                continue
            if difficulty is not None and case.difficulty != difficulty:
                continue
            rows.append((pack.pack.name, case.id, case.target.type, case.difficulty or "-"))
    if not rows:
        click.echo("no cases found")
        return
    for pack_name, case_id, target_type, case_difficulty in rows:
        click.echo(f"{pack_name}\t{case_id}\t{target_type}\t{case_difficulty}")


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
