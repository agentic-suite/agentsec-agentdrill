"""Neutrality process (M25 25.5, F91).

Published rules, pre-registration, equal rules for every defense, a corrections
log and author review — the process is documented and enforced. Design:
``docs/prd/29-bring-your-own-defense.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.byod.head_to_head import NeutralityError


class NeutralityRules(BaseModel):
    """The published, pre-registered rules of a neutral head-to-head."""

    rules: list[str] = Field(default_factory=list)
    published: bool = False
    preregistered: bool = False
    equal_rules: bool = False


class Correction(BaseModel):
    """One entry in the corrections log."""

    when: str
    what: str


class CorrectionsLog(BaseModel):
    """The corrections log (every correction to a published result is recorded)."""

    entries: list[Correction] = Field(default_factory=list)

    def add(self, *, when: str, what: str) -> Correction:
        """Record a correction."""
        entry = Correction(when=when, what=what)
        self.entries.append(entry)
        return entry


def default_rules() -> NeutralityRules:
    """The default neutrality rules (published + pre-registered + equal)."""
    return NeutralityRules(
        rules=[
            "publish the rules before running the head-to-head",
            "pre-register the metrics, seeds and thresholds",
            "apply the same rules and budget to every defense",
            "record every correction in the corrections log",
            "disclose author overlap and require an independent review",
        ],
        published=True,
        preregistered=True,
        equal_rules=True,
    )


def require_neutrality(rules: NeutralityRules) -> None:
    """Fail loudly if the neutrality process is not honoured.

    Raises:
        NeutralityError: The rules were not published, pre-registered or applied
            equally.
    """
    if not rules.published:
        raise NeutralityError("neutrality rules must be published before the run")
    if not rules.preregistered:
        raise NeutralityError("neutrality metrics/seeds/thresholds must be pre-registered")
    if not rules.equal_rules:
        raise NeutralityError("the same rules and budget must apply to every defense")


def author_review_needed(*, authors: list[str], reviewers: list[str]) -> bool:
    """Whether an independent author review is required (author overlap)."""
    return bool(set(authors) & set(reviewers))
