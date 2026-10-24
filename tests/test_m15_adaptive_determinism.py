"""M15 15.4 — adaptive determinism (RED → GREEN).

A pinned attacker model + seed, and the mutation **path** recorded in the
manifest: two identical runs produce identical paths.
"""

from __future__ import annotations

from agentdrill.chains import (
    AdaptiveCase,
    AdaptiveRun,
    record_adaptive,
    run_adaptive,
)


def _case() -> AdaptiveCase:
    return AdaptiveCase(
        id="a1",
        parent_pattern="incident-register#1",
        mutation_summary="paraphrase the injected instruction",
        reviewer="reviewer@example",
        mutation="paraphrase",
        max_mutations=4,
    )


def test_two_identical_runs_produce_identical_paths() -> None:
    first = run_adaptive(_case(), model="attacker-x", seed=7)
    second = run_adaptive(_case(), model="attacker-x", seed=7)
    assert isinstance(first, AdaptiveRun)
    assert [s.mutation for s in first.steps] == [s.mutation for s in second.steps]
    assert first.digest() == second.digest()


def test_a_different_seed_changes_the_recorded_path() -> None:
    assert run_adaptive(_case(), model="attacker-x", seed=7).digest() != (
        run_adaptive(_case(), model="attacker-x", seed=8).digest()
    )


def test_a_different_model_changes_the_recorded_path() -> None:
    assert run_adaptive(_case(), model="attacker-x", seed=7).digest() != (
        run_adaptive(_case(), model="attacker-y", seed=7).digest()
    )


def test_the_mutation_path_is_recorded_in_the_manifest() -> None:
    run = run_adaptive(_case(), model="attacker-x", seed=7)
    manifest = record_adaptive({}, run)
    adaptive = manifest["adaptive"]
    assert adaptive["model"] == "attacker-x"
    assert adaptive["seed"] == 7
    assert adaptive["path_digest"] == run.digest()
    assert adaptive["steps"]


def test_the_path_respects_the_mutation_cap() -> None:
    run = run_adaptive(_case(), model="attacker-x", seed=7)
    assert len(run.steps) <= 4
