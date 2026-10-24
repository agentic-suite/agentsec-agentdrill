"""M25 25.5 — neutrality process, F91 (RED → GREEN).

Published rules, pre-registration, equal rules for every defense, a corrections
log and author review; the process is documented and enforced.
"""

from __future__ import annotations

import pytest

from agentdrill.byod import (
    CorrectionsLog,
    NeutralityError,
    NeutralityRules,
    author_review_needed,
    default_rules,
    require_neutrality,
)


def test_default_rules_are_published_and_preregistered() -> None:
    rules = default_rules()
    assert isinstance(rules, NeutralityRules)
    assert rules.published is True
    assert rules.preregistered is True
    assert rules.equal_rules is True
    assert rules.rules
    require_neutrality(rules)  # no raise


def test_unpublished_rules_fail_enforcement() -> None:
    rules = default_rules()
    rules.published = False
    with pytest.raises(NeutralityError, match="publish"):
        require_neutrality(rules)


def test_corrections_log_records_fixes() -> None:
    log = CorrectionsLog()
    log.add(when="2026-10-23", what="re-ran head-to-head after a seed fix")
    assert log.entries[0].what == "re-ran head-to-head after a seed fix"


def test_author_review_flag_on_author_overlap() -> None:
    # When a defense's authors overlap the benchmark's authors, an independent
    # author review is required (a conflict must be disclosed).
    assert author_review_needed(authors=["agentdrill"], reviewers=["agentdrill"]) is True
    assert author_review_needed(authors=["agentdrill"], reviewers=["acme"]) is False
