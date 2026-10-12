"""Target, driver, and oracle registry for attack packs (M2 work item 2.3).

The *registry* is the set of references a case may name. Resolving a case at
load fails loudly with :class:`~agentdrill.models.errors.ConfigError` (exit 2)
on any unknown reference — never a silent pass (``docs/reference/errors.md``).

Vocabulary is consumed, never forked: target/driver/oracle sets per PRD 15 and
``docs/design/data-dictionary.md``; the agentwatch security-event set per
ADR-0004.
"""

from __future__ import annotations

from agentdrill.models.attack_pack import AttackCase
from agentdrill.models.errors import ConfigError

#: Deployed-stack components a case may target (PRD 15 · data-dictionary).
TARGET_TYPES: frozenset[str] = frozenset(
    {
        "agentgate",
        "agentkeys",
        "agentseatbelt",
        "agentkernel",
        "policyweave-output",
        "agenthalt",
    }
)

#: How an attack is delivered to the harness/agent (PRD 15 · data-dictionary).
DRIVER_TYPES: frozenset[str] = frozenset(
    {"subprocess", "python", "http", "claude-code", "cursor"}
)

#: Defense dimensions an oracle may assess.
ORACLE_DIMENSIONS: frozenset[str] = frozenset(
    {"compatibility", "enforcement", "integrity"}
)

#: Expectations an oracle may declare.
ORACLE_EXPECTATIONS: frozenset[str] = frozenset({"blocked", "missed", "degraded"})

#: agentwatch security-event vocabulary (ADR-0004 — consumed, never forked).
AGENTWATCH_EVENTS: frozenset[str] = frozenset(
    {"denied", "policy-fired", "secret-detected", "revoked", "halted"}
)

#: Drivers safe to run for ``external`` (untrusted) packs — sandbox-only.
SANDBOX_DRIVERS: frozenset[str] = frozenset({"subprocess"})


def resolve_target(case: AttackCase) -> None:
    """Fail loudly if ``case.target.type`` is not a registered target."""
    if case.target.type not in TARGET_TYPES:
        raise ConfigError(
            f"case {case.id}: unknown target type: {case.target.type!r}; "
            f"registered: {sorted(TARGET_TYPES)}"
        )


def resolve_driver(case: AttackCase) -> None:
    """Fail loudly if ``case.driver.type`` is not a registered driver."""
    if case.driver.type not in DRIVER_TYPES:
        raise ConfigError(
            f"case {case.id}: unknown driver type: {case.driver.type!r}; "
            f"registered: {sorted(DRIVER_TYPES)}"
        )


def resolve_oracle(case: AttackCase) -> None:
    """Fail loudly if the oracle names an unknown expectation/dimension/event."""
    if case.oracle.expect not in ORACLE_EXPECTATIONS:
        raise ConfigError(
            f"case {case.id}: unknown oracle expectation: {case.oracle.expect!r}; "
            f"registered: {sorted(ORACLE_EXPECTATIONS)}"
        )
    for dimension in case.oracle.dimensions:
        if dimension not in ORACLE_DIMENSIONS:
            raise ConfigError(
                f"case {case.id}: unknown oracle dimension: {dimension!r}; "
                f"registered: {sorted(ORACLE_DIMENSIONS)}"
            )
    for event in case.oracle.expect_telemetry:
        if event not in AGENTWATCH_EVENTS:
            raise ConfigError(
                f"case {case.id}: unknown agentwatch event: {event!r}; "
                f"registered: {sorted(AGENTWATCH_EVENTS)}"
            )


def resolve_case(case: AttackCase, trust: str) -> None:
    """Resolve every reference a case makes; ``external`` is sandbox-only."""
    resolve_target(case)
    resolve_driver(case)
    resolve_oracle(case)
    if trust == "external" and case.driver.type not in SANDBOX_DRIVERS:
        raise ConfigError(
            f"case {case.id}: external-trust packs must use a sandbox driver "
            f"{sorted(SANDBOX_DRIVERS)}; got {case.driver.type!r}"
        )
