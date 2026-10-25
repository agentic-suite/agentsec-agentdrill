"""M32 32.D — documentation coherence guards.

Regressions this prevents: system docs slipping back to stale status markers,
a local markdown link rotting, or an ADR left in `proposed` while the decision
it records is accepted and built.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SKIP_DIRS = (
    "docs/prd", "docs/wbs", "docs/plans", "docs/articles", "docs/skills",
    "field-test", "field/agents", ".venv", "node_modules", ".pytest_cache",
)
# No release doc is legitimately "pending" anymore; every status is recorded.
PENDING_OK: set[str] = set()

STALE = re.compile(r"design intent|v0\.1\.0 planned", re.IGNORECASE)
FENCE = re.compile(r"```.*?```", re.DOTALL)
LINK = re.compile(r"\]\((?!https?:|mailto:|#|tel:)([^)]+\.md)(?:#[^)]*)?\)")


def _system_docs() -> list[Path]:
    docs = list(REPO.glob("*.md")) + list((REPO / "docs").rglob("*.md"))
    return [p for p in docs if not any(s in str(p) for s in SKIP_DIRS)]


def test_no_stale_status_markers() -> None:
    offenders = {}
    for path in _system_docs():
        if path.name in PENDING_OK:
            continue
        if STALE.search(path.read_text(encoding="utf-8", errors="replace")):
            offenders[str(path.relative_to(REPO))] = True
    assert not offenders, f"stale status markers in: {sorted(offenders)}"


def test_local_markdown_links_resolve() -> None:
    broken: dict[str, set[str]] = {}
    for path in _system_docs():
        text = FENCE.sub("", path.read_text(encoding="utf-8", errors="replace"))
        for match in LINK.finditer(text):
            target = match.group(1)
            if not (path.parent / target).resolve().exists():
                broken.setdefault(str(path.relative_to(REPO)), set()).add(target)
    assert not broken, {k: sorted(v) for k, v in broken.items()}


def test_adrs_are_accepted() -> None:
    adrs = sorted((REPO / "docs" / "adr").glob("0*.md"))
    assert adrs, "no ADRs found"
    not_accepted = [
        a.name for a in adrs if "**Status:** accepted" not in a.read_text(encoding="utf-8")
    ]
    assert not not_accepted, f"ADRs not marked accepted: {not_accepted}"
