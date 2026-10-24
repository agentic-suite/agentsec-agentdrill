"""Standards participation (M30 30.7, F104).

Track the submissions agentdrill makes to the standards bodies -- **OWASP ASI,
MITRE ATLAS, NIST CAISI, IETF BMWG, OTel SIG** -- and the **mapping repository**
that holds the per-framework mappings. A release must have **at least one
submission in review**. Design:
``docs/design/trace-explorer-and-platform-standards.md``; PRD 42 (R78).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel

from agentdrill.standards.registry import StandardsError

#: The standards bodies agentdrill participates in.
BODIES: tuple[str, ...] = (
    "OWASP ASI",
    "MITRE ATLAS",
    "NIST CAISI",
    "IETF BMWG",
    "OTel SIG",
)

#: The lifecycle of a submission.
SubmissionState = Literal["draft", "in_review", "accepted", "rejected"]

#: The submission states as a runtime tuple.
SUBMISSION_STATES: tuple[str, ...] = ("draft", "in_review", "accepted", "rejected")

#: States that count as "in review or better" for the per-release gate.
_IN_REVIEW_OR_BETTER = frozenset({"in_review", "accepted"})

#: The mapping-repository layout (framework -> mapping document).
_MAPPING_INDEX: dict[str, str] = {
    "OWASP ASI": "mappings/owasp-asi.md",
    "MITRE ATLAS": "mappings/mitre-atlas.md",
    "NIST AI RMF": "mappings/nist-ai-rmf.md",
    "EU AI Act": "mappings/eu-ai-act.md",
    "ISO 42001": "mappings/iso-42001.md",
    "OTel GenAI": "mappings/otel-genai.md",
}


class Submission(BaseModel):
    """One standards submission."""

    body: str
    title: str
    state: SubmissionState = "draft"
    submitted: str = ""
    url: str = ""


def require_valid_body(body: str) -> None:
    """Fail loudly unless ``body`` is a tracked standards body.

    Raises:
        StandardsError: The body is unknown.
    """
    if body not in BODIES:
        raise StandardsError(f"unknown standards body {body!r}; known: {list(BODIES)}")


def require_bodies_covered(
    submissions: Sequence[Submission], *, minimum: int = 1
) -> None:
    """Fail loudly unless at least ``minimum`` submissions are in review or better.

    Raises:
        StandardsError: Too few submissions are in review; or a body is unknown.
    """
    for submission in submissions:
        require_valid_body(submission.body)
    in_review = [s for s in submissions if s.state in _IN_REVIEW_OR_BETTER]
    if len(in_review) < minimum:
        raise StandardsError(
            f"release needs >= {minimum} submission(s) in review; "
            f"found {len(in_review)} of {len(submissions)}"
        )


def submission_summary(submissions: Sequence[Submission]) -> dict[str, str]:
    """The latest state per body (later entries win)."""
    summary: dict[str, str] = {}
    for submission in submissions:
        summary[submission.body] = submission.state
    return summary


def mapping_index() -> dict[str, str]:
    """The mapping-repository layout (framework -> mapping document path)."""
    return dict(_MAPPING_INDEX)
