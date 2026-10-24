"""Security ecosystem integrations (M26) — emit findings where buyers work.

The outbound emitters turn the neutral :class:`IntegrationFinding` projection
into official interchange formats. 26.1 ships SARIF 2.1.0 and JUnit; later M26
items add OTel, OCSF/ECS, OSCAL, STIX, CI/ticketing adapters, inbound importers
and SIEM/EDR detection validation. Design: ``docs/design/integrations.md``.
"""

from agentdrill.integrations.code_scanning import (
    GITHUB_API_BASE,
    GITLAB_SAST_VERSION,
    CodeScanningError,
    github_code_scanning_request,
    to_gitlab_sast_report,
)
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
from agentdrill.integrations.ocsf import (
    DETECTION_FINDING_CLASS_UID,
    ECS_EPOCH,
    ECS_VERSION,
    OCSF_VERSION,
    ECSValidationError,
    OCSFValidationError,
    to_ecs_events,
    to_ocsf_findings,
    validate_ecs,
    validate_ocsf,
)
from agentdrill.integrations.oscal import (
    OSCAL_EPOCH,
    OSCAL_VERSION,
    OSCALValidationError,
    to_oscal_assessment_results,
    to_oscal_poam,
    validate_oscal,
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
from agentdrill.integrations.stix import (
    STIX_EPOCH,
    STIX_VERSION,
    STIXValidationError,
    to_stix_bundle,
    validate_stix,
)
from agentdrill.integrations.ticketing import (
    TICKET_VENDORS,
    TicketError,
    TicketVendor,
    render_ticket_body,
    ticket_endpoint,
    ticket_key,
    ticket_request,
)
from agentdrill.integrations.transport import (
    DELIVERY_DUPLICATE,
    DELIVERY_FAILED,
    DELIVERY_OK,
    DeliveryResult,
    HttpRequest,
    Transport,
    deliver_tickets,
)
from agentdrill.integrations.waivers import WaiverRecord, apply_waivers

__all__ = [
    "DEFAULT_INFORMATION_URI",
    "DEFAULT_MIN_SPAN_COVERAGE",
    "DEFAULT_SUITE_NAME",
    "DELIVERY_DUPLICATE",
    "DELIVERY_FAILED",
    "DELIVERY_OK",
    "DETECTION_FINDING_CLASS_UID",
    "DRILL_OPERATION",
    "ECS_EPOCH",
    "ECS_VERSION",
    "GEN_AI_SEMCONV_VERSION",
    "GITHUB_API_BASE",
    "GITLAB_SAST_VERSION",
    "OCSF_VERSION",
    "OSCAL_EPOCH",
    "OSCAL_VERSION",
    "SARIF_LEVEL",
    "SARIF_SCHEMA_URI",
    "SARIF_VERSION",
    "STAGE_PREFIX",
    "STIX_EPOCH",
    "STIX_VERSION",
    "TICKET_VENDORS",
    "CodeScanningError",
    "DeliveryResult",
    "ECSValidationError",
    "FindingOutcome",
    "HttpRequest",
    "IntegrationFinding",
    "JUnitError",
    "OCSFValidationError",
    "OSCALValidationError",
    "OTelError",
    "STIXValidationError",
    "SarifError",
    "TicketError",
    "TicketVendor",
    "Transport",
    "WaiverRecord",
    "apply_waivers",
    "deliver_tickets",
    "emit_drill",
    "findings_from_report",
    "github_code_scanning_request",
    "read_stage_timings",
    "render_sarif",
    "render_ticket_body",
    "require_span_coverage",
    "semconv_pin",
    "span_coverage",
    "ticket_endpoint",
    "ticket_key",
    "ticket_request",
    "to_ecs_events",
    "to_gitlab_sast_report",
    "to_junit",
    "to_ocsf_findings",
    "to_oscal_assessment_results",
    "to_oscal_poam",
    "to_sarif",
    "to_stix_bundle",
    "validate_ecs",
    "validate_junit",
    "validate_ocsf",
    "validate_oscal",
    "validate_sarif",
    "validate_stix",
]
