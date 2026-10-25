"""Driver adapters that deliver an attack to a harness (M4).

``Driver`` is the base contract; the ``subprocess`` / ``python`` / ``http`` and
per-harness drivers (``claude-code`` / ``cursor``) land in work items 4.2-4.5,
and the registry in 4.6.
"""

from __future__ import annotations

from agentdrill.drivers.base import Driver, normalize_envelope

__all__ = ["Driver", "normalize_envelope"]
