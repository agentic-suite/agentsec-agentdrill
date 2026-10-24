"""OSCAL emitters (M26 26.3, R74).

Emit a drill as an **OSCAL assessment-results** document (one *finding* and one
*observation* per case, with the honest ``target.status``) and a
**plan-of-action-and-milestones** (POA&M) listing the open — missed/degraded —
items. The waiver/ledger mapping is the M28 seam: until the exposure ledger
lands, POA&M items are derived from the report's outcomes.
UUIds are derived (``uuid5``) so exports are stable and dedup-able.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from agentdrill.integrations.model import IntegrationFinding

#: The OSCAL version this emitter targets.
OSCAL_VERSION = "1.1.2"

#: A deterministic default ``last-modified`` / ``start`` / ``end`` timestamp.
OSCAL_EPOCH = "1970-01-01T00:00:00Z"

#: Outcomes that represent an open (un-blocked) risk.
_OPEN_OUTCOMES = ("missed", "degraded")


class OSCALValidationError(ValueError):
    """Raised when an OSCAL document is missing a required field."""


def _uuid5(kind: str, key: str) -> str:
    """A stable UUID for ``kind``/``key`` (deterministic across exports)."""
    return str(uuid5(NAMESPACE_URL, f"agentdrill:{kind}:{key}"))


def _metadata(title: str, last_modified: str) -> dict[str, str]:
    return {
        "title": title,
        "last-modified": last_modified,
        "version": "0.1.0",
        "oscal-version": OSCAL_VERSION,
    }


def to_oscal_assessment_results(
    findings: Sequence[IntegrationFinding],
    *,
    title: str,
    start: str = OSCAL_EPOCH,
    end: str = OSCAL_EPOCH,
) -> dict[str, Any]:
    """Emit an OSCAL ``assessment-results`` document for a drill.

    Raises:
        OSCALValidationError: The built document fails :func:`validate_oscal`.
    """
    observations: list[dict[str, Any]] = []
    findings_json: list[dict[str, Any]] = []
    for finding in findings:
        observation_uuid = _uuid5("observation", finding.case_id)
        observations.append(
            {
                "uuid": observation_uuid,
                "description": finding.rationale or f"{finding.outcome}: {finding.case_id}",
                "methods": ["TEST"],
                "collected": start,
                "relevant-evidence": [{"href": f"#evidence/{finding.case_id}"}],
            }
        )
        state = "not-satisfied" if finding.outcome in _OPEN_OUTCOMES else "satisfied"
        findings_json.append(
            {
                "uuid": _uuid5("finding", finding.case_id),
                "title": finding.case_id,
                "description": finding.rationale or f"{finding.outcome}: {finding.case_id}",
                "target": {
                    "type": "objective-id",
                    "target-id": finding.case_id,
                    "status": {"state": state},
                },
                "related-observations": [{"observation-uuid": observation_uuid}],
            }
        )
    document: dict[str, Any] = {
        "assessment-results": {
            "uuid": _uuid5("assessment-results", title),
            "metadata": _metadata(title, end),
            "import-ap": {"href": "#assessment-plan"},
            "results": [
                {
                    "uuid": _uuid5("result", title),
                    "title": title,
                    "description": f"{len(findings)} case(s) assessed",
                    "start": start,
                    "end": end,
                    "findings": findings_json,
                    "observations": observations,
                }
            ],
        }
    }
    validate_oscal(document)
    return document


def to_oscal_poam(
    findings: Sequence[IntegrationFinding],
    *,
    title: str,
    last_modified: str = OSCAL_EPOCH,
) -> dict[str, Any]:
    """Emit an OSCAL ``plan-of-action-and-milestones`` for the open findings.

    Raises:
        OSCALValidationError: The built document fails :func:`validate_oscal`.
    """
    items = [
        {
            "uuid": _uuid5("poam-item", finding.case_id),
            "title": finding.case_id,
            "description": finding.rationale or f"{finding.outcome}: {finding.case_id}",
            "props": [
                {"name": "outcome", "value": finding.outcome},
                {"name": "severity", "value": finding.severity or "unrated"},
            ],
        }
        for finding in findings
        if finding.outcome in _OPEN_OUTCOMES
    ]
    document: dict[str, Any] = {
        "plan-of-action-and-milestones": {
            "uuid": _uuid5("poam", title),
            "metadata": _metadata(title, last_modified),
            "poam-items": items,
        }
    }
    validate_oscal(document)
    return document


def _require(document: dict[str, Any], key: str, where: str) -> Any:
    if key not in document:
        raise OSCALValidationError(f"{where} missing required field {key!r}")
    return document[key]


def validate_oscal(document: dict[str, Any]) -> None:
    """Validate the required OSCAL assessment-results / POA&M fields.

    Raises:
        OSCALValidationError: The root model is unknown or a required field is
            missing.
    """
    if "assessment-results" in document:
        root = _require(document, "assessment-results", "document")
        metadata = _require(root, "metadata", "assessment-results")
        for key in ("title", "last-modified", "version", "oscal-version"):
            _require(metadata, key, "metadata")
        if metadata["oscal-version"] != OSCAL_VERSION:
            raise OSCALValidationError(f"unexpected oscal-version {metadata['oscal-version']!r}")
        _require(root, "uuid", "assessment-results")
        _require(root, "import-ap", "assessment-results")
        results = _require(root, "results", "assessment-results")
        if not isinstance(results, list):
            raise OSCALValidationError("assessment-results.results must be a list")
        for result in results:
            for key in ("uuid", "title", "description", "start", "end", "findings", "observations"):
                _require(result, key, "result")
        return

    if "plan-of-action-and-milestones" in document:
        root = _require(document, "plan-of-action-and-milestones", "document")
        metadata = _require(root, "metadata", "plan-of-action-and-milestones")
        for key in ("title", "last-modified", "version", "oscal-version"):
            _require(metadata, key, "metadata")
        _require(root, "uuid", "plan-of-action-and-milestones")
        items = _require(root, "poam-items", "plan-of-action-and-milestones")
        if not isinstance(items, list):
            raise OSCALValidationError("poam-items must be a list")
        for item in items:
            for key in ("uuid", "title", "description"):
                _require(item, key, "poam-item")
        return

    raise OSCALValidationError(
        "unknown OSCAL model: expected 'assessment-results' or 'plan-of-action-and-milestones'"
    )
