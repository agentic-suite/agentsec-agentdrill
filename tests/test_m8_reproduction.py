"""M8 8.5 — reproducibility test (RED → GREEN).

Rerun a pinned pack ⇒ identical result unless a pin changed (and that change
is declared). A silent non-determinism fails the check; a declared re-pin is
the sanctioned exception. `ok` is the CI verdict.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.determinism import (
    PinSet,
    ReproductionResult,
    fingerprint_artifacts,
    verify_reproduction,
)
from agentdrill.fixtures import DriverFixture
from agentdrill.models.artifact import RunOutput, TrajectoryStep
from agentdrill.models.attack_pack import AttackPack


def _pack() -> AttackPack:
    return AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
                "hash": "deadbeef",
            },
            "cases": [
                {
                    "id": "c1",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                    "tags": [],
                }
            ],
        }
    )


def _ok(case: Any) -> CaseOutcome:
    return CaseOutcome(output=RunOutput(final="deny"), trajectory=[TrajectoryStep(type="response")])


def _pins(**overrides: object) -> PinSet:
    base: dict[str, object] = {
        "seed": 7,
        "model": "judge-x",
        "pack_hash": "abc",
        "oracle_versions": {"deny": "1.0.0"},
    }
    base.update(overrides)
    return PinSet(**base)  # type: ignore[arg-type]


def _run(tmp_path: Path, run_id: str) -> list[Any]:
    return AttackRunner(_ok, runs_dir=tmp_path / run_id).run_all(_pack(), run_id=run_id)


def test_same_pins_identical_results_reproduce(tmp_path: Path) -> None:
    first = _run(tmp_path, "a")
    second = _run(tmp_path, "b")
    result = verify_reproduction(first, second, previous_pins=_pins(), current_pins=_pins())
    assert isinstance(result, ReproductionResult)
    assert result.reproduced is True
    assert result.declared is False
    assert result.ok is True


def test_silent_nondeterminism_fails(tmp_path: Path) -> None:
    first = _run(tmp_path, "a")
    second = _run(tmp_path, "b")
    second[0].output = RunOutput(final="allow")  # the run changed with the same pins
    result = verify_reproduction(first, second, previous_pins=_pins(), current_pins=_pins())
    assert result.reproduced is False
    assert result.declared is False
    assert result.ok is False


def test_changed_pin_declares_the_difference(tmp_path: Path) -> None:
    first = _run(tmp_path, "a")
    second = _run(tmp_path, "b")
    second[0].output = RunOutput(final="allow")
    result = verify_reproduction(first, second, previous_pins=_pins(), current_pins=_pins(seed=9))
    assert result.reproduced is False
    assert result.declared is True
    assert result.ok is True
    assert result.note is not None
    assert "seed" in result.note


def test_fingerprint_ignores_run_identity_and_timestamp(tmp_path: Path) -> None:
    first = _run(tmp_path, "a")
    second = _run(tmp_path, "b")
    assert fingerprint_artifacts(first) == fingerprint_artifacts(second)


def test_reproduces_end_to_end_over_a_fixture_pack(tmp_path: Path) -> None:
    """A pinned pack replayed from fixtures reproduces exactly (ties 8.1 + 8.5)."""
    fixtures_dir = tmp_path / "fx"
    DriverFixture(fixtures_dir, source=_ok, mode="record")(_pack().cases[0])

    def produce(run_id: str) -> list[Any]:
        replay = DriverFixture(fixtures_dir, mode="replay")
        return AttackRunner(replay, runs_dir=tmp_path / run_id).run_all(_pack(), run_id=run_id)

    result = verify_reproduction(
        produce("a"), produce("b"), previous_pins=_pins(), current_pins=_pins()
    )
    assert result.ok is True
    assert result.reproduced is True
