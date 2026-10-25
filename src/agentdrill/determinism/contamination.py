"""Contamination checks — F30 (M8 8.4).

A case whose content overlaps a judge/target model's declared **training
posture** (its incident refs, case ids or tools) may be answered from memory
rather than from the deployed defense. Such a case is **flagged**, never
hidden, so a reader can discount it. Design:
``docs/design/storage-design.md`` §Contamination.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentdrill.models.attack_pack import AttackCase, AttackPack


@dataclass(frozen=True)
class TrainingPosture:
    """A model's declared training-exposure surface.

    Attributes:
        model: The judge/target model the posture describes.
        exposed_case_ids: Case ids known to be in the model's training data.
        exposed_incident_refs: Incident references known to be exposed.
        exposed_tools: Tool names whose behaviour the model was trained on.
    """

    model: str
    exposed_case_ids: frozenset[str] = frozenset()
    exposed_incident_refs: frozenset[str] = frozenset()
    exposed_tools: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ContaminationFlag:
    """The contamination probe result for one case.

    Attributes:
        case_id: The case that was probed.
        contaminated: Whether any overlap with the posture was found.
        reason: A human-readable declaration (empty when clean).
        matched: The overlapping surface keys (e.g. ``case:c1``).
    """

    case_id: str
    contaminated: bool
    reason: str = ""
    matched: list[str] = field(default_factory=list)


class ContaminationProbe:
    """Probe cases against a model's declared training posture."""

    def __init__(self, posture: TrainingPosture) -> None:
        self._posture = posture

    @property
    def posture(self) -> TrainingPosture:
        """The training posture this probe checks against."""
        return self._posture

    def probe(self, case: AttackCase) -> ContaminationFlag:
        """Flag ``case`` when it overlaps the posture; never hides a match."""
        matched: list[str] = []
        if case.id in self._posture.exposed_case_ids:
            matched.append(f"case:{case.id}")
        if case.incident_ref in self._posture.exposed_incident_refs:
            matched.append(f"incident:{case.incident_ref}")
        for step in case.attack.steps:
            key = f"tool:{step.tool}"
            if step.tool in self._posture.exposed_tools and key not in matched:
                matched.append(key)
        matched.sort()
        if not matched:
            return ContaminationFlag(case_id=case.id, contaminated=False)
        return ContaminationFlag(
            case_id=case.id,
            contaminated=True,
            reason=(f"case overlaps {self._posture.model} training posture: " + ", ".join(matched)),
            matched=matched,
        )

    def probe_pack(self, pack: AttackPack) -> list[ContaminationFlag]:
        """Probe every case in ``pack`` (pack order preserved)."""
        return [self.probe(case) for case in pack.cases]
