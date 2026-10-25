"""Trace explorer - core (M30 30.1, F102).

A local, offline view of a run: the **overview** (outcome x tier x witness;
`untested` never hidden; filters), the **case page** (step-through + stage
timeline F37), the **defense-vs-witness** panel (`witness_discrepancy`
highlighted), and the **HITL queue**. Untrusted content (payloads, tool names) is
rendered **inert** - everything is escaped, nothing is evaluated. Design:
``docs/design/trace-explorer-and-platform-standards.md``; PRD 40 (R76).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel, Field

#: Case outcomes, in the honest vocabulary.
_OUTCOMES = ("blocked", "missed", "degraded", "untested")


class ViewRow(BaseModel):
    """One case's row in the run overview."""

    case_id: str
    outcome: str
    tier: str | None = None
    witness: str | None = None
    stage: str | None = None
    tags: list[str] = Field(default_factory=list)
    severity: str | None = None
    defense_decision: str | None = None
    witness_effect: str | None = None
    witness_discrepancy: bool = False


class DefenseWitnessPanel(BaseModel):
    """The defense decision vs. the independently observed effect."""

    decision: str | None = None
    effect: str | None = None
    discrepancy: bool = False


class CaseView(BaseModel):
    """A case page: steps, stage timeline and the defense-vs-witness panel."""

    row: ViewRow
    steps: list[str] = Field(default_factory=list)
    stages: list[tuple[str, float]] = Field(default_factory=list)
    panel: DefenseWitnessPanel


class HitlQueueItem(BaseModel):
    """One case awaiting human adjudication."""

    case_id: str
    reason: str


def build_overview(rows: Sequence[ViewRow]) -> list[ViewRow]:
    """The run overview — every row, including ``untested`` (never hidden)."""
    return list(rows)


def filter_rows(
    rows: Sequence[ViewRow],
    *,
    outcome: str | None = None,
    tier: str | None = None,
    tag: str | None = None,
    severity: str | None = None,
) -> list[ViewRow]:
    """Filter rows by outcome / tier / tag / severity (all optional)."""
    return [
        row
        for row in rows
        if (outcome is None or row.outcome == outcome)
        and (tier is None or row.tier == tier)
        and (tag is None or tag in row.tags)
        and (severity is None or row.severity == severity)
    ]


def build_case_view(
    row: ViewRow,
    *,
    steps: Sequence[str] = (),
    stages: Sequence[tuple[str, float]] = (),
) -> CaseView:
    """Build a case page from its steps and stage timings."""
    return CaseView(
        row=row,
        steps=list(steps),
        stages=list(stages),
        panel=DefenseWitnessPanel(
            decision=row.defense_decision,
            effect=row.witness_effect,
            discrepancy=row.witness_discrepancy,
        ),
    )


def hitl_queue(rows: Iterable[ViewRow]) -> list[HitlQueueItem]:
    """Cases needing adjudication: a witness discrepancy or a degraded result."""
    queue: list[HitlQueueItem] = []
    for row in rows:
        if row.witness_discrepancy:
            queue.append(HitlQueueItem(case_id=row.case_id, reason="witness_discrepancy"))
        elif row.outcome == "degraded":
            queue.append(HitlQueueItem(case_id=row.case_id, reason="degraded"))
    return queue


def escape(text: str) -> str:
    """Escape untrusted text for inert HTML rendering."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def deep_link(case_id: str, *, base: str = "") -> str:
    """A stable deep link to a case page."""
    return f"{base}#case-{case_id}"


def _row_html(row: ViewRow) -> str:
    discrepancy = " ⚠ witness_discrepancy" if row.witness_discrepancy else ""
    return (
        f'<tr id="case-{escape(row.case_id)}">'
        f"<td>{escape(row.case_id)}</td>"
        f"<td>{escape(row.outcome)}</td>"
        f"<td>{escape(row.tier or '')}</td>"
        f"<td>{escape(row.witness or '')}</td>"
        f"<td>{escape(row.severity or '')}{discrepancy}</td>"
        "</tr>"
    )


def render_view_html(
    rows: Sequence[ViewRow], *, cases: Sequence[CaseView] = (), title: str = "agentdrill run"
) -> str:
    """Render a self-contained, inert, accessible run view (no scripts, no network)."""
    table = "\n".join(_row_html(row) for row in rows)
    panels = []
    for case in cases:
        panel = case.panel
        steps = "".join(f"<li>{escape(step)}</li>" for step in case.steps)
        stages = "".join(
            f"<li>{escape(stage)}: {duration} ms</li>" for stage, duration in case.stages
        )
        panels.append(
            f'<section aria-labelledby="case-{escape(case.row.case_id)}">'
            f"<h2 id=\"case-{escape(case.row.case_id)}\">{escape(case.row.case_id)}</h2>"
            f"<h3>Steps</h3><ol>{steps}</ol>"
            f"<h3>Stage timeline</h3><ul>{stages}</ul>"
            f"<h3>Defense vs. witness</h3>"
            f"<p>decision: {escape(panel.decision or '')} · "
            f"effect: {escape(panel.effect or '')} · "
            f"discrepancy: {escape(str(panel.discrepancy).lower())}</p>"
            "</section>"
        )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n</head>\n<body>\n"
        f"<h1>{escape(title)}</h1>\n"
        '<table>\n<caption>Run overview</caption>\n'
        "<thead><tr><th scope=\"col\">Case</th><th scope=\"col\">Outcome</th>"
        "<th scope=\"col\">Tier</th><th scope=\"col\">Witness</th>"
        "<th scope=\"col\">Severity</th></tr></thead>\n"
        f"<tbody>\n{table}\n</tbody>\n</table>\n"
        f"{''.join(panels)}\n"
        "</body>\n</html>\n"
    )
