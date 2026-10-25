"""Chain runner (M15 15.1).

Runs a chain step by step: a step conditioned on ``requires`` is reached only
when its prior steps succeeded, and a stopped step halts the chain (the attack
cannot progress). Design: ``docs/prd/16-attack-chain-orchestration.md``.
"""

from __future__ import annotations

from collections.abc import Callable

from agentdrill.chains.model import (
    STOP_OUTCOMES,
    Chain,
    ChainRun,
    ChainStep,
    StepResult,
    _required_step,
)

#: Runs one step and returns the observed outcome (e.g. ``blocked``/``allowed``).
StepRunner = Callable[[ChainStep], str]


def run_chain(chain: Chain, run_step: StepRunner) -> ChainRun:
    """Run ``chain`` step by step, honoring ``requires`` and halting on a stop.

    Args:
        chain: The chain to run.
        run_step: Runs one step and returns its observed outcome; a
            :data:`STOP_OUTCOMES` value means the defense stopped the step.

    Returns:
        A :class:`ChainRun` with one :class:`StepResult` per step.
    """
    succeeded: set[str] = set()
    results: list[StepResult] = []
    broken = False

    for step in chain.steps:
        requires_met = all(_required_step(cond) in succeeded for cond in step.requires)
        if broken or not requires_met:
            results.append(StepResult(step_id=step.id, reached=False))
            continue

        observed = run_step(step)
        stopped = observed in STOP_OUTCOMES
        results.append(
            StepResult(
                step_id=step.id,
                reached=True,
                observed=observed,
                stopped=stopped,
            )
        )
        if stopped:
            broken = True
        else:
            succeeded.add(step.id)

    return ChainRun(chain_id=chain.id, steps=results)
