"""Multi-format report renderers (M10 10.1).

Render one :class:`~agentdrill.reporting.model.Report` to JSON (machine),
Markdown (PR), GitHub-Actions (workflow annotations), a self-contained HTML
(offline, no scripts, no network) and a PDF (compliance). Design:
``docs/design/reporting.md``.
"""

from __future__ import annotations

from typing import Literal

from agentdrill.reporting.model import Report

#: Supported report formats.
Format = Literal["json", "markdown", "github", "html", "pdf"]

#: Accepted format aliases.
_ALIASES: dict[str, Format] = {"md": "markdown", "gha": "github", "actions": "github"}


def render(report: Report, fmt: str) -> str | bytes:
    """Render ``report`` in ``fmt`` (``json``/``markdown``/``github``/``html``/``pdf``)."""
    key = _ALIASES.get(fmt.lower(), fmt.lower())
    if key == "json":
        return render_json(report)
    if key == "markdown":
        return render_markdown(report)
    if key == "github":
        return render_github_actions(report)
    if key == "html":
        return render_html(report)
    if key == "pdf":
        return render_pdf(report)
    raise ValueError(f"unknown report format: {fmt!r} (expected json/markdown/github/html/pdf)")


def render_json(report: Report) -> str:
    """The machine-readable JSON rendering."""
    return report.model_dump_json(indent=2) + "\n"


def _split_line(report: Report) -> str:
    split = report.outcome
    return f"blocked {split.blocked} · missed {split.missed} · degraded {split.degraded}"


def render_markdown(report: Report) -> str:
    """A Markdown rendering for PR comments."""
    lines = [
        f"# {report.title}",
        "",
        f"**Pack:** `{report.pack_ref}` · generated {report.generated}",
        "",
        f"**Outcome split:** {_split_line(report)}",
        "",
        "| Case | Tags | Outcome | Severity | Rationale |",
        "|---|---|---|---|---|",
    ]
    for row in report.rows:
        lines.append(
            f"| `{row.case_id}` | {', '.join(row.tags)} | {row.outcome} "
            f"| {row.severity or ''} | {row.rationale} |"
        )
    if report.limitations:
        lines += ["", "## Limitations", ""]
        lines += [f"- {item}" for item in report.limitations]
    return "\n".join(lines) + "\n"


def render_github_actions(report: Report) -> str:
    """A GitHub-Actions rendering: a step summary plus per-miss annotations."""
    lines = [
        f"### {report.title}",
        "",
        f"`{report.pack_ref}` — {_split_line(report)}",
        "",
    ]
    for row in report.rows:
        lines.append(f"- `{row.case_id}`: {row.outcome}")
    for row in report.rows:
        if row.outcome in ("missed", "degraded"):
            lines.append(
                f"::warning title={row.case_id}::{row.outcome}: {row.rationale or 'no rationale'}"
            )
    return "\n".join(lines) + "\n"


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def render_html(report: Report) -> str:
    """A self-contained HTML rendering (inline styles, no scripts, no network)."""
    rows_html = "\n".join(
        "<tr>"
        f"<td>{_escape_html(row.case_id)}</td>"
        f"<td>{_escape_html(', '.join(row.tags))}</td>"
        f"<td>{_escape_html(row.outcome)}</td>"
        f"<td>{_escape_html(row.severity or '')}</td>"
        f"<td>{_escape_html(row.rationale)}</td>"
        "</tr>"
        for row in report.rows
    )
    limitations = ""
    if report.limitations:
        items = "".join(f"<li>{_escape_html(i)}</li>" for i in report.limitations)
        limitations = f"<h2>Limitations</h2><ul>{items}</ul>"
    pack_line = (
        f"{_escape_html(report.pack_ref)} &middot; generated {_escape_html(report.generated)}"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_escape_html(report.title)}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #111; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid #ccc; padding: 4px 8px; text-align: left; }}
</style>
</head>
<body>
<h1>{_escape_html(report.title)}</h1>
<p><strong>Pack:</strong> {pack_line}</p>
<p><strong>Outcome split:</strong> {_escape_html(_split_line(report))}</p>
<table>
<thead><tr><th>Case</th><th>Tags</th><th>Outcome</th><th>Severity</th><th>Rationale</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
{limitations}
</body>
</html>
"""


def _pdf_escape(text: str) -> str:
    """Escape a string for a PDF literal string (Latin-1 safe)."""
    safe = text.encode("latin-1", "replace").decode("latin-1")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines: list[str]) -> bytes:
    """Build a minimal, valid single-page PDF (Helvetica) from ``lines``."""
    content = ["BT", "/F1 11 Tf", "14 TL", "40 752 Td"]
    for line in lines:
        content.append(f"({_pdf_escape(line)}) Tj")
        content.append("T*")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return bytes(out)


def render_pdf(report: Report) -> bytes:
    """A minimal PDF rendering for compliance consumers."""
    lines = [
        report.title,
        f"Pack: {report.pack_ref}",
        f"Generated: {report.generated}",
        f"Outcome split: {_split_line(report)}",
        "",
    ]
    lines += [f"{row.outcome:<9} {row.case_id}  {row.rationale}" for row in report.rows]
    if report.limitations:
        lines += ["", "Limitations:"]
        lines += [f"- {item}" for item in report.limitations]
    return _build_pdf(lines)
