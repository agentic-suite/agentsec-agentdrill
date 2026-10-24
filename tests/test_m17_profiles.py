"""M17 17.3 — adversary profiles, F54 (RED → GREEN).

A pack-level threat-intel card (who, what, source, objective) rendered on
results.
"""

from __future__ import annotations

import pytest

from agentdrill.interop import AdversaryProfile, profile_section, render_profile


def _profile() -> AdversaryProfile:
    return AdversaryProfile(
        who="Opportunistic external actor",
        what="Prompt injection → data exfiltration",
        source="MITRE ATLAS AML.T0051 / incident-register#1",
        objective="Exfiltrate customer records via a rendered image",
    )


def test_profile_card_renders_who_what_source_objective() -> None:
    card = render_profile(_profile())
    assert "Opportunistic external actor" in card
    assert "data exfiltration" in card
    assert "AML.T0051" in card
    assert "Exfiltrate customer records" in card


def test_profile_section_is_a_dict() -> None:
    section = profile_section(_profile())
    assert section["who"] == "Opportunistic external actor"
    assert set(section) >= {"who", "what", "source", "objective"}


def test_an_empty_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="source"):
        AdversaryProfile(who="a", what="b", source="", objective="c").validate_profile()
