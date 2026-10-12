"""``agentdrill doctor`` — environment and target sanity check."""

from __future__ import annotations

import click

from agentdrill.cli.exit_codes import ExitCode


@click.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Report environment and target sanity (a clear verdict)."""
    from agentdrill.doctor import has_failures, run_checks

    checks = run_checks(ctx.obj)
    for check in checks:
        status = "ok" if check.ok else ("FAIL" if check.critical else "warn")
        click.echo(f"[{status}] {check.name}: {check.detail}")

    if has_failures(checks):
        click.echo("doctor: PROBLEMS FOUND")
        ctx.exit(int(ExitCode.CONFIG_ERROR))
    click.echo("doctor: OK")
