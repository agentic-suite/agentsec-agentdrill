"""Observability and telemetry for AgentDrill evaluation runs.

Provides metrics collection, OpenTelemetry-compatible tracing, and export
formats (JSON, Prometheus, OTLP) — all without requiring the OpenTelemetry SDK.
"""

from __future__ import annotations

from agentdrill.observability.metrics import EvalMetrics, MetricsCollector
from agentdrill.observability.tracing import OpenTelemetryTracer, TraceContext, TraceSpan

__all__ = [
    "EvalMetrics",
    "MetricsCollector",
    "OpenTelemetryTracer",
    "TraceContext",
    "TraceSpan",
]
