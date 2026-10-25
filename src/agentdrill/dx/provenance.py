"""Provenance cards (M20 20.6, F74).

A machine-readable card per pack — sources, dates, mutation policy, author and
reviewers — rendered on results. Reviewer fields must be non-empty. Design:
``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CardError(ValueError):
    """Raised when a provenance card is incomplete."""


class ProvenanceCard(BaseModel):
    """A pack's machine-readable provenance card."""

    pack_ref: str
    author: str
    reviewers: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    dates: dict[str, str] = Field(default_factory=dict)
    mutation_policy: str = ""


def build_card(
    *,
    pack_ref: str,
    author: str,
    reviewers: list[str],
    sources: list[str],
    dates: dict[str, str],
    mutation_policy: str,
) -> ProvenanceCard:
    """Build a provenance card."""
    return ProvenanceCard(
        pack_ref=pack_ref,
        author=author,
        reviewers=list(reviewers),
        sources=list(sources),
        dates=dict(dates),
        mutation_policy=mutation_policy,
    )


def validate_card(card: ProvenanceCard) -> None:
    """Fail loudly if the card is incomplete.

    Raises:
        CardError: The author is empty, or there are no reviewers, or sources.
    """
    if not card.author:
        raise CardError("provenance card: author must not be empty")
    if not card.reviewers:
        raise CardError("provenance card: reviewer fields must be non-empty")
    if not card.sources:
        raise CardError("provenance card: sources must not be empty")


def render_card(card: ProvenanceCard) -> str:
    """Render the card as Markdown (on results)."""
    validate_card(card)
    dates = ", ".join(f"{k}={v}" for k, v in sorted(card.dates.items()))
    return (
        f"### Provenance — {card.pack_ref}\n\n"
        f"- **Author:** {card.author}\n"
        f"- **Reviewers:** {', '.join(card.reviewers)}\n"
        f"- **Sources:** {', '.join(card.sources)}\n"
        f"- **Dates:** {dates}\n"
        f"- **Mutation policy:** {card.mutation_policy}\n"
    )
