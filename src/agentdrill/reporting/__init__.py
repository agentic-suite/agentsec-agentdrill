"""Reporting package (M10) — honest, multi-format run reports.

The reporter renders one run to JSON / Markdown / GitHub-Actions / self-contained
HTML / PDF (M10 10.1), enforcing the honesty rules: misses mandatory,
multi-seed numbers, bootstrap CIs, no composite score. Design:
``docs/design/reporting.md``.
"""

from agentdrill.reporting.ci import (
    BarePercentageError,
    RateCI,
    bootstrap_ci,
    format_rate,
    rate_cis,
    require_ci,
)
from agentdrill.reporting.honesty import (
    HonestyCheck,
    HonestyError,
    check_honesty,
    publish,
)
from agentdrill.reporting.model import Report, ReportRow
from agentdrill.reporting.render import (
    Format,
    render,
    render_github_actions,
    render_html,
    render_json,
    render_markdown,
    render_pdf,
)
from agentdrill.reporting.severity import (
    RatedFinding,
    Severity,
    rate_finding,
    sort_findings,
)
from agentdrill.reporting.stats import (
    MIN_SEEDS,
    SeedStat,
    SingleRunError,
    require_multi_seed,
    seed_stats,
)

__all__ = [
    "MIN_SEEDS",
    "BarePercentageError",
    "Format",
    "HonestyCheck",
    "HonestyError",
    "RateCI",
    "RatedFinding",
    "Report",
    "ReportRow",
    "SeedStat",
    "Severity",
    "SingleRunError",
    "bootstrap_ci",
    "check_honesty",
    "format_rate",
    "publish",
    "rate_cis",
    "rate_finding",
    "render",
    "render_github_actions",
    "render_html",
    "render_json",
    "render_markdown",
    "render_pdf",
    "require_ci",
    "require_multi_seed",
    "seed_stats",
    "sort_findings",
]
