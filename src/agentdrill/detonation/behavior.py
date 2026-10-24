"""Extension detonation (M29 29.1, F98).

Run an unknown extension (MCP server, skill, plugin/hook, rules file, package) in
the hermetic lab and report what it **actually did** — egress/DNS, honey-reads,
out-of-scope writes, process spawn, metadata drift, conditional behaviour,
declared-vs-actual mismatch, injection content — as **bounded evidence**: the
report always states the conditions **not covered**, and a clean report is never
"safe". A prior-version diff watches for a **rug pull**. Design:
``docs/design/detonation-breakit-frontier.md``; PRD 36 (R72).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

#: The observation vocabulary a detonation can produce.
ObservationKind = Literal[
    "egress",
    "dns",
    "honey_read",
    "out_of_scope_write",
    "process_spawn",
    "metadata_drift",
    "conditional_behavior",
    "declared_vs_actual",
    "injection_content",
]

#: The observation vocabulary as a runtime tuple.
OBSERVATION_KINDS: tuple[str, ...] = (
    "egress",
    "dns",
    "honey_read",
    "out_of_scope_write",
    "process_spawn",
    "metadata_drift",
    "conditional_behavior",
    "declared_vs_actual",
    "injection_content",
)

#: The default minimum seeded recall.
DEFAULT_MIN_RECALL = 0.8

#: ATLAS technique tags per observation kind.
_ATLAS: dict[str, list[str]] = {
    "egress": ["ATLAS-AML.T0048"],
    "dns": ["ATLAS-AML.T0048"],
    "honey_read": ["ATLAS-AML.T0057"],
    "out_of_scope_write": ["ATLAS-AML.T0053"],
    "process_spawn": ["ATLAS-AML.T0051"],
    "metadata_drift": ["ATLAS-AML.T0011"],
    "conditional_behavior": ["ATLAS-AML.T0011"],
    "declared_vs_actual": ["ATLAS-AML.T0054"],
    "injection_content": ["ATLAS-AML.T0051"],
}

#: Suggested mitigations per observation kind.
_POLICIES: dict[str, str] = {
    "egress": "deny egress to unlisted hosts from this extension",
    "dns": "resolve DNS through the lab sinkhole only",
    "honey_read": "block reads of canary/honey paths",
    "out_of_scope_write": "confine writes to the extension's declared paths",
    "process_spawn": "deny process spawn from an extension",
    "metadata_drift": "pin extension metadata and re-verify on change",
    "conditional_behavior": "run multi-schedule detonations (time-shifted, repeated)",
    "declared_vs_actual": "reject an extension that calls undeclared functions",
    "injection_content": "treat extension output as data, never instructions",
}

#: A marker that identifies a honey/canary path.
_HONEY_MARKERS = ("honey", "canary")


class DetonationError(ValueError):
    """Raised when a detonation escapes the lab or misses the recall gate."""


class ExtensionSpec(BaseModel):
    """An extension to detonate (its claims, not its trust)."""

    id: str
    kind: str
    declared_functions: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class LabEvent(BaseModel):
    """One observed action inside the lab."""

    kind: str
    target: str = ""
    detail: str = ""
    in_scope: bool = True
    escaped: bool = False


class Observation(BaseModel):
    """A detected behaviour, with its evidence and ATLAS tags."""

    kind: str
    target: str
    evidence: str
    atlas: list[str] = Field(default_factory=list)


class BehaviorReport(BaseModel):
    """The detonation result: bounded evidence, never "safe"."""

    extension_id: str
    observations: list[Observation] = Field(default_factory=list)
    conditions_covered: list[str] = Field(default_factory=list)
    conditions_not_covered: list[str] = Field(default_factory=list)
    policies: list[str] = Field(default_factory=list)
    escapes: list[str] = Field(default_factory=list)
    realness: str = "fixture"
    #: Always True at v0.1.0: absence of evidence is never a safety claim.
    bounded_evidence: bool = True


def _observation(kind: str, target: str, detail: str) -> Observation:
    return Observation(
        kind=kind,
        target=target,
        evidence=detail or f"{kind}: {target}",
        atlas=list(_ATLAS.get(kind, [])),
    )


def detect_observations(spec: ExtensionSpec, events: Sequence[LabEvent]) -> list[Observation]:
    """Detect the observable behaviours in ``events`` for ``spec``."""
    observations: list[Observation] = []
    for event in events:
        kind = event.kind
        target = event.target
        if kind == "network.connect":
            observations.append(_observation("egress", target, event.detail))
        elif kind == "network.dns":
            observations.append(_observation("dns", target, event.detail))
        elif kind == "fs.read" and any(m in target for m in _HONEY_MARKERS):
            observations.append(_observation("honey_read", target, event.detail))
        elif kind == "fs.write" and not event.in_scope:
            observations.append(_observation("out_of_scope_write", target, event.detail))
        elif kind == "process.spawn":
            observations.append(_observation("process_spawn", target, event.detail))
        elif kind == "metadata.change":
            observations.append(_observation("metadata_drift", target, event.detail))
        elif kind == "behavior.conditional":
            observations.append(_observation("conditional_behavior", target, event.detail))
        elif kind == "content.injection":
            observations.append(_observation("injection_content", target, event.detail))
        elif kind == "tool.call" and target not in spec.declared_functions:
            observations.append(_observation("declared_vs_actual", target, event.detail))
    return observations


def run_detonation(
    spec: ExtensionSpec, *, events: Sequence[LabEvent], realness: str = "fixture"
) -> BehaviorReport:
    """Detonate ``spec`` against ``events`` and build a bounded-evidence report."""
    observations = detect_observations(spec, events)
    covered = sorted({observation.kind for observation in observations})
    all_kinds = sorted(OBSERVATION_KINDS)
    return BehaviorReport(
        extension_id=spec.id,
        observations=observations,
        conditions_covered=covered,
        conditions_not_covered=[kind for kind in all_kinds if kind not in covered],
        policies=sorted({_POLICIES[kind] for kind in covered}),
        escapes=[event.target for event in events if event.escaped],
        realness=realness,
    )


def prior_version_diff(previous: BehaviorReport, current: BehaviorReport) -> list[str]:
    """New behaviours in ``current`` that were absent from ``previous`` (rug pull)."""
    before = {(observation.kind, observation.target) for observation in previous.observations}
    return [
        f"new: {observation.kind} -> {observation.target}"
        for observation in current.observations
        if (observation.kind, observation.target) not in before
    ]


def seeded_recall(detected: Sequence[str], expected: Sequence[str]) -> float:
    """Recall of a detector over a seeded corpus (0.0 when nothing is expected)."""
    if not expected:
        return 1.0
    return len(set(detected) & set(expected)) / len(set(expected))


def require_recall(
    detected: Sequence[str], expected: Sequence[str], *, minimum: float = DEFAULT_MIN_RECALL
) -> None:
    """Fail loudly unless recall is at least ``minimum``.

    Raises:
        DetonationError: The detector's recall is below the gate.
    """
    recall = seeded_recall(detected, expected)
    if recall < minimum:
        raise DetonationError(f"detonation recall {recall:.0%} is below the required {minimum:.0%}")


def require_no_escapes(report: BehaviorReport) -> None:
    """Fail loudly if the extension escaped the lab.

    Raises:
        DetonationError: An action left the hermetic lab.
    """
    if report.escapes:
        raise DetonationError(f"detonation escaped the lab: {report.escapes}")
