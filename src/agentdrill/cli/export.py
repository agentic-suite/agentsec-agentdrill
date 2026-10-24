"""``agentdrill export`` — CI-matrix export (M20 20.4, F72) and interchange
emitters (M26 26.1, R74: SARIF 2.1.0, JUnit).

CI-matrix export emits the pack set, manifest and attestation as a CI matrix;
the interchange emitters project an M10 report into SARIF/JUnit for code
scanning and CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click

from agentdrill.dx.ci_matrix import build_ci_matrix, render_ci_matrix, validate_ci_matrix

if TYPE_CHECKING:
    from agentdrill.integrations import IntegrationFinding

#: The M10 report JSON the interchange emitters consume.
_REPORT_OPTION = click.option(
    "--report",
    "report_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="M10 report JSON (a serialized `agentdrill.reporting.Report`).",
)
_OUT_OPTION = click.option(
    "--out",
    "out_path",
    default=None,
    type=click.Path(dir_okay=False),
    help="Write to this path (default: stdout).",
)


@click.group(name="export")
def export_group() -> None:
    """Export reproducible CI artifacts and interchange formats."""


def _report_findings(report_path: str) -> list[IntegrationFinding]:
    """Load the report and project it into neutral integration findings."""
    from agentdrill.integrations import findings_from_report
    from agentdrill.reporting import Report

    report = Report.model_validate_json(Path(report_path).read_text(encoding="utf-8"))
    return list(findings_from_report(report))


def _write(text: str, out_path: str | None) -> None:
    if out_path is None:
        click.echo(text, nl=False)
    else:
        Path(out_path).write_text(text, encoding="utf-8")
        click.echo(f"wrote {out_path}")


@export_group.command()
@_REPORT_OPTION
@_OUT_OPTION
def sarif(report_path: str, out_path: str | None) -> None:
    """Emit SARIF 2.1.0 for code scanning (rule = case id)."""
    from agentdrill.integrations import render_sarif

    _write(render_sarif(_report_findings(report_path)), out_path)


@export_group.command()
@_REPORT_OPTION
@_OUT_OPTION
def junit(report_path: str, out_path: str | None) -> None:
    """Emit JUnit XML (missed → failure, untested → skipped)."""
    from agentdrill.integrations import to_junit

    _write(to_junit(_report_findings(report_path)), out_path)


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

