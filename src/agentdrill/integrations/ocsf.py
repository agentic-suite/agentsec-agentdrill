"""OCSF + ECS emitters (M26 26.3, R74).

OCSF **Detection Finding** (class 2004, category *Findings*) events for a
SIEM/data lake, carrying the ATT&CK/ATLAS technique when the case has one, the
attacker tier and the witness ref in ``unmapped``, and a waiver as OCSF status
*Suppressed*. ECS 8.x ``alert`` events for the same findings. Each emitter
validates the required OCSF/ECS fields before returning.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from agentdrill.integrations.model import IntegrationFinding

#: The OCSF schema version this emitter targets.
OCSF_VERSION = "1.3.0"

#: Detection Finding (class 2004) in the Findings category (2).
DETECTION_FINDING_CLASS_UID = 2004
DETECTION_FINDING_CLASS_NAME = "Detection Finding"
FINDINGS_CATEGORY_UID = 2
FINDINGS_CATEGORY_NAME = "Findings"

#: Detection-Finding activity/status ids used here.
ACTIVITY_CREATE = 1
STATUS_NEW = 1
STATUS_SUPPRESSED = 3

#: OCSF severity_id per rated severity.
_SEVERITY_ID: dict[str, int] = {"critical": 5, "high": 4, "medium": 3, "low": 2}
#: Fallback severity_id per outcome (0 unknown, 1 informational, 4 high, 3 medium).
_OUTCOME_SEVERITY_ID: dict[str, int] = {"missed": 4, "degraded": 3, "blocked": 1, "untested": 0}

#: The ECS version this emitter targets.
ECS_VERSION = "8.11.0"

#: A deterministic default ECS timestamp (tests and reproducible exports).
ECS_EPOCH = "1970-01-01T00:00:00.000Z"


class OCSFValidationError(ValueError):
    """Raised when an OCSF event is missing a required field or carries a bad value."""


class ECSValidationError(ValueError):
    """Raised when an ECS event is missing a required field or carries a bad value."""


def _atlas_techniques(tags: Sequence[str]) -> list[dict[str, Any]]:
    """ATLAS techniques from a case's tags, as OCSF ``attacks`` entries."""
    prefix = "ATLAS-"
    return [
        {"technique": {"uid": tag[len(prefix) :], "name": tag}}
        for tag in tags
        if tag.startswith(prefix)
    ]


def to_ocsf_findings(
    findings: Sequence[IntegrationFinding],
    *,
    product_name: str = "agentdrill",
    version: str = OCSF_VERSION,
    timestamp_ms: int = 0,
) -> list[dict[str, Any]]:
    """Emit one OCSF Detection Finding per case.

    Raises:
        OCSFValidationError: A built event fails :func:`validate_ocsf`.
    """
    events: list[dict[str, Any]] = []
    for finding in findings:
        severity_id = _SEVERITY_ID.get(
            finding.severity or "", _OUTCOME_SEVERITY_ID[finding.outcome]
        )
        event: dict[str, Any] = {
            "class_uid": DETECTION_FINDING_CLASS_UID,
            "class_name": DETECTION_FINDING_CLASS_NAME,
            "category_uid": FINDINGS_CATEGORY_UID,
            "category_name": FINDINGS_CATEGORY_NAME,
            "activity_id": ACTIVITY_CREATE,
            "activity_name": "Create",
            "severity_id": severity_id,
            "status_id": STATUS_SUPPRESSED if finding.waived else STATUS_NEW,
            "time": timestamp_ms,
            "metadata": {"version": version, "product": {"name": product_name}},
            "finding_info": {
                "title": finding.case_id,
                "uid": finding.case_id,
                "desc": finding.rationale or f"{finding.outcome}: {finding.case_id}",
            },
            "unmapped": {
                "outcome": finding.outcome,
                "pack": finding.pack,
                "tier": finding.tier,
                "witness": finding.witness_ref,
                "tags": list(finding.tags),
            },
        }
        attacks = _atlas_techniques(finding.tags)
        if attacks:
            event["attacks"] = attacks
        events.append(event)
    validate_ocsf(events)
    return events


