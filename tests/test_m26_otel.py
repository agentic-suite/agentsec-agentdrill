"""M26 26.2 — OTel emit/read (RED → GREEN).

Emit drill spans (drill = trace, case = span) using the pinned GenAI semconv
version, and read stage timings back from an instrumented target's trace. Span
coverage must be ≥ 95 % or the emitter fails loudly.
"""

from __future__ import annotations

import pytest

from agentdrill.integrations import (
    GEN_AI_SEMCONV_VERSION,
    OTelError,
    emit_drill,
    read_stage_timings,
    require_span_coverage,
    semconv_pin,
    span_coverage,
)
from agentdrill.integrations.model import IntegrationFinding


def _findings() -> list[IntegrationFinding]:
    return [
        IntegrationFinding(case_id="c1", outcome="missed", tier="T1", witness_ref="w1"),
        IntegrationFinding(case_id="c2", outcome="blocked"),
    ]


def test_emit_drill_one_trace_one_span_per_case() -> None:
    trace = emit_drill(_findings(), stage_timings={"c1": {"detect": 12.5, "halt": 3.0}})
    names = [s["name"] for s in trace["spans"]]
    assert names[0] == "agentdrill.drill"
    assert "c1" in names and "c2" in names
    assert trace["trace_id"]


def test_emit_drill_carries_genai_and_evidence_attributes() -> None:
    trace = emit_drill(_findings(), stage_timings={"c1": {"detect": 12.5}})
    span = next(s for s in trace["spans"] if s["name"] == "c1")
    attrs = span["attributes"]
    assert attrs["gen_ai.system"] == "agentdrill"
    assert attrs["gen_ai.operation.name"] == "run_case"
    assert attrs["agentdrill.outcome"] == "missed"
    assert attrs["agentdrill.tier"] == "T1"
    assert attrs["agentdrill.witness"] == "w1"
    assert attrs["agentdrill.stage.detect_ms"] == 12.5


def test_emit_drill_records_the_semconv_pin() -> None:
    trace = emit_drill(_findings())
    assert trace["semconv"]["gen_ai.semconv"] == GEN_AI_SEMCONV_VERSION
    assert semconv_pin()["gen_ai.semconv"] == GEN_AI_SEMCONV_VERSION


def test_read_stage_timings_from_an_instrumented_target() -> None:
    trace = {
        "spans": [
            {"name": "stage:detect", "duration_ms": 12.5},
            {"name": "stage:decide", "duration_ms": 4.0},
            {"name": "c1", "duration_ms": 99.0},
        ]
    }
    assert read_stage_timings(trace) == {"detect": 12.5, "decide": 4.0}


def test_span_coverage_and_gate() -> None:
    trace = emit_drill(_findings())
    assert span_coverage(_findings(), trace) == 1.0
    require_span_coverage(_findings(), trace)

    partial = {"spans": [{"name": "agentdrill.drill"}, {"name": "c1"}]}
    assert span_coverage(_findings(), partial) == 0.5
    with pytest.raises(OTelError):
        require_span_coverage(_findings(), partial)
    require_span_coverage(_findings(), partial, minimum=0.5)


def test_emit_drill_fails_loudly_without_cases() -> None:
    with pytest.raises(OTelError):
        emit_drill([])


def test_span_coverage_fails_loudly_without_cases() -> None:
    with pytest.raises(OTelError):
        span_coverage([], {"spans": []})


def test_cli_export_otel_from_report(tmp_path) -> None:
    import json

    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main
    from agentdrill.oracles.engine import OutcomeSplit
    from agentdrill.reporting import Report, ReportRow

    report = Report(
        title="drill",
        pack_ref="incidents-core@1.0.0+deadbeef",
        generated="2026-10-24T00:00:00Z",
        outcome=OutcomeSplit(missed=1),
        rows=[ReportRow(case_id="c1", outcome="missed")],
    )
    report_path = tmp_path / "report.json"
    report_path.write_text(report.model_dump_json(), encoding="utf-8")
    result = CliRunner().invoke(main, ["export", "otel", "--report", str(report_path)])
    assert result.exit_code == 0, result.output
    trace = json.loads(result.output)
    assert trace["semconv"]["gen_ai.semconv"] == GEN_AI_SEMCONV_VERSION
    require_span_coverage([IntegrationFinding(case_id="c1", outcome="missed")], trace)
