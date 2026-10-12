"""Helpers for CLI commands whose engine lands in a later v0.1.0 milestone.

M1 (foundation) wires the full command surface so ``agentdrill --help`` matches
``docs/reference/cli-reference.md``. Commands whose behavior arrives later are
registered as explicit *planned* stubs that fail **loudly** with a reserved exit
code — never silently no-op.
"""

from __future__ import annotations

from typing import NoReturn

import click

from agentdrill.cli.exit_codes import ExitCode


def planned(name: str) -> NoReturn:
    """Fail loudly for a command planned in a later v0.1.0 milestone."""
    click.echo(
        f"agentdrill {name}: not yet implemented "
        "(planned for a later v0.1.0 milestone).",
        err=True,
    )
    raise SystemExit(int(ExitCode.CONFIG_ERROR))
