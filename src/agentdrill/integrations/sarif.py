"""SARIF 2.1.0 emitter (M26 26.1, R74).

Emit findings as a SARIF 2.1.0 log for GitHub/GitLab code scanning and IDEs:
**rule = case id**; the result level reflects the outcome; ``properties`` carry
the severity vector, attacker ``tier``/``k``, the independent ``witness`` ref and
the ASI/ATLAS tags; ``partialFingerprints`` give a stable, dedup-able identity;
``suppressions`` map waivers. Every log validates against the official OASIS
schema (vendored under ``schemas/``) before it is returned.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from agentdrill.integrations.model import SARIF_LEVEL, IntegrationFinding

#: The SARIF version this emitter produces.
SARIF_VERSION = "2.1.0"

#: The official SARIF 2.1.0 schema URI (written into every log).
SARIF_SCHEMA_URI = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)

#: The default tool identity.
DEFAULT_TOOL_NAME = "agentdrill"
DEFAULT_TOOL_VERSION = "0.1.0"
DEFAULT_INFORMATION_URI = "https://github.com/agentic-suite/agentsec-agentdrill"

#: The vendored official schema, validated offline.
_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "sarif-2.1.0.json"


class SarifError(ValueError):
    """Raised when a SARIF log cannot be built or fails schema validation."""


def _properties(finding: IntegrationFinding) -> dict[str, Any]:
    """The SARIF ``properties`` bag (the severity vector + evidence fields)."""
    props: dict[str, Any] = {"outcome": finding.outcome, "tags": list(finding.tags)}
    if finding.severity is not None:
        props["severity"] = finding.severity
    if finding.tier is not None:
        props["tier"] = finding.tier
    if finding.k is not None:
        props["k"] = finding.k
    if finding.witness_ref is not None:
        props["witness"] = finding.witness_ref
    if finding.trace_ref is not None:
        props["trace"] = finding.trace_ref
    return props


def _rule(finding: IntegrationFinding) -> dict[str, Any]:
    """A reporting descriptor for a case (rule = case id)."""
    rule: dict[str, Any] = {
        "id": finding.case_id,
        "shortDescription": {"text": finding.rationale or finding.case_id},
        "defaultConfiguration": {"level": SARIF_LEVEL[finding.outcome]},
        "properties": {"tags": list(finding.tags)},
    }
    if finding.severity is not None:
        rule["properties"]["severity"] = finding.severity
    return rule


def _result(finding: IntegrationFinding, rule_index: int) -> dict[str, Any]:
    """A SARIF result for one case."""
    level = SARIF_LEVEL.get(finding.outcome)
    if level is None:
        raise SarifError(f"case {finding.case_id!r}: unknown outcome {finding.outcome!r}")
    result: dict[str, Any] = {
        "ruleId": finding.case_id,
        "ruleIndex": rule_index,
        "level": level,
        "message": {"text": finding.rationale or f"{finding.outcome}: {finding.case_id}"},
        "partialFingerprints": {"agentdrill/v1": finding.partial_fingerprint()},
        "properties": _properties(finding),
    }
    if finding.pack:
        result["locations"] = [
            {"physicalLocation": {"artifactLocation": {"uri": finding.pack}}}
        ]
    if finding.waived:
        result["suppressions"] = [
            {"kind": "external", "justification": finding.waiver_reason or "waived"}
        ]
    return result


def to_sarif(
    findings: Sequence[IntegrationFinding],
    *,
    tool_name: str = DEFAULT_TOOL_NAME,
    tool_version: str = DEFAULT_TOOL_VERSION,
    information_uri: str = DEFAULT_INFORMATION_URI,
) -> dict[str, Any]:
    """Build a valid SARIF 2.1.0 log from ``findings``.

    Raises:
        SarifError: The built log fails official schema validation.
    """
    rules: list[dict[str, Any]] = []
    rule_index: dict[str, int] = {}
    results: list[dict[str, Any]] = []
    for finding in findings:
        if finding.case_id not in rule_index:
            rule_index[finding.case_id] = len(rules)
            rules.append(_rule(finding))
        results.append(_result(finding, rule_index[finding.case_id]))

    driver: dict[str, Any] = {
        "name": tool_name,
        "version": tool_version,
        "informationUri": information_uri,
        "rules": rules,
    }
    log: dict[str, Any] = {
        "$schema": SARIF_SCHEMA_URI,
        "version": SARIF_VERSION,
        "runs": [{"tool": {"driver": driver}, "results": results}],
    }
    validate_sarif(log)
    return log


def render_sarif(findings: Sequence[IntegrationFinding], **kwargs: Any) -> str:
    """Build and serialize the SARIF log as pretty JSON."""
    return json.dumps(to_sarif(findings, **kwargs), indent=2) + "\n"


def validate_sarif(log: dict[str, Any]) -> None:
    """Validate ``log`` against the vendored official SARIF 2.1.0 schema.

    Raises:
        SarifError: The log is not a valid SARIF 2.1.0 log, or the schema is
            unavailable.
    """
    try:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    except OSError as exc:  # pragma: no cover - a broken install, not a code path
        raise SarifError(f"SARIF schema unavailable at {_SCHEMA_PATH}: {exc}") from exc

    from jsonschema.validators import validator_for  # type: ignore[import-untyped]

    validator = validator_for(schema)(schema)
    for error in validator.iter_errors(log):
        path = " -> ".join(str(part) for part in error.absolute_path) or "(root)"
        raise SarifError(f"invalid SARIF at {path}: {error.message}")
