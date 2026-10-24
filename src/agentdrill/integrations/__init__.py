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
    "DEFAULT_SUITE_NAME",
    "SARIF_LEVEL",
    "SARIF_SCHEMA_URI",
    "SARIF_VERSION",
    "FindingOutcome",
    "IntegrationFinding",
    "JUnitError",
    "SarifError",
    "WaiverRecord",
    "apply_waivers",
    "findings_from_report",
    "render_sarif",
    "to_junit",
    "to_sarif",
    "validate_junit",
    "validate_sarif",
]
