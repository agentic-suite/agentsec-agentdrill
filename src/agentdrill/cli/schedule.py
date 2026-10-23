"""``agentdrill schedule`` — cadence drills for out-of-PR drift (M11 11.8, F71).

Runs the drill schedules that are due for the configured cadence (vendor
model, MCP rug-pull, marketplace skill) and writes a finding per run, labeled
with its trigger. Schedule definitions come from config. Design:
``docs/design/ci-gate.md``.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

import click

from agentdrill.ci.schedule import DrillSchedule, due_drills, record_finding


@click.command()
@click.option("--cadence", default=None, help="Only drills of this cadence.")
@click.option("--once", is_flag=True, help="Evaluate due drills once and exit.")
@click.option(
    "--output", default=".agentdrill/findings", show_default=True, help="Finding output dir."
)
def schedule(cadence: str | None, once: bool, output: str) -> None:
    """Run cadence drills for out-of-PR drift."""
    schedules: list[DrillSchedule] = []  # definitions come from config (later)
    if cadence:
        schedules = [s for s in schedules if s.cadence == cadence]

    due = due_drills(schedules, now=time.time())
    if once:
        click.echo(f"schedule: {len(due)} due drill(s)")
        return

    for drill in due:
        path = record_finding(drill, output, generated=datetime.now(UTC).isoformat())
        click.echo(f"scheduled finding: {path}")
