"""Adversary profiles (M17 17.3, F54).

A pack-level threat-intel card — **who / what / source / objective** — rendered
on results so a reader knows the adversary behind a case. Design:
``docs/prd/03-landscape.md``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AdversaryProfile(BaseModel):
    """A pack-level threat-intel card."""

    who: str
    what: str
    source: str
    objective: str

    def validate_profile(self) -> None:
        """Fail loudly if any field is empty.

        Raises:
            ValueError: A field is empty.
        """
        for field in ("who", "what", "source", "objective"):
            if not getattr(self, field):
                raise ValueError(f"adversary profile: {field} must not be empty")


def render_profile(profile: AdversaryProfile) -> str:
    """Render the profile as a Markdown card for results."""
    profile.validate_profile()
    return (
        "### Adversary profile\n\n"
        f"- **Who:** {profile.who}\n"
        f"- **What:** {profile.what}\n"
        f"- **Source:** {profile.source}\n"
        f"- **Objective:** {profile.objective}\n"
    )


def profile_section(profile: AdversaryProfile) -> dict[str, Any]:
    """The profile as a result-payload section."""
    profile.validate_profile()
    return {
        "who": profile.who,
        "what": profile.what,
        "source": profile.source,
        "objective": profile.objective,
    }
