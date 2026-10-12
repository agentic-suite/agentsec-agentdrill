"""Pydantic models for the versioned attack-pack format (M2 work item 2.1).

An attack pack is the unit of defense proof: `pack` metadata plus a list of
`cases`, where each case binds an attempted attack to a target, a driver and an
oracle. This is the schema against which attack-pack YAML/JSON is validated
(see :mod:`agentdrill.loading.pack_loader`).

Normative shape: `docs/design/pack-format.md` and
`docs/reference/pack-format-spec.md`; entities per PRD 15 (`AttackPack` →
`AttackCase` → `Target`/`Driver` → …).

Design intent (pre-build) — absorbed from the predecessor scenario-pack shape
and re-pointed for defense proof (DD-16). Strict validation (path-safe ids,
resolvers, thresholds) lands in work item 2.2.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentdrill.models.pack import Budget

#: Trust level of a pack's origin. `external` packs are sandbox-only.
TrustLevel = Literal["built-in", "local", "external"]

#: Result a case's oracle expects from the deployed stack.
OracleExpectation = Literal["blocked", "missed", "degraded"]

#: Defense dimension a case exercises.
OracleDimension = Literal["compatibility", "enforcement", "integrity"]

#: Case difficulty, when annotated.
Difficulty = Literal["easy", "medium", "hard"]


class AttackTarget(BaseModel):
    """The deployed-stack component a case exercises, with its config."""

    type: str
    config: dict[str, Any] = Field(default_factory=dict)


class Driver(BaseModel):
    """How the attack is delivered to the harness/agent, with its config."""

    type: str
    config: dict[str, Any] = Field(default_factory=dict)


class AttackStep(BaseModel):
    """One attempted action in a case's attack."""

    tool: str
    args: dict[str, Any] = Field(default_factory=dict)


class Attack(BaseModel):
    """The attempted actions that constitute a case's attack."""

    steps: list[AttackStep]


class KillTime(BaseModel):
    """Kill-time bound the deployed stack must meet for a case to pass."""

    max_seconds: int


class Oracle(BaseModel):
    """What the case expects of the deployed stack, and on which dimensions."""

    expect: OracleExpectation
    dimensions: list[OracleDimension] = Field(default_factory=list)
    expect_telemetry: list[str] = Field(default_factory=list)
    kill_time: KillTime | None = None


class CleanupStep(BaseModel):
    """A post-case cleanup action; its failure marks the target dirty."""

    cmd: str
    expect: str = "success"


class AttackCase(BaseModel):
    """One attack step bound to a target and an oracle.

    Fields mirror `docs/reference/pack-format-spec.md` §Case. `id` is
    path-safe by contract; enforcement (in the loader) lands in work item 2.2.
    """

    id: str
    title: str
    goal: str
    incident_ref: str
    target: AttackTarget
    driver: Driver
    attack: Attack
    oracle: Oracle
    benign_twin: str | None = None
    cleanup: list[CleanupStep] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    difficulty: Difficulty | None = None
    budget: Budget | None = None


class AttackPackMetadata(BaseModel):
    """The `pack` block: identity, compatibility and trust of a pack."""

    name: str
    version: str
    description: str
    min_agentdrill: str
    license: str
    trust: TrustLevel = "local"
    #: SHA-256 of the pack content; computed/populated at load (work item 2.7).
    hash: str | None = None


class AttackPack(BaseModel):
    """A parsed attack pack: metadata plus its cases."""

    pack: AttackPackMetadata
    cases: list[AttackCase]
