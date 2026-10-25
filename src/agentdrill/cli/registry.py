"""``agentdrill registry`` — signed, read-only pack registry access (M16 16.6).

Reads a signed ``registry.json`` from a file/mirror, verifies its signature
offline, and (optionally) writes the local index. A bad signature is rejected
loudly (exit 2).
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from agentdrill.cli.exit_codes import ExitCode
from agentdrill.registry import HmacSigner, RegistryIndex, SyncError, sync_index


@click.group(name="registry")
def registry_group() -> None:
    """Pack registry operations."""


@registry_group.command()
@click.option(
    "--from",
    "source",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Signed registry.json to sync from.",
)
@click.option("--key", default=None, help="Signing key (hex) to verify the signature.")
@click.option(
    "--out",
    default=None,
    type=click.Path(dir_okay=False),
    help="Write the verified index here (default: verify + print only).",
)
def sync(source: str, key: str | None, out: str | None) -> None:
    """Sync the local index from a signed registry file (read-only, verified)."""
    if not key:
        click.echo("registry sync: --key is required to verify the signature", err=True)
        raise SystemExit(int(ExitCode.CONFIG_ERROR))

    remote = RegistryIndex.model_validate(json.loads(Path(source).read_text(encoding="utf-8")))
    key_id = remote.signature.partition(":")[0] or "registry"
    verifier = HmacSigner(key=bytes.fromhex(key), key_id=key_id)
    try:
        synced = sync_index(remote, verifier=verifier)
    except SyncError as exc:
        click.echo(f"registry sync: {exc}", err=True)
        raise SystemExit(int(ExitCode.CONFIG_ERROR)) from exc

    if out:
        target = Path(out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(synced.model_dump_json(indent=2) + "\n", encoding="utf-8")
    for entry in synced.entries:
        click.echo(f"{entry.name}@{entry.version}")
