"""Kill-chain verification package (M12).

Stage model + per-case timeline (12.1), the cessation probe (12.2), repeated
trials → percentiles (12.3), the timeline + typed findings (12.4), kill-time
budgets as policy (12.5) and probe evidence (12.6). Design:
``docs/design/killchain.md``.
"""

from agentdrill.killchain.model import KILL_CHAIN_STAGES, KillChainTimeline, build_timeline
from agentdrill.killchain.probe import ProbeResult, run_cessation_probe

__all__ = [
    "KILL_CHAIN_STAGES",
    "KillChainTimeline",
    "ProbeResult",
    "build_timeline",
    "run_cessation_probe",
]
