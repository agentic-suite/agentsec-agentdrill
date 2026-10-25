"""M17 17.5 — standards submission + fuzzing (RED → GREEN).

A submission artifact for NIST CAISI / AgentDojo-Inspect / OWASP Agentic
generates offline; OSS-Fuzz is a pack class (R13, F28).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdrill.interop import (
    FUZZ_PACK_CLASS,
    SUBMISSION_TARGETS,
    Submission,
    SubmissionError,
    build_submission,
    export_submission,
    fuzz_class_pack,
)


def test_submission_artifact_generates(tmp_path: Path) -> None:
    assert set(SUBMISSION_TARGETS) == {"nist-caisi", "agentdojo-inspect", "owasp-agentic"}
    for target in SUBMISSION_TARGETS:
        submission = build_submission(
            target,
            pack_ref="p@1.0.0+abc",
            summary={"blocked": 2, "missed": 1},
            generated="2026-10-23T00:00:00Z",
        )
        assert isinstance(submission, Submission)
        path = export_submission(submission, tmp_path / target)
        assert path.exists()
        assert submission.pack_ref in path.read_text(encoding="utf-8")


def test_unknown_target_fails_loudly() -> None:
    with pytest.raises(SubmissionError, match="cosmic"):
        build_submission("cosmic", pack_ref="p", summary={}, generated="t")


def test_oss_fuzz_is_a_pack_class() -> None:
    pack = fuzz_class_pack("oss-fuzz-quickstart")
    assert FUZZ_PACK_CLASS == "oss-fuzz"
    assert FUZZ_PACK_CLASS in pack.cases[0].tags
