"""Oracle credibility package (M19).

Oracle versioning (19.1, F79), the calibration corpus (19.2, F80), judge drift
detection (19.3, F81), the meta-eval battery (19.4, F82), the human
adjudication layer (19.5, F83), honesty labels (19.6, F84) and the dispute
process (19.7, CUJ-13). Design: ``docs/prd/23-oracle-credibility.md``.
"""

from agentdrill.credibility.calibration import (
    CalibrationCase,
    CalibrationReport,
    calibrate,
)
from agentdrill.credibility.drift import (
    JUDGE_DRIFT,
    CanaryCase,
    DriftReport,
    JudgeDriftError,
    detect_drift,
    hash_prompt,
    require_no_drift,
)
from agentdrill.credibility.versioning import (
    OracleVersion,
    major_changed,
    parse_semver,
    pin_versions,
    rebaseline_note,
    version_changed,
)

__all__ = [
    "JUDGE_DRIFT",
    "CalibrationCase",
    "CalibrationReport",
    "CanaryCase",
    "DriftReport",
    "JudgeDriftError",
    "OracleVersion",
    "calibrate",
    "detect_drift",
    "hash_prompt",
    "major_changed",
    "parse_semver",
    "pin_versions",
    "rebaseline_note",
    "require_no_drift",
    "version_changed",
]
