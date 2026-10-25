"""OpenTelemetry emit/read for drills (M26 26.2, R74).

Emit one **trace per drill** and one **span per case**, decorated with the
pinned GenAI semantic-convention attributes plus the evidence fields a published
result must carry (outcome, attacker tier, independent witness ref, stage
timings). It also reads stage timings back from an **instrumented target**'s
trace, and gates on span coverage (≥ 95 %) so a partial trace fails loudly.

Transport is delegated to the ported :class:`~agentdrill.observability.tracing.
OpenTelemetryTracer` (single source of truth) — this module only maps the drill
model onto it. Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from agentdrill.integrations.model import IntegrationFinding
from agentdrill.observability.tracing import OpenTelemetryTracer

#: The pinned GenAI semantic-convention version this emitter targets.
GEN_AI_SEMCONV_VERSION = "1.29.0"

#: The default root span name (drill = trace).
DRILL_OPERATION = "agentdrill.drill"

#: The prefix marking a stage-timing span in an instrumented target's trace.
STAGE_PREFIX = "stage:"

#: The minimum fraction of cases that must appear as spans.
DEFAULT_MIN_SPAN_COVERAGE = 0.95


class OTelError(ValueError):
    """Raised when a drill trace cannot be emitted or a trace fails its gate."""


def semconv_pin(version: str = GEN_AI_SEMCONV_VERSION) -> dict[str, str]:
    """The semantic-convention pin recorded in every emitted trace/manifest."""
    return {"gen_ai.semconv": version}


def _attributes(
    finding: IntegrationFinding, stages: Mapping[str, float]
) -> dict[str, Any]:
    """GenAI + evidence attributes for one case span."""
    attrs: dict[str, Any] = {
        "gen_ai.system": "agentdrill",
        "gen_ai.operation.name": "run_case",
        "agentdrill.case.id": finding.case_id,
        "agentdrill.outcome": finding.outcome,
    }
    if finding.tier is not None:
        attrs["agentdrill.tier"] = finding.tier
    if finding.witness_ref is not None:
        attrs["agentdrill.witness"] = finding.witness_ref
    for stage, milliseconds in stages.items():
        attrs[f"agentdrill.stage.{stage}_ms"] = milliseconds
    return attrs


def emit_drill(
    findings: Sequence[IntegrationFinding],
    *,
    service_name: str = "agentdrill",
    semconv_version: str = GEN_AI_SEMCONV_VERSION,
    stage_timings: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, Any]:
    """Emit a drill trace: one trace, one span per case.

    Args:
        findings: The cases in the drill.
        service_name: OTel resource service name.
        semconv_version: The pinned GenAI semconv version to record.
        stage_timings: Optional ``case_id -> {stage: ms}`` timings to attach.

    Raises:
        OTelError: There are no cases to emit.
    """
    if not findings:
        raise OTelError("no cases to emit")
    stages = stage_timings or {}
    tracer = OpenTelemetryTracer(service_name=service_name)
    tracer.start_trace(DRILL_OPERATION)
    for finding in findings:
        span = tracer.start_span(finding.case_id)
        tracer.end_span(span, attributes=_attributes(finding, stages.get(finding.case_id, {})))
    trace = tracer.to_dict()
    trace["semconv"] = semconv_pin(semconv_version)
    return trace


def read_stage_timings(trace: dict[str, Any]) -> dict[str, float]:
    """Read stage timings from an instrumented target's trace.

    Stage spans are named ``stage:<name>`` and carry ``duration_ms``.
    """
    timings: dict[str, float] = {}
    for span in trace.get("spans", []):
        name = str(span.get("name", ""))
        if not name.startswith(STAGE_PREFIX):
            continue
        duration = span.get("duration_ms")
        if duration is not None:
            timings[name[len(STAGE_PREFIX) :]] = float(duration)
    return timings


def span_coverage(
    findings: Sequence[IntegrationFinding], trace: dict[str, Any]
) -> float:
    """The fraction of ``findings`` that appear as spans in ``trace``.

    Raises:
        OTelError: There are no cases to measure coverage against.
    """
    if not findings:
        raise OTelError("no cases to measure span coverage against")
    names = {str(span.get("name", "")) for span in trace.get("spans", [])}
    covered = sum(1 for finding in findings if finding.case_id in names)
    return covered / len(findings)


def require_span_coverage(
    findings: Sequence[IntegrationFinding],
    trace: dict[str, Any],
    *,
    minimum: float = DEFAULT_MIN_SPAN_COVERAGE,
) -> None:
    """Fail loudly unless span coverage is at least ``minimum``."""
    coverage = span_coverage(findings, trace)
    if coverage < minimum:
        raise OTelError(
            f"span coverage {coverage:.0%} is below the required {minimum:.0%} "
            f"({len(findings)} cases)"
        )
