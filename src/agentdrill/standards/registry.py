"""Standards master table, version pins + evidence index (M30 30.6, F104).

The **master standards table** with **version pins** and a **drift watcher** (a
pin that has not been refreshed within 30 days fails); **ASI coverage** that
shows `untested`; an **ATLAS-mitigation** mapping; and a per-framework **evidence
index** that lists `not covered` **explicitly** -- a silent "fully covered" claim
is refused. Design: ``docs/design/trace-explorer-and-platform-standards.md``;
PRD 42 (R78).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

from pydantic import BaseModel, Field

from agentdrill.frontier import ASI_CATEGORIES

#: The maximum age of a version pin, in days.
PIN_MAX_AGE_DAYS = 30


class StandardsError(ValueError):
    """Raised when a pin drifts, a table is stale, or a gap is undecalred."""


class StandardPin(BaseModel):
    """One row of the master standards table."""

    name: str
    version: str
    updated: str
    uri: str = ""


class Drift(BaseModel):
    """A pin that disagrees with the published standard version."""

    standard: str
    pinned: str
    published: str


class EvidenceIndexEntry(BaseModel):
    """Per-framework evidence: what is covered and what is **not**."""

    framework: str
    covered: list[str] = Field(default_factory=list)
    not_covered: list[str] = Field(default_factory=list)
    #: Must be set to True to claim there are no gaps (never implied).
    fully_covered: bool = False


#: The ATLAS-technique -> mitigation (control) mapping.
_ATLAS_MITIGATION: dict[str, str] = {
    "ATLAS-AML.T0051": "treat model output as data; enforce tool allow-lists",
    "ATLAS-AML.T0048": "deny egress to unlisted hosts; DLP on tool results",
    "ATLAS-AML.T0057": "provenance-tag and isolate memory stores",
    "ATLAS-AML.T0011": "require step-up plus a rendered diff before approval",
    "ATLAS-AML.T0055": "scope tokens to the task; enforce RFC 8707 audience",
}


def detect_drift(
    pins: Sequence[StandardPin], published: Mapping[str, str]
) -> list[Drift]:
    """Pins whose version disagrees with the published standard version."""
    drift: list[Drift] = []
    for pin in pins:
        current = published.get(pin.name)
        if current is not None and current != pin.version:
            drift.append(Drift(standard=pin.name, pinned=pin.version, published=current))
    return drift


def require_no_drift(pins: Sequence[StandardPin], published: Mapping[str, str]) -> None:
    """Fail loudly if any pin has drifted from a published standard.

    Raises:
        StandardsError: A pin drifted.
    """
    drift = detect_drift(pins, published)
    if drift:
        detail = ", ".join(f"{d.standard}: {d.pinned} -> {d.published}" for d in drift)
        raise StandardsError(f"standards drift detected: {detail}")


def require_pins_current(
    pins: Sequence[StandardPin], *, now: str, max_age_days: int = PIN_MAX_AGE_DAYS
) -> None:
    """Fail loudly if a pin has not been refreshed within ``max_age_days``.

    Raises:
        StandardsError: A pin is stale.
    """
    today = date.fromisoformat(now)
    for pin in pins:
        age = (today - date.fromisoformat(pin.updated)).days
        if age > max_age_days:
            raise StandardsError(
                f"pin {pin.name!r} was updated {age} days ago (max {max_age_days})"
            )


def asi_coverage_table(verified: Sequence[str]) -> dict[str, str]:
    """Map every ASI category to ``verified`` or ``untested`` (never omitted)."""
    known = {category for category in verified if category in ASI_CATEGORIES}
    return {
        category: ("verified" if category in known else "untested")
        for category in ASI_CATEGORIES
    }


def atlas_mitigation_mapping() -> dict[str, str]:
    """The published ATLAS-technique -> mitigation (control) mapping."""
    return dict(_ATLAS_MITIGATION)


def build_evidence_index(
    frameworks: Mapping[str, tuple[Sequence[str], Sequence[str]]],
    *,
    fully_covered: Sequence[str] = (),
) -> list[EvidenceIndexEntry]:
    """Build the per-framework evidence index (``not_covered`` is always listed)."""
    return [
        EvidenceIndexEntry(
            framework=name,
            covered=list(covered),
            not_covered=list(not_covered),
            fully_covered=name in set(fully_covered),
        )
        for name, (covered, not_covered) in frameworks.items()
    ]


def require_explicit_gaps(index: Sequence[EvidenceIndexEntry]) -> None:
    """Fail loudly unless every no-gap claim is explicit (``fully_covered``).

    Raises:
        StandardsError: An entry claims full coverage without listing gaps, and
            without setting ``fully_covered``.
    """
    for entry in index:
        if not entry.not_covered and not entry.fully_covered:
            raise StandardsError(
                f"evidence index for {entry.framework!r} lists no gaps but does not "
                f"set fully_covered=True (gaps must be explicit)"
            )
