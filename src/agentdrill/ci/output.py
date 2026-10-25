"""CI output — GitHub Actions / GitLab + step summary (M11 11.3).

Renders the gate result so it is visible in a PR: GitHub Actions annotations,
GitLab Markdown, and the ``$GITHUB_STEP_SUMMARY`` file. Design:
``docs/design/ci-gate.md``.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path

from agentdrill.ci.gating import GateFailure

#: Supported CI output formats.
FORMATS: tuple[str, ...] = ("github-actions", "gitlab")


def render_ci_output(
    exit_code: int,
    failures: Sequence[GateFailure],
    *,
    output_format: str = "github-actions",
    title: str = "agentdrill drill",
) -> str:
    """Render the gate result for CI.

    Raises:
        ValueError: ``output_format`` is not ``github-actions`` or ``gitlab``.
    """
    if output_format not in FORMATS:
        raise ValueError(f"unknown output_format: {output_format!r} (expected {FORMATS})")

    lines: list[str] = []
    if output_format == "github-actions":
        for failure in failures:
            lines.append(f"::error title={failure.kind}::{failure.detail}")
        lines.append("")

    lines += [
        f"### {title}",
        "",
        f"Exit code: **{int(exit_code)}**",
        "",
    ]
    if failures:
        lines += ["| kind | dimension | severity | detail |", "|---|---|---|---|"]
        lines += [
            f"| {f.kind} | {f.dimension or ''} | {f.severity or ''} | {f.detail} |"
            for f in failures
        ]
    else:
        lines.append("All cases behaved as expected.")
    return "\n".join(lines) + "\n"


def write_step_summary(text: str, *, env: Mapping[str, str] | None = None) -> Path | None:
    """Append ``text`` to ``$GITHUB_STEP_SUMMARY``; ``None`` when it is unset."""
    environ = env if env is not None else os.environ
    target = environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return None
    path = Path(target)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
    return path
