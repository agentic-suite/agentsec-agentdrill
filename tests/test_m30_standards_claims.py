"""M30 30.5 — standards claims linter (RED -> GREEN).

The claim vocabulary is *Conforms to / Maps to / Interoperates with / Aligned
with*; "compliant/certified/secure" are **banned** unless explicitly quoted,
negated or declared banned. The linter runs over the repo's reference docs.
"""

from __future__ import annotations

from pathlib import Path

from agentdrill.standards import (
    BANNED_TERMS,
    CLAIM_VOCABULARY,
    ClaimViolation,
    lint_claims,
    lint_claims_files,
    require_claims_clean,
)


def test_the_claim_vocabulary_and_banned_terms() -> None:
    assert CLAIM_VOCABULARY == ("Conforms to", "Maps to", "Interoperates with", "Aligned with")
    assert set(BANNED_TERMS) == {"compliant", "certified", "secure"}


def test_an_allowed_claim_is_clean() -> None:
    assert lint_claims("agentdrill Conforms to NIST AI RMF and Maps to ATLAS.") == []


def test_banned_claims_are_flagged() -> None:
    violations = lint_claims("agentdrill is compliant with ISO 42001.")
    assert len(violations) == 1
    assert isinstance(violations[0], ClaimViolation)
    assert violations[0].word == "compliant"
    assert violations[0].line == 1

    assert lint_claims("We are certified.")[0].word == "certified"
    assert lint_claims("The platform is secure.")[0].word == "secure"


def test_quoted_negated_or_declared_banned_words_are_allowed() -> None:
    assert lint_claims('A valid attestation is **not** "secure".') == []
    assert lint_claims('"compliant/certified/secure" are **banned** by policy.') == []
    assert lint_claims("The term `certified` is banned here.") == []


def test_require_claims_clean_fails_loudly() -> None:
    require_claims_clean("Conforms to X.")
    try:
        require_claims_clean("agentdrill is compliant.")
    except Exception as exc:
        assert "compliant" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected a violation")


def test_quoted_words_alone_are_allowed_and_files_fail_loudly(tmp_path) -> None:
    assert lint_claims('The word "certified" appears in this quoted example.') == []
    bad = tmp_path / "bad.md"
    bad.write_text("agentdrill is secure.", encoding="utf-8")
    assert lint_claims_files([bad])
    from agentdrill.standards import require_files_clean

    try:
        require_files_clean([bad])
    except Exception as exc:
        assert "banned claim" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected a violation")


def test_the_reference_docs_are_clean() -> None:
    docs = sorted(Path("docs/reference").glob("*.md"))
    assert docs, "expected reference docs to lint"
    violations = lint_claims_files(docs)
    assert violations == [], violations
