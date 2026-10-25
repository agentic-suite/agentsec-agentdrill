"""M20 20.6 — provenance cards, F74 (RED → GREEN).

A machine-readable card per pack (sources, dates, mutation policy, author,
reviewers), rendered on results; reviewer fields must be non-empty.
"""

from __future__ import annotations

import json

import pytest

from agentdrill.dx import (
    CardError,
    ProvenanceCard,
    build_card,
    render_card,
    validate_card,
)


def _card(**overrides: object) -> ProvenanceCard:
    base: dict[str, object] = {
        "pack_ref": "p@1.0.0+abc",
        "author": "author@example",
        "reviewers": ["r1@example", "r2@example"],
        "sources": ["incident-register#1", "vendor-advisory"],
        "dates": {"created": "2026-10-01", "updated": "2026-10-20"},
        "mutation_policy": "documented-pattern mutation only",
    }
    base.update(overrides)
    return build_card(**base)  # type: ignore[arg-type]


def test_card_renders_with_all_fields() -> None:
    rendered = render_card(_card())
    assert "p@1.0.0+abc" in rendered
    assert "author@example" in rendered
    assert "r1@example" in rendered
    assert "documented-pattern mutation only" in rendered


def test_reviewer_fields_must_be_non_empty() -> None:
    with pytest.raises(CardError, match="reviewer"):
        validate_card(_card(reviewers=[]))


def test_card_is_machine_readable() -> None:
    data = json.loads(_card().model_dump_json())
    assert data["author"] == "author@example"
    assert data["reviewers"] == ["r1@example", "r2@example"]
