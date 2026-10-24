"""Attack-chain orchestration package (M15).

Chain structure (15.1), break-point reporting (15.2), the bounded adaptive
orchestrator (15.3, F40), adaptive determinism (15.4) and the registry review
gate (15.5). Design: ``docs/prd/16-attack-chain-orchestration.md``.
"""

from agentdrill.chains.adaptive import (
    ADAPTIVE_LABEL,
    DEFAULT_COST_CEILING,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_MUTATIONS,
    MUTATION_KINDS,
    AdaptiveCase,
    AdaptiveError,
    enforce_caps,
    is_golden_comparable,
    validate_adaptive,
)
from agentdrill.chains.breakpoint import ChainBreakFinding, analyze_chain
from agentdrill.chains.model import (
    STOP_OUTCOMES,
    Chain,
    ChainOracle,
    ChainRun,
    ChainStep,
    StepOracle,
    StepResult,
)
from agentdrill.chains.runner import StepRunner, run_chain

__all__ = [
    "ADAPTIVE_LABEL",
    "DEFAULT_COST_CEILING",
    "DEFAULT_MAX_DEPTH",
    "DEFAULT_MAX_MUTATIONS",
    "MUTATION_KINDS",
    "STOP_OUTCOMES",
    "AdaptiveCase",
    "AdaptiveError",
    "Chain",
    "ChainBreakFinding",
    "ChainOracle",
    "ChainRun",
    "ChainStep",
    "StepOracle",
    "StepResult",
    "StepRunner",
    "analyze_chain",
    "enforce_caps",
    "is_golden_comparable",
    "run_chain",
    "validate_adaptive",
]
