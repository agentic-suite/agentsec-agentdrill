"""Inbound import of external results (M26 26.5, R74).

Normalize result files from **Inspect / promptfoo / garak / AgentDojo / PyRIT**
into :class:`ImportedResult`s that carry the ``imported`` trust label (lower than
first-party evidence), and import a capability **inventory**. The parsers are
deliberately tolerant — each accepts a small set of well-known keys — but a
record with no identity, an unknown source, or a mapping rate below the gate
fails loudly. Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from agentdrill.integrations.model import IntegrationFinding

#: The supported inbound result sources.
ImportedSource = Literal["inspect", "promptfoo", "garak", "agentdojo", "pyrit"]

#: All supported sources, in a stable order.
IMPORTED_SOURCES: tuple[ImportedSource, ...] = (
    "inspect",
    "promptfoo",
    "garak",
    "agentdojo",
    "pyrit",
)

#: The trust label on every imported result (lower than first-party evidence).
IMPORTED_TRUST = "imported"

#: The minimum field-mapping rate required by the gate.
DEFAULT_MIN_MAPPING = 0.95

#: Record keys searched (in order) for a case identity.
_ID_KEYS = ("id", "case_id", "task_id", "probe", "objective", "description", "name")
#: Record keys whose truthiness means "the external tool blocked the attack".
_BLOCKED_KEYS = ("blocked", "passed", "success", "security", "detected")
#: Container keys searched (in order) for the record list.
_RECORD_KEYS = ("results", "samples", "cases", "items")
#: Container keys searched (in order) for an inventory list.
_INVENTORY_KEYS = ("inventory", "items", "nodes", "capabilities")


class IngestError(ValueError):
    """Raised when a source is unknown or its mapping is below the gate."""


class ImportedResult(BaseModel):
    """One external result normalized into the honest outcome vocabulary."""

    case_id: str
    source: str
    blocked: bool | None
    outcome: str
    severity: str | None = None
    tags: list[str] = Field(default_factory=list)
    rationale: str = ""
    trust: str = IMPORTED_TRUST


class InventoryItem(BaseModel):
    """One capability-inventory entry (the M27 attack-path graph consumes it)."""

    id: str
    kind: str
    name: str


def _unwrap(data: Any, key: str) -> Any:
    """Look for ``key`` at the top level and one level down."""
    if not isinstance(data, dict):
        return None
    value = data.get(key)
    if isinstance(value, (list, dict)):
        return value
    return None


def _records(data: Any, keys: tuple[str, ...] = _RECORD_KEYS) -> list[Any]:
    """Extract the record list from a source document (tolerantly)."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            value = _unwrap(data, key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                for nested in keys:
                    inner = value.get(nested)
                    if isinstance(inner, list):
                        return inner
        return []
    raise IngestError(f"expected a list or mapping, got {type(data).__name__}")


def _case_id(record: Any) -> str | None:
    """The case identity for a record, or ``None`` when there is none."""
    if not isinstance(record, dict):
        return None
    for key in _ID_KEYS:
        value = record.get(key)
        if value:
            return str(value).replace(" ", "-")
    variables = record.get("vars")
    if isinstance(variables, dict):
        for key in _ID_KEYS:
            value = variables.get(key)
            if value:
                return str(value).replace(" ", "-")
    return None


def _blocked(record: Any) -> bool | None:
    """Whether the external tool blocked the case, or ``None`` when unreported."""
    if not isinstance(record, dict):
        return None
    for key in _BLOCKED_KEYS:
        if key in record:
            return bool(record[key])
    scores = record.get("scores")
    if isinstance(scores, dict):
        for key in _BLOCKED_KEYS:
            if key in scores:
                return bool(scores[key])
    if "score" in record:
        try:
            return float(record["score"]) <= 0.0
        except (TypeError, ValueError):
            return None
    return None


def _outcome(blocked: bool | None) -> str:
    if blocked is None:
        return "untested"
    return "blocked" if blocked else "missed"


def import_results(data: Any, source: str) -> list[ImportedResult]:
    """Normalize a source document into imported results.

    Raises:
        IngestError: The source is unknown.
    """
    if source not in IMPORTED_SOURCES:
        raise IngestError(f"unknown import source: {source!r}; supported: {list(IMPORTED_SOURCES)}")
    results: list[ImportedResult] = []
    for record in _records(data):
        case_id = _case_id(record)
        if case_id is None:
            continue
        blocked = _blocked(record)
        results.append(
            ImportedResult(
                case_id=case_id,
                source=source,
                blocked=blocked,
                outcome=_outcome(blocked),
                tags=[source, IMPORTED_TRUST],
                rationale=f"imported from {source}",
            )
        )
    return results


def mapping_report(data: Any, source: str) -> tuple[int, int, float]:
    """Return ``(mapped, total, coverage)`` for a source document.

    Raises:
        IngestError: The source is unknown.
    """
    if source not in IMPORTED_SOURCES:
        raise IngestError(f"unknown import source: {source!r}; supported: {list(IMPORTED_SOURCES)}")
    records = _records(data)
    total = len(records)
    mapped = sum(1 for record in records if _case_id(record) is not None)
    coverage = 1.0 if total == 0 else mapped / total
    return mapped, total, coverage


def require_mapping(
    data: Any, source: str, *, minimum: float = DEFAULT_MIN_MAPPING
) -> None:
    """Fail loudly unless the source maps at least ``minimum`` of its records.

    Raises:
        IngestError: The mapping rate is below ``minimum``.
    """
    mapped, total, coverage = mapping_report(data, source)
    if coverage < minimum:
        raise IngestError(
            f"{source}: mapped {mapped}/{total} records ({coverage:.0%}) "
            f"below the required {minimum:.0%}"
        )


def to_imported_findings(results: Sequence[ImportedResult]) -> list[IntegrationFinding]:
    """Project imported results into findings marked ``imported``."""
    return [
        IntegrationFinding(
            case_id=result.case_id,
            outcome=result.outcome,  # type: ignore[arg-type]
            pack=f"imported:{result.source}",
            tags=sorted(set(result.tags) | {IMPORTED_TRUST}),
            severity=result.severity,
            rationale=result.rationale,
        )
        for result in results
    ]


def parse_inventory(data: Any) -> list[InventoryItem]:
    """Normalize a capability inventory; the M27 attack-path graph consumes it."""
    items: list[InventoryItem] = []
    for index, record in enumerate(_records(data, _INVENTORY_KEYS)):
        if not isinstance(record, dict):
            continue
        identity = record.get("id") or record.get("name") or f"item-{index}"
        items.append(
            InventoryItem(
                id=str(identity),
                kind=str(record.get("kind") or record.get("type") or "unknown"),
                name=str(record.get("name") or identity),
            )
        )
    return items
