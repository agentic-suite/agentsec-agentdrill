"""Evasion / self-attack pack checks (M14 14.1, R7).

The evasion pack red-teams the ecosystem's **own** tools. Every case must
declare an expected **fail-closed** defense (outcome ``blocked`` on an
enforcement or integrity dimension) — a self-attack that does not fail closed
is a shipped vulnerability. Design: ``docs/design/threat-model.md``.
"""

from __future__ import annotations

from agentdrill.models.attack_pack import AttackPack

#: The documented evasion attack kinds (case ids in the self-attack pack).
EVASION_ATTACKS: tuple[str, ...] = (
    "pack-tamper",
    "hook-disable",
    "policy-edit",
    "telemetry-injection",
    "evidence-edit",
    "update-hijack",
    "agent-instructed-evasion",
)

#: Dimensions that count as a fail-closed defense.
FAIL_CLOSED_DIMENSIONS: frozenset[str] = frozenset({"enforcement", "integrity"})


class SelfAttackError(ValueError):
    """Raised when a self-attack case does not fail closed."""


def evasion_case_ids(pack: AttackPack) -> list[str]:
    """The case ids in an evasion pack (pack order)."""
    return [case.id for case in pack.cases]


def assert_fail_closed(pack: AttackPack) -> None:
    """Fail loudly unless every case expects a fail-closed defense.

    Raises:
        SelfAttackError: A case does not expect ``blocked``, or carries no
            enforcement/integrity dimension.
    """
    for case in pack.cases:
        if case.oracle.expect != "blocked":
            raise SelfAttackError(
                f"case {case.id}: a self-attack must fail closed (expect 'blocked'), "
                f"got {case.oracle.expect!r}"
            )
        if not (set(case.oracle.dimensions) & FAIL_CLOSED_DIMENSIONS):
            raise SelfAttackError(
                f"case {case.id}: a self-attack needs an enforcement or integrity "
                f"dimension, got {case.oracle.dimensions}"
            )
