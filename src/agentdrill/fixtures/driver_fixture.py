"""Record/replay fixtures for driver (target/tool) responses.

A :class:`DriverFixture` wraps a driver callable and persists the
:class:`~agentdrill.attack_runner.CaseOutcome` it returns — the target/tool
response observed for a case. Replaying a recorded fixture reproduces that
outcome without touching the live harness, so two identical fixture runs
produce identical results (R6, DD-19). Design:
``docs/design/storage-design.md``.

Modes:

- ``record`` — invoke the source driver, persist its outcome per case id.
- ``replay`` — load the recorded outcome; a missing fixture fails loudly.
- ``live`` — pass straight through to the source driver (no fixtures).

``--fixtures`` / ``--live`` remain mutually exclusive on the CLI; the mode here
is the programmatic equivalent for the attack path.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from agentdrill.attack_runner import CaseOutcome
from agentdrill.fixtures.tool_stub import FixtureNotFoundError
from agentdrill.models.attack_pack import AttackCase

#: Fixture mode for a driver.
FixtureMode = Literal["record", "replay", "live"]

#: The modes a :class:`DriverFixture` accepts.
VALID_MODES: tuple[str, ...] = ("record", "replay", "live")

#: Modes that require an underlying source driver.
_SOURCED_MODES: frozenset[str] = frozenset({"record", "live"})


class DriverFixture:
    """Record + replay a driver's target/tool responses deterministically.

    Args:
        fixtures_dir: Directory holding ``<case_id>.json`` fixtures.
        source: The underlying driver callable. Required for ``record`` and
            ``live``; optional (and unused) for ``replay``.
        mode: One of ``record`` / ``replay`` / ``live`` (default ``replay``).

    Raises:
        ValueError: If ``mode`` is unknown, or ``record``/``live`` is used
            without a ``source``.
    """

    def __init__(
        self,
        fixtures_dir: str | Path,
        *,
        source: Callable[[AttackCase], CaseOutcome] | None = None,
        mode: FixtureMode = "replay",
    ) -> None:
        if mode not in VALID_MODES:
            raise ValueError(f"unknown fixture mode: {mode!r} (expected one of {VALID_MODES})")
        if mode in _SOURCED_MODES and source is None:
            raise ValueError(f"fixture mode {mode!r} requires a source driver")
        self._fixtures_dir = Path(fixtures_dir)
        self._source = source
        self._mode: FixtureMode = mode

    @property
    def mode(self) -> FixtureMode:
        """The active fixture mode."""
        return self._mode

    @property
    def fixtures_dir(self) -> Path:
        """The directory fixtures are recorded to / replayed from."""
        return self._fixtures_dir

    def _fixture_path(self, case_id: str) -> Path:
        """The fixture path for ``case_id``, guarding against traversal.

        A case id that would escape the fixtures directory (a separator or a
        ``..`` segment) fails loudly — never silently reads/writes elsewhere.
        """
        if case_id in ("", ".", "..") or "/" in case_id or "\\" in case_id:
            raise ValueError(f"unsafe case id for a fixture: {case_id!r}")
        return self._fixtures_dir / f"{case_id}.json"

    def _require_source(self) -> Callable[[AttackCase], CaseOutcome]:
        """The source driver, or a loud error when the mode needs one."""
        if self._source is None:
            raise ValueError(f"fixture mode {self._mode!r} requires a source driver")
        return self._source

    def __call__(self, case: AttackCase) -> CaseOutcome:
        """Return the outcome for ``case`` per the active mode."""
        if self._mode == "record":
            return self._record(case)
        if self._mode == "live":
            return self._require_source()(case)
        return self._replay(case)

    def _record(self, case: AttackCase) -> CaseOutcome:
        """Invoke the source driver and persist its outcome."""
        outcome = self._require_source()(case)
        path = self._fixture_path(case.id)
        self._fixtures_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(outcome.model_dump(mode="json"), indent=2, sort_keys=True)
        path.write_text(payload + "\n", encoding="utf-8")
        return outcome

    def _replay(self, case: AttackCase) -> CaseOutcome:
        """Load the recorded outcome for ``case`` (loudly if absent)."""
        path = self._fixture_path(case.id)
        if not path.exists():
            raise FixtureNotFoundError(
                f"No recorded fixture for case '{case.id}': {path} not found"
            )
        return CaseOutcome.model_validate(json.loads(path.read_text(encoding="utf-8")))
