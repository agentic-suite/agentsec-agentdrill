"""M30 30.7 — standards participation (RED -> GREEN).

Track submissions to the standards bodies (OWASP ASI, MITRE ATLAS, NIST CAISI,
IETF BMWG, OTel SIG) with the rule that **>=1 is in review per release**, and
expose the mapping repository layout.
"""

from __future__ import annotations

import pytest

from agentdrill.standards import (
    BODIES,
    SUBMISSION_STATES,
    StandardsError,
    Submission,
    mapping_index,
    require_bodies_covered,
    require_valid_body,
    submission_summary,
)


def _sub(body: str, state: str = "in_review", **over: object) -> Submission:
    base = dict(body=body, title=f"{body} submission", state=state, submitted="2026-02-01")
    base.update(over)
    return Submission.model_validate(base)


def test_the_standards_bodies_and_states() -> None:
    assert set(BODIES) == {"OWASP ASI", "MITRE ATLAS", "NIST CAISI", "IETF BMWG", "OTel SIG"}
    assert set(SUBMISSION_STATES) == {"draft", "in_review", "accepted", "rejected"}


def test_at_least_one_in_review_per_release() -> None:
    require_bodies_covered([_sub("OWASP ASI"), _sub("MITRE ATLAS", state="draft")])
    with pytest.raises(StandardsError):
        require_bodies_covered([_sub("NIST CAISI", state="draft")])
    with pytest.raises(StandardsError):
        require_bodies_covered([])


def test_an_unknown_body_fails_loudly() -> None:
    require_valid_body("MITRE ATLAS")
    with pytest.raises(StandardsError):
        require_valid_body("MySpace Standards")
    bogus = _sub("OWASP ASI").model_copy(update={"body": "nope"})
    with pytest.raises(StandardsError):
        require_bodies_covered([bogus])


def test_submission_summary_reports_the_state_per_body() -> None:
    summary = submission_summary(
        [_sub("OWASP ASI"), _sub("NIST CAISI", state="draft"), _sub("OWASP ASI", state="accepted")]
    )
    assert summary["OWASP ASI"] == "accepted"
    assert summary["NIST CAISI"] == "draft"


def test_the_mapping_repository_layout_is_exposed() -> None:
    index = mapping_index()
    assert index
    assert all(isinstance(path, str) and path.endswith(".md") for path in index.values())
