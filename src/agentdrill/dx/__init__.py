"""Developer-experience package (M20).

Pack diff (20.1, F67), dry-run/explain (20.2, F69), templates (20.3, F70),
CI-matrix export (20.4, F72), programmatic assertions (20.5, F73), provenance
cards (20.6, F74), the read-only MCP drill surface (20.7, F77) and fleet mode
(20.8, F45). Design: ``docs/prd/22-frontier-dx-features.md``.
"""

from agentdrill.dx.diff import PackDiff, diff_packs
from agentdrill.dx.dry_run import DryRunCase, DryRunPlan, dry_run, render_dry_run
from agentdrill.dx.templates import TEMPLATES, TemplateError, scaffold, scaffold_yaml

__all__ = [
    "TEMPLATES",
    "DryRunCase",
    "DryRunPlan",
    "PackDiff",
    "TemplateError",
    "diff_packs",
    "dry_run",
    "render_dry_run",
    "scaffold",
    "scaffold_yaml",
]
