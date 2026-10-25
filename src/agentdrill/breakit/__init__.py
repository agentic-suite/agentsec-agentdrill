"""Break-It program (M29, F99).

Pinned reference ranges, witness-auto-verified proof-of-bypass, coordinated
disclosure, and conversion of an accepted bypass to a permanent regression.
Design: ``docs/design/detonation-breakit-frontier.md``; PRD 37 (R73).
"""

from agentdrill.breakit.corpus import (
    ALLOWED_LICENSES,
    CORPUS_ORIGIN,
    CORPUS_TARGET,
    CorpusEntry,
    CorpusError,
    check_license,
    import_corpus,
    require_lint_clean,
)
from agentdrill.breakit.program import (
    ACK_SLA_HOURS,
    DEFAULT_MIN_AUTO_VERIFIED,
    MAX_FIX_WINDOW_DAYS,
    MIN_FIX_WINDOW_DAYS,
    BreakItError,
    BypassSubmission,
    DisclosureTimeline,
    ProofOfBypass,
    auto_verified_rate,
    convert_to_regression,
    dedup_families,
    family_catalogue,
    require_auto_verified,
    require_disclosure_timeline,
    require_triage_sla,
    triage,
    verify_proof,
)

__all__ = [
    "ACK_SLA_HOURS",
    "ALLOWED_LICENSES",
    "CORPUS_ORIGIN",
    "CORPUS_TARGET",
    "DEFAULT_MIN_AUTO_VERIFIED",
    "MAX_FIX_WINDOW_DAYS",
    "MIN_FIX_WINDOW_DAYS",
    "BreakItError",
    "BypassSubmission",
    "CorpusEntry",
    "CorpusError",
    "DisclosureTimeline",
    "ProofOfBypass",
    "auto_verified_rate",
    "check_license",
    "convert_to_regression",
    "dedup_families",
    "family_catalogue",
    "import_corpus",
    "require_auto_verified",
    "require_disclosure_timeline",
    "require_lint_clean",
    "require_triage_sla",
    "triage",
    "verify_proof",
]
