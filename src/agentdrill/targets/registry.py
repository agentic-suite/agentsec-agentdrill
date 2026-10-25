"""Target registry (M5 work item 5.2).

The registered deployed-stack components; an unknown name fails loudly with
:class:`ConfigError` (never a silent pass).
"""

from __future__ import annotations

from typing import Any

from agentdrill.models.errors import ConfigError
from agentdrill.targets.base import Target
from agentdrill.targets.components import COMPONENTS

#: Registered targets by component name.
TARGETS: dict[str, type[Target]] = {cls.component: cls for cls in COMPONENTS}


def get_target(name: str, config: dict[str, Any] | None = None) -> Target:
    """Return a target instance for ``name``, or raise :class:`ConfigError`."""
    target_cls = TARGETS.get(name)
    if target_cls is None:
        raise ConfigError(f"unknown target: {name!r}; registered: {sorted(TARGETS)}")
    return target_cls(config or {})
