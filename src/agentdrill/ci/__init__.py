"""CI gate package (M11).

Structured exit codes (11.1), per-dimension and divergence gating (11.2),
CI output (11.3), change-driven execution (11.4-11.6), annotations (11.7) and
scheduled drills (11.8). Design: ``docs/design/ci-gate.md``.
"""

from agentdrill.ci.annotations import (
    Annotation,
    annotate,
    build_alert,
    github_annotation,
    notify,
)
from agentdrill.ci.gate import run_exit_code
from agentdrill.ci.gating import GateFailure, check_gates
from agentdrill.ci.output import render_ci_output, write_step_summary
from agentdrill.ci.schedule import DrillSchedule, due_drills, is_due, record_finding
from agentdrill.ci.selection import Selection, affected_cases, case_surfaces, selection
from agentdrill.ci.triggers import ChangeEvent, TriggerWatcher
from agentdrill.ci.watch import LocalWatcher, snapshot_paths
from agentdrill.cli.exit_codes import ExitCode

__all__ = [
    "Annotation",
    "ChangeEvent",
    "DrillSchedule",
    "ExitCode",
    "GateFailure",
    "LocalWatcher",
    "Selection",
    "TriggerWatcher",
    "affected_cases",
    "annotate",
    "build_alert",
    "case_surfaces",
    "check_gates",
    "due_drills",
    "github_annotation",
    "is_due",
    "notify",
    "record_finding",
    "render_ci_output",
    "run_exit_code",
    "selection",
    "snapshot_paths",
    "write_step_summary",
]
