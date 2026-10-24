"""M29 29.1 — extension detonation lab (RED → GREEN).

Detonate an unknown extension in the hermetic lab and report the observed
behaviours (egress, honey-reads, out-of-scope writes, spawn, metadata drift,
conditional behaviour, declared-vs-actual, injection content) as bounded
evidence — never "safe" — with a prior-version (rug-pull) diff and a seeded-recall
gate (≥80 %). Zero escapes.
"""

from __future__ import annotations

import pytest

from agentdrill.detonation import (
    BehaviorReport,
    DetonationError,
    ExtensionSpec,
    LabEvent,
    ObservationKind,
    detect_observations,
    prior_version_diff,
    require_no_escapes,
    require_recall,
    run_detonation,
    seeded_recall,
)


def _spec(**over: object) -> ExtensionSpec:
    base = dict(
        id="pkg-evil-1.0",
        kind="package",
        declared_functions=["read_file"],
        metadata={"homepage": "https://example.com"},
    )
    base.update(over)
    return ExtensionSpec.model_validate(base)


def _events() -> list[LabEvent]:
    return [
        LabEvent(kind="network.connect", target="https://evil.example/x"),
        LabEvent(kind="network.dns", target="evil.example"),
        LabEvent(kind="fs.read", target="/lab/honey/credentials.txt"),
        LabEvent(kind="fs.write", target="/etc/hosts", in_scope=False),
        LabEvent(kind="process.spawn", target="curl"),
        LabEvent(kind="tool.call", target="rm_rf"),
        LabEvent(kind="metadata.change", target="homepage"),
        LabEvent(kind="behavior.conditional", target="weekday-only"),
        LabEvent(kind="content.injection", target="ignore previous instructions"),
    ]


def test_every_observation_kind_is_detected() -> None:
    observations = detect_observations(_spec(), _events())
    kinds = {observation.kind for observation in observations}
    assert kinds == set(ObservationKind.__args__)
    assert all(observation.evidence for observation in observations)
    assert all(observation.atlas for observation in observations if observation.kind == "egress")


def test_report_is_bounded_evidence_never_safe() -> None:
    report = run_detonation(_spec(), events=_events())
    assert isinstance(report, BehaviorReport)
    assert report.extension_id == "pkg-evil-1.0"
    assert report.bounded_evidence is True
    assert set(report.conditions_covered) == set(ObservationKind.__args__)
    assert report.conditions_not_covered == []
    assert report.policies  # suggested mitigations
    assert report.escapes == []


def test_a_clean_report_still_states_what_was_not_covered() -> None:
    report = run_detonation(_spec(), events=[LabEvent(kind="network.connect", target="x")])
    assert report.conditions_not_covered  # absence of evidence != safe
    assert report.bounded_evidence is True


def test_zero_escapes_is_enforced() -> None:
    escaped = [*_events(), LabEvent(kind="network.connect", target="evil", escaped=True)]
    report = run_detonation(_spec(), events=escaped)
    assert report.escapes
    with pytest.raises(DetonationError):
        require_no_escapes(report)


def test_seeded_recall_of_nothing_is_one() -> None:
    assert seeded_recall([], []) == 1.0


def test_rug_pull_diff_and_seeded_recall() -> None:
    previous = run_detonation(_spec(), events=[LabEvent(kind="fs.read", target="/lab/honey/a")])
    current = run_detonation(_spec(), events=_events())
    added = prior_version_diff(previous, current)
    assert any("egress" in entry for entry in added)

    expected = ["egress", "honey_read", "out_of_scope_write", "process_spawn", "declared_vs_actual"]
    detected = expected[:4]
    assert seeded_recall(detected, expected) == pytest.approx(0.8)
    require_recall(detected, expected)  # ≥80%
    with pytest.raises(DetonationError):
        require_recall(detected[:2], expected)
