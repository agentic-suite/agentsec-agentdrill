"""Standards claims linter (M30 30.5, F104).

Every claim about a standard uses the fixed vocabulary -- **Conforms to ·
Maps to · Interoperates with · Aligned with**. The words
**"compliant" / "certified" / "secure"** are **banned**: they assert an
authority agentdrill does not have. A banned word is allowed only when the text
marks it as **quoted**, **negated**, or **declared banned**. Design:
``docs/design/trace-explorer-and-platform-standards.md``; PRD 42 (R78).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from pathlib import Path

from pydantic import BaseModel

#: The allowed claim vocabulary.
CLAIM_VOCABULARY: tuple[str, ...] = (
    "Conforms to",
    "Maps to",
    "Interoperates with",
    "Aligned with",
)

#: Words that must never be used as a claim.
BANNED_TERMS: tuple[str, ...] = ("compliant", "certified", "secure")

#: Matches any banned word as a whole word (case-insensitive).
_BANNED_RE = re.compile(r"\b(" + "|".join(BANNED_TERMS) + r")\b", re.IGNORECASE)

#: Markers that excuse a banned word (quoting, negation, or a ban statement).
_MARKERS = ("not", "never", "no ", "banned", "ban ", "forbidden")


class ClaimViolation(BaseModel):
    """One banned-word occurrence."""

    line: int
    word: str
    text: str


def _is_allowed(line: str, match: re.Match[str]) -> bool:
    """Whether a banned word is quoted, negated, or declared banned."""
    start, end = match.span()
    before = line[max(0, start - 2) : start]
    after = line[end : end + 2]
    quoted = before.endswith(('"', "'", "`")) or after.startswith(('"', "'", "`"))
    lowered = line.lower()
    negated = any(marker in lowered for marker in _MARKERS)
    return quoted or negated


def lint_claims(text: str) -> list[ClaimViolation]:
    """Find banned claims in ``text`` (allowing quoted/negated/banned words)."""
    violations: list[ClaimViolation] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in _BANNED_RE.finditer(line):
            if _is_allowed(line, match):
                continue
            violations.append(
                ClaimViolation(line=number, word=match.group(0).lower(), text=line.strip())
            )
    return violations


def lint_claims_files(paths: Iterable[str | Path]) -> list[ClaimViolation]:
    """Find banned claims across files (path noted in ``text``)."""
    violations: list[ClaimViolation] = []
    for path in paths:
        content = Path(path).read_text(encoding="utf-8")
        for violation in lint_claims(content):
            violations.append(
                violation.model_copy(update={"text": f"{path}: {violation.text}"})
            )
    return violations


def require_claims_clean(text: str) -> None:
    """Fail loudly if ``text`` contains a banned claim.

    Raises:
        ValueError: A banned claim was found.
    """
    violations = lint_claims(text)
    if violations:
        words = sorted({violation.word for violation in violations})
        raise ValueError(f"banned claim(s) found: {words}")


def require_files_clean(paths: Sequence[str | Path]) -> None:
    """Fail loudly if any file contains a banned claim.

    Raises:
        ValueError: A banned claim was found.
    """
    violations = lint_claims_files(paths)
    if violations:
        raise ValueError(
            "banned claim(s) in: "
            + "; ".join(f"{violation.word} ({violation.text})" for violation in violations[:5])
        )
