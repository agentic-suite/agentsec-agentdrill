"""M15 15.2 — break point reporting (RED → GREEN).

Per-step outcome + `broke_at` (where the chain broke); a defense that breaks
too late is a distinct finding from one that never breaks the chain.
"""

from __future__ import annotations

from agentdrill.chains import (
    Chain,
    ChainBreakFinding,
    ChainOracle,
    ChainStep,
    StepOracle,
    run_chain,
)
from agentdrill.chains.breakpoint import analyze_chain


def _chain() -> Chain:
    return Chain(
        id="slack-ai-exfil",
        incident_ref="incident-register#1",
        steps=[
            ChainStep(id="inject", tool="post_message", oracle=StepOracle(expect="neutralized")),
            ChainStep(id="render", tool="image_render", oracle=StepOracle(expect="blocked")),
            ChainStep(id="exfil", tool="send_external", oracle=StepOracle(expect="blocked")),
        ],
        chain_oracle=ChainOracle(expect_break_before="render"),
    )


def _run(stop_at: str | None):
    def run_step(step: ChainStep) -> str:
        return "blocked" if step.id == stop_at else "allowed"

    return run_chain(_chain(), run_step)


def test_broke_at_names_where_it_broke() -> None:
    run = _run("inject")
    assert run.broke_at == "inject"
    finding = analyze_chain(_chain(), run)
    assert isinstance(finding, ChainBreakFinding)
    assert finding.broke_at == "inject"
    assert finding.on_time is True
    assert finding.late is False


def test_a_late_break_is_a_distinct_finding() -> None:
    finding = analyze_chain(_chain(), _run("render"))
    assert finding.broke_at == "render"
    assert finding.late is True
    assert finding.on_time is False
    assert "late" in finding.detail


def test_post_exfil_break_is_late() -> None:
    assert analyze_chain(_chain(), _run("exfil")).late is True


def test_never_breaking_is_the_worst() -> None:
    finding = analyze_chain(_chain(), _run(None))
    assert finding.broke_at is None
    assert finding.never_broke is True
    assert finding.on_time is False


def test_furthest_reached_names_the_last_step() -> None:
    run = _run("render")
    assert run.furthest_reached == "render"
