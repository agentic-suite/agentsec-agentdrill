"""Interop package (M17).

Import community attack suites (17.1, F12); MITRE ATLAS + OWASP tagging
(17.2, F13); adversary profiles (17.3, F54); compliance-mapped reporting
(17.4, F24); standards submission + fuzzing (17.5, F28/R13); competitor
benchmark (17.6, R12). Design: ``docs/prd/03-landscape.md``.
"""

from agentdrill.interop.compliance import (
    FRAMEWORKS,
    ComplianceError,
    ComplianceMapping,
    ComplianceReport,
    ComplianceRow,
    build_compliance_report,
    export_agentcomply,
    map_finding,
)
from agentdrill.interop.importers import (
    SUPPORTED_TOOLS,
    ImportedCase,
    InteropError,
    import_suite,
    parse_agentdojo,
    parse_garak,
    parse_promptfoo,
    parse_pyrit,
    to_pack,
)
from agentdrill.interop.profiles import (
    AdversaryProfile,
    profile_section,
    render_profile,
)
from agentdrill.interop.submission import (
    FUZZ_PACK_CLASS,
    SUBMISSION_TARGETS,
    Submission,
    SubmissionError,
    build_submission,
    export_submission,
    fuzz_class_pack,
)
from agentdrill.interop.tagging import (
    ATLAS_PREFIX,
    OWASP_PREFIX,
    TaggingError,
    has_atlas,
    has_owasp,
    untagged_cases,
    validate_tagging,
)

__all__ = [
    "ATLAS_PREFIX",
    "FRAMEWORKS",
    "FUZZ_PACK_CLASS",
    "OWASP_PREFIX",
    "SUBMISSION_TARGETS",
    "SUPPORTED_TOOLS",
    "AdversaryProfile",
    "ComplianceError",
    "ComplianceMapping",
    "ComplianceReport",
    "ComplianceRow",
    "ImportedCase",
    "InteropError",
    "Submission",
    "SubmissionError",
    "TaggingError",
    "build_compliance_report",
    "build_submission",
    "export_agentcomply",
    "export_submission",
    "fuzz_class_pack",
    "has_atlas",
    "has_owasp",
    "import_suite",
    "map_finding",
    "parse_agentdojo",
    "parse_garak",
    "parse_promptfoo",
    "parse_pyrit",
    "profile_section",
    "render_profile",
    "to_pack",
    "untagged_cases",
    "validate_tagging",
]
