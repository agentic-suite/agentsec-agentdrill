"""Chain structure (M15 15.1).

Real incidents are **chains**: each step is individually plausible; only the
sequence is the attack. A chain carries per-step oracles, a ``chain_oracle``
stating where the chain must break, and state conditioning (``requires:``)
between steps. Design: ``docs/prd/16-attack-chain-orchestration.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

#: Per-step outcomes that stop the attack (a defense acted).
STOP_OUTCOMES: frozenset[str] = frozenset({"blocked", "neutralized", "denied"})


class StepOracle(BaseModel):
    """The per-step oracle: what the step's outcome must be."""

    expect: str


class ChainStep(BaseModel):
    """One step of a chain.

    Attributes:
        id: The step id.
        tool: The tool the step invokes.
        args: The step's arguments.
        oracle: The per-step oracle.
        requires: State conditions, e.g. ``["inject.succeeded"]`` — the step is
            reached only when each named prior step succeeded.
    """

    id: str
    tool: str
    args: dict[str, object] = Field(default_factory=dict)
    oracle: StepOracle
    requires: list[str] = Field(default_factory=list)


class ChainOracle(BaseModel):
    """Where the chain MUST break."""

    expect_break_before: str


class Chain(BaseModel):
    """A multi-step attack chain with a chain oracle."""

    id: str
    incident_ref: str
    steps: list[ChainStep]
    chain_oracle: ChainOracle


class StepResult(BaseModel):
    """The outcome of one chain step."""

    step_id: str
    reached: bool
    observed: str | None = None
    stopped: bool = False


class ChainRun(BaseModel):
    """The per-step outcome of running a chain."""

    chain_id: str
    steps: list[StepResult] = Field(default_factory=list)

    @property
    def broke_at(self) -> str | None:
        """The step id where the chain first broke, or ``None`` if it never did."""
        return next((s.step_id for s in self.steps if s.stopped), None)

    @property
    def furthest_reached(self) -> str | None:
        """The last step the attack reached, or ``None`` if none were reached."""
        reached = [s.step_id for s in self.steps if s.reached]
        return reached[-1] if reached else None


def _required_step(condition: str) -> str:
    """The step id a ``<step>.succeeded`` condition refers to."""
    return condition.split(".", 1)[0]
