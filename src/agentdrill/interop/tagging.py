"""Standards tagging (M17 17.2, F13).

Every pack/attack carries a **MITRE ATLAS** + **OWASP** (LLM Top-10 or Agentic)
tag; lint requires them, so an untagged pack is rejected. Design:
``docs/prd/03-landscape.md``.
"""

from __future__ import annotations

from collections.abc import Iterable

from agentdrill.models.attack_pack import AttackPack

#: Tag prefixes for the two standards.
ATLAS_PREFIX = "ATLAS-"
OWASP_PREFIX = "OWASP-"


class TaggingError(ValueError):
    """Raised when a case lacks its required ATLAS/OWASP tags."""


def has_atlas(tags: Iterable[str]) -> bool:
    """Whether any tag is a MITRE ATLAS tag."""
    return any(tag.startswith(ATLAS_PREFIX) for tag in tags)


def has_owasp(tags: Iterable[str]) -> bool:
    """Whether any tag is an OWASP tag (LLM Top-10 or Agentic)."""
    return any(tag.startswith(OWASP_PREFIX) for tag in tags)


def untagged_cases(pack: AttackPack) -> list[str]:
    """Case ids missing an ATLAS or OWASP tag (pack order)."""
    return [case.id for case in pack.cases if not (has_atlas(case.tags) and has_owasp(case.tags))]


def validate_tagging(pack: AttackPack) -> None:
    """Fail loudly unless every case carries an ATLAS and an OWASP tag.

    Raises:
        TaggingError: One or more cases lack the required standards tags.
    """
    offenders = untagged_cases(pack)
    if offenders:
        raise TaggingError(f"pack {pack.pack.name}: cases missing ATLAS/OWASP tags: {offenders}")
