"""Developer-experience package (M20).

Pack diff (20.1, F67), dry-run/explain (20.2, F69), templates (20.3, F70),
CI-matrix export (20.4, F72), programmatic assertions (20.5, F73), provenance
cards (20.6, F74), the read-only MCP drill surface (20.7, F77) and fleet mode
(20.8, F45). Design: ``docs/prd/22-frontier-dx-features.md``.
"""

from agentdrill.dx.assertions import (
    DxAssertionError,
    assert_blocked,
    assert_degraded,
    assert_kill_time_under,
    assert_missed,
)
from agentdrill.dx.ci_matrix import (
    CI_FORMATS,
    CiMatrix,
    CiMatrixError,
    build_ci_matrix,
    render_ci_matrix,
    validate_ci_matrix,
)
from agentdrill.dx.diff import PackDiff, diff_packs
from agentdrill.dx.dry_run import DryRunCase, DryRunPlan, dry_run, render_dry_run
from agentdrill.dx.mcp_surface import (
    WRITE_TOKENS,
    McpDrillSurface,
    McpError,
    McpTool,
    is_write_tool,
    require_read_only,
)
from agentdrill.dx.provenance import (
    CardError,
    ProvenanceCard,
    build_card,
    render_card,
    validate_card,
)
from agentdrill.dx.templates import TEMPLATES, TemplateError, scaffold, scaffold_yaml

__all__ = [
    "CI_FORMATS",
    "TEMPLATES",
    "WRITE_TOKENS",
    "CardError",
    "CiMatrix",
    "CiMatrixError",
    "DryRunCase",
    "DryRunPlan",
    "DxAssertionError",
    "McpDrillSurface",
    "McpError",
    "McpTool",
    "PackDiff",
    "ProvenanceCard",
    "TemplateError",
    "assert_blocked",
    "assert_degraded",
    "assert_kill_time_under",
    "assert_missed",
    "build_card",
    "build_ci_matrix",
    "diff_packs",
    "dry_run",
    "is_write_tool",
    "render_card",
    "render_ci_matrix",
    "render_dry_run",
    "require_read_only",
    "scaffold",
    "scaffold_yaml",
    "validate_card",
    "validate_ci_matrix",
]