def validate_ocsf(events: Sequence[dict[str, Any]]) -> None:
    """Validate the required OCSF Detection Finding fields on every event.

    Raises:
        OCSFValidationError: A required field is missing or has a bad value.
    """
    for event in events:
        for field in (
            "class_uid",
            "class_name",
            "category_uid",
            "category_name",
            "activity_id",
            "activity_name",
            "severity_id",
            "status_id",
            "time",
            "metadata",
            "finding_info",
        ):
            if field not in event:
                raise OCSFValidationError(f"OCSF event missing required field {field!r}")
        if event["class_uid"] != DETECTION_FINDING_CLASS_UID:
            raise OCSFValidationError(f"unexpected class_uid {event['class_uid']!r}")
        if event["category_uid"] != FINDINGS_CATEGORY_UID:
            raise OCSFValidationError(f"unexpected category_uid {event['category_uid']!r}")
        if not isinstance(event["severity_id"], int) or not 0 <= event["severity_id"] <= 6:
            raise OCSFValidationError(f"bad severity_id {event['severity_id']!r}")
        if not isinstance(event["time"], int):
            raise OCSFValidationError(f"time must be an integer (epoch ms): {event['time']!r}")
        metadata = event["metadata"]
        if not metadata.get("version") or not metadata.get("product", {}).get("name"):
            raise OCSFValidationError("metadata must carry version and product.name")
        finding_info = event["finding_info"]
        if not finding_info.get("uid") or not finding_info.get("title"):
            raise OCSFValidationError("finding_info must carry uid and title")


def to_ecs_events(
    findings: Sequence[IntegrationFinding], *, timestamp: str = ECS_EPOCH
) -> list[dict[str, Any]]:
    """Emit one ECS 8.x ``alert`` event per case.

    Raises:
        ECSValidationError: A built event fails :func:`validate_ecs`.
    """
    events: list[dict[str, Any]] = []
    for finding in findings:
        outcome = "failure" if finding.outcome in ("missed", "degraded") else "success"
        event: dict[str, Any] = {
            "@timestamp": timestamp,
            "event": {
                "kind": "alert",
                "category": ["intrusion_detection"],
                "action": finding.outcome,
                "outcome": outcome,
                "severity": finding.severity or finding.outcome,
            },
            "rule": {"id": finding.case_id, "name": finding.case_id},
            "message": finding.rationale or f"{finding.outcome}: {finding.case_id}",
            "tags": list(finding.tags),
            "service": {"name": "agentdrill"},
        }
        techniques = [
            {"id": tag[len("ATLAS-") :], "name": tag}
            for tag in finding.tags
            if tag.startswith("ATLAS-")
        ]
        if techniques:
            event["threat"] = {"technique": techniques[0]}
        events.append(event)
    validate_ecs(events)
    return events


def validate_ecs(events: Sequence[dict[str, Any]]) -> None:
    """Validate the required ECS fields on every event.

    Raises:
        ECSValidationError: A required field is missing or has a bad value.
    """
    for event in events:
        if not event.get("@timestamp"):
            raise ECSValidationError("ECS event missing @timestamp")
        inner = event.get("event")
        if not isinstance(inner, dict):
            raise ECSValidationError("ECS event missing the event object")
        for field in ("kind", "category", "action", "outcome"):
            if field not in inner:
                raise ECSValidationError(f"ECS event object missing {field!r}")
        if inner["kind"] != "alert":
            raise ECSValidationError(f"unexpected event.kind {inner['kind']!r}")
        if not isinstance(inner["category"], list) or not inner["category"]:
            raise ECSValidationError("event.category must be a non-empty list")
        if inner["outcome"] not in ("success", "failure", "unknown"):
            raise ECSValidationError(f"bad event.outcome {inner['outcome']!r}")
