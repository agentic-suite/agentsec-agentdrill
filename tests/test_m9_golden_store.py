"""M9 9.6 — golden/preregistration store (RED → GREEN).

Goldens live under `.agentdrill/goldens/`, bound to `pack@version+hash`. A
missing golden, a tampered pack ref, or an unsafe ref fails loudly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdrill.comparison import Golden, GoldenStore


def _golden(pack_ref: str = "p@1.0.0+deadbeef") -> Golden:
    return Golden.from_outcomes(
        pack_ref=pack_ref,
        outcomes={"c1": "blocked", "c2": "missed"},
        pins={"seed": 7},
    )


def test_save_then_load_binds_to_pack(tmp_path: Path) -> None:
    store = GoldenStore(tmp_path / "goldens")
    store.save(_golden())
    loaded = store.load("p@1.0.0+deadbeef")
    assert loaded.pack_ref == "p@1.0.0+deadbeef"
    expected = _golden()
    assert loaded.pins == {"seed": 7}
    assert loaded.cases == expected.cases
    assert loaded.locked is True


def test_store_path_is_bound_to_pack_ref(tmp_path: Path) -> None:
    store = GoldenStore(tmp_path / "goldens")
    path = store.save(_golden())
    assert path.exists()
    assert path.parent == tmp_path / "goldens"
    assert "p@1.0.0+deadbeef" in path.name


def test_exists_helper(tmp_path: Path) -> None:
    store = GoldenStore(tmp_path / "goldens")
    assert store.exists("p@1.0.0+deadbeef") is False
    store.save(_golden())
    assert store.exists("p@1.0.0+deadbeef") is True


def test_load_missing_fails_loudly(tmp_path: Path) -> None:
    store = GoldenStore(tmp_path / "goldens")
    with pytest.raises(KeyError):
        store.load("nope@9.9.9+0000")


def test_tampered_pack_ref_fails_loudly(tmp_path: Path) -> None:
    store = GoldenStore(tmp_path / "goldens")
    path = store.save(_golden())
    path.write_text('{"pack_ref": "evil@1.0.0+ffff", "cases": []}')
    with pytest.raises(ValueError, match="pack_ref"):
        store.load("p@1.0.0+deadbeef")


def test_unsafe_pack_ref_is_rejected(tmp_path: Path) -> None:
    store = GoldenStore(tmp_path / "goldens")
    with pytest.raises(ValueError, match="unsafe"):
        store.save(_golden("../escape"))
