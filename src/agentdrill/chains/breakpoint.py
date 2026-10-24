"""Break-point reporting (M15 15.2).

A chain names **where** it broke: ``broke_at`` (the step that stopped the
chain) and ``furthest_reached``. A defense that breaks the chain too late —
at or after the ``chain_oracle`` step — is a **distinct finding** from one that
never breaks it. Design: ``docs/prd/16-attack-chain-orchestration.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

from agentdrill.chains.model import Chain, ChainRun


class ChainBreakFinding(BaseModel):
    """Where a chain broke, relative to where the chain oracle says it must."""

    chain_id: str
    broke_at: str | None
    furthest_reached: str | None
    expected_break_before: str
    on_time: bool
    late: bool
    never_broke: bool
    detail: str = ""


def analyze_chain(chain: Chain, run: ChainRun) -> ChainBreakFinding:
    """Analyze ``run`` against ``chain``'s chain oracle.

    The chain must break **before** ``chain_oracle.expect_break_before``:
    ``on_time`` when it broke earlier, ``late`` when it broke at/after that
    step, ``never_broke`` when it never stopped.
    """
    step_ids = [step.id for step in chain.steps]
    expected = chain.chain_oracle.expect_break_before
    expected_index = step_ids.index(expected) if expected in step_ids else len(step_ids)

    broke_at = run.broke_at
    never_broke = broke_at is None
    broke_index = step_ids.index(broke_at) if broke_at in step_ids else None
    on_time = broke_index is not None and broke_index < expected_index
    late = broke_index is not None and broke_index >= expected_index

    if never_broke:
        detail = f"chain never broke (must break before {expected})"
    elif late:
        detail = f"chain broke late at {broke_at} (must break before {expected})"
    else:
        detail = f"chain broke on time at {broke_at} (before {expected})"

    return ChainBreakFinding(
        chain_id=chain.id,
        broke_at=broke_at,
        furthest_reached=run.furthest_reached,
        expected_break_before=expected,
        on_time=on_time,
        late=late,
        never_broke=never_broke,
        detail=detail,
    )
