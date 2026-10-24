"""Hidden adversarial case (M14 14.5).

An **independent-reviewer-authored secret case** (the JPS pattern), kept inside
the meta pack. It is authored to **escape a single-layer defense**: it is
stopped only when every required layer is present. Design:
``docs/design/threat-model.md``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from agentdrill.models.attack_pack import AttackCase, AttackPack

#: The hidden case's id inside the meta pack.
HIDDEN_CASE_ID = "hidden-adversarial"

#: The layers that must all be present to stop the hidden case.
HIDDEN_REQUIRED_LAYERS: tuple[str, ...] = (
    "policyweave-output",
    "agentgate",
    "agentseatbelt",
)

#: The tag that marks an independent-reviewer-authored hidden case.
HIDDEN_TAG = "hidden"


def is_hidden_case(tags: Iterable[str]) -> bool:
    """Whether a case is a hidden (secret, reviewer-authored) case."""
    return HIDDEN_TAG in set(tags)


def hidden_cases(pack: AttackPack) -> list[AttackCase]:
    """The hidden cases inside ``pack`` (pack order)."""
    return [case for case in pack.cases if is_hidden_case(case.tags)]


def escapes_single_layer(present_layers: Sequence[str]) -> bool:
    """Whether the hidden case escapes the ``present_layers`` defense.

    The case escapes unless **every** required layer is present — so no single
    control stops it.
    """
    return not set(HIDDEN_REQUIRED_LAYERS).issubset(set(present_layers))
