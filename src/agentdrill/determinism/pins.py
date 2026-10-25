"""Pins — the inputs a run must hold stable to reproduce (M8 8.3).

A :class:`PinSet` records the seed, model, pack hash and oracle versions a run
was produced under. A run against different pins is not comparable: a changed
pin is **declared** (never silent) and forces a re-publish. Design:
``docs/design/storage-design.md`` (DD-28).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

#: The pinned fields, in declaration order.
PIN_FIELDS: tuple[str, ...] = ("seed", "model", "pack_hash", "oracle_versions")


@dataclass(frozen=True)
class PinSet:
    """The pinned inputs for a run.

    Attributes:
        seed: The RNG seed pinned for the run (or ``None`` when unseeded).
        model: The judge/target model pinned for the run (or ``None``).
        pack_hash: The SHA-256 of the attack pack.
        oracle_versions: Oracle name → version map.
    """

    seed: int | None = None
    model: str | None = None
    pack_hash: str | None = None
    oracle_versions: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (the ``pins`` block of a run manifest)."""
        data = asdict(self)
        data["oracle_versions"] = dict(self.oracle_versions)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PinSet:
        """Rebuild a :class:`PinSet` from :meth:`to_dict` output."""
        return cls(
            seed=data.get("seed"),
            model=data.get("model"),
            pack_hash=data.get("pack_hash"),
            oracle_versions=dict(data.get("oracle_versions") or {}),
        )

    def digest(self) -> str:
        """A SHA-256 over the canonical JSON of the pins (stable, order-free)."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PinChange:
    """A single pinned input that differs between two runs."""

    field: str
    previous: Any
    current: Any


def compare_pins(previous: PinSet, current: PinSet) -> list[PinChange]:
    """Return every pinned field that changed, in declaration order.

    An empty list means the pins are identical. ``oracle_versions`` is compared
    as a whole so a version bump is one declared change.
    """
    changes: list[PinChange] = []
    for name in PIN_FIELDS:
        before = getattr(previous, name)
        after = getattr(current, name)
        if before != after:
            changes.append(PinChange(field=name, previous=before, current=after))
    return changes


def repin_note(previous: PinSet, current: PinSet) -> str | None:
    """Declare a re-pin when the pins changed since ``previous``; else ``None``.

    The returned note names every changed field — the re-publish trigger that
    keeps a silent number change impossible.
    """
    changes = compare_pins(previous, current)
    if not changes:
        return None
    detail = "; ".join(f"{c.field} {c.previous!r} -> {c.current!r}" for c in changes)
    return f"re-pin declared: {detail}"
