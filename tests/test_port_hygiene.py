"""M0 port guard: no predecessor-namespace references remain in the repository.

The M0 port renamed the predecessor's namespace to ``agentdrill`` and reset the
project to v0.1.0. Only the provenance notes may name the absorbed source
project; every other file in the tree must be free of the predecessor name.

The token is assembled from fragments so this test file does not itself contain
a literal match (the guard scans the whole tree, including itself).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Provenance port notes: these legitimately name the absorbed source project.
ALLOWLIST: frozenset[str] = frozenset(
    {
        "THIRD_PARTY_NOTICES.md",
        "CHANGELOG.md",
    }
)

# Predecessor identifiers (case-insensitive), built from fragments so this
# file does not itself contain a literal match.
_A, _B = "eval", "forge"
_PREDECESSOR_TOKENS = re.compile(
    "|".join(re.escape(t) for t in (_A + _B, _A + "-" + _B, _A + " " + _B)),
    re.IGNORECASE,
)

# Directories that are not repository sources (caches, VCS, virtualenvs).
_SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "build",
        "dist",
        ".agentdrill",
    }
)


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if _SKIP_DIRS.intersection(path.relative_to(REPO_ROOT).parts):
            continue
        files.append(path)
    return files


def test_no_predecessor_namespace_references() -> None:
    offenders: list[str] = []
    for path in _iter_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in ALLOWLIST:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if _PREDECESSOR_TOKENS.search(line):
                offenders.append(f"{rel}:{lineno}: {line.strip()[:120]}")

    assert not offenders, (
        "Predecessor-namespace references found — only the provenance port notes "
        "may name the absorbed source project:\n" + "\n".join(offenders)
    )
