"""CI gate package (M11).

Structured exit codes (11.1), per-dimension and divergence gating (11.2),
CI output (11.3), change-driven execution (11.4-11.6), annotations (11.7) and
scheduled drills (11.8). Design: ``docs/design/ci-gate.md``.
"""

from agentdrill.ci.gate import run_exit_code
from agentdrill.ci.gating import GateFailure, check_gates
from agentdrill.ci.output import render_ci_output, write_step_summary
from agentdrill.ci.triggers import ChangeEvent, TriggerWatcher
from agentdrill.cli.exit_codes import ExitCode

__all__ = [
    "ChangeEvent",
    "ExitCode",
    "GateFailure",
    "TriggerWatcher",
    "check_gates",
    "render_ci_output",
    "run_exit_code",
    "write_step_summary",
]
