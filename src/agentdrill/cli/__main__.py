"""Command-line interface for AgentDrill.

The CLI is a thin wrapper over the core library (spec §"Runtime Interfaces").
All three surfaces — CLI, pytest plugin, and Python library — share the same
core runner, scorer, and adapter engine; nothing business-logic lives here.

Commands registered:
  - `run`        Run a scenario pack against an agent and score the results.
  - `list`       List packs, cases, oracles, targets, or drivers.
  - `validate`   Validate packs, agents, and baselines for correctness.
  - `verify`     Verify a bundle or release offline.
  - `quickstart` Boot the bundled demo stack.
  - `pack`       Pack lifecycle (lint/diff/publish/verify/outdated/deprecate).
  - `registry`   Pack registry operations (read-only sync).
  - `watch`      Re-run affected packs on change (dev loop).
  - `schedule`   Cadence runs for out-of-PR drift.
  - `compare`    Compare a candidate run against a golden baseline.
  - `init`       Scaffold a new AgentDrill project.
  - `baseline`   Manage golden baselines (save/list/validate/describe/tag/annotate/delete).
  - `cache`      Manage evaluation caches (clear/stats).
  - `plugins`    Discover, list, and inspect plugins.
  - `test`       Run scenario packs as tests with auto-discovery.
  - `benchmark`  Import external benchmark datasets as scenario packs.
  - `doctor`     Report environment and target sanity.
  - `version`    Print the installed version.
"""

from __future__ import annotations

import click

# Import all subcommand modules; each registers itself on its own Click group
# or top-level command, and is wired into the `main` group below.
from agentdrill.cli.baseline import baseline_group
from agentdrill.cli.benchmark import benchmark
from agentdrill.cli.cache import cache_group
from agentdrill.cli.compare import compare
from agentdrill.cli.doctor import doctor
from agentdrill.cli.exit_codes import ExitCode
from agentdrill.cli.export import export_group
from agentdrill.cli.init import init_cmd
from agentdrill.cli.list import list_group
from agentdrill.cli.pack import pack_group
from agentdrill.cli.plugins import plugins
from agentdrill.cli.quickstart import quickstart
from agentdrill.cli.registry import registry_group
from agentdrill.cli.run import run
from agentdrill.cli.schedule import schedule
from agentdrill.cli.test import test_group
from agentdrill.cli.validate import validate
from agentdrill.cli.verify import verify
from agentdrill.cli.watch import watch


@click.group()
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(),
    help="Path to agentdrill.toml (overrides $AGENTDRILL_CONFIG and cwd).",
)
@click.pass_context
def main(ctx: click.Context, config_path: str | None) -> None:
    """AgentDrill — gate agent releases with evidence."""
    from agentdrill.config import load_config
    from agentdrill.models.errors import ConfigError

    try:
        ctx.obj = load_config(config_path)
    except ConfigError as exc:
        click.echo(f"configuration error: {exc}", err=True)
        ctx.exit(int(ExitCode.CONFIG_ERROR))


@main.command()
def version() -> None:
    """Print the installed version."""
    from agentdrill import __version__

    click.echo(__version__)


# Wire up all subcommands and command groups under the root `main` group.
main.add_command(run)
main.add_command(list_group)
main.add_command(validate)
main.add_command(verify)
main.add_command(quickstart)
main.add_command(pack_group)
main.add_command(registry_group)
main.add_command(export_group)
main.add_command(watch)
main.add_command(schedule)
main.add_command(compare)
main.add_command(init_cmd)
main.add_command(baseline_group)
main.add_command(cache_group)
main.add_command(plugins)
main.add_command(test_group)
main.add_command(benchmark)
main.add_command(doctor)
