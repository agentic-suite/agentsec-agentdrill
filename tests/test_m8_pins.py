"""M8 8.3 — pins (RED → GREEN).

A :class:`PinSet` pins the inputs that must be stable for a run to reproduce:
seed, model, pack hash and oracle versions. Comparing two pin sets declares
every change — a changed pin is never silent. The re-pin ⇒ re-publish rule is
wired through :func:`repin_note`.
"""

from __future__ import annotations

from agentdrill.determinism import PinChange, PinSet, compare_pins, repin_note


def _pins(**overrides: object) -> PinSet:
    base: dict[str, object] = {
        "seed": 7,
        "model": "judge-x",
        "pack_hash": "abc",
        "oracle_versions": {"deny": "1.0.0"},
    }
    base.update(overrides)
    return PinSet(**base)  # type: ignore[arg-type]


def test_identical_pins_declare_no_change() -> None:
    assert compare_pins(_pins(), _pins()) == []
    assert repin_note(_pins(), _pins()) is None


def test_changed_seed_is_declared() -> None:
    changes = compare_pins(_pins(seed=7), _pins(seed=9))
    assert [c.field for c in changes] == ["seed"]
    assert changes[0].previous == 7
    assert changes[0].current == 9


def test_changed_pack_hash_is_declared() -> None:
    changes = compare_pins(_pins(pack_hash="abc"), _pins(pack_hash="def"))
    assert [c.field for c in changes] == ["pack_hash"]


def test_changed_oracle_version_is_declared() -> None:
    changes = compare_pins(
        _pins(oracle_versions={"deny": "1.0.0"}),
        _pins(oracle_versions={"deny": "2.0.0"}),
    )
    assert [c.field for c in changes] == ["oracle_versions"]


def test_repin_note_names_every_changed_field() -> None:
    note = repin_note(_pins(seed=7, pack_hash="abc"), _pins(seed=9, pack_hash="def"))
    assert note is not None
    assert "seed" in note
    assert "pack_hash" in note


def test_pins_round_trip() -> None:
    pins = _pins()
    assert PinSet.from_dict(pins.to_dict()) == pins


def test_pin_digest_is_stable_for_equal_pins_and_changes_on_repin() -> None:
    assert _pins().digest() == _pins().digest()
    assert _pins(seed=7).digest() != _pins(seed=9).digest()


def test_pin_change_is_reported_against_a_previous_run() -> None:
    """A previous run's manifest pins can be the baseline for a re-pin check."""
    previous = _pins()
    current = _pins(model="judge-y")
    note = repin_note(previous, current)
    assert note is not None
    assert "model" in note
    assert isinstance(compare_pins(previous, current)[0], PinChange)
