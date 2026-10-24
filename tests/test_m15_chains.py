"""M15 15.1 — chain structure (RED → GREEN).

Pack-level chains: per-step oracles + a `chain_oracle`
(`expect_break_before: <step>`) and state conditioning (`requires:`). A chain
runs step by step, and a stopped step halts it.
"""

from __future__ import annotations

from agentdrill.chains import Chain, ChainOracle, ChainStep, StepOracle, run_chain


def _chain() -> Chain:
    return Chain(
        id="slack-ai-exfil",
        incident_ref="incident-register#1",
        steps=[
            ChainStep(id="inject", tool="post_message", oracle=StepOracle(expect="neutralized")),
            ChainStep(
                id="render",
                tool="image_render",
                oracle=StepOracle(expect="blocked"),
                requires=["inject.succeeded"],
            ),
            ChainStep(
                id="exfil",
                tool="send_external",
                oracle=StepOracle(expect="blocked"),
                requires=["render.succeeded"],
            ),
        ],
        chain_oracle=ChainOracle(expect_break_before="render"),
    )


def test_chain_structure_carries_steps_and_a_chain_oracle() -> None:
    chain = _chain()
    assert [s.id for s in chain.steps] == ["inject", "render", "exfil"]
    assert chain.chain_oracle.expect_break_before == "render"
    assert chain.steps[1].requires == ["inject.succeeded"]


def test_chain_runs_step_by_step() -> None:
    seen: list[str] = []

    def run_step(step: ChainStep) -> str:
        seen.append(step.id)
        return "allowed"

    result = run_chain(_chain(), run_step)
    assert seen == ["inject", "render", "exfil"]
    assert result.chain_id == "slack-ai-exfil"
    assert [s.step_id for s in result.steps] == ["inject", "render", "exfil"]
    assert all(s.reached for s in result.steps)


def test_a_stopped_step_halts_the_chain() -> None:
    def run_step(step: ChainStep) -> str:
        return "blocked" if step.id == "render" else "allowed"

    result = run_chain(_chain(), run_step)
    by_id = {s.step_id: s for s in result.steps}
    assert by_id["inject"].reached is True
    assert by_id["render"].stopped is True
    assert by_id["exfil"].reached is False


def test_state_is_conditioned_on_requires() -> None:
    def run_step(step: ChainStep) -> str:
        return "blocked" if step.id == "inject" else "allowed"

    result = run_chain(_chain(), run_step)
    by_id = {s.step_id: s for s in result.steps}
    assert by_id["inject"].stopped is True
    assert by_id["render"].reached is False  # requires inject.succeeded
