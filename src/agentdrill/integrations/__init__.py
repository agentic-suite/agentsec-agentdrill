"""Security ecosystem integrations (M26) — emit findings where buyers work.

The outbound emitters turn the neutral :class:`IntegrationFinding` projection
into official interchange formats. 26.1 ships SARIF 2.1.0 and JUnit; later M26
items add OTel, OCSF/ECS, OSCAL, STIX, CI/ticketing adapters, inbound importers
and SIEM/EDR detection validation. Design: ``docs/design/integrations.md``.
"""

from agentdrill.integrations.junit import (
    DEFAULT_SUITE_NAME,
    JUnitError,
    to_junit,
    validate_junit,
)
from agentdrill.integrations.model import (
    SARIF_LEVEL,
    FindingOutcome,
    IntegrationFinding,
    findings_from_report,
)
from agentdrill.integrations.otel import (
    DEFAULT_MIN_SPAN_COVERAGE,
    DRILL_OPERATION,
    GEN_AI_SEMCONV_VERSION,
    STAGE_PREFIX,
    OTelError,
    emit_drill,
    read_stage_timings,
    require_span_coverage,
    semconv_pin,
    span_coverage,
)
from agentdrill.integrations.sarif import (
    DEFAULT_INFORMATION_URI,
    SARIF_SCHEMA_URI,
    SARIF_VERSION,
    SarifError,
    render_sarif,
    to_sarif,
    validate_sarif,
)
from agentdrill.integrations.waivers import WaiverRecord, apply_waivers

__all__ = [
    "DEFAULT_INFORMATION_URI",
    "DEFAULT_MIN_SPAN_COVERAGE",
    "DEFAULT_SUITE_NAME",
    "DRILL_OPERATION",
    "GEN_AI_SEMCONV_VERSION",
    "SARIF_LEVEL",
    "SARIF_SCHEMA_URI",
    "SARIF_VERSION",
    "STAGE_PREFIX",
    "FindingOutcome",
    "IntegrationFinding",
    "JUnitError",
    "OTelError",
    "SarifError",
    "WaiverRecord",
    "apply_waivers",
    "emit_drill",
    "findings_from_report",
    "read_stage_timings",
    "render_sarif",
    "require_span_coverage",
    "semconv_pin",
    "span_coverage",
    "to_junit",
    "to_sarif",
    "validate_junit",
    "validate_sarif",
]
