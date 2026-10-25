"""M10 10.1 — multi-format reporter (RED → GREEN).

One run renders to JSON (machine), Markdown (PR), GitHub-Actions, a
self-contained HTML (offline) and a PDF (compliance). An unknown format fails
loudly.
"""

from __future__ import annotations

import json

import pytest

from agentdrill.oracles.engine import OutcomeSplit
from agentdrill.reporting import Report, ReportRow, render


def _report() -> Report:
    return Report(
        title="Incident-core drill",
        pack_ref="p@1.0.0+deadbeef",
        generated="2026-10-23T00:00:00Z",
        outcome=OutcomeSplit(blocked=2, missed=1, degraded=0),
        rows=[
            ReportRow(case_id="c1", tags=["destructive"], outcome="blocked"),
            ReportRow(case_id="c2", tags=["secret"], outcome="missed"),
        ],
    )


def test_json_renders_one_run() -> None:
    data = json.loads(render(_report(), "json"))
    assert data["pack_ref"] == "p@1.0.0+deadbeef"
    assert data["outcome"]["blocked"] == 2
    assert [r["case_id"] for r in data["rows"]] == ["c1", "c2"]


def test_markdown_renders_one_run() -> None:
    md = render(_report(), "markdown")
    assert "Incident-core drill" in md
    assert "c1" in md and "c2" in md
    assert "blocked" in md and "missed" in md


def test_github_actions_renders_one_run() -> None:
    out = render(_report(), "github")
    assert "Incident-core drill" in out
    # workflow annotations or a step summary
    assert "::" in out or "###" in out


def test_html_is_self_contained() -> None:
    html = render(_report(), "html")
    assert "<!doctype html" in html.lower() or "<html" in html.lower()
    assert "c1" in html
    assert "<script" not in html.lower()  # no scripts
    assert "http://" not in html and "https://" not in html  # no network refs


def test_pdf_is_a_valid_pdf() -> None:
    pdf = render(_report(), "pdf")
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")


def test_unknown_format_fails_loudly() -> None:
    with pytest.raises(ValueError, match="format"):
        render(_report(), "docx")
