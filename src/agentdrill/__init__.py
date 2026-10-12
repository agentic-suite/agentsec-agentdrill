"""AgentDrill — a framework-agnostic evaluation harness for tool-using AI agents.

Package root.
"""

from __future__ import annotations

from pathlib import Path

__version__ = "0.1.0"

from agentdrill.baselines import Baseline, BaselineStore
from agentdrill.comparison.engine import ComparisonEngine
from agentdrill.loading import load_pack
from agentdrill.models.artifact import RunArtifact
from agentdrill.runner import Runner
from agentdrill.scoring.engine import ScoringEngine
from agentdrill.scoring.judge.client import JudgeClient
from agentdrill.scoring.result import RunScore, ScenarioScore, ScoreResult
from agentdrill.security.policy import TrustPolicy

__all__ = [
    "Baseline",
    "BaselineStore",
    "ComparisonEngine",
    "RunArtifact",
    "RunScore",
    "Runner",
    "ScenarioScore",
    "ScoreResult",
    "ScoringEngine",
    "TrustPolicy",
    "__version__",
    "evaluate",
    "load_pack",
]


def evaluate(
    pack: str | Path,
    agent: str,
    judge: str | None = None,
    model: str | None = None,
    baseline: str | None = None,
    output_dir: str | None = None,
    tags: str | list[str] | None = None,
    sandbox: bool = False,
    workers: int = 1,
    timeout: int = 120,
) -> RunScore:
    """Run a full evaluation pipeline and return results.

    Args:
        pack: Path to scenario pack YAML/JSON
        agent: Agent spec string (e.g., 'python:my_agent.run')
        judge: Judge provider (e.g., 'openai', 'anthropic')
        model: Judge model (e.g., 'gpt-4o-mini')
        baseline: Optional baseline name for comparison
        output_dir: Directory for artifacts
        tags: Filter scenarios by tags
        sandbox: Enable sandbox mode
        workers: Number of parallel workers
        timeout: Agents timeout in seconds

    Returns:
        RunScore with all scenario scores
    """
    from agentdrill.cache import JudgeCache
    from agentdrill.cli.util import parse_agent_spec

    agent_config = parse_agent_spec(agent)
    agent_config["timeout_seconds"] = timeout
    agent_config["sandbox"] = sandbox

    tag_list = tags.split(",") if isinstance(tags, str) else tags

    runner = Runner(
        agent_config=agent_config,
        output_dir=output_dir or ".agentdrill",
    )
    runner.load_pack(pack)

    artifacts = runner.run_all(tags=tag_list, workers=workers)

    judge_client = None
    if judge is not None:
        judge_client = _resolve_judge(judge, model)

    judge_cache = JudgeCache(base_dir=output_dir or ".agentdrill")
    engine = ScoringEngine(runner.pack, judge_cache=judge_cache)
    run_score = engine.score_run(artifacts, judge=judge_client)

    if baseline is not None:
        from agentdrill.baselines.store import BaselineStore
        from agentdrill.comparison.engine import ComparisonEngine

        store = BaselineStore(base_dir=f"{output_dir or '.agentdrill'}/baselines")
        baseline_obj = store.load(baseline)
        baseline_score = engine.score_run(baseline_obj.runs, judge=judge_client)
        comp_engine = ComparisonEngine(runner.pack)
        comp_engine.compare(
            baseline_score=baseline_score,
            candidate_score=run_score,
            baseline=baseline_obj,
        )

    return run_score


def _resolve_judge(provider: str, model: str | None = None) -> JudgeClient:
    import os

    if provider == "openai":
        from agentdrill.scoring.judge.openai import OpenAIClient

        return OpenAIClient(
            api_key=os.environ["OPENAI_API_KEY"],
            model=model or "gpt-4o-mini",
        )

    if provider == "anthropic":
        from agentdrill.scoring.judge.anthropic import AnthropicClient

        return AnthropicClient(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            model=model or "claude-3-haiku-20240307",
        )

    if provider == "ollama":
        from agentdrill.scoring.judge.ollama import OllamaClient

        return OllamaClient(model=model or "llama3")

    if provider == "mlx":
        from agentdrill.scoring.judge.mlx import MLXJudgeClient

        return MLXJudgeClient(
            model=model or "mlx-community/Llama-3.2-3B-Instruct-4bit"
        )

    if provider == "mock":
        from agentdrill.scoring.judge.mock import MockJudge

        return MockJudge(score=1.0)

    raise ValueError(f"unknown judge provider: {provider}")
