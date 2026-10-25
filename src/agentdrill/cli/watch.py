"""``agentdrill watch`` — re-run affected packs on change (dev loop, M11 11.5).

Polls the given paths (default: the working directory) and reports the packs
affected by each change via the trigger watcher. Pack/surface bindings come
from config; the local dev loop surfaces the affected set so it can be
re-run. Design: ``docs/design/ci-gate.md``.
"""

from __future__ import annotations

import time

import click

from agentdrill.ci.triggers import TriggerWatcher
from agentdrill.ci.watch import LocalWatcher, snapshot_paths


@click.command()
@click.argument("paths", nargs=-1)
@click.option("--poll-interval", type=float, default=1.0, show_default=True)
@click.option("--once", is_flag=True, help="Poll once and exit (dev/CI).")
def watch(paths: tuple[str, ...], poll_interval: float, once: bool) -> None:
    """Watch for changes and re-run affected packs."""
    watch_paths = paths or (".",)
    watcher = LocalWatcher(TriggerWatcher())

    if once:
        affected = watcher.poll(snapshot_paths(watch_paths), {})
        click.echo(f"watch: affected packs: {', '.join(affected) or 'none'}")
        return

    click.echo(f"watching {', '.join(watch_paths)} (Ctrl-C to stop)")
    try:
        while True:
            affected = watcher.poll(snapshot_paths(watch_paths), {})
            if affected:
                click.echo(f"affected: {', '.join(affected)}")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        click.echo("stopped")
